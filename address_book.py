import sqlite3
from contact import Contact

class AddressBook:
    def __init__(self, db_file="address_book.db"):
        self.db_file = db_file
        self._create_table()

    def _create_table(self):
        conn = sqlite3.connect(self.db_file)
        c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS contacts
                     (id INTEGER PRIMARY KEY, name TEXT, phone TEXT, group_name TEXT)''')
        conn.commit()
        conn.close()

    def add_contact(self, name, phone, group=""):
        conn = sqlite3.connect(self.db_file)
        c = conn.cursor()
        c.execute("INSERT INTO contacts (name, phone, group_name) VALUES (?, ?, ?)", (name, phone, group))
        conn.commit()
        conn.close()

    def get_all_contacts(self):
        conn = sqlite3.connect(self.db_file)
        c = conn.cursor()
        c.execute("SELECT * FROM contacts")
        rows = c.fetchall()
        contacts = [Contact(row[1], row[2], row[3]) for row in rows]
        conn.close()
        return contacts

    def export_to_csv(self, filename):
        contacts = self.get_all_contacts()
        with open(filename, 'w') as file:
            for contact in contacts:
                file.write(f"{contact.name},{contact.phone},{contact.group}\n")

    def import_from_csv(self, filename):
        conn = sqlite3.connect(self.db_file)
        c = conn.cursor()
        c.execute("DELETE FROM contacts")
        conn.commit()

        with open(filename, 'r') as file:
            for line in file:
                parts = line.strip().split(',')
                if len(parts) >= 2:
                    name, phone, group = parts[:3]
                    c.execute("INSERT INTO contacts (name, phone, group_name) VALUES (?, ?, ?)", (name, phone, group))
        conn.commit()
        conn.close()

    def delete_contact(self, name):
        conn = sqlite3.connect(self.db_file)
        c = conn.cursor()
        c.execute("DELETE FROM contacts WHERE name=?", (name,))
        conn.commit()
        conn.close()

    def edit_contact(self, name, new_phone, new_group=""):
        conn = sqlite3.connect(self.db_file)
        c = conn.cursor()
        c.execute("UPDATE contacts SET phone=?, group_name=? WHERE name=?", (new_phone, new_group, name))
        conn.commit()
        conn.close()

    def search_contact(self, term):
        conn = sqlite3.connect(self.db_file)
        c = conn.cursor()
        c.execute("SELECT * FROM contacts WHERE name LIKE ? OR phone LIKE ? OR group_name LIKE ?", ('%'+term+'%', '%'+term+'%', '%'+term+'%'))
        rows = c.fetchall()
        contacts = [Contact(row[1], row[2], row[3]) for row in rows]
        conn.close()
        return contacts

    def _sort_contacts(self):
        contacts = self.get_all_contacts()
        contacts.sort(key=lambda x: x.name.lower())
        return contacts
