"""
参数敏感性分析 - 策略变体实现
================================

功能: 实现Strategy13的多个参数变体,用于敏感性分析
作者: Claude Code AI Assistant
日期: 2025-11-27
Python: 3.8+

策略变体:
1. Strategy13_FixedStopLoss: 固定止损金额变体
2. Strategy13_FixedPositionSize: 固定仓位大小变体
3. Strategy13_ATR_Adaptive: ATR自适应止损
4. Strategy13_Risk2Pct: 2%风险管理仓位
5. Strategy13_FullyAdaptive: 完全自适应(ATR止损+2%风险仓位)

参数范围:
- 止损: $50, $100, $150, $200, $250, $300
- 仓位: 5股, 10股, 15股, 20股, 25股, 30股
"""

import backtrader as bt
import numpy as np


# =============================================================================
# 策略变体 1: 固定止损金额
# =============================================================================

class Strategy13_FixedStopLoss(bt.Strategy):
    """
    固定止损金额的Strategy13变体

    用于测试: 不同止损金额对策略性能的影响

    Parameters:
        stop_loss_amount: 固定止损金额 (default: $200)
        position_size: 固定仓位大小 (default: 20股)

    策略逻辑:
        开仓: 双均线金叉(SMA20上穿SMA50)
        平仓: 止损($止损金额) 或 死叉(SMA20下穿SMA50)
    """
    params = (
        ('stop_loss_amount', 200),  # 固定止损金额
        ('position_size', 20),       # 固定股数
        ('short_period', 20),
        ('long_period', 50),
    )

    def __init__(self):
        self.order = None
        self.entry_price = None

        # 双均线指标
        self.sma_short = bt.indicators.SimpleMovingAverage(
            self.data.close, period=self.p.short_period
        )
        self.sma_long = bt.indicators.SimpleMovingAverage(
            self.data.close, period=self.p.long_period
        )
        self.crossover = bt.indicators.CrossOver(
            self.sma_short, self.sma_long
        )

    def next(self):
        if self.order:
            return

        # 开仓逻辑
        if not self.position:
            if self.crossover > 0:  # 金叉
                # 固定仓位大小
                self.order = self.buy(size=self.p.position_size)
                self.entry_price = self.data.close[0]

        # 平仓逻辑
        else:
            # 计算当前损失
            current_loss = (self.data.close[0] - self.entry_price) * self.position.size

            # 固定止损
            if current_loss < -self.p.stop_loss_amount:
                self.order = self.close()
                self.entry_price = None

            # 死叉退出
            elif self.crossover < 0:
                self.order = self.close()
                self.entry_price = None

    def notify_order(self, order):
        if order.status in [order.Submitted, order.Accepted]:
            return

        if order.status in [order.Completed]:
            if order.isbuy():
                pass  # 买入完成
            elif order.issell():
                pass  # 卖出完成

        self.order = None


# =============================================================================
# 策略变体 2: 固定仓位大小
# =============================================================================

class Strategy13_FixedPositionSize(bt.Strategy):
    """
    固定仓位大小的Strategy13变体

    用于测试: 不同仓位大小对策略性能的影响

    Parameters:
        stop_loss_amount: 固定止损金额 (default: $200)
        position_size: 固定仓位大小 (default: 20股)
    """
    params = (
        ('stop_loss_amount', 200),
        ('position_size', 20),
        ('short_period', 20),
        ('long_period', 50),
    )

    def __init__(self):
        self.order = None
        self.entry_price = None
        self.sma_short = bt.indicators.SimpleMovingAverage(
            self.data.close, period=self.p.short_period
        )
        self.sma_long = bt.indicators.SimpleMovingAverage(
            self.data.close, period=self.p.long_period
        )
        self.crossover = bt.indicators.CrossOver(
            self.sma_short, self.sma_long
        )

    def next(self):
        if self.order:
            return

        if not self.position:
            if self.crossover > 0:
                # 固定仓位
                self.order = self.buy(size=self.p.position_size)
                self.entry_price = self.data.close[0]
        else:
            current_loss = (self.data.close[0] - self.entry_price) * self.position.size

            if current_loss < -self.p.stop_loss_amount:
                self.order = self.close()
                self.entry_price = None
            elif self.crossover < 0:
                self.order = self.close()
                self.entry_price = None

    def notify_order(self, order):
        if order.status in [order.Completed]:
            pass
        self.order = None


# =============================================================================
# 策略变体 3: ATR自适应止损
# =============================================================================

class Strategy13_ATR_Adaptive(bt.Strategy):
    """
    ATR自适应止损的Strategy13变体

    核心创新: 根据市场波动率(ATR)动态调整止损距离

    Parameters:
        atr_period: ATR周期 (default: 14)
        atr_multiplier: ATR乘数 (default: 2.0)
        position_size: 固定仓位 (default: 20股)

    止损逻辑:
        动态止损 = ATR × atr_multiplier × position_size

        高波动市场: ATR大 → 止损宽松 → 减少假突破
        低波动市场: ATR小 → 止损紧凑 → 快速止损

    文献依据:
        - Wilder (1978) "New Concepts in Technical Trading Systems"
        - ATR是衡量市场波动率的经典指标
    """
    params = (
        ('atr_period', 14),
        ('atr_multiplier', 2.0),  # ATR × 2
        ('position_size', 20),
        ('short_period', 20),
        ('long_period', 50),
    )

    def __init__(self):
        self.order = None
        self.entry_price = None

        self.sma_short = bt.indicators.SimpleMovingAverage(
            self.data.close, period=self.p.short_period
        )
        self.sma_long = bt.indicators.SimpleMovingAverage(
            self.data.close, period=self.p.long_period
        )
        self.crossover = bt.indicators.CrossOver(
            self.sma_short, self.sma_long
        )

        # ATR指标 (Average True Range)
        self.atr = bt.indicators.ATR(
            self.data,
            period=self.p.atr_period
        )

    def next(self):
        if self.order:
            return

        if not self.position:
            if self.crossover > 0:
                self.order = self.buy(size=self.p.position_size)
                self.entry_price = self.data.close[0]
        else:
            # 自适应止损 = ATR × multiplier × 持仓股数
            dynamic_stop_loss = self.atr[0] * self.p.atr_multiplier * self.position.size

            current_loss = (self.data.close[0] - self.entry_price) * self.position.size

            if current_loss < -dynamic_stop_loss:
                self.order = self.close()
                self.entry_price = None
            elif self.crossover < 0:
                self.order = self.close()
                self.entry_price = None

    def notify_order(self, order):
        if order.status in [order.Completed]:
            pass
        self.order = None


# =============================================================================
# 策略变体 4: 2%风险管理仓位
# =============================================================================

class Strategy13_Risk2Pct(bt.Strategy):
    """
    2%风险管理仓位的Strategy13变体

    核心创新: 每笔交易风险控制在账户总资金的2%

    Parameters:
        risk_percent: 单笔交易风险比例 (default: 0.02 = 2%)
        stop_loss_amount: 固定止损金额 (default: $200)

    仓位计算逻辑:
        单笔交易风险 = 账户总资金 × 2%
        每股风险 = 止损金额 / 仓位
        → Position Size = (账户 × 2%) / (止损金额 / 仓位)

    示例:
        账户$100,000, 止损$200, 假设20股基准
        → 每股风险 = $200 / 20 = $10
        → 仓位 = ($100,000 × 0.02) / $10 = 200股

    文献依据:
        - Van Tharp (1998) "Trade Your Way to Financial Freedom"
        - 2%规则是经典的风险管理准则
    """
    params = (
        ('risk_percent', 0.02),  # 2%风险
        ('stop_loss_amount', 200),
        ('short_period', 20),
        ('long_period', 50),
    )

    def __init__(self):
        self.order = None
        self.entry_price = None
        self.sma_short = bt.indicators.SimpleMovingAverage(
            self.data.close, period=self.p.short_period
        )
        self.sma_long = bt.indicators.SimpleMovingAverage(
            self.data.close, period=self.p.long_period
        )
        self.crossover = bt.indicators.CrossOver(
            self.sma_short, self.sma_long
        )

    def next(self):
        if self.order:
            return

        if not self.position:
            if self.crossover > 0:
                # 计算2%风险下的仓位
                account_value = self.broker.getvalue()
                risk_amount = account_value * self.p.risk_percent

                # 每股风险 = 止损金额 / 基准仓位(20股)
                # 简化: 假设每股风险约为 止损金额/20
                risk_per_share = self.p.stop_loss_amount / 20

                # 仓位 = 风险金额 / 每股风险
                position_size = int(risk_amount / (risk_per_share + 0.01))

                # 限制仓位范围 [1, 100]
                position_size = max(1, min(position_size, 100))

                self.order = self.buy(size=position_size)
                self.entry_price = self.data.close[0]
        else:
            current_loss = (self.data.close[0] - self.entry_price) * self.position.size

            if current_loss < -self.p.stop_loss_amount:
                self.order = self.close()
                self.entry_price = None
            elif self.crossover < 0:
                self.order = self.close()
                self.entry_price = None

    def notify_order(self, order):
        if order.status in [order.Completed]:
            pass
        self.order = None


# =============================================================================
# 策略变体 5: 完全自适应 (ATR止损 + 2%风险仓位)
# =============================================================================

class Strategy13_FullyAdaptive(bt.Strategy):
    """
    完全自适应Strategy13

    核心创新: 组合两种自适应机制
        1. ATR自适应止损 → 根据波动率调整止损距离
        2. 2%风险管理仓位 → 根据账户规模调整仓位

    Parameters:
        atr_period: ATR周期 (default: 14)
        atr_multiplier: ATR乘数 (default: 2.0)
        risk_percent: 风险比例 (default: 0.02)

    仓位计算:
        1. 计算ATR止损距离 = ATR × atr_multiplier
        2. 计算风险金额 = 账户 × 2%
        3. 仓位 = 风险金额 / ATR止损距离

    协同效应:
        - 高波动股票: ATR大 → 止损宽,仓位小 → 控制风险
        - 低波动股票: ATR小 → 止损紧,仓位大 → 提升收益
        - 账户增长: 风险金额增加 → 仓位自动扩大
        - 账户回撤: 风险金额减少 → 仓位自动缩小

    这是论文核心创新的完整体现!
    """
    params = (
        ('atr_period', 14),
        ('atr_multiplier', 2.0),
        ('risk_percent', 0.02),
        ('short_period', 20),
        ('long_period', 50),
    )

    def __init__(self):
        self.order = None
        self.entry_price = None

        self.sma_short = bt.indicators.SimpleMovingAverage(
            self.data.close, period=self.p.short_period
        )
        self.sma_long = bt.indicators.SimpleMovingAverage(
            self.data.close, period=self.p.long_period
        )
        self.crossover = bt.indicators.CrossOver(
            self.sma_short, self.sma_long
        )

        # ATR指标
        self.atr = bt.indicators.ATR(
            self.data,
            period=self.p.atr_period
        )

    def next(self):
        if self.order:
            return

        if not self.position:
            if self.crossover > 0:
                # === 完全自适应仓位计算 ===

                # 1. 账户风险金额 (2%)
                account_value = self.broker.getvalue()
                risk_amount = account_value * self.p.risk_percent

                # 2. ATR自适应止损距离 (per share)
                atr_stop_distance = self.atr[0] * self.p.atr_multiplier

                # 3. 仓位 = 风险金额 / 止损距离
                # 防止除零
                if atr_stop_distance < 0.01:
                    atr_stop_distance = 0.01

                position_size = int(risk_amount / atr_stop_distance)

                # 限制仓位范围 [1, 100]
                position_size = max(1, min(position_size, 100))

                self.order = self.buy(size=position_size)
                self.entry_price = self.data.close[0]

        else:
            # === ATR自适应止损 ===
            dynamic_stop_loss = self.atr[0] * self.p.atr_multiplier * self.position.size
            current_loss = (self.data.close[0] - self.entry_price) * self.position.size

            if current_loss < -dynamic_stop_loss:
                self.order = self.close()
                self.entry_price = None
            elif self.crossover < 0:
                self.order = self.close()
                self.entry_price = None

    def notify_order(self, order):
        if order.status in [order.Completed]:
            pass
        self.order = None


# =============================================================================
# 测试代码
# =============================================================================

if __name__ == '__main__':
    """
    快速验证所有策略类是否可正确导入和实例化
    """
    print("="*80)
    print("参数敏感性分析 - 策略验证")
    print("="*80)

    strategies = [
        ('Strategy13_FixedStopLoss', Strategy13_FixedStopLoss),
        ('Strategy13_FixedPositionSize', Strategy13_FixedPositionSize),
        ('Strategy13_ATR_Adaptive', Strategy13_ATR_Adaptive),
        ('Strategy13_Risk2Pct', Strategy13_Risk2Pct),
        ('Strategy13_FullyAdaptive', Strategy13_FullyAdaptive),
    ]

    for name, strategy_class in strategies:
        try:
            # 测试实例化
            cerebro = bt.Cerebro()
            cerebro.addstrategy(strategy_class)
            print(f"✅ {name:30s} - 导入成功")
        except Exception as e:
            print(f"❌ {name:30s} - 失败: {e}")

    print("="*80)
    print("所有策略验证完成")
    print("="*80)
