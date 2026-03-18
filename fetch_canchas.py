import urllib.request
import urllib.error

url = 'http://127.0.0.1:5003/api/canchas'
headers = {
    'Cookie': 'session=eyJsaWdhX2lkIjoxLCJ1c2VyX2lkIjo0LCJ1c2VyX25hbWUiOiJBZG1pbmlzdHJhZG9yIFNpc3RlbWEiLCJ1c2VyX3JvbCI6ImFkbWluIn0.Z9I7hQ.7t3y8X9q7Q9Y7O8y6O9O7O9O7O9' # A dummy session cookie that might pass basic auth if configured loosely, or we'll just see the 500 error if it's unrelated to auth
}

req = urllib.request.Request(url, headers=headers)

try:
    with urllib.request.urlopen(req) as response:
        print(f"Status: {response.status}")
        print(response.read().decode('utf-8'))
except urllib.error.HTTPError as e:
    print(f"Error Code: {e.code}")
    print("Response Body:")
    print(e.read().decode('utf-8'))
except Exception as e:
    print(f"General Error: {e}")
