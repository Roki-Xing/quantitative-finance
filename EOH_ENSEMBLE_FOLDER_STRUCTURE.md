# EOH Ensemble 实验文件夹结构

**创建日期**: 2025-11-28

**根目录**: `/root/autodl-tmp/eoh_ensemble_experiment/`

---

## 文件夹组织方案

```
/root/autodl-tmp/eoh_ensemble_experiment/
│
├── 00_scripts/                           # 所有执行脚本
│   ├── generate_ensemble_pool.sh         # 策略生成脚本
│   ├── filter_ensemble_strategies.py     # 策略筛选脚本
│   └── run_ensemble_backtest.py          # 集成回测脚本
│
├── 01_strategy_pool/                     # 策略池（20个策略）
│   ├── strategy_01/
│   │   ├── evolved_strategy.py           # LLM生成的策略代码
│   │   ├── backtest_results.json         # 训练期回测结果
│   │   └── strategy_description.txt      # 策略描述（如果有）
│   ├── strategy_02/
│   ├── ...
│   └── strategy_20/
│
├── 02_generation_logs/                   # 生成过程日志
│   ├── ensemble_generation.log           # 总日志
│   ├── strategy_01.log                   # 单个策略日志
│   ├── strategy_02.log
│   ├── ...
│   ├── strategy_20.log
│   └── generation_summary.txt            # 生成汇总
│
├── 03_filtered_strategies/               # 筛选后的top策略
│   ├── top_strategies.json               # Top 10策略ID列表
│   ├── filter_summary.txt                # 筛选结果汇总
│   └── strategy_rankings.csv             # 策略排名表
│
├── 04_individual_backtests/              # 单个策略回测结果
│   ├── us_market/                        # US市场测试
│   │   ├── SPY_strategy01_results.json
│   │   ├── SPY_strategy02_results.json
│   │   ├── ...
│   │   ├── QQQ_strategy01_results.json
│   │   └── QQQ_strategy02_results.json
│   │
│   └── cn_ashares/                       # A股市场测试
│       ├── 600519_strategy01_results.json  # 贵州茅台
│       ├── 600519_strategy02_results.json
│       ├── ...
│       └── 300059_strategy20_results.json  # 东方财富
│
├── 05_ensemble_backtests/                # 集成方法回测结果
│   ├── method1_simple_average/
│   │   ├── SPY_results.json
│   │   ├── QQQ_results.json
│   │   ├── 600519_results.json
│   │   └── ...
│   │
│   ├── method2_weighted_sharpe/
│   │   ├── SPY_results.json
│   │   └── ...
│   │
│   └── method3_portfolio_mv/
│       ├── SPY_results.json
│       └── ...
│
├── 06_analysis_results/                  # 分析结果
│   ├── ensemble_comparison.csv           # 集成方法对比表
│   ├── strategy_diversity_analysis.txt   # 策略多样性分析
│   ├── performance_statistics.json       # 性能统计
│   └── ensemble_vs_single_comparison.csv # 集成vs单策略对比
│
├── 07_visualizations/                    # 可视化图表
│   ├── ensemble_performance_comparison.png
│   ├── strategy_correlation_heatmap.png
│   ├── ensemble_vs_single_boxplot.png
│   └── cross_asset_success_rate.png
│
├── 08_reports/                           # 最终报告
│   ├── ENSEMBLE_ANALYSIS_REPORT.md       # 完整分析报告（S6）
│   ├── ENSEMBLE_EXECUTIVE_SUMMARY.md     # 执行摘要
│   └── ENSEMBLE_DATA_SUMMARY.json        # 数据汇总（机器可读）
│
└── README_EXPERIMENT.md                  # 实验说明文档
```

---

## 文件命名规范

### 策略文件
- 格式: `strategy_XX/` (XX = 01-20)
- 内容: evolved_strategy.py, backtest_results.json

### 日志文件
- 总日志: `ensemble_generation.log`
- 单个策略: `strategy_XX.log`

### 回测结果
- US市场: `{SYMBOL}_strategy{XX}_results.json` (例: SPY_strategy01_results.json)
- A股: `{CODE}_strategy{XX}_results.json` (例: 600519_strategy01_results.json)

### 分析文件
- CSV格式: 用于表格数据
- JSON格式: 用于结构化数据
- TXT格式: 用于文本报告
- MD格式: 用于最终文档

---

## 关键文件说明

### 必读文件（实验完成后）

1. **README_EXPERIMENT.md**
   - 作用: 实验总览，快速了解所有内容
   - 位置: 根目录
   - 读取顺序: 第1个

2. **08_reports/ENSEMBLE_EXECUTIVE_SUMMARY.md**
   - 作用: 执行摘要，关键发现
   - 位置: 08_reports/
   - 读取顺序: 第2个

3. **03_filtered_strategies/top_strategies.json**
   - 作用: Top 10策略列表
   - 位置: 03_filtered_strategies/
   - 读取顺序: 第3个

4. **06_analysis_results/ensemble_comparison.csv**
   - 作用: 集成方法性能对比
   - 位置: 06_analysis_results/
   - 读取顺序: 第4个

5. **08_reports/ENSEMBLE_ANALYSIS_REPORT.md**
   - 作用: 完整分析报告（S6）
   - 位置: 08_reports/
   - 读取顺序: 第5个

### 数据文件（供论文引用）

- `08_reports/ENSEMBLE_DATA_SUMMARY.json`: 所有关键数字的汇总
- `06_analysis_results/performance_statistics.json`: 性能统计
- `03_filtered_strategies/strategy_rankings.csv`: 策略排名

### 可视化文件（供论文使用）

- `07_visualizations/ensemble_performance_comparison.png`: 性能对比图
- `07_visualizations/strategy_correlation_heatmap.png`: 策略相关性热图

---

## 数据流向

```
Step 1: Strategy Generation
   00_scripts/generate_ensemble_pool.sh
   ↓
   01_strategy_pool/strategy_XX/
   02_generation_logs/

Step 2: Quality Filtering
   00_scripts/filter_ensemble_strategies.py
   ↓
   03_filtered_strategies/top_strategies.json

Step 3: Individual Backtesting
   (批量回测脚本，待实现)
   ↓
   04_individual_backtests/us_market/
   04_individual_backtests/cn_ashares/

Step 4: Ensemble Backtesting
   00_scripts/run_ensemble_backtest.py
   ↓
   05_ensemble_backtests/method{1,2,3}/

Step 5: Analysis
   (分析脚本，待实现)
   ↓
   06_analysis_results/
   07_visualizations/

Step 6: Report Generation
   (报告生成脚本，待实现)
   ↓
   08_reports/ENSEMBLE_ANALYSIS_REPORT.md
```

---

## 备份策略

### 实验中备份
- 每个阶段完成后，创建阶段快照
- 格式: `eoh_ensemble_experiment_stage{N}_YYYYMMDD.tar.gz`

### 最终备份
- 完整文件夹打包
- 格式: `eoh_ensemble_experiment_complete_20251128.tar.gz`
- 保存位置: `/root/autodl-tmp/backups/` 和本地桌面

---

## 磁盘空间估算

| 文件夹 | 预计大小 | 说明 |
|--------|---------|------|
| 01_strategy_pool | ~200MB | 20个策略 × ~10MB |
| 02_generation_logs | ~50MB | 日志文件 |
| 04_individual_backtests | ~100MB | 240个回测结果 |
| 05_ensemble_backtests | ~20MB | 36个回测结果 |
| 其他 | ~30MB | 分析、可视化、报告 |
| **总计** | **~400MB** | 完整实验 |

---

## 快速访问命令

```bash
# SSH到服务器
ssh -p 18077 root@connect.westd.seetacloud.com

# 进入实验目录
cd /root/autodl-tmp/eoh_ensemble_experiment

# 查看实验进度
cat 02_generation_logs/generation_summary.txt

# 查看Top策略
cat 03_filtered_strategies/top_strategies.json

# 查看分析结果
cat 06_analysis_results/ensemble_comparison.csv

# 查看最终报告
cat 08_reports/ENSEMBLE_EXECUTIVE_SUMMARY.md
```

---

## 版本控制

| 版本 | 日期 | 变更 |
|------|------|------|
| v1.0 | 2025-11-28 | 初始结构设计 |

---

**文件夹结构版本**: v1.0

**状态**: ✅ 准备创建

**下一步**: 在服务器上创建文件夹结构
