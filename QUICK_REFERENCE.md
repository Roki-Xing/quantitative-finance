# 📖 项目文件快速查询指南

## 🎯 快速定位 - 我想查看...

### ✅ 完整项目总结
**文件**: `DAY31_FINAL_REPORT.md`
- Day 1-31所有工作总结
- 核心发现和洞察
- 下一步计划 (Day 32-60)
- 重要文件索引

---

### 📊 实验详细报告

**Experiment 5 - Auto-fix实验**
- **文件**: `EXPERIMENT5_REPORT.md`
- 内容: Few-shot auto-fix实验完整过程
- 成果: 30/30 baseline策略100%可运行
- 关键发现: Auto-fix成功率35.3%, Manual fix 100%

**Experiment 7 - 策略演化实验**
- **文件**: `EXPERIMENT7_REPORT.md`
- 内容: 基于Top 3策略的遗传演化实验
- 成果: 5个演化策略生成 (需手动修复)
- 关键发现: LLM演化成功率0%, 生成比修复难10倍

---

### 🔬 实验脚本和数据

**服务器位置**: `/root/autodl-tmp/eoh/`

#### Experiment 6 - Baseline评估
```
实验脚本: experiment6_baseline_evaluation.py
结果目录: experiment6_baseline_evaluation/
详细结果: experiment6_baseline_evaluation/backtest_results.json
```

**关键数据**:
- Top 1: strategy_007 (2.93%)
- Top 2: strategy_016 (1.38%)
- Top 3: strategy_022 (0.75%)

#### Experiment 7 - 策略演化
```
演化脚本: experiment7_strategy_evolution.py
重试脚本: experiment7_retry_failed.py
验证脚本: experiment7_verify_evolved.py
结果目录: experiment7_evolved_strategies/
```

**生成的5个策略** (待手动修复):
1. `mutation1_optimize_007.py`
2. `mutation2_enhance_022.py`
3. `crossover1_position_atr.py`
4. `crossover2_ma_breakout.py`
5. `innovation_triple_fusion.py`

---

### 💼 策略文件库

**服务器位置**: `/root/autodl-tmp/eoh/`

#### Baseline策略 (7个原始可运行)
```
目录: experiment4_trading_extended/baseline/
文件: strategy_001.py ~ strategy_030.py
可运行: strategy_001, 002, 003, 004, 005, 006, 009
```

#### 手动修复策略 (11个)
```
目录: manual_fix/baseline/
文件: strategy_007_fixed.py, strategy_013_fixed.py, ...
列表: 007, 013, 017, 019, 020, 021, 023, 024, 025, 026, 028
```

#### Auto-fix策略 (6个)
```
目录: experiment5_autofix/
文件: strategy_014_autofix.py, strategy_016_autofix.py, ...
列表: 014, 016, 018, 027, 029, 030
```

**总计**: 30/30 策略100%可运行

---

### 📈 回测数据

**服务器位置**: `/root/autodl-tmp/eoh/backtest_data_extended/`

**可用数据**:
- 主要测试数据: `stock_sh_600519.csv` (贵州茅台)
- 其他股票数据: `stock_*.csv` (多只A股)

**数据格式**:
```
date, open, high, low, close, volume
```

---

## 🗺️ 项目路线图文件

**文件**: `PROJECT_ROADMAP.md`
- 完整的Day 1-60计划
- 当前进度: Day 31/60 (51.7%)
- 下一步详细任务

---

## 📁 本地文件目录结构

```
C:/Users/Xing/Desktop/day31_code_review/
├── DAY31_FINAL_REPORT.md          ⭐ 完整总结报告
├── PROJECT_ROADMAP.md             ⭐ 项目路线图
├── QUICK_REFERENCE.md              ⭐ 本文件 - 快速查询指南
│
├── EXPERIMENT5_REPORT.md           📊 Exp5详细报告
├── EXPERIMENT7_REPORT.md           📊 Exp7详细报告
│
├── experiment6_baseline_evaluation.py
├── experiment7_strategy_evolution.py
├── experiment7_retry_failed.py
├── experiment7_verify_evolved.py
│
└── evolved_strategies/             📁 演化策略(待修复)
    ├── mutation1_optimize_007.py
    ├── mutation2_enhance_022.py
    ├── crossover1_position_atr.py
    ├── crossover2_ma_breakout.py
    └── innovation_triple_fusion.py
```

---

## 🔍 常见查询场景

### 1. "Day 31做了什么?"
→ 查看 `DAY31_FINAL_REPORT.md` 的"Day 31 完成工作"章节

### 2. "Top 3策略是哪些?"
→ 查看 `DAY31_FINAL_REPORT.md` 的"Top 3 Baseline策略"表格
- strategy_007: 2.93%
- strategy_016: 1.38%
- strategy_022: 0.75%

### 3. "LLM自动修复成功率多少?"
→ 查看 `EXPERIMENT5_REPORT.md`
- Auto-fix: 35.3% (6/17)
- Manual fix: 100% (11/11)

### 4. "LLM策略演化成功率多少?"
→ 查看 `EXPERIMENT7_REPORT.md`
- 生成成功率: 100% (5/5生成)
- 代码可运行率: 0% (0/5可运行)
- **结论**: 需100%人工修复

### 5. "下一步该做什么?"
→ 查看 `DAY31_FINAL_REPORT.md` 的"下一步计划"章节
或 `PROJECT_ROADMAP.md`

**优先任务**:
1. 完成Experiment 7 (手动修复5个策略)
2. 参数优化Top 3策略
3. 多市场验证

### 6. "策略修复模板是什么?"
→ 查看 `EXPERIMENT5_REPORT.md` 的"成功的Manual Fix Pattern"
或 `DAY31_FINAL_REPORT.md` 的"建立了完整的策略修复模板"

### 7. "常见错误有哪些?"
→ 查看 `EXPERIMENT5_REPORT.md` 的"常见错误模式分析"
或 `EXPERIMENT7_REPORT.md` 的"错误模式分析"

**Top 3错误**:
1. API Hallucination (60%): self.log(), broker.set_stoploss()
2. 逻辑错误 (25%): 未初始化变量, 缺少订单管理
3. 参数错误 (15%): MACD/ATR参数命名

### 8. "各个实验的时间成本?"
→ 查看 `DAY31_FINAL_REPORT.md` 的"工作量统计"

| 实验 | 时间 |
|------|------|
| Exp 5 Auto-fix | ~1小时 |
| Exp 5 Manual fix | ~55分钟 (11个策略) |
| Exp 6 Baseline评估 | ~30分钟 |
| Exp 7 策略生成 | ~30分钟 |
| Exp 7 修复(待完成) | ~30-50分钟 (预估) |

---

## 🚀 下一步快速行动指南

### 立即开始 (Day 32)

**任务1: 完成Experiment 7**
1. 手动修复5个演化策略 (~30-50分钟)
   - 位置: `evolved_strategies/`
   - 参考: Exp5修复模板
2. 回测验证
   - 运行: `experiment7_verify_evolved.py`
3. 性能对比
   - vs Top 3 baseline

**任务2: 生成Experiment 7完整报告**
1. 更新 `EXPERIMENT7_REPORT.md`
2. 添加修复后性能数据

### 本周计划 (Day 32-35)

**Experiment 8: 参数优化**
- 对Top 3策略进行Grid Search
- 优化MA周期、止损/止盈比例
- 目标: 提升至3-5%收益

**Experiment 9: 多市场验证**
- 在10-20只不同股票上测试
- 分析策略泛化能力

---

## 📞 需要帮助?

### 遇到问题时查看:

1. **策略加载失败** → `EXPERIMENT5_REPORT.md` "常见错误模式"
2. **回测报错** → 检查数据格式和API使用
3. **性能不佳** → 尝试参数优化 (Exp 8计划)
4. **不知道下一步** → `PROJECT_ROADMAP.md` 或 `DAY31_FINAL_REPORT.md`

---

**最后更新**: 2025-11-24
**当前进度**: Day 31/60 (51.7%)
**下一里程碑**: 完成Experiment 7
