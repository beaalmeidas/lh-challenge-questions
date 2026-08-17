import streamlit as st
import pandas as pd
from pathlib import Path
import plotly.express as px


# CONFIG -----------------------------------------------------
st.set_page_config(
    page_title="LH Nauticals",
    page_icon="⚓",
    layout="wide",
)

DATA_DIR = Path(__file__).resolve().parent.parent / "data"


# CARREGAMENTO DE DADOS ---------------------------------------
@st.cache_data
def load_data():

    orders = pd.read_csv(
        DATA_DIR / "orders.csv",
        usecols=[
            "id",
            "channel",
            "customer_id",
            "status",
            "discount_amount",
            "total",
            "placed_at",
        ],
    )

    order_items = pd.read_csv(
        DATA_DIR / "order_items.csv",
        usecols=[
            "id",
            "order_id",
            "product_variant_id",
            "quantity",
            "unit_price",
            "line_total",
        ],
    )

    products = pd.read_csv(
        DATA_DIR / "products.csv",
        usecols=[
            "id",
            "name",
            "category_id",
        ],
    )

    variants = pd.read_csv(
        DATA_DIR / "product_variants.csv",
        usecols=[
            "id",
            "product_id",
            "cost_price",
        ],
    )

    categories = pd.read_csv(
        DATA_DIR / "categories.csv",
        usecols=[
            "id",
            "name",
        ],
    )

    returns = pd.read_csv(
        DATA_DIR / "returns.csv",
        usecols=[
            "id",
            "status",
            "reason",
            "total_refund_amount",
        ],
    )

    stock = pd.read_csv(
        DATA_DIR / "stock_levels.csv",
        usecols=[
            "product_variant_id",
            "quantity_on_hand",
            "reorder_point",
        ],
    )

    orders["placed_at"] = pd.to_datetime(
        orders["placed_at"],
        errors="coerce",
    )

    return (
        orders,
        order_items,
        products,
        variants,
        categories,
        returns,
        stock,
    )


(
    orders,
    order_items,
    products,
    variants,
    categories,
    returns,
    stock,
) = load_data()


# FILTROS ----------------------------------------------------
st.sidebar.title("Filtros")

min_date = orders["placed_at"].min().date()
max_date = orders["placed_at"].max().date()

date_range = st.sidebar.date_input(
    "Período",
    value=(min_date, max_date),
    min_value=min_date,
    max_value=max_date,
)

channels = sorted(
    orders["channel"].dropna().unique()
)

selected_channels = st.sidebar.multiselect(
    "Canal de vendas",
    channels,
    default=channels,
)


if len(date_range) == 2:

    start_date = pd.Timestamp(date_range[0])
    end_date = (
        pd.Timestamp(date_range[1])
        + pd.Timedelta(days=1)
    )

    filtered_orders = orders[
        (orders["placed_at"] >= start_date)
        & (orders["placed_at"] < end_date)
        & (
            orders["channel"].isin(
                selected_channels
            )
        )
    ].copy()

else:
    filtered_orders = orders.copy()


# HEADER -----------------------------------------------------
st.title("LH Nauticals")

st.markdown(
    """
### Visão geral do negócio no período
"""
)


# PRINCIPAIS INDICADORES -------------------------------------
total_revenue = filtered_orders["total"].sum()

total_orders = filtered_orders["id"].nunique()

total_customers = filtered_orders["customer_id"].nunique()

average_ticket = (
    total_revenue / total_orders
    if total_orders > 0
    else 0
)

total_discount = filtered_orders["discount_amount"].sum()


col1, col2, col3 = st.columns(3)

col1.metric(
    "Receita total",
    f"R$ {total_revenue:,.2f}",
)

col2.metric(
    "Pedidos",
    f"{total_orders:,}",
)

col3.metric(
    "Clientes",
    f"{total_customers:,}",
)


col1, col2 = st.columns(2)

col1.metric(
    "Ticket médio",
    f"R$ {average_ticket:,.2f}",
)

col2.metric(
    "Descontos",
    f"R$ {total_discount:,.2f}",
)


st.divider()


# VENDAS MES A MES--------------------------------------------
filtered_orders["month"] = (
    filtered_orders["placed_at"]
    .dt.to_period("M")
    .astype(str)
)

monthly_sales = (
    filtered_orders
    .groupby("month")
    .agg(
        revenue=("total", "sum"),
        orders=("id", "nunique"),
    )
    .reset_index()
)

monthly_sales["revenue"] = (
    monthly_sales["revenue"].round(2)
)


st.subheader("Evolução das vendas mês a mês")

st.line_chart(
    monthly_sales.set_index("month")["revenue"]
)


# PREPARO PRODUTOS -------------------------------------------
sales_data = (
    order_items
    .merge(
        filtered_orders[
            [
                "id",
                "placed_at",
                "channel",
            ]
        ],
        left_on="order_id",
        right_on="id",
        how="inner",
        suffixes=("", "_order"),
    )
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


# ANALISE DE PRODUTOS ----------------------------------------
product_sales = (
    sales_data
    .groupby(
        ["product_id", "name"],
        dropna=False,
    )
    .agg(
        units_sold=("quantity", "sum"),
        revenue=("line_total", "sum"),
    )
    .reset_index()
    .sort_values(
        "revenue",
        ascending=False,
    )
)


category_sales = (
    sales_data
    .groupby(
        "name_category",
        dropna=False,
    )
    .agg(
        units_sold=("quantity", "sum"),
        revenue=("line_total", "sum"),
    )
    .reset_index()
    .sort_values(
        "revenue",
        ascending=False,
    )
)


col1, col2 = st.columns(2)


with col1:

    st.subheader("Top 10 produtos")

    top_products = (
        product_sales
        .head(10)
        .sort_values("revenue")
    )

    st.bar_chart(
        top_products.set_index("name")["revenue"]
    )


with col2:

    st.subheader("Receita por categoria")

    top_categories = (
        category_sales
        .head(10)
        .sort_values("revenue")
    )

    st.bar_chart(
        top_categories.set_index(
            "name_category"
        )["revenue"]
    )


# CANAIS DE VENDA --------------------------------------------
st.subheader("Receita por canal de vendas")

channel_sales = (
    filtered_orders
    .groupby("channel")
    .agg(
        revenue=("total", "sum"),
        orders=("id", "nunique"),
    )
    .reset_index()
)

fig = px.pie(
    channel_sales,
    names="channel",
    values="revenue",
    title="Distribuição da receita por canal"
)

st.plotly_chart(fig, use_container_width=True)

st.divider()


# PRODUTOS POR MARGEM BRUTA ESTIMADA -------------------------
sales_data["gross_profit"] = (
    sales_data["line_total"]
    - (
        sales_data["quantity"]
        * sales_data["cost_price"]
    )
)

margin_data = (
    sales_data
    .groupby(
        ["product_id", "name"],
        dropna=False,
    )
    .agg(
        revenue=("line_total", "sum"),
        gross_profit=("gross_profit", "sum"),
        units_sold=("quantity", "sum"),
    )
    .reset_index()
)

margin_data["gross_margin"] = (
    margin_data["gross_profit"]
    / margin_data["revenue"]
)

margin_data = margin_data[
    margin_data["revenue"] > 0
].copy()


st.subheader("Produtos por margem bruta estimada")

top_margin = (
    margin_data
    .sort_values(
        "gross_margin",
        ascending=False,
    )
    .head(10)
)

st.dataframe(
    top_margin[
        [
            "name",
            "units_sold",
            "revenue",
            "gross_profit",
            "gross_margin",
        ]
    ],
    column_config={
        "revenue": st.column_config.NumberColumn(
            "Receita",
            format="R$ %.2f",
        ),
        "gross_profit": st.column_config.NumberColumn(
            "Lucro bruto estimado",
            format="R$ %.2f",
        ),
        "gross_margin": st.column_config.NumberColumn(
            "Margem",
            format="%.1f%%",
        ),
    },
    hide_index=True,
    use_container_width=True,
)


st.divider()


# ANALISE DE CLIENTES ----------------------------------------
st.subheader("Comportamento dos clientes")

customer_data = (
    filtered_orders
    .groupby("customer_id")
    .agg(
        orders=("id", "nunique"),
        revenue=("total", "sum"),
    )
    .reset_index()
)

customer_frequency = (
    customer_data
    .assign(
        frequency=pd.cut(
            customer_data["orders"],
            bins=[
                0,
                1,
                5,
                10,
                float("inf"),
            ],
            labels=[
                "1 compra",
                "2–5 compras",
                "6–10 compras",
                "11+ compras",
            ],
        )
    )
    .groupby(
        "frequency",
        observed=True,
    )
    .agg(
        customers=("customer_id", "count"),
        revenue=("revenue", "sum"),
    )
    .reset_index()
)

col1, col2 = st.columns(2)

with col1:

    st.write("**Frequência de compras**")

    st.bar_chart(
        customer_frequency.set_index(
            "frequency"
        )["customers"]
    )


with col2:

    st.write("**Receita por frequência de compra**")

    st.bar_chart(
        customer_frequency.set_index(
            "frequency"
        )["revenue"]
    )


# ANALISE DE DEVOLUCOES --------------------------------------
st.divider()

st.subheader("Devoluções")

completed_returns = returns[
    returns["status"] == "completed"
]

return_count = len(completed_returns)

refund_total = (
    completed_returns[
        "total_refund_amount"
    ].sum()
)

return_col1, return_col2 = st.columns(2)

return_col1.metric(
    "Devoluções concluídas",
    f"{return_count:,}",
)

return_col2.metric(
    "Valor devolvido",
    f"R$ {refund_total:,.2f}",
)


return_reasons = (
    completed_returns
    .groupby("reason")
    .agg(
        returns=("id", "count"),
        refunded_amount=(
            "total_refund_amount",
            "sum",
        ),
    )
    .reset_index()
    .sort_values(
        "returns",
        ascending=False,
    )
)

st.write("**Principais motivos**")

st.bar_chart(
    return_reasons
    .head(10)
    .set_index("reason")["returns"]
)


# ANALISE DE ESTOQUE------------------------------------------
st.divider()

st.subheader("Estoque")

stock_summary = (
    stock
    .groupby("product_variant_id")
    .agg(
        stock=("quantity_on_hand", "sum"),
        reorder_point=("reorder_point", "max"),
    )
    .reset_index()
)

stock_summary = (
    stock_summary
    .merge(
        variants[
            [
                "id",
                "product_id",
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

stock_summary = (
    stock_summary
    .groupby(
        ["product_id", "name"],
        dropna=False,
    )
    .agg(
        stock=("stock", "sum"),
    )
    .reset_index()
)


stock_summary = (
    stock_summary
    .merge(
        product_sales[
            [
                "product_id",
                "units_sold",
                "revenue",
            ]
        ],
        on="product_id",
        how="left",
    )
    .fillna(
        {
            "units_sold": 0,
            "revenue": 0,
        }
    )
)

stock_summary["stock"] = (
    stock_summary["stock"].clip(lower=0)
)


col1, col2 = st.columns(2)

with col1:

    st.write("**Maior estoque disponível**")

    st.dataframe(
        stock_summary
        .sort_values(
            "stock",
            ascending=False,
        )
        .head(10)[
            [
                "name",
                "stock",
                "units_sold",
                "revenue",
            ]
        ],
        column_config={
            "stock": st.column_config.NumberColumn(
                "Estoque",
                format="%.0f",
            ),
            "units_sold": st.column_config.NumberColumn(
                "Vendidos",
                format="%.0f",
            ),
            "revenue": st.column_config.NumberColumn(
                "Receita",
                format="R$ %.2f",
            ),
        },
        hide_index=True,
        use_container_width=True,
    )


with col2:

    st.write("**Produtos com maior venda**")

    st.dataframe(
        product_sales
        .head(10)[
            [
                "name",
                "units_sold",
                "revenue",
            ]
        ],
        column_config={
            "units_sold": st.column_config.NumberColumn(
                "Unidades",
                format="%.0f",
            ),
            "revenue": st.column_config.NumberColumn(
                "Receita",
                format="R$ %.2f",
            ),
        },
        hide_index=True,
        use_container_width=True,
    )