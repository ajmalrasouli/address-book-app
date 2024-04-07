class Contact:
    def __init__(self, name, phone, group=""):
        self.name = name
        self.phone = phone
        self.group = group

    def __str__(self):
        return f"Name: {self.name}, Phone: {self.phone}, Group: {self.group}"

    def to_dict(self):
        return {
            'name': self.name,
            'phone': self.phone,
            'group': self.group
        }
