# Binance Data Exporter

This project fetches **historical Kline (candlestick) data** from the **Binance API** and stores it in **CSV and Parquet formats**.  
It features **automatic resumption**, **unit tests**, and **Docker support** for easy deployment.

---

## Features
- Fetches **historical Kline (candlestick) data** from Binance  
- Supports multiple **Kline intervals** (e.g., 1m, 5m, 30m, 1h, 1d)  
- Saves data in **CSV** and **Parquet** formats  
- Automatically **resumes downloads** from the last saved timestamp  
- **Mocked unit tests** – No real API calls required  
- **Dockerized** for easy deployment  

---

## Project Setup

### 1. Clone the Repository
```bash
git clone https://github.com/omega1119/binance-exporter.git
cd binance-exporter
```

### 2. Create a Virtual Environment (Optional)
```bash
python3 -m venv venv
source venv/bin/activate  # macOS/Linux
venv\Scripts\activate  # Windows
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

---

## Configuration
### Set Up API Keys

Modify `myconfig.py`:
```python
BINANCE_API_KEY = "your_api_key_here"
BINANCE_API_SECRET = "your_api_secret_here"
```

---

## Usage
### **Run the Binance Data Exporter**
```bash
python app/fetch_binance_data.py
```
This will:
- Fetch historical Binance Kline data  
- Save it in **CSV and Parquet**  
- Store files in `data/{timestamp}/`  

---

## Docker Deployment
### 1. Build the Docker Image
```bash
chmod +x run.sh
chmod +x manage.sh

./scripts/run.sh
```

### 2. Run the Container
```bash
./scripts/manage.sh start
```

### 3. Stop the Container
```bash
./scripts/manage.sh stop
```

### 4. Other
```bash
./scripts/manage.sh logs

./scripts/manage.sh remove
```

---

## Running Unit Tests
### Run All Tests
```bash
pytest
```

### Run Tests with Detailed Output
```bash
pytest -v
```

- **Tests use mocked Binance API** – No real API calls are made  
- **Temp directories ensure clean file handling**  

---

## Project Structure
```bash
brew install tree  # Install tree (if not already installed)
tree -a -I "venv|node_modules|__pycache__|.git"
```

```
├── .gitignore
├── README.md
├── app
│   ├── __init__.py
│   ├── config
│   │   └── myconfig_template.py
│   ├── data
│   ├── fetch_binance_data.py
│   ├── last_run.txt
│   ├── logs
│   └── tests
│       └── test_fetch_binance_data.py
├── docker
│   ├── Dockerfile
│   ├── docker-compose.yml
│   └── requirements.txt
├── pytest.ini
└── scripts
    ├── manage.sh
    └── run.sh
```

---

## Troubleshooting
### `ModuleNotFoundError: No module named 'app'`
Run tests from the **project root**:
```bash
pytest
```

### `binance.client.BinanceAPIException: Invalid API-key`
- **Double-check your API keys in `.env` or `config.py`**  
- **Ensure your Binance account has API permissions enabled**  

---

## 👨‍💻 **Contributing**
1. **Fork** the repository  
2. **Create a feature branch** (`git checkout -b feature-name`)  
3. **Commit your changes** (`git commit -m "Added new feature"`)  
4. **Push to your fork** (`git push origin feature-name`)  
5. **Create a Pull Request**

---

## License
This project is licensed under the **MIT License**.  

---

## Need Help?
If you run into any issues, feel free to:
- **Create a GitHub Issue**

Happy Trading.

