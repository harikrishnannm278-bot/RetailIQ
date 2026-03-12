import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import os

PROCESSED_PATH = "data/processed"
OUTPUTS_PATH = "outputs"
os.makedirs(OUTPUTS_PATH, exist_ok=True)

# ── STEP 1: Load clean data ────────────────────────────


def load_data():
    master = pd.read_csv(f"{PROCESSED_PATH}/master_table.csv",
                         parse_dates=["order_purchase_timestamp"])
    # Keep only delivered orders
    master = master[master["order_status"] == "delivered"]
    print(f"\n  ✓ Loaded {master.shape[0]:,} delivered orders\n")
    return master

# ── STEP 2: Calculate R, F, M ─────────────────────────


def calculate_rfm(master):
    print(" Calculating RFM scores...\n")

    # Reference date = 1 day after the last purchase in dataset
    snapshot_date = master["order_purchase_timestamp"].max() + \
        pd.Timedelta(days=1)
    print(f"  Snapshot date: {snapshot_date.date()}")

    rfm = (master.groupby("customer_unique_id")
           .agg(
               Recency=("order_purchase_timestamp", lambda x: (
                   snapshot_date - x.max()).days),
               Frequency=("order_id",                 "nunique"),
               Monetary=("payment_value",            "sum")
    )
        .reset_index())

    print(f"\n  RFM Table Sample:")
    print("  " + "-"*60)
    print(f"  {'Customer':^20} {'Recency':^10} {'Frequency':^10} {'Monetary':^10}")
    print("  " + "-"*60)
    for _, row in rfm.head(5).iterrows():
        cust = row["customer_unique_id"][:12] + "..."
        print(
            f"  {cust:^20} {row['Recency']:^10.0f} {row['Frequency']:^10.0f} R${row['Monetary']:>8.2f}")

    return rfm

# ── STEP 3: Score each dimension 1–5 ──────────────────


def score_rfm(rfm):
    print("\n Scoring R, F, M dimensions (1-5)...\n")

    # Recency: LOWER days = BETTER = Score 5
    rfm["R_Score"] = pd.qcut(rfm["Recency"], 5, labels=[5, 4, 3, 2, 1])

    # Frequency: HIGHER = BETTER = Score 5
    rfm["F_Score"] = pd.qcut(rfm["Frequency"].rank(
        method="first"), 5, labels=[1, 2, 3, 4, 5])

    # Monetary: HIGHER = BETTER = Score 5
    rfm["M_Score"] = pd.qcut(rfm["Monetary"], 5, labels=[1, 2, 3, 4, 5])

    # Convert to int for arithmetic
    rfm["R_Score"] = rfm["R_Score"].astype(int)
    rfm["F_Score"] = rfm["F_Score"].astype(int)
    rfm["M_Score"] = rfm["M_Score"].astype(int)
    rfm["RFM_Total"] = rfm["R_Score"] + rfm["F_Score"] + rfm["M_Score"]

    print(
        f"  ✓ Scores assigned. RFM Total range: {rfm['RFM_Total'].min()} – {rfm['RFM_Total'].max()}")
    return rfm

# ── STEP 4: Assign Segments ───────────────────────────


def assign_segments(rfm):
    print("\n Assigning customer segments...\n")

    def segment(row):
        r = row["R_Score"]
        f = row["F_Score"]
        m = row["M_Score"]
        if r >= 4 and f >= 4 and m >= 4:
            return "Champion"
        elif r >= 3 and f >= 3:
            return "Loyal"
        elif r >= 3 and f <= 2:
            return "New Customer"
        elif r <= 2 and f >= 3:
            return "At Risk"
        elif r == 1 and f == 1:
            return "Lost"
        else:
            return "Potential"

    rfm["Segment"] = rfm.apply(segment, axis=1)

    # ── Print segment summary ──────────────────────────
    summary = (rfm.groupby("Segment")
               .agg(
                   Customers=("customer_unique_id", "count"),
                   Avg_Recency=("Recency",            "mean"),
                   Avg_Frequency=("Frequency",          "mean"),
                   Avg_Revenue=("Monetary",           "mean")
    )
        .round(1)
        .sort_values("Customers", ascending=False))

    print(f"  {'Segment':15} {'Customers':>10} {'Avg Recency':>12} {'Avg Freq':>10} {'Avg R$':>10}")
    print("  " + "-"*60)
    for seg, row in summary.iterrows():
        print(
            f"  {seg:15} {row['Customers']:>10,} {row['Avg_Recency']:>11.0f}d {row['Avg_Frequency']:>10.1f} {row['Avg_Revenue']:>9.2f}")

    return rfm, summary

# ── STEP 5: Visualise ─────────────────────────────────


def visualise(rfm, summary):
    print("\n Building charts...\n")

    colors = {
        "Champion":    "#1a7a4a",
        "Loyal":       "#2e75b6",
        "New Customer": "#c9a227",
        "Potential":   "#8e44ad",
        "At Risk":     "#e67e22",
        "Lost":        "#c0392b"
    }

    # ── Chart 1: Segment size ──────────────────────────
    seg_counts = rfm["Segment"].value_counts()
    chart_colors = [colors[s] for s in seg_counts.index]

    plt.figure(figsize=(10, 6))
    bars = plt.bar(seg_counts.index, seg_counts.values,
                   color=chart_colors, edgecolor="white", linewidth=1.5)

    for bar, count in zip(bars, seg_counts.values):
        pct = count / len(rfm) * 100
        plt.text(bar.get_x() + bar.get_width()/2,
                 bar.get_height() + 100,
                 f"{count:,}\n({pct:.1f}%)",
                 ha="center", va="bottom", fontsize=9, fontweight="bold")

    plt.title("Customer Segments — RFM Analysis",
              fontsize=14, fontweight="bold", pad=15)
    plt.ylabel("Number of Customers")
    plt.xlabel("Segment")
    plt.tight_layout()
    plt.savefig(f"{OUTPUTS_PATH}/05_rfm_segments.png", dpi=150)
    plt.close()
    print("  ✓ Chart saved → outputs/05_rfm_segments.png")

    # ── Chart 2: Avg Revenue per Segment ──────────────
    rev_data = summary["Avg_Revenue"].sort_values(ascending=True)
    chart_colors2 = [colors[s] for s in rev_data.index]

    plt.figure(figsize=(10, 5))
    bars2 = plt.barh(rev_data.index, rev_data.values, color=chart_colors2)

    for bar, val in zip(bars2, rev_data.values):
        plt.text(bar.get_width() + 5, bar.get_y() + bar.get_height()/2,
                 f"R${val:,.0f}", va="center", fontsize=9)

    plt.title("Average Revenue per Customer Segment",
              fontsize=13, fontweight="bold")
    plt.xlabel("Average Revenue (R$)")
    plt.tight_layout()
    plt.savefig(f"{OUTPUTS_PATH}/06_rfm_revenue.png", dpi=150)
    plt.close()
    print("  ✓ Chart saved → outputs/06_rfm_revenue.png")

# ── STEP 6: Save results ──────────────────────────────


def save_results(rfm):
    rfm.to_csv(f"{PROCESSED_PATH}/rfm_segments.csv", index=False)
    print(f"\n  ✓ RFM data saved → data/processed/rfm_segments.csv")


# ── Run everything ─────────────────────────────────────
if __name__ == "__main__":
    master = load_data()
    rfm = calculate_rfm(master)
    rfm = score_rfm(rfm)
    rfm, summary = assign_segments(rfm)
    visualise(rfm, summary)
    save_results(rfm)
    print("\n Script 04_rfm.py complete!\n")
