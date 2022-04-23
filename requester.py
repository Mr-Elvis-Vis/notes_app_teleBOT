import requests

from bot_date import DICT_URL


class Requester():
    def get_list(self, chat):
        b_token = self.token(chat)
        response = requests.get(DICT_URL['note_list'], headers={
            "Authorization": f"Bearer {b_token}"
        })
        return response

    def get_note(self, chat, note_id):
        url = DICT_URL['note_create']
        url_note = f'{url}{note_id}'
        b_token = self.token(chat)
        response = requests.get(url_note, headers={
            "Authorization": f"Bearer {b_token}"
        })
        return response

    def delete_note(self, chat, note_id):
        b_token = self.token(chat)
        url = DICT_URL['note_create']
        url_note = f'{url}{note_id}'
        requests.delete(url_note, headers={
            "Authorization": f"Bearer {b_token}"
        })

    def create_note(self, chat, mes_text):
        b_token = self.token(chat)
        response = requests.post(DICT_URL['note_create'], headers={
            "Authorization": f"Bearer {b_token}"
        }, data={
            "text": f"{mes_text}",
        })
        return response

    def patch_note(self, chat, note_id, mes_text):
        url = DICT_URL['note_create']
        url_note = f'{url}{note_id}/'
        b_token = self.token(chat)
        requests.patch(url_note, headers={
            "Authorization": f"Bearer {b_token}"
        }, data={
            "text": f"{mes_text}",
        })

    def token(self, chat):
        with open("token.txt", 'r+') as file:
            d = {}
            lines = file.readlines()
            for line in lines:
                key, value = line.split()
                d[key] = value
            b_token = d[str(chat.id)]
        return b_token
