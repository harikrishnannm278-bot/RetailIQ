import pandas as pd
import os

# ── Configuration ──────────────────────────────────────
RAW_DATA_PATH = "data/raw"

# ── File list defined inside function scope ────────────


def load_all_data(path):

    files = {
        "orders":      "olist_orders_dataset.csv",
        "customers":   "olist_customers_dataset.csv",
        "items":       "olist_order_items_dataset.csv",
        "payments":    "olist_order_payments_dataset.csv",
        "reviews":     "olist_order_reviews_dataset.csv",
        "products":    "olist_products_dataset.csv",
        "sellers":     "olist_sellers_dataset.csv",
        "geolocation": "olist_geolocation_dataset.csv",
        "categories":  "product_category_name_translation.csv"
    }

    dataframes = {}
    print("\n Loading Olist Datasets...\n")

    for name, filename in files.items():
        full_path = os.path.join(path, filename)
        df = pd.read_csv(full_path)
        dataframes[name] = df
        print(f"  ✓ {name:15} → {df.shape[0]:,} rows | {df.shape[1]} columns")

    print("\n All datasets loaded successfully!\n")
    return dataframes


# ── Run it ─────────────────────────────────────────────
if __name__ == "__main__":
    data = load_all_data(RAW_DATA_PATH)
