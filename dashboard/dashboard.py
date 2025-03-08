import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

st.set_page_config(
    page_title="Bike Rental Dashboard ",
    page_icon="🚲",
    layout="centered"
)


def create_monthyear_progress_df(df_day):
    # Group by month and year to calculate total rentals
    monthyear_progress_df = df_day.groupby(['month', 'year'], observed=False).agg({
        'total_count': 'sum'
    }).reset_index()
    
    # Create 'month/year' column
    monthyear_progress_df['month/year'] = monthyear_progress_df['month'].astype(str) + '/' + monthyear_progress_df['year'].astype(str)

    # Sort by year first, then by month to maintain chronological order
    monthyear_progress_df = monthyear_progress_df.sort_values(by=['year', 'month']).reset_index(drop=True)
    
    return  monthyear_progress_df


# Function to create the monthly orders DataFrame
def create_monthly_orders_df(df_day):
    monthly_orders_df = df_day.groupby("month", observed=False).agg({
        "total_count": "mean"
    }).reset_index()

    # Mapping month numbers to names
    month_map = {
        1: 'January', 2: 'February', 3: 'March', 4: 'April',
        5: 'May', 6: 'June', 7: 'July', 8: 'August',
        9: 'September', 10: 'October', 11: 'November', 12: 'December'
    }
    monthly_orders_df["month"] = monthly_orders_df["month"].map(month_map)

    return monthly_orders_df

# Function to create the daily orders DataFrame
def create_daily_orders_df(df_day):
    daily_orders_df = df_day.groupby('weekday', observed=False).agg({
        'total_count': ['max', 'min', 'sum', 'mean']
    }).reset_index()

    # Mapping weekdays to names
    weekday_map = {
        0: 'Sunday', 1: 'Monday', 2: 'Tuesday', 3: 'Wednesday',
        4: 'Thursday', 5: 'Friday', 6: 'Saturday'
    }
    daily_orders_df['weekday'] = daily_orders_df['weekday'].map(weekday_map)

    return daily_orders_df

# Function to create season orders DataFrame
def create_season_orders_df(df_day):
    season_orders_df = df_day.groupby('season', observed=False).agg({
        'total_count': ['max', 'min', 'sum', 'mean']
    }).reset_index()

    # Define the correct seasonal order
    season_order = ['spring', 'summer', 'fall', 'winter']
    
    # Convert to categorical with the defined order
    season_orders_df['season'] = pd.Categorical(season_orders_df['season'], categories=season_order, ordered=True)

    # Sort dataframe based on the defined seasonal order
    season_orders_df = season_orders_df.sort_values(by="season")

    return season_orders_df

# Function to create hourly trend DataFrame
def create_hourly_trend_df(hour_df):
    hourly_trend_df = hour_df.groupby('hour', observed=False).agg({
        'total_count': ['max', 'min', 'sum', 'mean']
    }).reset_index()

    # Convert hour values to "HH.00" format for better visualization
    hourly_trend_df['hour_formatted'] = hourly_trend_df['hour'].astype(str).str.zfill(2) + ".00"

    return hourly_trend_df

def create_user_comparison_df(day_df):
    user_comparison_df = day_df.agg({
        'registered_users': ['sum', 'mean'],
        'casual_users': ['sum', 'mean']
    }).map(lambda x: round(x, 2))
    
    return user_comparison_df

def create_workingday_comparison_df(day_df):
    workingday_comparison_df = day_df.groupby('working_day', observed=False).agg({
        'total_count': ['sum', 'mean']
    })
    return workingday_comparison_df


# Load datasets
df_day = pd.read_csv('./dashboard/cleaned_day.csv')
df_hour = pd.read_csv('./dashboard/cleaned_hour.csv')

# Convert date column to datetime
df_day['date'] = pd.to_datetime(df_day['date'])

# Sidebar for date selection
st.sidebar.header("Date Range Selection")
MIN_DATE = df_day['date'].min().date()
MAX_DATE = df_day['date'].max().date()

min_date = st.sidebar.date_input(
    label="Min Date",
    min_value=MIN_DATE, max_value=MAX_DATE,
    value=MIN_DATE
)

max_date = st.sidebar.date_input(
    label="Max Date",
    min_value=MIN_DATE, max_value=MAX_DATE,
    value=MAX_DATE
)

# Filter data based on selected date range
df_filtered = df_day[(df_day['date'].dt.date >= min_date) & (df_day['date'].dt.date <= max_date)]

# Generate DataFrames
monthyear_progress_df = create_monthyear_progress_df(df_day)
monthly_orders_df = create_monthly_orders_df(df_day)
daily_orders_df = create_daily_orders_df(df_day)
season_orders_df = create_season_orders_df(df_day)
hourly_trend_df = create_hourly_trend_df(df_hour)
user_comparison_df = create_user_comparison_df(df_day)
workingday_comparison_df = create_workingday_comparison_df(df_day)

# Calculate key metrics
total_rentals = df_day['total_count'].sum()
avg_rentals_per_day = df_day['total_count'].mean()
total_registered_users = df_day['registered_users'].sum()
total_casual_users = df_day['casual_users'].sum()
min_orders_per_day = df_day['total_count'].min()
max_orders_per_day = df_day['total_count'].max()

# Format numbers with commas
total_rentals_fmt = f"{int(total_rentals):,}"
avg_rentals_fmt = f"{int(avg_rentals_per_day):,}"
total_registered_fmt = f"{int(total_registered_users):,}"
total_casual_fmt = f"{int(total_casual_users):,}"
min_orders_fmt = f"{int(min_orders_per_day):,}"
max_orders_fmt = f"{int(max_orders_per_day):,}"


# Header with a title and description
st.markdown("<h1 style='text-align: center; color: #00A3FF;'>🚴‍♂️ Bike Rental Dashboard 🚴‍♀️</h1>", unsafe_allow_html=True)

st.markdown('''
    <div style="
        text-align: center; 
        font-size: 18px; 
        background-color: #dff6ff; 
        padding: 15px; 
        border-radius: 10px; 
        color: #004C99;
        font-weight: bold;
        margin-bottom: 20px;
    ">
        📊 Explore trends in bike rentals across different timeframes, user types, and conditions. 
        Gain insights into demand fluctuations, peak rental hours, and seasonal variations! 🚲
    </div>
''', unsafe_allow_html=True)

st.divider()

# Create layout with columns
col1, col2, col3 = st.columns(3)

with col1:
    st.metric(label="Total Bike Rentals", value=total_rentals_fmt)
    st.metric(label="Min Orders/Day", value=min_orders_fmt)

with col2:
    st.metric(label="Avg Rentals/Day", value=avg_rentals_fmt)
    st.metric(label="Max Orders/Day", value=max_orders_fmt)

with col3:
    st.metric(label="Total Registered Users", value=total_registered_fmt)
    st.metric(label="Total Casual Users", value=total_casual_fmt)

st.divider()

# Function to create styled subheaders
def styled_subheader(text):
    st.markdown(f"<h2 style='color: #00A3FF;'>{text}</h2>", unsafe_allow_html=True)
    
# 📅 Monthly Progress Visualization    
styled_subheader("📅 Monthly Progress")
if not monthyear_progress_df.empty:
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.plot(monthyear_progress_df['month/year'], monthyear_progress_df['total_count'], marker='o', linewidth=2, label='Monthly Progress (2011-2012)')
    ax.set_title('Monthly Progress of Bike Renting (2011-2012)')
    ax.set_xlabel('Month/Year')
    ax.set_ylabel('Total Bikes Rented')
    ax.legend()
    plt.xticks(rotation=45)
    st.pyplot(fig)
else:
    st.warning("No data available for monthly progress.")
    
st.divider()

# 🎯 Monthly Rentals Visualization
styled_subheader("📅 Average Monthly Rentals")
if not monthly_orders_df.empty:
    max_value = monthly_orders_df["total_count"].max()
    colors = ['#A7C7E7' if v < max_value else '#004C99' for v in monthly_orders_df["total_count"]]

    fig, ax = plt.subplots(figsize=(14, 7))
    sns.barplot(x=monthly_orders_df["month"], y=monthly_orders_df["total_count"], ax=ax, palette=colors)

    ax.set_xlabel("Month")
    ax.set_ylabel("Total Bike Rented")
    ax.set_title("Average Monthly Rentals")
    st.pyplot(fig)
else:
    st.warning("No data available to display.")
st.divider()

# 📆 Daily Rentals Visualization
styled_subheader("📊 Average Daily Rentals")
if not daily_orders_df.empty:
    max_value = daily_orders_df[('total_count', 'mean')].max()
    colors = ['#A7C7E7' if v < max_value else '#004C99' for v in daily_orders_df[('total_count', 'mean')]]

    fig, ax = plt.subplots(figsize=(14, 7))
    sns.barplot(x=daily_orders_df["weekday"], y=daily_orders_df[('total_count', 'mean')], ax=ax, palette=colors)

    ax.set_xlabel("Day of the Week")
    ax.set_ylabel("Total Bike Rented")
    ax.set_title("Average Daily Rentals")
    st.pyplot(fig)
else:
    st.warning("No data available to display.")
st.divider()

# 🌦️ Seasonal Rentals
styled_subheader("🌍 Average Seasonal Rentals")
if not season_orders_df.empty:
    max_value = season_orders_df[('total_count', 'mean')].max()
    colors = ['#A7C7E7' if v < max_value else '#004C99' for v in season_orders_df[('total_count', 'mean')]]

    fig, ax = plt.subplots(figsize=(14, 7))
    sns.barplot(x=season_orders_df['season'], y=season_orders_df[('total_count', 'mean')], ax=ax, palette=colors)

    ax.set_xlabel("Season of the Year")
    ax.set_ylabel("Total Bike Rented")
    ax.set_title("Average Seasonal Rentals")
    st.pyplot(fig)
else:
    st.warning("No data available to display.")
st.divider()

# ⏰ Hourly Trends
styled_subheader("⏳ Total Bike Rentals by Hour")
if not hourly_trend_df.empty:
    max_value = hourly_trend_df[('total_count', 'sum')].max()
    colors = ['#A7C7E7' if v < max_value else '#004C99' for v in hourly_trend_df[('total_count', 'sum')]]

    fig, ax = plt.subplots(figsize=(10, 5))
    sns.barplot(x=hourly_trend_df['hour_formatted'], y=hourly_trend_df[('total_count', 'sum')], ax=ax, palette=colors)

    ax.set_xlabel('Hour of the Day')
    ax.set_ylabel('Total Bike Rented')
    ax.set_title('Total Bike Rentals by Hour')
    plt.xticks(rotation=45)
    plt.grid(False)
    st.pyplot(fig)
else:
    st.warning("No data available to display.")
st.divider()

# 🏆 User Type Comparison
styled_subheader("👥 Total Bike Rentals by User Type")
if not user_comparison_df.empty and not user_comparison_df.isna().values.any():
    values = [user_comparison_df['registered_users']['mean'], user_comparison_df['casual_users']['mean']]
    labels = ['Registered', 'Casual']
    colors = ['#A7C7E7', '#004C99']

    fig1, ax1 = plt.subplots(figsize=(6, 6))
    ax1.pie(values, labels=labels, autopct='%1.1f%%', colors=colors, startangle=90, explode=[0.05, 0.05], shadow=True, textprops={'fontsize': 12})
    ax1.set_title('Total Bike Rentals by User Type', fontsize=14)
    st.pyplot(fig1)
else:
    st.warning("No data available to display.")
st.divider()

# 📅 Holiday vs. Working Day Rentals
styled_subheader("🏖️ Holiday vs. Working Day Rentals")
if not workingday_comparison_df.empty and not workingday_comparison_df.isna().values.any():
    workingday_values = workingday_comparison_df['total_count']['mean'].tolist()
    
    if len(workingday_values) == 2:
        values = workingday_values
        labels = ['Holiday', 'Working Day']
        colors = ['#A7C7E7', '#004C99']

        fig2, ax2 = plt.subplots(figsize=(6, 6))
        ax2.pie(values, labels=labels, autopct='%1.1f%%', colors=colors, startangle=90, explode=[0.05, 0.05], shadow=True, textprops={'fontsize': 12})
        ax2.set_title('Total Bike Rentals: Holiday vs. Working Day', fontsize=14)
        st.pyplot(fig2)
    else:
        st.warning("Data for both Holiday and Working Day is missing or incomplete.")
else:
    st.warning("No data available to display.")
st.divider()

st.markdown("<p style='text-align: center;'>Developed by <strong>Naia Shaffa Camila 💖</strong></p>", unsafe_allow_html=True)
