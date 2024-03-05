import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
import plotly.express as px
from babel.numbers import format_currency

sns.set(style='dark')

# Helper function yang dibutuhkan untuk menyiapkan berbagai dataframe

def create_daily_orders_df(df):
    daily_orders_df = df.resample(rule='D', on='order_date').agg({
        "order_id": "nunique",
        # "total_price": "sum"
    })
    daily_orders_df = daily_orders_df.reset_index()
    daily_orders_df.rename(columns={
        "order_id": "order_count",
        # "total_price": "revenue"
    }, inplace=True)
    
    return daily_orders_df

def create_sum_order_items_df(df):
    sum_order_items_df = df.groupby("product_name").quantity_x.sum().sort_values(ascending=False).reset_index()
    return sum_order_items_df

def create_bygender_df(df):
    bygender_df = df.groupby(by="gender").customer_id.nunique().reset_index()
    bygender_df.rename(columns={
        "customer_id": "customer_count"
    }, inplace=True)
    
    return bygender_df

def create_byage_df(df):
    byage_df = df.groupby(by="age_group").customer_id.nunique().reset_index()
    byage_df.rename(columns={
        "customer_id": "customer_count"
    }, inplace=True)
    byage_df['age_group'] = pd.Categorical(byage_df['age_group'], ["Youth", "Adults", "Seniors"])
    
    return byage_df

def create_bystate_df(df):
    bystate_df = df.groupby(by="state").customer_id.nunique().reset_index()
    bystate_df.rename(columns={
        "customer_id": "customer_count"
    }, inplace=True)
    
    return bystate_df

def create_rfm_df(df):
    rfm_df = df.groupby(by="customer_id", as_index=False).agg({
        "order_date": "max", #mengambil tanggal order terakhir
        "order_id": "nunique",
        "total_price": "sum"
    })
    rfm_df.columns = ["customer_id", "max_order_timestamp", "frequency", "monetary"]
    
    rfm_df["max_order_timestamp"] = rfm_df["max_order_timestamp"].dt.date
    recent_date = df["order_date"].dt.date.max()
    rfm_df["recency"] = rfm_df["max_order_timestamp"].apply(lambda x: (recent_date - x).days)
    rfm_df.drop("max_order_timestamp", axis=1, inplace=True)
    
    return rfm_df

# Load cleaned data
all_df_data = pd.read_csv("/dashboard/main_data.csv")

# Calculate total payments by payment type
total_payments_by_type = all_df_data.groupby('payment_type')['payment_value'].sum().sort_values(ascending=False)

# Streamlit app
st.title('Total Pembayaran Berdasarkan Jenis Pembayaran')

# Create pie chart using plotly
fig = px.pie(total_payments_by_type, values=total_payments_by_type.values, names=total_payments_by_type.index, title='Total Pembayaran Berdasarkan Jenis Pembayaran')
# st.write("Visualisasi:")
st.plotly_chart(fig)

# Calculate the number of sellers by city
seller_count_by_city = all_df_data['seller_city'].value_counts().reset_index()
seller_count_by_city.columns = ['seller_city', 'seller_count']

# Streamlit app
st.title('Jumlah Penjual Berdasarkan Kota Asal')

# Plot the distribution of sellers across cities using a horizontal bar chart
st.write("Visualisasi Distribusi Penjual Berdasarkan Kota Asal:")
st.bar_chart(seller_count_by_city.set_index('seller_city'))

# Convert order_purchase_timestamp to datetime
all_df_data['order_purchase_timestamp'] = pd.to_datetime(all_df_data['order_purchase_timestamp'])

# Extract month from order_purchase_timestamp
all_df_data['order_month'] = all_df_data['order_purchase_timestamp'].dt.month

# Calculate the number of orders for each month
monthly_orders = all_df_data.groupby('order_month').size()

# Find the month with the highest number of orders
highest_month = monthly_orders.idxmax()

# Streamlit app
st.title('Penjualan tertinggi sepanjang tahun 2018')

# Plot the line chart
# st.write("Visualisasi:")
st.line_chart(monthly_orders)
st.write('Data diatas merupakan data penjualan tertinggi sepanjang 2018 dalam bulan.')

with st.sidebar:
    # Menambahkan logo perusahaan
    st.image("https://github.com/dicodingacademy/assets/raw/main/logo.png")

# plot number of daily orders (2021)
st.subheader('Menampilkan data review dengan tanggal yang sama')

# Sidebar filter for selecting year and station
selected_year = st.sidebar.selectbox(
    'Select Date', sorted(all_df_data['review_creation_date'].unique()))

# Filter data based on user selection
filtered_data = all_df_data[(all_df_data['review_creation_date'] == selected_year)]

# Display the filtered data
st.write(f"Data untuk Tahun {selected_year} ")
st.write(filtered_data)
