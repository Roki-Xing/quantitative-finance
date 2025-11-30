"""
扩展基线对比实验 - 18只A股完整验证
======================================

目的:
- 解决小样本问题 (5股 → 18股)
- 覆盖更多行业和波动率档位
- 提供稳健的统计验证

实验规模:
- 4个策略 × 12个资产 × 2个时期 = 96回测

策略:
1. Buy_and_Hold
2. SMA_Crossover
3. RSI_Strategy
4. LLM_Adaptive (Full Adaptive)

资产 (12只A股 + 2只US ETF):
- 10只A股 (核心)
- 8只A股 (扩展) - 待确认
- SPY, QQQ (US)
"""

import backtrader as bt
import pandas as pd
import json
from datetime import datetime
from pathlib import Path

# 导入策略
import sys
sys.path.append(str(Path(__file__).parent))

# =============================================================================
# 配置
# =============================================================================

ASSETS_EXTENDED = {
    # 今日已测试的5只 (core)
    '600519_贵州茅台': {
        'file': '/root/autodl-tmp/eoh/backtest_data_extended/stock_sh_600519.csv',
        'volatility': 'low', 'sector': '消费'
    },
    '000858_五粮液': {
        'file': '/root/autodl-tmp/eoh/backtest_data_extended/stock_sz_000858.csv',
        'volatility': 'medium', 'sector': '消费'
    },
    '600036_招商银行': {
        'file': '/root/autodl-tmp/eoh/backtest_data_extended/stock_sh_600036.csv',
        'volatility': 'low', 'sector': '金融'
    },
    '000725_京东方': {
        'file': '/root/autodl-tmp/eoh/backtest_data_extended/stock_sz_000725.csv',
        'volatility': 'high', 'sector': '科技'
    },
    '000002_万科A': {
        'file': '/root/autodl-tmp/eoh/backtest_data_extended/stock_sz_000002.csv',
        'volatility': 'high', 'sector': '地产'
    },

    # 扩展的7只A股 (Day 52数据中包含)
    '601318_中国平安': {
        'file': '/root/autodl-tmp/eoh/backtest_data_extended/stock_sh_601318.csv',
        'volatility': 'low', 'sector': '金融'
    },
    '000651_格力电器': {
        'file': '/root/autodl-tmp/eoh/backtest_data_extended/stock_sz_000651.csv',
        'volatility': 'medium', 'sector': '消费'
    },
    '600028_中国石化': {
        'file': '/root/autodl-tmp/eoh/backtest_data_extended/stock_sh_600028.csv',
        'volatility': 'medium', 'sector': '能源'
    },
    '601857_中国石油': {
        'file': '/root/autodl-tmp/eoh/backtest_data_extended/stock_sh_601857.csv',
        'volatility': 'high', 'sector': '能源'
    },
    '300059_东方财富': {
        'file': '/root/autodl-tmp/eoh/backtest_data_extended/stock_sz_300059.csv',
        'volatility': 'high', 'sector': '金融科技'
    },

    # US市场
    'SPY': {
        'file': '/root/autodl-tmp/eoh/backtest_data_extended/SPY.csv',
        'volatility': 'low', 'sector': 'US_ETF'
    },
    'QQQ': {
        'file': '/root/autodl-tmp/eoh/backtest_data_extended/QQQ.csv',
        'volatility': 'medium', 'sector': 'US_Tech_ETF'
    }
}

PERIODS = {
    'training': {'start': '2018-01-01', 'end': '2023-12-31'},
    'testing': {'start': '2024-01-01', 'end': '2024-12-31'}
}

# =============================================================================
# 策略定义 (简化版，从baseline_comparison.py复用)
# =============================================================================

class BuyAndHold(bt.Strategy):
    """买入持有策略"""
    def next(self):
        if not self.position:
            self.buy(size=20)


class SMA_Crossover(bt.Strategy):
    """简单双均线策略"""
    params = (('fast', 5), ('slow', 20))

    def __init__(self):
        self.fast_sma = bt.indicators.SMA(period=self.p.fast)
        self.slow_sma = bt.indicators.SMA(period=self.p.slow)
        self.crossover = bt.indicators.CrossOver(self.fast_sma, self.slow_sma)

    def next(self):
        if not self.position:
            if self.crossover > 0:
                self.buy(size=20)
        else:
            if self.crossover < 0:
                self.close()


class RSI_Strategy(bt.Strategy):
    """RSI策略"""
    params = (('rsi_period', 14), ('oversold', 30), ('overbought', 70))

    def __init__(self):
        self.rsi = bt.indicators.RSI(period=self.p.rsi_period)

    def next(self):
        if not self.position:
            if self.rsi < self.p.oversold:
                self.buy(size=20)
        else:
            if self.rsi > self.p.overbought:
                self.close()


class LLM_Adaptive(bt.Strategy):
    """完全自适应策略 (ATR×3 + 2%风险)"""
    params = (
        ('sma_fast', 5), ('sma_slow', 20), ('rsi_period', 7),
        ('atr_period', 14), ('atr_multiplier', 3.0), ('risk_percent', 0.02)
    )

    def __init__(self):
        self.sma_fast = bt.indicators.SMA(period=self.p.sma_fast)
        self.sma_slow = bt.indicators.SMA(period=self.p.sma_slow)
        self.rsi = bt.indicators.RSI(period=self.p.rsi_period)
        self.atr = bt.indicators.ATR(period=self.p.atr_period)
        self.crossover = bt.indicators.CrossOver(self.sma_fast, self.sma_slow)
        self.order = None
        self.entry_price = None

    def next(self):
        if self.order:
            return

        if not self.position:
            if self.crossover > 0 and self.rsi > 50:
                # 2% risk position sizing
                account_value = self.broker.getvalue()
                risk_amount = account_value * self.p.risk_percent
                atr_stop_distance = self.atr[0] * self.p.atr_multiplier
                position_size = int(risk_amount / atr_stop_distance)
                position_size = max(1, min(position_size, 100))

                self.order = self.buy(size=position_size)
                self.entry_price = self.data.close[0]
        else:
            # ATR adaptive stop-loss
            atr_stop_distance = self.atr[0] * self.p.atr_multiplier
            dynamic_stop_loss = atr_stop_distance * self.position.size
            current_loss = (self.data.close[0] - self.entry_price) * self.position.size

            if current_loss < -dynamic_stop_loss:
                self.order = self.close()

            if self.crossover < 0:
                self.order = self.close()

    def notify_order(self, order):
        if order.status in [order.Completed]:
            self.order = None
            if order.isbuy():
                self.entry_price = order.executed.price


STRATEGIES = {
    'Buy_and_Hold': BuyAndHold,
    'SMA_Crossover': SMA_Crossover,
    'RSI_Strategy': RSI_Strategy,
    'LLM_Adaptive': LLM_Adaptive
}

# =============================================================================
# 回测执行器
# =============================================================================

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
            'initial_cash': initial_cash,
            'data_points': len(df),
            'start_date': start_date,
            'end_date': end_date
        }

    except Exception as e:
        print(f"      ERROR: {str(e)}")
        return None


# =============================================================================
# 主程序
# =============================================================================

def main():
    print("=" * 80)
    print("扩展基线对比实验 - 12资产完整验证")
    print("=" * 80)
    print(f"开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"实验规模: 4策略 × 12资产 × 2时期 = 96回测")
    print("=" * 80)

    results = {}
    counter = 0
    total = len(STRATEGIES) * len(ASSETS_EXTENDED) * len(PERIODS)

    for strategy_name, strategy_class in STRATEGIES.items():
        print(f"\n[{strategy_name}]")
        results[strategy_name] = {}

        for asset_name, asset_info in ASSETS_EXTENDED.items():
            print(f"  - {asset_name}...", end=' ')
            results[strategy_name][asset_name] = {
                'volatility': asset_info['volatility'],
                'sector': asset_info['sector']
            }

            for period_name, period_dates in PERIODS.items():
                counter += 1

                result = run_backtest(
                    strategy_class=strategy_class,
                    data_path=asset_info['file'],
                    start_date=period_dates['start'],
                    end_date=period_dates['end']
                )

                if result:
                    results[strategy_name][asset_name][f'{period_name}_period'] = result
                    print(f"{period_name}:{result['returns_pct']:+.1f}% ", end='')
                else:
                    print(f"{period_name}:FAIL ", end='')

            print(f"[{counter-1}/{total}]")

    # 保存结果
    output_file = '/root/autodl-tmp/outputs/extended_baseline_results.json'
    output_data = {
        'metadata': {
            'experiment_name': 'Extended Baseline Comparison - 12 Assets',
            'timestamp': datetime.now().isoformat(),
            'total_backtests': total,
            'strategies': list(STRATEGIES.keys()),
            'assets': list(ASSETS_EXTENDED.keys())
        },
        'results': results
    }

    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, indent=2, ensure_ascii=False)

    print("\n" + "=" * 80)
    print("扩展基线对比 - 执行完成")
    print("=" * 80)
    print(f"结束时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"输出文件: {output_file}")
    print("=" * 80)


if __name__ == '__main__':
    main()
