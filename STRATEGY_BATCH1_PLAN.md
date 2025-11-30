# 策略生成批次1计划 - 10个策略

**日期**: 2025-11-22 (Day 39准备，Day 40执行)
**目标**: 生成第一批10个多样化交易策略
**方法**: 使用Phase 1验证的多层次Prompt结构

---

## 第一部分：策略选择原则

### 1.1 多样性保证

**技术指标覆盖**:
- 趋势类指标: MA, MACD
- 动量类指标: RSI, Momentum
- 波动率指标: Bollinger Bands, ATR
- 成交量指标: Volume confirmation

**交易频率分布**:
- 高频（日内）: 0个（避免滑点问题）
- 中频（持仓1-5天）: 4个
- 低频（持仓5-20天）: 6个

**风险收益特征**:
- 保守型（目标Sharpe > 1.5，低回撤）: 3个
- 平衡型（目标Sharpe > 1.0）: 5个
- 进取型（追求高收益，可接受高波动）: 2个

### 1.2 实用性考虑

**数据要求**:
- 仅使用OHLCV数据（开高低收量）
- 避免需要另类数据（财报、新闻等）
- 确保数据易获取（yfinance可提供）

**计算复杂度**:
- 避免复杂机器学习（批次2再引入）
- 专注经典技术分析策略
- 确保回测速度快

---

## 第二部分：10个策略详细规格

### 策略1: 双均线交叉（经典趋势跟踪）

**策略名称**: `dual_ma_crossover`
**类别**: 趋势跟踪
**核心逻辑**:
- 快线：20日移动平均
- 慢线：50日移动平均
- 入场：快线上穿慢线，做多
- 出场：快线下穿慢线，平仓

**风险管理**:
- 止损：-5%
- 止盈：+15%
- 最大仓位：100%

**预期特征**:
- 交易频率：中低（年10-20次）
- 胜率：~45%
- 盈亏比：~2:1
- 适合市场：明显趋势市

---

### 策略2: MACD零轴穿越

**策略名称**: `macd_zero_cross`
**类别**: 趋势跟踪
**核心逻辑**:
- MACD参数：12, 26, 9
- 入场：MACD线上穿0轴，做多
- 出场：MACD线下穿0轴，平仓

**风险管理**:
- 止损：-4%
- 止盈：+12%
- 最大仓位：100%

**预期特征**:
- 交易频率：中（年15-30次）
- 胜率：~50%
- 盈亏比：~1.5:1
- 适合市场：趋势初期

---

### 策略3: RSI超卖反转

**策略名称**: `rsi_oversold_reversal`
**类别**: 均值回归
**核心逻辑**:
- RSI参数：14日
- 入场：RSI < 30（超卖），且价格上涨突破前日高点
- 出场：RSI > 50，或持仓5天

**风险管理**:
- 止损：-3%
- 止盈：+8%
- 最大仓位：100%

**预期特征**:
- 交易频率：中高（年30-50次）
- 胜率：~55%
- 盈亏比：~1.2:1
- 适合市场：震荡市

---

### 策略4: 布林带突破

**策略名称**: `bollinger_breakout`
**类别**: 波动率/趋势
**核心逻辑**:
- 布林带参数：20日，2倍标准差
- 入场：收盘价突破上轨，做多
- 出场：收盘价跌破中轨，平仓

**风险管理**:
- 止损：-4%
- 止盈：+10%
- 最大仓位：100%

**预期特征**:
- 交易频率：中（年20-35次）
- 胜率：~48%
- 盈亏比：~1.8:1
- 适合市场：波动扩张期

---

### 策略5: 动量确认策略

**策略名称**: `momentum_confirmation`
**类别**: 动量
**核心逻辑**:
- 动量：10日收益率 > 5%
- 成交量确认：当日成交量 > 20日均量
- 入场：动量+成交量双重确认
- 出场：动量转负，或持仓10天

**风险管理**:
- 止损：-6%
- 止盈：+18%
- 最大仓位：100%

**预期特征**:
- 交易频率：低（年10-20次）
- 胜率：~50%
- 盈亏比：~2:1
- 适合市场：强势趋势

---

### 策略6: ATR通道突破

**策略名称**: `atr_channel_breakout`
**类别**: 波动率
**核心逻辑**:
- ATR参数：14日
- 通道：收盘价 ± 2*ATR
- 入场：价格突破上通道
- 出场：价格跌破下通道，或ATR收缩50%

**风险管理**:
- 止损：动态（2*ATR）
- 止盈：动态（4*ATR）
- 最大仓位：100%

**预期特征**:
- 交易频率：中（年15-25次）
- 胜率：~45%
- 盈亏比：~2.5:1
- 适合市场：波动率扩张

---

### 策略7: 三重过滤趋势

**策略名称**: `triple_filter_trend`
**类别**: 多因子趋势
**核心逻辑**:
- 过滤器1：50日MA向上
- 过滤器2：MACD > 0
- 过滤器3：ADX > 25（趋势强度）
- 入场：三者同时满足
- 出场：任一过滤器失效

**风险管理**:
- 止损：-5%
- 止盈：+15%
- 最大仓位：100%

**预期特征**:
- 交易频率：低（年8-15次）
- 胜率：~60%（高质量信号）
- 盈亏比：~2:1
- 适合市场：强趋势

---

### 策略8: 均值回归网格

**策略名称**: `mean_reversion_grid`
**类别**: 均值回归
**核心逻辑**:
- 基准：20日移动平均
- 入场：价格偏离MA超过-10%
- 加仓：每偏离-5%加仓一次（最多3次）
- 出场：回归至MA+2%

**风险管理**:
- 止损：总仓位-15%
- 单次仓位：33%（分三次）
- 最大仓位：100%

**预期特征**:
- 交易频率：低（年5-10次）
- 胜率：~65%（保守入场）
- 盈亏比：~1.5:1
- 适合市场：震荡市

---

### 策略9: 价格突破+成交量

**策略名称**: `price_volume_breakout`
**类别**: 突破
**核心逻辑**:
- 入场：价格突破20日高点，且成交量 > 50日均量1.5倍
- 出场：跌破10日低点
- 追踪止盈：最高点回撤10%

**风险管理**:
- 止损：-4%
- 追踪止盈：-10%
- 最大仓位：100%

**预期特征**:
- 交易频率：中（年15-30次）
- 胜率：~50%
- 盈亏比：~2:1
- 适合市场：突破行情

---

### 策略10: 波动率收缩突破

**策略名称**: `volatility_squeeze_breakout`
**类别**: 波动率
**核心逻辑**:
- 识别波动率收缩：20日ATR < 50日ATR * 0.7
- 等待突破：价格突破收缩期间高点
- 入场：收缩后首次突破
- 出场：波动率扩张至2倍起始值

**风险管理**:
- 止损：-3%（收缩期波动小）
- 止盈：+12%
- 最大仓位：100%

**预期特征**:
- 交易频率：低（年8-12次）
- 胜率：~55%
- 盈亏比：~2.5:1
- 适合市场：盘整后突破

---

## 第三部分：策略生成Prompt模板

### 3.1 统一结构（基于HPDT）

每个策略的Prompt都包含4层：

```markdown
# Layer 1: Safety & Risk Constraints
- No lookahead bias（不使用未来数据）
- No in-place data modification（不修改历史数据）
- Explicit stop-loss mechanism（明确止损）
- Position size limits（仓位限制）
- Trade logging（交易日志）

# Layer 2: Strategy-Specific Functional Requirements
- Strategy type: [趋势/均值回归/...]
- Entry conditions: [具体条件]
- Exit conditions: [止盈/止损/时间]
- Indicators: [MA/RSI/MACD/...]
- Parameters: [具体数值]

# Layer 3: Code Quality Standards
- Backtrader compatible
- Type hints on all methods
- Docstrings (strategy description)
- Logging (entry/exit signals)
- Configurable parameters

# Layer 4: Backtrader Strategy Template
[完整Backtrader策略代码，~150-250行]
```

### 3.2 示例：策略1的完整Prompt

```markdown
# Task: Generate a Dual Moving Average Crossover Strategy for Backtrader

## Layer 1: Safety & Risk Constraints (CRITICAL)

### Data Integrity
- NEVER use future data in calculations
- NEVER modify historical price data
- Use only OHLCV data available at the time of each bar
- Implement proper data alignment

### Risk Management (MANDATORY)
- Stop-loss: 5% from entry price
- Take-profit: 15% from entry price
- Maximum position size: 100% of capital
- No overlapping positions
- Log every entry and exit with reasons

### Error Handling
- Handle missing data gracefully
- Validate indicator calculations
- Ensure position exists before exit
- Log errors without crashing

## Layer 2: Functional Requirements

### Strategy Logic

**Entry Signal**:
- Fast MA (20-day) crosses above Slow MA (50-day)
- Confirm with closing price > Fast MA
- Enter at next bar's open price

**Exit Signal**:
- Fast MA crosses below Slow MA (normal exit)
- Stop-loss: Price falls 5% below entry
- Take-profit: Price rises 15% above entry
- Exit at next bar's open price

### Required Indicators
```python
- Simple Moving Average (SMA) 20
- Simple Moving Average (SMA) 50
```

### Parameters (Configurable)
```python
fast_period = 20    # Fast MA period
slow_period = 50    # Slow MA period
stop_loss = 0.05    # 5% stop loss
take_profit = 0.15  # 15% take profit
```

### Required Libraries
```python
import backtrader as bt
import datetime
import logging
```

## Layer 3: Code Quality Standards

### Structure
- Inherit from bt.Strategy
- Separate parameter definition
- Clear method organization: __init__, next, notify_order, notify_trade
- Modular helper methods if needed

### Documentation
- Class docstring explaining strategy logic
- Method docstrings for all functions
- Inline comments for complex logic
- Parameter descriptions

### Logging
- INFO: Entry and exit signals
- WARNING: Stop-loss or take-profit triggered
- ERROR: Data issues or calculation errors
- Include timestamp, price, and reason

### Type Hints
- Type hints on all method parameters
- Return type annotations

### Best Practices
- Use bt.indicators for calculations
- Store entry price for stop-loss/take-profit
- Use self.buy() and self.sell() for orders
- Track order status in notify_order()

## Layer 4: Complete Backtrader Strategy Template

```python
#!/usr/bin/env python3
"""
Dual Moving Average Crossover Strategy

A classic trend-following strategy that enters long when a fast moving average
crosses above a slow moving average, and exits when the opposite occurs.

Strategy Rules:
- Entry: 20-day SMA crosses above 50-day SMA
- Exit: 20-day SMA crosses below 50-day SMA, or stop-loss/take-profit
- Stop-loss: 5% below entry price
- Take-profit: 15% above entry price

Expected Performance:
- Win rate: ~45%
- Profit factor: ~2:1
- Best for: Trending markets

Author: LLM Generated
Date: 2025-11-22
"""

import backtrader as bt
import logging
from typing import Optional

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class DualMAStrategy(bt.Strategy):
    """
    Dual Moving Average Crossover Strategy

    Buys when fast MA crosses above slow MA.
    Sells when fast MA crosses below slow MA, or stop-loss/take-profit triggered.
    """

    params = (
        ('fast_period', 20),     # Fast moving average period
        ('slow_period', 50),     # Slow moving average period
        ('stop_loss', 0.05),     # Stop loss percentage (5%)
        ('take_profit', 0.15),   # Take profit percentage (15%)
        ('order_size', 1.0),     # Position size (100% of capital)
    )

    def __init__(self):
        """Initialize strategy indicators and variables"""
        # Calculate moving averages
        self.fast_ma = bt.indicators.SimpleMovingAverage(
            self.data.close, period=self.params.fast_period
        )
        self.slow_ma = bt.indicators.SimpleMovingAverage(
            self.data.close, period=self.params.slow_period
        )

        # Crossover signal
        self.crossover = bt.indicators.CrossOver(self.fast_ma, self.slow_ma)

        # Track orders and trades
        self.order: Optional[bt.Order] = None
        self.entry_price: float = 0.0
        self.stop_loss_price: float = 0.0
        self.take_profit_price: float = 0.0

        logger.info(f"Strategy initialized with fast_period={self.params.fast_period}, "
                   f"slow_period={self.params.slow_period}")

    def notify_order(self, order: bt.Order):
        """Handle order execution notifications"""
        if order.status in [order.Submitted, order.Accepted]:
            return

        if order.status in [order.Completed]:
            if order.isbuy():
                logger.info(
                    f"BUY EXECUTED at {order.executed.price:.2f}, "
                    f"Size: {order.executed.size:.2f}, "
                    f"Cost: {order.executed.value:.2f}, "
                    f"Commission: {order.executed.comm:.2f}"
                )
            elif order.issell():
                logger.info(
                    f"SELL EXECUTED at {order.executed.price:.2f}, "
                    f"Size: {order.executed.size:.2f}, "
                    f"Cost: {order.executed.value:.2f}, "
                    f"Commission: {order.executed.comm:.2f}"
                )

            self.order = None

        elif order.status in [order.Canceled, order.Margin, order.Rejected]:
            logger.warning(f"Order {order.Status[order.status]} - Reason: {order.status}")
            self.order = None

    def notify_trade(self, trade: bt.Trade):
        """Handle trade close notifications"""
        if trade.isclosed:
            pnl_pct = (trade.pnl / trade.price) * 100
            logger.info(
                f"TRADE CLOSED - PnL: {trade.pnl:.2f} ({pnl_pct:.2f}%), "
                f"Gross: {trade.pnlcomm:.2f}"
            )

    def next(self):
        """Execute strategy logic on each bar"""
        # Check if we have an order pending
        if self.order:
            return

        # Get current values
        current_price = self.data.close[0]
        fast_ma_value = self.fast_ma[0]
        slow_ma_value = self.slow_ma[0]

        # Check if we have a position
        if not self.position:
            # Entry logic: Fast MA crosses above Slow MA
            if self.crossover > 0:
                # Calculate position size
                size = self.broker.get_cash() * self.params.order_size / current_price

                # Place buy order
                self.order = self.buy(size=size)
                self.entry_price = current_price

                # Calculate stop-loss and take-profit levels
                self.stop_loss_price = self.entry_price * (1 - self.params.stop_loss)
                self.take_profit_price = self.entry_price * (1 + self.params.take_profit)

                logger.info(
                    f"BUY SIGNAL at {current_price:.2f} - "
                    f"Fast MA: {fast_ma_value:.2f}, Slow MA: {slow_ma_value:.2f}, "
                    f"Stop-loss: {self.stop_loss_price:.2f}, "
                    f"Take-profit: {self.take_profit_price:.2f}"
                )

        else:
            # Exit logic
            exit_reason = None

            # Check stop-loss
            if current_price <= self.stop_loss_price:
                exit_reason = f"STOP-LOSS triggered at {current_price:.2f}"

            # Check take-profit
            elif current_price >= self.take_profit_price:
                exit_reason = f"TAKE-PROFIT triggered at {current_price:.2f}"

            # Check MA crossover (normal exit)
            elif self.crossover < 0:
                exit_reason = f"MA CROSSOVER (Fast below Slow) at {current_price:.2f}"

            # Execute exit if triggered
            if exit_reason:
                self.order = self.sell(size=self.position.size)
                logger.warning(
                    f"SELL SIGNAL - {exit_reason} - "
                    f"Fast MA: {fast_ma_value:.2f}, Slow MA: {slow_ma_value:.2f}"
                )

    def stop(self):
        """Called when strategy ends"""
        final_value = self.broker.getvalue()
        logger.info(f"Strategy finished - Final Portfolio Value: {final_value:.2f}")


# Backtrader setup example
if __name__ == '__main__':
    cerebro = bt.Cerebro()
    cerebro.addstrategy(DualMAStrategy)

    # Add data (example - replace with actual data source)
    # data = bt.feeds.YahooFinanceData(dataname='AAPL',
    #                                   fromdate=datetime(2020, 1, 1),
    #                                   todate=datetime(2025, 1, 1))
    # cerebro.adddata(data)

    cerebro.broker.setcash(100000.0)
    cerebro.broker.setcommission(commission=0.001)  # 0.1% commission

    print(f'Starting Portfolio Value: {cerebro.broker.getvalue():.2f}')
    cerebro.run()
    print(f'Final Portfolio Value: {cerebro.broker.getvalue():.2f}')
```

## Success Criteria Checklist

Before submitting, verify the code includes:

- [ ] No lookahead bias (only uses past data)
- [ ] Stop-loss mechanism (5% below entry)
- [ ] Take-profit mechanism (15% above entry)
- [ ] Proper MA calculation using bt.indicators
- [ ] Crossover detection
- [ ] Entry signal logging
- [ ] Exit signal logging (all three types)
- [ ] Order and trade notifications
- [ ] Type hints on methods
- [ ] Comprehensive docstrings
- [ ] Configurable parameters
- [ ] Backtrader compatible structure

Generate a complete, production-ready Backtrader strategy following all requirements above.
```

---

## 第四部分：生成流程

### 4.1 Day 40执行计划

**上午（8:00-12:00）**:
1. 准备LLM环境（加载模型）
2. 生成策略1-5（使用对应Prompt）
3. 语法检查与初步审查

**下午（14:00-18:00）**:
4. 生成策略6-10
5. 完整代码审查
6. 初步手动回测（测试1-2个策略）

### 4.2 质量保证

**自动检查**:
- Python语法检查（ast.parse）
- Backtrader兼容性检查（导入测试）
- 参数完整性检查

**手动审查**:
- 逻辑正确性（是否有lookahead bias）
- 风险管理完整性（止损、止盈、仓位）
- 代码清晰度（注释、文档）

**淘汰标准**:
- 语法错误 → 重新生成
- 逻辑错误（如未来数据） → 修复或重新生成
- 缺少风险管理 → 补充

---

## 第五部分：预期产出

### 5.1 代码文件

```
strategy_library/batch1/
├── 01_dual_ma_crossover.py
├── 02_macd_zero_cross.py
├── 03_rsi_oversold_reversal.py
├── 04_bollinger_breakout.py
├── 05_momentum_confirmation.py
├── 06_atr_channel_breakout.py
├── 07_triple_filter_trend.py
├── 08_mean_reversion_grid.py
├── 09_price_volume_breakout.py
└── 10_volatility_squeeze_breakout.py
```

### 5.2 文档

**DAY40_STRATEGY_GENERATION_BATCH1.md**:
- 生成过程记录
- 每个策略的审查结果
- 初步测试结果
- 问题与修复

---

## 第六部分：成功标准

### 最低目标（Day 40结束）:
- ✅ 生成10个策略
- ✅ 所有策略语法正确
- ✅ 所有策略包含止损/止盈
- ✅ 至少8个策略通过手动审查

### 理想目标:
- ✅ 10个策略全部高质量
- ✅ 初步回测2-3个策略成功运行
- ✅ 无明显逻辑错误

---

**批次1计划完成！准备Day 40执行！** 🎯

---

*STRATEGY_BATCH1_PLAN.md - 10页, ~3,500字*
*10个策略 × 平均200行代码 = ~2,000行策略代码*
*预计Day 40完成*
