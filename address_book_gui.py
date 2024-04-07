import tkinter as tk
from tkinter import messagebox, ttk
from PIL import Image, ImageTk
from tkinter import filedialog
from address_book import AddressBook

class AddressBookGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Address Book")
        self.root.geometry("800x400")
        self.root.configure(bg="#f0f0f0")

        self.address_book = AddressBook()

        self.header_label = tk.Label(
            self.root, text="Address Book", font=("Helvetica", 20), bg="#f0f0f0"
        )
        self.header_label.pack(pady=(20, 10))

        self.frame = tk.Frame(self.root, bg="#f0f0f0")
        self.frame.pack(padx=20, pady=10, side=tk.LEFT, fill=tk.Y)

        self.name_label = tk.Label(self.frame, text="Name:", bg="#f0f0f0")
        self.name_label.grid(row=0, column=0, sticky="w")

        self.name_entry = tk.Entry(self.frame, width=30)
        self.name_entry.grid(row=0, column=1, padx=10, pady=5, sticky="w")

        self.phone_label = tk.Label(self.frame, text="Phone:", bg="#f0f0f0")
        self.phone_label.grid(row=1, column=0, sticky="w")

        self.phone_entry = tk.Entry(self.frame, width=30)
        self.phone_entry.grid(row=1, column=1, padx=10, pady=5, sticky="w")

        self.group_label = tk.Label(self.frame, text="Group:", bg="#f0f0f0")
        self.group_label.grid(row=2, column=0, sticky="w")

        self.group_entry = tk.Entry(self.frame, width=30)
        self.group_entry.grid(row=2, column=1, padx=10, pady=5, sticky="w")

        self.add_icon = Image.open("icons/add.png").resize((24, 24))
        self.add_icon = ImageTk.PhotoImage(self.add_icon)

        self.add_button = tk.Button(
            self.frame, text="Add Contact", image=self.add_icon, compound=tk.LEFT, command=self.add_contact, bg="#4caf50", fg="white", relief=tk.FLAT
        )
        self.add_button.grid(row=3, column=1, pady=10, sticky="e")

        self.view_icon = Image.open("icons/view.png").resize((24, 24))
        self.view_icon = ImageTk.PhotoImage(self.view_icon)

        self.view_button = tk.Button(
            self.frame, text="View Contacts", image=self.view_icon, compound=tk.LEFT, command=self.view_contacts, bg="#2196f3", fg="white", relief=tk.FLAT
        )
        self.view_button.grid(row=4, column=1, pady=10, sticky="e")

        self.export_icon = Image.open("icons/export.png").resize((24, 24))
        self.export_icon = ImageTk.PhotoImage(self.export_icon)

        self.export_button = tk.Button(
            self.frame, text="Export to CSV", image=self.export_icon, compound=tk.LEFT, command=self.export_to_csv, bg="#ff9800", fg="white", relief=tk.FLAT
        )
        self.export_button.grid(row=5, column=1, pady=10, sticky="e")

        self.import_icon = Image.open("icons/import.png").resize((24, 24))
        self.import_icon = ImageTk.PhotoImage(self.import_icon)

        self.import_button = tk.Button(
            self.frame, text="Import from CSV", image=self.import_icon, compound=tk.LEFT, command=self.import_from_csv, bg="#795548", fg="white", relief=tk.FLAT
        )
        self.import_button.grid(row=6, column=1, pady=10, sticky="e")

        self.contacts_tree = ttk.Treeview(self.root, columns=("Name", "Phone", "Group"), selectmode="browse")
        self.contacts_tree.heading("#0", text="ID")
        self.contacts_tree.column("#0", width=50, stretch=tk.NO)
        self.contacts_tree.heading("Name", text="Name")
        self.contacts_tree.heading("Phone", text="Phone")
        self.contacts_tree.heading("Group", text="Group")
        self.contacts_tree.pack(padx=20, pady=20, fill="both", expand=True)

        self.load_contacts()

    def add_contact(self):
        name = self.name_entry.get()
        phone = self.phone_entry.get()
        group = self.group_entry.get()
        if name and phone:
            self.address_book.add_contact(name, phone, group)
            self.load_contacts()
            messagebox.showinfo("Success", f"Contact '{name}' added successfully!")
        else:
            messagebox.showerror("Error", "Please enter both name and phone number.")

    def view_contacts(self):
        self.load_contacts()

    def export_to_csv(self):
        filename = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files", "*.csv")])
        if filename:
            self.address_book.export_to_csv(filename)
            messagebox.showinfo("Exported", f"Address book exported to {filename}")

    def import_from_csv(self):
        filename = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")])
        if filename:
            self.address_book.import_from_csv(filename)
            self.load_contacts()
            messagebox.showinfo("Imported", f"Address book imported from {filename}")

    def load_contacts(self):
        for record in self.contacts_tree.get_children():
            self.contacts_tree.delete(record)

        contacts = self.address_book.get_all_contacts()
        for idx, contact in enumerate(contacts, start=1):
            self.contacts_tree.insert("", "end", text=idx, values=(contact.name, contact.phone, contact.group))

def main():
    root = tk.Tk()
    app = AddressBookGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()
