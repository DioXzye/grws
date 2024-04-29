import requests
import time
from tinydb import TinyDB, Query

TOKEN = '6904353532:AAF2jFf5q4C9AIiQemcbwVLpH51xMP5sfzw'
YOUR_ACCOUNT_ID = '1809154424'
GET_FILE_URL = f'https://api.telegram.org/bot{TOKEN}/getFile'
GET_UPDATES_URL = f'https://api.telegram.org/bot{TOKEN}/getUpdates'
SEND_MESSAGE_URL = f'https://api.telegram.org/bot{TOKEN}/sendMessage'
SEND_PHOTO_URL = f'https://api.telegram.org/bot{TOKEN}/sendPhoto'
SEND_VIDEO_URL = f'https://api.telegram.org/bot{TOKEN}/sendVideo'
SEND_AUDIO_URL = f'https://api.telegram.org/bot{TOKEN}/sendAudio'
SEND_DOCUMENT_URL = f'https://api.telegram.org/bot{TOKEN}/sendDocument'

db = TinyDB('db.json')
User = Query()

def get_updates(offset=None):
    params = {'timeout': 100, 'offset': offset}
    response = requests.get(GET_UPDATES_URL, params=params)
    return response.json()

def get_file_url(file_path):
    response = requests.get(GET_FILE_URL, params={'file_id': file_path})
    file_info = response.json()
    if file_info['ok']:
        file_path = file_info['result']['file_path']
        return f'https://api.telegram.org/file/bot{TOKEN}/{file_path}'
    else:
        return None

def send_message(chat_id, text):
    data = {'chat_id': chat_id, 'text': text}
    requests.post(SEND_MESSAGE_URL, json=data)

def send_photo(chat_id, photo_url, caption=None):
    data = {'chat_id': chat_id, 'photo': photo_url}
    if caption:
        data['caption'] = caption
    requests.post(SEND_PHOTO_URL, data=data)

def send_video(chat_id, video_url, caption=None):
    data = {'chat_id': chat_id, 'video': video_url}
    if caption:
        data['caption'] = caption
    requests.post(SEND_VIDEO_URL, data=data)

def send_audio(chat_id, audio_url, caption=None):
    data = {'chat_id': chat_id, 'audio': audio_url}
    if caption:
        data['caption'] = caption
    requests.post(SEND_AUDIO_URL, data=data)

def send_document(chat_id, document_url, caption=None):
    data = {'chat_id': chat_id, 'document': document_url}
    if caption:
        data['caption'] = caption
    requests.post(SEND_DOCUMENT_URL, data=data)

def handle_messages(updates):
    for update in updates['result']:
        if 'message' in update:
            message = update['message']
            chat_id = message['chat']['id']
            text = message.get('text', '')
            username = message['from'].get('username', '')
            
            user = db.get(User.chat_id == chat_id)
            
            if not user:
                db.insert({'chat_id': chat_id, 'username': username})
            
            if text == '/start':
                continue
            
            send_message(YOUR_ACCOUNT_ID, f"Отчет от {username} ({chat_id}):\n{text}")
            
            send_message(chat_id, 'Ваш отчет получен и передан.')
            
            if 'document' in message:
                document = message['document']
                file_url = get_file_url(document['file_id'])
                if file_url:
                    send_document(chat_id, file_url, caption=f"Документ от {username} ({chat_id})")
            elif 'photo' in message:
                photo = message['photo'][-1]
                file_url = get_file_url(photo['file_id'])
                if file_url:
                    send_photo(chat_id, file_url, caption=f"Фото от {username} ({chat_id})")
            elif 'audio' in message:
                audio = message['audio']
                file_url = get_file_url(audio['file_id'])
                if file_url:
                    send_audio(chat_id, file_url, caption=f"Аудио от {username} ({chat_id})")
            elif 'video' in message:
                video = message['video']
                file_url = get_file_url(video['file_id'])
                if file_url:
                    send_video(chat_id, file_url, caption=f"Видео от {username} ({chat_id})")
            
            offset = update['update_id'] + 1
            return offset
    return None

def main():
    offset = None
    while True:
        updates = get_updates(offset)
        if 'result' in updates:
            offset = handle_messages(updates)
        time.sleep(1)

if __name__ == '__main__':
    main()