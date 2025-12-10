# E-commerce Synthetic Data Pipeline

Complete, ready-to-run pipeline that generates realistic e-commerce data, ingests it into SQLite, and produces a joined analytics report.

## Folder Structure
```
project/
├── data/
│   ├── users.csv
│   ├── products.csv
│   ├── orders.csv
│   ├── order_items.csv
│   └── payments.csv
├── ecom.db              # created after ingestion
├── generate_data.py
├── ingest_to_sqlite.py
└── run_queries.py
```

Sample CSVs are already populated so you can ingest immediately. You can also regenerate fresh synthetic data any time.

## Prerequisites
- Python 3.9+
- No third-party packages required (only the standard library)

## 1) Generate Synthetic Data
Creates new CSVs (and optional JSON copies) under `data/`.
```bash
cd project
python generate_data.py              # default volumes: 25 users, 15 products, 40 orders
python generate_data.py --json       # also emits *.json beside the CSVs
# Other knobs: --users 50 --products 20 --orders 75
```

## 2) Ingest into SQLite
Loads all CSVs into `ecom.db` with matching tables.
```bash
python ingest_to_sqlite.py
```
Expected output: row counts for each table confirming the insert volume.

## 3) Run the Joined SQL Report
Produces a combined view across users, orders, order items, products, and payments.
```bash
python run_queries.py
```
Output columns:
`user_id, name, order_id, product_name, quantity, unit_price, total_amount, payment_status, payment_method`.

## Notes
- The ingestion script clears tables before each load so you can regenerate data freely.
- Payment rows are generated per order with realistic statuses and methods.

