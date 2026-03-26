import os
import toml
import json
import requests
import sys
from datetime import datetime, timedelta, timezone

# Windowsのコンソールで絵文字等の出力エラーを防ぐ
if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

# 設定
SECRETS_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), '.streamlit', 'secrets.toml')
OUTPUT_PATH = os.path.join(os.path.dirname(__file__), 'trending_products.json')

def load_secrets():
    try:
        with open(SECRETS_PATH, 'r', encoding='utf-8') as f:
            return toml.load(f)
    except Exception as e:
        print(f"Error loading secrets: {e}")
        return {}

def fetch_youtube_videos(api_key, query="スキンケア おすすめ | スキンケア ルーティン | 化粧水 おすすめ | 美容液 おすすめ", max_results=3):
    print("YouTubeで最近話題のスキンケア動画を検索中...")
    url = "https://www.googleapis.com/youtube/v3/search"
    
    # 過去30日以内の動画に絞る
    past_30_days = (datetime.now(timezone.utc) - timedelta(days=30)).isoformat("T", "seconds")
    
    params = {
        "part": "snippet",
        "q": query,
        "type": "video",
        "order": "viewCount", # 再生回数が多い順（バズっているもの）
        "publishedAfter": past_30_days,
        "maxResults": max_results,
        "key": api_key,
        "regionCode": "JP"
    }
    
    response = requests.get(url, params=params)
    if response.status_code != 200:
        print(f"YouTube API エラー: {response.text}")
        return []
        
    data = response.json()
    videos = []
    
    for item in data.get("items", []):
        video = {
            "title": item["snippet"]["title"],
            "description": item["snippet"]["description"],
            "channel": item["snippet"]["channelTitle"]
        }
        videos.append(video)
        print(f"発見: 『{video['title']}』 ({video['channel']})")
        
    return videos

def extract_products_with_ai(videos, gemini_api_key):
    print("\nGemini AIを使って動画の概要欄から神アイテム（商品名）を抽出中...")
    
    from google import genai
    from google.genai import types
    from pydantic import BaseModel
    import json
    
    class TrendingOutput(BaseModel):
        products: list[str]
    
    combined_text = ""
    for v in videos:
        combined_text += f"\n【動画タイトル】{v['title']}\n【概要欄】{v['description']}\n"
        
    prompt = f"""
    以下のYouTube美容動画のタイトルと概要欄のテキストから、紹介されている「スキンケア商品（化粧水、美容液、乳液、クリーム、クレンジング、洗顔など）」の具体的な商品名（ブランド名＋商品名）のみを厳密に抽出してください。
    
    重要：
    - メイクアップコスメ（リップ、ファンデーション、クッションファンデ、アイシャドウなど）や、カラーコンタクト、美容家電などの【スキンケア以外の商品】は「絶対に」除外してください。純粋な基礎化粧品（スキンケア）だけを対象とします。
    - 最大10個までに絞ってください。関連性のない言葉は省いてください。
    
    対象テキスト:
    {combined_text}
    """
    
    try:
        client = genai.Client(api_key=gemini_api_key)
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt,
            config=types.GenerateContentConfig(
                temperature=0.2,
                response_mime_type="application/json",
                response_schema=TrendingOutput,
            ),
        )
        
        result_text = response.text.strip()
        
        try:
            parsed_json = json.loads(result_text)
            product_list = parsed_json.get("products", [])
            print(f"AIが {len(product_list)} 個のバズ商品名を抽出しました！")
            for p in product_list:
                print(f" - {p}")
                
            return product_list
        except Exception as json_e:
            print(f"JSON Parse Error: {json_e}")
            print(f"Raw AI Output: {result_text}")
            return []
            
    except Exception as e:
        print(f"AI抽出エラー: {e}")
        import traceback
        traceback.print_exc()
        return []

def main():
    print("=== YouTubeトレンド商品 全自動収集エンジン ===")
    secrets = load_secrets()
    youtube_key = secrets.get('YOUTUBE_API_KEY')
    gemini_key = secrets.get('GEMINI_BACKEND_API_KEY')
    
    if not youtube_key or not gemini_key:
        print("エラー: secrets.toml に YOUTUBE_API_KEY と GEMINI_BACKEND_API_KEY を設定してください。")
        return
        
    videos = fetch_youtube_videos(youtube_key, max_results=3) # 上位3動画を分析
    
    if videos:
        products = extract_products_with_ai(videos, gemini_key)
        
        # 取得した「商品名のリスト」をJSONで保存
        with open(OUTPUT_PATH, 'w', encoding='utf-8') as f:
            json.dump(products, f, ensure_ascii=False, indent=2)
            
        print(f"\n=> 抽出完了！トレンド商品 {len(products)}件 のリストを {OUTPUT_PATH} に一時保存しました。")
        print("=> 次のステップで、この名前リストを使って楽天で実際の商品情報を検索します。")
    else:
        print("動画が見つかりませんでした、またはAPIエラーが発生しました。")

if __name__ == "__main__":
    main()
