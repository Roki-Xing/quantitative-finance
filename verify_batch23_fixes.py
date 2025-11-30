#!/usr/bin/env python3
"""验证batch 2+3共8个新修复策略"""
import backtrader as bt
import pandas as pd
from pathlib import Path
import sys
import importlib.util
from datetime import datetime

def test_strategy(strategy_file, data_file):
    try:
        df = pd.read_csv(data_file)
        df["date"] = pd.to_datetime(df["date"])
        df.set_index("date", inplace=True)

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

data_file = "/root/autodl-tmp/eoh/backtest_data_extended/stock_sh_600519.csv"

print("="*80)
print("新修复策略验证测试 (Batch 2+3)")
print("="*80)
now = datetime.now()
print(f"测试数据: 贵州茅台 (600519)")
print(f"时间: {now.year}-{now.month:02d}-{now.day:02d} {now.hour:02d}:{now.minute:02d}:{now.second:02d}")
print("="*80)

new_fixes = [13, 17, 19, 23, 24, 25, 26, 28]
fix_dir = "/root/autodl-tmp/eoh/manual_fix/baseline"

success_count = 0
failed_count = 0

for idx in new_fixes:
    strategy_file = f"{fix_dir}/strategy_{idx:03d}_fixed.py"

    print(f"\n[strategy_{idx:03d}_fixed]")
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
print(f"成功: {success_count}/8 ({success_count/8*100:.1f}%)")
print(f"失败: {failed_count}/8 ({failed_count/8*100:.1f}%)")
print("="*80)

if success_count == 8:
    print("\n🎉 所有新修复策略通过测试!")
    print("最终baseline可运行率: 30/30 (100%)")
    print("Experiment 5完成!")
elif success_count > 0:
    print(f"\n✅ {success_count}个策略通过")
    print(f"当前baseline可运行率: {29 + success_count}/30 ({(29 + success_count)/30*100:.1f}%)")
