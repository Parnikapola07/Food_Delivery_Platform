import urllib.request
try:
    response = urllib.request.urlopen("http://127.0.0.1:5000/auth/login/user")
    print("STATUS:", response.getcode())
    html = response.read().decode('utf-8')
    print("BODY LENGTH:", len(html))
except urllib.error.HTTPError as e:
    print("HTTP ERROR:", e.code)
    print(e.read().decode('utf-8')[:500])
except Exception as e:
    print("ERROR:", e)
