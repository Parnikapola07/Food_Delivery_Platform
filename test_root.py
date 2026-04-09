import urllib.request
try:
    response = urllib.request.urlopen("http://127.0.0.1:5000/")
    print("STATUS:", response.getcode())
    html = response.read().decode('utf-8')
    print("BODY LENGTH:", len(html))
    print("SAMPLE:", html[:200])
except Exception as e:
    print("ERROR:", e)
