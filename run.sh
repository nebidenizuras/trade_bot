#!/bin/bash
cd "$(dirname "$0")"

python3 -m venv venv
source venv/bin/activate

nohup python crypto_strategy_test.py > crypto_test_output.log 2>&1 &
nohup python crypto_strategy.py > crypto_output.log 2>&1 &
nohup python bist_strategy.py > bist_output.log 2>&1 &
nohup python usstock_strategy.py > usstock_output.log 2>&1 &