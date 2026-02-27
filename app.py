import streamlit as st
import json
from streamlit_drawable_canvas import st_canvas
from utils.gemini_handler import GeminiHandler


# ページ設定
st.set_page_config(
    page_title="スキンケア診断 | あなたにぴったりのスキンケアを見つけよう",
    page_icon="assets/ai_avatar.png",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# カスタムCSS（16Personalities風デザイン）
st.markdown("""
<style>
    /* Google Fonts読み込み - Inter（モダン）+ Noto Sans JP */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Noto+Sans+JP:wght@400;500;600;700&display=swap');
    
    /* カラーパレット（16Personalities風） */
    :root {
        --color-purple: #88619A;
        --color-teal: #4298B4;
        --color-green: #33A474;
        --color-yellow: #E4AE3A;
        --color-text: #343C4B;
        --color-text-light: #72809D;
        --color-bg: #F2F3F5;
        --color-card: #FFFFFF;
    }
    
    /* 全体のスタイル */
    * {
        font-family: 'Noto Sans JP', 'Inter', sans-serif !important;
    }
    
    .stApp {
        background: linear-gradient(180deg, #EEF2F6 0%, #F8F9FB 50%, #FFFFFF 100%);
    }
    
    /* メインコンテナ */
    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
        max-width: 650px;
    }
    
    /* ヘッダー */
    .header-container {
        text-align: center;
        padding: 2.5rem 0 2rem 0;
    }
    
    .header-label {
        display: inline-block;
        font-size: 0.75rem;
        letter-spacing: 0.15em;
        text-transform: uppercase;
        color: white;
        font-weight: 600;
        padding: 0.4rem 1rem;
        border-radius: 50px;
        background: linear-gradient(135deg, var(--color-purple) 0%, var(--color-teal) 100%);
        margin-bottom: 1.2rem;
    }
    
    .header-title {
        font-size: 2rem;
        font-weight: 700;
        color: var(--color-text);
        line-height: 1.5;
        margin-bottom: 0.5rem;
    }
    
    .header-title .accent {
        background: linear-gradient(135deg, var(--color-purple) 0%, var(--color-teal) 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }
    
    .header-subtitle {
        color: var(--color-text-light);
        font-size: 1rem;
        font-weight: 400;
        line-height: 1.8;
        margin-top: 1rem;
    }
    
    /* 入力カード */
    .input-card {
        background: white;
        border-radius: 20px;
        padding: 2rem;
        margin: 1.5rem 0;
        box-shadow: 0 2px 12px rgba(0, 0, 0, 0.06);
        border: none;
    }
    
    .input-card h3 {
        color: var(--color-text);
        font-weight: 600;
        margin-bottom: 0.5rem;
        font-size: 1.2rem;
    }
    
    .input-card .card-subtitle {
        color: var(--color-text-light);
        font-size: 0.9rem;
        margin-bottom: 1.5rem;
    }
    
    /* セクションタイトル */
    .section-title {
        font-size: 0.95rem;
        letter-spacing: 0.12em;
        text-transform: uppercase;
        color: var(--color-text-light);
        font-weight: 600;
        margin-bottom: 0.8rem;
        margin-top: 1.2rem;
    }
    
    /* スライダー値表示 */
    .slider-display {
        display: flex;
        align-items: center;
        justify-content: space-between;
        margin-bottom: 1rem;
    }
    
    .slider-value {
        font-size: 2rem;
        font-weight: 700;
        background: linear-gradient(135deg, var(--color-purple) 0%, var(--color-teal) 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }
    
    .slider-range {
        display: flex;
        justify-content: space-between;
        color: var(--color-text-light);
        font-size: 0.75rem;
        margin-top: 0.5rem;
    }
    
    .slider-container {
        background: #F8F9FB;
        border-radius: 16px;
        padding: 1.2rem;
        margin-bottom: 0.5rem;
    }
    
    /* Streamlitのデフォルトスタイル上書き */
    .stSlider > div > div > div {
        background: linear-gradient(90deg, #E8D5F0, var(--color-purple)) !important;
    }
    
    .stSlider > div > div > div > div {
        background-color: var(--color-purple) !important;
        border: 3px solid white !important;
        box-shadow: 0 2px 8px rgba(136, 97, 154, 0.4) !important;
    }
    
    .stSelectbox > div > div {
        border-radius: 12px !important;
        border: 2px solid #E5E7EB !important;
        background-color: white !important;
    }
    
    .stMultiSelect > div > div {
        border-radius: 12px !important;
        border: 2px solid #E5E7EB !important;
        background-color: white !important;
    }
    
    .stMultiSelect [data-baseweb="tag"] {
        background: linear-gradient(135deg, var(--color-purple) 0%, var(--color-teal) 100%) !important;
        border: none !important;
        border-radius: 50px !important;
        color: white !important;
    }
    
    /* Expander Icon Text Overlap Fix - Force hide Material icons */
    [data-testid="stExpander"] details summary svg {
        display: none !important;
    }
    
    [data-testid="stExpander"] details summary {
        list-style-type: none !important;
    }
    
    [data-testid="stExpander"] details summary::-webkit-details-marker {
        display: none !important;
    }
    
    /* Hide the "keyboard_arrow_right" ligature text node */
    .st-emotion-cache-1gcp3n2,
    .st-emotion-cache-7q0xed,
    .stIcon,
    [data-testid="stExpanderToggleIcon"] {
        display: none !important;
        opacity: 0 !important;
        font-size: 0 !important;
        width: 0 !important;
        height: 0 !important;
        visibility: hidden !important;
    }
    
    /* 診断ボタン */
    .stButton > button {
        background: linear-gradient(135deg, var(--color-purple) 0%, var(--color-teal) 100%) !important;
        color: white !important;
        border: none !important;
        border-radius: 50px !important;
        padding: 1rem 2.5rem !important;
        font-size: 1.05rem !important;
        font-weight: 600 !important;
        width: 100% !important;
        transition: all 0.3s ease !important;
        box-shadow: 0 4px 15px rgba(136, 97, 154, 0.35) !important;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 6px 20px rgba(136, 97, 154, 0.45) !important;
    }
    
    /* 結果カード */
    .result-card {
        background: white;
        border-radius: 20px;
        padding: 1.8rem;
        margin: 1rem 0;
        box-shadow: 0 2px 12px rgba(0, 0, 0, 0.06);
        transition: all 0.3s ease;
    }
    
    .result-card:hover {
        transform: translateY(-3px);
        box-shadow: 0 8px 25px rgba(0, 0, 0, 0.1);
    }
    
    .result-rank {
        display: inline-block;
        background: linear-gradient(135deg, var(--color-green) 0%, var(--color-teal) 100%);
        color: white;
        font-weight: 600;
        padding: 0.4rem 1.2rem;
        border-radius: 50px;
        font-size: 0.8rem;
        margin-bottom: 1rem;
    }
    
    .product-image {
        max-width: 140px;
        width: 100%;
        height: auto;
        border-radius: 12px;
        object-fit: cover;
        box-shadow: 0 4px 10px rgba(0, 0, 0, 0.05);
    }
    
    .result-product-name {
        font-size: 1.3rem;
        font-weight: 700;
        color: var(--color-text);
        margin-bottom: 0.3rem;
    }
    
    .result-brand {
        color: var(--color-purple);
        font-size: 0.9rem;
        font-weight: 600;
        margin-bottom: 0.8rem;
    }
    
    .result-price {
        font-size: 1.4rem;
        font-weight: 700;
        color: var(--color-green);
        margin: 0.8rem 0;
    }
    
    .result-description {
        color: var(--color-text-light);
        font-size: 0.9rem;
        line-height: 1.7;
        margin-bottom: 1rem;
    }
    
    .result-tags {
        margin-bottom: 1rem;
    }
    
    .result-tag {
        display: inline-block;
        background: #F3F0F7;
        color: var(--color-purple);
        padding: 0.35rem 0.9rem;
        border-radius: 50px;
        font-size: 0.75rem;
        font-weight: 500;
        margin-right: 0.4rem;
        margin-bottom: 0.4rem;
    }
    
    /* アフィリエイトボタン */
    .affiliate-buttons {
        display: flex;
        gap: 0.8rem;
        margin-top: 1.2rem;
    }
    
    .amazon-btn {
        display: inline-block;
        background: linear-gradient(135deg, #FF9900 0%, #FFB347 100%);
        color: white !important;
        text-decoration: none !important;
        padding: 0.85rem 1.2rem;
        border-radius: 50px;
        font-weight: 600;
        font-size: 0.85rem;
        text-align: center;
        flex: 1;
        transition: all 0.3s ease;
        box-shadow: 0 3px 10px rgba(255, 153, 0, 0.3);
    }
    
    .amazon-btn:hover {
        transform: translateY(-2px);
        box-shadow: 0 5px 15px rgba(255, 153, 0, 0.4);
    }
    
    .rakuten-btn {
        display: inline-block;
        background: linear-gradient(135deg, #BF0000 0%, #E53935 100%);
        color: white !important;
        text-decoration: none !important;
        padding: 0.85rem 1.2rem;
        border-radius: 50px;
        font-weight: 600;
        font-size: 0.85rem;
        text-align: center;
        flex: 1;
        transition: all 0.3s ease;
        box-shadow: 0 3px 10px rgba(191, 0, 0, 0.3);
    }
    
    .rakuten-btn:hover {
        transform: translateY(-2px);
        box-shadow: 0 5px 15px rgba(191, 0, 0, 0.4);
    }
    
    /* 結果ヘッダー */
    .result-header {
        text-align: center;
        padding: 1.5rem 0 1rem 0;
    }
    
    .result-header h2 {
        color: var(--color-text);
        font-size: 1.5rem;
        font-weight: 700;
    }
    
    .result-header .accent {
        background: linear-gradient(135deg, var(--color-purple) 0%, var(--color-teal) 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }
    
    /* フッター */
    .footer {
        text-align: center;
        padding: 2rem 0;
        color: var(--color-text-light);
        font-size: 0.8rem;
        line-height: 1.8;
    }
    
    /* 画像スタイル */
    .product-image {
        width: 100%;
        max-width: 150px;
        border-radius: 16px;
        margin-bottom: 1rem;
    }
    
    /* 詳細ページスタイル */
    .detail-container {
        background: white;
        border-radius: 20px;
        padding: 2.5rem;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
    }
    
    .detail-header {
        margin-bottom: 2rem;
        border-bottom: 2px solid #F2F3F5;
        padding-bottom: 1.5rem;
    }

    .detail-section-title {
        font-size: 1.1rem;
        font-weight: 700;
        color: var(--color-text);
        margin: 2rem 0 1rem 0;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }
    
    .detail-section-title::before {
        content: '';
        display: block;
        width: 6px;
        height: 24px;
        background: linear-gradient(180deg, var(--color-purple) 0%, var(--color-teal) 100%);
        border-radius: 10px;
    }

    .texture-box {
        background: #F8F9FB;
        padding: 1.5rem;
        border-radius: 16px;
        line-height: 1.8;
        color: var(--color-text);
        border: 1px solid #EEF2F6;
    }

    .ingredient-card {
        background: white;
        border: 1px solid #EEF2F6;
        border-radius: 12px;
        padding: 1.2rem;
        margin-bottom: 1rem;
        transition: all 0.3s ease;
    }
    
    .ingredient-card:hover {
        border-color: var(--color-teal);
        box-shadow: 0 4px 12px rgba(66, 152, 180, 0.1);
    }

    .ingredient-name {
        font-weight: 700;
        color: var(--color-teal);
        font-size: 1.05rem;
        margin-bottom: 0.4rem;
    }
    
    .ingredient-benefit {
        font-weight: 600;
        color: var(--color-text);
        margin-bottom: 0.6rem;
    }
    
    .evidence-box {
        background: #F0F7FA;
        padding: 0.8rem 1rem;
        border-radius: 8px;
        font-size: 0.8rem;
        color: #4A5568;
        line-height: 1.6;
    }
    
    .evidence-label {
        font-weight: 700;
        color: var(--color-teal);
        font-size: 0.7rem;
        margin-bottom: 0.2rem;
        display: block;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }

    .back-btn-container {
        margin-bottom: 1.5rem;
    }
    
    /* 非表示 */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
</style>
""", unsafe_allow_html=True)


def create_chart_initial_drawing(width=300, height=250, marker_pos=None):
    """Fabric.js形式でチャートの初期描画データを作成する
    marker_pos: (x, y) のタプル。指定された場合、その位置に点を描画する。
    """
    cx = width / 2
    cy = height / 2
    
    objects = []
    
    # 共通設定
    line_props = {"stroke": "#e0e0e0", "strokeWidth": 2, "selectable": False, "evented": False}
    text_props = {"fill": "#888888", "fontSize": 12, "fontFamily": "sans-serif", "selectable": False, "evented": False}
    label_props = {"fill": "#cccccc", "fontSize": 14, "fontFamily": "sans-serif", "fontWeight": "bold", "selectable": False, "evented": False}

    # 枠線
    objects.append({
        "type": "rect",
        "left": 2, "top": 2, "width": width-4, "height": height-4,
        "fill": "transparent", "stroke": "#eeeeee", "strokeWidth": 4,
        "selectable": False, "evented": False
    })
    
    # 軸線
    objects.append({"type": "line", "x1": cx, "y1": 20, "x2": cx, "y2": height-20, **line_props})
    objects.append({"type": "line", "x1": 20, "y1": cy, "x2": width-20, "y2": cy, **line_props})

    # 軸ラベル
    # 水分
    objects.append({"type": "text", "text": "水分 多", "left": cx-20, "top": 5, **text_props})
    objects.append({"type": "text", "text": "水分 少", "left": cx-20, "top": height-20, **text_props})
    # 皮脂
    objects.append({"type": "text", "text": "皮脂 多", "left": width-45, "top": cy-20, **text_props})
    objects.append({"type": "text", "text": "皮脂 少", "left": 5, "top": cy-20, **text_props})
    
    # エリア名
    objects.append({"type": "text", "text": "脂性肌", "left": width-60, "top": 40, **label_props})
    objects.append({"type": "text", "text": "普通肌", "left": 40, "top": 40, **label_props})
    objects.append({"type": "text", "text": "混合肌", "left": width-60, "top": height-50, **label_props})
    objects.append({"type": "text", "text": "乾燥肌", "left": 40, "top": height-50, **label_props})
    
    return {"version": "4.4.0", "objects": objects}


def load_products():
    """商品データを読み込む"""
    with open("products.json", "r", encoding="utf-8") as f:
        return json.load(f)


def create_chart_background(width=300, height=250):
    """肌質診断チャートの背景画像を生成する"""
    # 白背景
    img = Image.new('RGB', (width, height), color='white')
    draw = ImageDraw.Draw(img)
    
def create_chart_initial_drawing(width=300, height=250, marker_pos=None, marker_pos2=None):
    """Fabric.js形式でチャートの初期描画データを作成する
    marker_pos: (x, y) のタプル。指定された場合、その位置に点を描画する（紫）。
    marker_pos2: (x, y) のタプル。指定された場合、その位置に点を描画する（ティール）。
    """
    cx = width / 2
    cy = height / 2
    
    objects = []
    
    # 共通設定 (背景オブジェクト用: 完全にロックする)
    lock_props = {
        "selectable": False, "evented": False,
        "lockMovementX": True, "lockMovementY": True,
        "lockRotation": True, 
        "lockScalingX": True, "lockScalingY": True,
        "hoverCursor": "default"
    }
    
    line_props = {"stroke": "#e0e0e0", "strokeWidth": 2, **lock_props}
    text_props = {"fill": "#888888", "fontSize": 12, "fontFamily": "sans-serif", **lock_props}
    label_props = {"fill": "#cccccc", "fontSize": 14, "fontFamily": "sans-serif", "fontWeight": "bold", **lock_props}

    # 枠線 (Rectではなく4本のLineで描画して、中央のクリック判定を回避)
    # 上
    objects.append({"type": "line", "x1": 0, "y1": 0, "x2": width, "y2": 0, "stroke": "#eeeeee", "strokeWidth": 4, **lock_props})
    # 下
    objects.append({"type": "line", "x1": 0, "y1": height, "x2": width, "y2": height, "stroke": "#eeeeee", "strokeWidth": 4, **lock_props})
    # 左
    objects.append({"type": "line", "x1": 0, "y1": 0, "x2": 0, "y2": height, "stroke": "#eeeeee", "strokeWidth": 4, **lock_props})
    # 右
    objects.append({"type": "line", "x1": width, "y1": 0, "x2": width, "y2": height, "stroke": "#eeeeee", "strokeWidth": 4, **lock_props})
    
    # 軸線
    objects.append({"type": "line", "x1": cx, "y1": 20, "x2": cx, "y2": height-20, **line_props})
    objects.append({"type": "line", "x1": 20, "y1": cy, "x2": width-20, "y2": cy, **line_props})

    # 軸ラベル
    # 水分
    objects.append({"type": "text", "text": "水分 多", "left": cx-20, "top": 5, **text_props})
    objects.append({"type": "text", "text": "水分 少", "left": cx-20, "top": height-20, **text_props})
    # 皮脂
    objects.append({"type": "text", "text": "皮脂 多", "left": width-45, "top": cy-20, **text_props})
    objects.append({"type": "text", "text": "皮脂 少", "left": 5, "top": cy-20, **text_props})
    
    
    # マーカー1（現在の点：紫）
    if marker_pos:
        mx, my = marker_pos
        objects.append({
            "type": "circle",
            "left": mx, "top": my,
            "radius": 6,
            "fill": "#88619A", # var(--color-purple)
            "stroke": "white",
            "strokeWidth": 2,
            "originX": "center", "originY": "center",
            "selectable": True, "evented": True,
            "hasControls": False, "hasBorders": False,
            "hoverCursor": "move"
        })

    # マーカー2（比較点：ティール）
    if marker_pos2:
        mx2, my2 = marker_pos2
        objects.append({
            "type": "circle",
            "left": mx2, "top": my2,
            "radius": 6,
            "fill": "#2A9D8F", # Teal
            "stroke": "white",
            "strokeWidth": 2,
            "originX": "center", "originY": "center",
            "selectable": True, "evented": True,
            "hasControls": False, "hasBorders": False,
            "hoverCursor": "move"
        })
    
    return {"version": "4.4.0", "objects": objects}




def determine_skin_type(moisture, oil):
    """水分量と皮脂量から肌質を判定する"""
    if moisture >= 50:
        # 高水分
        if oil >= 50:
            return "脂性肌"  # 高皮脂・高水分（脂性）
        else:
            return "普通肌"  # 低皮脂・高水分（理想的）
    else:
        # 低水分
        if oil >= 50:
            return "混合肌"  # 高皮脂・低水分（インナードライ）
        else:
            return "乾燥肌"  # 低皮脂・低水分


def determine_combined_skin_type(t_moisture, t_oil, u_moisture, u_oil):
    """TゾーンとUゾーンから総合的な肌タイプを判定する
    
    判定基準:
    - 普通肌: T(皮脂30-55,水分45+) & U(皮脂30-55,水分45+)
    - 乾燥肌: T(皮脂0-30,水分0-40) & U(皮脂0-20,水分0-40)
    - 脂性肌: T(皮脂60+) & U(皮脂60+)
    - 混合肌: T(皮脂60+) & U(皮脂30以下)
    """
    
    # 混合肌: Tゾーンが脂っぽく(60+)、Uゾーンが乾く(30以下)
    if t_oil >= 60 and u_oil <= 30:
        return "混合肌", "Tゾーンはテカりやすく、Uゾーンは乾燥しがち。部位別のケアが効果的です。"
    
    # 脂性肌: 両方とも皮脂60以上
    if t_oil >= 60 and u_oil >= 60:
        return "脂性肌", "全体的に皮脂が多め。さっぱりタイプのスキンケアがおすすめです。"
    
    # 乾燥肌: T(皮脂0-30,水分0-40) & U(皮脂0-20,水分0-40)
    if t_oil <= 30 and t_moisture <= 40 and u_oil <= 20 and u_moisture <= 40:
        return "乾燥肌", "全体的に水分・油分が少なめ。しっかり保湿しましょう。"
    
    # 普通肌: T(皮脂30-55,水分45+) & U(皮脂30-55,水分45+)
    if (30 <= t_oil <= 55 and t_moisture >= 45 and 
        30 <= u_oil <= 55 and u_moisture >= 45):
        return "普通肌", "バランスの取れた肌状態です。現在のケアを続けましょう。"
    
    # どれにも該当しない場合（中間的な状態）
    # 優先順位: 混合肌っぽい傾向があるかチェック
    if t_oil > u_oil + 20:  # TがUより明らかに脂っぽい
        return "混合肌", "Tゾーンの皮脂が多めです。部位別のケアを心がけましょう。"
    
    # デフォルト: 普通肌寄り
    return "普通肌", "おおむねバランスが取れています。保湿ケアを心がけましょう。"


def calculate_score(product, age, skin_type, concerns, budget, is_sensitive):
    """商品のスコアを計算する"""
    score = 0
    
    # 肌質マッチ: +30点
    if skin_type in product["skin_types"]:
        score += 30
    
    # 敏感肌対応: +20点
    if is_sensitive and "敏感肌" in product["skin_types"]:
        score += 20
    
    # 悩みマッチ: 各+15点
    for concern in concerns:
        if concern in product["concerns"]:
            score += 15
    
    # 年齢マッチ: +20点
    if product["age_min"] <= age <= product["age_max"]:
        score += 20
    
    # 予算内: +20点
    if product["price"] <= budget:
        score += 20
    elif product["price"] <= budget * 1.2:
        score += 10
    
    return score


def get_recommendations(products, age, skin_type, concerns, budget, is_sensitive, target_items):
    """条件に合う商品を抽出する。フルラインの場合は各カテゴリから1つずつ、合計5つ。"""
    
    if "フルライン（一式）" in target_items:
        categories = ["洗顔", "化粧水", "美容液", "乳液", "クリーム"]
        final_recommendations = []
        
        for category in categories:
            # 該当カテゴリの商品だけをフィルタリング
            category_products = [p for p in products if p.get("type") == category]
            if not category_products:
                continue
                
            scored = []
            for product in category_products:
                score = calculate_score(product, age, skin_type, concerns, budget, is_sensitive)
                scored.append((product, score))
            
            # そのカテゴリで最もスコアが高いものを1つ選択
            scored.sort(key=lambda x: x[1], reverse=True)
            if scored:
                final_recommendations.append(scored[0])
                
        return final_recommendations
        
    else:
        final_recommendations = []
        
        if not target_items:
            # ターゲット指定がない場合は全体から上位3つ
            scored_products = []
            for product in products:
                score = calculate_score(product, age, skin_type, concerns, budget, is_sensitive)
                scored_products.append((product, score))
            scored_products.sort(key=lambda x: x[1], reverse=True)
            return scored_products[:3]
            
        # ターゲット指定がある場合は、指定された各カテゴリから選出
        # ただし、ターゲットが1つだけの場合はそのカテゴリの上位3つを返す
        if len(target_items) == 1:
            category = target_items[0]
            category_products = [p for p in products if p.get("type") == category]
            
            scored = []
            for product in category_products:
                score = calculate_score(product, age, skin_type, concerns, budget, is_sensitive)
                scored.append((product, score))
            
            scored.sort(key=lambda x: x[1], reverse=True)
            return scored[:3]
            
        # 複数ターゲット指定がある場合は、指定された各カテゴリから1つずつ選出
        for category in target_items:
            category_products = [p for p in products if p.get("type") == category]
            if not category_products:
                continue
                
            scored = []
            for product in category_products:
                score = calculate_score(product, age, skin_type, concerns, budget, is_sensitive)
                scored.append((product, score))
            
            scored.sort(key=lambda x: x[1], reverse=True)
            if scored:
                final_recommendations.append(scored[0])
                
        # もし選出結果が空なら、全体から3つ
        if not final_recommendations:
            scored_products = []
            for product in products:
                score = calculate_score(product, age, skin_type, concerns, budget, is_sensitive)
                scored_products.append((product, score))
            scored_products.sort(key=lambda x: x[1], reverse=True)
            return scored_products[:3]
            
        return final_recommendations



def render_detail_page(product):
    """商品詳細ページを表示する"""
    if st.button("← 診断結果に戻る", key="back_btn"):
        st.session_state.selected_product_id = None
        st.rerun()

    # HTMLを構築
    html_content = f"""
<div class="detail-container">
<div class="detail-header">
<span class="result-brand">{product["brand"]} | {product["type"]}</span>
<h2 class="result-product-name" style="font-size: 1.8rem; margin-top: 0.5rem;">{product["name"]}</h2>
<div class="result-price" style="font-size: 1.5rem;">¥{product["price"]:,}</div>
</div>

<div style="display: flex; justify-content: center; margin-bottom: 2rem;">
<img src="{product["image_url"]}" style="width: 100%; max-width: 300px; border-radius: 20px;">
</div>

<div class="detail-section-title">使用感・テクスチャー</div>
<div class="texture-box">
{product.get("texture", "情報がありません")}
</div>

<div class="detail-section-title">注目成分とエビデンス</div>
"""

    for ingredient in product.get("ingredients", []):
        html_content += f"""
<div class="ingredient-card">
<div class="ingredient-name">{ingredient["name"]}</div>
<div class="ingredient-benefit">{ingredient["benefit"]}</div>
<div class="evidence-box">
<span class="evidence-label">Scientific Evidence</span>
{ingredient["evidence"]}
</div>
</div>
"""
        
    html_content += """
<div class="detail-section-title">購入リンク</div>
<div class="affiliate-buttons" style="margin-top: 1rem;">
"""
    
    html_content += f"""
<a href="{product["amazon_link"]}" target="_blank" class="amazon-btn">Amazonで購入</a>
<a href="{product["rakuten_link"]}" target="_blank" class="rakuten-btn">楽天で購入</a>
"""
            
    html_content += "</div></div>"

    st.markdown(html_content, unsafe_allow_html=True)



def render_ai_chat():
    """AI相談室タブの表示"""
    st.markdown('<div class="result-header"><h2>AI相談室 <span class="accent">Beta</span></h2></div>', unsafe_allow_html=True)
    st.markdown('<p style="text-align: center; color: #666; font-size: 0.9rem;">あなたの肌質データに基づき、医学的エビデンスを用いて回答します。</p>', unsafe_allow_html=True)

    # Initialize Chat History
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []
    
    # Handler (simple init)
    handler = GeminiHandler()

    # Display Chat History
    for role, message, sources in st.session_state.chat_history:
        avatar = "👤" if role == "user" else "assets/ai_avatar.png"
        with st.chat_message(role, avatar=avatar):
            st.markdown(message)
            if sources:
                 with st.expander("📚 参照ソースを確認"):
                     for src in sources:
                         st.markdown(f"- {src}")
    
    # Input
    if prompt := st.chat_input("スキンケアについて質問する..."):
        # Display user message
        with st.chat_message("user", avatar="👤"):
            st.markdown(prompt)
        
        # Context
        context = {
            "skin_type": st.session_state.get("combined_skin_type", "未診断"),
            "age": st.session_state.get("age", "不明"),
            "budget": st.session_state.get("budget", "不明"),
            "concerns": st.session_state.get("concerns", []),
            "target_items": st.session_state.get("target_items", [])
        }
        
        # Generate
        with st.chat_message("assistant", avatar="assets/ai_avatar.png"):
            with st.spinner("Searching medical databases & verifying sources..."):
                response_text, metadata = handler.get_response(prompt, context, st.session_state.chat_history)
                
                st.markdown(response_text)
                
                # Parse Sources
                source_htmls = []
                if metadata:
                    st.markdown("---")
                    st.caption("🔍 **Source Grounding**")
                    # metadata.grounding_chunks (list of GroundingChunk)
                    # chunk.web (Web object: uri, title)
                    if hasattr(metadata, 'grounding_chunks'):
                        for chunk in metadata.grounding_chunks:
                            if hasattr(chunk, 'web') and chunk.web:
                                title = chunk.web.title or "Source"
                                uri = chunk.web.uri
                                link_md = f"[{title}]({uri})"
                                st.markdown(f"- {link_md}")
                                source_htmls.append(link_md)
        
        # Save to history
        st.session_state.chat_history.append(("user", prompt, None))
        st.session_state.chat_history.append(("assistant", response_text, source_htmls))


def render_diagnosis_flow():
    # ヘッダー
    st.markdown("""
<div class="header-container">
<p class="header-label">Personalized Skincare</p>
<h1 class="header-title">あなたの肌に、<br>確かな<span class="accent">答え</span>を。</h1>
<p class="header-subtitle">肌質・年齢・悩みを分析して<br>今のあなたにベストな選択を。</p>

<!-- 3ステップフロー -->
<div style="background: white; border-radius: 20px; padding: 2rem; margin-top: 2rem; box-shadow: 0 4px 20px rgba(0,0,0,0.05);">
<div style="text-align: center; margin-bottom: 2rem;">
<span style="background: #F0F7FA; color: var(--color-teal); font-weight: 700; padding: 0.5rem 1.5rem; border-radius: 50px; font-size: 0.9rem;">3ステップで完了</span>
<h3 style="margin-top: 1rem; font-size: 1.3rem; color: var(--color-text);">自分に合うスキンケアの見つけ方</h3>
</div>

<div style="display: flex; justify-content: space-between; gap: 1rem; text-align: left;">
<!-- Step 1 -->
<div style="flex: 1; background: #F8F9FB; padding: 1.5rem; border-radius: 16px; position: relative;">
<div style="display: flex; align-items: center; margin-bottom: 1rem;">
<div style="width: 32px; height: 32px; background: var(--color-purple); color: white; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-weight: 700; margin-right: 10px; flex-shrink: 0;">1</div>
<div style="font-weight: 700; color: var(--color-text); font-size: 1rem;">情報を入力</div>
</div>
<div style="font-size: 0.85rem; color: var(--color-text-light); line-height: 1.6;">
年齢・肌質・お悩みを入力。<br>
<span style="color: var(--color-purple); font-weight: 600; font-size: 0.8rem;">※個人情報は不要です</span>
</div>
<div style="font-size: 3rem; position: absolute; bottom: 10px; right: 10px; opacity: 0.1;">📝</div>
</div>

<div style="display: flex; align-items: center; color: #DAE0E7; font-size: 1.5rem;">▶</div>

<!-- Step 2 -->
<div style="flex: 1; background: #F8F9FB; padding: 1.5rem; border-radius: 16px; position: relative;">
<div style="display: flex; align-items: center; margin-bottom: 1rem;">
<div style="width: 32px; height: 32px; background: var(--color-purple); color: white; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-weight: 700; margin-right: 10px; flex-shrink: 0;">2</div>
<div style="font-weight: 700; color: var(--color-text); font-size: 1rem;">AIが分析</div>
</div>
<div style="font-size: 0.85rem; color: var(--color-text-light); line-height: 1.6;">
あなたの肌データを元に、<br>最適なスキンケアを解析。
</div>
<div style="font-size: 3rem; position: absolute; bottom: 10px; right: 10px; opacity: 0.1;">🤖</div>
</div>

<div style="display: flex; align-items: center; color: #DAE0E7; font-size: 1.5rem;">▶</div>

<!-- Step 3 -->
<div style="flex: 1; background: #F8F9FB; padding: 1.5rem; border-radius: 16px; position: relative;">
<div style="display: flex; align-items: center; margin-bottom: 1rem;">
<div style="width: 32px; height: 32px; background: var(--color-purple); color: white; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-weight: 700; margin-right: 10px; flex-shrink: 0;">3</div>
<div style="font-weight: 700; color: var(--color-text); font-size: 1rem;">結果を確認</div>
</div>
<div style="font-size: 0.85rem; color: var(--color-text-light); line-height: 1.6;">
あなただけの処方箋を表示。<br>そのまま購入も可能。
</div>
<div style="font-size: 3rem; position: absolute; bottom: 10px; right: 10px; opacity: 0.1;">✨</div>
</div>
</div>
</div>
</div>
""", unsafe_allow_html=True)
    
    # 商品データ読み込み
    products = load_products()
    
    # セッション状態の初期化
    if "show_results" not in st.session_state:
        st.session_state.show_results = False
    if "age" not in st.session_state:
        st.session_state.age = 30
    if "budget" not in st.session_state:
        st.session_state.budget = 4000
    if "selected_product_id" not in st.session_state:
        st.session_state.selected_product_id = None
        
    # 詳細ページ表示ロジック
    if st.session_state.selected_product_id is not None:
        product = next((p for p in products if p["id"] == st.session_state.selected_product_id), None)
        if product:
            render_detail_page(product)
            return

    # 入力フォーム
    st.markdown('<div class="input-card">', unsafe_allow_html=True)
    st.markdown('<h3>Profile Setup</h3>', unsafe_allow_html=True)
    st.markdown('<p class="card-subtitle">より正確な診断のため、<br>あなたの肌情報を教えてください。</p>', unsafe_allow_html=True)
    
    # 年齢
    st.markdown('<p class="section-title">年齢 <span style="font-size: 0.6em; margin-left: 5px; opacity: 0.6; font-weight: 500;">AGE</span></p>', unsafe_allow_html=True)
    # st.markdown('<div class="slider-container">', unsafe_allow_html=True) は削除（レイアウト崩れ対策）
    age = st.number_input(
        "年齢を入力",
        min_value=0,
        max_value=100,
        value=st.session_state.age,
        step=1,
        key="age_input",
        label_visibility="collapsed"
    )
    st.session_state.age = age
    # st.markdown('</div>', unsafe_allow_html=True) は削除
    
    # 性別
    st.markdown('<p class="section-title">性別 <span style="font-size: 0.6em; margin-left: 5px; opacity: 0.6; font-weight: 500;">GENDER</span></p>', unsafe_allow_html=True)
    gender = st.selectbox(
        "性別を選択",
        options=["女性", "男性", "その他"],
        label_visibility="collapsed"
    )
    

    # 肌質（クリック可能なインタラクティブグラフ）
    st.markdown('<p class="section-title">肌質 <span style="font-size: 0.6em; margin-left: 5px; opacity: 0.6; font-weight: 500;">SKIN TYPE</span></p>', unsafe_allow_html=True)
    st.markdown('<p style="font-size: 0.8rem; color: #888; margin-bottom: 0.5rem;">チャートをドラッグして、各ゾーンの肌状態を教えてください。<br><span style="color: #88619A; font-weight: bold;">●紫：Tゾーン</span>（おでこ・鼻）/ <span style="color: #2A9D8F; font-weight: bold;">●緑：Uゾーン</span>（頬・あご）</p>', unsafe_allow_html=True)
    
    # デフォルト値（初回または保存された値）
    moisture = st.session_state.get("moisture", 50)
    oil = st.session_state.get("oil", 50)
    # マーカー2（Uゾーン）のデフォルト
    moisture2 = st.session_state.get("moisture2", 80)
    oil2 = st.session_state.get("oil2", 20)
    
    # 座標の初期化（初回のみ）
    if "canvas_x" not in st.session_state:
        st.session_state.canvas_x = (oil / 100) * 320
    if "canvas_y" not in st.session_state:
        st.session_state.canvas_y = 280 - ((moisture / 100) * 280)
        
    if "canvas_x2" not in st.session_state:
        st.session_state.canvas_x2 = (oil2 / 100) * 320
    if "canvas_y2" not in st.session_state:
        st.session_state.canvas_y2 = 280 - ((moisture2 / 100) * 280)

    # チャートの初期描画データ生成（初回のみ生成してキャッシュ）
    # チャートの初期描画データ生成（初回のみ生成してキャッシュ）
    # keyを変更してキャッシュを強制更新 (drawing_v7 -> drawing_v8)
    if "drawing_v8" not in st.session_state:
        st.session_state.drawing_v8 = create_chart_initial_drawing(
            width=320, 
            height=280, 
            marker_pos=(st.session_state.canvas_x, st.session_state.canvas_y),
            marker_pos2=(st.session_state.canvas_x2, st.session_state.canvas_y2)
        )
    
    initial_drawing = st.session_state.drawing_v8
    
    # Canvasの表示（中央寄せ）
    col1, col2, col3 = st.columns([1, 1.8, 1])
    with col2:
        canvas_result = st_canvas(
            fill_color="rgba(136, 97, 154, 0.8)",  # 紫色（透過）
            stroke_width=0,
            initial_drawing=initial_drawing, # 画像ではなくベクターデータとして背景を描画
            update_streamlit=True,
            width=320,
            height=280,
            drawing_mode="transform", # ドラッグモード
            key="skin_canvas_drag_v3", # キー更新
            display_toolbar=False, 
        )
    
    # クリック（ドラッグ）データの取得と変換
    if canvas_result.json_data is not None:
        objects = canvas_result.json_data["objects"]
        
        for obj in objects:
            if obj["type"] == "circle":
                # 色で識別
                fill_color = obj.get("fill", "").upper()
                x = obj["left"]
                y = obj["top"]
                
                # 座標(0-320, 0-280) を水分・皮脂(0-100)に変換
                c_oil = int((x / 320) * 100)
                c_moisture = int(((280 - y) / 280) * 100)
                # 範囲制限
                c_oil = max(0, min(100, c_oil))
                c_moisture = max(0, min(100, c_moisture))

                if fill_color == "#88619A": # 紫（Tゾーン）
                    st.session_state.canvas_x = x
                    st.session_state.canvas_y = y
                    st.session_state.moisture = c_moisture
                    st.session_state.oil = c_oil
                    moisture = c_moisture
                    oil = c_oil
                elif fill_color == "#2A9D8F": # ティール（Uゾーン）
                    st.session_state.canvas_x2 = x
                    st.session_state.canvas_y2 = y
                    st.session_state.moisture2 = c_moisture
                    st.session_state.oil2 = c_oil
                    moisture2 = c_moisture
                    oil2 = c_oil
            
    # 値の保存 (rerunしない場合のため)
    st.session_state.moisture = moisture
    st.session_state.oil = oil
    st.session_state.moisture2 = moisture2
    st.session_state.oil2 = oil2
    
    # 肌質判定（各ゾーン + 総合判定）
    skin_type = determine_skin_type(moisture, oil)
    skin_type2 = determine_skin_type(moisture2, oil2)
    combined_type, advice = determine_combined_skin_type(moisture, oil, moisture2, oil2)
    # AI相談用にセッション保存
    st.session_state.combined_skin_type = combined_type
    
    st.markdown(f"""
    <div style="text-align: center; margin-top: 1rem;">
        <div style="display: flex; justify-content: center; gap: 1rem; margin-bottom: 1rem;">
            <div style="background: rgba(136, 97, 154, 0.1); padding: 0.8rem 1.2rem; border-radius: 12px; border-left: 4px solid #88619A;">
                <div style="font-size: 0.85rem; color: #88619A; font-weight: bold;">●Tゾーン</div>
                <div style="font-size: 0.85rem; color: #666;">水分{moisture} / 皮脂{oil}</div>
            </div>
            <div style="background: rgba(42, 157, 143, 0.1); padding: 0.8rem 1.2rem; border-radius: 12px; border-left: 4px solid #2A9D8F;">
                <div style="font-size: 0.85rem; color: #2A9D8F; font-weight: bold;">●Uゾーン</div>
                <div style="font-size: 0.85rem; color: #666;">水分{moisture2} / 皮脂{oil2}</div>
            </div>
        </div>
        <div style="background: linear-gradient(135deg, rgba(136,97,154,0.15), rgba(42,157,143,0.15)); padding: 1rem 1.5rem; border-radius: 16px; margin-top: 0.5rem;">
            <div style="font-size: 0.9rem; color: #666; margin-bottom: 0.3rem;">総合診断</div>
            <div style="font-size: 1.6rem; font-weight: bold; color: var(--color-text);">{combined_type}</div>
            <div style="font-size: 0.85rem; color: #888; margin-top: 0.3rem;">{advice}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # skin_typeのセレクトボックスは削除
    
    # 敏感肌チェック
    st.markdown('<p class="section-title" style="margin-top: 1rem;">敏感肌 <span style="font-size: 0.6em; margin-left: 5px; opacity: 0.6; font-weight: 500;">SENSITIVE SKIN</span></p>', unsafe_allow_html=True)
    is_sensitive_selection = st.radio(
        "敏感肌ですか？",
        options=["いいえ", "はい"],
        horizontal=True,
        label_visibility="collapsed"
    )
    is_sensitive = (is_sensitive_selection == "はい")
    
    # 悩み（複数選択）
    st.markdown('<p class="section-title">肌悩み <span style="font-size: 0.6em; margin-left: 5px; opacity: 0.6; font-weight: 500;">SKIN CONCERNS</span></p>', unsafe_allow_html=True)
    concerns = st.multiselect(
        "お悩みを選択",
        options=[
            "シミ・そばかす", "たるみ", "シワ", "ハリ・ツヤのなさ", 
            "乾燥", "目の下のくま", "毛穴の黒ずみ・開き", "くすみ",
            "ニキビ・吹き出物", "赤み・赤ら顔", "脂っぽさ・テカリ", 
            "化粧ノリが悪い", "かゆみ"
        ],
        default=["乾燥"],
        label_visibility="collapsed"
    )
    
    # 探しているアイテム
    st.markdown('<p class="section-title">探しているアイテム <span style="font-size: 0.6em; margin-left: 5px; opacity: 0.6; font-weight: 500;">TARGET ITEM</span></p>', unsafe_allow_html=True)
    st.markdown('<p style="font-size: 0.8rem; color: #888; margin-bottom: 0.5rem;">今、特に探しているスキンケアアイテムを選択してください。</p>', unsafe_allow_html=True)
    target_items = st.multiselect(
        "探しているアイテム",
        options=["化粧水", "美容液", "乳液・クリーム", "洗顔", "日焼け止め", "フルライン（一式）"],
        default=["化粧水"],
        label_visibility="collapsed"
    )

    # 自由記述（任意）
    st.markdown("""
        <div style="margin-top: 1rem; margin-bottom: 0.5rem;">
            <span style="font-size: 0.85rem; font-weight: 600; color: var(--color-text);">その他のお悩み（任意）</span>
            <span style="font-size: 0.75rem; color: var(--color-text-light); margin-left: 0.5rem;">※書かなくても大丈夫です</span>
        </div>
    """, unsafe_allow_html=True)
    detailed_concern = st.text_area(
        "その他のお悩み",
        placeholder="例：季節の変わり目に肌荒れしやすい、Tゾーンのテカリが特に気になる...など",
        height=100,
        label_visibility="collapsed"
    )
    
    # 予算
    # st.markdown('<p class="section-title">ご予算 <span style="font-size: 0.6em; margin-left: 5px; opacity: 0.6; font-weight: 500;">BUDGET</span></p>', unsafe_allow_html=True) は削除

    st.markdown("""
        <div style="display: flex; align-items: center; margin-bottom: 10px;">
            <div style="background: linear-gradient(135deg, var(--color-purple) 0%, var(--color-teal) 100%); width: 40px; height: 40px; border-radius: 50%; display: flex; align-items: center; justify-content: center; margin-right: 15px; flex-shrink: 0; color: white; font-weight: bold; font-size: 1.2rem;">
                ￥
            </div>
            <div>
                <span style="font-weight: 700; color: var(--color-text);">ご予算の上限 <span style="font-size: 0.8em; margin-left: 5px; opacity: 0.6; font-weight: 500;">BUDGET</span></span><br>
                <span style="font-size: 0.8rem; color: var(--color-text-light);">これくらいまで出せる金額を入力</span>
            </div>
        </div>
    """, unsafe_allow_html=True)

    budget = st.number_input(
        "金額 (円)",
        min_value=1000,
        max_value=10000,
        value=st.session_state.budget,
        step=500,
        key="budget_input",
        label_visibility="collapsed"
    )
    st.session_state.budget = budget
    # st.markdown('</div>', unsafe_allow_html=True) は削除
    # 診断ボタン
    st.markdown('<div style="margin-top: 2.5rem; margin-bottom: 1rem;">', unsafe_allow_html=True)
    if st.button("診断する", use_container_width=True):
        with st.spinner('AIが肌質データを分析し、最適なスキンケアを検索中...'):
            st.session_state.show_results = True
            st.session_state.concerns = concerns
            st.session_state.detailed_concern = detailed_concern
            st.session_state.is_sensitive = is_sensitive
            st.session_state.target_items = target_items  # 選択項目を保存
            st.session_state.recommendations = get_recommendations(
                products, age, combined_type, concerns, budget, is_sensitive, target_items
            )
            st.rerun()
    
    # 結果表示
    if st.session_state.show_results and st.session_state.recommendations:
        # ターゲットアイテム名を見出しに反映
        targets = st.session_state.get("target_items", [])
        target_str = "、".join(targets) if targets else "あなた"
        
        st.markdown(f"""
        <div class="result-header">
            <h2 style="font-size: 1.6rem;">{target_str}に<span class="accent">おすすめ</span></h2>
        </div>
        """, unsafe_allow_html=True)
        
        if "フルライン（一式）" in targets:
            rank_labels = ["STEP 1：洗顔", "STEP 2：化粧水", "STEP 3：美容液", "STEP 4：乳液", "STEP 5：クリーム"]
            rank_suffix = ""
        elif targets and len(targets) > 1:
            rank_labels = targets
            rank_suffix = " おすすめ"
        else:
            rank_labels = ["1st", "2nd", "3rd"]
            rank_suffix = " RECOMMEND"
        
        for i, (product, score) in enumerate(st.session_state.recommendations):
            tags_html = "".join([
                f'<span class="result-tag">{t}</span>' 
                for t in product["skin_types"][:2] + product["concerns"][:2]
            ])
            
            st.markdown(f"""
            <div class="result-card">
                <span class="result-rank">{rank_labels[i]}{rank_suffix}</span>
                <div style="display: flex; gap: 1.5rem; align-items: flex-start;">
                    <div style="flex-shrink: 0;">
                        <img src="{product["image_url"]}" style="width: 140px; height: auto; border-radius: 12px; object-fit: cover; box-shadow: 0 4px 10px rgba(0, 0, 0, 0.05);" alt="{product["name"]}">
                    </div>
                    <div style="flex: 1;">
                        <div class="result-product-name">{product["name"]}</div>
                        <div class="result-brand">{product["brand"]} | {product["type"]}</div>
                        <div class="result-tags">{tags_html}</div>
                        <div class="result-description">{product["description"]}</div>
                        <div class="result-price">¥{product["price"]:,}</div>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            if st.button(f"🔍 詳細・使用感・成分を見る", key=f"detail_{product['id']}", use_container_width=True):
                st.session_state.selected_product_id = product['id']
                st.rerun()

    # フッター
    st.markdown("""
    <div class="footer">
        <p>※ 本診断は参考情報です。肌トラブルがある場合は専門医にご相談ください。</p>
        <p>※ 当サイトはアフィリエイトプログラムに参加しています。</p>
    </div>
    """, unsafe_allow_html=True)



def render_fab():
    """右下にAI相談室へのフローティングボタン（FAB）を表示する"""
    st.markdown("""
    <style>
    .ai-fab-btn {
        position: fixed;
        bottom: 30px;
        right: 30px;
        background: linear-gradient(135deg, var(--color-purple) 0%, var(--color-teal) 100%);
        width: 65px;
        height: 65px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 30px;
        box-shadow: 0 4px 15px rgba(136, 97, 154, 0.4);
        cursor: pointer;
        z-index: 999999;
        transition: transform 0.3s cubic-bezier(0.175, 0.885, 0.32, 1.275), box-shadow 0.3s;
    }
    .ai-fab-btn:hover {
        transform: translateY(-5px) scale(1.05);
        box-shadow: 0 8px 25px rgba(136, 97, 154, 0.6);
    }
    .ai-fab-tooltip {
        position: fixed;
        bottom: 110px;
        right: 20px;
        background: white;
        padding: 10px 18px;
        border-radius: 20px;
        font-size: 0.95rem;
        font-weight: 700;
        color: var(--color-text);
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        pointer-events: none;
        z-index: 999999;
        animation: float 3s ease-in-out infinite;
    }
    .ai-fab-tooltip::after {
        content: '';
        position: absolute;
        bottom: -10px;
        right: 30px;
        border-width: 10px 10px 0;
        border-style: solid;
        border-color: white transparent transparent transparent;
        display: block;
        width: 0;
    }
    @keyframes float {
        0% { transform: translateY(0px); }
        50% { transform: translateY(-8px); }
        100% { transform: translateY(0px); }
    }
    </style>
    
    <div class="ai-fab-tooltip">AIに相談する✨</div>
    <div class="ai-fab-btn">
        💬
    </div>
    """, unsafe_allow_html=True)

    import streamlit.components.v1 as components
    components.html("""
    <script>
    const targetDoc = window.parent.document;
    if (!targetDoc.getElementById('fab-click-handler')) {
        const script = targetDoc.createElement('script');
        script.id = 'fab-click-handler';
        script.innerHTML = `
            document.addEventListener('click', function(e) {
                if (e.target.closest('.ai-fab-btn')) {
                    const tabs = document.querySelectorAll('button[data-baseweb="tab"]');
                    for (let t of tabs) {
                        if (t.innerText.includes('AI相談室')) {
                            t.click();
                            break;
                        }
                    }
                }
            });
        `;
        targetDoc.head.appendChild(script);
    }
    </script>
    """, height=0, width=0)


def main():
    # 詳細ページモードの場合はタブを表示せず詳細ページのみ（既存ロジック維持）
    if st.session_state.get("show_results", False) and st.session_state.get("selected_product_id") is not None:
         render_diagnosis_flow()
         return

    # タブ作成
    tab1, tab2 = st.tabs(["肌質診断", "AI相談室"])
    
    with tab1:
        render_diagnosis_flow()
        
    with tab2:
        render_ai_chat()

    # タブの描画後にフローティングボタンを描画
    render_fab()

if __name__ == "__main__":
    main()
