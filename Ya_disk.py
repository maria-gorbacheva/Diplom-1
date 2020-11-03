from urllib.parse import urljoin
from time import sleep
import requests
import tqdm
from pprint import pprint
import json
import datetime
import os


class YaUploader:

    SM = {'1': ['OK', 'OK_photo_info.json'],
          '2': ['VK', 'VK_photo_info.json']}

    def __init__(self, token: str):
        self.token = token

    def make_dir(self, sm):
        """Метод создает папку на яндекс диск"""
        now = datetime.datetime.now()
        folder_name = YaUploader.SM[sm][0] + '_' + now.strftime('%d\%m\%Y__%H-%M')

        response_url = requests.put(
            "https://cloud-api.yandex.net/v1/disk/resources",
            params={'path': folder_name, 'overwrite': True},
            headers={"Authorization": f"OAuth {self.token}"},
        )
        return folder_name

    def upload_photo(self, social):
        operation_ids = {}
        with open(YaUploader.SM[social][1]) as d:
            s = d.read()
            w = json.loads(s)

        for item in tqdm.tqdm(w):
            name = item['file_name']
            response_url = requests.post(
                "https://cloud-api.yandex.net/v1/disk/resources/upload",
                params={'url': item['url'],
                        'path': f'/{folder_name}/{name}',
                        'fields': 'operation_id'
                        },
                headers={"Authorization": f"OAuth {self.token}"},
            )
            status_link = response_url.json()['href']
            operation_ids[item['file_name']] = status_link.split('/')[-1]
            counter = 0
        while counter < len(w):
            for file_name, id in operation_ids.items():
                if id == 0:
                    continue
                response_status = requests.get(
                    f"https://cloud-api.yandex.net/v1/disk/operations/{id}",
                    headers={"Authorization": f"OAuth {self.token}"}
                  )
                if response_status.json()['status'] != 'in-progress':
                    counter += 1
                    print(f"{counter}) {file_name} - {response_status.json()['status']}")
                    operation_ids[file_name] = 0
            sleep(1)

    def upload_info(self, social):
        name = os.path.join(os.getcwd(), YaUploader.SM[social][1])
        url_ = f'/{folder_name}/{YaUploader.SM[social][1]}'
        response_url = requests.get(
            "https://cloud-api.yandex.net/v1/disk/resources/upload",
            params={'path': url_, 'overwrite': True},
            headers={"Authorization": f"OAuth {self.token}"},
        )
        url = response_url.json()['href']

        with open(name, 'rb') as f:
            my_file = f.read()
            response = requests.put(url, data=my_file, headers={'content-type': 'json'}, params={'file': name})
        return 'Файл успешно загружен'

    def file_info(self, file_name: str, file_data: json):
        with open(file_name, 'w') as y:
            json.dump(file_data, y, ensure_ascii=False, indent=2)


if __name__ == '__main__':
    token = input('Введите токен Яндекс Диска: ')
    social = input('Выберите соц.сеть [1 - для Одноклассники, 2 - для Вконтакте]: ')
    uploader = YaUploader(token)
    print()
    folder_name = uploader.make_dir(social)

    if social == '1':
        import OK as Ok
        user_id = input('Введите id пользователя: ')
        count_number = int(input('Введите количество фото (max = 100): '))
        user = Ok.OK_API(user_id)
        photos_and_info = user.all_photos(count_number)
    else:
        from VK import VkPhotos
        import VK_oauth
        vk_token = input('Перейдите по ссылке и введите token: ')
        vk_user_id = input('Введите id пользователя Vk: ')

        vk_user = VkPhotos(vk_user_id, vk_token)
        pprint(vk_user.get_Albums_list())

        def album_load():
            album_id = input('Введите id одного из альбомов: ')
            photo_num = int(input('Введите количество фотографий: '))

            return vk_user.info_file_generator(photo_num, album_id)

        photos_and_info = album_load()

    uploader.file_info(YaUploader.SM[social][1], photos_and_info)
    uploader.upload_photo(social)
    uploader.upload_info(social)




