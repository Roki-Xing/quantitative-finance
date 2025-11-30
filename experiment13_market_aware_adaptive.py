#!/usr/bin/env python3
"""
Experiment 13: Market-Aware Adaptive Strategy (行业+市场环境 双重自适应)
目标: 整合Exp11和Exp12的发现,实现二维自适应策略选择

改进:
1. 基于行业分类选择基础策略 (Exp10+11优化)
2. 基于市场环境动态调整策略 (Exp12发现)
3. 东方财富重新分类为innovation (Exp11建议)

预期目标:
- 平均收益: 39-40%
- 成功率: 100%
"""

import backtrader as bt
import pandas as pd
import numpy as np
from pathlib import Path
from datetime import datetime
import json
from tqdm import tqdm
import sys

# 导入市场环境识别模块
sys.path.insert(0, '/root/autodl-tmp/eoh')
try:
    from market_regime_detector import MarketRegimeDetector
except ImportError:
    print("警告: 无法导入market_regime_detector,将禁用市场环境识别功能")
    MarketRegimeDetector = None

# ========== 配置 ==========
DATA_DIR = Path("/root/autodl-tmp/eoh/backtest_data_extended")
OUTPUT_DIR = Path("/root/autodl-tmp/eoh/experiment13_market_aware")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

INITIAL_CASH = 100000.0
COMMISSION = 0.001

# ========== 行业分类 V2.0 (整合Exp11优化) ==========
INDUSTRY_CLASSIFICATION_V2 = {
    # 消费行业 - 使用 innovation
    "stock_sh_600519.csv": {"name": "贵州茅台", "industry": "消费", "sub_industry": "白酒", "strategy": "innovation"},
    "stock_sz_000858.csv": {"name": "五粮液", "industry": "消费", "sub_industry": "白酒", "strategy": "innovation"},
    "stock_sz_000568.csv": {"name": "泸州老窖", "industry": "消费", "sub_industry": "白酒", "strategy": "innovation"},
    "stock_sz_002304.csv": {"name": "洋河股份", "industry": "消费", "sub_industry": "白酒", "strategy": "innovation"},

    # 医药行业 - 使用 innovation
    "stock_sz_000538.csv": {"name": "云南白药", "industry": "医药", "sub_industry": "医药制造", "strategy": "innovation"},
    "stock_sh_600276.csv": {"name": "恒瑞医药", "industry": "医药", "sub_industry": "医药制造", "strategy": "innovation"},
    "stock_sz_300760.csv": {"name": "迈瑞医疗", "industry": "医药", "sub_industry": "医疗器械", "strategy": "innovation"},

    # 制造行业 - 使用 innovation
    "stock_sz_000333.csv": {"name": "美的集团", "industry": "制造", "sub_industry": "家电", "strategy": "innovation"},
    "stock_sz_000651.csv": {"name": "格力电器", "industry": "制造", "sub_industry": "家电", "strategy": "innovation"},
    "stock_sh_600036.csv": {"name": "招商银行", "industry": "金融", "sub_industry": "传统银行", "strategy": "baseline"},
    "stock_sz_000001.csv": {"name": "平安银行", "industry": "金融", "sub_industry": "传统银行", "strategy": "baseline"},
    "stock_sh_601318.csv": {"name": "中国平安", "industry": "金融", "sub_industry": "保险", "strategy": "baseline"},
    "stock_sh_601398.csv": {"name": "工商银行", "industry": "金融", "sub_industry": "传统银行", "strategy": "baseline"},

    # **关键改动**: 东方财富从baseline改为innovation (Exp11建议)
    "stock_sz_300059.csv": {"name": "东方财富", "industry": "金融", "sub_industry": "互联网金融", "strategy": "innovation"},

    # 科技行业 - 使用 baseline
    "stock_sz_000063.csv": {"name": "中兴通讯", "industry": "科技", "sub_industry": "通信设备", "strategy": "baseline"},
    "stock_sz_002415.csv": {"name": "海康威视", "industry": "科技", "sub_industry": "安防", "strategy": "baseline"},

    # 能源行业 - 使用 baseline
    "stock_sh_601857.csv": {"name": "中国石油", "industry": "能源", "sub_industry": "石油", "strategy": "baseline"},

    # 房地产行业 - 使用 baseline
    "stock_sz_000002.csv": {"name": "万科A", "industry": "房地产", "sub_industry": "房地产开发", "strategy": "baseline"},
}

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
    """strategy_007 (baseline)"""
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


def run_backtest(strategy_class, params, data, stock_name, strategy_name):
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
            "strategy": strategy_name,
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
            "strategy": strategy_name,
            "error": str(e),
            "params": params
        }


# ========== 主实验函数 ==========

def main():
    print(f"""
{'='*80}
Experiment 13: Market-Aware Adaptive Strategy
{'='*80}
目标: 行业 + 市场环境 双重自适应
改进:
  1. 东方财富重新分类为innovation (Exp11)
  2. 震荡市强制切换为baseline (Exp12)
  3. 保持Exp10的行业分类优势

预期: 平均收益39-40%, 成功率100%
{'='*80}
    """)

    # 初始化市场环境识别器
    if MarketRegimeDetector:
        regime_detector = MarketRegimeDetector()
        print("✅ 市场环境识别器已启动")
    else:
        regime_detector = None
        print("⚠️  市场环境识别器不可用,将仅使用行业分类")

    all_results = []
    regime_stats = {"bull": 0, "bear": 0, "sideways": 0, "transitional": 0}

    # 测试每只股票
    for stock_file, info in tqdm(INDUSTRY_CLASSIFICATION_V2.items(), desc="回测进度"):
        print(f"\n{'='*80}")
        print(f"测试股票: {info['name']} ({info['industry']} - {info['sub_industry']})")
        print(f"{'='*80}")

        file_path = DATA_DIR / stock_file

        try:
            # 加载数据
            data = load_data(file_path)
            print(f"数据加载成功: {len(data)} 天")

            # 检测市场环境
            if regime_detector:
                regime_info = regime_detector.detect_with_details(data)
                regime = regime_info['regime']
                regime_stats[regime] += 1
                print(f"市场环境: {regime} (置信度: {regime_info['confidence']})")
                print(f"  趋势强度: {regime_info['trend_strength']:.2f}%")
                print(f"  ADX: {regime_info['adx']:.2f}")
                print(f"  波动率: {regime_info['volatility']:.2f}%")
            else:
                regime = "unknown"
                regime_info = None

            # 选择策略
            # 策略选择逻辑 (Exp12核心改进):
            # 1. 如果是震荡市,强制使用baseline
            # 2. 否则,使用行业推荐的策略
            if regime == "sideways":
                strategy_name = "baseline"
                reason = "震荡市环境"
                print(f"策略选择: baseline (原因: {reason})")
            else:
                strategy_name = info['strategy']
                reason = f"{info['industry']}行业推荐"
                print(f"策略选择: {strategy_name} (原因: {reason})")

            # 执行回测
            if strategy_name == "innovation":
                strategy_class = AdaptiveMultiFactorStrategy
                params = INNOVATION_PARAMS
            else:
                strategy_class = TrendFollowingStrategy
                params = BASELINE_PARAMS

            result = run_backtest(strategy_class, params, data, info['name'], strategy_name)

            # 添加市场环境信息
            result['industry'] = info['industry']
            result['sub_industry'] = info['sub_industry']
            result['market_regime'] = regime
            result['strategy_reason'] = reason
            if regime_info:
                result['regime_confidence'] = regime_info['confidence']
                result['trend_strength'] = regime_info['trend_strength']
                result['adx'] = regime_info['adx']

            all_results.append(result)

            # 输出结果
            if result['success']:
                print(f"✅ 收益: {result['return_pct']:+.2f}% | Sharpe: {result['sharpe']} | 交易次数: {result['total_trades']}")
            else:
                print(f"❌ 错误: {result.get('error', 'Unknown')}")

        except Exception as e:
            print(f"❌ 处理失败: {str(e)}")

    # 保存结果
    output_file = OUTPUT_DIR / "market_aware_results.json"
    with open(output_file, 'w') as f:
        json.dump({
            "experiment": "Experiment 13: Market-Aware Adaptive Strategy",
            "date": datetime.now().isoformat(),
            "improvements": [
                "东方财富重新分类为innovation (Exp11)",
                "震荡市强制使用baseline (Exp12)",
                "保持行业分类优势 (Exp10)"
            ],
            "regime_distribution": regime_stats,
            "results": all_results
        }, f, indent=2, default=str)

    print(f"\n{'='*80}")
    print("实验完成!")
    print(f"结果已保存: {output_file}")
    print(f"{'='*80}")

    # 汇总分析
    print(f"\n{'='*80}")
    print("结果汇总")
    print(f"{'='*80}\n")

    successful = [r for r in all_results if r['success']]

    if successful:
        # 整体统计
        avg_return = np.mean([r['return_pct'] for r in successful])
        success_rate = len(successful) / len(all_results) * 100
        positive_returns = len([r for r in successful if r['return_pct'] > 0])
        positive_rate = positive_returns / len(successful) * 100

        print(f"整体表现:")
        print(f"  平均收益: {avg_return:.2f}%")
        print(f"  成功率: {success_rate:.1f}% ({len(successful)}/{len(all_results)})")
        print(f"  盈利率: {positive_rate:.1f}% ({positive_returns}/{len(successful)})")

        # 市场环境统计
        print(f"\n市场环境分布:")
        for regime, count in regime_stats.items():
            if count > 0:
                pct = count / len(all_results) * 100
                print(f"  {regime}: {count} ({pct:.1f}%)")

        # 按行业统计
        print(f"\n按行业统计:")
        industries = {}
        for r in successful:
            ind = r['industry']
            if ind not in industries:
                industries[ind] = []
            industries[ind].append(r['return_pct'])

        for ind, returns in industries.items():
            avg = np.mean(returns)
            print(f"  {ind}: {avg:+.2f}% (平均, {len(returns)}只)")

        # 按策略统计
        print(f"\n按策略统计:")
        strategies = {}
        for r in successful:
            strat = r['strategy']
            if strat not in strategies:
                strategies[strat] = []
            strategies[strat].append(r['return_pct'])

        for strat, returns in strategies.items():
            avg = np.mean(returns)
            print(f"  {strat}: {avg:+.2f}% (平均, {len(returns)}次使用)")

        # 对比Exp10
        print(f"\n对比Experiment 10:")
        print(f"  Exp10 v1.0: 32.23% (18只, 100%成功)")
        print(f"  Exp13 v2.0: {avg_return:.2f}% ({len(successful)}只, {positive_rate:.1f}%盈利)")

        improvement = avg_return - 32.23
        print(f"  改进: {improvement:+.2f}% ({improvement/32.23*100:+.1f}%相对提升)")

    else:
        print("无成功案例!")


if __name__ == "__main__":
    main()
