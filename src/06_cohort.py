import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import os

PROCESSED_PATH = "data/processed"
OUTPUTS_PATH = "outputs"
os.makedirs(OUTPUTS_PATH, exist_ok=True)


def load_data():
    orders = pd.read_csv(f"{PROCESSED_PATH}/orders_clean.csv",
                         parse_dates=["order_purchase_timestamp"])
    customers = pd.read_csv("data/raw/olist_customers_dataset.csv")
    delivered = orders[orders["order_status"] == "delivered"].copy()
    df = delivered.merge(customers, on="customer_id", how="left")
    print(f"\n  ✓ Loaded {len(df):,} delivered orders\n")
    return df


def build_cohort(df):
    print(" Building cohort table...\n")

    # ── Each order's purchase month ────────────────────
    df["PurchaseMonth"] = df["order_purchase_timestamp"].dt.to_period("M")

    # ── Each customer's FIRST purchase month = cohort ──
    df["CohortMonth"] = (df.groupby("customer_unique_id")["PurchaseMonth"]
                           .transform("min"))

    # ── How many months since first purchase ──────────
    df["CohortIndex"] = (df["PurchaseMonth"] -
                         df["CohortMonth"]).apply(lambda x: x.n)

    # ── Count unique customers per cohort + index ──────
    cohort_data = (df.groupby(["CohortMonth", "CohortIndex"])["customer_unique_id"]
                     .nunique()
                     .reset_index())

    cohort_pivot = cohort_data.pivot(index="CohortMonth",
                                     columns="CohortIndex",
                                     values="customer_unique_id")

    # ── Retention % — divide by cohort size (column 0) ─
    cohort_size = cohort_pivot.iloc[:, 0]
    retention = cohort_pivot.divide(cohort_size, axis=0).round(3) * 100

    print(
        f"  ✓ Cohort table built → {retention.shape[0]} cohorts × {retention.shape[1]} months")
    return retention, cohort_size


def print_cohort_text(retention, cohort_size):
    print("\n  Cohort Retention Table (% returning customers):\n")
    print(
        f"  {'Cohort':<12} {'Size':>6}   Month0   Month1   Month2   Month3   Month4")
    print("  " + "-"*65)

    for cohort in retention.index:
        size = int(cohort_size[cohort])
        row = retention.loc[cohort]
        m0 = f"{row.get(0, 0):.0f}%" if 0 in row.index else "-"
        m1 = f"{row.get(1, 0):.1f}%" if 1 in row.index else "-"
        m2 = f"{row.get(2, 0):.1f}%" if 2 in row.index else "-"
        m3 = f"{row.get(3, 0):.1f}%" if 3 in row.index else "-"
        m4 = f"{row.get(4, 0):.1f}%" if 4 in row.index else "-"
        print(
            f"  {str(cohort):<12} {size:>6}   {m0:>6}   {m1:>6}   {m2:>6}   {m3:>6}   {m4:>6}")


def visualise_cohort(retention):
    print("\n Building cohort heatmap...\n")

    fig, ax = plt.subplots(figsize=(16, 10))

    # ── Draw heatmap manually with colours ────────────
    data = retention.values
    months = retention.columns.tolist()
    cohorts = [str(c) for c in retention.index]

    im = ax.imshow(data, cmap="YlGn", aspect="auto", vmin=0, vmax=100)

    # ── Add value labels inside each cell ─────────────
    for i in range(len(cohorts)):
        for j in range(len(months)):
            val = data[i][j]
            if not pd.isna(val):
                color = "white" if val > 60 else "black"
                ax.text(j, i, f"{val:.0f}%",
                        ha="center", va="center",
                        fontsize=8, color=color, fontweight="bold")

    # ── Axis labels ───────────────────────────────────
    ax.set_xticks(range(len(months)))
    ax.set_xticklabels([f"Month {m}" for m in months], fontsize=9)
    ax.set_yticks(range(len(cohorts)))
    ax.set_yticklabels(cohorts, fontsize=9)

    ax.set_title("Customer Cohort Retention Rate (%)\nHow many customers come back each month?",
                 fontsize=14, fontweight="bold", pad=20)
    ax.set_xlabel("Months Since First Purchase", fontsize=11)
    ax.set_ylabel("Cohort (First Purchase Month)", fontsize=11)

    plt.colorbar(im, ax=ax, label="Retention %")
    plt.tight_layout()
    plt.savefig(f"{OUTPUTS_PATH}/07_cohort_heatmap.png", dpi=150)
    plt.close()
    print("  ✓ Chart saved → outputs/07_cohort_heatmap.png")


def business_insight(retention):
    print("\n" + "="*55)
    print("        COHORT ANALYSIS — KEY INSIGHTS")
    print("="*55)

    # Month 1 average retention across all cohorts
    if 1 in retention.columns:
        avg_m1 = retention[1].dropna().mean()
        print(f"\n  Month 1 Avg Retention:  {avg_m1:.1f}%")
        print(
            f"  → {100-avg_m1:.1f}% of customers never come back after first purchase")

    if 2 in retention.columns:
        avg_m2 = retention[2].dropna().mean()
        print(f"\n  Month 2 Avg Retention:  {avg_m2:.1f}%")

    # Best and worst cohort
    m1_retention = retention[1].dropna()
    best = m1_retention.idxmax()
    worst = m1_retention.idxmin()
    print(
        f"\n  Best cohort  (Month 1): {best}  → {m1_retention[best]:.1f}% returned")
    print(
        f"  Worst cohort (Month 1): {worst} → {m1_retention[worst]:.1f}% returned")
    print("\n" + "="*55 + "\n")


# ── Run everything ─────────────────────────────────────
if __name__ == "__main__":
    df = load_data()
    retention, cohort_size = build_cohort(df)
    print_cohort_text(retention, cohort_size)
    visualise_cohort(retention)
    business_insight(retention)
    print("  Script 06_cohort.py complete!\n")
