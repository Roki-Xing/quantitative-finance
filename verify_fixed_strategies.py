#!/usr/bin/env python3
"""Verify the 2 manually fixed strategies"""
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

# Test both strategies
data_file = "/root/autodl-tmp/eoh/backtest_data_extended/stock_sh_600519.csv"

print("="*80)
print("策略验证测试")
print("="*80)
now = datetime.now()
print(f"测试数据: 贵州茅台 (600519)")
print(f"时间: {now.year}-{now.month:02d}-{now.day:02d} {now.hour:02d}:{now.minute:02d}:{now.second:02d}")
print("="*80)

strategies = [
    ("/root/autodl-tmp/eoh/experiment4_trading_extended/baseline/strategy_001.py", "strategy_001"),
    ("/root/autodl-tmp/eoh/experiment4_trading_extended/baseline/strategy_002.py", "strategy_002"),
    ("/root/autodl-tmp/eoh/experiment4_trading_extended/baseline/strategy_003.py", "strategy_003"),
    ("/root/autodl-tmp/eoh/experiment4_trading_extended/baseline/strategy_004.py", "strategy_004"),
    ("/root/autodl-tmp/eoh/experiment4_trading_extended/baseline/strategy_005.py", "strategy_005"),
    ("/root/autodl-tmp/eoh/experiment4_trading_extended/baseline/strategy_006.py", "strategy_006"),
    ("/root/autodl-tmp/eoh/experiment4_trading_extended/baseline/strategy_008.py", "strategy_008"),
    ("/root/autodl-tmp/eoh/experiment4_trading_extended/baseline/strategy_009.py", "strategy_009"),
    ("/root/autodl-tmp/eoh/experiment4_trading_extended/baseline/strategy_010.py", "strategy_010"),
    ("/root/autodl-tmp/eoh/experiment4_trading_extended/baseline/strategy_011.py", "strategy_011"),
    ("/root/autodl-tmp/eoh/experiment4_trading_extended/baseline/strategy_012.py", "strategy_012"),
    ("/root/autodl-tmp/eoh/experiment4_trading_extended/baseline/strategy_015.py", "strategy_015"),
    ("/root/autodl-tmp/eoh/experiment4_trading_extended/baseline/strategy_022.py", "strategy_022")
]

for strat_file, name in strategies:
    print(f"\n[{name}]")
    print("-"*80)
    result = test_strategy(strat_file, data_file)

    if result.get("success"):
        print(f"✅ 回测成功")
        print(f"   初始资金: {result['initial']:,.0f}")
        print(f"   最终资金: {result['final']:,.0f}")
        print(f"   收益率: {result['return_pct']:.2f}%")
    else:
        print(f"❌ 回测失败")
        print(f"   错误: {result.get('error', 'Unknown')}")

print("\n" + "="*80)
print("验证完成")
print("="*80)
