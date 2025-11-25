
# Realistic 5-Year Data Stack Cost Simulation

This project models the long-term financial behavior of modern data architectures.
It simulates 60 months (5 years) of cost growth for five realistic analytics stacks using actual vendor pricing structures and enterprise usage patterns.

The goal is to give data leaders a clear picture of how different platforms behave as an organization’s data volume, ingestion, and user base grow over time.

---

## What This Simulator Does

The script forecasts monthly cost for five full end-to-end data stacks:

1. Snowflake + Fivetran + Tableau
2. SQL Server + Microsoft Fabric + Power BI
3. Databricks + Airbyte Enterprise + Tableau
4. BigQuery + Airbyte Enterprise + Tableau
5. AWS RDS + Redshift + QuickSight

Each stack includes:

- Storage
- Compute / Warehouse / DBU / RPU cost
- Ingestion (Fivetran / Airbyte Enterprise)
- Business Intelligence licensing
- Growth inputs that match real enterprise behavior

The output is:

- A CSV file with 60 months of projected cost
- A PNG chart comparing all stack curves
- A pandas DataFrame for downstream analysis

---

## Why This Exists

Most cloud data pricing appears simple on the surface but behaves very differently over long periods.
Consumption-based warehouses scale with:

- growing tables
- increasing scans
- concurrency demand
- metadata work
- ingestion volume
- CDC growth

Capacity-based systems scale much more gently.

This simulator helps you see:

- how each architecture responds to real multi-year growth
- when costs diverge
- which stacks remain stable
- which stacks accelerate with workload intensity
- which pricing models compound over time

This is not vendor-specific advice.
It is a transparent, repeatable model for comparing architectural cost behavior.

---

## Key Inputs

The simulator uses realistic baseline values commonly seen in enterprise analytics environments:

- Initial database size: 5 TB  
- Initial query volume: 12 TB scanned/processed per month  
- Initial ingestion volume: 1.2 TB per month  
- CDC activity: 500,000 row changes per day  
- User count: 500  
- Concurrency: 8  
- Monthly growth rate: 3.5 percent for data & ingestion, 1 percent for users  

Every month, the script updates:

- data size  
- ingestion size  
- number of changed rows  
- query volume  
- user count  

This produces realistic compounding behavior instead of artificial spikes.

---

## Realistic Pricing Models

Each platform is modeled using real-world mechanics:

### Snowflake
- Warehouse credits based on actual warehouse sizes (S/M/L)
- Credits per hour × hours per month
- Storage at typical on-demand regional rates
- Cloud Services at 10 percent of compute (industry median)
- Auto-suspend behavior reflected via limited warehouse hours

### Fivetran
- Monthly Active Row (MAR) tiered pricing
- Platform fees
- Historical sync overhead
- CDC-driven MAR growth

### Databricks
- DBUs derived from workload size
- Cost per DBU
- Per-user platform overhead

### Airbyte Enterprise
- Platform fee
- Usage cost per GB
- CDC cost

### BigQuery
- Per-TB scanned
- Per-TB stored

### Redshift Serverless + RDS
- RPU consumption
- Redshift storage
- RDS instance + IOPS + backup cost

### Fabric + Power BI
- Capacity pricing
- Incremental storage
- User licensing

### Tableau / QuickSight
- Role-based licensing
- Per-user cost

These reflect how enterprises pay in practice rather than oversimplified calculators.

---

## How to Run the Simulation

### 1. Install dependencies
```
pip install pandas matplotlib
```

### 2. Run the script
```
python realistic_data_stack_simulation.py
```

### 3. Outputs
After running:

- realistic_full_output.csv  
- realistic_compare.png  
- First few rows printed to console  

---

## Interpreting the Results

The generated chart shows monthly cost curves for each stack, typically:

- Snowflake + Fivetran + Tableau grows fastest due to compounding compute, ingestion, and BI licensing.
- SQL Server + Fabric + Power BI remains stable due to capacity-based pricing.
- Databricks + Airbyte Enterprise + Tableau grows moderately.
- BigQuery + Airbyte Enterprise + Tableau shows linear growth based on TB scanned.
- RDS + Redshift + QuickSight remains lowest due to efficient compute and low BI cost.

This reveals the economic personality of each architecture.

---

## Customization

The simulation can be extended to support:

- Cumulative 5-year spend  
- Discount modeling  
- Reserved capacity  
- Licensing variations  
- Data minimization strategies  
- Auto-suspend tuning  
- Additional ingestion vendors  

---

## Disclaimer

This simulation is based on publicly documented pricing and common enterprise patterns.  
Actual costs vary by region, enterprise contract, reserved capacity, and negotiated discounts.  
This model is for directional analysis, not contract-level estimation.

---

## Purpose

This repository helps data leaders:

- understand long-term cost trajectories  
- compare realistic architectural patterns  
- quantify differences between platforms  
- communicate tradeoffs to executives  
- plan multi-year data strategies  

It makes the cost side of data architecture visible.
