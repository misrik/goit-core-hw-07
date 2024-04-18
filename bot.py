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

    def remove_phone(self, phone):
        for p in self.phones:
            if p.value == phone:
                self.phones.remove(p)
                break

    def edit_phone(self, old_phone, new_phone):
        found = False
        for p in self.phones:
            if p.value == old_phone:
                found = True
                if not new_phone.isdigit() or len(new_phone) != 10:
                    raise ValueError("Invalid new phone number format")
                p.value = new_phone
                break

        if not found:
            raise ValueError("Old phone number not found")

    def find_phone(self, phone):
        for p in self.phones:
            if p.value == phone:
                return p
        return None

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

    def get_upcoming_birthdays(self, days=7):
        def prepare_users(records):
            prepared_records = []
            for record in records:
                if record.birthday:
                    prepared_records.append(record)
            return prepared_records

        def find_next_weekday(d, weekday: int):
            days_ahead = weekday - d.weekday()
            if days_ahead <= 0:
                days_ahead += 7
            return d + timedelta(days=days_ahead)

        def find_upcoming_birthdays(prepared_records):
            today = datetime.today().date()
            upcoming_birthdays = []
            for record in prepared_records:
                birthday_this_year = record.birthday.value.replace(year=today.year)

                if birthday_this_year < today:
                    birthday_this_year = birthday_this_year.replace(year=today.year + 1)

                if 0 <= (birthday_this_year - today).days <= days:
                    if birthday_this_year.weekday() >= 5:
                        birthday_this_year = find_next_weekday(birthday_this_year, 0)

                    congratulation_date_str = birthday_this_year.strftime('%d.%m.%Y')
                    upcoming_birthdays.append({
                        "name": record.name.value,
                        "congratulation_date": congratulation_date_str
                    })
            return upcoming_birthdays

        prepared_records = prepare_users(self.data.values())
        upcoming_birthdays = find_upcoming_birthdays(prepared_records)
        return upcoming_birthdays

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
        except Exception as e:
            return str(e)

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
    if len(args) < 3:
        raise Exception("Enter name, old phone number, and new phone number.")
    
    name, old_phone, new_phone = args
    record = book.find(name)
    
    if record:
        old_phone_obj = record.find_phone(old_phone)
        if old_phone_obj:
            try:
                record.edit_phone(old_phone, new_phone)
                return "Contact updated successfully"
            except ValueError as e:
                return str(e)
        else:
            return "The old number is not correct"
    else:
        return "Contact not found."

@input_error
def phone_contact(args, book):
    username = args[0]
    record = book.find(username)
    if record:
        phone_numbers = ", ".join(str(phone) for phone in record.phones)
        return f"Phone numbers for {username}: {phone_numbers}"
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
    upcoming_birthdays = book.get_upcoming_birthdays()
    if upcoming_birthdays:
        return "Upcoming birthdays:\n" + "\n".join(
            f"{user['name']}'s birthday: {user['congratulation_date']}" for user in upcoming_birthdays
        )
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
    print("  - hello: Get a greeting.")
    print("  - add [name] [phone]: Add or update a contact.")
    print("  - change [name] [old phone] [new phone]: change phone number.")
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
