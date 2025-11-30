#!/usr/bin/env python3
"""
Experiment 6: 全面Baseline回测与性能评估
目标: 回测所有30个可运行的baseline策略,筛选top performers
"""
import backtrader as bt
import pandas as pd
from pathlib import Path
import sys
import importlib.util
from datetime import datetime
import json
import traceback

# 配置
BASELINE_DIR = Path("/root/autodl-tmp/eoh/experiment4_trading_extended/baseline")
MANUAL_FIX_DIR = Path("/root/autodl-tmp/eoh/manual_fix/baseline")
AUTOFIX_DIR = Path("/root/autodl-tmp/eoh/experiment5_autofix")
DATA_DIR = Path("/root/autodl-tmp/eoh/backtest_data_extended")
RESULTS_DIR = Path("/root/autodl-tmp/eoh/experiment6_baseline_evaluation")
RESULTS_DIR.mkdir(parents=True, exist_ok=True)

# 需要从manual_fix使用的策略列表
MANUAL_FIX_STRATEGIES = [7, 13, 17, 19, 20, 21, 23, 24, 25, 26, 28]
# 需要从autofix使用的策略列表 (Experiment 5中auto-fix成功的)
AUTOFIX_STRATEGIES = [14, 16, 18, 27, 29, 30]

def load_strategy_class(strategy_file):
    """动态加载策略类"""
    try:
        # Clean up any previous strategy module to avoid conflicts
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

        # 添加分析器
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
        returns = strat.analyzers.returns.get_analysis()

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
    print("="*80)
    print("Experiment 6: 全面Baseline回测与性能评估")
    print("="*80)
    print(f"时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*80)

    # 收集所有可用数据文件
    data_files = sorted(DATA_DIR.glob("stock_*.csv"))
    print(f"\n找到 {len(data_files)} 个股票数据文件")

    # 为每个股票选择一个测试数据(贵州茅台)
    test_data = DATA_DIR / "stock_sh_600519.csv"
    if not test_data.exists():
        print(f"错误: 测试数据 {test_data} 不存在")
        return

    print(f"使用测试数据: {test_data.name}")
    print("="*80)

    # 收集所有策略
    all_results = []

    for idx in range(1, 31):
        strategy_num = idx

        # 确定使用哪个目录的策略文件
        if strategy_num in MANUAL_FIX_STRATEGIES:
            strategy_file = MANUAL_FIX_DIR / f"strategy_{idx:03d}_fixed.py"
            source = "manual_fix"
        elif strategy_num in AUTOFIX_STRATEGIES:
            strategy_file = AUTOFIX_DIR / f"strategy_{idx:03d}_autofix.py"
            source = "autofix"
        else:
            strategy_file = BASELINE_DIR / f"strategy_{idx:03d}.py"
            source = "baseline"

        if not strategy_file.exists():
            print(f"[strategy_{idx:03d}] ❌ 文件不存在: {strategy_file}")
            continue

        print(f"\n[strategy_{idx:03d}] ({source}) 回测中...", end=" ")

        # 加载策略类
        strategy_class = load_strategy_class(strategy_file)
        if not strategy_class:
            print(f"❌ 无法加载策略类")
            all_results.append({
                "strategy": f"strategy_{idx:03d}",
                "source": source,
                "success": False,
                "error": "Failed to load strategy class"
            })
            continue

        # 运行回测
        result = run_backtest(strategy_class, test_data, f"strategy_{idx:03d}")
        result["strategy"] = f"strategy_{idx:03d}"
        result["source"] = source
        all_results.append(result)

        if result.get("success"):
            print(f"✅ 收益: {result['return_pct']:.2f}% | Sharpe: {result.get('sharpe', 'N/A')} | MaxDD: {result['max_drawdown']:.2f}%")
        else:
            print(f"❌ 错误: {result.get('error', 'Unknown')[:50]}")

    # 保存详细结果
    results_file = RESULTS_DIR / "backtest_results.json"
    with open(results_file, 'w') as f:
        json.dump({
            "date": datetime.now().isoformat(),
            "data_file": test_data.name,
            "total_strategies": len(all_results),
            "results": all_results
        }, f, indent=2)

    # 生成汇总报告
    print("\n" + "="*80)
    print("回测汇总")
    print("="*80)

    success_results = [r for r in all_results if r.get("success")]
    failed_results = [r for r in all_results if not r.get("success")]

    print(f"成功: {len(success_results)}/{len(all_results)} ({len(success_results)/len(all_results)*100:.1f}%)")
    print(f"失败: {len(failed_results)}")

    if success_results:
        print("\n" + "-"*80)
        print("性能统计")
        print("-"*80)

        avg_return = sum(r['return_pct'] for r in success_results) / len(success_results)
        sharpes = [r['sharpe'] for r in success_results if r['sharpe'] and r['sharpe'] != float('inf')]
        avg_sharpe = sum(sharpes) / len(sharpes) if sharpes else 0
        avg_dd = sum(r['max_drawdown'] for r in success_results) / len(success_results)
        avg_trades = sum(r['total_trades'] for r in success_results) / len(success_results)

        print(f"平均收益率: {avg_return:.2f}%")
        print(f"平均Sharpe: {avg_sharpe:.2f}")
        print(f"平均最大回撤: {avg_dd:.2f}%")
        print(f"平均交易次数: {avg_trades:.0f}")

        # Top 10 策略
        print("\n" + "-"*80)
        print("Top 10 策略 (按收益率)")
        print("-"*80)
        sorted_results = sorted(success_results, key=lambda x: x['return_pct'], reverse=True)
        for i, r in enumerate(sorted_results[:10], 1):
            print(f"{i:2d}. {r['strategy']:15s} | 收益: {r['return_pct']:7.2f}% | Sharpe: {r.get('sharpe', 'N/A')!s:6s} | MaxDD: {r['max_drawdown']:6.2f}% | 交易: {r['total_trades']:3d}")

        # Bottom 5 策略
        print("\n" + "-"*80)
        print("Bottom 5 策略 (表现最差)")
        print("-"*80)
        for i, r in enumerate(sorted_results[-5:], 1):
            print(f"{i}. {r['strategy']:15s} | 收益: {r['return_pct']:7.2f}% | Sharpe: {r.get('sharpe', 'N/A')!s:6s} | MaxDD: {r['max_drawdown']:6.2f}%")

    print("\n" + "="*80)
    print(f"结果已保存: {results_file}")
    print("="*80)

if __name__ == "__main__":
    main()
