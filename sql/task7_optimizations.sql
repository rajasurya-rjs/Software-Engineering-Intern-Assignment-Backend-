-- Indexes on new tables
CREATE INDEX IF NOT EXISTS idx_orders_norm_order_date
ON public_norm.orders_norm(order_date);

CREATE INDEX IF NOT EXISTS idx_fact_order_order_date
ON public_messy.fact_order(order_date);

-- Star-schema style view
CREATE OR REPLACE VIEW public_messy.v_orders_with_dims AS
SELECT
  f.order_id,
  f.order_date,
  c.customer_name,
  c.country,
  p.product_name,
  p.category,
  f.quantity,
  f.total_amount
FROM public_messy.fact_order f
JOIN public_messy.dim_customer c ON f.customer_key = c.customer_key
JOIN public_messy.dim_product  p ON f.product_key  = p.product_key;

-- Materialized view for daily revenue
CREATE MATERIALIZED VIEW IF NOT EXISTS public_messy.mv_daily_revenue AS
SELECT
  order_date::date AS day,
  SUM(total_amount) AS revenue,
  COUNT(*) AS orders_count
FROM public_messy.fact_order
GROUP BY day;

CREATE INDEX IF NOT EXISTS idx_mv_daily_revenue_day
ON public_messy.mv_daily_revenue(day);

-- Stored procedure to refresh MV
CREATE OR REPLACE FUNCTION public_messy.sp_refresh_mv_daily_revenue()
RETURNS void AS $$
BEGIN
  REFRESH MATERIALIZED VIEW CONCURRENTLY public_messy.mv_daily_revenue;
END;
$$ LANGUAGE plpgsql;
