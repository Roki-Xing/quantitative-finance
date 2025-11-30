import backtrader as bt
import pandas as pd
import json
import sys
from datetime import datetime
from strategy_013_original import Strategy013Original

# 10只A股代码（与Day 53相同）
STOCKS = [
    ('600519', '贵州茅台'),
    ('000858', '五粮液'),
    ('600036', '招商银行'),
    ('601318', '中国平安'),
    ('000651', '格力电器'),
    ('000725', '京东方'),
    ('000002', '万科A'),
    ('600028', '中国石化'),
    ('601857', '中国石油'),
    ('300059', '东方财富'),
]

def run_single_stock(stock_code, stock_name, start_date="2024-01-01", end_date="2024-12-31"):
    # 确定文件路径
    if stock_code.startswith('6'):
        csv_file = f"/root/autodl-tmp/eoh/backtest_data_extended/stock_sh_{stock_code}.csv"
    else:
        csv_file = f"/root/autodl-tmp/eoh/backtest_data_extended/stock_sz_{stock_code}.csv"

    try:
        # 读取数据
        df = pd.read_csv(csv_file)
        df["date"] = pd.to_datetime(df["date"])
        df = df[(df["date"] >= start_date) & (df["date"] <= end_date)]

        if len(df) < 50:
            return None

        # 初始化Cerebro
        cerebro = bt.Cerebro()
        cerebro.addstrategy(Strategy013Original)

        # 添加数据
        data = bt.feeds.PandasData(
            dataname=df,
            datetime="date",
            open="open",
            high="high",
            low="low",
            close="close",
            volume="volume",
            openinterest=-1
        )
        cerebro.adddata(data)

        # 设置参数
        cerebro.broker.setcash(100000.0)
        cerebro.broker.setcommission(commission=0.001)

        # 添加分析器
        cerebro.addanalyzer(bt.analyzers.SharpeRatio, _name="sharpe")
        cerebro.addanalyzer(bt.analyzers.DrawDown, _name="drawdown")
        cerebro.addanalyzer(bt.analyzers.Returns, _name="returns")
        cerebro.addanalyzer(bt.analyzers.TradeAnalyzer, _name="trades")

        # 运行
        initial_value = cerebro.broker.getvalue()
        results = cerebro.run()
        final_value = cerebro.broker.getvalue()
        strat = results[0]

        # 提取指标
        sharpe = strat.analyzers.sharpe.get_analysis().get("sharperatio", 0)
        if sharpe is None:
            sharpe = 0.0

        drawdown_info = strat.analyzers.drawdown.get_analysis()
        max_drawdown = drawdown_info.get("max", {}).get("drawdown", 0)

        trade_analysis = strat.analyzers.trades.get_analysis()
        total_trades = trade_analysis.get("total", {}).get("closed", 0)

        returns = (final_value - initial_value) / initial_value * 100

        return {
            "stock_code": stock_code,
            "stock_name": stock_name,
            "returns_pct": round(returns, 2),
            "sharpe_ratio": round(sharpe, 2),
            "max_drawdown_pct": round(max_drawdown, 2),
            "total_trades": total_trades,
            "final_value": round(final_value, 2),
            "initial_value": initial_value
        }

    except Exception as e:
        print(f"Error testing {stock_name} ({stock_code}): {e}")
        return None

def main():
    print("="*60)
    print("Testing Original Strategy #13 on 2024 A-shares")
    print("="*60)
    print(f"Test Period: 2024-01-01 to 2024-12-31")
    print(f"Initial Capital: ¥100,000")
    print(f"Commission: 0.1%")
    print()

    results = []

    for stock_code, stock_name in STOCKS:
        print(f"Testing {stock_name} ({stock_code})...", end=" ")
        result = run_single_stock(stock_code, stock_name)
        if result:
            results.append(result)
            print(f"✓ Returns: {result['returns_pct']}%")
        else:
            print("✗ Failed")

    # 保存结果
    import os
    os.makedirs("/root/autodl-tmp/outputs", exist_ok=True)
    output_file = "/root/autodl-tmp/outputs/strategy013_original_2024_results.json"
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

    # 打印汇总
    print()
    print("="*60)
    print("Summary Statistics")
    print("="*60)

    if results:
        avg_returns = sum(r["returns_pct"] for r in results) / len(results)
        avg_sharpe = sum(r["sharpe_ratio"] for r in results) / len(results)
        avg_drawdown = sum(r["max_drawdown_pct"] for r in results) / len(results)
        avg_trades = sum(r["total_trades"] for r in results) / len(results)
        success_count = sum(1 for r in results if r["returns_pct"] > 0)

        print(f"Tested Stocks: {len(results)}/10")
        print(f"Average Returns: {avg_returns:.2f}%")
        print(f"Average Sharpe: {avg_sharpe:.2f}")
        print(f"Average Max Drawdown: {avg_drawdown:.2f}%")
        print(f"Average Trades: {avg_trades:.1f}")
        print(f"Success Rate: {success_count}/{len(results)} ({success_count/len(results)*100:.1f}%)")
        print()
        print(f"Results saved to: {output_file}")

    return results

if __name__ == "__main__":
    main()
