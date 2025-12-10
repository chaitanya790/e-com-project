from __future__ import annotations

import csv
import sqlite3
from pathlib import Path
from typing import Iterable, Tuple


DATA_DIR = Path(__file__).parent / "data"
DB_PATH = Path(__file__).parent / "ecom.db"


def ensure_tables(conn: sqlite3.Connection) -> None:
    cur = conn.cursor()
    cur.executescript(
        """
        PRAGMA foreign_keys = ON;

        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            email TEXT NOT NULL,
            phone TEXT,
            created_at TEXT
        );

        CREATE TABLE IF NOT EXISTS products (
            product_id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            category TEXT,
            price REAL,
            stock INTEGER
        );

        CREATE TABLE IF NOT EXISTS orders (
            order_id INTEGER PRIMARY KEY,
            user_id INTEGER NOT NULL REFERENCES users(user_id),
            order_date TEXT,
            total_amount REAL
        );

        CREATE TABLE IF NOT EXISTS order_items (
            order_item_id INTEGER PRIMARY KEY,
            order_id INTEGER NOT NULL REFERENCES orders(order_id),
            product_id INTEGER NOT NULL REFERENCES products(product_id),
            quantity INTEGER NOT NULL,
            unit_price REAL NOT NULL
        );

        CREATE TABLE IF NOT EXISTS payments (
            payment_id INTEGER PRIMARY KEY,
            order_id INTEGER NOT NULL REFERENCES orders(order_id),
            amount REAL NOT NULL,
            method TEXT,
            status TEXT,
            paid_at TEXT
        );
        """
    )
    conn.commit()


def clear_tables(conn: sqlite3.Connection) -> None:
    cur = conn.cursor()
    for table in ["payments", "order_items", "orders", "products", "users"]:
        cur.execute(f"DELETE FROM {table}")
    conn.commit()


def load_users(path: Path) -> Iterable[Tuple]:
    with path.open() as f:
        for row in csv.DictReader(f):
            yield (
                int(row["user_id"]),
                row["name"],
                row["email"],
                row["phone"],
                row["created_at"],
            )


def load_products(path: Path) -> Iterable[Tuple]:
    with path.open() as f:
        for row in csv.DictReader(f):
            yield (
                int(row["product_id"]),
                row["name"],
                row["category"],
                float(row["price"]),
                int(row["stock"]),
            )


def load_orders(path: Path) -> Iterable[Tuple]:
    with path.open() as f:
        for row in csv.DictReader(f):
            yield (int(row["order_id"]), int(row["user_id"]), row["order_date"], float(row["total_amount"]))


def load_order_items(path: Path) -> Iterable[Tuple]:
    with path.open() as f:
        for row in csv.DictReader(f):
            yield (
                int(row["order_item_id"]),
                int(row["order_id"]),
                int(row["product_id"]),
                int(row["quantity"]),
                float(row["unit_price"]),
            )


def load_payments(path: Path) -> Iterable[Tuple]:
    with path.open() as f:
        for row in csv.DictReader(f):
            yield (
                int(row["payment_id"]),
                int(row["order_id"]),
                float(row["amount"]),
                row["method"],
                row["status"],
                row["paid_at"],
            )


def main():
    if not DATA_DIR.exists():
        raise SystemExit(f"Data directory not found at {DATA_DIR}")

    conn = sqlite3.connect(DB_PATH)
    ensure_tables(conn)
    clear_tables(conn)

    cur = conn.cursor()
    cur.executemany(
        "INSERT INTO users (user_id, name, email, phone, created_at) VALUES (?, ?, ?, ?, ?)",
        load_users(DATA_DIR / "users.csv"),
    )
    cur.executemany(
        "INSERT INTO products (product_id, name, category, price, stock) VALUES (?, ?, ?, ?, ?)",
        load_products(DATA_DIR / "products.csv"),
    )
    cur.executemany(
        "INSERT INTO orders (order_id, user_id, order_date, total_amount) VALUES (?, ?, ?, ?)",
        load_orders(DATA_DIR / "orders.csv"),
    )
    cur.executemany(
        "INSERT INTO order_items (order_item_id, order_id, product_id, quantity, unit_price) VALUES (?, ?, ?, ?, ?)",
        load_order_items(DATA_DIR / "order_items.csv"),
    )
    cur.executemany(
        "INSERT INTO payments (payment_id, order_id, amount, method, status, paid_at) VALUES (?, ?, ?, ?, ?, ?)",
        load_payments(DATA_DIR / "payments.csv"),
    )
    conn.commit()

    print("Rows inserted:")
    for table in ["users", "products", "orders", "order_items", "payments"]:
        count = cur.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
        print(f"  {table}: {count}")

    conn.close()


if __name__ == "__main__":
    main()

