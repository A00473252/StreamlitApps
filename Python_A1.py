import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import requests

# Configuration for API access
api_key = "CG-NcncrdeWGMMXhF8h9QLz5omP"
headers = {
    "accept": "application/json",
    "x-cg-demo-api-key": api_key
}

# Function to fetch historical price data for a given cryptocurrency within a specified time frame
def get_historical_data(coin_id, days):
    url = f"https://api.coingecko.com/api/v3/coins/{coin_id}/market_chart"
    params = {
        "vs_currency": "usd",
        "days": days
    }
    response = requests.get(url, headers=headers, params=params)
    data = response.json()
    
    try:
        prices = data['prices']
        df = pd.DataFrame(prices, columns=['timestamp', 'price'])
        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
        return df
    except KeyError:
        # Handle the case where the API response does not contain the expected price data
        print("Unexpected API response format. Unable to retrieve historical price data.")
        print("Response data:", data)
        return None

# Function to get coin ID from coin name with error handling
def get_coin_id(coin_name):
    try:
        url = "https://api.coingecko.com/api/v3/coins/list"
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # Raise an exception for unsuccessful status codes
        coins = response.json()
        
        if isinstance(coins, list):
            for coin in coins:
                if isinstance(coin, dict) and 'name' in coin:
                    if coin['name'].lower() == coin_name.lower():
                        return coin['id']
        return None
    except requests.exceptions.RequestException as e:
        # Handle any request exceptions, such as network errors
        print("Error fetching data from CoinGecko API:", e)
        return None
    except KeyError:
        # Handle the case where the API response does not contain expected data
        print("Unexpected API response format. Unable to retrieve coin ID.")
        return None



# Main Streamlit app for Stock Details
def stock_details_app():
    st.title('Stock Details App')

    # User input for cryptocurrency name
    coin_name = st.text_input('Enter cryptocurrency name (e.g., Bitcoin):')

    if coin_name:
        coin_id = get_coin_id(coin_name)
        if coin_id:
            st.write(f"Fetching data for {coin_name}...")
            data = get_historical_data(coin_id, 365)
            
            if data is not None:
                # Plotting historical price data
                st.subheader('Historical Price Chart')
                plt.figure(figsize=(10, 6))
                plt.plot(data['timestamp'], data['price'])
                plt.title(f'{coin_name} Price Over Last Year')
                plt.xlabel('Date')
                plt.ylabel('Price (USD)')
                st.pyplot(plt)
                
                # Displaying additional details
                st.subheader('Additional Details')
                st.write(f"Maximum Price: ${data['price'].max():.2f}")
                st.write(f"Minimum Price: ${data['price'].min():.2f}")
                max_date = data.loc[data['price'].idxmax()]['timestamp'].strftime('%Y-%m-%d')
                min_date = data.loc[data['price'].idxmin()]['timestamp'].strftime('%Y-%m-%d')
                st.write(f"Date of Maximum Price: {max_date}")
                st.write(f"Date of Minimum Price: {min_date}")
            else:
                st.error("Unable to fetch historical price data. Please try again later.")
        else:
            st.error("Cryptocurrency not found. Please enter a valid name.")

# Function to fetch historical price data for two cryptocurrencies within a specified time frame
def get_comparison_data(coin1_id, coin2_id, days):
    data1 = get_historical_data(coin1_id, days)
    data2 = get_historical_data(coin2_id, days)
    return data1, data2

# Main Streamlit app for Coin Comparison
def coin_comparison_app():
    st.title('Coin Comparison App')

    # User input for cryptocurrency names and time frame
    coin1_name = st.text_input('Enter the first cryptocurrency name (e.g., Bitcoin):')
    coin2_name = st.text_input('Enter the second cryptocurrency name (e.g., Bitcoin):')
    time_frame = st.selectbox('Select time frame:', ['1 week', '1 month', '1 year', '5 years'])

    if coin1_name and coin2_name:
        coin1_id = get_coin_id(coin1_name)
        coin2_id = get_coin_id(coin2_name)
        if coin1_name and coin2_name:
            st.write(f"Fetching data for {coin1_name} and {coin2_name}...")
            if time_frame == '1 week':
                days = 7
            elif time_frame == '1 month':
                days = 30
            elif time_frame == '1 year':
                days = 365
            elif time_frame == '5 years':
                days = 1825  # Considering 365 days per year

            data1, data2 = get_comparison_data(coin1_id, coin2_id, days)

            if data1 is not None and data2 is not None:
                # Plotting historical price data for both cryptocurrencies
                st.subheader('Price Comparison Chart')
                plt.figure(figsize=(10, 6))
                plt.plot(data1['timestamp'], data1['price'], label=coin1_name)
                plt.plot(data2['timestamp'], data2['price'], label=coin2_name)
                plt.title(f'{coin1_name} vs {coin2_name} Price Comparison')
                plt.xlabel('Date')
                plt.ylabel('Price (USD)')
                plt.legend()
                st.pyplot(plt)

                # Displaying additional details for both coins
                st.subheader('Additional Details for Both Coins')
                for coin_name, data in zip([coin1_name, coin2_name], [data1, data2]):
                    st.markdown(f"**{coin_name}**")
                    st.write(f"**Maximum Price:** ${data['price'].max():.2f}")
                    st.write(f"**Minimum Price:** ${data['price'].min():.2f}")
                    max_date = data.loc[data['price'].idxmax()]['timestamp'].strftime('%Y-%m-%d')
                    min_date = data.loc[data['price'].idxmin()]['timestamp'].strftime('%Y-%m-%d')
                    st.write(f"**Date of Maximum Price:** {max_date}")
                    st.write(f"**Date of Minimum Price:** {min_date}")
                    st.write("\n")
                    st.write("\n")
            else:
                st.error("Unable to fetch historical price data for one or both cryptocurrencies. Please try again later.")
        else:
            st.error("One or both cryptocurrencies not found. Please enter valid names.")

# Main Streamlit app
def main():
    st.sidebar.title("Pick an App you want to try")
    app_selection = st.sidebar.radio(
        "Choose an app:",
        ("Stock Details", "Coin Comparison")
    )

    if app_selection == "Stock Details":
        stock_details_app()
    elif app_selection == "Coin Comparison":
        coin_comparison_app()

if __name__ == "__main__":
    main()
