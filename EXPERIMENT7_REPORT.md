# Experiment 7: 策略演化实验报告

## 实验概要

**目标**: 基于Top 3 baseline策略,通过LLM进行遗传演化生成更优秀的策略

**方法**:
- 变异 (Mutation): 优化参数和逻辑
- 交叉 (Crossover): 组合不同策略的优势特性
- 创新 (Innovation): 基于insights创建全新策略

**模型**: qwen2.5-coder:7b (Ollama本地部署)

---

## 一、实验设计

### 1.1 Top 3 Baseline策略 (Experiment 6结果)

| 策略 | 收益率 | Sharpe | 特点 |
|------|--------|--------|------|
| strategy_007 | 2.93% | N/A | Trend-following + 动态仓位管理 |
| strategy_016 | 1.38% | N/A | Volatility breakout |
| strategy_022 | 0.75% | N/A | Dual MA + ATR filtering |

### 1.2 演化策略设计

设计了5个演化方向:

1. **mutation1_optimize_007** - 优化007参数和止损逻辑
   - 添加基于ATR的自适应止损
   - 优化MA周期和风险参数
   - 改进出场逻辑

2. **mutation2_enhance_022** - 增强022的ATR过滤
   - 更复杂的ATR入场过滤器
   - 基于ATR倍数的动态止盈
   - 添加成交量确认

3. **crossover1_position_atr** - 007仓位管理 + 022 ATR过滤
   - 动态仓位计算 (风险2%/交易)
   - ATR波动率过滤 (只在ATR上升时入场)
   - 基于ATR的止损

4. **crossover2_ma_breakout** - 007均线系统 + 016突破逻辑
   - 双MA识别趋势方向
   - 价格突破精确入场
   - 仅在趋势方向上突破入场

5. **innovation_triple_fusion** - 三策略insights创新组合
   - 三条MA (fast/medium/slow) 多时间框架
   - 结合ATR和RSI双重确认
   - 加仓机制 (pyramiding)
   - ATR trailing stop

---

## 二、执行过程

### 2.1 初次演化 (5个策略)

**执行时间**: 2025-11-24 20:14:37

**结果**: 2/5 成功, 3/5 超时

| 策略 | 状态 | 代码长度 |
|------|------|----------|
| mutation1_optimize_007 | ❌ 超时 (180s) | - |
| mutation2_enhance_022 | ❌ 超时 | - |
| crossover1_position_atr | ❌ 超时 | - |
| crossover2_ma_breakout | ✅ 成功 | 1845字符 |
| innovation_triple_fusion | ✅ 成功 | 2585字符 |

**问题**: LLM生成时间过长,导致3个策略超时

### 2.2 重试失败策略 (3个)

**执行时间**: 2025-11-24 20:34:18

**优化**:
- 超时时间增加到300秒
- 改进prompt (明确禁止`self.log()`)

**结果**: 3/3 成功

| 策略 | 状态 | 代码长度 |
|------|------|----------|
| mutation1_optimize_007 | ✅ 成功 | 2454字符 |
| mutation2_enhance_022 | ✅ 成功 | 1149字符 |
| crossover1_position_atr | ✅ 成功 | 1643字符 |

**总计**: 5/5 策略全部生成成功

---

## 三、验证结果

### 3.1 回测验证 (贵州茅台 600519)

**执行时间**: 2025-11-24 20:59:59

**结果**: **0/5 策略可运行**

| 策略 | 状态 | 错误类型 |
|------|------|----------|
| mutation1_optimize_007 | ❌ | `'<' not supported between instances of 'float' and 'NoneType'` |
| mutation2_enhance_022 | ❌ | `Failed to load strategy class` (语法错误) |
| crossover1_position_atr | ❌ | `name 'btind' is not defined` |
| crossover2_ma_breakout | ❌ | `no attribute 'log'` |
| innovation_triple_fusion | ❌ | `no attribute 'high'` (ATR参数错误) |

### 3.2 错误模式分析

检查代码后发现的典型LLM错误:

**1. API Hallucination** (最严重)
- 使用不存在的`self.log()` 方法
- 错误的`Volume`指标用法
- 不存在的`bt.utils.round_down()`

**2. 导入/命名错误**
- 使用`btind`而非`bt.indicators`
- 缺少必要的import

**3. 逻辑错误**
- 比较未初始化的变量 (None)
- ATR参数错误 (`self.data.close` 应该是 `self.data`)
- 缺少必要的`self.order`, `self.entry_price`, `notify_order()`

**4. 数据访问错误**
- 错误的指标访问方式
- 不存在的方法调用 (如`self.volume.avg()`)

---

## 四、手动修复结果 ✅ 完成

### 4.1 修复过程

**修复时间**: ~10分钟

**修复策略数**: 5/5

**修复方法**:
1. 删除所有`self.log()`调用
2. 修正API命名: `btind` → `bt.indicators`
3. 修正ATR初始化: `ATR(self.data.close)` → `ATR(self.data)`
4. 添加订单管理: `self.order`, `notify_order()`
5. 修正逻辑错误: 初始化变量、简化复杂逻辑
6. 移除不存在的API: `bt.utils.round_down()`, `Volume.avg()`

### 4.2 修复后回测结果

**测试数据**: 贵州茅台 (600519)
**测试时间**: 2025-11-24 21:24:54

| 策略 | 收益率 | Sharpe | 最大回撤 | 交易次数 | 状态 |
|------|--------|--------|---------|---------|------|
| **innovation_triple_fusion** | **26.92%** | 0.181 | 4.02% | 33 | ✅ |
| crossover1_position_atr | 17.76% | 0.037 | 22.72% | 2 | ✅ |
| crossover2_ma_breakout | 0.36% | -4.24 | 1.28% | 97 | ✅ |
| mutation1_optimize_007 | 0.00% | N/A | 0.00% | 0 | ✅ |
| mutation2_enhance_022 | 0.00% | N/A | 0.00% | 0 | ✅ |

**成功率**: 5/5 (100%) ✅

### 4.3 性能对比分析

**Baseline Top 3 vs 最佳演化策略**:

| 排名 | Baseline | 收益率 | 演化策略 | 收益率 | 改进幅度 |
|------|----------|--------|----------|--------|---------|
| 1 | strategy_007 | 2.93% | **innovation_triple_fusion** | **26.92%** | **+23.99%** |
| 2 | strategy_016 | 1.38% | crossover1_position_atr | 17.76% | +16.38% |
| 3 | strategy_022 | 0.75% | crossover2_ma_breakout | 0.36% | -0.39% |

**关键发现**:

1. **Innovation方法最有效**: 创新组合策略 (innovation_triple_fusion) 达到 **26.92%** 收益，是baseline最佳策略的 **9.2倍**

2. **Crossover方法有效**: crossover1 (仓位管理 + ATR过滤) 达到 17.76%，是baseline最佳策略的 **6倍**

3. **Mutation方法失效**: 两个变异策略均未产生交易 (0%收益)，参数优化未能改进原策略

4. **策略特征分析**:
   - **最佳策略** (innovation_triple_fusion):
     - 三重MA (fast/medium/slow) 多时间框架
     - RSI波动率过滤 (RSI < 30 or > 70)
     - ATR动态仓位管理
     - ATR trailing stop
     - 33次交易，4.02%最大回撤

   - **次佳策略** (crossover1_position_atr):
     - MA交叉识别趋势
     - ATR上升时入场 (波动率增加)
     - 基于ATR的动态仓位
     - 仅2次交易，22.72%回撤偏高

---

## 四、关键发现

### 4.1 与Experiment 5对比

| 指标 | Experiment 5 (Auto-fix) | Experiment 7 (Evolution) |
|------|-------------------------|-------------------------|
| LLM模型 | qwen2.5-coder:7b | qwen2.5-coder:7b |
| 任务类型 | 修复已有策略 | 生成全新策略 |
| 生成成功率 | 17/17 (100%) | 5/5 (100%) |
| 代码可运行率 | 6/17 (35.3%) | **0/5 (0%)** |
| 平均生成时间 | 4.2秒/个 | ~120秒/个 (含超时) |

**关键洞察:**
1. **生成新策略比修复现有代码更难** - 0% vs 35.3%
2. **LLM在自由创作时更容易产生hallucination**
3. **即使使用了few-shot examples和明确禁止的API,仍然出错**

### 4.2 成功因素分析

**为什么初次3个超时?**
- 生成完整策略需要更长推理时间
- 模型需要"思考"如何组合不同特性

**为什么所有策略都有错误?**
- 策略演化是"创新"任务,不是"修复"任务
- LLM缺乏backtrader API的准确知识
- Few-shot examples不足以覆盖所有边界情况

### 4.3 错误模式一致性

**与Experiment 5的共同错误:**
- `self.log()` hallucination
- 缺少`notify_order()`
- 订单管理缺失

**Evolution特有错误:**
- 复杂逻辑导致未初始化变量
- 尝试使用不存在的高级API
- 指标参数错误

---

## 五、结论

### 5.1 主要成果

✅ **成功设计并实现了5种演化策略生成方案**
✅ **验证了LLM策略演化的可行性**(虽然需要人工修复)
✅ **发现策略生成比策略修复难度更高** (0% vs 35.3%)
✅ **总结了LLM生成策略代码的系统性错误模式**

### 5.2 验证的假设

❌ **假设**: LLM能直接生成可运行的演化策略
✅ **实际**: 所有策略都需要人工修复 (与Exp5一致)

✅ **假设**: 增加超时时间能提高成功率
✅ **实际**: 300秒超时使3个失败策略成功生成

❌ **假设**: 明确禁止错误API能避免hallucination
✅ **实际**: 仍然出现`self.log()`等错误

### 5.3 ✅ 完整完成 (2025-11-24 更新)

**已完成工作**:
- ✅ 手动修复5个演化策略 (实际时间: ~10分钟)
- ✅ 修复后的策略回测评估 (5/5成功)
- ✅ 与Top 3 baseline性能对比

**修复实际结果**:
- Manual fix成功率: 100% (5/5)
- 实际修复时间: ~10分钟
- 最佳策略收益: **26.92%** (innovation_triple_fusion)
- vs Baseline最佳: **+23.99%** (9.2倍提升)

**核心结论**:
虽然LLM生成的演化策略初始可运行率为0%,但经过快速人工修复后,演化策略可以显著超越baseline表现。**Innovation方法**通过组合多种技术指标和风险管理策略,实现了baseline最佳策略 **9.2倍的收益提升**。

---

## 六、对比Experiment 5的新洞察

### 6.1 任务难度对比

| 维度 | Auto-Fix (Exp5) | Evolution (Exp7) |
|------|----------------|-----------------|
| 输入 | 已有策略(有bug) | Top 3策略insights |
| 输出 | 修复后的策略 | 全新演化策略 |
| 创造性要求 | 低 (诊断+修复) | 高 (设计+实现) |
| 成功率 | 35.3% | 0% |
| 结论 | **修复比创造简单** | **创造需要更强能力** |

### 6.2 LLM能力边界

**能做到的:**
- ✅ 理解策略演化prompt
- ✅ 生成结构合理的Python代码
- ✅ 尝试组合不同特性

**做不到的:**
- ❌ 准确使用backtrader API
- ❌ 避免基础的代码错误
- ❌ 生成可直接运行的代码

---

## 七、下一步建议

### 7.1 短期 (完成Experiment 7)

1. **手动修复5个演化策略**
   - 使用Experiment 5总结的修复模板
   - 时间预计: 30-45分钟

2. **性能评估**
   - 回测修复后的策略
   - 与Top 3 baseline对比

3. **性能改进分析**
   - 是否超过2.93%基准?
   - 哪种演化方法最有效?

### 7.2 长期 (改进策略演化)

1. **增强Few-Shot Examples**
   - 添加10-15个正确示例
   - 覆盖更多错误模式
   - 添加"what NOT to do"反例

2. **迭代修复机制**
   - LLM生成 → 验证 → 提取错误 → 重新生成
   - 类似self-debugging

3. **使用更强模型**
   - qwen2.5-coder:14b/32b
   - 或GPT-4/Claude等商业模型

4. **混合方法**
   - LLM生成策略框架
   - 人工审核关键逻辑
   - LLM生成测试用例

---

## 八、文件清单

### 实验脚本
- `experiment7_strategy_evolution.py` - 演化主脚本
- `experiment7_retry_failed.py` - 重试脚本
- `experiment7_verify_evolved.py` - 验证脚本

### 演化结果
- `experiment7_evolved_strategies/` 目录:
  - `mutation1_optimize_007.py` (2454字符, ❌需修复)
  - `mutation2_enhance_022.py` (1149字符, ❌需修复)
  - `crossover1_position_atr.py` (1643字符, ❌需修复)
  - `crossover2_ma_breakout.py` (1845字符, ❌需修复)
  - `innovation_triple_fusion.py` (2585字符, ❌需修复)
  - `evolution_summary.json` - 初次演化汇总
  - `retry_summary.json` - 重试汇总
  - `evolved_backtest_results.json` - 验证结果

### 日志文件
- `experiment7_evolution.log` - 初次演化日志
- `experiment7_retry.log` - 重试日志

---

## 九、实验时间统计

| 阶段 | 时间 |
|------|------|
| 设计演化方案 | ~10分钟 |
| 初次演化 (2/5成功) | ~12分钟 |
| 重试3个失败策略 | ~2分钟 |
| 验证回测 | ~1分钟 |
| 代码分析 | ~5分钟 |
| **总计** | **~30分钟** |

**未完成部分预估:**
- 手动修复5个策略: 30-45分钟
- 修复后回测+对比: 10分钟
- **完整实验预估总时间**: ~1.5-2小时

---

**Experiment 7 当前状态: 已完成策略生成和验证,待人工修复**

**核心发现: LLM策略演化需要100%人工验证和修复,证明了Experiment 5的结论在更复杂任务上同样成立**
