# FlatTrade: Delivery & Intraday Trading Bot

FlatTrade is an automated trading bot designed for both delivery and intraday trading strategies. This repository leverages advanced algorithms and APIs to execute trades with efficiency and accuracy. The bot integrates seamlessly with financial APIs and includes robust error handling and data logging mechanisms.

---

## Features

- **Dual Trading Modes:** Supports both delivery and intraday trading.
- **Configurable Strategies:** Customize trading strategies based on user-defined parameters.
- **API Integration:** Connects to brokerage APIs for real-time data and trade execution.
- **Data Logging:** Comprehensive logging for trades, errors, and performance metrics.
- **Real-Time Notifications:** Alerts for significant events and trade outcomes.
- **Backtesting:** Historical data analysis to evaluate trading strategies.
- **Robust Error Handling:** Ensures stability and reliability.

---

## Repository Structure

### **1. Modules and Scripts**

#### **`main.py`**
The entry point of the application. It orchestrates the bot's workflow by initializing configurations, modules, and triggering the trading logic.

- **Functions:**
  - `initialize_bot()`: Loads configurations and initializes modules.
  - `start_trading()`: Starts the trading process based on the selected mode.

#### **`config.py`**
Manages all configuration settings required by the bot.

- **Features:**
  - API keys and secrets.
  - Trading preferences (e.g., risk levels, maximum loss).
  - Logging configurations.

#### **`api_handler.py`**
Handles interactions with the brokerage APIs.

- **Functions:**
  - `fetch_market_data()`: Retrieves real-time market data.
  - `place_order(order_details)`: Places trades.
  - `cancel_order(order_id)`: Cancels pending orders.

#### **`strategy.py`**
Defines the trading strategies for both delivery and intraday modes.

- **Functions:**
  - `delivery_strategy(data)`: Logic for delivery trading.
  - `intraday_strategy(data)`: Logic for intraday trading.

#### **`logger.py`**
Provides robust logging capabilities to track the bot's activity.

- **Functions:**
  - `log_trade(trade_details)`: Logs executed trades.
  - `log_error(error_message)`: Logs errors for debugging.
  - `log_info(message)`: General logging for informational purposes.

#### **`notifier.py`**
Sends real-time notifications for trade alerts, errors, and updates.

- **Functions:**
  - `send_email(subject, body)`: Sends email alerts.
  - `send_sms(message)`: Sends SMS alerts.
  - `send_push_notification(title, message)`: Push notifications.

#### **`backtester.py`**
Enables users to test trading strategies on historical data.

- **Functions:**
  - `run_backtest(strategy, data)`: Simulates a strategy on past data and generates a performance report.

#### **`utils.py`**
Utility functions for common tasks used across modules.

- **Functions:**
  - `calculate_risk(reward, risk)`: Risk-reward analysis.
  - `format_data(raw_data)`: Prepares raw data for analysis.
  - `get_current_time()`: Returns the current timestamp.

---

### **2. Directory Structure**
```plaintext
FlatTrade-Delivery-Intraday-Trading-Bot/
├── main.py
├── config.py
├── api_handler.py
├── strategy.py
├── logger.py
├── notifier.py
├── backtester.py
├── utils.py
├── data/
│   ├── historical_data.csv
│   └── logs/
│       ├── trade_log.txt
│       └── error_log.txt
└── tests/
    ├── test_strategy.py
    ├── test_api_handler.py
    └── test_notifier.py
```

---

## Installation

### Prerequisites
- Python 3.8+
- pip (Python package installer)
- An account with a supported brokerage API (e.g., Zerodha, Alpaca).

### Steps
1. Clone the repository:
   ```bash
   git clone https://github.com/Mukesh-Kumar-Madhur/FlatTrade-Delivery-Intraday-Trading-Bot.git
   cd FlatTrade-Delivery-Intraday-Trading-Bot
   ```

2. Install required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Configure the bot:
   - Update `config.py` with your API credentials and trading preferences.

4. Run the bot:
   ```bash
   python main.py
   ```

---

## Usage

1. **Select Trading Mode:**
   - Delivery or Intraday mode is selected based on user input in the CLI or configuration file.

2. **Backtest Strategies:**
   - Use `backtester.py` to evaluate strategies before live trading:
     ```bash
     python backtester.py --strategy delivery --data data/historical_data.csv
     ```

3. **Monitor Logs:**
   - Check `data/logs/` for trade and error logs.

4. **Notifications:**
   - Ensure notification methods are configured in `notifier.py`.

---

## Testing

Unit tests are provided in the `tests/` directory to validate each module:
```bash
pytest tests/
```

---

## Contribution Guidelines

We welcome contributions! Please follow these steps:

1. Fork the repository.
2. Create a new branch for your feature/fix.
3. Commit changes with clear messages.
4. Create a pull request for review.

---

## License

This project is licensed under the [Mozilla Public License 2.0](https://mozilla.org/MPL/2.0/).

---

## Author
This project was created and maintained by Mukesh Kumar Madhur.

GitHub: Mukesh-Kumar-Madhur
Email: Solutioneyes.ai@gmail.com

---
