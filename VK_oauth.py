from urllib.parse import urlencode
APP_ID = 7628269
OAUTH_API_BASE_URL = 'https://oauth.vk.com/authorize'
REDIRECT_URI = 'https://oauth.vk.com/blank.html'
SCOPE = 'photos'
PARAMS = {
    'redirect_uri': REDIRECT_URI,
    'scope': SCOPE,
    'response_type': 'token',
    'client_id': APP_ID

}
# ссылка для получения токена
print('?'.join([OAUTH_API_BASE_URL, urlencode(PARAMS, encoding='utf-8')]))

