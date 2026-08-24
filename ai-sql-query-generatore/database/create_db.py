"""
create_db.py
-------------
Generates a realistic e-commerce SQLite database for the AI SQL Query
Generator project.

Tables:

    customers(
        customer_id,
        name,
        email,
        city,
        signup_date
    )

    orders(
        order_id,
        customer_id,
        order_date,
        amount,
        status
    )

Run:

    python database/create_db.py
"""

import random
import sqlite3
from datetime import datetime, timedelta
from pathlib import Path


DB_PATH = (
    Path(__file__).resolve().parent
    / "store.db"
)


FIRST_NAMES = [
    "Aarav",
    "Vivaan",
    "Aditya",
    "Ananya",
    "Diya",
    "Ishaan",
    "Kavya",
    "Meera",
    "Rohan",
    "Sara",
    "Vihaan",
    "Zara",
    "Arjun",
    "Priya",
    "Kabir",
    "Anika",
    "Dev",
    "Neha",
    "Rahul",
    "Sneha",
    "Karan",
    "Pooja",
    "Amit",
    "Riya",
]


LAST_NAMES = [
    "Sharma",
    "Verma",
    "Iyer",
    "Reddy",
    "Nair",
    "Gupta",
    "Menon",
    "Rao",
    "Kumar",
    "Singh",
    "Patel",
    "Das",
    "Joshi",
    "Mehta",
    "Pillai",
    "Shetty",
]


CITIES = [
    "Bangalore",
    "Chennai",
    "Hyderabad",
    "Mumbai",
    "Pune",
    "Delhi",
    "Kolkata",
]


STATUSES = [
    "completed",
    "completed",
    "completed",
    "cancelled",
    "refunded",
]


def build_database(
    seed: int = 42,
    n_customers: int = 60,
):

    random.seed(seed)

    if DB_PATH.exists():
        DB_PATH.unlink()

    conn = sqlite3.connect(
        DB_PATH
    )

    try:

        conn.execute(
            "PRAGMA foreign_keys = ON"
        )

        cursor = conn.cursor()

        cursor.executescript(
            """
            CREATE TABLE customers (
                customer_id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT NOT NULL UNIQUE,
                city TEXT NOT NULL,
                signup_date DATE NOT NULL
            );

            CREATE TABLE orders (
                order_id INTEGER PRIMARY KEY AUTOINCREMENT,
                customer_id INTEGER NOT NULL,
                order_date DATE NOT NULL,
                amount DECIMAL(10, 2) NOT NULL,
                status TEXT NOT NULL,

                FOREIGN KEY (
                    customer_id
                )
                REFERENCES customers(customer_id)
            );

            CREATE INDEX idx_orders_customer_id
                ON orders(customer_id);

            CREATE INDEX idx_orders_order_date
                ON orders(order_date);

            CREATE INDEX idx_orders_status
                ON orders(status);
            """
        )

        # Use the current date so questions such as
        # "last 90 days" remain meaningful.
        today = datetime.now()

        # -------------------------------------------------------------------
        # Customers
        # -------------------------------------------------------------------

        customers = []

        for i in range(
            n_customers
        ):

            first_name = random.choice(
                FIRST_NAMES
            )

            last_name = random.choice(
                LAST_NAMES
            )

            name = (
                f"{first_name} "
                f"{last_name}"
            )

            email = (
                f"{first_name.lower()}."
                f"{last_name.lower()}"
                f"{i}@example.com"
            )

            city = random.choice(
                CITIES
            )

            signup_days_ago = random.randint(
                120,
                900,
            )

            signup_date = (
                today
                - timedelta(
                    days=signup_days_ago
                )
            ).date().isoformat()

            customers.append(
                (
                    name,
                    email,
                    city,
                    signup_date,
                )
            )

        cursor.executemany(
            """
            INSERT INTO customers (
                name,
                email,
                city,
                signup_date
            )
            VALUES (?, ?, ?, ?)
            """,
            customers,
        )

        # -------------------------------------------------------------------
        # Orders
        # -------------------------------------------------------------------

        orders = []

        for customer_id in range(
            1,
            n_customers + 1,
        ):

            number_of_orders = random.choices(
                [
                    0,
                    1,
                    2,
                    3,
                    4,
                    5,
                    6,
                ],
                weights=[
                    5,
                    15,
                    25,
                    20,
                    15,
                    12,
                    8,
                ],
            )[0]

            for _ in range(
                number_of_orders
            ):

                days_ago = random.randint(
                    1,
                    400,
                )

                order_date = (
                    today
                    - timedelta(
                        days=days_ago
                    )
                ).date().isoformat()

                amount = round(
                    random.uniform(
                        299,
                        8999,
                    ),
                    2,
                )

                status = random.choice(
                    STATUSES
                )

                orders.append(
                    (
                        customer_id,
                        order_date,
                        amount,
                        status,
                    )
                )

        cursor.executemany(
            """
            INSERT INTO orders (
                customer_id,
                order_date,
                amount,
                status
            )
            VALUES (?, ?, ?, ?)
            """,
            orders,
        )

        conn.commit()

        customer_count = cursor.execute(
            "SELECT COUNT(*) FROM customers"
        ).fetchone()[0]

        order_count = cursor.execute(
            "SELECT COUNT(*) FROM orders"
        ).fetchone()[0]

        print(
            f"Created {DB_PATH}"
        )

        print(
            f"Customers: {customer_count}"
        )

        print(
            f"Orders: {order_count}"
        )

    finally:

        conn.close()


if __name__ == "__main__":

    build_database()