import pandas as pd
import sqlalchemy as sa
from datetime import datetime

# NeonDB connection URL
DB_URL = "postgresql://neondb_owner:npg_QXgCAz3mUOM9@ep-sweet-union-adde35pm-pooler.c-2.us-east-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require"

engine = sa.create_engine(DB_URL)

# ---------- NORMALIZED DATASET ----------

def full_load_normalized():
    # absolute path, no extra spaces
    path = "/Users/rajasurya/Desktop/sst-data-migration/data/public/normalized/Global Online Orders/orders_norm.csv"
    print("Loading normalized CSV:", path)

    df = pd.read_csv(path)

    # Map your columns -> target schema
    df_norm = df.rename(columns={
        "OrderID": "order_id",
        "CustomerID": "customer_name",   # using ID as name placeholder
        "OrderDate": "order_date",
    })

    # Add missing columns required by table
    df_norm["email"] = None
    df_norm["country"] = None
    df_norm["product_name"] = None
    df_norm["category"] = None
    df_norm["quantity"] = None
    df_norm["total_amount"] = None

    df_norm.to_sql(
        "orders_norm",
        engine,
        schema="public_norm",
        if_exists="replace",
        index=False
    )

    print("Normalized load complete. Rows:", len(df_norm))


# ---------- MESSY DATASET ----------

def full_load_messy():
    start = datetime.utcnow()

    path = "/Users/rajasurya/Desktop/sst-data-migration/data/public/messy/Online-eCommerce.csv"
    print("Loading messy CSV:", path)

    df = pd.read_csv(path)

    # Raw load into staging
    df.to_sql(
        "stg_online_orders_raw",
        engine,
        schema="public_messy",
        if_exists="replace",
        index=False
    )

    # Clean + split into dims + fact
    df["order_date"] = pd.to_datetime(df["Order_Date"], errors="coerce")
    df = df.dropna(subset=["order_date", "Customer_Name", "Product"])

    # Build customers and products
    customers = df[["Customer_Name", "State_Code"]].drop_duplicates()
    customers = customers.rename(columns={
        "Customer_Name": "customer_name",
        "State_Code": "country"          # treat state code as country/region
    })
    customers["email"] = None           # not present in this dataset

    products = df[["Product", "Category", "Cost"]].drop_duplicates()
    products = products.rename(columns={
        "Product": "product_name",
        "Category": "category",
        "Cost": "unit_price"
    })

    with engine.begin() as conn:
        customers.to_sql(
            "dim_customer",
            conn,
            schema="public_messy",
            if_exists="append",
            index=False
        )
        products.to_sql(
            "dim_product",
            conn,
            schema="public_messy",
            if_exists="append",
            index=False
        )

        dim_c = pd.read_sql(
            "SELECT customer_key, customer_name FROM public_messy.dim_customer",
            conn
        )
        dim_p = pd.read_sql(
            "SELECT product_key, product_name, category FROM public_messy.dim_product",
            conn
        )

    # Join fact to dimensions
    df_fact = df.merge(
        dim_c,
        left_on="Customer_Name",
        right_on="customer_name",
        how="left"
    ).merge(
        dim_p,
        left_on=["Product", "Category"],
        right_on=["product_name", "category"],
        how="left"
    )

    fact = df_fact[[
        "Order_Number",
        "order_date",
        "customer_key",
        "product_key",
        "Quantity",
        "Total_Sales"
    ]]
    fact.columns = [
        "order_id",
        "order_date",
        "customer_key",
        "product_key",
        "quantity",
        "total_amount"
    ]

    with engine.begin() as conn:
        fact.to_sql(
            "fact_order",
            conn,
            schema="public_messy",
            if_exists="append",
            index=False
        )
        end = datetime.utcnow()
        conn.execute(sa.text("""
          INSERT INTO public_messy.etl_runs_public
          (dataset_name, run_type, started_at, ended_at, rows_loaded, status)
          VALUES ('messy', 'full', :s, :e, :rows, 'success')
        """), {"s": start, "e": end, "rows": len(fact)})

    print("Messy load complete. Rows:", len(fact))


if __name__ == "__main__":
    full_load_normalized()
    full_load_messy()
