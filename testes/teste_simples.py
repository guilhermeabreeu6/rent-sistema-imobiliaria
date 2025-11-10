import requests

try:
    response = requests.get('http://127.0.0.1:5001/health')
    print(f"Status: {response.status_code}")
    print(f"Response: {response.text}")
except Exception as e:
    print(f"Erro: {e}")