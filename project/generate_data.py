from __future__ import annotations

import argparse
import csv
import json
import os
import random
from dataclasses import asdict, dataclass
from datetime import datetime, timedelta
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path
from typing import List


random.seed(42)


@dataclass
class User:
    user_id: int
    name: str
    email: str
    phone: str
    created_at: str


@dataclass
class Product:
    product_id: int
    name: str
    category: str
    price: str
    stock: int


@dataclass
class Order:
    order_id: int
    user_id: int
    order_date: str
    total_amount: str


@dataclass
class OrderItem:
    order_item_id: int
    order_id: int
    product_id: int
    quantity: int
    unit_price: str


@dataclass
class Payment:
    payment_id: int
    order_id: int
    amount: str
    method: str
    status: str
    paid_at: str


def money(value: float) -> str:
    return str(Decimal(value).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP))


def random_date(start: datetime, end: datetime) -> datetime:
    delta = end - start
    return start + timedelta(seconds=random.randint(0, int(delta.total_seconds())))


def generate_users(count: int) -> List[User]:
    first_names = [
        "Ava",
        "Liam",
        "Noah",
        "Olivia",
        "Ethan",
        "Sophia",
        "Mason",
        "Emma",
        "Isabella",
        "Lucas",
        "Mia",
        "Elijah",
    ]
    last_names = [
        "Thompson",
        "Rodriguez",
        "Patel",
        "Chen",
        "Walker",
        "Nguyen",
        "Johnson",
        "Garcia",
        "Wright",
        "Kim",
        "Davis",
        "Bennett",
    ]
    today = datetime.utcnow()
    users = []
    for uid in range(1, count + 1):
        first = random.choice(first_names)
        last = random.choice(last_names)
        name = f"{first} {last}"
        email = f"{first}.{last}{uid}@example.com".lower()
        phone = f"555-{random.randint(200, 999)}-{random.randint(1000, 9999)}"
        created_at = random_date(today - timedelta(days=365), today - timedelta(days=10))
        users.append(
            User(
                user_id=uid,
                name=name,
                email=email,
                phone=phone,
                created_at=created_at.strftime("%Y-%m-%d"),
            )
        )
    return users


def generate_products(count: int) -> List[Product]:
    adjectives = ["Aurora", "Summit", "TrailRunner", "Cypress", "Horizon", "Breeze", "Cascade", "Drift"]
    nouns = ["Laptop", "Headphones", "Smartwatch", "Coffee Grinder", "Standing Desk", "Air Purifier", "Water Bottle", "Wireless Mouse"]
    categories = ["Electronics", "Wearables", "Kitchen", "Furniture", "Home", "Outdoors", "Accessories"]
    products = []
    for pid in range(1, count + 1):
        name = f"{random.choice(adjectives)} {random.choice(nouns)}"
        category = random.choice(categories)
        base_price = random.uniform(20, 1200)
        stock = random.randint(20, 400)
        products.append(
            Product(
                product_id=pid,
                name=name,
                category=category,
                price=money(base_price),
                stock=stock,
            )
        )
    return products


def generate_orders(users: List[User], products: List[Product], order_count: int):
    today = datetime.utcnow()
    start_window = today - timedelta(days=120)
    orders: List[Order] = []
    items: List[OrderItem] = []
    payments: List[Payment] = []

    order_item_id = 1
    payment_id = 1
    for oid in range(1, order_count + 1):
        user = random.choice(users)
        order_date = random_date(start_window, today - timedelta(days=1))
        product_choices = random.sample(products, k=random.randint(1, min(4, len(products))))
        line_total = Decimal("0.00")
        for product in product_choices:
            qty = random.randint(1, 3)
            unit_price = Decimal(product.price)
            line_total += unit_price * qty
            items.append(
                OrderItem(
                    order_item_id=order_item_id,
                    order_id=oid,
                    product_id=product.product_id,
                    quantity=qty,
                    unit_price=money(unit_price),
                )
            )
            order_item_id += 1

        total_amount = money(line_total)
        orders.append(
            Order(
                order_id=oid,
                user_id=user.user_id,
                order_date=order_date.strftime("%Y-%m-%d"),
                total_amount=total_amount,
            )
        )

        status = random.choices(["Completed", "Pending", "Failed"], weights=[0.82, 0.12, 0.06])[0]
        payment_method = random.choice(["Credit Card", "Debit Card", "PayPal", "Apple Pay"])
        paid_at = (order_date + timedelta(hours=random.randint(1, 48))).strftime("%Y-%m-%d %H:%M:%S")
        payments.append(
            Payment(
                payment_id=payment_id,
                order_id=oid,
                amount=total_amount,
                method=payment_method,
                status=status,
                paid_at=paid_at,
            )
        )
        payment_id += 1

    return orders, items, payments


def write_csv(path: Path, rows: List[dataclass], fieldnames: List[str]):
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow(asdict(row))


def write_json(path: Path, rows: List[dataclass]):
    with path.open("w", encoding="utf-8") as f:
        json.dump([asdict(r) for r in rows], f, indent=2)


def main():
    parser = argparse.ArgumentParser(description="Generate synthetic e-commerce data.")
    parser.add_argument("--users", type=int, default=25, help="Number of users to generate")
    parser.add_argument("--products", type=int, default=15, help="Number of products to generate")
    parser.add_argument("--orders", type=int, default=40, help="Number of orders to generate")
    parser.add_argument("--json", action="store_true", help="Also write .json copies alongside CSVs")
    args = parser.parse_args()

    data_dir = Path(__file__).parent / "data"
    os.makedirs(data_dir, exist_ok=True)

    users = generate_users(args.users)
    products = generate_products(args.products)
    orders, order_items, payments = generate_orders(users, products, args.orders)

    write_csv(data_dir / "users.csv", users, ["user_id", "name", "email", "phone", "created_at"])
    write_csv(data_dir / "products.csv", products, ["product_id", "name", "category", "price", "stock"])
    write_csv(data_dir / "orders.csv", orders, ["order_id", "user_id", "order_date", "total_amount"])
    write_csv(
        data_dir / "order_items.csv",
        order_items,
        ["order_item_id", "order_id", "product_id", "quantity", "unit_price"],
    )
    write_csv(
        data_dir / "payments.csv",
        payments,
        ["payment_id", "order_id", "amount", "method", "status", "paid_at"],
    )

    if args.json:
        write_json(data_dir / "users.json", users)
        write_json(data_dir / "products.json", products)
        write_json(data_dir / "orders.json", orders)
        write_json(data_dir / "order_items.json", order_items)
        write_json(data_dir / "payments.json", payments)

    print(f"Data written to {data_dir.resolve()}")


if __name__ == "__main__":
    main()

