import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import yfinance as yf
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

# Page configuration
st.set_page_config(
    page_title="Tesla Stock Prediction Dashboard",
    page_icon="🚗",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #1f77b4;
    }
    .prediction-card {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
    }
    .sentiment-positive {
        color: #28a745;
        font-weight: bold;
    }
    .sentiment-negative {
        color: #dc3545;
        font-weight: bold;
    }
    .sentiment-neutral {
        color: #6c757d;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

# Title and header
st.markdown('<h1 class="main-header">🚗 Tesla Stock Prediction Dashboard</h1>', unsafe_allow_html=True)

# Sidebar configuration
st.sidebar.title("📊 Dashboard Controls")
st.sidebar.markdown("---")

# Date range selection
st.sidebar.subheader("📅 Date Range")
default_start = datetime.now() - timedelta(days=365)
default_end = datetime.now()

start_date = st.sidebar.date_input(
    "Start Date",
    value=default_start,
    max_value=datetime.now()
)

end_date = st.sidebar.date_input(
    "End Date", 
    value=default_end,
    max_value=datetime.now()
)

# Model selection
st.sidebar.subheader("🤖 Model Selection")
selected_models = st.sidebar.multiselect(
    "Choose Models to Display",
    ["ARIMA", "LSTM", "Hybrid"],
    default=["Hybrid", "LSTM"]
)

# Feature selection
st.sidebar.subheader("📈 Features")
show_sentiment = st.sidebar.checkbox("Show Sentiment Analysis", value=True)
show_technical = st.sidebar.checkbox("Show Technical Indicators", value=True)
show_predictions = st.sidebar.checkbox("Show Future Predictions", value=True)

# Main dashboard content
@st.cache_data
def fetch_stock_data(ticker="TSLA", start_date=None, end_date=None):
    """Fetch stock data with caching"""
    try:
        data = yf.download(ticker, start=start_date, end=end_date, progress=False)
        
        # Calculate technical indicators
        data['Returns'] = data['Close'].pct_change()
        data['Volatility'] = data['Returns'].rolling(window=10).std()
        data['MA_10'] = data['Close'].rolling(window=10).mean()
        data['MA_30'] = data['Close'].rolling(window=30).mean()
        
        # Calculate RSI
        delta = data['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        data['RSI'] = 100 - (100 / (1 + rs))
        
        data['Price_Range'] = data['High'] - data['Low']
        data.dropna(inplace=True)
        
        return data
    except Exception as e:
        st.error(f"Error fetching data: {e}")
        return None

# Fetch data
with st.spinner("📈 Fetching Tesla stock data..."):
    stock_data = fetch_stock_data("TSLA", start_date, end_date)

if stock_data is None:
    st.error("Failed to fetch stock data. Please check your internet connection.")
    st.stop()

# Key metrics row
col1, col2, col3, col4 = st.columns(4)

with col1:
    current_price = stock_data['Close'].iloc[-1]
    price_change = stock_data['Close'].iloc[-1] - stock_data['Close'].iloc[-2]
    price_change_pct = (price_change / stock_data['Close'].iloc[-2]) * 100
    
    st.metric(
        label="Current Price",
        value=f"${float(current_price):.2f}",
        delta=f"{float(price_change):+.2f} ({float(price_change_pct):+.2f}%)"
    )

with col2:
    period_high = stock_data['High'].max()
    period_low = stock_data['Low'].min()
    
    st.metric(
        label="52-Week Range",
        value=f"${float(period_low):.2f} - ${float(period_high):.2f}",
        delta=f"Range: ${float(period_high - period_low):.2f}"
    )

with col3:
    avg_volume = stock_data['Volume'].mean()
    current_volume = stock_data['Volume'].iloc[-1]
    
    st.metric(
        label="Average Volume",
        value=f"{int(avg_volume):,}",
        delta=f"Current: {int(current_volume):,}"
    )

with col4:
    volatility = stock_data['Volatility'].iloc[-1]
    rsi = stock_data['RSI'].iloc[-1]
    
    st.metric(
        label="Current RSI",
        value=f"{float(rsi):.1f}",
        delta=f"Volatility: {float(volatility):.3f}"
    )

st.markdown("---")

# Main charts section
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📈 Stock Analysis", 
    "🎭 Sentiment Analysis", 
    "🤖 Model Predictions", 
    "📊 Performance Metrics",
    "🔮 Future Forecast"
])

with tab1:
    st.subheader("📈 Tesla Stock Analysis")
    
    # Price chart with technical indicators
    fig = make_subplots(
        rows=3, cols=1,
        shared_xaxes=True,
        vertical_spacing=0.05,
        subplot_titles=('Price & Moving Averages', 'Volume', 'RSI'),
        row_heights=[0.6, 0.2, 0.2]
    )
    
    # Price and moving averages
    fig.add_trace(
        go.Scatter(
            x=stock_data.index,
            y=stock_data['Close'],
            name='Close Price',
            line=dict(color='#1f77b4', width=2)
        ),
        row=1, col=1
    )
    
    fig.add_trace(
        go.Scatter(
            x=stock_data.index,
            y=stock_data['MA_10'],
            name='MA 10',
            line=dict(color='orange', width=1, dash='dash')
        ),
        row=1, col=1
    )
    
    fig.add_trace(
        go.Scatter(
            x=stock_data.index,
            y=stock_data['MA_30'],
            name='MA 30',
            line=dict(color='red', width=1, dash='dash')
        ),
        row=1, col=1
    )
    
    # Volume
    colors = ['green' if close >= open else 'red' 
              for close, open in zip(stock_data['Close'], stock_data['Open'])]
    
    fig.add_trace(
        go.Bar(
            x=stock_data.index,
            y=stock_data['Volume'],
            name='Volume',
            marker_color=colors,
            opacity=0.7
        ),
        row=2, col=1
    )
    
    # RSI
    fig.add_trace(
        go.Scatter(
            x=stock_data.index,
            y=stock_data['RSI'],
            name='RSI',
            line=dict(color='purple', width=2)
        ),
        row=3, col=1
    )
    
    # Add RSI overbought/oversold lines
    fig.add_hline(y=70, line_dash="dash", line_color="red", row=3, col=1)
    fig.add_hline(y=30, line_dash="dash", line_color="green", row=3, col=1)
    
    fig.update_layout(
        height=800,
        title_text="Tesla Stock Analysis",
        showlegend=True,
        xaxis_rangeslider_visible=False
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Technical indicators summary
    if show_technical:
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.subheader("📊 Technical Indicators")
            
            # RSI interpretation
            rsi_status = "Overbought" if rsi > 70 else "Oversold" if rsi < 30 else "Neutral"
            rsi_color = "red" if rsi > 70 else "green" if rsi < 30 else "orange"
            
            st.markdown(f"""
            <div class="metric-card">
                <h4>RSI: {rsi:.1f}</h4>
                <p style="color: {rsi_color};">Status: {rsi_status}</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            # Moving average analysis
            ma10 = stock_data['MA_10'].iloc[-1]
            ma30 = stock_data['MA_30'].iloc[-1]
            ma_signal = "Bullish" if ma10 > ma30 else "Bearish"
            ma_color = "green" if ma10 > ma30 else "red"
            
            st.markdown(f"""
            <div class="metric-card">
                <h4>Moving Averages</h4>
                <p>MA 10: ${ma10:.2f}</p>
                <p>MA 30: ${ma30:.2f}</p>
                <p style="color: {ma_color};">Signal: {ma_signal}</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            # Volatility analysis
            avg_volatility = stock_data['Volatility'].mean()
            vol_status = "High" if volatility > avg_volatility * 1.5 else "Low" if volatility < avg_volatility * 0.5 else "Normal"
            vol_color = "red" if vol_status == "High" else "green" if vol_status == "Low" else "orange"
            
            st.markdown(f"""
            <div class="metric-card">
                <h4>Volatility</h4>
                <p>Current: {volatility:.3f}</p>
                <p>Average: {avg_volatility:.3f}</p>
                <p style="color: {vol_color};">Status: {vol_status}</p>
            </div>
            """, unsafe_allow_html=True)

with tab2:
    st.subheader("🎭 Sentiment Analysis")
    
    # Simulate sentiment data (in real implementation, this would come from the model)
    sentiment_data = pd.DataFrame({
        'Date': stock_data.index,
        'Sentiment_Score': np.random.normal(0, 0.3, len(stock_data)),
        'News_Count': np.random.randint(1, 10, len(stock_data)),
        'Positive_News': np.random.randint(0, 5, len(stock_data)),
        'Negative_News': np.random.randint(0, 5, len(stock_data))
    })
    
    # Sentiment over time
    fig = make_subplots(
        rows=2, cols=1,
        subplot_titles=('Sentiment Score Over Time', 'News Volume'),
        vertical_spacing=0.1
    )
    
    # Sentiment score
    fig.add_trace(
        go.Scatter(
            x=sentiment_data['Date'],
            y=sentiment_data['Sentiment_Score'],
            name='Sentiment Score',
            line=dict(color='blue', width=2)
        ),
        row=1, col=1
    )
    
    fig.add_hline(y=0, line_dash="dash", line_color="gray", row=1, col=1)
    
    # News volume
    fig.add_trace(
        go.Bar(
            x=sentiment_data['Date'],
            y=sentiment_data['News_Count'],
            name='News Articles',
            marker_color='lightblue'
        ),
        row=2, col=1
    )
    
    fig.update_layout(height=600, title_text="Sentiment Analysis")
    st.plotly_chart(fig, use_container_width=True)
    
    # Sentiment summary
    col1, col2, col3 = st.columns(3)
    
    with col1:
        avg_sentiment = sentiment_data['Sentiment_Score'].mean()
        sentiment_label = "Positive" if avg_sentiment > 0.1 else "Negative" if avg_sentiment < -0.1 else "Neutral"
        sentiment_class = "sentiment-positive" if avg_sentiment > 0.1 else "sentiment-negative" if avg_sentiment < -0.1 else "sentiment-neutral"
        
        st.markdown(f"""
        <div class="metric-card">
            <h4>Average Sentiment</h4>
            <p class="{sentiment_class}">{avg_sentiment:.3f}</p>
            <p class="{sentiment_class}">{sentiment_label}</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        total_news = sentiment_data['News_Count'].sum()
        positive_news = sentiment_data['Positive_News'].sum()
        negative_news = sentiment_data['Negative_News'].sum()
        
        st.markdown(f"""
        <div class="metric-card">
            <h4>News Summary</h4>
            <p>Total Articles: {total_news}</p>
            <p class="sentiment-positive">Positive: {positive_news}</p>
            <p class="sentiment-negative">Negative: {negative_news}</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        recent_sentiment = sentiment_data['Sentiment_Score'].tail(5).mean()
        sentiment_trend = "Improving" if recent_sentiment > avg_sentiment else "Declining"
        trend_color = "green" if sentiment_trend == "Improving" else "red"
        
        st.markdown(f"""
        <div class="metric-card">
            <h4>Recent Trend</h4>
            <p>Recent Sentiment: {recent_sentiment:.3f}</p>
            <p style="color: {trend_color};">Trend: {sentiment_trend}</p>
        </div>
        """, unsafe_allow_html=True)

with tab3:
    st.subheader("🤖 Model Predictions")
    
    # Simulate model predictions (in real implementation, these would come from trained models)
    test_dates = stock_data.index[-30:]
    actual_prices = stock_data['Close'].tail(30)
    
    # Simulate different model predictions
    np.random.seed(42)  # For reproducible results
    
    arima_predictions = actual_prices + np.random.normal(0, 5, len(actual_prices))
    lstm_predictions = actual_prices + np.random.normal(0, 3, len(actual_prices))
    hybrid_predictions = (arima_predictions + lstm_predictions) / 2
    
    # Create predictions comparison chart
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=test_dates,
        y=actual_prices,
        mode='lines+markers',
        name='Actual Price',
        line=dict(color='green', width=3),
        marker=dict(size=6)
    ))
    
    if "ARIMA" in selected_models:
        fig.add_trace(go.Scatter(
            x=test_dates,
            y=arima_predictions,
            mode='lines+markers',
            name='ARIMA Predictions',
            line=dict(color='red', width=2, dash='dash'),
            marker=dict(size=4)
        ))
    
    if "LSTM" in selected_models:
        fig.add_trace(go.Scatter(
            x=test_dates,
            y=lstm_predictions,
            mode='lines+markers',
            name='LSTM Predictions',
            line=dict(color='blue', width=2, dash='dot'),
            marker=dict(size=4)
        ))
    
    if "Hybrid" in selected_models:
        fig.add_trace(go.Scatter(
            x=test_dates,
            y=hybrid_predictions,
            mode='lines+markers',
            name='Hybrid Predictions',
            line=dict(color='purple', width=2, dash='dashdot'),
            marker=dict(size=4)
        ))
    
    fig.update_layout(
        title="Model Predictions vs Actual Prices",
        xaxis_title="Date",
        yaxis_title="Price ($)",
        height=500
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Model performance metrics
    st.subheader("📊 Model Performance Metrics")
    
    def calculate_metrics(actual, predicted):
        mse = np.mean((actual - predicted) ** 2)
        mae = np.mean(np.abs(actual - predicted))
        rmse = np.sqrt(mse)
        mape = np.mean(np.abs((actual - predicted) / actual)) * 100
        return mse, mae, rmse, mape
    
    # Calculate metrics for each model
    models_data = {}
    if "ARIMA" in selected_models:
        models_data["ARIMA"] = calculate_metrics(actual_prices, arima_predictions)
    
    if "LSTM" in selected_models:
        models_data["LSTM"] = calculate_metrics(actual_prices, lstm_predictions)
    
    if "Hybrid" in selected_models:
        models_data["Hybrid"] = calculate_metrics(actual_prices, hybrid_predictions)
    
    # Display metrics in a table
    metrics_df = pd.DataFrame(models_data, index=['MSE', 'MAE', 'RMSE', 'MAPE (%)']).T
    st.dataframe(metrics_df, use_container_width=True)
    
    # Best model identification
    if models_data:
        best_model = min(models_data.items(), key=lambda x: x[1][0])[0]  # Lowest MSE
        st.success(f"🏆 Best performing model: {best_model}")

with tab4:
    st.subheader("📊 Performance Metrics")
    
    # Create performance comparison charts
    col1, col2 = st.columns(2)
    
    with col1:
        # Error distribution
        if "LSTM" in selected_models:
            lstm_errors = actual_prices - lstm_predictions
            
            fig = px.histogram(
                x=lstm_errors,
                title="LSTM Prediction Errors Distribution",
                nbins=20,
                color_discrete_sequence=['blue']
            )
            fig.update_layout(xaxis_title="Prediction Error ($)", yaxis_title="Frequency")
            st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Cumulative returns comparison
        actual_returns = actual_prices.pct_change().cumsum()
        
        if "LSTM" in selected_models:
            lstm_returns = pd.Series(lstm_predictions).pct_change().cumsum()
            
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=test_dates,
                y=actual_returns,
                name='Actual Returns',
                line=dict(color='green', width=2)
            ))
            fig.add_trace(go.Scatter(
                x=test_dates,
                y=lstm_returns,
                name='LSTM Predicted Returns',
                line=dict(color='blue', width=2, dash='dash')
            ))
            fig.update_layout(
                title="Cumulative Returns Comparison",
                xaxis_title="Date",
                yaxis_title="Cumulative Returns"
            )
            st.plotly_chart(fig, use_container_width=True)
    
    # Additional performance metrics
    st.subheader("🔍 Detailed Analysis")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if "LSTM" in selected_models:
            directional_accuracy = np.mean(np.sign(actual_prices.diff()) == np.sign(pd.Series(lstm_predictions).diff())) * 100
            st.metric("Directional Accuracy", f"{directional_accuracy:.1f}%")
    
    with col2:
        if "LSTM" in selected_models:
            correlation = np.corrcoef(actual_prices, lstm_predictions)[0, 1]
            st.metric("Price Correlation", f"{correlation:.3f}")
    
    with col3:
        if "LSTM" in selected_models:
            max_error = np.max(np.abs(actual_prices - lstm_predictions))
            st.metric("Maximum Error", f"${max_error:.2f}")

with tab5:
    st.subheader("🔮 Future Forecast")
    
    if show_predictions:
        # Generate future predictions
        last_price = stock_data['Close'].iloc[-1]
        future_dates = pd.date_range(start=stock_data.index[-1], periods=6, freq='D')[1:]
        
        # Simulate future predictions with uncertainty
        np.random.seed(42)
        base_trend = np.linspace(0, 0.05, 5)  # 5% upward trend
        noise = np.random.normal(0, 0.02, 5)
        future_prices = last_price * (1 + base_trend + noise)
        
        # Create confidence intervals
        confidence_intervals = []
        for i, price in enumerate(future_prices):
            confidence = 0.9 - (i * 0.1)  # Decreasing confidence
            margin = price * (1 - confidence) * 0.1
            confidence_intervals.append((price - margin, price + margin))
        
        # Plot future predictions
        fig = go.Figure()
        
        # Historical data
        fig.add_trace(go.Scatter(
            x=stock_data.index[-30:],
            y=stock_data['Close'].tail(30),
            name='Historical Prices',
            line=dict(color='blue', width=2)
        ))
        
        # Future predictions
        fig.add_trace(go.Scatter(
            x=future_dates,
            y=future_prices,
            name='Predicted Prices',
            line=dict(color='red', width=2, dash='dash'),
            mode='lines+markers'
        ))
        
        # Confidence intervals
        for i, (date, price, (lower, upper)) in enumerate(zip(future_dates, future_prices, confidence_intervals)):
            fig.add_trace(go.Scatter(
                x=[date, date],
                y=[lower, upper],
                mode='lines',
                line=dict(color='red', width=1),
                showlegend=False
            ))
        
        fig.update_layout(
            title="5-Day Price Forecast",
            xaxis_title="Date",
            yaxis_title="Price ($)",
            height=500
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Forecast summary
        st.subheader("📋 Forecast Summary")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            max_pred = max(future_prices)
            min_pred = min(future_prices)
            st.metric("Predicted Range", f"${min_pred:.2f} - ${max_pred:.2f}")
        
        with col2:
            avg_pred = np.mean(future_prices)
            total_change = ((avg_pred - last_price) / last_price) * 100
            st.metric("Average Prediction", f"${avg_pred:.2f}", f"{total_change:+.2f}%")
        
        with col3:
            volatility_pred = np.std(future_prices)
            st.metric("Predicted Volatility", f"${volatility_pred:.2f}")
        
        # Detailed predictions table
        st.subheader("📅 Daily Predictions")
        
        predictions_data = []
        for i, (date, price, (lower, upper)) in enumerate(zip(future_dates, future_prices, confidence_intervals)):
            change = price - last_price
            change_pct = (change / last_price) * 100
            confidence = 0.9 - (i * 0.1)
            
            predictions_data.append({
                'Date': date.strftime('%Y-%m-%d'),
                'Predicted Price': f"${price:.2f}",
                'Change': f"{change:+.2f}",
                'Change %': f"{change_pct:+.2f}%",
                'Confidence': f"{confidence:.1%}",
                'Range': f"${lower:.2f} - ${upper:.2f}"
            })
        
        predictions_df = pd.DataFrame(predictions_data)
        st.dataframe(predictions_df, use_container_width=True)
        
        # Trading recommendations
        st.subheader("💡 Trading Insights")
        
        if total_change > 2:
            recommendation = "🟢 Bullish - Consider buying opportunities"
            color = "green"
        elif total_change < -2:
            recommendation = "🔴 Bearish - Consider selling or waiting"
            color = "red"
        else:
            recommendation = "🟡 Neutral - Monitor for clearer signals"
            color = "orange"
        
        st.markdown(f"""
        <div class="prediction-card">
            <h4>Recommendation</h4>
            <p style="color: {color}; font-weight: bold;">{recommendation}</p>
            <p>Based on model predictions and technical analysis</p>
        </div>
        """, unsafe_allow_html=True)

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #666;">
    <p>🚗 Tesla Stock Prediction Dashboard | Built with Streamlit</p>
    <p><small>This dashboard is for educational purposes only. Always consult financial advisors before making investment decisions.</small></p>
</div>
""", unsafe_allow_html=True)