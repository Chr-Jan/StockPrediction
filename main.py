import streamlit as st
from datetime import date
import yfinance as yf
from prophet import Prophet
from prophet.plot import plot_plotly
from plotly import graph_objs as go

START = "2015-01-01"
TODAY = date.today().strftime("%Y-%m-%d")

# Title
st.title("Stock Price Prediction")

# Stock selection
stocks = ("AAPL", "GOOG", "TSLA", "AMZN", "MSFT", "GME", "AMC")
selected_stock = st.selectbox("Select a Stock", stocks)

# Years of prediction
n_years = st.slider("Years of prediction:", 1, 5)
period = n_years * 365

# Cache data loading function
@st.cache_data(persist=True)
def load_data(ticker):
    try:
        data = yf.download(ticker, START, TODAY)
        data.reset_index(inplace=True)
        return data
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return None

# Load data
data_load_state = st.text("Loading data...")
data = load_data(selected_stock)
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
    st.error("Failed to load data.")
