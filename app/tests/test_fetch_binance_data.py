import pytest
import os
import tempfile
import pyarrow as pa
import pyarrow.parquet as pq
from unittest.mock import patch, MagicMock
from datetime import datetime, timedelta
from app.fetch_binance_data import (
    fetch_historical_data,
    save_to_csv,
    save_to_parquet,
    get_last_end_time,
    save_end_time,
)

# Mock API response with limited data to prevent infinite loops
def mock_binance_klines(*args, **kwargs):
    if mock_binance_klines.call_count == 0:
        mock_binance_klines.call_count += 1
        return [
            [1700000000000, "100", "110", "90", "105", "1000", 1700000300000, "10000", 500, "500", "5000", "0"],
            [1700000300000, "105", "115", "95", "110", "2000", 1700000600000, "20000", 600, "600", "6000", "0"],
        ]
    return []  # Stop returning data to exit loop

mock_binance_klines.call_count = 0

@pytest.fixture
def temp_dir():
    with tempfile.TemporaryDirectory() as tmpdir:
        yield tmpdir

@patch("app.fetch_binance_data.client.get_historical_klines", side_effect=mock_binance_klines)
def test_fetch_historical_data(mock_get_klines):
    start_time = datetime.utcnow() - timedelta(hours=1)
    end_time = datetime.utcnow()
    result = fetch_historical_data("BTCUSDT", start_time, end_time, "30m")
    assert len(result) == 2
    assert result[0][1] == "100"  # Open price check
    assert result[1][4] == "110"  # Close price check

@patch("builtins.open", new_callable=MagicMock)
def test_save_end_time(mock_open, temp_dir):
    test_time = datetime.utcnow()
    file_path = os.path.join(temp_dir, "last_run.txt")
    
    with patch("app.fetch_binance_data.LAST_RUN_FILE", file_path):
        save_end_time(test_time)
    
    mock_open.assert_called_once()
    
@patch("builtins.open", new_callable=MagicMock)
def test_get_last_end_time(mock_open, temp_dir):
    mock_open.return_value.__enter__.return_value.read.return_value = str(int(datetime.utcnow().timestamp() * 1000))
    file_path = os.path.join(temp_dir, "last_run.txt")
    
    with patch("app.fetch_binance_data.LAST_RUN_FILE", file_path):
        last_time = get_last_end_time()
    
    assert isinstance(last_time, datetime)

@patch("app.fetch_binance_data.pl.DataFrame.to_arrow", side_effect=lambda: pa.Table.from_arrays(
    [
        pa.array([1700000000000, 1700000300000], pa.int64()),
        pa.array(["100", "105"], pa.string()),
        pa.array(["110", "115"], pa.string()),
        pa.array(["90", "95"], pa.string()),
        pa.array(["105", "110"], pa.string()),
        pa.array(["1000", "2000"], pa.string()),
        pa.array([1700000300000, 1700000600000], pa.int64()),
        pa.array(["10000", "20000"], pa.string()),
        pa.array([500, 600], pa.int64()),
        pa.array(["500", "600"], pa.string()),
        pa.array(["5000", "6000"], pa.string()),
        pa.array(["0", "0"], pa.string()),
    ],
    names=[
        "Open Time", "Open", "High", "Low", "Close", "Volume",
        "Close Time", "Quote Asset Volume", "Number of Trades",
        "Taker Buy Base Asset Volume", "Taker Buy Quote Asset Volume", "Ignore"
    ]
))
def test_save_to_parquet(mock_to_arrow, temp_dir):
    klines = mock_binance_klines()
    save_to_parquet("BTCUSDT", klines, temp_dir)
    parquet_file = os.path.join(temp_dir, "BTCUSDT.parquet")
    
    # Check if the file exists
    assert os.path.exists(parquet_file)

    # Verify that the written file is a valid Parquet file
    table = pq.read_table(parquet_file)
    assert table.num_rows == 2
    assert table.column_names == [
        "Open Time", "Open", "High", "Low", "Close", "Volume",
        "Close Time", "Quote Asset Volume", "Number of Trades",
        "Taker Buy Base Asset Volume", "Taker Buy Quote Asset Volume", "Ignore"
    ]

@patch("csv.writer")
def test_save_to_csv(mock_csv_writer, temp_dir):
    klines = mock_binance_klines()
    save_to_csv("BTCUSDT", klines, temp_dir)
    csv_file = os.path.join(temp_dir, "BTCUSDT.csv")
    assert os.path.exists(csv_file) or mock_csv_writer.called
