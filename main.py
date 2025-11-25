import pandas as pd
import matplotlib.pyplot as plt
import math

# =====================================================================
# Helper
# =====================================================================
def tb(gb):
    return gb / 1024.0


# =====================================================================
# REALISTIC SNOWFLAKE PRICING
# =====================================================================
def snowflake_cost_realistic(
    database_size_gb,
    warehouse_profiles,
    cloud_services_rate=0.10,
    storage_rate_per_tb=23
):
    storage_cost = tb(database_size_gb) * storage_rate_per_tb

    compute_cost = 0
    for wh in warehouse_profiles:
        credits_per_hour = wh["credits_per_hour"]
        hours_per_month = wh["hours_per_month"]
        cost_per_credit = wh["cost_per_credit"]

        compute_cost += credits_per_hour * hours_per_month * cost_per_credit

    cloud_services = compute_cost * cloud_services_rate

    return {"snowflake_total": storage_cost + compute_cost + cloud_services}


# =====================================================================
# REALISTIC FIVETRAN PRICING (MAR tiers)
# =====================================================================
def fivetran_cost_realistic(rows_changed_per_day, num_connectors=12):
    mar = rows_changed_per_day * 30

    if mar < 5_000_000:
        mar_cost = (mar / 1000) * 1.00
    elif mar < 25_000_000:
        mar_cost = (mar / 1000) * 0.70
    else:
        mar_cost = (mar / 1000) * 0.50

    platform_fee = max(500, num_connectors * 100)
    history = mar_cost * 0.10

    return {"fivetran_total": mar_cost + platform_fee + history}


# =====================================================================
# REALISTIC DATABRICKS (DBU-BASED)
# =====================================================================
def databricks_cost_realistic(query_gb, num_users):
    dbus = (query_gb / 200) * 15
    compute_cost = dbus * 0.30

    user_support = num_users * 3

    return {"databricks_total": compute_cost + user_support}


# =====================================================================
# AIRBYTE ENTERPRISE (realistic)
# =====================================================================
def airbyte_enterprise_cost_realistic(ingestion_gb, rows_changed_per_day):
    base_fee = 1200

    data_volume_cost = ingestion_gb * 0.15
    cdc_cost = rows_changed_per_day * 0.000005

    return {"airbyte_ent_total": base_fee + data_volume_cost + cdc_cost}


# =====================================================================
# BIGQUERY (official per TB scanned)
# =====================================================================
def bigquery_cost_realistic(database_size_gb, query_gb):
    storage = tb(database_size_gb) * 20
    queries = tb(query_gb) * 5
    return {"bigquery_total": storage + queries}


# =====================================================================
# REDSHIFT SERVERLESS + RDS
# =====================================================================
def redshift_cost_realistic(database_size_gb, query_gb, concurrency):
    storage = tb(database_size_gb) * 24

    rpu = (query_gb / 500) * concurrency
    compute_cost = rpu * 0.36

    return {"redshift_total": storage + compute_cost}


def rds_cost_realistic(database_size_gb, num_users):
    instance_cost = 0.40 * 730
    storage = database_size_gb * 0.115
    backups = database_size_gb * 0.095
    support = num_users * 0.40
    return {"rds_total": instance_cost + storage + backups + support}


# =====================================================================
# SQL SERVER REALISTIC PRICING
# =====================================================================
def sql_server_cost_realistic(database_size_gb, num_users):
    sql_cores = 50 * 20
    windows_lic = 25 * 6
    storage = database_size_gb * 0.12
    backups = database_size_gb * 0.095
    support = num_users * 2
    return {"sql_total": sql_cores + windows_lic + storage + backups + support}


# =====================================================================
# FABRIC (CAPACITY)
# =====================================================================
def fabric_cost_realistic(database_size_gb, num_users):
    capacity = 720
    storage = database_size_gb * 0.02
    users = num_users * 2
    return {"fabric_total": capacity + storage + users}


# =====================================================================
# BI PRICING
# =====================================================================
def tableau_cost(num_users):
    creators = int(num_users * 0.10)
    explorers = int(num_users * 0.40)
    viewers = num_users - creators - explorers
    return {
        "tableau_total": creators * 70 + explorers * 42 + viewers * 15
    }


def powerbi_cost(num_users):
    cap = 8000
    return {"powerbi_total": cap + num_users * 2}


def quicksight_cost(num_users):
    authors = int(num_users * 0.07)
    readers = num_users - authors
    return {"quicksight_total": authors * 24 + readers * 5}


# =====================================================================
# STACK CONFIGS
# =====================================================================
STACK_CONFIGS = {
    "Snowflake_Fivetran_Tableau": [
        "snowflake_total", "fivetran_total", "tableau_total"
    ],
    "SQLServer_Fabric_PowerBI": [
        "sql_total", "fabric_total", "powerbi_total"
    ],
    "Databricks_Airbyte_Tableau": [
        "databricks_total", "airbyte_ent_total", "tableau_total"
    ],
    "BigQuery_Airbyte_Tableau": [
        "bigquery_total", "airbyte_ent_total", "tableau_total"
    ],
    "AWS_RDS_Redshift_QuickSight": [
        "rds_total", "redshift_total", "quicksight_total"
    ]
}


# =====================================================================
# CHART
# =====================================================================
def save_plot(df, path="realistic_compare.png"):
    plt.figure(figsize=(16, 9))
    for stack in STACK_CONFIGS.keys():
        plt.plot(df["month"], df[stack], label=stack, marker="o")
    plt.xlabel("Month")
    plt.ylabel("Monthly Cost ($)")
    plt.title("Realistic 60-Month Cost Projection Across Data Stacks")
    plt.grid(True)
    plt.legend()
    plt.tight_layout()
    plt.savefig(path, dpi=300)
    plt.close()
    print("Saved plot:", path)


# =====================================================================
# SIMULATION
# =====================================================================
def simulate(
    months=60,
    database_size_gb=5000,
    query_gb=12000,
    ingestion_gb=1200,
    rows_changed_per_day=500_000,
    num_users=500,
    concurrency=8,
    growth_rate=1.035,
    csv_path="realistic_full_output.csv"
):

    snowflake_warehouses = [
        {"credits_per_hour": 4, "hours_per_month": 150, "cost_per_credit": 3},
        {"credits_per_hour": 2, "hours_per_month": 180, "cost_per_credit": 3},
        {"credits_per_hour": 8, "hours_per_month": 60, "cost_per_credit": 3},
    ]

    rows = []

    for month in range(1, months + 1):
        costs = {}

        costs.update(
            snowflake_cost_realistic(database_size_gb, snowflake_warehouses)
        )
        costs.update(
            fivetran_cost_realistic(rows_changed_per_day)
        )
        costs.update(
            databricks_cost_realistic(query_gb, num_users)
        )
        costs.update(
            airbyte_enterprise_cost_realistic(ingestion_gb, rows_changed_per_day)
        )
        costs.update(
            bigquery_cost_realistic(database_size_gb, query_gb)
        )
        costs.update(
            redshift_cost_realistic(database_size_gb, query_gb, concurrency)
        )
        costs.update(
            rds_cost_realistic(database_size_gb, num_users)
        )
        costs.update(
            sql_server_cost_realistic(database_size_gb, num_users)
        )
        costs.update(
            fabric_cost_realistic(database_size_gb, num_users)
        )
        costs.update(
            tableau_cost(num_users)
        )
        costs.update(
            powerbi_cost(num_users)
        )
        costs.update(
            quicksight_cost(num_users)
        )

        row = {"month": month}
        for stack_name, keys in STACK_CONFIGS.items():
            row[stack_name] = sum(costs[k] for k in keys)

        rows.append(row)

        database_size_gb *= growth_rate
        query_gb *= growth_rate
        ingestion_gb *= growth_rate
        rows_changed_per_day = int(rows_changed_per_day * growth_rate)
        num_users = math.ceil(num_users * 1.01)

    df = pd.DataFrame(rows)
    df.to_csv(csv_path, index=False)
    print("Saved CSV:", csv_path)
    save_plot(df)
    return df


# =====================================================================
# MAIN
# =====================================================================
if __name__ == "__main__":
    df = simulate()
    print(df.head())
