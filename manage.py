import sys
import csv
from app import app
from store.db import db
from store.models import Customer, Product, Category


def create_tables():
    db.create_all()
    print("Tables created successfully.")


def drop_tables():
    db.drop_all()
    print("Tables dropped successfully.")


def seed_data():
    with open("customers.csv", mode="r", encoding="utf-8") as f:
        reader = csv.DictReader(f)

        for row in reader:
            customer = Customer(
                name=row["name"],
                phone=row["phone"],
            )
            db.session.add(customer)

    with open("products.csv", mode="r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        category_cache = {}

        for row in reader:
            cat_name = row["category"]

            if cat_name not in category_cache:
                stmt = db.select(Category).where(Category.name == cat_name)
                existing_cat = db.session.scalar(stmt)

                if existing_cat:
                    category_cache[cat_name] = existing_cat
                else:
                    new_cat = Category(name=cat_name)
                    db.session.add(new_cat)
                    category_cache[cat_name] = new_cat

            product = Product(
                name=row["name"],
                price=float(row["price"]),
                available=int(row["available"]),
                category=category_cache[cat_name],
            )
            db.session.add(product)

    db.session.commit()


def main():
    print("Hello from store!")

    if len(sys.argv) < 2:
        print("Available commands: create, drop, seed, or reset")
        return

    command = sys.argv[1].lower()

    with app.app_context():
        if command == "create":
            create_tables()
        elif command == "drop":
            drop_tables()
        elif command == "seed":
            seed_data()
        elif command == "reset":
            drop_tables()
            create_tables()
            seed_data()
        else:
            print(f"Unknown command: '{command}'")


if __name__ == "__main__":
    main()
