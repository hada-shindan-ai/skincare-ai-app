import os
import json
import time

# ai_evaluatorから共通関数をインポート
from ai_evaluator import parse_with_gemini, get_api_key

PRODUCTS_FILE = os.path.join(os.path.dirname(os.path.dirname(__file__)), "products.json")
RAW_DATA_FILE = os.path.join(os.path.dirname(__file__), "rakuten_raw_products.json")

def main():
    print("=== 商品データベース自動更新スクリプト ===")
    
    api_key = get_api_key()
    if not api_key:
        print("エラー: GEMINI_API_KEY が見つかりません。")
        return

    if not os.path.exists(RAW_DATA_FILE):
        print(f"エラー: 生データ({RAW_DATA_FILE})が見つかりません。先に fetch_products.py を実行してください。")
        return

    with open(RAW_DATA_FILE, "r", encoding="utf-8") as f:
        raw_products = json.load(f)

    # 既存のデータベースを読み込み
    if not os.path.exists(PRODUCTS_FILE):
        existing_products = []
        next_id = 1
    else:
        with open(PRODUCTS_FILE, "r", encoding="utf-8") as f:
            existing_products = json.load(f)
        if existing_products:
            next_id = max(p.get("id", 0) for p in existing_products) + 1
        else:
            next_id = 1

    print(f"取得済みの {len(raw_products)} 件の商品データをAIで評価し、データベースに追加します...")
    
    success_count = 0
    skip_count = 0
    
    for i, raw in enumerate(raw_products):
        print(f"\n[{i+1}/{len(raw_products)}] {raw.get('raw_name', '')[:30]}... を評価中")
        
        # 重複チェック（アフィリエイトリンクが同じものは既に登録済みとみなす）
        is_duplicate = False
        raw_link = raw.get("rakuten_link", "")
        if raw_link:
            for p in existing_products:
                if p.get("rakuten_link") == raw_link:
                    is_duplicate = True
                    break
        
        if is_duplicate:
            print("  -> 既にデータベースに存在するためスキップします。")
            skip_count += 1
            continue

        # AIに製品データを渡して評価させる
        result = parse_with_gemini(raw, api_key)
        
        if result:
            result["id"] = next_id
            next_id += 1
            existing_products.append(result)
            success_count += 1
            print("  -> 評価成功！DBに追加しました。")
            
            # 途中で止まっても大丈夫なように1件ごとに上書き保存
            with open(PRODUCTS_FILE, "w", encoding="utf-8") as f:
                json.dump(existing_products, f, ensure_ascii=False, indent=2)
                
        else:
            print("  -> 評価失敗（スキップします）")
            
        # APIのレートリミット対策のため少し待機（無料枠だと1分間に15リクエストまで等の制限があるため）
        # ここでは安全のために 4秒待機 (1分間に15回の制限でも大丈夫なように)
        time.sleep(4)

    print(f"\n完了！ 新たに {success_count} 件の商品を products.json に追加しました。（重複スキップ: {skip_count}件）")
    print("アプリの画面をリロードすると、新しい商品が表示されます！")

if __name__ == "__main__":
    main()
