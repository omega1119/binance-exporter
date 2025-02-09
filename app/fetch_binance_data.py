from binance.client import Client
from config import myconfig
from datetime import datetime, timedelta
import os
import csv
import time
from tqdm import tqdm
import pyarrow as pa
import pyarrow.parquet as pq
import polars as pl

# Read API keys
API_KEY = myconfig.BINANCE_API_KEY
API_SECRET = myconfig.BINANCE_API_SECRET

# Initialize Binance client
client = Client(API_KEY, API_SECRET)

# Get the absolute path of the script directory
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

# File to store last known end_time
LAST_RUN_FILE = os.path.join(SCRIPT_DIR, "last_run.txt")

# Overwrite mode: True = overwrites previous CSV and Parquet files, False = appends new data
OVERWRITE_MODE = True  

# Restart mode: True = skips pairs that already have CSV/Parquet files, False = fetches all pairs
RESTART_MODE = True  

# Parameterized Kline interval (Set this to any valid Binance interval) 1s, 1m, 3m, 5m, 15m, 30m
KLINE_INTERVAL = Client.KLINE_INTERVAL_30MINUTE  # Change as needed

# Select specific trading pairs (Set to None to fetch all)
# TARGET_PAIRS = ["BTCUSDT", "ETHUSDT", "BNBUSDT"]  # Modify or set to None for all
# TARGET_PAIRS = None
TARGET_PAIRS = ["BTCUSDT"]

def get_time_ms_to_str(time):
    return str(int(time.timestamp() * 1000))

# Function to read last recorded end_time from file
def get_last_end_time():
    if os.path.exists(LAST_RUN_FILE):
        with open(LAST_RUN_FILE, "r") as f:
            last_end_time_ms = f.read().strip()
            if last_end_time_ms.isdigit():
                return datetime.utcfromtimestamp(int(last_end_time_ms) / 1000)
    return datetime.now()  # Default to current time if no record exists

# Function to fetch historical data for a trading pair
def fetch_historical_data(pair, start_time, end_time, interval=KLINE_INTERVAL):
    """
    Fetch historical klines (candlestick data) for a trading pair.
    Handles Binance's 1000-candle limit via pagination.
    """
    start_time_ms = int(start_time.timestamp() * 1000)
    end_time_ms = int(end_time.timestamp() * 1000)

    all_klines = []
    
    while start_time_ms < end_time_ms:
        klines = client.get_historical_klines(
            symbol=pair,
            interval=interval,
            start_str=start_time_ms
        )

        if not klines:
            break  # Exit if no data is returned
        
        all_klines.extend(klines)

        # Binance returns max 1000 candles per request. Continue from last timestamp.
        start_time_ms = klines[-1][0] + 1

        # Sleep to avoid hitting Binance rate limits
        time.sleep(0.5)
    
    return all_klines

# Function to save klines data to a CSV file
def save_to_csv(pair, klines, interval_folder):
    """
    Save klines data to a CSV file. Supports both overwrite and append modes.
    """
    os.makedirs(interval_folder, exist_ok=True)  # Ensure directory exists

    csv_file = os.path.join(interval_folder, f"{pair}.csv")

    mode = 'w' if OVERWRITE_MODE else 'a'
    file_exists = os.path.isfile(csv_file)

    with open(csv_file, mode=mode, newline='') as file:
        writer = csv.writer(file)

        # Write header only if overwriting or if the file is new
        if OVERWRITE_MODE or not file_exists:
            writer.writerow([
                "Open Time", "Open", "High", "Low", "Close", "Volume",
                "Close Time", "Quote Asset Volume", "Number of Trades",
                "Taker Buy Base Asset Volume", "Taker Buy Quote Asset Volume", "Ignore"
            ])

        for kline in klines:
            writer.writerow(kline)

# Function to save klines data to a Parquet file
def save_to_parquet(pair, klines, interval_folder):
    """
    Save klines data to a Parquet file in the given folder.
    """
    os.makedirs(interval_folder, exist_ok=True)  # Ensure directory exists

    parquet_file = os.path.join(interval_folder, f"{pair}.parquet")

    # Explicitly set orientation="row" to avoid the warning
    df = pl.DataFrame(klines, schema=[
        "Open Time", "Open", "High", "Low", "Close", "Volume",
        "Close Time", "Quote Asset Volume", "Number of Trades",
        "Taker Buy Base Asset Volume", "Taker Buy Quote Asset Volume", "Ignore"
    ], orient="row")

    pq.write_table(df.to_arrow(), parquet_file)

# Function to save last end_time
def save_end_time(end_time):
    with open(LAST_RUN_FILE, "w") as f:
        f.write(get_time_ms_to_str(end_time))  # Save in milliseconds

# Add this function to your script
def main():
    # Define the time range (Last 24 hours from last recorded end_time)
    end_time = get_last_end_time()
    start_time = end_time - timedelta(days=1)

    print(f"⏳ Fetching data from {start_time} to {end_time} (Interval: {KLINE_INTERVAL})")

    # Define the folder structure based on the selected Kline interval
    data_folder = os.path.join(SCRIPT_DIR, f"data/{get_time_ms_to_str(end_time)}")
    interval_folder = os.path.join(data_folder, KLINE_INTERVAL)

    # Create required directories if they don't exist
    os.makedirs(interval_folder, exist_ok=True)

    # Get exchange information
    exchange_info = client.get_exchange_info()

    # Extract trading pairs and filter for 'TRADING' status
    trading_pairs = []
    for symbol_info in exchange_info['symbols']:
        if symbol_info['status'] == 'TRADING':  # Ensure the pair is actively trading
            trading_pair = symbol_info['symbol']
            if TARGET_PAIRS is None or trading_pair in TARGET_PAIRS:
                trading_pairs.append(trading_pair)

    # Get existing CSV/Parquet files if RESTART_MODE is enabled
    existing_files = set(os.listdir(interval_folder)) if RESTART_MODE else set()

    # Fetch and save historical data for each trading pair
    for pair in tqdm(trading_pairs, desc="Fetching Binance Data", unit="pair"):
        csv_file = f"{pair}.csv"
        parquet_file = f"{pair}.parquet"

        # Skip if RESTART_MODE is enabled and the files already exist
        if RESTART_MODE and (csv_file in existing_files or parquet_file in existing_files):
            print(f"⏩ Skipping {pair}, data already exists.")
            continue

        print(f"Fetching historical data for {pair}...")
        try:
            # Fetch historical data
            klines = fetch_historical_data(pair, start_time, end_time, KLINE_INTERVAL)

            # Save to CSV
            save_to_csv(pair, klines, interval_folder)

            # Save to Parquet
            save_to_parquet(pair, klines, interval_folder)

            print(f"✔ Data for {pair} saved to {interval_folder}/{pair}.csv and {interval_folder}/{pair}.parquet")
        except Exception as e:
            print(f"❌ Failed to fetch data for {pair}: {e}")

    # Save the latest end_time after fetching data
    save_end_time(datetime.now())

    # Load a Parquet file into Polars DataFrame for verification
    if trading_pairs:
        test_pair = trading_pairs[0]
        parquet_path = os.path.join(interval_folder, f"{test_pair}.parquet")

        if os.path.exists(parquet_path):
            df = pl.read_parquet(parquet_path)
            print(f"📊 Sample data from {test_pair} Parquet file:")
            print(df.head())

# Add this at the end of your script to call main() when the script is executed
if __name__ == "__main__":
    main()