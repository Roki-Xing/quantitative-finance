#!/bin/bash

###############################################################################
# EOH Strategy Ensemble Pool Generator (Organized Version - With Adaptive Prompts)
#
# Purpose: Generate 20 diverse trading strategies using EOH
#          All outputs organized in clear folder structure
#
# Output Structure:
#   eoh_ensemble_experiment/
#     ├── 00_scripts/
#     ├── 01_strategy_pool/
#     ├── 02_generation_logs/
#     └── README_EXPERIMENT.md
###############################################################################

# Base directory
BASE_DIR="/root/autodl-tmp/eoh_ensemble_experiment"

# Configuration
MODEL_DIR="/root/autodl-tmp/models/Meta-Llama-3.1-8B-Instruct"
EOH_SCRIPT="/root/autodl-tmp/eoh/eoh_gpu_loop_fixed.py"

# Output directories
STRATEGY_POOL_DIR="$BASE_DIR/01_strategy_pool"
LOG_DIR="$BASE_DIR/02_generation_logs"
SCRIPTS_DIR="$BASE_DIR/00_scripts"

# Training configuration
SYMBOL="SPY"
TRAIN_START="2020-01-01"
TRAIN_END="2023-12-31"
TEST_START="2024-01-01"
TEST_END="2024-12-31"

# EOH parameters
TEMPERATURE=0.2
POPULATION=10
GENERATIONS=1

# Prompt configuration
PROMPT_STYLE="adaptive"
PROMPT_DIR="/root/autodl-tmp/eoh/prompts_day51_adaptive"

###############################################################################
# Setup: Create folder structure
###############################################################################

echo "=========================================="
echo "EOH Ensemble Experiment Setup"
echo "=========================================="
echo "Creating organized folder structure..."
echo ""

# Create all directories
mkdir -p "$BASE_DIR"
mkdir -p "$SCRIPTS_DIR"
mkdir -p "$STRATEGY_POOL_DIR"
mkdir -p "$LOG_DIR"

# Copy this script to scripts directory
cp "$0" "$SCRIPTS_DIR/" 2>/dev/null

echo "✓ Folder structure created:"
echo "  - Base: $BASE_DIR"
echo "  - Scripts: $SCRIPTS_DIR"
echo "  - Strategy Pool: $STRATEGY_POOL_DIR"
echo "  - Logs: $LOG_DIR"
echo ""

###############################################################################
# Create README
###############################################################################

cat > "$BASE_DIR/README_EXPERIMENT.md" << 'EOF'
# EOH Ensemble Experiment

**实验开始时间**: $(date)

**实验目标**: 生成20个多样化的LLM交易策略,展示EOH的自主学习能力

## 文件夹结构

```
eoh_ensemble_experiment/
├── 00_scripts/              # 执行脚本
├── 01_strategy_pool/        # 生成的20个策略
├── 02_generation_logs/      # 生成日志
├── 03_filtered_strategies/  # 筛选后的Top策略（待生成）
└── README_EXPERIMENT.md     # 本文件
```

## 实验进度

- [x] Step 1: 创建文件夹结构
- [ ] Step 2: 生成20个策略
- [ ] Step 3: 质量筛选（Top 10）
- [ ] Step 4: 单策略回测
- [ ] Step 5: 集成方法回测
- [ ] Step 6: 分析和报告

## 快速查看

### 查看生成进度
```bash
tail -f 02_generation_logs/ensemble_generation.log
```

### 查看生成摘要
```bash
cat 02_generation_logs/generation_summary.txt
```

### 查看策略列表
```bash
ls -1 01_strategy_pool/
```

## 关键文件

- `02_generation_logs/ensemble_generation.log`: 总体生成日志
- `02_generation_logs/generation_summary.txt`: 生成结果汇总
- `01_strategy_pool/strategy_XX/gen*_best.py`: 单个策略代码

---

**实验版本**: v1.0
**状态**: 进行中...
EOF

echo "✓ README created: $BASE_DIR/README_EXPERIMENT.md"
echo ""

###############################################################################
# Strategy Generation
###############################################################################

echo "=========================================="
echo "Strategy Generation Started"
echo "=========================================="
echo "Start Time: $(date)"
echo "Model: Meta-Llama-3.1-8B-Instruct"
echo "Temperature: $TEMPERATURE"
echo "Population: $POPULATION"
echo "Prompt Style: $PROMPT_STYLE"
echo "Training Period: $TRAIN_START to $TRAIN_END"
echo "Testing Period: $TEST_START to $TEST_END"
echo "Total Strategies: 20"
echo "=========================================="
echo ""

# Main log file
MAIN_LOG="$LOG_DIR/ensemble_generation.log"
echo "EOH Ensemble Generation Log" > "$MAIN_LOG"
echo "Start Time: $(date)" >> "$MAIN_LOG"
echo "==========================================" >> "$MAIN_LOG"
echo "" >> "$MAIN_LOG"

# Generate 20 strategies
SUCCESS_COUNT=0
FAIL_COUNT=0

for SEED in {1..20}; do
    STRATEGY_NUM=$(printf "%02d" $SEED)

    echo "=========================================="
    echo "Generating Strategy $STRATEGY_NUM / 20"
    echo "=========================================="
    echo "Seed: $SEED"
    echo "Start Time: $(date)"

    # Output directories for this strategy
    STRATEGY_DIR="$STRATEGY_POOL_DIR/strategy_$STRATEGY_NUM"
    LOG_FILE="$LOG_DIR/strategy_$STRATEGY_NUM.log"

    mkdir -p "$STRATEGY_DIR"

    # Log to main log
    echo "=== Strategy $STRATEGY_NUM ===" >> "$MAIN_LOG"
    echo "Seed: $SEED" >> "$MAIN_LOG"
    echo "Start: $(date)" >> "$MAIN_LOG"

    # Run EOH
    /root/miniconda3/envs/eoh1/bin/python $EOH_SCRIPT \
        --model-dir $MODEL_DIR \
        --symbol $SYMBOL \
        --population $POPULATION \
        --temperature $TEMPERATURE \
        --generations $GENERATIONS \
        --train_start $TRAIN_START \
        --train_end $TRAIN_END \
        --test_start $TEST_START \
        --test_end $TEST_END \
        --prompt-style $PROMPT_STYLE \
        --prompt-dir $PROMPT_DIR \
        --seed $SEED \
        --outdir "$STRATEGY_DIR" \
        > "$LOG_FILE" 2>&1

    EXIT_CODE=$?

    if [ $EXIT_CODE -eq 0 ] && ls "$STRATEGY_DIR"/gen*_best.py 1> /dev/null 2>&1; then
        echo "✓ Strategy $STRATEGY_NUM generated successfully"
        echo "End: $(date)" >> "$MAIN_LOG"
        echo "Status: SUCCESS" >> "$MAIN_LOG"
        SUCCESS_COUNT=$((SUCCESS_COUNT + 1))

        # Find best strategy file
        BEST_FILE=$(ls "$STRATEGY_DIR"/gen*_best.py | tail -1)
        echo "  → Strategy file: $(basename $BEST_FILE)"
        echo "  File: $(basename $BEST_FILE)" >> "$MAIN_LOG"

    else
        echo "✗ Strategy $STRATEGY_NUM generation failed"
        echo "  See log: $LOG_FILE"
        echo "End: $(date)" >> "$MAIN_LOG"
        echo "Status: FAILED" >> "$MAIN_LOG"
        FAIL_COUNT=$((FAIL_COUNT + 1))
    fi

    echo "" >> "$MAIN_LOG"
    echo "End Time: $(date)"
    echo ""

    # Small delay
    sleep 5
done

###############################################################################
# Generate Summary
###############################################################################

echo "=========================================="
echo "Strategy Pool Generation Complete"
echo "=========================================="
echo "End Time: $(date)"
echo "Total Strategies Attempted: 20"
echo "Successful: $SUCCESS_COUNT"
echo "Failed: $FAIL_COUNT"
echo "Success Rate: $((SUCCESS_COUNT * 100 / 20))%"
echo "Output Directory: $STRATEGY_POOL_DIR"
echo "=========================================="

# Write summary file
SUMMARY_FILE="$LOG_DIR/generation_summary.txt"

cat > "$SUMMARY_FILE" << EOF
EOH Strategy Pool Generation Summary
=====================================

Generation Date: $(date)
Model: Meta-Llama-3.1-8B-Instruct
Temperature: $TEMPERATURE
Population: $POPULATION
Prompt Style: $PROMPT_STYLE
Training Period: $TRAIN_START to $TRAIN_END
Testing Period: $TEST_START to $TEST_END

Results
-------
Total Strategies: 20
Successful: $SUCCESS_COUNT
Failed: $FAIL_COUNT
Success Rate: $((SUCCESS_COUNT * 100 / 20))%

Strategy List
-------------
EOF

# Append individual strategy results
for SEED in {1..20}; do
    STRATEGY_NUM=$(printf "%02d" $SEED)
    STRATEGY_DIR="$STRATEGY_POOL_DIR/strategy_$STRATEGY_NUM"

    if ls "$STRATEGY_DIR"/gen*_best.py 1> /dev/null 2>&1; then
        BEST_FILE=$(ls "$STRATEGY_DIR"/gen*_best.py | tail -1)
        echo "Strategy $STRATEGY_NUM: SUCCESS - $(basename $BEST_FILE)" >> "$SUMMARY_FILE"
    else
        echo "Strategy $STRATEGY_NUM: FAILED" >> "$SUMMARY_FILE"
    fi
done

echo "" >> "$SUMMARY_FILE"
echo "=====================================" >> "$SUMMARY_FILE"
echo "" >> "$SUMMARY_FILE"
echo "File Locations:" >> "$SUMMARY_FILE"
echo "  Strategy Pool: $STRATEGY_POOL_DIR" >> "$SUMMARY_FILE"
echo "  Logs: $LOG_DIR" >> "$SUMMARY_FILE"
echo "  Main Log: $LOG_DIR/ensemble_generation.log" >> "$SUMMARY_FILE"

echo ""
echo "✓ Summary saved to: $SUMMARY_FILE"
echo ""

# Update README with completion
sed -i 's/- \[ \] Step 2: 生成20个策略/- [x] Step 2: 生成20个策略/' "$BASE_DIR/README_EXPERIMENT.md"

# Append to README
cat >> "$BASE_DIR/README_EXPERIMENT.md" << EOF

## 生成结果

**完成时间**: $(date)
**成功率**: $((SUCCESS_COUNT * 100 / 20))%
**成功**: $SUCCESS_COUNT / 20
**失败**: $FAIL_COUNT / 20

详细结果见: \`02_generation_logs/generation_summary.txt\`
EOF

###############################################################################
# Next steps reminder
###############################################################################

echo "=========================================="
echo "Next Steps"
echo "=========================================="
echo "1. Review generation logs:"
echo "   cat $LOG_DIR/generation_summary.txt"
echo ""
echo "2. Run quality filter:"
echo "   cd $BASE_DIR"
echo "   /root/miniconda3/bin/python ../filter_ensemble_strategies_organized.py"
echo ""
echo "3. Check experiment README:"
echo "   cat $BASE_DIR/README_EXPERIMENT.md"
echo "=========================================="

exit 0
