
from urllib.parse import urljoin
import requests
from datetime import datetime


class VkPhotos:
    VERSION = '5.124'
    API_BASE_URL = 'https://api.vk.com/method/'
    BASE_URL = API_BASE_URL

    def __init__(self, user_id, token, version=VERSION):
        self.token = token
        self.version = version
        self.user_id = user_id

    def get_Albums_list(self):
        albums_url = urljoin(VkPhotos.API_BASE_URL, 'photos.getAlbums')
        result = requests.get(albums_url, params={
            'owner_id': self.user_id,
            'access_token': self.token,
            'need_system': 1,
            'photo_sizes': 1,
            'v': self.version
        })
        dic = {d['title']: d['id'] for d in result.json()['response']['items']}
        return dic

    def get_photos(self, photo_number, album_id='profile'):
        photos_url = urljoin(VkPhotos.API_BASE_URL, 'photos.get')
        photos_taged = urljoin(VkPhotos.API_BASE_URL, 'photos.getUserPhotos')
        if album_id == '-9000':
            result = requests.get(photos_taged, params={
                'user_id': self.user_id,
                'access_token': self.token,
                'count': photo_number,
                'extended': 1,
                'photo_sizes': 1,
                'v': self.version
            })
            return result.json()['response']
        result = requests.get(photos_url, params={
            'owner_id': self.user_id,
            'album_id': album_id,
            'access_token': self.token,
            'rev': 0,
            'extended': 1,
            'photo_sizes': 1,
            'v': self.version
        })
        return result.json()['response']

    def info_file_generator(self, photo_number, album_id):
        json_object = self.get_photos(photo_number, album_id)
        dict_list = []
        photo_names = {}
        iterator = 0
        i = 0
        for photo in json_object['items']:

            # перевод формата даты в строковый
            timestamp = photo['date']
            dt_object = datetime.fromtimestamp(timestamp)
            date = dt_object.strftime("%d.%m.%Y")

            # получение названия фотографии
            file_name = str(photo['likes']['count'])+'.jpg'
            if file_name not in photo_names:
                photo_names[file_name] = 0
            elif photo_names[file_name] == 0:
                photo_names[file_name] = i + 1
                file_name = str(photo['likes']['count']) + '_' + str(date) + '.jpg'
            else:
                photo_names[file_name] += 1
                file_name = f"{photo['likes']['count']}_{date}({photo_names[file_name]})"

            # поиск максимальной фотографии:
            types = 'a'
            url = ''
            for size in photo['sizes']:
                if size['type'] == 'w':
                    types = size['type']
                    url = size['url']
                    break
                elif size['type'] > types and size['type'] != 's':
                    types = size['type']
                    url = size['url']
                else:
                    types = 's'
                    url = size['url']

            new_dict = {'file_name': file_name, 'file_size': types, 'url': url}
            dict_list.append(new_dict)
            iterator += 1
            if iterator >= photo_number:
                break

        return dict_list
