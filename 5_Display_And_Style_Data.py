import streamlit as st
import pandas as pd
import numpy as np
from datetime import date, timedelta

st.set_page_config(
    page_title="Streamlit: Display & Style Data", page_icon="📊", layout="wide"
)

# ------------------------------------------------------------
# 0) Create a small sample dataset
# ------------------------------------------------------------
rng = np.random.default_rng(42)
products = [
    ("Engine Oil", "AutoCare"),
    ("Air Filter", "AutoCare"),
    ("Spark Plug", "AutoCare"),
    ("Brake Pads", "AutoCare"),
    ("Coolant", "AutoCare"),
    ("Wiper Blade", "AutoCare"),
    ("GPS Tracker", "Electronics"),
    ("Phone Mount", "Electronics"),
    ("Dash Cam", "Electronics"),
    ("Tyre Shine", "CarCare"),
]

rows = []
start = date.today() - timedelta(days=120)
for i, (name, cat) in enumerate(products, start=1):
    units = int(rng.integers(50, 400))
    price = float(rng.integers(150, 3500))  # ₹
    rating = float(rng.choice([3.2, 3.8, 4.0, 4.3, 4.6, 4.8, 5.0]))
    in_stock = bool(rng.choice([True, True, True, False]))
    added_on = start + timedelta(days=int(rng.integers(0, 120)))
    url = f"https://example.com/product/{i}"
    rows.append((i, name, cat, units, price, rating, in_stock, added_on, url))

df = pd.DataFrame(
    rows,
    columns=[
        "id",
        "product",
        "category",
        "units",
        "price",
        "rating",
        "in_stock",
        "added_on",
        "url",
    ],
)
df["revenue"] = df["units"] * df["price"]

st.title("📊 Streamlit: Display & Style Data")
st.caption("Clean tables, readable numbers, and interactive editing — all from Python!")

# ------------------------------------------------------------
# 1) st.dataframe vs st.table
# ------------------------------------------------------------
st.header("1) st.dataframe vs st.table")

c1, c2 = st.columns(2)

with c1:
    st.subheader("st.dataframe (interactive)")
    st.write("• Scrollable, resizable, sortable. Great for exploration.")
    st.dataframe(df.head(8), use_container_width=True)

with c2:
    st.subheader("st.table (static)")
    st.write("• Static HTML snapshot (no scroll/resize). Nice for small summaries.")
    st.table(df.loc[:4, ["product", "category", "units", "price"]])

# ------------------------------------------------------------
# 2) Column formatting with column_config
#    - Works with st.dataframe and st.data_editor
# ------------------------------------------------------------
st.header("2) Column formatting with column_config")

st.write(
    "Below we format numbers as currency, show rating as a progress bar, linkify URLs, "
    "and present dates nicely."
)

st.dataframe(
    df,
    use_container_width=True,
    column_config={
        "id": st.column_config.NumberColumn(
            "ID", help="Internal identifier", format="%d", width="small"
        ),
        "product": st.column_config.TextColumn("Product", width="medium"),
        "category": st.column_config.TextColumn("Category", width="small"),
        "units": st.column_config.NumberColumn(
            "Units", format="localized", help="Pieces sold"
        ),
        "price": st.column_config.NumberColumn(
            "Unit Price", help="Per item", format="accounting"
        ),
        "revenue": st.column_config.NumberColumn(
            "Revenue", help="units × price", format="accounting"
        ),
        "rating": st.column_config.ProgressColumn(
            "Rating",
            help="Out of 5",
            min_value=0.0,
            max_value=5.0,
            width="small",
            format="%d",
        ),
        "in_stock": st.column_config.CheckboxColumn("In Stock", help="Available now?"),
        "added_on": st.column_config.DateColumn("Added On", help="Date added"),
        "url": st.column_config.LinkColumn("Link", display_text="View"),
    },
    hide_index=True,
)

st.divider()

# ------------------------------------------------------------
# 3) KPIs with st.metric
# ------------------------------------------------------------
st.header("3) Quick KPIs with st.metric")
total_rev = df["revenue"].sum()
avg_rating = df["rating"].mean()
in_stock_pct = df["in_stock"].mean() * 100

m1, m2, m3 = st.columns(3)

with m1:
    st.metric("Total Revenue", f"₹ {total_rev:,.2f}")

with m2:
    st.metric("Average Rating", f"{avg_rating:,.2f} / 5")

with m3:
    st.metric("In-Stock %", f"{in_stock_pct:.1f}%")

st.caption(
    "Use `delta` in st.metric for time-based change if you have a previous value to compare."
)

st.divider()

# ------------------------------------------------------------
# 4) Interactive editing with st.data_editor
#    - Great for quick admin tools and what-if analysis
# ------------------------------------------------------------
st.header("4) Interactive editing with st.data_editor")

st.write("Edit the **Units** and **In Stock** flags; Revenue recalculates below.")

editable_cols = ["units", "in_stock"]
edited = st.data_editor(
    df[["id", "product", "units", "price", "in_stock"]],
    use_container_width=True,
    column_config={
        "units": st.column_config.NumberColumn(
            "Units", min_value=0, format="localized"
        ),
        "price": st.column_config.NumberColumn(
            "Unit Price", disabled=True, format="accounting"
        ),
        "in_stock": st.column_config.CheckboxColumn("In Stock"),
    },
    disabled=["id", "product", "price"],  # keep master data read-only
    hide_index=True,
)

# Recompute revenue after edits
merged = df.drop(columns=["units", "in_stock"]).merge(
    edited[["id", "units", "in_stock"]], on="id", how="left"
)
merged["revenue"] = merged["units"] * merged["price"]

st.write("**Recomputed totals after edits**")
st.dataframe(
    merged[["product", "units", "price", "revenue", "in_stock"]],
    use_container_width=True,
    column_config={
        "units": st.column_config.NumberColumn("Units", format="localized"),
        "price": st.column_config.NumberColumn("Unit Price", format="accounting"),
        "revenue": st.column_config.NumberColumn("Revenue", format="accounting"),
        "in_stock": st.column_config.CheckboxColumn("In Stock"),
    },
    hide_index=True,
)

st.divider()

# ------------------------------------------------------------
# 5) Styling with Pandas Styler (color gradients & highlights)
#    - Use this when you want rich formatting inside the table cells
# ------------------------------------------------------------
st.header("5) Styling with Pandas Styler")

# Make a small view to style
view = df[["product", "category", "units", "price", "revenue", "rating"]].copy()


def highlight_top_revenue(s: pd.Series):
    is_max = s == s.max()
    return ["background-color: #ffe599" if v else "" for v in is_max]


styler = (
    view.style.format(
        {
            "units": "{:,}",
            "price": "₹ {:,.2f}",
            "revenue": "₹ {:,.2f}",
            "rating": "{:.1f}",
        }
    )
    .background_gradient(subset=["revenue"], cmap="Greens")
    .apply(highlight_top_revenue, subset=["revenue"])
)

st.write("**Pandas Styler** (supports gradients, per-cell formatting):")
st.dataframe(styler, use_container_width=True)

st.info(
    "Note: Styled DataFrames are static-ish (no sorting). For interactive exploration, use plain `st.dataframe`."
)

st.divider()

# ------------------------------------------------------------
# 6) Column selection and simple pivot with styling
# ------------------------------------------------------------
st.header("6) Column selection & simple pivot")

cols = st.multiselect(
    "Select columns to display",
    list(df.columns),
    default=["product", "category", "units", "price", "revenue"],
)
st.dataframe(df[cols], use_container_width=True, hide_index=True)

st.subheader("Category summary (pivot)")
pivot = df.pivot_table(
    index="category", values=["units", "revenue"], aggfunc="sum"
).sort_values("revenue", ascending=False)
pivot_styled = pivot.style.format(
    {"units": "{:,}", "revenue": "₹ {:,.2f}"}
).background_gradient(cmap="Blues")
st.dataframe(pivot_styled, use_container_width=True)

st.divider()
