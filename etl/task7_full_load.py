import pandas as pd
import sqlalchemy as sa
from datetime import datetime

# NeonDB connection
DB_URL = (
    "postgresql://neondb_owner:npg_QXgCAz3mUOM9"
    "@ep-sweet-union-adde35pm-pooler.c-2.us-east-1.aws.neon.tech"
    "/neondb?sslmode=require&channel_binding=require"
)

engine = sa.create_engine(DB_URL)


# ========== NORMALIZED DATASET (orders_norm.csv) ==========

def full_load_normalized():
    # Path exactly as in your repo
    path = "data/public/normalized/Global Online Orders/orders_norm.csv"
    print("Loading normalized CSV:", path)

    # Headers: OrderID,CustomerID,EmployeeID,OrderDate,ShipperID
    df = pd.read_csv(path)

    df_norm = df.rename(columns={
        "OrderID": "order_id",
        "CustomerID": "customer_name",   # using ID as placeholder for name
        "OrderDate": "order_date",
    })

    # Add missing columns required by public_norm.orders_norm
    df_norm["email"] = None
    df_norm["country"] = None
    df_norm["product_name"] = None
    df_norm["category"] = None
    df_norm["quantity"] = None
    df_norm["total_amount"] = None

    df_norm = df_norm[
        [
            "order_id",
            "customer_name",
            "email",
            "country",
            "product_name",
            "category",
            "order_date",
            "quantity",
            "total_amount",
        ]
    ]

    df_norm.to_sql(
        "orders_norm",
        engine,
        schema="public_norm",
        if_exists="replace",
        index=False,
    )

    print("Normalized load complete. Rows:", len(df_norm))


# ========== MESSY DATASET (Online-eCommerce.csv) ==========

def full_load_messy():
    start = datetime.utcnow()

    path = "data/public/messy/Online-eCommerce.csv"
    print("Loading messy CSV:", path)

    # Headers:
    # Order_Number,State_Code,Customer_Name,Order_Date,Status,Product,Category,
    # Brand,Cost,Sales,Quantity,Total_Cost,Total_Sales,Assigned Supervisor
    df = pd.read_csv(path)

    # Raw load into staging
    df.to_sql(
        "stg_online_orders_raw",
        engine,
        schema="public_messy",
        if_exists="replace",
        index=False,
    )

    # Clean + basic validation
    df["order_date"] = pd.to_datetime(df["Order_Date"], errors="coerce")
    df = df.dropna(subset=["order_date", "Customer_Name", "Product"])

    # ----- dimensions -----

    # dim_customer
    customers = df[["Customer_Name", "State_Code"]].drop_duplicates()
    customers = customers.rename(columns={
        "Customer_Name": "customer_name",
        "State_Code": "country",
    })
    customers["email"] = None

    # dim_product
    products = df[["Product", "Category", "Cost"]].drop_duplicates()
    products = products.rename(columns={
        "Product": "product_name",
        "Category": "category",
        "Cost": "unit_price",
    })

    with engine.begin() as conn:
        # customers: just append, no unique constraint on (name,country)
        customers.to_sql(
            "dim_customer",
            conn,
            schema="public_messy",
            if_exists="append",
            index=False,
        )

        # products: load via temp table then ON CONFLICT DO NOTHING
        products.to_sql(
            "dim_product_tmp",
            conn,
            schema="public_messy",
            if_exists="replace",
            index=False,
        )

        conn.execute(sa.text("""
            INSERT INTO public_messy.dim_product (product_name, category, unit_price)
            SELECT p.product_name, p.category, p.unit_price
            FROM public_messy.dim_product_tmp p
            ON CONFLICT (product_name, category) DO NOTHING
        """))

        conn.execute(sa.text("DROP TABLE public_messy.dim_product_tmp"))

        # reload dimensions after upsert
        dim_c = pd.read_sql(
            "SELECT customer_key, customer_name FROM public_messy.dim_customer",
            conn,
        )
        dim_p = pd.read_sql(
            "SELECT product_key, product_name, category FROM public_messy.dim_product",
            conn,
        )

    # ----- fact table -----

    df_fact = df.merge(
        dim_c,
        left_on="Customer_Name",
        right_on="customer_name",
        how="left",
    ).merge(
        dim_p,
        left_on=["Product", "Category"],
        right_on=["product_name", "category"],
        how="left",
    )

    fact = df_fact[
        [
            "Order_Number",   # -> order_id
            "order_date",
            "customer_key",
            "product_key",
            "Quantity",
            "Total_Sales",
        ]
    ]
    fact.columns = [
        "order_id",
        "order_date",
        "customer_key",
        "product_key",
        "quantity",
        "total_amount",
    ]

    with engine.begin() as conn:
        fact.to_sql(
            "fact_order",
            conn,
            schema="public_messy",
            if_exists="append",
            index=False,
        )
        end = datetime.utcnow()
        conn.execute(
            sa.text(
                """
                INSERT INTO public_messy.etl_runs_public
                (dataset_name, run_type, started_at, ended_at, rows_loaded, status)
                VALUES ('messy', 'full', :s, :e, :rows, 'success')
                """
            ),
            {"s": start, "e": end, "rows": len(fact)},
        )

    print("Messy load complete. Rows:", len(fact))


if __name__ == "__main__":
    full_load_normalized()
    full_load_messy()
