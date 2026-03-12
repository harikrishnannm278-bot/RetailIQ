import pandas as pd
import os

PROCESSED_PATH = "data/processed"
OUTPUTS_PATH = "outputs"


def load_data():
    master = pd.read_csv(f"{PROCESSED_PATH}/master_table.csv",
                         parse_dates=["order_purchase_timestamp",
                                      "order_delivered_customer_date",
                                      "order_estimated_delivery_date"])
    orders = pd.read_csv(f"{PROCESSED_PATH}/orders_clean.csv",
                         parse_dates=["order_purchase_timestamp",
                                      "order_delivered_customer_date",
                                      "order_estimated_delivery_date"])
    rfm = pd.read_csv(f"{PROCESSED_PATH}/rfm_segments.csv")
    return master, orders, rfm


def calculate_kpis(master, orders, rfm):

    # ── REVENUE KPIs ───────────────────────────────────
    total_revenue = master["payment_value"].sum()
    total_orders = master["order_id"].nunique()
    aov = total_revenue / total_orders

    # ── CUSTOMER KPIs ──────────────────────────────────
    total_customers = rfm["customer_unique_id"].nunique()
    champions = (rfm["Segment"] == "Champion").sum()
    at_risk = (rfm["Segment"] == "At Risk").sum()
    champion_revenue = rfm[rfm["Segment"] == "Champion"]["Monetary"].sum()
    champion_pct_rev = champion_revenue / rfm["Monetary"].sum() * 100

    # ── OPERATIONAL KPIs ───────────────────────────────
    delivered = orders[orders["order_status"] == "delivered"].copy()
    cancelled = orders[orders["order_status"] == "canceled"]
    cancel_rate = len(cancelled) / len(orders) * 100

    delivered["on_time"] = (delivered["order_delivered_customer_date"]
                            <= delivered["order_estimated_delivery_date"])
    on_time_rate = delivered["on_time"].mean() * 100

    delivered["delivery_days"] = (
        delivered["order_delivered_customer_date"] -
        delivered["order_purchase_timestamp"]
    ).dt.days
    avg_delivery_days = delivered["delivery_days"].mean()

    # ── SATISFACTION KPIs ──────────────────────────────
    avg_review = master["review_score"].mean()
    pct_5star = (master["review_score"] == 5).mean() * 100
    pct_1star = (master["review_score"] == 1).mean() * 100
    nps_proxy = pct_5star - pct_1star

    # ── PRINT FULL DASHBOARD ───────────────────────────
    print("\n" + "="*55)
    print("        RETAILIQ — BUSINESS KPI DASHBOARD")
    print("="*55)

    print("\n  💰 REVENUE")
    print(f"     Total Revenue          R$ {total_revenue:>15,.2f}")
    print(f"     Total Orders               {total_orders:>15,}")
    print(f"     Avg Order Value        R$ {aov:>15,.2f}")

    print("\n  👥 CUSTOMERS")
    print(f"     Total Customers            {total_customers:>15,}")
    print(f"     Champions                  {champions:>15,}")
    print(f"     At Risk                    {at_risk:>15,}")
    print(f"     Champion Revenue Share       {champion_pct_rev:>13.1f}%")

    print("\n  🚚 OPERATIONS")
    print(f"     Cancellation Rate            {cancel_rate:>13.1f}%")
    print(f"     On-Time Delivery Rate        {on_time_rate:>13.1f}%")
    print(f"     Avg Delivery Days            {avg_delivery_days:>13.1f} days")

    print("\n  ⭐ SATISFACTION")
    print(f"     Avg Review Score             {avg_review:>13.2f} / 5")
    print(f"     5-Star Reviews               {pct_5star:>13.1f}%")
    print(f"     1-Star Reviews               {pct_1star:>13.1f}%")
    print(f"     NPS Proxy Score              {nps_proxy:>13.1f}")

    print("\n" + "="*55)

    # ── SAVE TO CSV ────────────────────────────────────
    kpis = {
        "KPI": [
            "Total Revenue", "Total Orders", "Avg Order Value",
            "Total Customers", "Champions", "At Risk Customers",
            "Champion Revenue Share",
            "Cancellation Rate", "On-Time Delivery Rate",
            "Avg Delivery Days", "Avg Review Score",
            "5-Star Rate", "1-Star Rate", "NPS Proxy"
        ],
        "Value": [
            f"R${total_revenue:,.2f}", total_orders, f"R${aov:.2f}",
            total_customers, champions, at_risk,
            f"{champion_pct_rev:.1f}%",
            f"{cancel_rate:.1f}%", f"{on_time_rate:.1f}%",
            f"{avg_delivery_days:.1f} days", f"{avg_review:.2f}/5",
            f"{pct_5star:.1f}%", f"{pct_1star:.1f}%", f"{nps_proxy:.1f}"
        ]
    }

    pd.DataFrame(kpis).to_csv(f"{PROCESSED_PATH}/kpis.csv", index=False)
    print(f"\n  ✓ KPIs saved → data/processed/kpis.csv\n")


# ── Run it ─────────────────────────────────────────────
if __name__ == "__main__":
    master, orders, rfm = load_data()
    calculate_kpis(master, orders, rfm)
    print("  Script 05_kpis.py complete!\n")
