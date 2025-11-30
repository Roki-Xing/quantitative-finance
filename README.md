# 论文补充实验材料 - 快速索引

**生成时间**: 2025-11-28
**实验周期**: Day 55 (继续)
**总回测数**: 370个 (97.1%成功率)

---

## 快速导航

### 核心数据文件 (data/)

| 文件 | 大小 | 回测数 | 用途 |
|------|------|--------|------|
| baseline_comparison_results.json | 31 KB | 96 | Gap 1: 外部基线对比 |
| sensitivity_A_stop_loss.json | 28 KB | 70 | Gap 2: 止损参数扫描 |
| sensitivity_B_position_size.json | 26 KB | 70 | Gap 2: 仓位参数扫描 |
| ablation_study_results.json | 15.8 KB | 40 | Gap 3: 组件贡献分解 |
| transaction_cost_sensitivity.json | 13.7 KB | 40 | Gap 5: 成本稳健性 |
| extended_baseline_results.json | ~50 KB | 84 | Gap 4: 扩展泛化 (10股) |

### 分析报告 (reports/)

| 报告 | 字数 | 核心发现 |
|------|------|----------|
| COMPREHENSIVE_SUMMARY.md | 7000 | **总览**: 所有实验汇总+论文引用建议 |
| gap_analysis_and_roadmap.md | 5000 | 六大缺口分析+执行路线图 |
| statistical_report_full.md | 3000 | 基线对比统计检验 (scipy) |
| ablation_study_report.md | 4000 | 消融实验完整分析 (含诚实负面结果) |
| parameter_sensitivity_report.md | 1500 | 参数敏感性总结 (14.66pp证据) |
| transaction_cost_report.md | 2000 | 交易成本线性衰减分析 |

**最重要**: 先阅读  (最全面的总结)

---

## 关键数字速查

| 指标 | 数值 | 说明 |
|------|------|------|
| 总回测数 | 370个 | 97.1%成功率 |
| 固定参数敏感度 (止损) | 14.66 pp | 证明固定参数陷阱 |
| ATR自适应改进 | +1.87 pp | vs Baseline |
| 完全自适应改进 | +4.36% | 训练期最优 |
| 交易成本衰减率 | -2.7 pp / 0.1% | 线性衰减 |
| 测试期表现 (2024) | +5.68% vs +27.24% | LLM vs Buy&Hold (p=0.017) |

---

## 六大缺口状态

| Gap | 优先级 | 实验 | 回测数 | 状态 |
|-----|--------|------|--------|------|
| 1. 外部基线对比 | ⭐⭐⭐⭐ | Baseline Comparison | 96 | ✅ |
| 2. 参数敏感性 | ⭐⭐⭐ | Parameter Sensitivity | 150 | ✅ |
| 3. 消融实验 | ⭐⭐⭐ | Ablation Study | 40 | ✅ |
| 4. 扩展验证 | ⭐⭐⭐ | Extended Generalization | 84 | ✅ |
| 5. 交易成本 | ⭐⭐ | Transaction Cost | 40 | ✅ |
| 6. 文档可视化 | ⭐⭐ | Reports + Charts | - | ✅ |

**总体完成度**: 100%

---

## 文件夹结构

**总文件数**: 28个
**总大小**: ~2.8 MB

---

## 论文使用建议

### 引用关键数字
- 固定参数陷阱: 14.66pp敏感度 (图4.1)
- 组件贡献: ATR +1.87pp, Risk2% +0.38pp (表5.1)
- 交易成本稳健性: 0.30%仍盈利 (图5.3)

### 诚实局限性
- 2024测试期弱于Buy&Hold (p=0.017)
- 协同效应不明显 (+0.13pp)
- 小样本不稳定 (N=5-10)

---

**最后更新**: 2025-11-28
