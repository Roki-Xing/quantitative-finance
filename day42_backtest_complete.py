#!/usr/bin/env python3
"""
Day 42: Complete Backtest Solution
Downloads data and runs batch backtest on all 10 strategies
"""

import subprocess
import sys
import os
from pathlib import Path
from datetime import datetime
import json

# Paths
DATA_DIR = Path("/root/autodl-tmp/eoh/backtest_data")
STRATEGY_DIR = Path("/root/autodl-tmp/eoh/strategy_library/batch1")
RESULTS_DIR = Path("/root/autodl-tmp/eoh/backtest_results/batch1")

print("=" * 80)
print("DAY 42: COMPLETE BACKTEST SOLUTION")
print("=" * 80)
print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print()

# Step 1: Install akshare
print("[STEP 1] Installing akshare...")
try:
    subprocess.check_call([sys.executable, "-m", "pip", "install", "akshare", "-q"])
    import akshare as ak
    print("akshare installed successfully")
except Exception as e:
    print(f"akshare install failed: {e}")
    sys.exit(1)

# Step 2: Download A-share data
print("\n[STEP 2] Downloading A-share data...")
DATA_DIR.mkdir(parents=True, exist_ok=True)

symbols = {
    "000001": "平安银行",
    "000002": "万科A",
    "000300": "沪深300ETF"
}

for sym, name in symbols.items():
    try:
        print(f"  Downloading {sym} ({name})...")
        df = ak.stock_zh_a_hist(symbol=sym, period="daily",
                                 start_date="20200101", end_date="20251122", adjust="qfq")

        # Rename columns for backtrader
        df.columns = ['Date', 'Open', 'Close', 'High', 'Low', 'Volume', 'Amount', 'Amplitude', 'PctChange', 'Change', 'Turnover']
        df = df[['Date', 'Open', 'High', 'Low', 'Close', 'Volume']]
        df.to_csv(DATA_DIR / f"{sym}.csv", index=False)
        print(f"    {sym}: {len(df)} bars saved")
    except Exception as e:
        print(f"    {sym} failed: {e}")

# Check data files
data_files = list(DATA_DIR.glob("*.csv"))
print(f"\nData files available: {len(data_files)}")
if not data_files:
    print("ERROR: No data files available!")
    sys.exit(1)

# Step 3: Import backtrader and run backtests
print("\n[STEP 3] Running backtests...")
import backtrader as bt
import pandas as pd

RESULTS_DIR.mkdir(parents=True, exist_ok=True)

# Load strategy classes dynamically
strategy_files = sorted(STRATEGY_DIR.glob("*.py"))
print(f"Found {len(strategy_files)} strategy files")

results = []

for strategy_file in strategy_files:
    strategy_name = strategy_file.stem
    print(f"\n--- Testing: {strategy_name} ---")

    try:
        # Load strategy module
        import importlib.util
        spec = importlib.util.spec_from_file_location(strategy_name, strategy_file)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        # Find strategy class
        strategy_class = None
        for attr_name in dir(module):
            attr = getattr(module, attr_name)
            if isinstance(attr, type) and issubclass(attr, bt.Strategy) and attr != bt.Strategy:
                strategy_class = attr
                break

        if not strategy_class:
            print(f"  No strategy class found in {strategy_name}")
            continue

        print(f"  Strategy class: {strategy_class.__name__}")

        # Run on first available data file
        data_file = data_files[0]

        # Create cerebro
        cerebro = bt.Cerebro()
        cerebro.addstrategy(strategy_class)

        # Load data
        df = pd.read_csv(data_file)
        df['Date'] = pd.to_datetime(df['Date'])
        df.set_index('Date', inplace=True)

        data = bt.feeds.PandasData(dataname=df)
        cerebro.adddata(data)

        # Broker settings
        cerebro.broker.setcash(100000.0)
        cerebro.broker.setcommission(commission=0.001)

        # Analyzers
        cerebro.addanalyzer(bt.analyzers.SharpeRatio, _name='sharpe', riskfreerate=0.02)
        cerebro.addanalyzer(bt.analyzers.DrawDown, _name='drawdown')
        cerebro.addanalyzer(bt.analyzers.Returns, _name='returns')
        cerebro.addanalyzer(bt.analyzers.TradeAnalyzer, _name='trades')

        # Run
        initial = cerebro.broker.getvalue()
        strats = cerebro.run()
        final = cerebro.broker.getvalue()
        strat = strats[0]

        # Extract metrics
        sharpe = strat.analyzers.sharpe.get_analysis()
        drawdown = strat.analyzers.drawdown.get_analysis()
        returns = strat.analyzers.returns.get_analysis()
        trades = strat.analyzers.trades.get_analysis()

        total_return = (final - initial) / initial * 100
        sharpe_ratio = sharpe.get('sharperatio', None)
        max_dd = drawdown.get('max', {}).get('drawdown', 0)
        total_trades = trades.get('total', {}).get('total', 0)

        result = {
            "strategy": strategy_name,
            "class": strategy_class.__name__,
            "initial_value": initial,
            "final_value": round(final, 2),
            "total_return_pct": round(total_return, 2),
            "sharpe_ratio": round(sharpe_ratio, 4) if sharpe_ratio else None,
            "max_drawdown_pct": round(max_dd, 2),
            "total_trades": total_trades,
            "status": "SUCCESS"
        }

        print(f"  Return: {total_return:.2f}%")
        print(f"  Sharpe: {sharpe_ratio:.4f}" if sharpe_ratio else "  Sharpe: N/A")
        print(f"  MaxDD: {max_dd:.2f}%")
        print(f"  Trades: {total_trades}")

    except Exception as e:
        print(f"  ERROR: {e}")
        import traceback
        traceback.print_exc()
        result = {
            "strategy": strategy_name,
            "status": "FAILED",
            "error": str(e)
        }

    results.append(result)

# Step 4: Save results
print("\n[STEP 4] Saving results...")

output = {
    "experiment": "Day 42 Batch Backtest",
    "date": datetime.now().isoformat(),
    "data_file": str(data_files[0]),
    "total_strategies": len(strategy_files),
    "successful": sum(1 for r in results if r.get("status") == "SUCCESS"),
    "failed": sum(1 for r in results if r.get("status") == "FAILED"),
    "results": results
}

output_file = RESULTS_DIR / "backtest_results.json"
with open(output_file, 'w') as f:
    json.dump(output, f, indent=2, ensure_ascii=False)

print(f"Results saved to: {output_file}")

# Summary
print("\n" + "=" * 80)
print("BACKTEST SUMMARY")
print("=" * 80)

successful = [r for r in results if r.get("status") == "SUCCESS"]
print(f"Total strategies: {len(results)}")
print(f"Successful: {len(successful)}")
print(f"Failed: {len(results) - len(successful)}")

if successful:
    print("\nPerformance Ranking (by Sharpe Ratio):")
    ranked = sorted([r for r in successful if r.get("sharpe_ratio")],
                    key=lambda x: x.get("sharpe_ratio", -999), reverse=True)
    for i, r in enumerate(ranked, 1):
        print(f"  {i}. {r['strategy']}: Sharpe={r.get('sharpe_ratio', 'N/A')}, "
              f"Return={r.get('total_return_pct', 0):.1f}%, MaxDD={r.get('max_drawdown_pct', 0):.1f}%")

print("\n" + "=" * 80)
print("DAY 42 BACKTEST COMPLETE")
print("=" * 80)
