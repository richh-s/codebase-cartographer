# Phase 0: Business Reconnaissance Report (Manual Audit)
**Target**: `jaffle-shop-classic`
**Auditor**: FDE Lead

This report establishes the "Ground Truth" for the `jaffle-shop-classic` repository through manual exploration, addressing the five FDE Day-One questions with precise evidence.

## 1. Primary Data Ingestion Path
**Evidence**: `seeds/raw_customers.csv`, `seeds/raw_orders.csv`, `seeds/raw_payments.csv`
The raw ingress consists of three CSV files in the `seeds/` directory. These are materialized as tables in the warehouse by the `dbt seed` command. The logical ingestion flow begins in the staging models:
- `models/staging/stg_customers.sql` reads directly from `raw_customers`.
- `models/staging/stg_orders.sql` reads from `raw_orders`.
- `models/staging/stg_payments.sql` reads from `raw_payments`.

## 2. Critical Output Datasets
**Evidence**: `models/customers.sql`, `models/orders.sql`
The system terminates in two primary business entities:
- **`customers` (Sink)**: Consolidates `stg_customers`, `stg_orders`, and `stg_payments` to calculate lifetime value.
- **`orders` (Sink)**: The core fact table joining `stg_orders` and `stg_payments` to define order status (e.g., 'placed', 'shipped', 'returned').

## 3. Blast Radius Analysis
**Critical Module**: `models/staging/stg_orders.sql`
**Evidence**: References in `models/customers.sql` (L12) and `models/orders.sql` (L4).
Because `stg_orders` is the source of truth for order status across all downstream models, a mutation in its logic (e.g., changing the filter on `status`) would invalidate both terminal business reports, resulting in a **100% blast radius** for the analytics layer.

## 4. Concentration of Business Logic
**Concentration**: `models/customers.sql` (CTE `customer_orders` and `final` [L45-80])
**Evidence**: Complex aggregation logic involving `min(order_date)`, `max(order_date)`, and `count(order_id)` joined with payment amounts. This is where the business defines "What is a Customer's Value?" rather than just moving data.

## 5. Recent Change Velocity
**High-Velocity Area**: `models/staging/`
**Evidence**: Git logs show frequent updates to `stg_payments.sql` and `stg_customers.sql` as the underlying seed schemas evolved or status definitions were refined in early March 2026.

## 🚀 Difficulty Analysis (Manual vs Automation)
The most significant structural obstacle encountered was **cross-language lineage crossing**. For example, tracing a field from the `raw_payments.csv` seed through the SQL staging layer into a hypothetical Python-based `revenue_reconciliation.py` script is nearly impossible to do manually without errors. 

**System Impact**: This pain point directly informed the "Cartographer" architectural priority of unified graph stitching—ensuring that `Hydrologist` (Data Flow) and `Surveyor` (Structural) agents share a common `Knowledge Graph` to provide end-to-end visibility that manual "grep and scroll" analysis cannot achieve.