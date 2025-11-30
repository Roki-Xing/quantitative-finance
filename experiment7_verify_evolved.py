#!/usr/bin/env python3
"""
Experiment 7: 验证并回测5个演化策略
"""
import backtrader as bt
import pandas as pd
from pathlib import Path
import sys
import importlib.util
from datetime import datetime
import json

# 配置
EVOLVED_DIR = Path("/root/autodl-tmp/eoh/experiment7_evolved_strategies")
DATA_FILE = Path("/root/autodl-tmp/eoh/backtest_data_extended/stock_sh_600519.csv")
RESULTS_DIR = Path("/root/autodl-tmp/eoh/experiment7_evolved_strategies")

# 演化策略列表
EVOLVED_STRATEGIES = [
    "mutation1_optimize_007",
    "mutation2_enhance_022",
    "crossover1_position_atr",
    "crossover2_ma_breakout",
    "innovation_triple_fusion"
]

def load_strategy_class(strategy_file):
    """动态加载策略类"""
    try:
        if "strategy" in sys.modules:
            del sys.modules["strategy"]

        spec = importlib.util.spec_from_file_location("strategy", strategy_file)
        module = importlib.util.module_from_spec(spec)
        sys.modules["strategy"] = module
        spec.loader.exec_module(module)

        for name in dir(module):
            obj = getattr(module, name)
            if isinstance(obj, type) and issubclass(obj, bt.Strategy) and obj != bt.Strategy:
                return obj
        return None
    except Exception as e:
        return None

def run_backtest(strategy_class, data_file, strategy_name):
    """运行单个策略回测"""
    try:
        df = pd.read_csv(data_file)
        df["date"] = pd.to_datetime(df["date"])
        df.set_index("date", inplace=True)

        cerebro = bt.Cerebro()
        cerebro.addstrategy(strategy_class)
        data = bt.feeds.PandasData(dataname=df[["open", "high", "low", "close", "volume"]])
        cerebro.adddata(data)
        cerebro.broker.setcash(100000.0)
        cerebro.broker.setcommission(commission=0.001)

        cerebro.addanalyzer(bt.analyzers.SharpeRatio, _name='sharpe')
        cerebro.addanalyzer(bt.analyzers.DrawDown, _name='drawdown')
        cerebro.addanalyzer(bt.analyzers.TradeAnalyzer, _name='trades')
        cerebro.addanalyzer(bt.analyzers.Returns, _name='returns')

        initial = cerebro.broker.getvalue()
        results = cerebro.run()
        final = cerebro.broker.getvalue()

        strat = results[0]
        sharpe = strat.analyzers.sharpe.get_analysis()
        dd = strat.analyzers.drawdown.get_analysis()
        trades = strat.analyzers.trades.get_analysis()

        return {
            "success": True,
            "initial": initial,
            "final": final,
            "return_pct": (final - initial) / initial * 100,
            "sharpe": sharpe.get('sharperatio', None),
            "max_drawdown": dd.get('max', {}).get('drawdown', 0),
            "total_trades": trades.get('total', {}).get('total', 0),
            "win_rate": trades.get('won', {}).get('total', 0) / trades.get('total', {}).get('total', 1) * 100 if trades.get('total', {}).get('total', 0) > 0 else 0,
        }
    except Exception as e:
        return {"success": False, "error": str(e)[:200]}

def main():
    print("=" * 80)
    print("Experiment 7: 演化策略验证与回测")
    print("=" * 80)
    print(f"时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"测试数据: 贵州茅台 (600519)")
    print("=" * 80)

    all_results = []

    for strategy_name in EVOLVED_STRATEGIES:
        strategy_file = EVOLVED_DIR / f"{strategy_name}.py"

        print(f"\n[{strategy_name}]")
        print("-" * 80)

        if not strategy_file.exists():
            print(f"  ❌ 文件不存在")
            all_results.append({
                "strategy": strategy_name,
                "success": False,
                "error": "File not found"
            })
            continue

        # 加载策略类
        strategy_class = load_strategy_class(strategy_file)
        if not strategy_class:
            print(f"  ❌ 无法加载策略类")
            all_results.append({
                "strategy": strategy_name,
                "success": False,
                "error": "Failed to load strategy class"
            })
            continue

        # 运行回测
        result = run_backtest(strategy_class, DATA_FILE, strategy_name)
        result["strategy"] = strategy_name
        all_results.append(result)

        if result.get("success"):
            print(f"  ✅ 回测成功")
            print(f"     收益率: {result['return_pct']:.2f}%")
            print(f"     Sharpe: {result.get('sharpe', 'N/A')}")
            print(f"     最大回撤: {result['max_drawdown']:.2f}%")
            print(f"     交易次数: {result['total_trades']}")
        else:
            print(f"  ❌ 回测失败: {result.get('error', 'Unknown')[:100]}")

    # 保存结果
    results_file = RESULTS_DIR / "evolved_backtest_results.json"
    with open(results_file, 'w') as f:
        json.dump({
            "date": datetime.now().isoformat(),
            "data_file": str(DATA_FILE),
            "total": len(all_results),
            "success": sum(1 for r in all_results if r.get('success')),
            "results": all_results
        }, f, indent=2, default=str)

    # 汇总
    print("\n" + "=" * 80)
    print("回测汇总")
    print("=" * 80)

    success_results = [r for r in all_results if r.get("success")]
    failed_results = [r for r in all_results if not r.get("success")]

    print(f"成功: {len(success_results)}/{len(all_results)}")
    print(f"失败: {len(failed_results)}")

    if success_results:
        print("\n" + "-" * 80)
        print("演化策略性能排名")
        print("-" * 80)
        sorted_results = sorted(success_results, key=lambda x: x['return_pct'], reverse=True)
        for i, r in enumerate(sorted_results, 1):
            print(f"{i}. {r['strategy']:30s} | 收益: {r['return_pct']:7.2f}% | Sharpe: {str(r.get('sharpe', 'N/A'))[:6]:6s} | MaxDD: {r['max_drawdown']:6.2f}%")

        # 与Top 3 baseline对比
        print("\n" + "-" * 80)
        print("对比Top 3 Baseline")
        print("-" * 80)
        print("Baseline Top 3:")
        print("  1. strategy_007: 2.93%")
        print("  2. strategy_016: 1.38%")
        print("  3. strategy_022: 0.75%")

        if sorted_results:
            best_evolved = sorted_results[0]
            improvement = best_evolved['return_pct'] - 2.93
            print(f"\n最佳演化策略: {best_evolved['strategy']}")
            print(f"  收益率: {best_evolved['return_pct']:.2f}%")
            print(f"  相对改进: {improvement:+.2f}%")

    if failed_results:
        print("\n" + "-" * 80)
        print("失败策略详情")
        print("-" * 80)
        for r in failed_results:
            print(f"  {r['strategy']}: {r.get('error', 'Unknown')[:80]}")

    print("\n" + "=" * 80)
    print(f"结果已保存: {results_file}")
    print("=" * 80)

if __name__ == "__main__":
    main()
