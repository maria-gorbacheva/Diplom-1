from urllib.parse import urlencode
from datetime import datetime
import requests
from hashlib import md5
import json

APP_ID = 512000462880
API_URL = 'https://api.ok.ru/fb.do'
DEFAULT_TIMEOUT = 30
OAUTH_API_BASE_URL = 'https://connect.ok.ru/oauth/authorize'
REDIRECT_URI = 'https://oauth.mycdn.me/blank.html'
APP_PUBLIC = 'CBCBBMJGDIHBABABA'
SCOPE = 'PHOTO_CONTENT, VALUABLE_ACCESS'
PARAMS = {
    'redirect_uri': REDIRECT_URI,
    'scope': SCOPE,
    'response_type': 'token',
    'client_id': APP_ID

}
# ссылка для получения токена
print('?'.join([OAUTH_API_BASE_URL, urlencode(PARAMS, encoding='utf-8')]))

TOKEN = input('Перейдите по ссылке выше и введите token: ')
secret_key = input('Введите секретный ключ сессии: ')
rights = 'VALUABLE_ACCESS; PHOTO_CONTENT'
API_BASE_URL = ' https://api.ok.ru/fb.do?method=photos.getPhotos'


class OK_API:

    def __init__(self, user_id, session_secret=secret_key, token=TOKEN):
        self.token = token
        self.user_id = user_id
        self.session_secret = session_secret

    def _signature(self, params):
        keys = sorted(params.keys())
        param_str = ''.join(['{k}={v}'.format(k=key, v=params[key]) for key in keys])
        param_str += self.session_secret
        return md5(param_str.encode('utf-8')).hexdigest().lower()

    def albums_id_request(self, timeout=DEFAULT_TIMEOUT, **kwargs):

        params = {
            'application_key': APP_PUBLIC,
            'method': 'photos.getAlbums',
            'fid': self.user_id
        }
        a = self._request(params)
        albums_id = [int(x['aid']) for x in a[1]['albums']]
        albums_id.append('')
        return albums_id

    def album_photos(self, album_id):
        params = {
            'application_key': APP_PUBLIC,
            'aid': album_id,
            'fields': 'photo.PIC_MAX, photo.CREATED_MS, photo.LIKE_COUNT',
            'method': 'photos.getPhotos',
            'detectTotalCount': True,
            'count': 100,
            'fid': self.user_id
        }
        d = self._request(params)[1]
        return d

    def _request(self, params, timeout=DEFAULT_TIMEOUT, **kwargs):
        params.update(kwargs)
        sig = self._signature(params)
        params['sig'] = sig
        if self.token:
            params['access_token'] = self.token

        headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/x-www-form-urlencoded'
        }

        req = requests.post(API_URL, data=params, headers=headers, timeout=timeout)
        return req.status_code, req.json()

    def all_photos(self, count_number=5):
        all_photos = []
        photo_dic = {}
        a = self.albums_id_request()
        for item in a:
            if len(all_photos) >= count_number:
                break
            i = 0
            for photo in self.album_photos(item)['photos']:
                if len(all_photos) >= count_number:
                    break
                timestamp = int(photo['created_ms'] / 1000)
                dt_object = datetime.fromtimestamp(timestamp)
                date = dt_object.strftime("%d.%m.%Y")
                name = str(photo['like_count']) + '.jpg'

                if name not in photo_dic.keys():
                    photo_dic[name] = 0

                elif photo_dic[name] == 0:
                    photo_dic[name] = i+1
                    name = str(photo['like_count']) + '_' + str(date)

                else:
                    photo_dic[name] += 1
                    name = f"{photo['like_count']}_{date}({photo_dic[name]})"
                all_photos.append({'file_name': name, 'url': photo['pic_max']})

        return all_photos


