#!/usr/bin/env python3
"""
Experiment 12: 市场环境分离测试
目标: 在牛市/熊市/震荡市分别测试策略表现
"""

import backtrader as bt
import pandas as pd
import numpy as np
from pathlib import Path
from datetime import datetime
import json
from tqdm import tqdm

# ========== 配置 ==========
DATA_DIR = Path("/root/autodl-tmp/eoh/backtest_data_extended")
OUTPUT_DIR = Path("/root/autodl-tmp/eoh/experiment12_market_regime")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

INITIAL_CASH = 100000.0
COMMISSION = 0.001

# ========== 市场环境定义 ==========
# 根据上证指数(可用贵州茅台作为代理)的表现划分市场环境
MARKET_REGIMES = {
    "bull": {
        "name": "牛市",
        "periods": [
            ("2014-07-01", "2015-06-30"),  # 2014-2015大牛市
            ("2019-01-01", "2021-02-28"),  # 2019-2021复苏牛市
        ]
    },
    "bear": {
        "name": "熊市",
        "periods": [
            ("2010-01-04", "2014-06-30"),  # 2010-2014熊市/震荡
            ("2015-07-01", "2018-12-31"),  # 2015-2018股灾+熊市
        ]
    },
    "sideways": {
        "name": "震荡市",
        "periods": [
            ("2021-03-01", "2025-11-21"),  # 2021-2025震荡市
        ]
    }
}

# ========== 测试股票 (选择代表性股票) ==========
TEST_STOCKS = [
    {"file": "stock_sh_600519.csv", "name": "贵州茅台", "industry": "消费"},
    {"file": "stock_sz_000858.csv", "name": "五粮液", "industry": "消费"},
    {"file": "stock_sh_600036.csv", "name": "招商银行", "industry": "金融"},
    {"file": "stock_sz_000001.csv", "name": "平安银行", "industry": "金融"},
]

# ========== 策略参数 ==========
INNOVATION_PARAMS = {
    'fast_ma_period': 15,
    'medium_ma_period': 25,
    'slow_ma_period': 40,
    'rsi_period': 10,
    'atr_period': 28,
    'atr_multiple': 2.0,
    'risk_factor': 0.03
}

BASELINE_PARAMS = {
    'short_window': 30,
    'long_window': 40,
    'risk': 0.03,
    'stop_loss': 0.03,
    'take_profit': 0.08
}

# ========== 策略定义 ==========

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


# ========== 回测函数 ==========

def load_data(file_path):
    """加载数据"""
    df = pd.read_csv(file_path)
    df['date'] = pd.to_datetime(df['date'])
    df.set_index('date', inplace=True)
    df = df[['open', 'high', 'low', 'close', 'volume']]
    return df


def filter_data_by_regime(data, regime_periods):
    """根据市场环境筛选数据"""
    filtered_dfs = []
    for start_date, end_date in regime_periods:
        mask = (data.index >= start_date) & (data.index <= end_date)
        filtered_dfs.append(data[mask])

    if filtered_dfs:
        return pd.concat(filtered_dfs)
    return pd.DataFrame()


def run_backtest(strategy_class, params, data, stock_name, strategy_name, regime_name):
    """运行单次回测"""
    if len(data) < 100:
        return {
            "success": False,
            "stock": stock_name,
            "strategy": strategy_name,
            "regime": regime_name,
            "error": "数据点不足(<100)",
            "data_points": len(data)
        }

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
            "strategy": strategy_name,
            "regime": regime_name,
            "return_pct": return_pct,
            "sharpe": sharpe,
            "max_drawdown": max_dd,
            "total_trades": total_trades,
            "win_rate": win_rate,
            "data_points": len(data),
            "params": params
        }
    except Exception as e:
        return {
            "success": False,
            "stock": stock_name,
            "strategy": strategy_name,
            "regime": regime_name,
            "error": str(e),
            "data_points": len(data),
            "params": params
        }


# ========== 主分析函数 ==========

def main():
    print(f"""
{'='*80}
Experiment 12: 市场环境分离测试
{'='*80}
目标: 测试策略在牛市/熊市/震荡市的表现
测试股票: {len(TEST_STOCKS)}只
市场环境: 3种 (牛市/熊市/震荡市)
测试策略: 2个 (innovation vs baseline)
{'='*80}
    """)

    all_results = []

    # 测试每只股票
    for stock_info in tqdm(TEST_STOCKS, desc="测试股票"):
        print(f"\n{'='*80}")
        print(f"测试股票: {stock_info['name']} ({stock_info['industry']})")
        print(f"{'='*80}")

        file_path = DATA_DIR / stock_info['file']

        try:
            # 加载完整数据
            full_data = load_data(file_path)
            print(f"完整数据: {len(full_data)} 天")

            # 在每个市场环境下测试
            for regime_type, regime_info in MARKET_REGIMES.items():
                print(f"\n  📊 {regime_info['name']}环境:")

                # 筛选数据
                regime_data = filter_data_by_regime(full_data, regime_info['periods'])

                if len(regime_data) == 0:
                    print(f"    ⚠️  无数据")
                    continue

                print(f"    数据点: {len(regime_data)} 天")

                # 测试innovation策略
                result_innovation = run_backtest(
                    AdaptiveMultiFactorStrategy,
                    INNOVATION_PARAMS,
                    regime_data,
                    stock_info['name'],
                    "innovation",
                    regime_info['name']
                )
                all_results.append(result_innovation)

                # 测试baseline策略
                result_baseline = run_backtest(
                    TrendFollowingStrategy,
                    BASELINE_PARAMS,
                    regime_data,
                    stock_info['name'],
                    "baseline",
                    regime_info['name']
                )
                all_results.append(result_baseline)

                # 输出结果
                if result_innovation['success']:
                    print(f"    innovation: {result_innovation['return_pct']:+.2f}%")
                else:
                    print(f"    innovation: ❌ {result_innovation.get('error', 'Unknown')}")

                if result_baseline['success']:
                    print(f"    baseline:   {result_baseline['return_pct']:+.2f}%")
                else:
                    print(f"    baseline: ❌ {result_baseline.get('error', 'Unknown')}")

        except Exception as e:
            print(f"❌ 错误: {str(e)}")

    # 保存结果
    output_file = OUTPUT_DIR / "market_regime_results.json"
    with open(output_file, 'w') as f:
        json.dump({
            "experiment": "Experiment 12: Market Regime Testing",
            "date": datetime.now().isoformat(),
            "results": all_results
        }, f, indent=2, default=str)

    print(f"\n{'='*80}")
    print("分析完成!")
    print(f"结果已保存: {output_file}")
    print(f"{'='*80}")

    # 汇总分析
    print(f"\n{'='*80}")
    print("按市场环境汇总")
    print(f"{'='*80}\n")

    successful = [r for r in all_results if r['success']]

    for regime_type, regime_info in MARKET_REGIMES.items():
        regime_name = regime_info['name']
        regime_results = [r for r in successful if r['regime'] == regime_name]

        if not regime_results:
            print(f"📌 {regime_name}: 无有效数据")
            continue

        print(f"📌 {regime_name}:")

        # 按策略分组
        innovation_results = [r for r in regime_results if r['strategy'] == 'innovation']
        baseline_results = [r for r in regime_results if r['strategy'] == 'baseline']

        if innovation_results:
            avg_innovation = np.mean([r['return_pct'] for r in innovation_results])
            print(f"  innovation: {avg_innovation:+.2f}% (平均, {len(innovation_results)}次)")

        if baseline_results:
            avg_baseline = np.mean([r['return_pct'] for r in baseline_results])
            print(f"  baseline:   {avg_baseline:+.2f}% (平均, {len(baseline_results)}次)")

        if innovation_results and baseline_results:
            if avg_innovation > avg_baseline + 5:
                print(f"  💡 建议: {regime_name}下使用 innovation")
            elif avg_baseline > avg_innovation + 5:
                print(f"  💡 建议: {regime_name}下使用 baseline")
            else:
                print(f"  💡 建议: 两者差异不大")

        print()

    # 按策略汇总
    print(f"{'='*80}")
    print("按策略汇总")
    print(f"{'='*80}\n")

    for strategy_name in ['innovation', 'baseline']:
        print(f"📌 {strategy_name}:")
        strategy_results = [r for r in successful if r['strategy'] == strategy_name]

        for regime_type, regime_info in MARKET_REGIMES.items():
            regime_name = regime_info['name']
            regime_strategy_results = [r for r in strategy_results if r['regime'] == regime_name]

            if regime_strategy_results:
                avg_return = np.mean([r['return_pct'] for r in regime_strategy_results])
                print(f"  {regime_name}: {avg_return:+.2f}%")

        print()


if __name__ == "__main__":
    main()
