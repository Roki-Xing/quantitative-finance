# Complete File Manifest

**Paper Title**: Cross-Market Generalization of LLM-Based Trading Strategies: Identifying and Resolving the Fixed Parameter Trap

**Package Version**: v1.0

**Last Updated**: 2025-11-28

**Total Files**: ~56 files

**Total Size**: ~10-15MB

---

## I. Quick Navigation

| Category | File Count | Directory | Description |
|----------|-----------|-----------|-------------|
| **Root Documents** | 6 | `.`/ | Master documentation |
| **Reports** | 12 | `reports/` | Analysis reports |
| **Data** | 12 | `data/` | Experimental results (JSON) |
| **Code** | 18 | `code/` | Reproducible scripts (Python) |
| **Charts** | 5 | `charts/` | Visualizations (PNG) |
| **Results** | 3 | `results/` | CSV exports |

---

## II. Root Directory (6 files)

### Essential Documents (READ THESE FIRST)

#### `README_SUPPLEMENTARY_MATERIALS.md` ⭐ **START HERE**
- **Size**: ~20KB (~400 lines)
- **Purpose**: Master index for all supplementary materials
- **Contents**:
  - Package structure overview
  - Addresses all 5 paper weaknesses with evidence
  - Experimental scale summary (625+ backtests)
  - Citation guidelines (S1-S5 mapping)
  - Quick access index
  - Document reading guide for reviewers
- **Supplementary Material ID**: N/A (meta-document)
- **Must Read**: YES - Read this first to navigate package

#### `FILE_MANIFEST.md` (THIS FILE)
- **Size**: ~15KB (~600 lines)
- **Purpose**: Complete file listing with descriptions
- **Contents**:
  - All files organized by directory
  - File sizes and purposes
  - Quick navigation index
  - File dependency map
- **Supplementary Material ID**: N/A (meta-document)
- **Must Read**: YES - Use this to find specific files

### Submission Preparation Documents

#### `SUBMISSION_CHECKLIST.md`
- **Size**: ~25KB (~600 lines)
- **Purpose**: Pre-submission verification checklist
- **Contents**:
  - Document completeness verification (all files present)
  - Content quality verification (statistics, experiments)
  - Addresses all 5 weaknesses checklist
  - Reproducibility verification
  - File organization check
  - Pre-submission final checks (24h, 1h before)
  - Submission portal requirements (NeurIPS, ICML, AAAI, ICLR)
  - Post-review preparation
- **Use When**: Before creating ZIP package for submission
- **Must Read**: YES - before packaging

#### `REVIEWER_RESPONSE_TEMPLATE.md`
- **Size**: ~30KB (~800 lines)
- **Purpose**: Response templates for reviewer comments
- **Contents**:
  - 5 complete response templates (one per weakness)
  - General response strategies
  - Statistical significance response template
  - Reproducibility response template
  - Cross-references to supplementary materials (S1-S5)
- **Use When**: During revision phase, responding to reviewers
- **Must Read**: When preparing revision letter

#### `PAPER_CITATION_TEMPLATES.md`
- **Size**: ~30KB (~900 lines)
- **Purpose**: LaTeX citation examples for main paper
- **Contents**:
  - Abstract citations
  - Method section citations (HPDT, CCT, adaptive parameters)
  - Results section citations (all experiments)
  - Discussion section citations (theoretical framework)
  - Table/figure caption templates
  - BibTeX entries for supplementary materials
  - Inline citation examples
  - Overleaf/LaTeX project setup
- **Use When**: Writing/revising main paper LaTeX
- **Must Read**: When integrating supplementary materials into paper

#### `PACKAGING_GUIDE.md`
- **Size**: ~35KB (~900 lines)
- **Purpose**: Instructions for creating submission ZIP package
- **Contents**:
  - Pre-packaging checklist
  - Directory structure organization
  - Step-by-step packaging instructions (Windows, 7-Zip, Python)
  - Post-packaging verification
  - Naming conventions
  - Upload instructions for journals
  - Troubleshooting
  - Backup and version control
  - Automated packaging pipeline (Python script included)
- **Use When**: Creating ZIP for submission
- **Must Read**: Before packaging materials

---

## III. Reports Directory (12 files)

### Core Reports (Supplementary Materials S1-S3)

#### `PROMPT_ENGINEERING_COMPREHENSIVE_REPORT.md` ⭐ **S1**
- **Size**: ~25KB (~500 lines)
- **Supplementary Material ID**: S1
- **Purpose**: Validates HPDT and CCT through 120 backtests
- **Addresses**: Weakness #1 (Prompt Engineering)
- **Contents**:
  - HPDT validation (Day 9, 20 backtests)
    - Gentle vs harsh prompts: 75% vs 0% success (p<0.001, Cohen's h=2.39)
  - CCT validation (Day 12, 100 backtests)
    - Temperature sweep: 0.1-1.0, optimal T=0.2 (100% success)
  - Statistical analysis (Fisher's exact test, Cohen's h)
  - Raw data tables
  - Paper writing templates
- **Key Finding**: HPDT and CCT are statistically validated (p<0.001, large effect sizes)
- **Citation in Paper**: "See Supplementary Material S1"

#### `CAUSALITY_ANALYSIS.md` ⭐ **S2**
- **Size**: ~40KB (~850 lines)
- **Supplementary Material ID**: S2
- **Purpose**: 5-layer causal evidence + formal theoretical framework
- **Addresses**: Weakness #2 (Causality), Weakness #5 (Theory)
- **Contents**:
  - **Section 1-2**: Pearl's Causal DAG
  - **Section 3**: Ablation study (ATR +16.6pp, Risk2% +37.6pp, Cohen's d=1.42)
  - **Section 4**: Parameter sensitivity analysis (47.2pp variance)
  - **Section 5**: Multi-year validation (2022/2023/2024)
  - **Section 6-7**: Controlled experiment (ATE = +292.81pp, 95% CI: [+180%, +405%])
  - **Section 8**: Formal definitions (4 definitions)
  - **Section 9**: Mathematical theorems (2 theorems with proofs)
  - **Section 10**: Theoretical connections
    - Concept Drift (Gama et al., 2014)
    - Transfer Learning (Pan & Yang, 2010)
    - Robust Optimization (Ben-Tal & Nemirovski, 2002)
- **Key Finding**: Causal relationship established through 5 layers, ATE=+292.81pp
- **Citation in Paper**: "See Supplementary Material S2" or "See S2, Section X"

#### `CLASSICAL_BASELINES_RESULTS.md` ⭐ **S3**
- **Size**: ~35KB (~700 lines)
- **Supplementary Material ID**: S3
- **Purpose**: Extended baseline comparison (7 strategies, 80 new backtests)
- **Addresses**: Weakness #3 (Limited Baselines)
- **Contents**:
  - Experimental design (4 strategies × 10 assets × 2 periods)
  - Training period results (2018-2023)
  - Testing period results (2024 out-of-sample)
  - Comparison with LLM_Adaptive
  - Fixed Parameter Trap evidence (35-136pp spreads)
  - Academic literature support (Jegadeesh & Titman 1993, etc.)
  - Paper writing templates
  - Reviewer response templates
- **Key Finding**: All classical strategies exhibit Fixed Parameter Trap (Momentum 136pp, MACD 91pp)
- **Citation in Paper**: "See Supplementary Material S3"

### Supporting Reports

#### `CLASSICAL_BASELINES_ANALYSIS.md`
- **Size**: ~40KB (~850 lines)
- **Purpose**: Theoretical framework for classical baselines (pre-experiment prediction)
- **Contents**:
  - 7 strategy descriptions with academic citations
  - Theoretical predictions for performance
  - Parameter rigidity analysis framework
  - Expected results
  - Connections to literature
- **Relation to S3**: This is the theoretical pre-analysis; S3 is the actual results
- **Use**: Background reading for understanding classical strategy theory

#### `ablation_study_report.md`
- **Size**: ~15KB (~300 lines)
- **Purpose**: Detailed ablation study results
- **Contents**:
  - 2×2 factorial design (ATR × Risk2%)
  - Per-asset breakdown
  - Main effects and interaction effects
  - Statistical tests (Cohen's d, t-tests)
- **Relation to S2**: Detailed version of S2 Section 3
- **Use**: Extended analysis, not directly cited in paper

#### `parameter_sensitivity_report.md`
- **Size**: ~18KB (~400 lines)
- **Purpose**: Parameter sensitivity analysis results
- **Contents**:
  - Stop-loss sensitivity (7 values: $50-$350)
  - Position size sensitivity (7 values: 10-40 shares)
  - Performance variance analysis (47.2pp for fixed, 8.4pp for adaptive)
  - Charts and tables
- **Relation to S2**: Detailed version of S2 Section 4
- **Use**: Extended analysis for parameter robustness

#### `transaction_cost_report.md`
- **Size**: ~12KB (~250 lines)
- **Purpose**: Transaction cost sensitivity analysis
- **Contents**:
  - Commission levels tested: 0%, 0.1%, 0.15%, 0.3%, 0.5%
  - Performance degradation analysis
  - Break-even analysis
- **Use**: Robustness check for real-world trading costs
- **Citation**: Optional, can cite for robustness validation

#### `multi_year_rolling_validation_report.md`
- **Size**: ~15KB (~300 lines)
- **Purpose**: Multi-year rolling window validation
- **Contents**:
  - 2022/2023/2024 independent test results
  - Rolling window methodology
  - Temporal consistency analysis
  - Bootstrap confidence intervals
- **Relation to S2**: Detailed version of S2 Section 5
- **Relation to S4**: Source of multi-year data
- **Use**: Temporal generalization validation

#### `statistical_report_full.md`
- **Size**: ~20KB (~450 lines)
- **Purpose**: Comprehensive statistical analysis across all experiments
- **Contents**:
  - Descriptive statistics (means, SDs, ranges)
  - Inferential statistics (t-tests, effect sizes)
  - Bootstrap confidence intervals methodology
  - Comparison tables
  - Statistical test results summary
- **Relation to S4**: Main statistical report
- **Use**: Methodological reference for statistical procedures

#### `baseline_statistical_report.md`
- **Size**: ~10KB (~200 lines)
- **Purpose**: Statistical comparison of baselines vs LLM_Adaptive
- **Contents**:
  - Pairwise comparisons (all strategies vs LLM_Adaptive)
  - Success rate comparisons
  - Risk-adjusted metrics
- **Use**: Quick reference for baseline comparison stats

#### `data_consistency_summary.md`
- **Size**: ~8KB (~150 lines)
- **Purpose**: Data quality and consistency verification
- **Contents**:
  - Missing value analysis
  - Date range verification
  - Price data integrity checks
  - Volume data consistency
- **Use**: Data quality assurance documentation
- **Audience**: Reviewers asking about data quality

#### `gap_analysis_and_roadmap.md`
- **Size**: ~10KB (~200 lines)
- **Purpose**: Internal document identifying gaps and future work
- **Contents**:
  - Current limitations
  - Missing experiments
  - Future research directions
  - Roadmap for extended paper
- **Use**: Internal planning, NOT for submission
- **Note**: May exclude from final package (internal only)

---

## IV. Data Directory (12 JSON files)

### Primary Experimental Data

#### `classical_baselines_extended.json` ⭐
- **Size**: ~3MB
- **Purpose**: 80 backtests for 4 classical strategies
- **Supplementary Material**: Related to S3
- **Contents**:
  ```json
  {
    "metadata": {
      "total_backtests": 80,
      "strategies": ["Momentum", "MeanReversion", "Bollinger", "MACD"],
      "assets": [10 A-share stocks],
      "periods": ["training", "testing"]
    },
    "results": {
      "Momentum": {
        "600519_贵州茅台": {
          "training": {"returns_pct": 61.93, "sharpe_ratio": 0.382, ...},
          "testing": {"returns_pct": -16.57, "sharpe_ratio": 0, ...}
        },
        ...
      },
      ...
    }
  }
  ```
- **Fields per backtest**:
  - `returns_pct`: Percentage return
  - `sharpe_ratio`: Risk-adjusted return
  - `max_drawdown_pct`: Maximum drawdown
  - `total_trades`: Number of trades executed
  - `final_value`: Final portfolio value
- **Use in Paper**: Table 5.X (Classical Baselines Performance)

#### `statistical_robustness_results.json` ⭐
- **Size**: ~2MB
- **Purpose**: Bootstrap confidence intervals and multi-year validation
- **Supplementary Material**: S4 (partial)
- **Contents**:
  ```json
  {
    "bootstrap_ci": {
      "2024_A_shares": {
        "mean_return": 5.63,
        "ci_lower": 0.8,
        "ci_upper": 10.4,
        "iterations": 10000,
        "confidence_level": 0.95
      },
      ...
    },
    "multi_year_validation": {
      "2022": {"adaptive": 12.8, "fixed": -43.2, "improvement": 56.0, ...},
      "2023": {"adaptive": 8.4, "fixed": -51.7, "improvement": 60.1, ...},
      "2024": {"adaptive": 5.6, "fixed": -65.1, "improvement": 70.7, ...}
    }
  }
  ```
- **Use in Paper**: Multi-year validation table, Bootstrap CI reporting

#### `ablation_study_results.json` ⭐
- **Size**: ~1.5MB
- **Purpose**: 2×2 factorial ablation study results
- **Supplementary Material**: Related to S2 Section 3
- **Contents**:
  ```json
  {
    "configurations": {
      "baseline": {"atr_stop": false, "risk2pct": false, "avg_return": -65.10},
      "atr_only": {"atr_stop": true, "risk2pct": false, "avg_return": -48.50},
      "risk2_only": {"atr_stop": false, "risk2pct": true, "avg_return": -27.48},
      "full_adaptive": {"atr_stop": true, "risk2pct": true, "avg_return": -23.19}
    },
    "main_effects": {
      "atr_effect": 16.60,
      "risk2_effect": 37.62,
      "interaction": 4.31,
      "cohens_d": {"atr": 0.68, "risk2": 1.42}
    },
    "per_asset_results": {...}
  }
  ```
- **Use in Paper**: Table X (Ablation Study), decomposing causal mechanisms

#### `multi_year_rolling_validation.json`
- **Size**: ~1MB
- **Purpose**: 2022/2023/2024 rolling window validation
- **Supplementary Material**: Related to S2 Section 5, S4
- **Contents**:
  - Year-by-year results for both fixed and adaptive parameters
  - Rolling window methodology details
  - Bootstrap confidence intervals for each year
  - Market condition annotations (bull/bear/sideways)
- **Use in Paper**: Multi-year validation table (Section 4.4 or 5.X)

### Baseline Comparison Data

#### `baseline_comparison_results.json`
- **Size**: ~2.5MB
- **Purpose**: Initial baseline comparison (Buy&Hold, SMA, RSI)
- **Contents**:
  - 3 baseline strategies × 12 assets × 2 periods
  - Performance metrics
  - Comparison with LLM_Adaptive
- **Use**: Background data, extended by classical_baselines_extended.json

#### `extended_baseline_results.json`
- **Size**: ~1MB
- **Purpose**: Extended baseline comparison with additional metrics
- **Contents**:
  - Sharpe ratios
  - Sortino ratios
  - Maximum drawdowns
  - Calmar ratios
  - Win rates
- **Use**: Risk-adjusted performance comparison

#### `strategy013_original_2024_results.json`
- **Size**: ~800KB
- **Purpose**: Original strategy (fixed params) 2024 out-of-sample test
- **Contents**:
  - 10 A-shares 2024 backtest results
  - Fixed $200 stop-loss, fixed 20 shares
  - Performance: -65.10% average return
- **Use**: Control group for causal analysis (ATE calculation)
- **Related to**: Controlled experiment (S2 Section 7)

### Sensitivity Analysis Data

#### `sensitivity_A_stop_loss.json`
- **Size**: ~1.2MB
- **Purpose**: Stop-loss parameter sensitivity analysis
- **Contents**:
  - 7 stop-loss values tested: [$50, $100, $150, $200, $250, $300, $350]
  - Performance across 10 A-shares for each value
  - Variance analysis (47.2pp variance for fixed params)
- **Use**: Evidence that fixed stop-loss causes instability

#### `sensitivity_B_position_size.json`
- **Size**: ~1.2MB
- **Purpose**: Position size parameter sensitivity analysis
- **Contents**:
  - 7 position sizes tested: [10, 15, 20, 25, 30, 35, 40 shares]
  - Performance across 10 A-shares for each value
  - Comparison with 2% risk adaptive sizing
- **Use**: Evidence that fixed position sizing causes instability

#### `sensitivity_C_fully_adaptive.json`
- **Size**: ~800KB
- **Purpose**: Fully adaptive parameters performance
- **Contents**:
  - ATR×3 stop-loss + 2% risk sizing
  - Performance across 10 A-shares
  - Variance analysis (8.4pp variance, 5.6× more stable)
- **Use**: Evidence that adaptive parameters provide stability

### Other Data

#### `transaction_cost_sensitivity.json`
- **Size**: ~600KB
- **Purpose**: Performance under different commission levels
- **Contents**:
  - 5 commission levels: [0%, 0.1%, 0.15%, 0.3%, 0.5%]
  - Performance degradation analysis
  - Break-even analysis
- **Use**: Robustness validation for real-world trading

#### `day21_portfolio_optimization.json`
- **Size**: ~500KB
- **Purpose**: Portfolio-level optimization experiments (Day 21)
- **Contents**:
  - Multi-asset portfolio results
  - Risk-parity weighting
  - Sharpe ratio optimization
- **Use**: Advanced topic, may not cite in main paper

---

## V. Code Directory (18 Python scripts + 1 guide)

### Essential Code (Supplementary Material S5)

#### `EOH_USAGE_GUIDE.md` ⭐ **S5**
- **Size**: ~15KB (~267 lines)
- **Supplementary Material ID**: S5
- **Purpose**: Complete usage guide for EOH framework
- **Addresses**: Reproducibility
- **Contents**:
  - **Scenario 1**: Use existing adaptive strategy (no LLM needed)
    - Step-by-step instructions
    - Example commands
    - Expected results
  - **Scenario 2**: Generate new strategy with LLM (research use)
    - EOH framework setup
    - LLM invocation
    - Manual parameter improvement
  - Scenario comparison table
  - FAQ (10+ questions)
  - Technical architecture diagram
- **Use**: Reproducibility guide for reviewers/readers
- **Citation in Paper**: "See Supplementary Material S5"

### Core Analysis Scripts

#### `statistical_robustness_analysis.py` ⭐
- **Size**: ~30KB (~558 lines)
- **Purpose**: Bootstrap confidence intervals + effect size calculations
- **Produces**: `statistical_robustness_results.json`
- **Dependencies**: `numpy`, `scipy`, `pandas`
- **Key Functions**:
  - `bootstrap_ci(data, n_iterations=10000)`: Bootstrap 95% CI
  - `calculate_cohens_d(group1, group2)`: Effect size
  - `wilson_score_interval(successes, total)`: Proportion CI
- **Usage**:
  ```bash
  python statistical_robustness_analysis.py \
    --data data/raw_backtests.json \
    --output data/statistical_robustness_results.json
  ```
- **Reproducibility**: Fully documented, sets random seed (42)
- **Citation**: "Statistical analysis performed using `statistical_robustness_analysis.py` (S5)"

#### `classical_baselines_strategies.py` ⭐
- **Size**: ~20KB (~365 lines)
- **Purpose**: Implement 4 classical strategies
- **Produces**: `classical_baselines_extended.json`
- **Strategies Implemented**:
  1. **Momentum** (Jegadeesh & Titman 1993):
     - 20-day ROC, 5% threshold
     - Fixed 95% equity per trade
  2. **Mean Reversion** (Lo & MacKinlay 1988):
     - SMA(20) ± 2σ bands
     - Buy at lower band, sell at upper
  3. **Bollinger Bands** (Bollinger 1992):
     - 20-day SMA, 2σ envelope
     - Dynamic volatility adjustment
  4. **MACD** (Appel 1979):
     - 12/26/9 EMA parameters
     - Signal line crossover
- **Framework**: Backtrader 1.9.76
- **Usage**:
  ```bash
  python classical_baselines_strategies.py \
    --strategies all \
    --data-dir backtest_data_extended/ \
    --output classical_baselines_extended.json
  ```
- **Reproducibility**: Fixed parameters documented, deterministic execution

#### `run_strategy_on_new_data.py` ⭐
- **Size**: ~15KB (~263 lines)
- **Purpose**: Apply adaptive strategy to new CSV data (no LLM needed)
- **Implements**: Adaptive_Strategy_13
  - LLM logic: SMA(20/50) crossover + RSI(14) filter
  - Adaptive params: ATR×3 stop-loss + 2% risk sizing
- **Usage**:
  ```bash
  python run_strategy_on_new_data.py \
    --data new_stock.csv \
    --train-start 2020-01-01 \
    --train-end 2023-12-31 \
    --test-start 2024-01-01 \
    --test-end 2024-12-31
  ```
- **Outputs**: `new_stock_results.json` with training/testing metrics
- **Reproducibility**: Complete implementation, ready to use
- **Citation**: "Adaptive strategy applied using `run_strategy_on_new_data.py` (S5)"

#### `analyze_classical_baselines.py`
- **Size**: ~10KB (~195 lines)
- **Purpose**: Analyze and summarize classical baselines results
- **Inputs**: `classical_baselines_extended.json`
- **Outputs**: Summary tables, comparison statistics
- **Key Analyses**:
  - Average return by strategy
  - Success rate calculation
  - Performance spread (max - min across assets)
  - Comparison with LLM_Adaptive
- **Usage**:
  ```bash
  python analyze_classical_baselines.py \
    --input classical_baselines_extended.json \
    --output classical_baselines_summary.txt
  ```

### Experimental Scripts

#### `run_ablation_study.py`
- **Size**: ~18KB (~400 lines)
- **Purpose**: Run 2×2 factorial ablation study
- **Produces**: `ablation_study_results.json`, `ablation_study_report.md`
- **Experimental Design**:
  - Factor A: ATR dynamic stop-loss (yes/no)
  - Factor B: 2% risk sizing (yes/no)
  - 4 configurations × 10 assets × 2 periods = 80 backtests
- **Usage**:
  ```bash
  python run_ablation_study.py \
    --data-dir backtest_data_extended/ \
    --output ablation_study_results.json
  ```

#### `ablation_study_strategies.py`
- **Size**: ~15KB (~300 lines)
- **Purpose**: Strategy implementations for ablation study
- **Implements**: 4 configurations (Baseline, ATR-only, Risk2%-only, Full-Adaptive)
- **Framework**: Backtrader

#### `run_parameter_sensitivity_analysis.py`
- **Size**: ~20KB (~450 lines)
- **Purpose**: Run parameter sensitivity analysis
- **Produces**: `sensitivity_A_stop_loss.json`, `sensitivity_B_position_size.json`, `sensitivity_C_fully_adaptive.json`
- **Experimental Design**:
  - Stop-loss sweep: 7 values ($50-$350)
  - Position size sweep: 7 values (10-40 shares)
  - Total: 49 combinations × 10 assets × 2 periods = 980 backtests
- **Usage**:
  ```bash
  python run_parameter_sensitivity_analysis.py \
    --data-dir backtest_data_extended/ \
    --output-dir data/
  ```

#### `parameter_sensitivity_strategies.py`
- **Size**: ~12KB (~250 lines)
- **Purpose**: Strategy implementations for parameter sensitivity
- **Implements**: Parameterized strategies for sensitivity testing

#### `analyze_parameter_sensitivity.py`
- **Size**: ~15KB (~300 lines)
- **Purpose**: Analyze parameter sensitivity results
- **Produces**: Charts, variance analysis
- **Outputs**:
  - `charts/stop_loss_sensitivity_curves.png`
  - `charts/position_size_sensitivity_curves.png`
  - Variance statistics (47.2pp for fixed, 8.4pp for adaptive)

#### `multi_year_rolling_validation.py`
- **Size**: ~18KB (~400 lines)
- **Purpose**: Run multi-year rolling window validation
- **Produces**: `multi_year_rolling_validation.json`, `multi_year_rolling_validation_report.md`
- **Methodology**:
  - 3 years: 2022, 2023, 2024
  - Rolling window: Use prior years for training, current year for testing
  - Walk-forward validation (no look-ahead bias)
- **Usage**:
  ```bash
  python multi_year_rolling_validation.py \
    --data-dir backtest_data_extended/ \
    --output multi_year_rolling_validation.json
  ```

#### `generate_multiyear_report.py`
- **Size**: ~10KB (~200 lines)
- **Purpose**: Generate multi-year validation report from JSON
- **Inputs**: `multi_year_rolling_validation.json`
- **Outputs**: `multi_year_rolling_validation_report.md`

#### `transaction_cost_sensitivity.py`
- **Size**: ~15KB (~300 lines)
- **Purpose**: Test performance under different transaction costs
- **Produces**: `transaction_cost_sensitivity.json`, `transaction_cost_report.md`
- **Commission levels**: [0%, 0.1%, 0.15%, 0.3%, 0.5%]
- **Analysis**: Performance degradation, break-even points

#### `generate_transaction_cost_report.py`
- **Size**: ~8KB (~150 lines)
- **Purpose**: Generate transaction cost report from JSON

#### `extended_baseline_comparison.py`
- **Size**: ~16KB (~350 lines)
- **Purpose**: Extended baseline comparison with additional metrics
- **Produces**: `extended_baseline_results.json`
- **Metrics**: Sharpe, Sortino, Calmar, Max Drawdown, Win Rate

### Utility Scripts

#### `statistical_analysis.py`
- **Size**: ~15KB (~300 lines)
- **Purpose**: General-purpose statistical analysis
- **Functions**:
  - Descriptive statistics
  - Hypothesis testing (t-tests, Fisher exact)
  - Effect size calculations
  - Chart generation
- **Usage**:
  ```bash
  python statistical_analysis.py \
    --input baseline_comparison_results.json \
    --output statistical_report.md \
    --charts-dir charts/
  ```

#### `baseline_analysis_simple.py`
- **Size**: ~8KB (~150 lines)
- **Purpose**: Quick baseline comparison analysis
- **Outputs**: Simple comparison tables

#### `data_consistency_check.py`
- **Size**: ~10KB (~200 lines)
- **Purpose**: Verify data quality and consistency
- **Produces**: `data_consistency_summary.md`
- **Checks**:
  - Missing values
  - Date gaps
  - Price anomalies
  - Volume consistency

---

## VI. Charts Directory (5 PNG files)

### Performance Comparison Charts

#### `testing_returns_comparison.png`
- **Size**: ~400KB
- **Dimensions**: 1920×1080 pixels
- **Purpose**: 2024 out-of-sample returns comparison across 7 strategies
- **Contents**:
  - Bar chart: 7 strategies × 10 A-shares
  - Color-coded by strategy
  - Error bars: Bootstrap 95% CI
  - Success rate annotations
- **Generated by**: `statistical_analysis.py` or `analyze_classical_baselines.py`
- **Use in Paper**: Figure X (Performance Comparison), likely in Section 5 (Results)
- **Key Insight**: Bollinger 90% success, MACD +16.92% return, LLM_Adaptive 80% success

#### `training_returns_comparison.png`
- **Size**: ~450KB
- **Dimensions**: 1920×1080 pixels
- **Purpose**: Training period (2018-2023) returns comparison
- **Contents**:
  - Bar chart: 7 strategies × 10 A-shares
  - Shows overfitting patterns (MACD +31.88% training vs +16.92% testing)
- **Use in Paper**: Figure X (Training vs Testing Comparison)
- **Key Insight**: Performance degradation from training to testing (-3pp to -15pp)

#### `training_returns_boxplot.png`
- **Size**: ~300KB
- **Dimensions**: 1600×900 pixels
- **Purpose**: Distribution of training returns by strategy
- **Contents**:
  - Box plots showing median, quartiles, outliers
  - Visualizes variance across strategies
- **Use in Paper**: Optional, for showing performance distribution
- **Key Insight**: MACD highest variance (σ=74.59%), Mean Reversion most stable (σ=30.95%)

### Sensitivity Analysis Charts

#### `stop_loss_sensitivity_curves.png`
- **Size**: ~350KB
- **Dimensions**: 1800×1000 pixels
- **Purpose**: Visualize stop-loss parameter sensitivity
- **Contents**:
  - Line chart: Performance vs stop-loss value ($50-$350)
  - Multiple lines: 10 A-shares
  - Shows 47.2pp variance for fixed parameters
- **Generated by**: `analyze_parameter_sensitivity.py`
- **Use in Paper**: Figure X (Parameter Sensitivity)
- **Key Insight**: Fixed stop-loss causes large variance across assets

#### `position_size_sensitivity_curves.png`
- **Size**: ~350KB
- **Dimensions**: 1800×1000 pixels
- **Purpose**: Visualize position size parameter sensitivity
- **Contents**:
  - Line chart: Performance vs position size (10-40 shares)
  - Multiple lines: 10 A-shares
  - Shows similar 40+pp variance
- **Use in Paper**: Figure X (Position Size Sensitivity)
- **Key Insight**: Fixed position sizing causes instability

---

## VII. Results Directory (3 CSV files)

**Note**: These CSV files are exports for easy viewing in Excel/Sheets. The authoritative data is in JSON format.

#### `sensitivity_A_data.csv`
- **Size**: ~200KB
- **Purpose**: Stop-loss sensitivity data in tabular format
- **Columns**: Asset, Stop-Loss Value, Training Return, Testing Return, Sharpe Ratio, Max Drawdown
- **Use**: Quick Excel analysis, creating custom charts
- **Authoritative Source**: `sensitivity_A_stop_loss.json`

#### `sensitivity_B_data.csv`
- **Size**: ~200KB
- **Purpose**: Position size sensitivity data in tabular format
- **Columns**: Asset, Position Size, Training Return, Testing Return, Sharpe Ratio, Max Drawdown
- **Authoritative Source**: `sensitivity_B_position_size.json`

#### `sensitivity_C_data.csv`
- **Size**: ~150KB
- **Purpose**: Fully adaptive parameters data in tabular format
- **Columns**: Asset, Training Return, Testing Return, Sharpe Ratio, Max Drawdown, Total Trades
- **Authoritative Source**: `sensitivity_C_fully_adaptive.json`

---

## VIII. File Dependencies and Relationships

### Data Flow Diagram

```
[Raw CSV Data] → [Backtest Scripts] → [JSON Results] → [Analysis Scripts] → [Reports + Charts]
                                                                            ↘ [CSV Exports]
```

### Detailed Dependencies

**classical_baselines_extended.json** (output)
← Generated by: `classical_baselines_strategies.py`
← Input: CSV files in `backtest_data_extended/` (10 A-shares)
→ Analyzed by: `analyze_classical_baselines.py`
→ Produces: `CLASSICAL_BASELINES_RESULTS.md`, summary tables

**statistical_robustness_results.json** (output)
← Generated by: `statistical_robustness_analysis.py`
← Inputs: `classical_baselines_extended.json`, `strategy013_original_2024_results.json`, other backtest JSONs
→ Produces: Bootstrap CIs, multi-year validation results
→ Referenced in: `CAUSALITY_ANALYSIS.md` (S2)

**ablation_study_results.json** (output)
← Generated by: `run_ablation_study.py` (uses `ablation_study_strategies.py`)
← Input: CSV files
→ Analyzed by: `ablation_study_report.md` generation
→ Referenced in: `CAUSALITY_ANALYSIS.md` Section 3 (S2)

**multi_year_rolling_validation.json** (output)
← Generated by: `multi_year_rolling_validation.py`
← Input: CSV files (2022/2023/2024 data)
→ Analyzed by: `generate_multiyear_report.py`
→ Produces: `multi_year_rolling_validation_report.md`
→ Referenced in: `CAUSALITY_ANALYSIS.md` Section 5 (S2)

**Charts**
← Generated by: `statistical_analysis.py`, `analyze_parameter_sensitivity.py`
← Inputs: JSON result files
→ Used in: Paper figures
→ Also saved in: `charts/` directory

---

## IX. Supplementary Materials Mapping

### Complete S1-S5 Mapping

| ID | Primary Document | Supporting Documents | Data Files | Code Scripts |
|----|-----------------|---------------------|------------|--------------|
| **S1** | `PROMPT_ENGINEERING_COMPREHENSIVE_REPORT.md` | Day 9/12 summaries | Day 9/12 data (in other archives) | N/A (historical experiments) |
| **S2** | `CAUSALITY_ANALYSIS.md` | `ablation_study_report.md`, `parameter_sensitivity_report.md`, `multi_year_rolling_validation_report.md` | `ablation_study_results.json`, `sensitivity_*.json`, `multi_year_rolling_validation.json`, `strategy013_original_2024_results.json` | `run_ablation_study.py`, `run_parameter_sensitivity_analysis.py`, `multi_year_rolling_validation.py` |
| **S3** | `CLASSICAL_BASELINES_RESULTS.md` | `CLASSICAL_BASELINES_ANALYSIS.md` | `classical_baselines_extended.json`, `extended_baseline_results.json` | `classical_baselines_strategies.py`, `analyze_classical_baselines.py` |
| **S4** | `statistical_robustness_results.json` | `statistical_report_full.md`, `baseline_statistical_report.md` | `multi_year_rolling_validation.json`, `transaction_cost_sensitivity.json` | `statistical_robustness_analysis.py`, `statistical_analysis.py` |
| **S5** | `code/EOH_USAGE_GUIDE.md` | All code scripts | N/A (guide document) | `run_strategy_on_new_data.py` (main reproducibility script) |

### Paper Citation Guide

**When to cite S1**:
- "Prompt engineering validated through 120 backtests (S1)"
- "HPDT and CCT principles (see S1 for complete experiments)"

**When to cite S2**:
- "5-layer causal evidence chain (S2)"
- "Pearl's DAG and mathematical theorems (S2, Sections 8-9)"
- "Ablation study results (S2, Section 3)"
- "Multi-year validation (S2, Section 5)"

**When to cite S3**:
- "7 classical strategies comparison (S3)"
- "Fixed Parameter Trap evidence across all classical strategies (S3)"
- "Academic literature support for baselines (S3)"

**When to cite S4**:
- "Bootstrap 95% CI (S4: statistical_robustness_results.json)"
- "Multi-year rolling validation (S4)"
- "Statistical methodology (S4)"

**When to cite S5**:
- "Reproducibility ensured (S5: EOH_USAGE_GUIDE.md)"
- "Complete code implementation (S5)"

---

## X. Size Summary

### By Directory

| Directory | File Count | Total Size | Average Size |
|-----------|-----------|------------|--------------|
| Root | 6 | ~125KB | ~21KB |
| reports/ | 12 | ~250KB | ~21KB |
| data/ | 12 | ~15MB | ~1.25MB |
| code/ | 19 | ~300KB | ~16KB |
| charts/ | 5 | ~1.8MB | ~360KB |
| results/ | 3 | ~550KB | ~183KB |
| **TOTAL** | **57** | **~18MB** | - |

### Compression Estimate

- Uncompressed: ~18MB
- ZIP compressed (typical): ~10-12MB
- Compression ratio: ~40-45%

### Journal Compatibility

| Journal | Limit | Our Package | Status |
|---------|-------|-------------|--------|
| NeurIPS | 100MB | ~10-12MB | ✅ OK (10-12%) |
| ICML | 100MB | ~10-12MB | ✅ OK (10-12%) |
| AAAI | 50MB | ~10-12MB | ✅ OK (20-24%) |
| ICLR | 100MB | ~10-12MB | ✅ OK (10-12%) |

---

## XI. File Type Summary

### By File Type

| Type | Count | Purpose | Examples |
|------|-------|---------|----------|
| `.md` (Markdown) | 19 | Reports, documentation | README, CAUSALITY_ANALYSIS.md |
| `.json` (JSON) | 12 | Experimental data | classical_baselines_extended.json |
| `.py` (Python) | 18 | Analysis scripts | statistical_robustness_analysis.py |
| `.png` (Image) | 5 | Visualizations | testing_returns_comparison.png |
| `.csv` (CSV) | 3 | Tabular exports | sensitivity_A_data.csv |
| **TOTAL** | **57** | - | - |

---

## XII. Critical Files for Reviewers

### If Reviewers Have Limited Time

**Must Read (Priority 1)**:
1. `README_SUPPLEMENTARY_MATERIALS.md` - Master index
2. `CAUSALITY_ANALYSIS.md` (S2) - Most comprehensive analysis
3. `CLASSICAL_BASELINES_RESULTS.md` (S3) - Latest experiments

**Should Read (Priority 2)**:
4. `PROMPT_ENGINEERING_COMPREHENSIVE_REPORT.md` (S1) - Prompt engineering validation
5. `EOH_USAGE_GUIDE.md` (S5) - Reproducibility guide

**Optional (Priority 3)**:
6. Supporting reports (`ablation_study_report.md`, etc.)
7. Data files (`classical_baselines_extended.json`, etc.)
8. Code scripts (for detailed implementation)

### For Specific Reviewer Concerns

**Concern: "Insufficient prompt engineering validation"**
→ Read: `PROMPT_ENGINEERING_COMPREHENSIVE_REPORT.md` (S1)
→ Data: Day 9/12 experiments (120 backtests)

**Concern: "Causality not established"**
→ Read: `CAUSALITY_ANALYSIS.md` (S2), Sections 2-7
→ Data: `ablation_study_results.json`, `multi_year_rolling_validation.json`

**Concern: "Limited baseline comparison"**
→ Read: `CLASSICAL_BASELINES_RESULTS.md` (S3)
→ Data: `classical_baselines_extended.json` (80 new backtests)

**Concern: "Limited generalization"**
→ Read: `CAUSALITY_ANALYSIS.md` (S2) Section 5, `statistical_report_full.md`
→ Data: `multi_year_rolling_validation.json`, `statistical_robustness_results.json`

**Concern: "Lack of theory"**
→ Read: `CAUSALITY_ANALYSIS.md` (S2) Sections 8-9
→ Formal definitions, theorems, theoretical connections

**Concern: "Not reproducible"**
→ Read: `EOH_USAGE_GUIDE.md` (S5)
→ Code: All scripts in `code/` directory
→ Data: All JSON files in `data/` directory

---

## XIII. Version Control

### Current Version

- **Version**: v1.0
- **Date**: 2025-11-28
- **Status**: Ready for submission

### Version History

**v1.0 (2025-11-28)**:
- Initial complete package
- 625+ backtests
- 5-layer causal evidence
- 7 strategy comparison
- Complete theoretical framework

**Future Versions (if revision needed)**:
- v1.1: Minor revisions (typos, clarifications)
- v2.0: Major revisions (new experiments, restructured)

---

## XIV. Final Notes

### Package Integrity

All files have been verified:
- [x] All JSON files valid (parsed successfully)
- [x] All Python scripts syntax-checked
- [x] All Markdown files encoded in UTF-8
- [x] All PNG files render correctly
- [x] No missing files referenced in documents
- [x] No absolute paths in code (all relative)

### Contact Information

For questions about specific files or materials:
- See individual file headers for descriptions
- See `README_SUPPLEMENTARY_MATERIALS.md` for navigation
- See `EOH_USAGE_GUIDE.md` for reproducibility

### Acknowledgments

This complete file manifest was generated to facilitate:
- Quick navigation for reviewers
- Reproducibility verification
- Submission preparation
- Future reference

---

**END OF FILE MANIFEST**

**Package Status**: ✅ READY FOR SUBMISSION

**Total Files Documented**: 57

**Last Updated**: 2025-11-28
