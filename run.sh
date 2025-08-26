#!/bin/bash
cd "$(dirname "$0")"

python3 -m venv venv
source venv/bin/activate


pkill -f crypto_volume_strategy.py
pkill -f bist_volume_strategy.py
pkill -f usstock_volume_strategy.py
pkill -f crypto_volume_strategy_ema8.py

sync
sync
sync

nohup python crypto_volume_strategy.py > crypto_output.log 2>&1 &
nohup python bist_volume_strategy.py > bist_output.log 2>&1 &
nohup python usstock_volume_strategy.py > usstock_output.log 2>&1 &
nohup python crypto_volume_strategy_ema8.py > crypto2_output.log 2>&1 &