import json
import os
import dotenv
from telegram import Contact
class LDB:
    replies: dict

    def __init__(self):
        if not os.path.exists("./data.json"):
            start_json = self.init_json()
            self.save_json(start_json)
        self.update_replies()
        print(self.replies)


    def init_json(self):
        dotenv.load_dotenv()
        creator_id = int(os.getenv("ADMIN_ID"))
        init_json = {
            "admin_id": [creator_id],
            "replies": {
                "greenting_message_text": "Добрый день! Отправим чек-лист ... в этот чат. Нажмите на кнопку \"подтвердить\" для получения материалов.",
                "after_text": "Спасибо... Узнайте больше о возможностях размещения рекламы на Novikov TV:\nhttps://novikovtv.tv"
            },
            "contact": ["NovikovTV", "+79099092022"]
        }
        dump = json.dumps(init_json, indent=4, ensure_ascii=False)
        return dump

    def update_replies(self):
        with open('data.json', 'r', encoding='utf-8') as read_file:
            self.replies = json.load(read_file)

    def save_json(self, dump: str):
        with open("data.json", 'w', encoding='utf-8') as write_file:
            write_file.write(dump)

    def get_reply(self, name: str):
        return self.replies['replies'][name]

    def get_contact(self):
        contact = self.replies['contact']
        return Contact(phone_number=contact[1], first_name=contact[0])

    def is_admin(self, id: int):
        return id in self.replies["admin_id"]

    def update_json(self):
        with open('data.json', 'w', encoding='utf-8') as write_file:
            dump = json.dumps(self.replies, indent=4, ensure_ascii=False)
            write_file.write(dump)

    def set_contact(self, name: str, phone_number: str):
        self.replies["contact"] = [name, phone_number]
        self.update_json()
        self.update_replies()

    def set_reply(self, name: str, text: str):
        self.replies['replies'][name] = text
        self.update_json()
        self.update_replies()

    def add_admin(self, id: int):
        admin_list = self.replies['admin_id']
        admin_list.append(id)
        self.replies['admin_id'] = admin_list
        self.update_json()
        self.update_replies()

def main():
    ldb = LDB()
    print(ldb.get_contact())


if __name__ == '__main__':
    main()