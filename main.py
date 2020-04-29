import io
import json
import os
import zipfile
from typing import Dict, Optional

import requests


def main():
    songs: Dict[str, Optional[str]] = {}

    # parse songs from playlist files
    playlists_path = r'C:\home\games\steam\steamapps\common\Beat Saber\Playlists'
    for file in os.listdir(playlists_path):
        if file.endswith('.bplist'):
            print(f'parsing songs from {file}')
            with open(os.path.join(playlists_path, file), encoding='utf-8') as fout:
                playlist = json.load(fout)
            for song in playlist['songs']:
                songs[song['key']] = song['songName']
    print(f'found {len(songs)} songs in playlists')

    # determine what has already been download
    custom_songs_path = r'C:\home\games\steam\steamapps\common\Beat Saber\Beat Saber_Data\CustomLevels'
    for sub_dir in os.listdir(custom_songs_path):
        song_key = sub_dir.split(' ', maxsplit=1)[0]
        if song_key in songs:
            songs[song_key] = None

    # download
    songs_to_download = {song_key: song_name for song_key, song_name in songs.items() if song_name}
    base_download_url = 'https://beatsaver.com/api/download/key/'
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:73.0) Gecko/20100101 Firefox/73.0'}
    blacklist_chars = r'<>:"/\|?*'
    download_success_count = 0
    download_fail_count = 0
    download_skip_count = len(songs) - len(songs_to_download)
    for n, (song_key, song_name) in enumerate(songs_to_download.items()):
        if not song_name:
            download_skip_count += 1
            continue
        download_url = f'{base_download_url}{song_key}'
        print(f'{n}/{len(songs_to_download)}: downloading [{download_url}] - {song_name}')
        res = requests.get(download_url, allow_redirects=True, headers=headers)
        if not res.ok:
            print(res.status_code, res.content.decode())
            download_fail_count += 1
            continue
        with io.BytesIO(res.content) as zip_data, zipfile.ZipFile(zip_data) as zip_file:
            song_name = ''.join(c for c in song_name if c not in blacklist_chars)
            song_folder = os.path.join(custom_songs_path, f'{song_key} {song_name}')
            os.makedirs(song_folder)
            zip_file.extractall(song_folder)
        download_success_count += 1

    # print metrics
    print('=========================')
    print(f'success: {download_success_count}')
    print(f'fail: {download_fail_count}')
    print(f'skip: {download_skip_count}')


if __name__ == '__main__':
    main()
