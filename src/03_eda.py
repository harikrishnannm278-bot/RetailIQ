import pandas as pd
import matplotlib.pyplot as plt
import os

PROCESSED_PATH = "data/processed"
OUTPUTS_PATH = "outputs"
os.makedirs(OUTPUTS_PATH, exist_ok=True)


def load_clean_data():
    master = pd.read_csv(f"{PROCESSED_PATH}/master_table.csv")
    orders = pd.read_csv(f"{PROCESSED_PATH}/orders_clean.csv")
    print(f"\n  ✓ Master table loaded → {master.shape[0]:,} rows\n")
    return master, orders


def analyse_revenue(master):
    print(" analysing Revenue...\n")

    # ── Top 10 categories by revenue ──────────────────
    cat_rev = (master.groupby("category_english")["payment_value"]
               .sum()
               .sort_values(ascending=False)
               .head(10)
               .reset_index())
    cat_rev.columns = ["Category", "Revenue"]

    print("  Top 10 Categories by Revenue:")
    print("  " + "-"*40)
    for _, row in cat_rev.iterrows():
        print(f"  {row['Category']:30} R${row['Revenue']:>12,.2f}")

    # ── Plot it ───────────────────────────────────────
    plt.figure(figsize=(12, 6))
    plt.barh(cat_rev["Category"][::-1],
             cat_rev["Revenue"][::-1], color="steelblue")
    plt.xlabel("Total Revenue (R$)")
    plt.title("Top 10 Product Categories by Revenue")
    plt.tight_layout()
    plt.savefig(f"{OUTPUTS_PATH}/01_top_categories.png", dpi=150)
    plt.close()
    print("\n  ✓ Chart saved → outputs/01_top_categories.png")


def analyse_orders_over_time(orders):
    print("\n Analysing Orders Over Time...\n")

    orders["order_purchase_timestamp"] = pd.to_datetime(
        orders["order_purchase_timestamp"])
    orders["year_month"] = orders["order_purchase_timestamp"].dt.to_period(
        "M").astype(str)

    monthly = (orders[orders["order_status"] == "delivered"]
               .groupby("year_month")
               .size()
               .reset_index(name="order_count"))

    print("  Monthly Orders (delivered):")
    print("  " + "-"*30)
    for _, row in monthly.iterrows():
        bar = "█" * (row["order_count"] // 200)
        print(f"  {row['year_month']}  {bar} {row['order_count']:,}")

    # ── Plot it ───────────────────────────────────────
    plt.figure(figsize=(14, 5))
    plt.plot(monthly["year_month"], monthly["order_count"],
             marker="o", color="steelblue", linewidth=2)
    plt.xticks(rotation=45, ha="right")
    plt.title("Monthly Delivered Orders Over Time")
    plt.xlabel("Month")
    plt.ylabel("Number of Orders")
    plt.tight_layout()
    plt.savefig(f"{OUTPUTS_PATH}/02_monthly_orders.png", dpi=150)
    plt.close()
    print("\n  ✓ Chart saved → outputs/02_monthly_orders.png")


def analyse_reviews(master):
    print("\n Analysing Review Scores...\n")

    review_counts = (master["review_score"]
                     .value_counts()
                     .sort_index())

    total = review_counts.sum()
    print("  Review Score Distribution:")
    print("  " + "-"*30)
    for score, count in review_counts.items():
        bar = "█" * (count // 2000)
        pct = count / total * 100
        print(f"  ⭐ {score}  {bar} {count:,}  ({pct:.1f}%)")

    # ── Plot it ───────────────────────────────────────
    plt.figure(figsize=(8, 5))
    plt.bar(review_counts.index, review_counts.values,
            color=["#e74c3c", "#e67e22", "#f1c40f", "#2ecc71", "#27ae60"])
    plt.title("Customer Review Score Distribution")
    plt.xlabel("Review Score (1=Worst, 5=Best)")
    plt.ylabel("Number of Reviews")
    plt.tight_layout()
    plt.savefig(f"{OUTPUTS_PATH}/03_review_scores.png", dpi=150)
    plt.close()
    print("\n  ✓ Chart saved → outputs/03_review_scores.png")


def analyse_orders_by_day(orders):
    print("\n Analysing Orders by Day of Week...\n")

    day_order = ["Monday", "Tuesday", "Wednesday",
                 "Thursday", "Friday", "Saturday", "Sunday"]
    day_counts = (orders["purchase_day"]
                  .value_counts()
                  .reindex(day_order))

    print("  Orders by Day:")
    print("  " + "-"*30)
    for day, count in day_counts.items():
        bar = "█" * (count // 500)
        print(f"  {day:12} {bar} {count:,}")

    # ── Plot it ───────────────────────────────────────
    plt.figure(figsize=(10, 5))
    plt.bar(day_counts.index, day_counts.values, color="coral")
    plt.title("Orders by Day of Week")
    plt.ylabel("Number of Orders")
    plt.xticks(rotation=30)
    plt.tight_layout()
    plt.savefig(f"{OUTPUTS_PATH}/04_orders_by_day.png", dpi=150)
    plt.close()
    print("\n  ✓ Chart saved → outputs/04_orders_by_day.png")


# ── Run everything ─────────────────────────────────────
if __name__ == "__main__":
    master, orders = load_clean_data()
    analyse_revenue(master)
    analyse_orders_over_time(orders)
    analyse_reviews(master)
    analyse_orders_by_day(orders)
    print("\n Script 03_eda.py complete!")
    print(" Check your outputs/ folder for 4 charts!\n")
