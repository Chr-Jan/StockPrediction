import streamlit as st
from datetime import date, datetime
import yfinance as yf
from prophet import Prophet
from prophet.plot import plot_plotly
from plotly import graph_objs as go

# Title
st.title("Stock Price Prediction")

# User input for start year
start_year = st.number_input("Enter the start year (e.g., 1995)", min_value=1900, max_value=date.today().year - 1, value=1995)

# Convert start year to start date
START = datetime(start_year, 1, 1).strftime("%Y-%m-%d")
TODAY = date.today().strftime("%Y-%m-%d")

# Stock selection via text input
selected_stock = st.text_input("Enter a Stock Ticker Symbol (e.g., AAPL)", "AAPL")
if not selected_stock:
    st.warning("Please enter a valid stock ticker symbol.")
    st.stop()

# Years of prediction
n_years = st.slider("Years of prediction:", 1, 10)
period = n_years * 365

# Cache data loading function
@st.cache_data()
def load_data(ticker, start_date, end_date):
    try:
        data = yf.download(ticker, start_date, end_date)
        if data.empty:
            st.warning("No data found for the selected stock. Please try another.")
            return None
        data.reset_index(inplace=True)
        return data
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return None

# Load data
data_load_state = st.text("Loading data...")
data = load_data(selected_stock, START, TODAY)
data_load_state.text("")

# Check if data is loaded
if data is not None:
    st.subheader("Raw data")
    st.write(data.tail())

    # Plot raw data
    def plot_raw_data():
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=data['Date'], y=data['Open'], name="Stock Open"))
        fig.add_trace(go.Scatter(x=data['Date'], y=data['Close'], name="Stock Close"))
        fig.layout.update(title_text="Time Series Data", xaxis_rangeslider_visible=True)
        st.plotly_chart(fig)

    plot_raw_data()

    # Forecasting
    df_train = data[["Date", "Close"]].rename(columns={"Date": "ds", "Close": "y"})

    # Initialize and fit model
    m = Prophet()
    m.fit(df_train)
    
    # Make future predictions
    future = m.make_future_dataframe(periods=period)
    forecast = m.predict(future)

    st.subheader("Forecast data")
    st.write(forecast.tail())

    # Plot forecast
    st.write("Forecast data")
    fig1 = plot_plotly(m, forecast)
    st.plotly_chart(fig1, use_container_width=True)

    # Plot forecast components
    st.write("Forecast components")
    fig2 = m.plot_components(forecast)
    st.write(fig2)
else:
    st.error("Failed to load data. Please check your internet connection or try again later.")
