"""
交易成本敏感性分析
===================

目的: 证明策略在不同手续费率下的稳健性

实验设计:
- 4个费率档位: 0.10%, 0.15%, 0.20%, 0.30%
- 5个核心资产 (茅台, 五粮液, 招行, 京东方, 万科A)
- 2个时期 (训练期, 测试期)
- 总计: 4 × 5 × 2 = 40回测

策略: LLM_Adaptive (完全自适应)
"""

import backtrader as bt
import pandas as pd
import json
from datetime import datetime
from pathlib import Path

# =============================================================================
# 配置
# =============================================================================

COMMISSION_RATES = [0.001, 0.0015, 0.002, 0.003]  # 0.10%, 0.15%, 0.20%, 0.30%

ASSETS = {
    '600519_贵州茅台': {
        'file': '/root/autodl-tmp/eoh/backtest_data_extended/stock_sh_600519.csv',
        'volatility': 'low'
    },
    '000858_五粮液': {
        'file': '/root/autodl-tmp/eoh/backtest_data_extended/stock_sz_000858.csv',
        'volatility': 'medium'
    },
    '600036_招商银行': {
        'file': '/root/autodl-tmp/eoh/backtest_data_extended/stock_sh_600036.csv',
        'volatility': 'low'
    },
    '000725_京东方': {
        'file': '/root/autodl-tmp/eoh/backtest_data_extended/stock_sz_000725.csv',
        'volatility': 'high'
    },
    '000002_万科A': {
        'file': '/root/autodl-tmp/eoh/backtest_data_extended/stock_sz_000002.csv',
        'volatility': 'high'
    }
}

PERIODS = {
    'training': {'start': '2018-01-01', 'end': '2023-12-31'},
    'testing': {'start': '2024-01-01', 'end': '2024-12-31'}
}

# =============================================================================
# 策略定义
# =============================================================================

class LLM_Adaptive(bt.Strategy):
    """完全自适应策略"""
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
                account_value = self.broker.getvalue()
                risk_amount = account_value * self.p.risk_percent
                atr_stop_distance = self.atr[0] * self.p.atr_multiplier
                position_size = int(risk_amount / atr_stop_distance)
                position_size = max(1, min(position_size, 100))

                self.order = self.buy(size=position_size)
                self.entry_price = self.data.close[0]
        else:
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


# =============================================================================
# 回测执行器
# =============================================================================

def run_backtest(commission_rate, data_path, start_date, end_date, initial_cash=100000):
    """运行单个回测"""
    try:
        df = pd.read_csv(data_path, parse_dates=['date'])
        df = df[(df['date'] >= start_date) & (df['date'] <= end_date)]

        if len(df) < 50:
            return None

        cerebro = bt.Cerebro()
        cerebro.broker.setcash(initial_cash)
        cerebro.broker.setcommission(commission=commission_rate)  # 关键参数

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
        cerebro.addstrategy(LLM_Adaptive)

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
            'commission_rate': commission_rate,
            'initial_cash': initial_cash,
            'data_points': len(df)
        }

    except Exception as e:
        print(f"    ERROR: {str(e)}")
        return None


# =============================================================================
# 主程序
# =============================================================================

def main():
    print("=" * 80)
    print("交易成本敏感性分析")
    print("=" * 80)
    print(f"开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"实验规模: 4费率 × 5资产 × 2时期 = 40回测")
    print("=" * 80)

    results = {}
    counter = 0
    total = len(COMMISSION_RATES) * len(ASSETS) * len(PERIODS)

    for commission_rate in COMMISSION_RATES:
        rate_key = f"Commission_{commission_rate*100:.2f}%"
        print(f"\n[{rate_key}]")
        results[rate_key] = {}

        for asset_name, asset_info in ASSETS.items():
            print(f"  - {asset_name}...")
            results[rate_key][asset_name] = {'volatility': asset_info['volatility']}

            for period_name, period_dates in PERIODS.items():
                counter += 1
                print(f"    [{counter}/{total}] {period_name}...", end=' ')

                result = run_backtest(
                    commission_rate=commission_rate,
                    data_path=asset_info['file'],
                    start_date=period_dates['start'],
                    end_date=period_dates['end']
                )

                if result:
                    results[rate_key][asset_name][f'{period_name}_period'] = result
                    print(f"OK ({result['returns_pct']:+.2f}%)")
                else:
                    print("FAILED")

    # 保存结果
    output_file = '/root/autodl-tmp/outputs/transaction_cost_sensitivity.json'

    output_data = {
        'metadata': {
            'experiment_name': 'Transaction Cost Sensitivity Analysis',
            'timestamp': datetime.now().isoformat(),
            'total_backtests': total,
            'commission_rates': COMMISSION_RATES,
            'assets': list(ASSETS.keys())
        },
        'results': results
    }

    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, indent=2, ensure_ascii=False)

    print("\n" + "=" * 80)
    print("交易成本敏感性分析 - 执行完成")
    print("=" * 80)
    print(f"结束时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"输出文件: {output_file}")
    print(f"文件大小: {Path(output_file).stat().st_size / 1024:.1f} KB")
    print("=" * 80)


if __name__ == '__main__':
    main()
