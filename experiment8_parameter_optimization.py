#!/usr/bin/env python3
"""
Experiment 8: 参数优化
目标: 对Top 3 baseline + 最佳演化策略进行Grid Search参数优化
"""

import backtrader as bt
import pandas as pd
from pathlib import Path
from datetime import datetime
import json
import itertools
from tqdm import tqdm

# ========== 配置 ==========
DATA_FILE = Path("/root/autodl-tmp/eoh/backtest_data_extended/stock_sh_600519.csv")
OUTPUT_DIR = Path("/root/autodl-tmp/eoh/experiment8_parameter_optimization")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

INITIAL_CASH = 100000.0
COMMISSION = 0.001

# ========== 参数搜索空间 ==========

PARAM_SPACES = {
    "strategy_007": {
        'short_window': [10, 15, 20, 25, 30],
        'long_window': [40, 50, 60, 70],
        'risk': [0.01, 0.02, 0.03],
        'stop_loss': [0.03, 0.05, 0.07],
        'take_profit': [0.08, 0.10, 0.12]
    },
    "strategy_016": {
        'maperiod': [14, 20, 28],
        'stop_loss': [0.03, 0.05, 0.07],
        'take_profit': [0.03, 0.05, 0.07, 0.10]
    },
    "strategy_022": {
        'fast_ma_period': [10, 14, 20],
        'slow_ma_period': [21, 28, 35],
        'atr_period': [14, 20, 28],
        'atr_multiplier': [1.5, 2.0, 2.5],
        'stop_loss': [0.03, 0.05, 0.07],
        'take_profit': [0.08, 0.10, 0.12]
    },
    "innovation_triple_fusion": {
        'fast_ma_period': [5, 10, 15],
        'medium_ma_period': [15, 20, 25],
        'slow_ma_period': [40, 50, 60],
        'rsi_period': [10, 14, 20],
        'atr_period': [14, 20, 28],
        'atr_multiple': [2.0, 3.0, 4.0],
        'risk_factor': [0.01, 0.02, 0.03]
    }
}

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


def run_backtest(strategy_class, params, data):
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
            "error": str(e),
            "params": params
        }


def grid_search(strategy_name, strategy_class, param_space, data):
    """Grid Search参数优化"""
    print(f"\n{'='*80}")
    print(f"优化策略: {strategy_name}")
    print(f"{'='*80}")

    # 生成所有参数组合
    param_names = list(param_space.keys())
    param_values = [param_space[k] for k in param_names]
    param_combinations = list(itertools.product(*param_values))

    print(f"参数空间大小: {len(param_combinations)} 个组合")
    print(f"参数: {param_names}")

    # 运行所有组合
    results = []
    for combo in tqdm(param_combinations, desc=f"Grid Search {strategy_name}"):
        params = dict(zip(param_names, combo))
        result = run_backtest(strategy_class, params, data)
        results.append(result)

    # 筛选成功的结果
    successful = [r for r in results if r['success']]

    if not successful:
        print(f"❌ 没有成功的回测结果")
        return None

    # 按收益率排序
    successful.sort(key=lambda x: x['return_pct'], reverse=True)

    # Top 5
    print(f"\n✅ 成功回测: {len(successful)}/{len(results)}")
    print(f"\nTop 5 参数组合:")
    for i, res in enumerate(successful[:5], 1):
        print(f"\n  #{i} 收益率: {res['return_pct']:.2f}%")
        sharpe_str = f"{res['sharpe']:.3f}" if res['sharpe'] else 'N/A'
        print(f"      Sharpe: {sharpe_str}")
        print(f"      最大回撤: {res['max_drawdown']:.2f}%")
        print(f"      交易次数: {res['total_trades']}")
        print(f"      胜率: {res['win_rate']:.1f}%")
        print(f"      参数: {res['params']}")

    # 保存结果
    output_file = OUTPUT_DIR / f"{strategy_name}_optimization.json"
    with open(output_file, 'w') as f:
        json.dump({
            "strategy": strategy_name,
            "date": datetime.now().isoformat(),
            "total_combinations": len(results),
            "successful": len(successful),
            "top_10": successful[:10],
            "all_results": results
        }, f, indent=2, default=str)

    print(f"\n结果已保存: {output_file}")

    return successful[0]  # 返回最佳结果


# ========== 主程序 ==========

def main():
    print(f"""
{'='*80}
Experiment 8: 参数优化
{'='*80}
目标: 对Top 3 baseline + 最佳演化策略进行Grid Search参数优化
测试数据: 贵州茅台 (600519)
{'='*80}
    """)

    # 加载数据
    print("加载数据...")
    data = load_data(DATA_FILE)
    print(f"✅ 数据加载完成: {len(data)} 行")
    print(f"   时间范围: {data.index[0]} 至 {data.index[-1]}")

    # 定义策略映射
    strategies = {
        "strategy_007": TrendFollowingStrategy,
        "strategy_016": VolatilityBreakoutStrategy016,
        "strategy_022": VolatilityBreakoutStrategy022,
        "innovation_triple_fusion": AdaptiveMultiFactorStrategy
    }

    # 运行优化
    all_best_results = {}

    for strategy_name, strategy_class in strategies.items():
        param_space = PARAM_SPACES[strategy_name]
        best_result = grid_search(strategy_name, strategy_class, param_space, data)
        if best_result:
            all_best_results[strategy_name] = best_result

    # 汇总最佳结果
    print(f"\n\n{'='*80}")
    print("Experiment 8 汇总结果")
    print(f"{'='*80}\n")

    for strategy_name, result in all_best_results.items():
        print(f"{strategy_name}:")
        print(f"  最佳收益率: {result['return_pct']:.2f}%")
        sharpe_str = f"{result['sharpe']:.3f}" if result['sharpe'] else 'N/A'
        print(f"  Sharpe: {sharpe_str}")
        print(f"  最大回撤: {result['max_drawdown']:.2f}%")
        print(f"  交易次数: {result['total_trades']}")
        print(f"  胜率: {result['win_rate']:.1f}%")
        print(f"  最佳参数: {result['params']}\n")

    # 保存汇总
    summary_file = OUTPUT_DIR / "optimization_summary.json"
    with open(summary_file, 'w') as f:
        json.dump({
            "experiment": "Experiment 8: Parameter Optimization",
            "date": datetime.now().isoformat(),
            "best_results": all_best_results
        }, f, indent=2, default=str)

    print(f"汇总结果已保存: {summary_file}")
    print(f"\n{'='*80}")
    print("Experiment 8 完成!")
    print(f"{'='*80}")


if __name__ == "__main__":
    main()
