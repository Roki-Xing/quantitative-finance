"""
在新数据上运行Adaptive策略 (无需LLM!)
========================================

功能:
- 读取新的股票数据CSV
- 运行已有的Adaptive策略
- 输出回测结果

使用方法:
python run_strategy_on_new_data.py \
  --data /path/to/new_stock.csv \
  --train-start 2020-01-01 \
  --train-end 2023-12-31 \
  --test-start 2024-01-01 \
  --test-end 2024-12-31
"""

import backtrader as bt
import pandas as pd
import argparse
from datetime import datetime

# ============================================================================
# Adaptive Strategy #13 (来自LLM生成 + 人工改进参数)
# ============================================================================

class Adaptive_Strategy_13(bt.Strategy):
    """
    LLM生成的交易逻辑 + 自适应参数框架

    逻辑 (来自Llama-3.1-8B):
    - SMA(20/50) 交叉
    - RSI(14) 过滤

    参数 (人工改进):
    - ATR × 3 动态止损
    - 2% 风险仓位管理
    """
    params = (
        ('sma_fast', 20),
        ('sma_slow', 50),
        ('rsi_period', 14),
        ('rsi_low', 30),
        ('rsi_high', 70),
        ('atr_period', 14),
        ('atr_multiplier', 3.0),
        ('risk_per_trade', 0.02),  # 2% risk
    )

    def __init__(self):
        # LLM生成的指标
        self.sma_fast = bt.indicators.SMA(period=self.p.sma_fast)
        self.sma_slow = bt.indicators.SMA(period=self.p.sma_slow)
        self.rsi = bt.indicators.RSI(period=self.p.rsi_period)

        # 人工添加的自适应指标
        self.atr = bt.indicators.ATR(period=self.p.atr_period)

        self.order = None
        self.buy_price = None

    def next(self):
        if self.order:
            return

        # LLM生成的交易逻辑
        if not self.position:
            # 买入条件: SMA金叉 + RSI超卖
            if (self.sma_fast[0] > self.sma_slow[0] and
                self.sma_fast[-1] <= self.sma_slow[-1] and
                self.rsi[0] < self.p.rsi_high):

                # 人工改进的仓位计算 (2%风险)
                risk_amount = self.broker.getvalue() * self.p.risk_per_trade
                stop_distance = self.atr[0] * self.p.atr_multiplier

                if stop_distance > 0:
                    size = int(risk_amount / stop_distance)
                    if size > 0:
                        self.order = self.buy(size=size)
                        self.buy_price = self.data.close[0]

        else:
            # 卖出条件1: SMA死叉
            if (self.sma_fast[0] < self.sma_slow[0] and
                self.sma_fast[-1] >= self.sma_slow[-1]):
                self.order = self.close()

            # 卖出条件2: ATR动态止损
            elif self.buy_price is not None:
                stop_loss = self.buy_price - (self.atr[0] * self.p.atr_multiplier)
                if self.data.close[0] < stop_loss:
                    self.order = self.close()

            # 卖出条件3: RSI超买
            elif self.rsi[0] > self.p.rsi_high:
                self.order = self.close()

    def notify_order(self, order):
        if order.status in [order.Completed, order.Canceled, order.Margin]:
            self.order = None
            if order.isbuy():
                self.buy_price = order.executed.price


# ============================================================================
# 回测执行函数
# ============================================================================

def run_backtest(data_path, train_start, train_end, test_start, test_end,
                 initial_cash=100000):
    """
    在新数据上运行Adaptive策略

    参数:
        data_path: CSV数据路径
        train_start/end: 训练期日期
        test_start/end: 测试期日期
        initial_cash: 初始资金

    返回:
        dict: 回测结果
    """

    print("=" * 80)
    print(f"运行Adaptive策略 on {data_path}")
    print("=" * 80)

    # 读取数据
    df = pd.read_csv(data_path, parse_dates=['date'])

    results = {}

    # 训练期回测
    print("\n[1/2] 训练期回测...")
    train_df = df[(df['date'] >= train_start) & (df['date'] <= train_end)]

    if len(train_df) >= 50:
        cerebro_train = bt.Cerebro()
        cerebro_train.broker.setcash(initial_cash)
        cerebro_train.broker.setcommission(commission=0.0015)

        data_feed = bt.feeds.PandasData(
            dataname=train_df,
            datetime='date',
            open='open',
            high='high',
            low='low',
            close='close',
            volume='volume',
            openinterest=-1
        )

        cerebro_train.adddata(data_feed)
        cerebro_train.addstrategy(Adaptive_Strategy_13)
        cerebro_train.addanalyzer(bt.analyzers.SharpeRatio, _name='sharpe')
        cerebro_train.addanalyzer(bt.analyzers.DrawDown, _name='drawdown')
        cerebro_train.addanalyzer(bt.analyzers.TradeAnalyzer, _name='trades')

        train_results = cerebro_train.run()
        final_value_train = cerebro_train.broker.getvalue()

        sharpe_train = train_results[0].analyzers.sharpe.get_analysis()
        dd_train = train_results[0].analyzers.drawdown.get_analysis()
        trades_train = train_results[0].analyzers.trades.get_analysis()

        results['training'] = {
            'returns_pct': round(((final_value_train - initial_cash) / initial_cash) * 100, 2),
            'final_value': round(final_value_train, 2),
            'sharpe_ratio': round(sharpe_train.get('sharperatio', 0) or 0, 3),
            'max_drawdown_pct': round(dd_train.get('max', {}).get('drawdown', 0), 2),
            'total_trades': trades_train.get('total', {}).get('closed', 0),
        }

        print(f"  训练期收益: {results['training']['returns_pct']:+.2f}%")
        print(f"  夏普比率: {results['training']['sharpe_ratio']:.3f}")
        print(f"  最大回撤: {results['training']['max_drawdown_pct']:.2f}%")
        print(f"  交易次数: {results['training']['total_trades']}")

    # 测试期回测
    print("\n[2/2] 测试期回测...")
    test_df = df[(df['date'] >= test_start) & (df['date'] <= test_end)]

    if len(test_df) >= 50:
        cerebro_test = bt.Cerebro()
        cerebro_test.broker.setcash(initial_cash)
        cerebro_test.broker.setcommission(commission=0.0015)

        data_feed = bt.feeds.PandasData(
            dataname=test_df,
            datetime='date',
            open='open',
            high='high',
            low='low',
            close='close',
            volume='volume',
            openinterest=-1
        )

        cerebro_test.adddata(data_feed)
        cerebro_test.addstrategy(Adaptive_Strategy_13)
        cerebro_test.addanalyzer(bt.analyzers.SharpeRatio, _name='sharpe')
        cerebro_test.addanalyzer(bt.analyzers.DrawDown, _name='drawdown')
        cerebro_test.addanalyzer(bt.analyzers.TradeAnalyzer, _name='trades')

        test_results = cerebro_test.run()
        final_value_test = cerebro_test.broker.getvalue()

        sharpe_test = test_results[0].analyzers.sharpe.get_analysis()
        dd_test = test_results[0].analyzers.drawdown.get_analysis()
        trades_test = test_results[0].analyzers.trades.get_analysis()

        results['testing'] = {
            'returns_pct': round(((final_value_test - initial_cash) / initial_cash) * 100, 2),
            'final_value': round(final_value_test, 2),
            'sharpe_ratio': round(sharpe_test.get('sharperatio', 0) or 0, 3),
            'max_drawdown_pct': round(dd_test.get('max', {}).get('drawdown', 0), 2),
            'total_trades': trades_test.get('total', {}).get('closed', 0),
        }

        print(f"  测试期收益: {results['testing']['returns_pct']:+.2f}%")
        print(f"  夏普比率: {results['testing']['sharpe_ratio']:.3f}")
        print(f"  最大回撤: {results['testing']['max_drawdown_pct']:.2f}%")
        print(f"  交易次数: {results['testing']['total_trades']}")

    print("\n" + "=" * 80)
    return results


# ============================================================================
# 命令行接口
# ============================================================================

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='在新数据上运行Adaptive策略')

    parser.add_argument('--data', required=True, help='CSV数据文件路径')
    parser.add_argument('--train-start', default='2020-01-01', help='训练期开始日期')
    parser.add_argument('--train-end', default='2023-12-31', help='训练期结束日期')
    parser.add_argument('--test-start', default='2024-01-01', help='测试期开始日期')
    parser.add_argument('--test-end', default='2024-12-31', help='测试期结束日期')
    parser.add_argument('--cash', type=float, default=100000, help='初始资金')

    args = parser.parse_args()

    results = run_backtest(
        data_path=args.data,
        train_start=args.train_start,
        train_end=args.train_end,
        test_start=args.test_start,
        test_end=args.test_end,
        initial_cash=args.cash
    )

    # 保存结果
    import json
    output_file = args.data.replace('.csv', '_results.json')
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

    print(f"\n结果已保存到: {output_file}")
