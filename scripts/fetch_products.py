import requests
import toml
import os
import json
import time

# 設定
SECRETS_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), '.streamlit', 'secrets.toml')
OUTPUT_PATH = os.path.join(os.path.dirname(__file__), 'rakuten_raw_products.json')

def load_secrets():
    try:
        with open(SECRETS_PATH, 'r', encoding='utf-8') as f:
            return toml.load(f)
    except Exception as e:
        print(f"Error loading secrets: {e}")
        return {}

def fetch_products_for_category(app_id, affiliate_id, access_key, category_name, keyword, hits=5):
    """
    指定したカテゴリ・キーワードで楽天のスキンケアルージャンルから商品を検索する
    """
    url = "https://openapi.rakuten.co.jp/ichibams/api/IchibaItem/Search/20220601"
    
    # genreId: 100940 = スキンケア（美容・コスメ・香水ジャンル内）
    params = {
        "format": "json",
        "keyword": keyword,
        "applicationId": app_id.replace('-', ''),
        "accessKey": access_key,
        "affiliateId": affiliate_id,
        "genreId": 100940,  # スキンケアジャンル固定
        "hits": hits,
        "sort": "-reviewCount" # レビュー件数が多い順（人気のものを取得）
    }
    
    headers = {
        # 楽天APIシステムの許可ドメイン設定に合わせたヘッダー
        "Referer": "http://example.com",
        "Origin": "http://example.com"
    }
    
    print(f"[{category_name}] を検索中... (keyword: {keyword})")
    response = requests.get(url, params=params, headers=headers)
    
    if response.status_code != 200:
        print(f"エラー発生 ({category_name}): {response.status_code} - {response.text}")
        print("API制限または無効な認証情報のため、開発用のモックデータ（ダミー）を使用します。")
        # 開発を進めるためのモックデータを返す
        mock_items = [{
            "search_category": category_name,
            "raw_name": f"【ダミー】高保湿 {category_name}",
            "price": 1980,
            "raw_description": f"これはAPIエラー時に生成された{category_name}のダミーデータです。ヒアルロン酸・コラーゲン配合で肌の角質層まで浸透。",
            "image_url": "https://placehold.co/300x300/e0e0e0/000000?text=dummy",
            "rakuten_link": "https://rakuten.co.jp/",
            "review_count": 120,
            "review_average": 4.5
        }]
        return mock_items
        
    data = response.json()
    items = []
    
    for item_wrapper in data.get('Items', []):
        item = item_wrapper['Item']
        
        # 取得した商品を整形する（AIに読み込ませる前の生データとして保管）
        img_url = ""
        if item.get('mediumImageUrls') and len(item['mediumImageUrls']) > 0:
            # 楽天の画像の語尾 "?_ex=128x128" などを取り除きプレーンな画像URLにする
            img_url = item['mediumImageUrls'][0]['imageUrl'].split('?')[0]
            
        product_info = {
            "search_category": category_name,
            "raw_name": item.get('itemName'),
            "price": item.get('itemPrice'),
            "raw_description": item.get('itemCaption'),
            "image_url": img_url,
            "rakuten_link": item.get('affiliateUrl', item.get('itemUrl')),
            "review_count": item.get('reviewCount'),
            "review_average": item.get('reviewAverage')
        }
        items.append(product_info)
        
    return items

def main():
    print("=== 楽天商品自動取得スクリプトを開始します ===")
    secrets = load_secrets()
    app_id = secrets.get('RAKUTEN_APP_ID')
    affiliate_id = secrets.get('RAKUTEN_AFFILIATE_ID')
    access_key = secrets.get('RAKUTEN_ACCESS_KEY')
    
    if not app_id or not affiliate_id or not access_key:
        print("エラー: .streamlit/secrets.toml に RAKUTEN_APP_ID, RAKUTEN_AFFILIATE_ID, または RAKUTEN_ACCESS_KEY が見つかりません。")
        return
        
    # アプリの診断ステップに合わせてカテゴリを用意
    categories_to_search = [
        {"name": "クレンジング", "keyword": "クレンジング メイク落とし"},
        {"name": "洗顔", "keyword": "洗顔フォーム"},
        {"name": "化粧水", "keyword": "化粧水 ローション"},
        {"name": "美容液", "keyword": "美容液 セラム"},
        {"name": "乳液", "keyword": "乳液 ミルク"},
        {"name": "クリーム", "keyword": "フェイスクリーム 保湿クリーム"}
    ]
    
    all_products = []
    
    # 順番にAPIを実行
    for cat in categories_to_search:
        # まずは各カテゴリ上位5つを取得
        items = fetch_products_for_category(app_id, affiliate_id, access_key, cat["name"], cat["keyword"], hits=5)
        all_products.extend(items)
        
        # 楽天APIは1秒間に複数回アクセスするとエラー（HTTP/429）になるため、あえて休憩を挟む
        time.sleep(1.5)
        
    # 結果を一時的なJSONとして保存（これを次のステップでGemini AIに渡して綺麗なデータにする）
    with open(OUTPUT_PATH, 'w', encoding='utf-8') as f:
        json.dump(all_products, f, ensure_ascii=False, indent=2)
        
    print(f"\n完了！ {len(all_products)}件の商品データを {OUTPUT_PATH} に保存しました。")
    print("=> 次のステップ: update_db.py を実行して、このデータをAIに分析・整形させてください。")

if __name__ == "__main__":
    main()
