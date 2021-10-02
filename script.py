from pathlib import Path

import vk_api
import time
import re
import httplib2
import os
import sys

DELAY = 0.2
LOGIN = '+905372653209'
PASSWORD = 'can1202'
BASE_DIR = Path(__file__).resolve().parent

def get_api():
    vk_session = vk_api.VkApi(LOGIN, PASSWORD)
    vk_session.auth()
    vk = vk_session.get_api()
    return vk


def get_users_links(file_path: str):
    with open(file_path, 'r', encoding='utf8') as user_link_file:
        user_link_data = user_link_file.readlines()
    return user_link_data


def save_photo(username: str, image_url: str, path_dir_images:str):
    image_name_search = re.search('.+/(.+\.jpg)\?', image_url)
    if image_name_search:
        image_name = image_name_search.group(1)
    else:
        return
    h = httplib2.Http('.cache')
    response, content = h.request(image_url)
    if not os.path.exists(path_dir_images):
        os.mkdir(path_dir_images)
    path = os.path.join(path_dir_images, username, image_name)
    dir_images = os.path.join(path_dir_images, username)
    if not os.path.exists(dir_images):
        os.mkdir(dir_images)
    with open(path, 'wb') as out:
        out.write(content)


def main(file_links: str, path_dir_images: str):
    vk = get_api()
    users_links = get_users_links(file_links)
    for user_link in users_links:
        user_link = user_link.strip()
        print(f'{user_link} downloading images ...')
        username = user_link.split('/')[-1]
        users = vk.users.get(user_ids=[username])
        if users:
            user_id = users[-1]['id']
            try:
                photos = vk.photos.get_all(owner_id=user_id)
            except vk_api.ApiError:
                continue
            if photos['items']:
                for item in photos['items']:
                    image_url = item['sizes'][-1]['url']
                    save_photo(username, image_url, path_dir_images)
                    time.sleep(DELAY)
        time.sleep(DELAY)


if __name__ == '__main__':
    if len(sys.argv) == 3:
        path_list_urls = os.path.join(BASE_DIR, sys.argv[1])
        path_dir_images = os.path.join(BASE_DIR, sys.argv[2])
        main(path_list_urls, path_dir_images)
