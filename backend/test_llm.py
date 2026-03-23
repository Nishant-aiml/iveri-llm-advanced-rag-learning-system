"""Test Sarvam-M API directly — full output"""
import httpx, json
from app.config import SARVAM_API_KEY, SARVAM_API_URL

headers = {
    "Authorization": f"Bearer {SARVAM_API_KEY}",
    "Content-Type": "application/json",
}
payload = {
    "model": "sarvam-m",
    "messages": [{"role": "user", "content": "Say hello in one sentence"}],
    "max_tokens": 50,
}
r = httpx.post(SARVAM_API_URL, json=payload, headers=headers, timeout=30)
print(f"STATUS: {r.status_code}")
data = r.json()
print(f"KEYS: {list(data.keys())}")
if "choices" in data:
    print(f"ANSWER: {data['choices'][0]['message']['content']}")
else:
    print(f"FULL: {json.dumps(data, indent=2)[:500]}")
