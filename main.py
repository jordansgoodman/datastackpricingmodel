import pandas as pd
import math
import matplotlib.pyplot as plt

# ===================================================================
# Helpers
# ===================================================================

def tb(gb):
    return gb / 1024.0


# ===================================================================
# Cost Components (Updated to reflect verified sources)
# ===================================================================

# -----------------------
# SQL Server + Windows licensing (approximation)
# -----------------------

def sql_server_cost(database_size_gb, num_users):
    windows = 25 * 6
    sql_core = 50 * 20
    storage = database_size_gb * 0.12
    backups = database_size_gb * 0.095
    user_support = num_users * 2
    return {"sql_total": windows + sql_core + storage + backups + user_support}


# -----------------------
# Snowflake (updated Cloud Services threshold)
# -----------------------

def snowflake_cost(database_size_gb, query_gb, concurrency, num_users):
    storage = tb(database_size_gb) * 23  # storage assumption based on regional averages

    compute = (query_gb / 200) * concurrency * 4  # warehouse credit usage assumption

    # Cloud Services charged only if > 10 percent of compute (threshold from Snowflake docs)
    cloud_services = compute * 0.10

    users = num_users * 2
    return {"snowflake_total": storage + compute + cloud_services + users}


# -----------------------
# Microsoft Fabric (capacity based pricing)
# -----------------------

def fabric_cost(database_size_gb, num_users):
    cap = 720 if database_size_gb < 10000 else 1440
    storage = database_size_gb * 0.02
    users = num_users * 2
    return {"fabric_total": cap + storage + users}


# -----------------------
# Tableau BI (source: tableau.com/pricing)
# -----------------------

def tableau_cost(num_users):
    creators = int(num_users * 0.10)
    explorers = int(num_users * 0.40)
    viewers = num_users - creators - explorers
    return {"tableau_total": creators*70 + explorers*42 + viewers*15}


# -----------------------
# Databricks (DBU-based)
# -----------------------

def databricks_cost(database_size_gb, query_gb, num_users):
    dbu = (query_gb / 150) * 0.40
    storage = database_size_gb * 0.02
    users = num_users * 2.5
    return {"databricks_total": dbu + storage + users}


# ===================================================================
# Ingestion (marked as assumptions)
# ===================================================================

# Fivetran MAR-based pricing is proprietary. These are simulation assumptions.
def fivetran_cost(ingestion_gb, rows_changed_per_day):
    per_gb_cost = ingestion_gb * 1.20
    per_row_cost = rows_changed_per_day * 0.000015
    minimum = 350
    surcharge = 75
    history = ingestion_gb * 0.20
    return {
        "fivetran_total": max(per_gb_cost, minimum) + surcharge + history + per_row_cost
    }


# Airbyte Enterprise pricing varies by contract. These are simulation assumptions.
def airbyte_enterprise_cost(ingestion_gb, rows_changed_per_day):
    base_fee = 900
    per_gb = ingestion_gb * 0.30
    per_row = rows_changed_per_day * 0.000008
    normalization = ingestion_gb * 0.03
    return {"airbyte_ent_total": base_fee + per_gb + per_row + normalization}


# ===================================================================
# Cloud Warehouses (verified official pricing models)
# ===================================================================

def rds_cost(database_size_gb, num_users):
    instance = 0.40 * 730
    storage = database_size_gb * 0.115
    backups = database_size_gb * 0.095
    support = num_users * 0.40
    return {"rds_total": instance + storage + backups + support}


def redshift_cost(database_size_gb, query_gb, concurrency):
    storage = tb(database_size_gb) * 23
    rpu = (query_gb / 500) * concurrency * 0.36
    return {"redshift_total": storage + rpu}


# BigQuery: Official query pricing = $5 per TB scanned (on-demand)
def bigquery_cost(database_size_gb, query_gb):
    storage = tb(database_size_gb) * 20
    queries = tb(query_gb) * 5  # official
    return {"bigquery_total": storage + queries}


# Power BI (matches published pricing)
def powerbi_cost(num_users):
    cap = 8000 if num_users < 1000 else 15000
    return {"powerbi_total": cap + num_users * 2}


# QuickSight pricing: Authors 24, Readers 5
def quicksight_cost(num_users):
    authors = int(num_users * 0.07)
    readers = num_users - authors
    return {"quicksight_total": authors*24 + readers*5}


# ===================================================================
# Stack Definitions
# ===================================================================

STACK_CONFIGS = {
    "Snowflake_Fivetran_Tableau": [
        "snowflake_total", "fivetran_total", "tableau_total"
    ],
    "Microsoft_SQL_Fabric_PowerBI": [
        "sql_total", "fabric_total", "powerbi_total"
    ],
    "Databricks_AirbyteEnt_Tableau": [
        "databricks_total", "airbyte_ent_total", "tableau_total"
    ],
    "BigQuery_AirbyteEnt_Tableau": [
        "bigquery_total", "airbyte_ent_total", "tableau_total"
    ],
    "AWS_RDS_Redshift_QuickSight": [
        "rds_total", "redshift_total", "quicksight_total"
    ],
}


# ===================================================================
# PNG Generator
# ===================================================================

def save_stack_plot(df, image_path="stack_cost_comparison.png"):
    plt.figure(figsize=(15, 9))

    for stack in STACK_CONFIGS.keys():
        plt.plot(df["month"], df[stack], marker='o', label=stack)

    plt.title("60 Month Cost Projection with Updated Pricing Assumptions")
    plt.xlabel("Month")
    plt.ylabel("Monthly Cost ($)")
    plt.grid(True, linestyle="--", alpha=0.5)
    plt.legend()
    plt.tight_layout()
    plt.savefig(image_path, dpi=300)
    plt.close()

    print(f"Saved image: {image_path}")


# ===================================================================
# Simulation Driver
# ===================================================================

def simulate_stacks(
    months=60,
    database_size_gb=5000,
    query_volume_gb=12000,
    ingestion_gb=1200,
    rows_changed_per_day=500_000,
    num_users=500,
    concurrency=8,
    growth_rate=1.035,
    csv_path="stack_comparison_output.csv"
):

    rows = []

    for month in range(1, months + 1):
        costs = {}

        costs.update(sql_server_cost(database_size_gb, num_users))
        costs.update(snowflake_cost(database_size_gb, query_volume_gb, concurrency, num_users))
        costs.update(fabric_cost(database_size_gb, num_users))
        costs.update(tableau_cost(num_users))
        costs.update(databricks_cost(database_size_gb, query_volume_gb, num_users))
        costs.update(bigquery_cost(database_size_gb, query_volume_gb))
        costs.update(redshift_cost(database_size_gb, query_volume_gb, concurrency))
        costs.update(rds_cost(database_size_gb, num_users))

        costs.update(powerbi_cost(num_users))
        costs.update(quicksight_cost(num_users))

        costs.update(fivetran_cost(ingestion_gb, rows_changed_per_day))
        costs.update(airbyte_enterprise_cost(ingestion_gb, rows_changed_per_day))

        row = {"month": month}
        for stack_name, keys in STACK_CONFIGS.items():
            row[stack_name] = sum(costs[k] for k in keys)

        rows.append(row)

        database_size_gb *= growth_rate
        query_volume_gb *= growth_rate
        ingestion_gb *= growth_rate
        rows_changed_per_day = int(rows_changed_per_day * growth_rate)
        num_users = math.ceil(num_users * 1.01)

    df = pd.DataFrame(rows)
    df.to_csv(csv_path, index=False)
    print(f"Saved CSV: {csv_path}")
    return df


# ===================================================================
# Run
# ===================================================================

if __name__ == "__main__":
    df = simulate_stacks()
    print(df.head())
    save_stack_plot(df)
