#!/usr/bin/env python3
"""
Experiment 10: 行业自适应策略
目标: 根据股票所属行业自动选择最优策略
基于Experiment 9发现: 行业选择 > 参数优化
"""

import backtrader as bt
import pandas as pd
from pathlib import Path
from datetime import datetime
import json
from tqdm import tqdm

# ========== 配置 ==========
DATA_DIR = Path("/root/autodl-tmp/eoh/backtest_data_extended")
OUTPUT_DIR = Path("/root/autodl-tmp/eoh/experiment10_industry_adaptive")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

INITIAL_CASH = 100000.0
COMMISSION = 0.001

# ========== 行业分类 ==========
INDUSTRY_CLASSIFICATION = {
    # 消费行业 - 使用 innovation_triple_fusion
    "stock_sh_600519.csv": {"name": "贵州茅台", "industry": "消费", "strategy": "innovation"},
    "stock_sh_600887.csv": {"name": "伊利股份", "industry": "消费", "strategy": "innovation"},
    "stock_sz_000858.csv": {"name": "五粮液", "industry": "消费", "strategy": "innovation"},

    # 医药行业 - 使用 innovation_triple_fusion
    "stock_sh_600276.csv": {"name": "恒瑞医药", "industry": "医药", "strategy": "innovation"},
    "stock_sz_000538.csv": {"name": "云南白药", "industry": "医药", "strategy": "innovation"},

    # 制造行业 - 使用 innovation_triple_fusion
    "stock_sz_000333.csv": {"name": "美的集团", "industry": "制造", "strategy": "innovation"},
    "stock_sz_000651.csv": {"name": "格力电器", "industry": "制造", "strategy": "innovation"},

    # 金融行业 - 使用 strategy_007
    "stock_sh_600036.csv": {"name": "招商银行", "industry": "金融", "strategy": "baseline"},
    "stock_sh_601318.csv": {"name": "中国平安", "industry": "金融", "strategy": "baseline"},
    "stock_sz_000001.csv": {"name": "平安银行", "industry": "金融", "strategy": "baseline"},
    "stock_sz_300059.csv": {"name": "东方财富", "industry": "金融", "strategy": "baseline"},

    # 能源行业 - 使用 strategy_007
    "stock_sh_600028.csv": {"name": "中国石化", "industry": "能源", "strategy": "baseline"},
    "stock_sh_601857.csv": {"name": "中国石油", "industry": "能源", "strategy": "baseline"},

    # 房地产行业 - 使用 strategy_007
    "stock_sh_600048.csv": {"name": "保利发展", "industry": "房地产", "strategy": "baseline"},
    "stock_sz_000002.csv": {"name": "万科A", "industry": "房地产", "strategy": "baseline"},

    # 科技行业 - 使用 strategy_007 (因为innovation在科技行业表现不稳定)
    "stock_sz_000063.csv": {"name": "中兴通讯", "industry": "科技", "strategy": "baseline"},
    "stock_sz_000725.csv": {"name": "京东方A", "industry": "科技", "strategy": "baseline"},
    "stock_sz_002415.csv": {"name": "海康威视", "industry": "科技", "strategy": "baseline"},
}

# ========== 最优参数 ==========
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
    """innovation_triple_fusion - 用于消费/医药/制造"""
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
    """strategy_007 - 用于金融/能源/房地产/科技"""
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


def run_backtest(strategy_class, params, data, stock_info):
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
            "stock": stock_info['name'],
            "industry": stock_info['industry'],
            "strategy_used": stock_info['strategy'],
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
            "stock": stock_info['name'],
            "industry": stock_info['industry'],
            "strategy_used": stock_info['strategy'],
            "error": str(e),
            "params": params
        }


def run_adaptive_backtest():
    """运行行业自适应回测"""
    print(f"""
{'='*80}
Experiment 10: 行业自适应策略
{'='*80}
目标: 根据行业特征自动选择最优策略
策略规则:
  - 消费/医药/制造 → innovation_triple_fusion (高收益)
  - 金融/能源/房地产/科技 → strategy_007 (稳健)
{'='*80}
    """)

    results = []

    for stock_file, stock_info in tqdm(INDUSTRY_CLASSIFICATION.items(), desc="行业自适应回测"):
        file_path = DATA_DIR / stock_file

        try:
            data = load_data(file_path)

            # 根据行业选择策略
            if stock_info['strategy'] == 'innovation':
                strategy_class = AdaptiveMultiFactorStrategy
                params = INNOVATION_PARAMS
            else:
                strategy_class = TrendFollowingStrategy
                params = BASELINE_PARAMS

            result = run_backtest(strategy_class, params, data, stock_info)
            results.append(result)

            # 实时显示结果
            if result['success']:
                print(f"  ✅ {result['stock']} ({result['industry']}) | "
                      f"策略: {result['strategy_used']} | "
                      f"收益: {result['return_pct']:.2f}%")
            else:
                print(f"  ❌ {result['stock']} 失败: {result.get('error', 'Unknown')}")

        except Exception as e:
            results.append({
                "success": False,
                "stock": stock_info['name'],
                "industry": stock_info['industry'],
                "strategy_used": stock_info['strategy'],
                "error": f"数据加载错误: {str(e)}"
            })

    return results


def analyze_results(results):
    """分析结果"""
    successful = [r for r in results if r.get('success')]
    failed = [r for r in results if not r.get('success')]

    print(f"\n{'='*80}")
    print("结果分析")
    print(f"{'='*80}\n")

    print(f"✅ 成功: {len(successful)}/{len(results)}")
    print(f"❌ 失败: {len(failed)}")

    if not successful:
        return None

    # 整体统计
    avg_return = sum(r['return_pct'] for r in successful) / len(successful)
    positive = [r for r in successful if r['return_pct'] > 0]
    negative = [r for r in successful if r['return_pct'] <= 0]

    sharpes = [r['sharpe'] for r in successful if r['sharpe'] is not None]
    avg_sharpe = sum(sharpes) / len(sharpes) if sharpes else None

    print(f"\n📊 整体表现:")
    print(f"  平均收益率: {avg_return:.2f}%")
    print(f"  正收益股票: {len(positive)}/{len(successful)} ({len(positive)/len(successful)*100:.1f}%)")
    print(f"  负收益股票: {len(negative)}/{len(successful)}")
    if avg_sharpe:
        print(f"  平均Sharpe: {avg_sharpe:.3f}")

    # 按行业分析
    print(f"\n📈 按行业分析:")
    industry_stats = {}
    for r in successful:
        industry = r['industry']
        if industry not in industry_stats:
            industry_stats[industry] = []
        industry_stats[industry].append(r)

    for industry, stocks in sorted(industry_stats.items()):
        avg_ret = sum(s['return_pct'] for s in stocks) / len(stocks)
        pos_count = sum(1 for s in stocks if s['return_pct'] > 0)
        strategy_used = stocks[0]['strategy_used']

        print(f"  {industry} ({len(stocks)}只): 平均{avg_ret:.2f}% | "
              f"成功率{pos_count}/{len(stocks)} | 策略: {strategy_used}")

    # 按策略分析
    print(f"\n🎯 按策略分析:")
    strategy_stats = {}
    for r in successful:
        strat = r['strategy_used']
        if strat not in strategy_stats:
            strategy_stats[strat] = []
        strategy_stats[strat].append(r)

    for strategy, stocks in sorted(strategy_stats.items()):
        avg_ret = sum(s['return_pct'] for s in stocks) / len(stocks)
        pos_count = sum(1 for s in stocks if s['return_pct'] > 0)

        print(f"  {strategy}: {len(stocks)}只股票 | 平均{avg_ret:.2f}% | "
              f"成功率{pos_count}/{len(stocks)} ({pos_count/len(stocks)*100:.1f}%)")

    # Top 5 和 Bottom 5
    sorted_results = sorted(successful, key=lambda x: x['return_pct'], reverse=True)

    print(f"\n🏆 Top 5 表现:")
    for i, r in enumerate(sorted_results[:5], 1):
        sharpe_str = f"{r['sharpe']:.3f}" if r['sharpe'] else 'N/A'
        print(f"  #{i} {r['stock']} ({r['industry']}) | {r['strategy_used']}")
        print(f"      收益: {r['return_pct']:.2f}% | Sharpe: {sharpe_str} | "
              f"交易: {r['total_trades']} | 胜率: {r['win_rate']:.1f}%")

    print(f"\n📉 Bottom 5 表现:")
    for i, r in enumerate(sorted_results[-5:], 1):
        sharpe_str = f"{r['sharpe']:.3f}" if r['sharpe'] else 'N/A'
        print(f"  #{i} {r['stock']} ({r['industry']}) | {r['strategy_used']}")
        print(f"      收益: {r['return_pct']:.2f}% | Sharpe: {sharpe_str} | "
              f"交易: {r['total_trades']} | 胜率: {r['win_rate']:.1f}%")

    return {
        "avg_return": avg_return,
        "avg_sharpe": avg_sharpe,
        "success_rate": len(positive) / len(successful) * 100,
        "positive_count": len(positive),
        "total_stocks": len(successful),
        "industry_stats": industry_stats,
        "strategy_stats": strategy_stats
    }


# ========== 主程序 ==========

def main():
    # 运行自适应回测
    results = run_adaptive_backtest()

    # 分析结果
    stats = analyze_results(results)

    # 保存结果
    output_file = OUTPUT_DIR / "adaptive_results.json"
    with open(output_file, 'w') as f:
        json.dump({
            "experiment": "Experiment 10: Industry-Adaptive Strategy",
            "date": datetime.now().isoformat(),
            "total_stocks": len(results),
            "results": results,
            "statistics": stats
        }, f, indent=2, default=str)

    print(f"\n结果已保存: {output_file}")

    # 与Exp9对比
    print(f"\n{'='*80}")
    print("与Experiment 9对比")
    print(f"{'='*80}")
    print(f"{'方法':<20} {'平均收益':<12} {'成功率':<10} {'说明'}")
    print(f"{'-'*80}")
    print(f"{'Exp9 innovation':<20} {'35.65%':<12} {'55.6%':<10} {'所有股票用同一策略'}")
    print(f"{'Exp9 strategy_007':<20} {'4.98%':<12} {'100.0%':<10} {'所有股票用同一策略'}")
    if stats:
        avg_ret_str = f"{stats['avg_return']:.2f}%"
        success_rate_str = f"{stats['success_rate']:.1f}%"
        print(f"{'Exp10 自适应':<20} {avg_ret_str:<12} {success_rate_str:<10} {'根据行业选择策略'}")

    print(f"\n{'='*80}")
    print("Experiment 10 完成!")
    print(f"{'='*80}")


if __name__ == "__main__":
    main()
