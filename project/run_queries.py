from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Iterable, List


DB_PATH = Path(__file__).parent / "ecom.db"


def format_table(headers: List[str], rows: Iterable[Iterable]) -> str:
    str_rows = [[str(col) for col in row] for row in rows]
    widths = [len(h) for h in headers]
    for row in str_rows:
        for idx, col in enumerate(row):
            widths[idx] = max(widths[idx], len(col))

    def fmt_row(row: List[str]) -> str:
        return " | ".join(col.ljust(widths[idx]) for idx, col in enumerate(row))

    divider = "-+-".join("-" * w for w in widths)
    output = [fmt_row(headers), divider]
    output.extend(fmt_row(row) for row in str_rows)
    return "\n".join(output)


def fetch_report(conn: sqlite3.Connection):
    query = """
        SELECT
            u.user_id,
            u.name,
            o.order_id,
            p.name AS product_name,
            oi.quantity,
            printf('%.2f', oi.unit_price) as unit_price,
            printf('%.2f', o.total_amount) as total_amount,
            COALESCE(pay.status, 'N/A') AS payment_status,
            COALESCE(pay.method, 'N/A') AS payment_method
        FROM order_items oi
        JOIN orders o ON oi.order_id = o.order_id
        JOIN users u ON o.user_id = u.user_id
        JOIN products p ON oi.product_id = p.product_id
        LEFT JOIN payments pay ON pay.order_id = o.order_id
        ORDER BY u.user_id, o.order_id, oi.order_item_id;
    """
    cur = conn.cursor()
    cur.execute(query)
    return cur.fetchall()


def main():
    if not DB_PATH.exists():
        raise SystemExit("Database not found. Run ingest_to_sqlite.py first.")

    conn = sqlite3.connect(DB_PATH)
    rows = fetch_report(conn)
    conn.close()

    headers = [
        "user_id",
        "name",
        "order_id",
        "product_name",
        "quantity",
        "unit_price",
        "total_amount",
        "payment_status",
        "payment_method",
    ]

    if not rows:
        print("No data found. Verify the database has been populated.")
        return

    print(format_table(headers, rows))


if __name__ == "__main__":
    main()

