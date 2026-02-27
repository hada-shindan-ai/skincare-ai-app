import os
import json
import requests
from dotenv import load_dotenv

# .streamlit/secrets.toml もしくは .env からキーを読み込む処理の簡易版
# ここでは環境変数 GEMINI_API_KEY を使用前提で作成します
def get_api_key():
    # First, try to get a dedicated backend API key to avoid sharing quota with the frontend
    key = os.environ.get("GEMINI_BACKEND_API_KEY")
    if not key:
        key = os.environ.get("GEMINI_API_KEY")
        
    if not key:
        # Streamlit secrets path handling
        import toml
        secrets_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), ".streamlit", "secrets.toml")
        try:
            secrets = toml.load(secrets_path)
            # 1. Look for dedicated backend key
            key = secrets.get("GEMINI_BACKEND_API_KEY")
            
            # 2. Fallback to generic key
            if not key:
                key = secrets.get("GEMINI_API_KEY")
                
            # 3. Fallback to list of keys
            if not key and secrets.get("GEMINI_API_KEYS"):
                key = secrets.get("GEMINI_API_KEYS")[0]
                
        except Exception as e:
            print(f"Error loading secrets: {e}")
            
    return key

from google import genai
from google.genai import types
from pydantic import BaseModel

class IngredientInfo(BaseModel):
    name: str
    benefit: str
    evidence: str

class ProductEvaluation(BaseModel):
    skin_types: list[str]
    concerns: list[str]
    texture: str
    ingredients: list[IngredientInfo]

def parse_with_gemini(product_data, api_key):
    """
    生の製品データ（名前、説明、成分）をGeminiに渡し、
    Skin Type, Concerns, 注目の成分効果とエビデンスをJSONで抽出させる。
    """
    
    system_prompt = """
あなたはプロの皮膚科医・化粧品成分スペシャリストです。
提供された化粧品の「商品名」「商品説明」「全成分表示」を分析し、評価結果を出力してください。

【評価・付与ルール】
1. skin_types (肌質)
   - 以下の選択肢から合致するものを1つ以上選んで配列にしてください: ["乾燥肌", "脂性肌", "普通肌", "混合肌", "敏感肌"]
   - 例: 全成分がシンプルで弱酸性無香料なら "敏感肌" を含める。セラミド豊富なら "乾燥肌" など。
   
2. concerns (肌悩み)
   - 以下の選択肢から合致するものを1〜4つ選んで配列にしてください: ["シミ・そばかす", "たるみ", "シワ", "ハリ・ツヤのなさ", "乾燥", "目の下のくま", "毛穴の黒ずみ・開き", "くすみ", "ニキビ・吹き出物", "赤み・赤ら顔", "脂っぽさ・テカリ", "化粧ノリが悪い", "かゆみ"]
   
3. texture (テクスチャー予想)
   - 提供された情報から、どのような使用感か、どのような香りがするかを50文字程度で予想し、魅力的なテキストにしてください。
   
4. ingredients (注目成分リスト)
   - 成分表の中から、特に効果に寄与している「キーとなる成分（最大3つ）」を選び出してください。
   - name: 成分名
   - benefit: ユーザーへの分かりやすいベネフィット（効果）
   - evidence: その成分に関する「架空ではない一般的な科学的エビデンス」を簡単に記載してください（例：「Journal of Dermatology で美白効果が示されています」など。学術誌名や一般的知見を引用すること）
"""

    user_message = f"以下の商品データを分析してください:\n\n{json.dumps(product_data, ensure_ascii=False, indent=2)}"
    
    max_retries = 4
    for attempt in range(max_retries):
        try:
            client = genai.Client(api_key=api_key)
            response = client.models.generate_content(
                model='gemini-2.5-flash',
                contents=user_message,
                config=types.GenerateContentConfig(
                    system_instruction=system_prompt,
                    response_mime_type="application/json",
                    response_schema=ProductEvaluation,
                    temperature=0.2,
                ),
            )
            
            # 構造化されたテキストを辞書に変換
            result = json.loads(response.text)
            
            # Merge the generated data with the original data structure needed by app.py
            formatted_product = {
                "name": product_data.get("raw_name", product_data.get("name")),
                "brand": product_data.get("brand", "Unknown"),
                "type": product_data.get("search_category", product_data.get("type", "スキンケア")),
                "price": product_data.get("price", 0),
                "skin_types": result.get("skin_types", []),
                "concerns": result.get("concerns", []),
                "age_min": 15,  # デフォルト値
                "age_max": 65,  # デフォルト値
                "image_url": product_data.get("image_url", ""),
                "amazon_link": product_data.get("amazon_link", ""),
                "rakuten_link": product_data.get("rakuten_link", ""),
                "description": product_data.get("raw_description", "")[:100] + "...", # 短く概要に
                "texture": result.get("texture", ""),
                "ingredients": result.get("ingredients", [])
            }
            
            return formatted_product
            
        except Exception as e:
            if "429" in str(e) or "ResourceExhausted" in str(e) or "Quota" in str(e):
                import time
                wait_time = (attempt + 1) * 15
                print(f"API Rate limit hit. Retrying in {wait_time} seconds... (Attempt {attempt+1}/{max_retries})")
                time.sleep(wait_time)
            else:
                import traceback
                name_for_err = product_data.get("raw_name") or product_data.get("name") or "Unknown"
                print(f"Error evaluating product {name_for_err}: {e}")
                traceback.print_exc()
                return None
    
    print("Max retries exceeded for this product.")
    return None

def main():
    api_key = get_api_key()
    if not api_key:
        print("GEMINI_API_KEY is not set.")
        return
        
    input_file = "sample_raw_products.json"
    if not os.path.exists(input_file):
        print(f"Input file not found: {input_file}")
        return
        
    with open(input_file, "r", encoding="utf-8") as f:
        raw_products = json.load(f)
        
    print(f"Found {len(raw_products)} raw products. Entering evaluation phase...")
    evaluated_products = []
    
    # 仮のスタートID
    current_id = 100
    
    for raw in raw_products:
        print(f" - Evaluating: {raw['name']}...")
        result = parse_with_gemini(raw, api_key)
        if result:
            result["id"] = current_id
            current_id += 1
            evaluated_products.append(result)
            print("   -> Success!")
        else:
            print("   -> Failed.")
            
    # 結果の保存
    output_file = "evaluated_products_output.json"
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(evaluated_products, f, ensure_ascii=False, indent=2)
        
    print(f"Done. Saved to {output_file}")

if __name__ == "__main__":
    main()
