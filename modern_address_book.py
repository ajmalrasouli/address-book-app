import sys
import sqlite3
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                           QHBoxLayout, QPushButton, QLineEdit, QListWidget,
                           QLabel, QTabWidget, QFormLayout, QMessageBox, 
                           QStatusBar, QDialog, QFileDialog, QMenu,
                           QListWidgetItem, QComboBox, QInputDialog, QSystemTrayIcon)
from PyQt6.QtCore import Qt, QSize, QTimer
from PyQt6.QtGui import QIcon, QPixmap, QAction, QFont, QColor, QPalette

class Contact:
    def __init__(self, name, phone, email="", group="", notes="", contact_id=None):
        self.id = contact_id
        self.name = name
        self.phone = phone
        self.email = email
        self.group = group
        self.notes = notes

    def __str__(self):
        return f"{self.name} - {self.phone}"

class ContactDialog(QDialog):
    def __init__(self, contact=None, parent=None):
        super().__init__(parent)
        self.contact = contact
        self.setWindowTitle("Edit Contact" if contact else "Add Contact")
        self.setMinimumWidth(400)
        
        layout = QVBoxLayout()
        
        # Form layout for contact details
        form = QFormLayout()
        
        self.name_edit = QLineEdit()
        self.phone_edit = QLineEdit()
        self.email_edit = QLineEdit()
        self.group_combo = QComboBox()
        self.group_combo.setEditable(True)
        self.group_combo.addItems(["Family", "Friends", "Work", "Other"])
        self.notes_edit = QLineEdit()
        
        form.addRow("Name:", self.name_edit)
        form.addRow("Phone:", self.phone_edit)
        form.addRow("Email:", self.email_edit)
        form.addRow("Group:", self.group_combo)
        form.addRow("Notes:", self.notes_edit)
        
        if contact:
            self.name_edit.setText(contact.name)
            self.phone_edit.setText(contact.phone)
            self.email_edit.setText(contact.email)
            if contact.group:
                self.group_combo.setCurrentText(contact.group)
            self.notes_edit.setText(contact.notes)
        
        # Buttons
        btn_box = QHBoxLayout()
        save_btn = QPushButton("Save")
        save_btn.clicked.connect(self.accept)
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        
        btn_box.addWidget(save_btn)
        btn_box.addWidget(cancel_btn)
        
        layout.addLayout(form)
        layout.addLayout(btn_box)
        self.setLayout(layout)
    
    def get_contact_data(self):
        return {
            'name': self.name_edit.text().strip(),
            'phone': self.phone_edit.text().strip(),
            'email': self.email_edit.text().strip(),
            'group': self.group_combo.currentText().strip(),
            'notes': self.notes_edit.text().strip()
        }

class ModernAddressBook(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Modern Address Book")
        self.setMinimumSize(900, 600)
        
        # Initialize database
        self.init_database()
        
        # Set up the UI
        self.setup_ui()
        
        # Load contacts
        self.load_contacts()
        
        # Apply modern styling
        self.apply_styles()
    
    def init_database(self):
        self.conn = sqlite3.connect('address_book.db')
        cursor = self.conn.cursor()
        
        # Drop existing table if it exists
        cursor.execute("DROP TABLE IF EXISTS contacts")
        
        # Create new table with updated schema
        cursor.execute('''
            CREATE TABLE contacts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                phone TEXT,
                email TEXT,
                group_name TEXT,
                notes TEXT
            )
        ''')
        self.conn.commit()
        
        # Insert some sample data if the table is empty
        cursor.execute("SELECT COUNT(*) FROM contacts")
        if cursor.fetchone()[0] == 0:
            sample_contacts = [
                ("John Doe", "123-456-7890", "john@example.com", "Work", "Work colleague"),
                ("Jane Smith", "098-765-4321", "jane@example.com", "Friends", "Met at conference"),
                ("Alice Johnson", "555-123-4567", "alice@example.com", "Family", "Cousin")
            ]
            cursor.executemany(
                "INSERT INTO contacts (name, phone, email, group_name, notes) VALUES (?, ?, ?, ?, ?)",
                sample_contacts
            )
            self.conn.commit()
    
    def setup_ui(self):
        # Central widget and main layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)
        
        # Left panel - Contact list and search
        left_panel = QVBoxLayout()
        
        # Search bar
        search_layout = QHBoxLayout()
        self.search_edit = QLineEdit()
        self.search_edit.setPlaceholderText("Search contacts...")
        self.search_edit.textChanged.connect(self.filter_contacts)
        search_btn = QPushButton("🔍")
        search_btn.setFixedWidth(40)
        search_btn.clicked.connect(self.filter_contacts)
        
        search_layout.addWidget(self.search_edit)
        search_layout.addWidget(search_btn)
        
        # Contact list
        self.contact_list = QListWidget()
        self.contact_list.itemDoubleClicked.connect(self.edit_contact)
        self.contact_list.itemSelectionChanged.connect(self.show_contact_details)
        
        # Right panel - Contact details
        right_panel = QVBoxLayout()
        
        # Contact details
        self.details_widget = QWidget()
        self.details_layout = QFormLayout(self.details_widget)
        
        self.name_label = QLabel()
        self.phone_label = QLabel()
        self.email_label = QLabel()
        self.group_label = QLabel()
        self.notes_label = QLabel()
        
        self.details_layout.addRow("Name:", self.name_label)
        self.details_layout.addRow("Phone:", self.phone_label)
        self.details_layout.addRow("Email:", self.email_label)
        self.details_layout.addRow("Group:", self.group_label)
        self.details_layout.addRow("Notes:", self.notes_label)
        
        # Buttons
        btn_layout = QHBoxLayout()
        self.edit_btn = QPushButton("Edit")
        self.delete_btn = QPushButton("Delete")
        self.edit_btn.clicked.connect(self.edit_contact)
        self.delete_btn.clicked.connect(self.delete_contact)
        
        btn_layout.addWidget(self.edit_btn)
        btn_layout.addWidget(self.delete_btn)
        
        right_panel.addWidget(QLabel("Contact Details"))
        right_panel.addWidget(self.details_widget)
        right_panel.addStretch()
        right_panel.addLayout(btn_layout)
        
        # Add widgets to main layout
        left_panel.addLayout(search_layout)
        left_panel.addWidget(self.contact_list)
        
        main_layout.addLayout(left_panel, 40)
        main_layout.addLayout(right_panel, 60)
        
        # Create menu bar
        self.create_menu_bar()
        
        # Status bar
        self.statusBar().showMessage("Ready")
    
    def create_menu_bar(self):
        menu_bar = self.menuBar()
        
        # File menu
        file_menu = menu_bar.addMenu("&File")
        
        new_action = QAction("&New Contact", self)
        new_action.triggered.connect(self.add_contact)
        file_menu.addAction(new_action)
        
        import_action = QAction("&Import...", self)
        export_action = QAction("&Export...", self)
        file_menu.addSeparator()
        file_menu.addAction(import_action)
        file_menu.addAction(export_action)
        
        exit_action = QAction("E&xit", self)
        exit_action.triggered.connect(self.close)
        file_menu.addSeparator()
        file_menu.addAction(exit_action)
        
        # Edit menu
        edit_menu = menu_bar.addMenu("&Edit")
        
        preferences_action = QAction("&Preferences...", self)
        edit_menu.addAction(preferences_action)
    
    def apply_styles(self):
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f5f5f5;
            }
            QListWidget {
                background-color: white;
                border: 1px solid #ddd;
                border-radius: 4px;
                padding: 5px;
            }
            QListWidget::item {
                padding: 8px;
                border-bottom: 1px solid #eee;
            }
            QListWidget::item:selected {
                background-color: #e3f2fd;
                color: #1976d2;
            }
            QLineEdit, QComboBox {
                padding: 6px;
                border: 1px solid #ddd;
                border-radius: 4px;
                min-height: 28px;
            }
            QPushButton {
                background-color: #1976d2;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                min-width: 80px;
            }
            QPushButton:hover {
                background-color: #1565c0;
            }
            QPushButton:pressed {
                background-color: #0d47a1;
            }
            QLabel {
                padding: 4px 0;
            }
        """)
    
    def load_contacts(self, filter_text=""):
        self.contact_list.clear()
        cursor = self.conn.cursor()
        
        try:
            # Ensure the contacts table exists
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS contacts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    phone TEXT,
                    email TEXT,
                    group_name TEXT,
                    notes TEXT
                )
            """)
            
            if filter_text:
                cursor.execute("""
                    SELECT id, name, phone, email, group_name, notes 
                    FROM contacts 
                    WHERE name LIKE ? OR phone LIKE ? OR email LIKE ? OR group_name LIKE ?
                    ORDER BY name
                """, (f"%{filter_text}%", f"%{filter_text}%", f"%{filter_text}%", f"%{filter_text}%"))
            else:
                cursor.execute("""
                    SELECT id, name, phone, email, group_name, notes 
                    FROM contacts 
                    ORDER BY name
                """)
            
            rows = cursor.fetchall()
            if not rows:
                self.statusBar().showMessage("No contacts found. Add a new contact to get started.", 3000)
                return
                
            for row in rows:
                try:
                    contact = Contact(
                        contact_id=row[0],
                        name=row[1] or "Unnamed Contact",
                        phone=row[2] or "",
                        email=row[3] or "",
                        group=row[4] or "",
                        notes=row[5] or ""
                    )
                    item = QListWidgetItem(str(contact))
                    item.setData(Qt.ItemDataRole.UserRole, contact)
                    self.contact_list.addItem(item)
                except Exception as e:
                    print(f"Error loading contact: {e}")
                    continue
                    
            self.statusBar().showMessage(f"Loaded {len(rows)} contacts", 3000)
            
        except sqlite3.Error as e:
            QMessageBox.critical(self, "Database Error", f"An error occurred while loading contacts: {str(e)}")
            self.statusBar().showMessage("Error loading contacts", 3000)
    
    def filter_contacts(self):
        filter_text = self.search_edit.text()
        self.load_contacts(filter_text)
    
    def add_contact(self):
        dialog = ContactDialog()
        if dialog.exec() == QDialog.DialogCode.Accepted:
            data = dialog.get_contact_data()
            cursor = self.conn.cursor()
            cursor.execute("""
                INSERT INTO contacts (name, phone, email, group_name, notes)
                VALUES (?, ?, ?, ?, ?)
            """, (data['name'], data['phone'], data['email'], data['group'], data['notes']))
            self.conn.commit()
            self.load_contacts()
            self.statusBar().showMessage("Contact added successfully", 3000)
    
    def edit_contact(self):
        current_item = self.contact_list.currentItem()
        if not current_item:
            QMessageBox.warning(self, "No Selection", "Please select a contact to edit.")
            return
            
        contact = current_item.data(Qt.ItemDataRole.UserRole)
        dialog = ContactDialog(contact, self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            data = dialog.get_contact_data()
            cursor = self.conn.cursor()
            cursor.execute("""
                UPDATE contacts 
                SET name=?, phone=?, email=?, group_name=?, notes=?
                WHERE id=?
            """, (data['name'], data['phone'], data['email'], data['group'], data['notes'], contact.id))
            self.conn.commit()
            self.load_contacts()
            self.statusBar().showMessage("Contact updated successfully", 3000)
    
    def show_contact_details(self):
        """Display the details of the currently selected contact."""
        current_item = self.contact_list.currentItem()
        if not current_item:
            # Clear the details if no contact is selected
            self.name_label.clear()
            self.phone_label.clear()
            self.email_label.clear()
            self.group_label.clear()
            self.notes_label.clear()
            return
            
        contact = current_item.data(Qt.ItemDataRole.UserRole)
        if contact:
            self.name_label.setText(contact.name)
            self.phone_label.setText(contact.phone)
            self.email_label.setText(contact.email)
            self.group_label.setText(contact.group)
            self.notes_label.setText(contact.notes)
    
    def delete_contact(self):
        current_item = self.contact_list.currentItem()
        if not current_item:
            return
            
        contact = current_item.data(Qt.ItemDataRole.UserRole)
        reply = QMessageBox.question(
            self, 'Delete Contact',
            f'Are you sure you want to delete {contact.name}?',
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            cursor = self.conn.cursor()
            cursor.execute("DELETE FROM contacts WHERE id=?", (contact.id,))
            self.conn.commit()
            self.load_contacts()
            self.statusBar().showMessage("Contact deleted", 3000)
    
    def closeEvent(self, event):
        self.conn.close()
        event.accept()

def main():
    app = QApplication(sys.argv)
    app.setStyle('Fusion')  # Use Fusion style for a modern look
    
    # Set application info
    app.setApplicationName("Modern Address Book")
    app.setOrganizationName("Your Company")
    app.setOrganizationDomain("yourcompany.com")
    
    window = ModernAddressBook()
    window.show()
    sys.exit(app.exec())

if __name__ == '__main__':
    main()
