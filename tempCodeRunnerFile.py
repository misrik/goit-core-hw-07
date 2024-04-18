from collections import UserDict
from datetime import datetime, timedelta

class Field:
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return str(self.value)

class Name(Field):
    pass

class Phone(Field):
    def __init__(self, value):
        if not value.isdigit() or len(value) != 10:
            raise ValueError("Invalid phone number format")
        super().__init__(value)

class Birthday(Field):
    def __init__(self, value):
        try:
            self.value = datetime.strptime(value, "%d.%m.%Y").date()
        except ValueError:
            raise ValueError("Invalid date format. Use DD.MM.YYYY")

class Record:
    def __init__(self, name):
        self.name = Name(name)
        self.phones = []
        self.birthday = None

    def add_phone(self, phone):
        if not phone.isdigit() or len(phone) != 10:
            raise ValueError("Invalid phone number format")
        self.phones.append(Phone(phone))

    def add_birthday(self, birthday):
        self.birthday = Birthday(birthday)

    def __str__(self):
        return f"Contact name: {self.name.value}, phones: {', '.join(str(p) for p in self.phones)}"

class AddressBook(UserDict):
    def add_record(self, record):
        self.data[record.name.value] = record

    def find(self, name):
        return self.data.get(name)

    def delete(self, name):
        if name in self.data:
            del self.data[name]

def input_error(func):
    def inner(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except ValueError:
            return "Give me name and correct format of phone (10 digits) please."
        except KeyError:
            return "No contact found."
        except IndexError:
            return "Enter username."

    return inner

@input_error
def add_contact(args, book):
    name, phone, *_ = args
    record = book.find(name)
    message = "Contact updated."
    if record is None:
        record = Record(name)
        book.add_record(record)
        message = "Contact added."
    if phone:
        record.add_phone(phone)
    return message

@input_error
def change_contact(args, book):
    name, phone = args
    record = book.find(name)
    if record:
        record.phones = [Phone(phone)]
        return "Contact updated successfully"
    else:
        return "Contact not found."

@input_error
def phone_contact(args, book):
    username = args[0]
    record = book.find(username)
    if record:
        return f"Calling a phone number for {username}: {record.phones[0]}"
    else:
        return f"No contact found with username {username}"

@input_error
def show_contact(args, book):
    if len(args) < 1:
        raise IndexError
    name, *_ = args
    record = book.find(name)
    if record:
        return str(record)
    else:
        return f"No contact found with username {name}"

@input_error
def add_birthday(args, book):
    if len(args) < 2:
        raise Exception("Add a user name and birthday please.")
    name, birthday = args
    record = book.find(name)
    if record:
        try:
            record.add_birthday(birthday)
            return f"Birthday added for {name}."
        except ValueError:
            return "Invalid date format. Use DD.MM.YYYY"
    else:
        return "Contact not found."


@input_error
def show_birthday(args, book):
    if len(args) < 1:
        raise IndexError
    name, *_ = args
    record = book.find(name)
    if record and record.birthday:
        return f"{name}'s birthday: {record.birthday.value.strftime('%d.%m.%Y')}"
    elif record:
        return f"{name} has no birthday set."
    else:
        return "Contact not found."

@input_error
def birthdays(args, book):
    upcoming_birthdays = []
    today = datetime.today().date()
    next_week = today + timedelta(days=7)
    for record in book.data.values():
        if record.birthday and today.month == record.birthday.value.month and today.day <= record.birthday.value.day <= next_week.day:
            upcoming_birthdays.append((record.name.value, record.birthday.value))
    if upcoming_birthdays:
        upcoming_birthdays.sort(key=lambda x: x[1])
        print("Upcoming birthdays:")
        return "\n".join([f"{name}'s birthday: {birthday.strftime('%d.%m.%Y')}" for name, birthday in upcoming_birthdays])
    else:
        return "No upcoming birthdays within the next week."

@input_error
def parse_input(user_input):
    cmd, *args = user_input.split()
    cmd = cmd.strip().lower()
    return cmd, *args

def main():
    book = AddressBook()
    print("Welcome to the assistant bot! Here are the commands:")
    print("  - add [name] [phone]: Add or update a contact.")
    print("  - change [name] [new phone]: Change phone number.")
    print("  - show <name>: Show details of a contact")
    print("  - phone <name>: Calling a contact")
    print("  - all: Show all contacts")
    print("  - close/exit: Exit the assistant")
    print("  - add-birthday [name] [birthday]: Add birthday.")
    print("  - show-birthday [name]: Show birthday.")
    print("  - birthdays: Show upcoming birthdays.")
    print("  - close or exit: Close the program.")
    
    while True:
        user_input = input("Enter a command: ")
        command, *args = parse_input(user_input)

        if command in ["close", "exit"]:
            print("Good bye!")
            break

        elif command == "hello":
            print("How can I help you?")

        elif command == "add":
            print(add_contact(args, book))

        elif command == "change":
            print(change_contact(args, book))

        elif command == "show":
            print(show_contact(args, book))

        elif command == "phone":
            print(phone_contact(args, book))

        elif command == "all":
            for record in book.values():
                print(record)

        elif command == "add-birthday":
            print(add_birthday(args, book))

        elif command == "show-birthday":
            print(show_birthday(args, book))

        elif command == "birthdays":
            print(birthdays(args, book))

        else:
            print("Invalid command.")

if __name__ == "__main__":
    main()
