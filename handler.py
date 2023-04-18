import csv
import os
from telegram import Contact


class CsvHandler:
    file_name = "contacts.csv"

    def open_file(self):
        self.file = open(self.file_name, 'a+', encoding='utf-8', newline='')
        return self.file

    def append_contact(self, contact: Contact):
        row = [contact.first_name, contact.phone_number] if contact.last_name is None else [contact.first_name + " " + contact.last_name, contact.phone_number]
        file = self.open_file()
        writer = csv.writer(file)
        writer.writerow(row)
        file.close()

