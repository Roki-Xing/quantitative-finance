#!/bin/bash

###############################################################################
# EOH Strategy Ensemble Pool Generator
#
# Purpose: Generate 20 diverse trading strategies using EOH with different
#          random seeds to demonstrate autonomous learning capability
#
# Usage: bash generate_ensemble_pool.sh
#
# Expected Runtime: ~10-12 hours (30-40 min per strategy)
# Output: 20 strategy directories in ensemble_pool/
###############################################################################

# Configuration
MODEL_DIR="/root/autodl-tmp/models/Meta-Llama-3.1-8B-Instruct"
OUTPUT_BASE="/root/autodl-tmp/outputs/ensemble_pool"
EOH_SCRIPT="/root/autodl-fs/POM/eoh_gpu_loop_fixed.py"
LOG_DIR="$OUTPUT_BASE/logs"

# Create output directories
mkdir -p $OUTPUT_BASE
mkdir -p $LOG_DIR

# Training data configuration
SYMBOL="SPY"
TRAIN_START="2020-01-01"
TRAIN_END="2023-12-31"

# EOH parameters (validated optimal from Day 12)
TEMPERATURE=0.2
POPULATION=1
NUM_GENERATIONS=1

# Prompt (HPDT-compliant: gentle encouragement)
TASK="Generate a robust quantitative trading strategy for stock market trading.
Your strategy should:
1. Use technical indicators (moving averages, RSI, MACD, Bollinger Bands, etc.)
2. Have clear entry and exit rules
3. Include risk management (stop-loss, position sizing)
4. Be adaptable to different market conditions

Focus on creating a balanced strategy that can work across different stocks and time periods.
Think carefully about how to avoid overfitting to specific market conditions."

# Log experiment start
echo "=========================================="
echo "EOH Ensemble Pool Generation"
echo "=========================================="
echo "Start Time: $(date)"
echo "Model: Meta-Llama-3.1-8B-Instruct"
echo "Temperature: $TEMPERATURE"
echo "Training Period: $TRAIN_START to $TRAIN_END"
echo "Total Strategies: 20"
echo "Output Directory: $OUTPUT_BASE"
echo "=========================================="
echo ""

# Generate 20 strategies with different seeds
SUCCESS_COUNT=0
FAIL_COUNT=0

for SEED in {1..20}; do
    echo "=========================================="
    echo "Generating Strategy $SEED / 20"
    echo "=========================================="
    echo "Seed: $SEED"
    echo "Start Time: $(date)"

    STRATEGY_DIR="$OUTPUT_BASE/strategy_$(printf "%02d" $SEED)"
    LOG_FILE="$LOG_DIR/strategy_$(printf "%02d" $SEED).log"

    # Run EOH strategy generation
    /root/miniconda3/envs/eoh1/bin/python $EOH_SCRIPT \
        --model-dir $MODEL_DIR \
        --symbol $SYMBOL \
        --population $POPULATION \
        --temperature $TEMPERATURE \
        --num-generations $NUM_GENERATIONS \
        --train-start $TRAIN_START \
        --train-end $TRAIN_END \
        --seed $SEED \
        --outdir $STRATEGY_DIR \
        --task "$TASK" \
        > $LOG_FILE 2>&1

    EXIT_CODE=$?

    if [ $EXIT_CODE -eq 0 ]; then
        echo "✓ Strategy $SEED generated successfully"
        SUCCESS_COUNT=$((SUCCESS_COUNT + 1))

        # Verify output files exist
        if [ -f "$STRATEGY_DIR/evolved_strategy.py" ]; then
            echo "  → Strategy file: OK"
        else
            echo "  ⚠ Warning: Strategy file not found"
        fi

        if [ -f "$STRATEGY_DIR/backtest_results.json" ]; then
            echo "  → Backtest results: OK"

            # Extract key metrics
            TRAIN_RETURN=$(grep -oP '"returns_pct":\s*\K[0-9.-]+' "$STRATEGY_DIR/backtest_results.json" | head -1)
            TRAIN_SHARPE=$(grep -oP '"sharpe_ratio":\s*\K[0-9.-]+' "$STRATEGY_DIR/backtest_results.json" | head -1)

            echo "  → Training Return: $TRAIN_RETURN%"
            echo "  → Training Sharpe: $TRAIN_SHARPE"
        else
            echo "  ⚠ Warning: Backtest results not found"
        fi
    else
        echo "✗ Strategy $SEED generation failed (exit code: $EXIT_CODE)"
        FAIL_COUNT=$((FAIL_COUNT + 1))
        echo "  See log: $LOG_FILE"
    fi

    echo "End Time: $(date)"
    echo ""

    # Small delay to avoid GPU memory issues
    sleep 5
done

# Final summary
echo "=========================================="
echo "Strategy Pool Generation Complete"
echo "=========================================="
echo "End Time: $(date)"
echo "Total Strategies Attempted: 20"
echo "Successful: $SUCCESS_COUNT"
echo "Failed: $FAIL_COUNT"
echo "Success Rate: $((SUCCESS_COUNT * 100 / 20))%"
echo "Output Directory: $OUTPUT_BASE"
echo "=========================================="

# Generate quick summary file
SUMMARY_FILE="$OUTPUT_BASE/generation_summary.txt"
echo "EOH Strategy Ensemble Pool Generation Summary" > $SUMMARY_FILE
echo "===============================================" >> $SUMMARY_FILE
echo "" >> $SUMMARY_FILE
echo "Generation Date: $(date)" >> $SUMMARY_FILE
echo "Model: Meta-Llama-3.1-8B-Instruct" >> $SUMMARY_FILE
echo "Temperature: $TEMPERATURE" >> $SUMMARY_FILE
echo "Training Period: $TRAIN_START to $TRAIN_END" >> $SUMMARY_FILE
echo "" >> $SUMMARY_FILE
echo "Results:" >> $SUMMARY_FILE
echo "--------" >> $SUMMARY_FILE
echo "Total Strategies: 20" >> $SUMMARY_FILE
echo "Successful: $SUCCESS_COUNT" >> $SUMMARY_FILE
echo "Failed: $FAIL_COUNT" >> $SUMMARY_FILE
echo "Success Rate: $((SUCCESS_COUNT * 100 / 20))%" >> $SUMMARY_FILE
echo "" >> $SUMMARY_FILE
echo "Strategy Performance Summary:" >> $SUMMARY_FILE
echo "----------------------------" >> $SUMMARY_FILE

for SEED in {1..20}; do
    STRATEGY_DIR="$OUTPUT_BASE/strategy_$(printf "%02d" $SEED)"
    if [ -f "$STRATEGY_DIR/backtest_results.json" ]; then
        TRAIN_RETURN=$(grep -oP '"returns_pct":\s*\K[0-9.-]+' "$STRATEGY_DIR/backtest_results.json" | head -1)
        TRAIN_SHARPE=$(grep -oP '"sharpe_ratio":\s*\K[0-9.-]+' "$STRATEGY_DIR/backtest_results.json" | head -1)
        printf "Strategy %02d: Return=%s%%, Sharpe=%s\n" $SEED "$TRAIN_RETURN" "$TRAIN_SHARPE" >> $SUMMARY_FILE
    else
        printf "Strategy %02d: FAILED\n" $SEED >> $SUMMARY_FILE
    fi
done

echo "" >> $SUMMARY_FILE
echo "===============================================" >> $SUMMARY_FILE

echo ""
echo "Summary saved to: $SUMMARY_FILE"
echo ""

# Next steps reminder
echo "Next Steps:"
echo "1. Review generation logs in: $LOG_DIR"
echo "2. Run quality filter: python filter_ensemble_strategies.py"
echo "3. Analyze strategy diversity"
echo "4. Proceed with ensemble backtesting"
echo ""

exit 0
