import pygsheets
from telegram import Contact


class GoogleTable:
    def __init__(self, table_name: str, is_created=True):
        self.client = pygsheets.authorize(service_file='./google_secret.json')
        self.workbook = self.client.open(table_name) if is_created else self.client.create(table_name)
        self.sheet = self.workbook.sheet1
        if not is_created:
            self.sheet.update_value('A1', 'Имя')
            self.sheet.update_value('B1', 'Номер телефона')
        self.cells = self.sheet.get_all_values(include_tailing_empty_rows=False, include_tailing_empty=False, returnas='matrix')
        self.last_row = len(self.cells)

    def share(self, email: str, role='reader'):
        self.workbook.share(email, role=role)

    def get_cell(self, address: str):
        cell = self.sheet.cell(address)
        return cell.value

    def get_url(self):
        return self.workbook.url

    def append_contact(self, contact: Contact):
        values = [contact.first_name, contact.phone_number] if contact.last_name is None else [contact.first_name + " " + contact.last_name, contact.phone_number]
        self.sheet.insert_rows(self.last_row, number=1, values=values)
        self.last_row += 1


if __name__ == "__main__":
    contact_me = Contact('+79149810396', 'Балбар')
    contact_another = Contact('+78005553535', 'Oleg', "Miami")
    gt = GoogleTable('test_18_04')
    gt.append_contact(contact_me)
    gt.append_contact(contact_another)
