import urllib.request
import urllib.parse
import json
import http.cookiejar

url_login = 'http://127.0.0.1:5003/api/login'
url_canchas = 'http://127.0.0.1:5003/api/canchas'

cj = http.cookiejar.CookieJar()
opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj))

# Login
login_data = json.dumps({'email': 'admin@demo.futadmin', 'password': 'admin'}).encode('utf-8')
req_login = urllib.request.Request(url_login, data=login_data, headers={'Content-Type': 'application/json'}, method='POST')

try:
    with opener.open(req_login) as response:
        print("Login status:", response.status)
        
    # Fetch Canchas
    req_canchas = urllib.request.Request(url_canchas, method='GET')
    with opener.open(req_canchas) as response:
        print("Canchas status:", response.status)
        print("Body:", response.read().decode('utf-8'))
except urllib.error.HTTPError as e:
    print(f"HTTPError: {e.code}")
    print(e.read().decode('utf-8'))
except Exception as e:
    print(f"Error: {e}")
