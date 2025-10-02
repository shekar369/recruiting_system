import requests
import json

response = requests.get('http://localhost:8000/api/v1/openapi.json')
print('Status code:', response.status_code)
if response.status_code == 200:
    paths = json.loads(response.text)['paths']
    auth_paths = [p for p in paths if 'auth' in p]
    print('Auth paths found:', len(auth_paths))
    for p in sorted(auth_paths):
        print(p)
else:
    print('Error:', response.text)
