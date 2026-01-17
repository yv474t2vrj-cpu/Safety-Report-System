import http.cookiejar, urllib.request, urllib.parse

LOGIN_URL = 'http://127.0.0.1:8000/login'
USERS_URL = 'http://127.0.0.1:8000/master/users'

cj = http.cookiejar.CookieJar()
opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj))

# fetch login page to get cookies
opener.open(LOGIN_URL)

login_data = urllib.parse.urlencode({'username':'master','password':'master123'}).encode()
resp = opener.open(LOGIN_URL, login_data)

# now fetch users page
resp2 = opener.open(USERS_URL)
content = resp2.read().decode(errors='replace')

print('Status:', resp2.getcode())
# print a short snippet
snippet = '\n'.join(content.splitlines()[:80])
print(snippet)
