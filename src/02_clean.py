from load_01 import load_all_data
import pandas as pd
import os
import sys

# ── import our loader from script 1 ───────────────────
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

RAW_DATA_PATH = "data/raw"
PROCESSED_PATH = "data/processed"


def clean_data(data):
    print("\n Cleaning datasets...\n")

    # ── 1. ORDERS ──────────────────────────────────────
    orders = data["orders"].copy()

    # Convert date columns from text → real dates
    date_cols = [
        "order_purchase_timestamp",
        "order_approved_at",
        "order_delivered_carrier_date",
        "order_delivered_customer_date",
        "order_estimated_delivery_date"
    ]
    for col in date_cols:
        orders[col] = pd.to_datetime(orders[col])

    # Extract useful time features
    orders["purchase_year"] = orders["order_purchase_timestamp"].dt.year
    orders["purchase_month"] = orders["order_purchase_timestamp"].dt.month
    orders["purchase_day"] = orders["order_purchase_timestamp"].dt.day_name()
    orders["purchase_hour"] = orders["order_purchase_timestamp"].dt.hour

    print(f"  ✓ orders cleaned    → date columns converted, time features added")

    # ── 2. REVIEWS ─────────────────────────────────────
    reviews = data["reviews"].copy()
    reviews["review_comment_message"].fillna("No comment", inplace=True)
    reviews["review_comment_title"].fillna("No title", inplace=True)
    print(f"  ✓ reviews cleaned   → missing comments filled")

    # ── 3. PRODUCTS ────────────────────────────────────
    products = data["products"].copy()
    products["product_category_name"].fillna("unknown", inplace=True)
    print(f"  ✓ products cleaned  → missing categories filled")

    # ── 4. MERGE PRODUCTS WITH ENGLISH CATEGORIES ──────
    categories = data["categories"].copy()
    categories.columns = ["product_category_name", "category_english"]
    products = products.merge(
        categories, on="product_category_name", how="left")
    products["category_english"].fillna("unknown", inplace=True)
    print(f"  ✓ products merged   → English category names added")

    # ── 5. BUILD MASTER TABLE ──────────────────────────
    payments_agg = (data["payments"]
                    .groupby("order_id")["payment_value"]
                    .sum()
                    .reset_index())

    reviews_clean = reviews[["order_id", "review_score"]
                            ].drop_duplicates("order_id")

    master = (orders
              .merge(data["customers"], on="customer_id", how="left")
              .merge(data["items"][["order_id", "product_id", "seller_id", "price", "freight_value"]], on="order_id", how="left")
              .merge(products[["product_id", "category_english"]], on="product_id", how="left")
              .merge(payments_agg, on="order_id", how="left")
              .merge(reviews_clean, on="order_id", how="left"))

    print(
        f"  ✓ master table built → {master.shape[0]:,} rows | {master.shape[1]} columns")

    return orders, reviews, products, master


def save_data(orders, reviews, products, master):
    os.makedirs(PROCESSED_PATH, exist_ok=True)

    orders.to_csv(f"{PROCESSED_PATH}/orders_clean.csv", index=False)
    reviews.to_csv(f"{PROCESSED_PATH}/reviews_clean.csv", index=False)
    products.to_csv(f"{PROCESSED_PATH}/products_clean.csv", index=False)
    master.to_csv(f"{PROCESSED_PATH}/master_table.csv", index=False)

    print(f"\n  ✓ All cleaned files saved to data/processed/\n")


# ── Run it ─────────────────────────────────────────────
if __name__ == "__main__":
    data = load_all_data(RAW_DATA_PATH)
    orders, reviews, products, master = clean_data(data)
    save_data(orders, reviews, products, master)
    print(" Script 02_clean.py complete!\n")
