#!/usr/bin/env python3
"""Day 42: Batch Backtest - Fixed version"""
import backtrader as bt
import pandas as pd
from pathlib import Path
import json
from datetime import datetime
import importlib.util
import sys
import logging

logging.disable(logging.CRITICAL)  # Suppress strategy logs

STRAT_DIR = Path("/root/autodl-tmp/eoh/strategy_library/batch1")
DATA_DIR = Path("/root/autodl-tmp/eoh/backtest_data")
RESULTS_DIR = Path("/root/autodl-tmp/eoh/backtest_results/batch1")
RESULTS_DIR.mkdir(parents=True, exist_ok=True)

print("="*60)
print("DAY 42: BATCH BACKTEST")
print("="*60)

# Load data
df = pd.read_csv(DATA_DIR / "000001.csv")
df["日期"] = pd.to_datetime(df["日期"])
df.set_index("日期", inplace=True)
df = df.rename(columns={"开盘":"open", "收盘":"close", "最高":"high", "最低":"low", "成交量":"volume"})
df = df[["open", "high", "low", "close", "volume"]]
print(f"Data: {len(df)} bars ({df.index[0].date()} ~ {df.index[-1].date()})")

def run_backtest(strategy_file):
    try:
        spec = importlib.util.spec_from_file_location("strategy", strategy_file)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        strategy_class = None
        for name in dir(module):
            obj = getattr(module, name)
            if isinstance(obj, type) and issubclass(obj, bt.Strategy) and obj != bt.Strategy:
                strategy_class = obj
                break

        if not strategy_class:
            return {"status": "FAILED", "error": "No class"}

        cerebro = bt.Cerebro(stdstats=False)
        cerebro.addstrategy(strategy_class)
        data = bt.feeds.PandasData(dataname=df)
        cerebro.adddata(data)
        cerebro.broker.setcash(100000.0)
        cerebro.broker.setcommission(commission=0.001)

        cerebro.addanalyzer(bt.analyzers.SharpeRatio, _name="sharpe", riskfreerate=0.02)
        cerebro.addanalyzer(bt.analyzers.DrawDown, _name="drawdown")
        cerebro.addanalyzer(bt.analyzers.TradeAnalyzer, _name="trades")

        initial = cerebro.broker.getvalue()
        results = cerebro.run()
        final = cerebro.broker.getvalue()
        strat = results[0]

        sharpe = strat.analyzers.sharpe.get_analysis().get("sharperatio") or 0
        maxdd = strat.analyzers.drawdown.get_analysis().get("max", {}).get("drawdown", 0)
        trades = strat.analyzers.trades.get_analysis().get("total", {}).get("total", 0)

        return {
            "status": "SUCCESS",
            "class": strategy_class.__name__,
            "final": round(final, 2),
            "return_pct": round((final - initial) / initial * 100, 2),
            "sharpe": round(sharpe, 4),
            "max_dd": round(maxdd, 2),
            "trades": trades
        }
    except Exception as e:
        return {"status": "FAILED", "error": str(e)[:80]}

# Run backtests
results = []
for sf in sorted(STRAT_DIR.glob("*.py")):
    print(f"\n[{sf.stem}]")
    r = run_backtest(sf)
    r["strategy"] = sf.stem
    results.append(r)
    if r["status"] == "SUCCESS":
        print(f"  Return: {r['return_pct']:>7.2f}% | Sharpe: {r['sharpe']:>7.4f} | MaxDD: {r['max_dd']:>6.2f}% | Trades: {r['trades']}")
    else:
        print(f"  FAILED: {r.get('error', 'Unknown')}")

# Save
with open(RESULTS_DIR / "backtest_results.json", "w") as f:
    json.dump({"date": datetime.now().isoformat(), "data": "000001.SZ", "results": results}, f, indent=2)

# Summary
print("\n" + "="*60)
print("SUMMARY")
print("="*60)
success = [r for r in results if r["status"] == "SUCCESS"]
print(f"Success: {len(success)}/{len(results)}")

if success:
    avg_ret = sum(r["return_pct"] for r in success) / len(success)
    avg_sharpe = sum(r["sharpe"] for r in success) / len(success)
    best = max(success, key=lambda x: x["sharpe"])
    worst = min(success, key=lambda x: x["sharpe"])
    print(f"Avg Return: {avg_ret:.2f}%")
    print(f"Avg Sharpe: {avg_sharpe:.4f}")
    print(f"Best:  {best['strategy']} (Sharpe={best['sharpe']:.4f})")
    print(f"Worst: {worst['strategy']} (Sharpe={worst['sharpe']:.4f})")

print(f"\nResults saved: {RESULTS_DIR / 'backtest_results.json'}")
