#!/usr/bin/env python3
"""
Experiment 9: 多市场验证
目标: 在18只A股上验证Experiment 8优化参数的泛化能力
"""

import backtrader as bt
import pandas as pd
from pathlib import Path
from datetime import datetime
import json
from tqdm import tqdm

# ========== 配置 ==========
DATA_DIR = Path("/root/autodl-tmp/eoh/backtest_data_extended")
OUTPUT_DIR = Path("/root/autodl-tmp/eoh/experiment9_multi_market_validation")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

INITIAL_CASH = 100000.0
COMMISSION = 0.001

# ========== Experiment 8最优参数 ==========

OPTIMIZED_PARAMS = {
    "innovation_triple_fusion": {
        'fast_ma_period': 15,
        'medium_ma_period': 25,
        'slow_ma_period': 40,
        'rsi_period': 10,
        'atr_period': 28,
        'atr_multiple': 2.0,
        'risk_factor': 0.03
    },
    "strategy_007": {
        'short_window': 30,
        'long_window': 40,
        'risk': 0.03,
        'stop_loss': 0.03,
        'take_profit': 0.08
    },
    "strategy_016": {
        'maperiod': 28,
        'stop_loss': 0.07,
        'take_profit': 0.05
    },
    "strategy_022": {
        'fast_ma_period': 10,
        'slow_ma_period': 35,
        'atr_period': 28,
        'atr_multiplier': 1.5,
        'stop_loss': 0.07,
        'take_profit': 0.12
    }
}

# ========== 测试股票列表 ==========

STOCK_FILES = [
    "stock_sh_600028.csv",  # 中国石化
    "stock_sh_600036.csv",  # 招商银行
    "stock_sh_600048.csv",  # 保利发展
    "stock_sh_600276.csv",  # 恒瑞医药
    "stock_sh_600519.csv",  # 贵州茅台 (已在Exp8测试)
    "stock_sh_600887.csv",  # 伊利股份
    "stock_sh_601318.csv",  # 中国平安
    "stock_sh_601857.csv",  # 中国石油
    "stock_sz_000001.csv",  # 平安银行
    "stock_sz_000002.csv",  # 万科A
    "stock_sz_000063.csv",  # 中兴通讯
    "stock_sz_000333.csv",  # 美的集团
    "stock_sz_000538.csv",  # 云南白药
    "stock_sz_000651.csv",  # 格力电器
    "stock_sz_000725.csv",  # 京东方A
    "stock_sz_000858.csv",  # 五粮液
    "stock_sz_002415.csv",  # 海康威视
    "stock_sz_300059.csv"   # 东方财富
]

# ========== 策略定义 ==========

class TrendFollowingStrategy(bt.Strategy):
    """strategy_007"""
    params = (
        ('short_window', 20),
        ('long_window', 50),
        ('risk', 0.02),
        ('stop_loss', 0.05),
        ('take_profit', 0.1)
    )

    def __init__(self):
        self.order = None
        self.dataclose = self.datas[0].close
        self.sma_short = bt.indicators.SMA(period=self.p.short_window)
        self.sma_long = bt.indicators.SMA(period=self.p.long_window)

    def next(self):
        if self.position:
            if self.dataclose > self.sma_long and self.dataclose < self.sma_short:
                self.close()
            elif self.dataclose < self.sma_long and self.dataclose > self.sma_short:
                self.close()

        if not self.position:
            if self.dataclose > self.sma_long:
                size = int(self.broker.getvalue() * self.p.risk / self.dataclose[0])
                if size > 0:
                    self.buy(size=size)


class VolatilityBreakoutStrategy016(bt.Strategy):
    """strategy_016"""
    params = (
        ('maperiod', 20),
        ('stop_loss', 0.05),
        ('take_profit', 0.05),
    )

    def __init__(self):
        self.data_close = self.datas[0].close
        self.data_high = self.datas[0].high
        self.data_low = self.datas[0].low
        self.data_atr = bt.indicators.AverageTrueRange(self.data, period=self.p.maperiod)

        self.stop_loss_price = None
        self.take_profit_price = None
        self.buy_price = None
        self.order = None

    def next(self):
        if self.order:
            return

        if self.position.size == 0:
            if (self.data_close[0] > self.data_high[-1] and
                self.data_high[-1] > self.data_high[-2]):
                self.order = self.buy()
                self.buy_price = self.data_close[0]
                self.stop_loss_price = self.buy_price * (1 - self.p.stop_loss)
                self.take_profit_price = self.buy_price * (1 + self.p.take_profit)
        else:
            if self.position.size > 0:
                if (self.data_close[0] < self.stop_loss_price or
                    self.data_close[0] > self.take_profit_price):
                    self.order = self.close()

    def notify_order(self, order):
        if order.status == order.Completed:
            self.order = None


class VolatilityBreakoutStrategy022(bt.Strategy):
    """strategy_022"""
    params = (
        ('fast_ma_period', 14),
        ('slow_ma_period', 28),
        ('atr_period', 14),
        ('atr_multiplier', 2.0),
        ('stop_loss', 0.05),
        ('take_profit', 0.10)
    )

    def __init__(self):
        self.data_close = self.datas[0].close
        self.fast_ma = bt.indicators.SMA(self.data.close, period=self.params.fast_ma_period)
        self.slow_ma = bt.indicators.SMA(self.data.close, period=self.params.slow_ma_period)
        self.atr = bt.indicators.ATR(self.data, period=self.params.atr_period)
        self.order = None
        self.entry_price = None

    def next(self):
        if self.order:
            return

        if not self.position:
            if (self.data_close[0] > self.slow_ma[0] and
                self.data_close[-1] <= self.slow_ma[-1] and
                self.atr[0] > self.atr[-5]):
                self.order = self.buy()
                self.entry_price = self.data_close[0]
        else:
            if self.position.size > 0:
                if self.data_close[0] >= self.entry_price * (1 + self.params.take_profit):
                    self.order = self.close()
                    self.entry_price = None
                elif self.data_close[0] <= self.entry_price * (1 - self.params.stop_loss):
                    self.order = self.close()
                    self.entry_price = None

    def notify_order(self, order):
        if order.status == order.Completed:
            self.order = None


class AdaptiveMultiFactorStrategy(bt.Strategy):
    """innovation_triple_fusion"""
    params = (
        ('fast_ma_period', 10),
        ('medium_ma_period', 20),
        ('slow_ma_period', 50),
        ('rsi_period', 14),
        ('atr_period', 14),
        ('atr_multiple', 3.0),
        ('risk_factor', 0.01),
    )

    def __init__(self):
        from backtrader.indicators import SMA, ATR, RSI
        self.fast_ma = SMA(self.data.close, period=self.params.fast_ma_period)
        self.medium_ma = SMA(self.data.close, period=self.params.medium_ma_period)
        self.slow_ma = SMA(self.data.close, period=self.params.slow_ma_period)
        self.rsi = RSI(self.data.close, period=self.params.rsi_period)
        self.atr = ATR(self.data, period=self.params.atr_period)

        self.order = None
        self.entry_price = None

    def notify_order(self, order):
        if order.status in [order.Submitted, order.Accepted]:
            return

        if order.status == order.Completed:
            if order.isbuy():
                self.entry_price = order.executed.price
            elif order.issell():
                self.entry_price = None
            self.order = None

    def next(self):
        if self.order:
            return

        atr_val = self.atr[0] if self.atr[0] > 0 else self.data.close[0] * 0.02

        if not self.position:
            trend_strength = (self.fast_ma > self.medium_ma) and (self.medium_ma > self.slow_ma)
            volatility_filter = self.rsi < 30 or self.rsi > 70

            if trend_strength and volatility_filter:
                risk_per_trade = self.broker.getvalue() * self.params.risk_factor
                position_size = int(risk_per_trade / (atr_val * self.params.atr_multiple))

                if position_size > 0:
                    self.order = self.buy(size=position_size)

        else:
            if self.entry_price:
                trailing_stop = self.entry_price - atr_val * self.params.atr_multiple

                if self.data.close[0] < trailing_stop:
                    self.order = self.close()
                elif self.fast_ma < self.medium_ma:
                    self.order = self.close()


# ========== 回测函数 ==========

def load_data(file_path):
    """加载数据"""
    df = pd.read_csv(file_path)
    df['date'] = pd.to_datetime(df['date'])
    df.set_index('date', inplace=True)
    df = df[['open', 'high', 'low', 'close', 'volume']]
    return df


def run_backtest(strategy_class, params, data, stock_name):
    """运行单次回测"""
    try:
        cerebro = bt.Cerebro()
        cerebro.addstrategy(strategy_class, **params)

        btdata = bt.feeds.PandasData(dataname=data)
        cerebro.adddata(btdata)

        cerebro.broker.setcash(INITIAL_CASH)
        cerebro.broker.setcommission(commission=COMMISSION)

        cerebro.addanalyzer(bt.analyzers.SharpeRatio, _name='sharpe', riskfreerate=0.03)
        cerebro.addanalyzer(bt.analyzers.DrawDown, _name='drawdown')
        cerebro.addanalyzer(bt.analyzers.TradeAnalyzer, _name='trades')
        cerebro.addanalyzer(bt.analyzers.Returns, _name='returns')

        initial = cerebro.broker.getvalue()
        results = cerebro.run()
        final = cerebro.broker.getvalue()

        strat = results[0]
        sharpe_analysis = strat.analyzers.sharpe.get_analysis()
        dd_analysis = strat.analyzers.drawdown.get_analysis()
        trade_analysis = strat.analyzers.trades.get_analysis()

        return_pct = (final - initial) / initial * 100
        sharpe = sharpe_analysis.get('sharperatio', None)
        max_dd = dd_analysis.get('max', {}).get('drawdown', 0)
        total_trades = trade_analysis.get('total', {}).get('total', 0)

        won = trade_analysis.get('won', {}).get('total', 0)
        lost = trade_analysis.get('lost', {}).get('total', 0)
        win_rate = (won / (won + lost) * 100) if (won + lost) > 0 else 0

        return {
            "success": True,
            "stock": stock_name,
            "return_pct": return_pct,
            "sharpe": sharpe,
            "max_drawdown": max_dd,
            "total_trades": total_trades,
            "win_rate": win_rate,
            "params": params
        }
    except Exception as e:
        return {
            "success": False,
            "stock": stock_name,
            "error": str(e),
            "params": params
        }


def test_strategy_on_all_stocks(strategy_name, strategy_class, params):
    """在所有股票上测试单个策略"""
    print(f"\n{'='*80}")
    print(f"测试策略: {strategy_name}")
    print(f"参数: {params}")
    print(f"{'='*80}")

    results = []
    for stock_file in tqdm(STOCK_FILES, desc=f"{strategy_name}"):
        file_path = DATA_DIR / stock_file
        stock_name = stock_file.replace('.csv', '')

        try:
            data = load_data(file_path)
            result = run_backtest(strategy_class, params, data, stock_name)
            results.append(result)
        except Exception as e:
            results.append({
                "success": False,
                "stock": stock_name,
                "error": f"数据加载错误: {str(e)}",
                "params": params
            })

    # 统计分析
    successful = [r for r in results if r.get('success')]
    failed = [r for r in results if not r.get('success')]

    print(f"\n✅ 成功: {len(successful)}/{len(results)}")
    print(f"❌ 失败: {len(failed)}")

    if successful:
        avg_return = sum(r['return_pct'] for r in successful) / len(successful)
        positive = [r for r in successful if r['return_pct'] > 0]
        negative = [r for r in successful if r['return_pct'] <= 0]

        sharpes = [r['sharpe'] for r in successful if r['sharpe'] is not None]
        avg_sharpe = sum(sharpes) / len(sharpes) if sharpes else None

        print(f"\n平均收益率: {avg_return:.2f}%")
        print(f"正收益股票数: {len(positive)}/{len(successful)} ({len(positive)/len(successful)*100:.1f}%)")
        print(f"负收益股票数: {len(negative)}/{len(successful)}")
        if avg_sharpe:
            print(f"平均Sharpe: {avg_sharpe:.3f}")

        # Top 5 和 Bottom 5
        sorted_results = sorted(successful, key=lambda x: x['return_pct'], reverse=True)

        print(f"\nTop 5 表现:")
        for i, r in enumerate(sorted_results[:5], 1):
            sharpe_str = f"{r['sharpe']:.3f}" if r['sharpe'] else 'N/A'
            print(f"  #{i} {r['stock']}: {r['return_pct']:.2f}% (Sharpe: {sharpe_str}, 交易: {r['total_trades']})")

        print(f"\nBottom 5 表现:")
        for i, r in enumerate(sorted_results[-5:], 1):
            sharpe_str = f"{r['sharpe']:.3f}" if r['sharpe'] else 'N/A'
            print(f"  #{i} {r['stock']}: {r['return_pct']:.2f}% (Sharpe: {sharpe_str}, 交易: {r['total_trades']})")

    return {
        "strategy": strategy_name,
        "params": params,
        "total_stocks": len(results),
        "successful": len(successful),
        "failed": len(failed),
        "results": results,
        "statistics": {
            "avg_return": avg_return if successful else None,
            "avg_sharpe": avg_sharpe if successful else None,
            "positive_count": len(positive) if successful else 0,
            "negative_count": len(negative) if successful else 0,
            "success_rate": len(positive) / len(successful) * 100 if successful else 0
        }
    }


# ========== 主程序 ==========

def main():
    print(f"""
{'='*80}
Experiment 9: 多市场验证
{'='*80}
目标: 在18只A股上验证Experiment 8优化参数的泛化能力
测试股票数: {len(STOCK_FILES)}
测试策略数: {len(OPTIMIZED_PARAMS)}
{'='*80}
    """)

    # 策略映射
    strategies = {
        "innovation_triple_fusion": AdaptiveMultiFactorStrategy,
        "strategy_007": TrendFollowingStrategy,
        "strategy_016": VolatilityBreakoutStrategy016,
        "strategy_022": VolatilityBreakoutStrategy022
    }

    # 测试所有策略
    all_results = {}

    for strategy_name, strategy_class in strategies.items():
        params = OPTIMIZED_PARAMS[strategy_name]
        result = test_strategy_on_all_stocks(strategy_name, strategy_class, params)
        all_results[strategy_name] = result

        # 保存单个策略结果
        output_file = OUTPUT_DIR / f"{strategy_name}_multi_market.json"
        with open(output_file, 'w') as f:
            json.dump(result, f, indent=2, default=str)
        print(f"\n结果已保存: {output_file}")

    # 汇总对比
    print(f"\n\n{'='*80}")
    print("Experiment 9 汇总对比")
    print(f"{'='*80}\n")

    comparison_data = []
    for strategy_name, result in all_results.items():
        stats = result['statistics']
        comparison_data.append({
            "strategy": strategy_name,
            "avg_return": stats['avg_return'],
            "avg_sharpe": stats['avg_sharpe'],
            "success_rate": stats['success_rate'],
            "positive_stocks": stats['positive_count'],
            "total_stocks": result['successful']
        })

    # 按平均收益率排序
    comparison_data.sort(key=lambda x: x['avg_return'] if x['avg_return'] else -999, reverse=True)

    print(f"{'策略':<30} {'平均收益':<12} {'Sharpe':<10} {'成功率':<10} {'正收益股票'}")
    print(f"{'-'*80}")
    for item in comparison_data:
        avg_ret_str = f"{item['avg_return']:.2f}%" if item['avg_return'] else "N/A"
        sharpe_str = f"{item['avg_sharpe']:.3f}" if item['avg_sharpe'] else "N/A"
        success_rate_str = f"{item['success_rate']:.1f}%"
        positive_str = f"{item['positive_stocks']}/{item['total_stocks']}"
        print(f"{item['strategy']:<30} {avg_ret_str:<12} {sharpe_str:<10} {success_rate_str:<10} {positive_str}")

    # 保存汇总
    summary_file = OUTPUT_DIR / "validation_summary.json"
    with open(summary_file, 'w') as f:
        json.dump({
            "experiment": "Experiment 9: Multi-Market Validation",
            "date": datetime.now().isoformat(),
            "total_stocks": len(STOCK_FILES),
            "total_strategies": len(strategies),
            "comparison": comparison_data,
            "all_results": all_results
        }, f, indent=2, default=str)

    print(f"\n汇总结果已保存: {summary_file}")
    print(f"\n{'='*80}")
    print("Experiment 9 完成!")
    print(f"{'='*80}")


if __name__ == "__main__":
    main()
