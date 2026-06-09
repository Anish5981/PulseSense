import urllib.request
import json

url = "http://localhost:3000/api/frontend/settings"
req = urllib.request.Request(url, headers=headers, method='GET')
try:
    with urllib.request.urlopen(req) as response:
        data = json.loads(response.read().decode('utf-8'))
        ds = data.get('datasources', {})
        for k, v in ds.items():
            if v.get('uid') == 'TimescaleDB':
                print(json.dumps(v, indent=2))
except Exception as e:
    print(f"Error: {e}")
