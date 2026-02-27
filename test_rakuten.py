import requests
import json
import toml

s = toml.load('.streamlit/secrets.toml')
app_id = s.get('RAKUTEN_APP_ID')

print(f"Testing App ID: {app_id}")

try:
    res = requests.get(
        'https://app.rakuten.co.jp/services/api/IchibaItem/Search/20220601',
        params={'applicationId': app_id, 'keyword': 'test', 'format': 'json'}
    )
    print("STATUS CODE:", res.status_code)
    parsed = res.json()
    print("RESPONSE JSON:")
    print(json.dumps(parsed, ensure_ascii=False, indent=2))
except Exception as e:
    print("ERROR:", e)
