"""
经典策略基线扩展 - 补充实验
============================

目的: 回应审稿人"缺乏与经典策略对比"质疑
新增4个经典策略:
1. Momentum_Strategy (动量策略, 追涨杀跌)
2. MeanReversion_Strategy (均值回归策略)
3. Bollinger_Strategy (布林带突破策略)
4. MACD_Strategy (MACD指标策略)

与现有3个基线(Buy&Hold, SMA, RSI)形成完整对比组
预计新增: 4策略 × 12资产 × 2期 = 96回测

执行时间: ~90秒
"""

import backtrader as bt
import pandas as pd
import json
import numpy as np
from datetime import datetime
from pathlib import Path

# =============================================================================
# 策略1: 动量策略 (Momentum)
# =============================================================================

class Momentum_Strategy(bt.Strategy):
    """
    经典动量策略 (追涨杀跌)

    逻辑:
    - 买入信号: 过去N天收益率 > 阈值 (趋势向上)
    - 卖出信号: 过去N天收益率 < -阈值 (趋势向下)

    参数:
    - lookback_period: 动量计算窗口 (默认20天)
    - momentum_threshold: 买入阈值 (默认5%)
    """
    params = (
        ('lookback_period', 20),
        ('momentum_threshold', 0.05),  # 5% threshold
    )

    def __init__(self):
        self.momentum = bt.indicators.ROC(period=self.p.lookback_period)
        self.order = None

    def next(self):
        if self.order:
            return

        if not self.position:
            # 买入条件: 动量 > 阈值
            if self.momentum[0] > self.p.momentum_threshold:
                cash_per_trade = self.broker.getvalue() * 0.95
                price = self.data.close[0]
                size = int(cash_per_trade / price)
                self.order = self.buy(size=size)
        else:
            # 卖出条件: 动量转负
            if self.momentum[0] < -self.p.momentum_threshold:
                self.order = self.close()

    def notify_order(self, order):
        if order.status in [order.Completed, order.Canceled, order.Margin]:
            self.order = None


# =============================================================================
# 策略2: 均值回归策略 (Mean Reversion)
# =============================================================================

class MeanReversion_Strategy(bt.Strategy):
    """
    经典均值回归策略

    逻辑:
    - 买入信号: 价格低于移动平均线 > N个标准差 (超卖)
    - 卖出信号: 价格回归到均线附近 (获利了结)

    参数:
    - sma_period: 移动平均线周期 (默认20天)
    - num_std: 标准差倍数 (默认2)
    """
    params = (
        ('sma_period', 20),
        ('num_std', 2.0),
    )

    def __init__(self):
        self.sma = bt.indicators.SMA(period=self.p.sma_period)
        self.stddev = bt.indicators.StdDev(period=self.p.sma_period)
        self.order = None

    def next(self):
        if self.order:
            return

        if not self.position:
            # 买入条件: 价格 < SMA - 2*std (超卖)
            lower_band = self.sma[0] - self.p.num_std * self.stddev[0]
            if self.data.close[0] < lower_band:
                cash_per_trade = self.broker.getvalue() * 0.95
                price = self.data.close[0]
                size = int(cash_per_trade / price)
                self.order = self.buy(size=size)
        else:
            # 卖出条件: 价格回归到均线附近
            if self.data.close[0] >= self.sma[0]:
                self.order = self.close()

    def notify_order(self, order):
        if order.status in [order.Completed, order.Canceled, order.Margin]:
            self.order = None


# =============================================================================
# 策略3: 布林带策略 (Bollinger Bands)
# =============================================================================

class Bollinger_Strategy(bt.Strategy):
    """
    布林带突破策略

    逻辑:
    - 买入信号: 价格触及下轨 (超卖区域)
    - 卖出信号: 价格触及上轨 (超买区域)

    参数:
    - period: 布林带周期 (默认20天)
    - devfactor: 标准差倍数 (默认2)
    """
    params = (
        ('period', 20),
        ('devfactor', 2.0),
    )

    def __init__(self):
        self.boll = bt.indicators.BollingerBands(
            period=self.p.period,
            devfactor=self.p.devfactor
        )
        self.order = None

    def next(self):
        if self.order:
            return

        if not self.position:
            # 买入条件: 价格触及或低于下轨
            if self.data.close[0] <= self.boll.lines.bot[0]:
                cash_per_trade = self.broker.getvalue() * 0.95
                price = self.data.close[0]
                size = int(cash_per_trade / price)
                self.order = self.buy(size=size)
        else:
            # 卖出条件: 价格触及或高于上轨
            if self.data.close[0] >= self.boll.lines.top[0]:
                self.order = self.close()

    def notify_order(self, order):
        if order.status in [order.Completed, order.Canceled, order.Margin]:
            self.order = None


# =============================================================================
# 策略4: MACD策略
# =============================================================================

class MACD_Strategy(bt.Strategy):
    """
    MACD金叉死叉策略

    逻辑:
    - 买入信号: MACD线上穿信号线 (金叉)
    - 卖出信号: MACD线下穿信号线 (死叉)

    参数:
    - fast_period: 快线周期 (默认12)
    - slow_period: 慢线周期 (默认26)
    - signal_period: 信号线周期 (默认9)
    """
    params = (
        ('fast_period', 12),
        ('slow_period', 26),
        ('signal_period', 9),
    )

    def __init__(self):
        self.macd = bt.indicators.MACD(
            period_me1=self.p.fast_period,
            period_me2=self.p.slow_period,
            period_signal=self.p.signal_period
        )
        self.crossover = bt.indicators.CrossOver(
            self.macd.macd,
            self.macd.signal
        )
        self.order = None

    def next(self):
        if self.order:
            return

        if not self.position:
            # 买入条件: 金叉
            if self.crossover > 0:
                cash_per_trade = self.broker.getvalue() * 0.95
                price = self.data.close[0]
                size = int(cash_per_trade / price)
                self.order = self.buy(size=size)
        else:
            # 卖出条件: 死叉
            if self.crossover < 0:
                self.order = self.close()

    def notify_order(self, order):
        if order.status in [order.Completed, order.Canceled, order.Margin]:
            self.order = None


# =============================================================================
# 回测执行器
# =============================================================================

ASSETS = {
    # 原有5只核心股
    '600519_贵州茅台': '/root/autodl-tmp/eoh/backtest_data_extended/stock_sh_600519.csv',
    '000858_五粮液': '/root/autodl-tmp/eoh/backtest_data_extended/stock_sz_000858.csv',
    '600036_招商银行': '/root/autodl-tmp/eoh/backtest_data_extended/stock_sh_600036.csv',
    '000725_京东方': '/root/autodl-tmp/eoh/backtest_data_extended/stock_sz_000725.csv',
    '000002_万科A': '/root/autodl-tmp/eoh/backtest_data_extended/stock_sz_000002.csv',

    # 扩展5只
    '601318_中国平安': '/root/autodl-tmp/eoh/backtest_data_extended/stock_sh_601318.csv',
    '000651_格力电器': '/root/autodl-tmp/eoh/backtest_data_extended/stock_sz_000651.csv',
    '600028_中国石化': '/root/autodl-tmp/eoh/backtest_data_extended/stock_sh_600028.csv',
    '601857_中国石油': '/root/autodl-tmp/eoh/backtest_data_extended/stock_sh_601857.csv',
    '300059_东方财富': '/root/autodl-tmp/eoh/backtest_data_extended/stock_sz_300059.csv',
}

STRATEGIES = {
    'Momentum': Momentum_Strategy,
    'MeanReversion': MeanReversion_Strategy,
    'Bollinger': Bollinger_Strategy,
    'MACD': MACD_Strategy,
}

PERIODS = {
    'training': ('2018-01-01', '2023-12-31'),
    'testing': ('2024-01-01', '2024-12-31'),
}


def run_backtest(strategy_class, data_path, start_date, end_date, initial_cash=100000):
    """运行单个回测"""
    try:
        df = pd.read_csv(data_path, parse_dates=['date'])
        df = df[(df['date'] >= start_date) & (df['date'] <= end_date)]

        if len(df) < 50:
            return None

        cerebro = bt.Cerebro()
        cerebro.broker.setcash(initial_cash)
        cerebro.broker.setcommission(commission=0.0015)

        data_feed = bt.feeds.PandasData(
            dataname=df,
            datetime='date',
            open='open',
            high='high',
            low='low',
            close='close',
            volume='volume',
            openinterest=-1
        )

        cerebro.adddata(data_feed)
        cerebro.addstrategy(strategy_class)

        cerebro.addanalyzer(bt.analyzers.SharpeRatio, _name='sharpe')
        cerebro.addanalyzer(bt.analyzers.DrawDown, _name='drawdown')
        cerebro.addanalyzer(bt.analyzers.TradeAnalyzer, _name='trades')

        results = cerebro.run()
        final_value = cerebro.broker.getvalue()

        sharpe = results[0].analyzers.sharpe.get_analysis()
        drawdown = results[0].analyzers.drawdown.get_analysis()
        trades = results[0].analyzers.trades.get_analysis()

        return {
            'returns_pct': round(((final_value - initial_cash) / initial_cash) * 100, 2),
            'final_value': round(final_value, 2),
            'sharpe_ratio': round(sharpe.get('sharperatio', 0) or 0, 3),
            'max_drawdown_pct': round(drawdown.get('max', {}).get('drawdown', 0), 2),
            'total_trades': trades.get('total', {}).get('closed', 0),
        }

    except Exception as e:
        print(f"      ERROR: {str(e)}")
        return None


def main():
    print("=" * 80)
    print("经典策略基线扩展实验")
    print("=" * 80)
    print(f"开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"实验规模: 4策略 × 10资产 × 2期 = 80回测")
    print("=" * 80)

    results = {}
    counter = 0
    total = len(STRATEGIES) * len(ASSETS) * len(PERIODS)

    for strategy_name, strategy_class in STRATEGIES.items():
        print(f"\n[{strategy_name}] 策略测试")
        results[strategy_name] = {}

        for asset_name, data_path in ASSETS.items():
            results[strategy_name][asset_name] = {}

            for period_name, (start, end) in PERIODS.items():
                counter += 1
                print(f"  [{counter}/{total}] {asset_name} - {period_name}...", end=' ')

                result = run_backtest(strategy_class, data_path, start, end)

                if result:
                    results[strategy_name][asset_name][period_name] = result
                    print(f"OK ({result['returns_pct']:+.2f}%)")
                else:
                    print("FAILED")

    # 保存结果
    output_file = '/root/autodl-tmp/outputs/classical_baselines_extended.json'
    output_data = {
        'metadata': {
            'experiment_name': 'Classical Baselines Extended',
            'timestamp': datetime.now().isoformat(),
            'total_backtests': total,
            'strategies': list(STRATEGIES.keys()),
            'assets': list(ASSETS.keys()),
            'periods': list(PERIODS.keys()),
        },
        'results': results
    }

    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, indent=2, ensure_ascii=False)

    print("\n" + "=" * 80)
    print("经典策略基线扩展 - 执行完成")
    print("=" * 80)
    print(f"结束时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"输出文件: {output_file}")
    print("=" * 80)


if __name__ == '__main__':
    main()
