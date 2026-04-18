# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

A Telegram-based technical analysis bot that scans multiple markets (Binance Futures crypto, BIST Turkish stocks, US stocks) and sends buy/sell signal alerts to Telegram channels.

## Setup

```bash
pip install ta python-binance pandas requests mplfinance plotly cufflinks tqdm pandas-ta schedule ccxt pysimplesoap yfinance
```

## Running

Start all scanners in background (Linux/Mac):
```bash
bash run.sh
```

Run a single scanner:
```bash
python scan_strategy_crypto.py
python scan_strategy_bist.py
python scan_strategy_usstock.py
python scan_strategy_test.py   # test/sandbox — outputs to channel_06
```

Logs are written to `*_output.log` files when started via `run.sh`.

## Architecture

### Entry Points (one process each)
| File | Market | Data Source | Timeframes |
|---|---|---|---|
| `scan_strategy_crypto.py` | Binance Futures (USDT pairs) | python-binance | 4h, 1d |
| `scan_strategy_bist.py` | BIST (Turkish stocks) | yfinance | 1d |
| `scan_strategy_usstock.py` | US stocks (S&P 500 universe) | yfinance | 1d |
| `scan_strategy_test.py` | Binance Futures | python-binance | 15m, 1h |

Each script is self-contained and runs its own `scheduler_loop()` with an infinite `while True / time.sleep(30)` polling loop.

### Shared Infrastructure
- **`telegram_bot.py`** — all Telegram dispatch. Exposes `send_message_to_telegram(channelID, message)` and channel name constants (`channel_00` … `channel_07`). Each channel maps to a specific market/timeframe (e.g. `channel_00` = CRYPTO-1D, `channel_04` = BIST-1D).
- **`user_api_key.py`** — Binance API keys used by `data_manager.py` (`key_id`, `secret_key_id`).
- **`data_manager.py`** — reusable Binance utilities (historical data download, symbol lists, wallet info, price/precision helpers). Not used by the live scanners directly.

### Signal Logic

**Crypto (score-based, 0–9+ points):**  
`get_score()` in `scan_strategy_crypto.py` / `scan_strategy_test.py`:
- Mandatory for long: close > EMA8, bullish candle, body ≥ 0.75%
- Bonus points: volume increasing last 2 candles, prior candles below EMA8, body > 3%
- Volume filter: 1h requires close×volume ≥ $9M; 15m requires ≥ $2.5M
- Parallel execution via `ThreadPoolExecutor(max_workers=15)`
- Top 20 results sorted by (score, volume_value) sent to Telegram

**BIST / US Stocks (binary signal):**  
`is_long_signal()`: previous close ≤ EMA8 AND current close > EMA8 AND volume increased ≥ 10% AND bullish candle. Top 20 by volume sent.

### API Keys
- `scan_strategy_crypto.py` and `scan_strategy_test.py` have inline empty `API_KEY`/`API_SECRET` strings — fill these directly in the file.
- `data_manager.py` reads from `user_api_key.py`.
- `telegram_bot.py` has the bot token and channel IDs hardcoded.

### Scheduler Trigger Times (UTC)
- Crypto 4h: minute 59, hours 23/3/7/11/15/19
- Crypto 1d: 23:58
- BIST 1d: 14:45
- US Stock 1d: 20:55
- Test 15m: minutes 14/29/44/59; Test 1h: minute 58
