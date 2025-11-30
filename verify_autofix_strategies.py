#!/usr/bin/env python3
"""验证Experiment 5自动修复的17个策略"""
import backtrader as bt
import pandas as pd
from pathlib import Path
import sys
import importlib.util
from datetime import datetime

def test_strategy(strategy_file, data_file):
    try:
        # Load data
        df = pd.read_csv(data_file)
        df["date"] = pd.to_datetime(df["date"])
        df.set_index("date", inplace=True)

        # Load strategy
        spec = importlib.util.spec_from_file_location("strategy", strategy_file)
        module = importlib.util.module_from_spec(spec)
        sys.modules["strategy"] = module
        spec.loader.exec_module(module)

        strategy_class = None
        for name in dir(module):
            obj = getattr(module, name)
            if isinstance(obj, type) and issubclass(obj, bt.Strategy) and obj != bt.Strategy:
                strategy_class = obj
                break

        if not strategy_class:
            return {"error": "No strategy class found"}

        # Run backtest
        cerebro = bt.Cerebro()
        cerebro.addstrategy(strategy_class)
        data = bt.feeds.PandasData(dataname=df[["open", "high", "low", "close", "volume"]])
        cerebro.adddata(data)
        cerebro.broker.setcash(100000.0)
        cerebro.broker.setcommission(commission=0.001)

        initial = cerebro.broker.getvalue()
        results = cerebro.run()
        final = cerebro.broker.getvalue()

        return {
            "success": True,
            "initial": initial,
            "final": final,
            "return_pct": (final - initial) / initial * 100
        }
    except Exception as e:
        return {"success": False, "error": str(e)}

# Test autofix strategies
data_file = "/root/autodl-tmp/eoh/backtest_data_extended/stock_sh_600519.csv"

print("="*80)
print("自动修复策略验证测试")
print("="*80)
now = datetime.now()
print(f"测试数据: 贵州茅台 (600519)")
print(f"时间: {now.year}-{now.month:02d}-{now.day:02d} {now.hour:02d}:{now.minute:02d}:{now.second:02d}")
print("="*80)

autofix_strategies = [
    7, 13, 14, 16, 17, 18, 19, 20, 21, 23, 24, 25, 26, 27, 28, 29, 30
]

success_count = 0
failed_count = 0

for idx in autofix_strategies:
    strategy_file = f"/root/autodl-tmp/eoh/experiment5_autofix/strategy_{idx:03d}_autofix.py"

    print(f"\n[strategy_{idx:03d}]")
    print("-"*80)
    result = test_strategy(strategy_file, data_file)

    if result.get("success"):
        print(f"✅ 回测成功")
        print(f"   初始资金: {result['initial']:,.0f}")
        print(f"   最终资金: {result['final']:,.0f}")
        print(f"   收益率: {result['return_pct']:.2f}%")
        success_count += 1
    else:
        print(f"❌ 回测失败")
        print(f"   错误: {result.get('error', 'Unknown')[:200]}")
        failed_count += 1

print("\n" + "="*80)
print("验证完成")
print("="*80)
print(f"成功: {success_count}/17 ({success_count/17*100:.1f}%)")
print(f"失败: {failed_count}/17 ({failed_count/17*100:.1f}%)")
print("="*80)
