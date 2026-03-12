import pandas as pd
import sqlite3
import os

RAW_DATA_PATH = "data/raw"

files = {
    "orders":      "olist_orders_dataset.csv",
    "customers":   "olist_customers_dataset.csv",
    "order_items": "olist_order_items_dataset.csv",
    "payments":    "olist_order_payments_dataset.csv",
    "reviews":     "olist_order_reviews_dataset.csv",
    "products":    "olist_products_dataset.csv",
    "sellers":     "olist_sellers_dataset.csv",
    "geolocation": "olist_geolocation_dataset.csv",
    "categories":  "product_category_name_translation.csv"
}

print("\n Creating RetailIQ database...\n")
conn = sqlite3.connect("retailiq.db")

for table, filename in files.items():
    df = pd.read_csv(os.path.join(RAW_DATA_PATH, filename))
    df.to_sql(table, conn, if_exists="replace", index=False)
    print(f"  ✓ {table:15} → {len(df):,} rows loaded")

conn.close()
print("\n  ✓ retailiq.db created successfully!")
print("  ✓ Location: RetailIQ/retailiq.db\n")
