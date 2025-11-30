# Paper Supplementary Experiments - Download Instructions

**Created**: 2025-11-29
**Status**: P0 Tasks Complete (5/5) ✅
**Server**: root@connect.westd.seetacloud.com:18077

---

## Quick Download Command

Open PowerShell or Git Bash on your Desktop and run:

```bash
scp -P 18077 root@connect.westd.seetacloud.com:/root/autodl-tmp/paper_results_backup_20251129_231219.tar.gz .
```

Then extract:
```bash
tar -xzf paper_results_backup_20251129_231219.tar.gz
```

---

## Alternative: Download Individual Folders

### Method 1: Download entire paper_results folder
```bash
scp -r -P 18077 root@connect.westd.seetacloud.com:/root/autodl-tmp/paper_results ./paper_supplementary_experiments_2025-11-29/
```

### Method 2: Download specific sub-folders
```bash
# Core results
scp -r -P 18077 root@connect.westd.seetacloud.com:/root/autodl-tmp/paper_results/01_core_results ./

# Cross-market validation
scp -r -P 18077 root@connect.westd.seetacloud.com:/root/autodl-tmp/paper_results/02_cross_market ./

# Ablation studies
scp -r -P 18077 root@connect.westd.seetacloud.com:/root/autodl-tmp/paper_results/03_ablation_studies ./

# Baselines
scp -r -P 18077 root@connect.westd.seetacloud.com:/root/autodl-tmp/paper_results/04_baselines ./

# Sensitivity analysis
scp -r -P 18077 root@connect.westd.seetacloud.com:/root/autodl-tmp/paper_results/05_sensitivity ./

# Validation
scp -r -P 18077 root@connect.westd.seetacloud.com:/root/autodl-tmp/paper_results/06_validation ./

# Supplementary documents
scp -r -P 18077 root@connect.westd.seetacloud.com:/root/autodl-tmp/paper_results/08_supplementary ./
```

---

## What's Included (P0 Complete)

### ✅ P0-1: Per-Stock Detailed Results
- **Files**: `01_core_results/per_stock_detailed_results.{csv,json,md}`
- **Purpose**: Address Q1 reviewer concern
- **Data**: 5 A-shares, individual testing results

### ✅ P0-2: Buy-and-Hold Baseline Comparison
- **Files**: `04_baselines/buyhold_vs_llm_comparison.{csv,json,md}`
- **Purpose**: Address Q3 - comprehensive baseline comparison
- **Data**: 12 assets, honest comparison (LLM doesn't always win)

### ✅ P0-3: Local Optimization vs Adaptive
- **Files**: `05_sensitivity/local_optimization_comparison.{csv,md}`
- **Purpose**: Address Q3 - compare with locally optimized parameters
- **Key Finding**: Adaptive +22.68% vs Grid Search -0.18% (+22.87pp)

### ✅ P0-4: Q2 LLM Novelty Argumentation
- **Files**: `08_supplementary/Q2_LLM_Novelty_Argumentation.md` (8.0KB)
- **Purpose**: Address Q2 - "Where is LLM novelty?"
- **Key Arguments**: Discovery vs Invention, 360x faster, +22.87pp advantage

### ✅ P0-5: Cross-Market Validation Summary
- **Files**: `02_cross_market/cross_market_{validation_real.json,summary.{csv,md}}`
- **Purpose**: Validate Fixed Parameter Trap across 7 real markets
- **Key Findings**: 71.4% success rate, 6/7 markets had 0 trades with fixed params

---

## File Structure

```
paper_results/
├── 01_core_results/          # Main experimental results
│   ├── per_stock_detailed_results.{csv,json,md}
│   ├── day52_18ashares_results.{csv,json}
│   └── strategy013_original_2024_results.json
├── 02_cross_market/          # Cross-market validation
│   ├── cross_market_validation_real.json
│   └── cross_market_summary.{csv,md}
├── 03_ablation_studies/      # Component-wise analysis
│   └── ablation_study_results.json
├── 04_baselines/             # Baseline comparisons
│   ├── buyhold_vs_llm_comparison.{csv,json,md}
│   ├── classical_baselines_extended.json
│   └── extended_baseline_results.json
├── 05_sensitivity/           # Parameter sensitivity
│   ├── local_optimization_comparison.{csv,md}
│   ├── sensitivity_A_stop_loss.json
│   ├── sensitivity_B_position_size.json
│   ├── sensitivity_C_fully_adaptive.json
│   └── transaction_cost_sensitivity.json
├── 06_validation/            # Multi-year rolling validation
│   └── multi_year_rolling_validation.json
├── 08_supplementary/         # Supplementary documents
│   └── Q2_LLM_Novelty_Argumentation.md
├── Q1_Q2_Q3_DETAILED_RESPONSES.md
└── README_主索引.md
```

**Total**: 23 files, ~100KB
**Status**: All P0 (必需) tasks complete ✅

---

## Next Steps

After downloading, you can:
1. Review the markdown files for formatted summaries
2. Use CSV files for tables in the paper
3. Use JSON files for detailed data analysis
4. Integrate Q2_LLM_Novelty_Argumentation.md arguments into paper revision

---

## Support

If you encounter any issues:
1. Check SSH connection: `ssh -p 18077 root@connect.westd.seetacloud.com`
2. Verify files exist: `ls -lh /root/autodl-tmp/paper_results/`
3. Check archive: `ls -lh /root/autodl-tmp/paper_results_backup*.tar.gz`

**Document Version**: 1.0
**Last Updated**: 2025-11-29 23:12 UTC+8
