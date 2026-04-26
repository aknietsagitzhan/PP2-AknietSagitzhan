import csv
from connect import connect


def create_table():
    conn = connect()
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS phonebook (
            id SERIAL PRIMARY KEY,
            name VARCHAR(100),
            phone VARCHAR(20)
        )
    """)

    conn.commit()
    cur.close()
    conn.close()


def insert_from_csv():
    conn = connect()
    cur = conn.cursor()

    with open("/Users/aknietramazan/Desktop/pp2/lab7-ejudge/contacts.csv", encoding="utf-8") as f:
        reader = csv.reader(f)
        for row in reader:
            cur.execute(
                "INSERT INTO phonebook (name, phone) VALUES (%s, %s)",
                row
            )

    conn.commit()
    cur.close()
    conn.close()
    print("CSV imported!")


def add_contact():
    conn = connect()
    cur = conn.cursor()

    name = input("Name: ")
    phone = input("Phone: ")

    cur.execute(
        "INSERT INTO phonebook (name, phone) VALUES (%s, %s)",
        (name, phone)
    )

    conn.commit()
    cur.close()
    conn.close()
    print("Added!")


def show_contacts():
    conn = connect()
    cur = conn.cursor()

    print("1. Show all")
    print("2. Search by name")
    print("3. Search by phone prefix")

    choice = input("Choose: ")

    if choice == "1":
        cur.execute("SELECT * FROM phonebook")

    elif choice == "2":
        name = input("Name: ")
        cur.execute("SELECT * FROM phonebook WHERE name = %s", (name,))

    elif choice == "3":
        prefix = input("Prefix: ")
        cur.execute("SELECT * FROM phonebook WHERE phone LIKE %s", (prefix + "%",))

    rows = cur.fetchall()

    for row in rows:
        print(row)

    cur.close()
    conn.close()


def update_contact():
    conn = connect()
    cur = conn.cursor()

    name = input("Name to update: ")
    new_phone = input("New phone: ")

    cur.execute(
        "UPDATE phonebook SET phone = %s WHERE name = %s",
        (new_phone, name)
    )

    conn.commit()
    cur.close()
    conn.close()
    print("Updated!")


def delete_contact():
    conn = connect()
    cur = conn.cursor()

    print("1. Delete by name")
    print("2. Delete by phone")

    choice = input("Choose: ")

    if choice == "1":
        name = input("Name: ")
        cur.execute("DELETE FROM phonebook WHERE name = %s", (name,))

    elif choice == "2":
        phone = input("Phone: ")
        cur.execute("DELETE FROM phonebook WHERE phone = %s", (phone,))

    conn.commit()
    cur.close()
    conn.close()
    print("Deleted!")


def main():
    create_table()

    while True:
        print("\n--- PHONEBOOK ---")
        print("1. Import from CSV")
        print("2. Add contact")
        print("3. Show/Search")
        print("4. Update")
        print("5. Delete")
        print("6. Exit")

        choice = input("Choose: ")

        if choice == "1":
            insert_from_csv()

        elif choice == "2":
            add_contact()

        elif choice == "3":
            show_contacts()

        elif choice == "4":
            update_contact()

        elif choice == "5":
            delete_contact()

        elif choice == "6":
            break

        else:
            print("Invalid choice!")


if __name__ == "__main__":
    main()