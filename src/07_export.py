import pandas as pd
import os

PROCESSED_PATH = "data/processed"
OUTPUTS_PATH = "outputs"
os.makedirs(OUTPUTS_PATH, exist_ok=True)


def load_all():
    print("\n Loading all processed data...\n")
    master = pd.read_csv(f"{PROCESSED_PATH}/master_table.csv",
                         parse_dates=["order_purchase_timestamp",
                                      "order_delivered_customer_date",
                                      "order_estimated_delivery_date"])
    orders = pd.read_csv(f"{PROCESSED_PATH}/orders_clean.csv",
                         parse_dates=["order_purchase_timestamp",
                                      "order_delivered_customer_date",
                                      "order_estimated_delivery_date"])
    rfm = pd.read_csv(f"{PROCESSED_PATH}/rfm_segments.csv")
    kpis = pd.read_csv(f"{PROCESSED_PATH}/kpis.csv")
    print(f"  ✓ master    → {master.shape[0]:,} rows")
    print(f"  ✓ orders    → {orders.shape[0]:,} rows")
    print(f"  ✓ rfm       → {rfm.shape[0]:,} rows")
    print(f"  ✓ kpis      → {kpis.shape[0]:,} rows")
    return master, orders, rfm, kpis


def export_revenue_by_category(master):
    df = (master.groupby("category_english")
          .agg(
              Total_Orders=("order_id",       "nunique"),
              Total_Revenue=("payment_value",  "sum"),
              Avg_Price=("price",           "mean"),
              Avg_Review=("review_score",    "mean")
    )
        .round(2)
        .sort_values("Total_Revenue", ascending=False)
        .reset_index())
    df.to_csv(f"{PROCESSED_PATH}/export_revenue_by_category.csv", index=False)
    print(f"\n  ✓ revenue_by_category  → {len(df)} categories")
    return df


def export_monthly_revenue(master):
    master["year_month"] = master["order_purchase_timestamp"].dt.to_period(
        "M").astype(str)
    df = (master[master["order_status"] == "delivered"]
          .groupby("year_month")
          .agg(
              Orders=("order_id",      "nunique"),
              Revenue=("payment_value", "sum")
    )
        .round(2)
        .reset_index())
    df.to_csv(f"{PROCESSED_PATH}/export_monthly_revenue.csv", index=False)
    print(f"  ✓ monthly_revenue      → {len(df)} months")
    return df


def export_regional(master):
    df = (master.groupby("customer_state")
          .agg(
              Orders=("order_id",       "nunique"),
              Customers=("customer_unique_id", "nunique"),
              Revenue=("payment_value",  "sum"),
              Avg_Review=("review_score",   "mean")
    )
        .round(2)
        .sort_values("Revenue", ascending=False)
        .reset_index())
    df.to_csv(f"{PROCESSED_PATH}/export_regional.csv", index=False)
    print(f"  ✓ regional             → {len(df)} states")
    return df


def export_rfm_summary(rfm):
    df = (rfm.groupby("Segment")
          .agg(
              Customers=("customer_unique_id", "count"),
              Avg_Recency=("Recency",            "mean"),
              Avg_Frequency=("Frequency",          "mean"),
              Avg_Revenue=("Monetary",           "mean"),
              Total_Revenue=("Monetary",           "sum")
    )
        .round(2)
        .reset_index())
    df.to_csv(f"{PROCESSED_PATH}/export_rfm_summary.csv", index=False)
    print(f"  ✓ rfm_summary          → {len(df)} segments")
    return df


def export_delivery_performance(orders):
    delivered = orders[orders["order_status"] == "delivered"].copy()
    delivered["on_time"] = (delivered["order_delivered_customer_date"]
                            <= delivered["order_estimated_delivery_date"])
    delivered["delivery_days"] = (delivered["order_delivered_customer_date"]
                                  - delivered["order_purchase_timestamp"]).dt.days
    delivered["year_month"] = delivered["order_purchase_timestamp"].dt.to_period(
        "M").astype(str)

    df = (delivered.groupby("year_month")
          .agg(
              Orders=("order_id",       "count"),
              On_Time_Rate=("on_time",         "mean"),
              Avg_Delivery_Days=("delivery_days", "mean")
    )
        .round(3)
        .reset_index())
    df["On_Time_Rate"] = (df["On_Time_Rate"] * 100).round(1)
    df.to_csv(f"{PROCESSED_PATH}/export_delivery.csv", index=False)
    print(f"  ✓ delivery_performance → {len(df)} months")
    return df


def export_orders_by_hour_day(orders):
    df = (orders.groupby(["purchase_day", "purchase_hour"])
          .size()
          .reset_index(name="order_count"))
    df.to_csv(f"{PROCESSED_PATH}/export_orders_heatmap.csv", index=False)
    print(f"  ✓ orders_heatmap       → {len(df)} hour/day combinations")
    return df


def print_summary(cat, monthly, regional, rfm_sum, delivery):
    print("\n" + "="*55)
    print("        EXPORT SUMMARY — READY FOR POWER BI")
    print("="*55)

    print(f"\n  📦 TOP 5 CATEGORIES BY REVENUE:")
    for _, row in cat.head(5).iterrows():
        print(
            f"     {row['category_english']:30} R${row['Total_Revenue']:>12,.0f}")

    print(f"\n  🗺️  TOP 5 STATES BY REVENUE:")
    for _, row in regional.head(5).iterrows():
        print(
            f"     {row['customer_state']:5} → R${row['Revenue']:>12,.0f}  ({row['Orders']:,} orders)")

    print(f"\n  👥 RFM SEGMENTS:")
    for _, row in rfm_sum.sort_values("Customers", ascending=False).iterrows():
        print(
            f"     {row['Segment']:15} {row['Customers']:>7,} customers  Avg R${row['Avg_Revenue']:>8,.2f}")

    print(f"\n  🚚 DELIVERY (latest month):")
    last = delivery.iloc[-2]
    print(
        f"     {last['year_month']}  On-Time: {last['On_Time_Rate']}%  Avg: {last['Avg_Delivery_Days']:.1f} days")

    print("\n" + "="*55)
    print("\n  Files ready in data/processed/:")
    exports = [
        "export_revenue_by_category.csv",
        "export_monthly_revenue.csv",
        "export_regional.csv",
        "export_rfm_summary.csv",
        "export_delivery.csv",
        "export_orders_heatmap.csv"
    ]
    for f in exports:
        print(f"    ✓ {f}")
    print("\n  Import ALL of these into Power BI!\n")


# ── Run everything ──────────────────────────────────────
if __name__ == "__main__":
    master, orders, rfm, kpis = load_all()

    cat = export_revenue_by_category(master)
    monthly = export_monthly_revenue(master)
    regional = export_regional(master)
    rfm_sum = export_rfm_summary(rfm)
    delivery = export_delivery_performance(orders)
    heatmap = export_orders_by_hour_day(orders)

    print_summary(cat, monthly, regional, rfm_sum, delivery)
    print("  Script 07_export.py complete!\n")
