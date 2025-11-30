# Codex代码审查报告 - 策略1: 双均线交叉

**审查日期**: 2025-11-22
**审查工具**: Codex (gpt-4.1)
**策略**: 01_dual_ma_crossover.py
**生成质量**: 113行，语法正确

---

## Codex发现的问题

### 1. 🔴 High - 订单卡住风险

**问题描述**:
`notify_order()` 只处理了 `Completed` 状态，未处理 `Canceled`, `Margin`, `Rejected`。
如果订单被拒绝，`self.order` 永远不会清空，导致策略永久停止交易。

**当前代码**:
```python
def notify_order(self, order):
    if order.status in [order.Completed]:
        # 处理完成...
        self.order = None  # 只有Completed才清空
```

**修复方案**:
```python
def notify_order(self, order):
    if order.status in [order.Submitted, order.Accepted]:
        return

    if order.status in [order.Completed]:
        if order.isbuy():
            logger.info(f"BUY at {order.executed.price:.2f}")
            self.entry_price = order.executed.price
        elif order.issell():
            logger.info(f"SELL at {order.executed.price:.2f}")

    elif order.status in [order.Canceled, order.Margin, order.Rejected]:
        logger.warning(f"Order {order.status} - failed to execute")

    self.order = None  # 所有终态都清空
```

**严重性**: High - 可能导致策略完全失效

---

### 2. 🟡 Medium - 退出原因日志缺失

**问题描述**:
所有退出都调用 `self.sell()` 但没有记录具体原因（止损/止盈/交叉）。
规范要求止损/止盈用WARNING级别日志。

**当前代码**:
```python
if current <= self.entry_price * (1 - self.params.stop_loss):
    self.order = self.sell(size=self.position.size)  # 无日志
elif current >= self.entry_price * (1 + self.params.take_profit):
    self.order = self.sell(size=self.position.size)  # 无日志
elif self.crossover < 0:
    self.order = self.sell(size=self.position.size)  # 无日志
```

**修复方案**:
```python
if current <= self.entry_price * (1 - self.params.stop_loss):
    logger.warning(f"STOP-LOSS triggered at {current:.2f} (entry: {self.entry_price:.2f})")
    self.order = self.sell(size=self.position.size)
elif current >= self.entry_price * (1 + self.params.take_profit):
    logger.warning(f"TAKE-PROFIT triggered at {current:.2f} (entry: {self.entry_price:.2f})")
    self.order = self.sell(size=self.position.size)
elif self.crossover < 0:
    logger.info(f"CROSSOVER SELL signal at {current:.2f}")
    self.order = self.sell(size=self.position.size)
```

**严重性**: Medium - 影响可审计性和调试

---

### 3. 🟡 Medium - 入场确认检查

**Codex声称**: 缺少 `close > fast_ma` 检查

**实际代码**:
```python
if self.crossover > 0 and self.data.close[0] > self.fast_ma[0]:  # ✅ 实际有检查！
```

**结论**: **误报** - 代码实际是正确的

**严重性**: 无（误报）

---

### 4. 🟢 Low - 缺少方法docstrings和type hints

**问题描述**:
方法缺少docstrings和返回类型注解，违反Layer 3质量标准。

**当前代码**:
```python
def next(self):  # 缺少docstring和 -> None
    if self.order:
        return
    # ...
```

**修复方案**:
```python
def next(self) -> None:
    """
    Execute strategy logic on each bar.

    Checks for entry (MA crossover + price > fast MA) and
    exit signals (crossover down, stop-loss, take-profit).
    """
    if self.order:
        return
    # ...
```

**严重性**: Low - 代码质量问题，不影响功能

---

## 审查总结

### 问题分类
- 🔴 High: 1个（订单卡住）
- 🟡 Medium: 1个（日志缺失）+ 1个误报
- 🟢 Low: 1个（文档缺失）

### 整体评分: **75/100**

**扣分项**:
- -15: 订单处理不完整（可能卡住）
- -10: 退出日志缺失（不符合规范）
- -5: 方法文档不完整

**优点**:
- ✅ 语法完全正确
- ✅ 逻辑基本正确（入场有确认）
- ✅ 止损止盈机制存在
- ✅ Backtrader兼容

### 建议

1. **必须修复**: 订单卡住问题（High优先级）
2. **应该改进**: 添加退出原因日志
3. **可选改进**: 补充方法docstrings

---

## 行动计划

**选项A: 快速修复**
- 手动修复策略1的2个关键问题
- 继续生成剩余8个策略

**选项B: 改进Prompt（推荐）** ⭐
- 更新Layer 4模板，包含完整的订单处理和日志
- 用改进的模板生成剩余8个策略
- 避免重复相同问题

**推荐**: **选项B** - 改进模板后批量生成，确保所有策略都避免这些问题。

---

**审查完成时间**: 2025-11-22 12:00
**下一步**: 改进Prompt模板 → 生成策略3-10
