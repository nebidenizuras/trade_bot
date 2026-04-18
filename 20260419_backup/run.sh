#!/bin/bash
cd "$(dirname "$0")"

python3 -m venv venv
source venv/bin/activate

nohup python scan_strategy_test.py > crypto_test_output.log 2>&1 &
nohup python scan_strategy_crypto.py > crypto_output.log 2>&1 &
nohup python scan_strategy_bist.py > bist_output.log 2>&1 &
nohup python scan_strategy_usstock.py > usstock_output.log 2>&1 &