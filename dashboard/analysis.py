import pandas as pd
from pathlib import Path


DATA_DIR = Path(__file__).resolve().parent.parent / "data"


print("\n--- Preparando dados para uso no dashboard")

orders = pd.read_csv(
    DATA_DIR / "orders.csv",
    usecols=[
        "id",
        "channel",
        "customer_id",
        "status",
        "subtotal",
        "discount_amount",
        "total",
        "placed_at",
    ],
)

print(f"Orders: {len(orders):,} registros")


order_items = pd.read_csv(
    DATA_DIR / "order_items.csv",
    usecols=[
        "order_id",
        "product_variant_id",
        "quantity",
        "unit_price",
        "line_total",
    ],
)

print(f"Order items: {len(order_items):,} registros")


products = pd.read_csv(
    DATA_DIR / "products.csv",
    usecols=[
        "id",
        "name",
        "brand_id",
        "category_id",
        "is_active",
    ],
)

print(f"Products: {len(products):,} registros")


variants = pd.read_csv(
    DATA_DIR / "product_variants.csv",
    usecols=[
        "id",
        "product_id",
        "sku",
        "sale_price",
        "cost_price",
        "is_active",
    ],
)

print(f"Product variants: {len(variants):,} registros")


categories = pd.read_csv(
    DATA_DIR / "categories.csv",
    usecols=[
        "id",
        "name",
    ],
)

print(f"Categories: {len(categories):,} registros")


returns = pd.read_csv(
    DATA_DIR / "returns.csv",
    usecols=[
        "id",
        "order_id",
        "status",
        "reason",
        "total_refund_amount",
    ],
)

print(f"Returns: {len(returns):,} registros")


return_items = pd.read_csv(
    DATA_DIR / "return_items.csv",
    usecols=[
        "return_id",
        "order_item_id",
        "quantity",
        "action",
        "unit_refund_amount",
    ],
)

print(f"Return items: {len(return_items):,} registros")



# PREPARACAO DOS PEDIDOS POR STATUS --------------------------
orders["placed_at"] = pd.to_datetime(
    orders["placed_at"],
    errors="coerce"
)

valid_status = ["paid", "completed"]

sales_orders = orders[
    orders["status"].isin(valid_status)
].copy()



# PERIODO DOS DADOS ------------------------------------------
print("\n--- PERÍODO DOS DADOS")


print(
    f"Primeira venda: {sales_orders['placed_at'].min()}"
)

print(
    f"Última venda:   {sales_orders['placed_at'].max()}"
)



print("\n--- VISÃO GERAL DAS VENDAS")


total_revenue = sales_orders["total"].sum()
total_orders = sales_orders["id"].nunique()
total_customers = sales_orders["customer_id"].nunique()
average_ticket = total_revenue / total_orders

total_discount = sales_orders["discount_amount"].sum()


print(f"Receita total:       R$ {total_revenue:,.2f}")
print(f"Pedidos:             {total_orders:,}")
print(f"Clientes únicos:     {total_customers:,}")
print(f"Ticket médio:        R$ {average_ticket:,.2f}")
print(f"Descontos concedidos:R$ {total_discount:,.2f}")



print("\n--- VENDAS POR MÊS")


sales_orders["month"] = (
    sales_orders["placed_at"]
    .dt.to_period("M")
    .astype(str)
)

monthly_sales = (
    sales_orders
    .groupby("month")
    .agg(
        revenue=("total", "sum"),
        orders=("id", "nunique"),
        customers=("customer_id", "nunique"),
    )
    .reset_index()
)

monthly_sales["average_ticket"] = (
    monthly_sales["revenue"]
    / monthly_sales["orders"]
)

print(
    monthly_sales
    .sort_values("revenue", ascending=False)
    .head(12)
    .to_string(index=False)
)


# PREP PRODUTOS PARA ANALISE ---------------------------------
product_data = (
    order_items
    .merge(
        variants,
        left_on="product_variant_id",
        right_on="id",
        how="left",
        suffixes=("", "_variant"),
    )
    .merge(
        products,
        left_on="product_id",
        right_on="id",
        how="left",
        suffixes=("", "_product"),
    )
    .merge(
        categories,
        left_on="category_id",
        right_on="id",
        how="left",
        suffixes=("", "_category"),
    )
)


# ANALISES PRODUTO -------------------------------------------
print("\n--- TOP 10 PRODUTOS POR RECEITA")


product_sales = (
    product_data
    .groupby(
        ["product_id", "name"],
        dropna=False
    )
    .agg(
        units_sold=("quantity", "sum"),
        revenue=("line_total", "sum"),
    )
    .reset_index()
    .sort_values(
        "revenue",
        ascending=False
    )
)

print(
    product_sales
    .head(10)
    .to_string(index=False)
)



print("\n--- VENDAS POR CATEGORIA")

category_sales = (
    product_data
    .groupby(
        "name_category",
        dropna=False
    )
    .agg(
        units_sold=("quantity", "sum"),
        revenue=("line_total", "sum"),
    )
    .reset_index()
    .sort_values(
        "revenue",
        ascending=False
    )
)

print(
    category_sales
    .head(15)
    .to_string(index=False)
)



print("\n--- VENDAS POR CANAL")

channel_sales = (
    sales_orders
    .groupby("channel")
    .agg(
        revenue=("total", "sum"),
        orders=("id", "nunique"),
        customers=("customer_id", "nunique"),
    )
    .reset_index()
)

channel_sales["average_ticket"] = (
    channel_sales["revenue"]
    / channel_sales["orders"]
)

print(
    channel_sales
    .sort_values(
        "revenue",
        ascending=False
    )
    .to_string(index=False)
)



print("\n--- PRODUTOS COM MAIOR MARGEM")

product_data["gross_profit"] = (
    product_data["line_total"]
    - (
        product_data["quantity"]
        * product_data["cost_price"]
    )
)

product_data["gross_margin"] = (
    product_data["gross_profit"]
    / product_data["line_total"]
)

margin_analysis = (
    product_data
    .groupby(
        ["product_id", "name"],
        dropna=False
    )
    .agg(
        revenue=("line_total", "sum"),
        gross_profit=("gross_profit", "sum"),
        units_sold=("quantity", "sum"),
    )
    .reset_index()
)

margin_analysis["gross_margin"] = (
    margin_analysis["gross_profit"]
    / margin_analysis["revenue"]
)

print(
    margin_analysis[
        margin_analysis["revenue"] > 0
    ]
    .sort_values(
        "gross_margin",
        ascending=False
    )
    .head(10)
    .to_string(index=False)
)



# ANALISE DEVOLUCOES -----------------------------------------
print("\n--- DEVOLUÇÕES")

completed_returns = returns[
    returns["status"] == "completed"
].copy()

total_returns = len(completed_returns)

total_refunded = (
    completed_returns[
        "total_refund_amount"
    ].sum()
)

returned_units = (
    return_items[
        return_items["action"] == "refund"
    ]["quantity"]
    .sum()
)

print(f"Devoluções concluídas: {total_returns:,}")
print(f"Valor devolvido:       R$ {total_refunded:,.2f}")
print(f"Unidades devolvidas:   {returned_units:,.0f}")


print("\n--- PRINCIPAIS MOTIVOS DE DEVOLUÇÃO")


return_reasons = (
    completed_returns
    .groupby("reason")
    .agg(
        returns=("id", "count"),
        refunded_amount=(
            "total_refund_amount",
            "sum"
        ),
    )
    .reset_index()
    .sort_values(
        "returns",
        ascending=False
    )
)

print(
    return_reasons
    .head(10)
    .to_string(index=False)
)



# CLIENTES ---------------------------------------------------
print("\n--- RECORRÊNCIA DOS CLIENTES")

customer_orders = (
    sales_orders
    .groupby("customer_id")
    .agg(
        orders=("id", "nunique"),
        revenue=("total", "sum"),
    )
    .reset_index()
)

customer_orders["customer_type"] = pd.cut(
    customer_orders["orders"],
    bins=[0, 1, 5, 10, float("inf")],
    labels=[
        "1 compra",
        "2-5 compras",
        "6-10 compras",
        "11+ compras",
    ],
)

customer_frequency = (
    customer_orders
    .groupby("customer_type", observed=True)
    .agg(
        customers=("customer_id", "count"),
        revenue=("revenue", "sum"),
    )
    .reset_index()
)

customer_frequency["revenue_percentage"] = (
    customer_frequency["revenue"]
    / total_revenue
    * 100
)

print(
    customer_frequency
    .to_string(index=False)
)



print("\n--- CONCENTRAÇÃO DA RECEITA")


customer_revenue = (
    sales_orders
    .groupby("customer_id")
    .agg(
        revenue=("total", "sum"),
        orders=("id", "nunique"),
    )
    .reset_index()
    .sort_values(
        "revenue",
        ascending=False
    )
)

for n in [10, 50, 100]:
    revenue_top = customer_revenue.head(n)["revenue"].sum()

    percentage = (
        revenue_top
        / total_revenue
        * 100
    )

    print(
        f"Top {n} clientes: "
        f"R$ {revenue_top:,.2f} "
        f"({percentage:.2f}% da receita)"
    )



# ESTOQUE ----------------------------------------------------
print("\n--- ESTOQUE X VENDAS")


stock_levels = pd.read_csv(
    DATA_DIR / "stock_levels.csv",
    usecols=[
        "product_variant_id",
        "location_id",
        "quantity_on_hand",
        "reorder_point",
    ],
)

print(
    f"Stock levels: {len(stock_levels):,} registros"
)

stock_by_variant = (
    stock_levels
    .groupby("product_variant_id")
    .agg(
        stock=("quantity_on_hand", "sum"),
        reorder_point=("reorder_point", "max"),
    )
    .reset_index()
)

sales_by_variant = (
    order_items
    .groupby("product_variant_id")
    .agg(
        units_sold=("quantity", "sum"),
        revenue=("line_total", "sum"),
    )
    .reset_index()
)

stock_analysis = (
    sales_by_variant
    .merge(
        stock_by_variant,
        on="product_variant_id",
        how="left",
    )
    .merge(
        variants[
            [
                "id",
                "product_id",
                "sku",
            ]
        ],
        left_on="product_variant_id",
        right_on="id",
        how="left",
    )
    .merge(
        products[
            [
                "id",
                "name",
            ]
        ],
        left_on="product_id",
        right_on="id",
        how="left",
        suffixes=("", "_product"),
    )
)


print("\n--- PRODUTOS COM ALTA VENDA E BAIXO ESTOQUE")


stock_analysis["stock"] = (
    stock_analysis["stock"]
    .fillna(0)
)

stock_analysis["reorder_point"] = (
    stock_analysis["reorder_point"]
    .fillna(0)
)

high_demand_low_stock = (
    stock_analysis[
        (stock_analysis["units_sold"] > stock_analysis["units_sold"].median())
        & (
            stock_analysis["stock"]
            <= stock_analysis["reorder_point"]
        )
    ]
    .sort_values(
        "units_sold",
        ascending=False
    )
)

print(
    high_demand_low_stock[
        [
            "product_id",
            "name",
            "units_sold",
            "stock",
            "reorder_point",
            "revenue",
        ]
    ]
    .head(15)
    .to_string(index=False)
)


print("\n--- Analise concluida. Os dados podem ser usados no dashboard")