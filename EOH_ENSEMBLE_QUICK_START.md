# EOH Ensemble Enhancement: Quick Start Guide

**Date**: 2025-11-28

**Purpose**: Showcase EOH's autonomous strategy generation capability through ensemble methods

**Status**: ✅ Implementation plan and scripts ready for execution

---

## I. What Has Been Prepared

### A. Strategic Planning

**Document**: `EOH_ENSEMBLE_IMPLEMENTATION_PLAN.md` (~700 lines)
- Complete experimental design
- Timeline (2 weeks)
- Expected outcomes (+276 backtests, 38% growth)
- Integration with existing materials

### B. Executable Scripts

#### 1. Strategy Generation Script
**File**: `code/generate_ensemble_pool.sh`
- **Purpose**: Generate 20 diverse strategies with EOH
- **Runtime**: ~10-12 hours
- **Configuration**: Temperature=0.2, Seeds 1-20
- **Output**: 20 strategy directories + performance logs

#### 2. Quality Filter Script
**File**: `code/filter_ensemble_strategies.py`
- **Purpose**: Select top 10 strategies by Sharpe ratio
- **Criteria**: Return>0%, Sharpe>0.5, DD<30%, Trades≥10
- **Output**: `top_strategies.json` + summary report

#### 3. Ensemble Backtest Framework
**File**: Implementation plan includes detailed design
- **Methods**: Simple average, Weighted Sharpe, Portfolio MV
- **Assets**: 12 total (2 US + 10 A-shares)
- **Output**: 36 ensemble backtests

---

## II. Implementation Roadmap

### Week 1: Strategy Pool Generation (Days 1-5)

#### Day 1-2: Generate Strategy Pool
```bash
# Upload script to server
scp -P 18077 code/generate_ensemble_pool.sh root@connect.westd.seetacloud.com:/root/autodl-tmp/

# SSH to server
ssh -p 18077 root@connect.westd.seetacloud.com

# Make executable
chmod +x /root/autodl-tmp/generate_ensemble_pool.sh

# Run generation (expect ~10-12 hours)
cd /root/autodl-tmp
nohup bash generate_ensemble_pool.sh > ensemble_generation.log 2>&1 &

# Monitor progress
tail -f ensemble_generation.log
```

**Expected Output**:
- 20 strategy directories: `ensemble_pool/strategy_01/` to `strategy_20/`
- Each contains: `evolved_strategy.py`, `backtest_results.json`
- Generation summary: `ensemble_pool/generation_summary.txt`

#### Day 3: Filter Top Strategies
```bash
# Upload filter script
scp -P 18077 code/filter_ensemble_strategies.py root@connect.westd.seetacloud.com:/root/autodl-tmp/

# Run filter
cd /root/autodl-tmp
/root/miniconda3/bin/python filter_ensemble_strategies.py

# Check results
cat /root/autodl-tmp/outputs/ensemble_pool/filter_summary.txt
cat /root/autodl-tmp/outputs/ensemble_pool/top_strategies.json
```

**Expected Output**:
- `top_strategies.json`: List of 10 best strategy IDs
- `filter_summary.txt`: Performance statistics and rankings

#### Day 4-5: Individual Strategy Testing
```bash
# Test each top strategy on 10 A-shares
# This requires implementing a batch testing script
# Placeholder for future implementation
```

### Week 2: Ensemble Testing (Days 6-10)

#### Day 6-7: Implement Ensemble Backtester
- Complete the `run_ensemble_backtest.py` implementation
- Test 3 ensemble methods
- Run on 12 assets (36 backtests total)

#### Day 8-9: Analysis and Report
- Generate ensemble performance comparison
- Create visualization charts
- Draft S6: `LLM_ENSEMBLE_ANALYSIS.md`

#### Day 10: Integration
- Update all master documents
- Package new materials
- Final quality check

---

## III. Quick Execution Commands

### Step 1: Upload Scripts to Server
```bash
# From your local machine (Desktop directory)
cd "C:\Users\Xing\Desktop\paper_supplementary_experiments_2025-11-27\code"

# Upload generation script
scp -P 18077 generate_ensemble_pool.sh root@connect.westd.seetacloud.com:/root/autodl-tmp/

# Upload filter script
scp -P 18077 filter_ensemble_strategies.py root@connect.westd.seetacloud.com:/root/autodl-tmp/
```

### Step 2: Start Strategy Generation
```bash
# SSH to server
ssh -p 18077 root@connect.westd.seetacloud.com

# Navigate and prepare
cd /root/autodl-tmp
chmod +x generate_ensemble_pool.sh

# Start generation (background process)
nohup bash generate_ensemble_pool.sh > ensemble_generation.log 2>&1 &

# Get process ID for monitoring
ps aux | grep generate_ensemble_pool

# Monitor log in real-time
tail -f ensemble_generation.log

# Or check periodically
tail -100 ensemble_generation.log
```

### Step 3: Check Progress
```bash
# Count generated strategies
ls -1d /root/autodl-tmp/outputs/ensemble_pool/strategy_* | wc -l

# Check latest generation log
ls -lt /root/autodl-tmp/outputs/ensemble_pool/logs/*.log | head -1

# View generation summary
cat /root/autodl-tmp/outputs/ensemble_pool/generation_summary.txt
```

### Step 4: Filter Top Strategies
```bash
# After generation completes (check log shows "Complete")
cd /root/autodl-tmp
/root/miniconda3/bin/python filter_ensemble_strategies.py

# View results
cat /root/autodl-tmp/outputs/ensemble_pool/filter_summary.txt
cat /root/autodl-tmp/outputs/ensemble_pool/top_strategies.json
```

---

## IV. Expected Results

### A. Strategy Pool Statistics (Predictions)

**Generation Success Rate**: ~80-90% (16-18 strategies)
- Some may fail due to LLM generation errors
- Quality filter will select top 10

**Performance Distribution**:
- Mean return: +2% to +5%
- Mean Sharpe: 0.6 to 1.2
- Success rate (return > 0): 60-80%

### B. Ensemble Performance (Targets)

**Goal**: Demonstrate ensemble robustness

**Expected Improvements**:
- Ensemble vs single-best: +5-10pp return
- Ensemble success rate: 75-85% (higher than average individual)
- Variance reduction: 30-50% lower than individual strategies

### C. Paper Contribution Enhancement

**Current EOH Usage**: ~20% of 625 backtests = ~125 backtests
**After Ensemble**: ~40% of 901 backtests = ~360 backtests

**Narrative Shift**:
- **Before**: "We use adaptive parameters to fix LLM strategies"
- **After**: "EOH autonomously generates diverse profitable strategies; adaptive parameters enable cross-market transfer"

**Reviewer Impact**:
- Addresses "EOH underutilization" concern
- Shows systematic generation, not cherry-picking
- Demonstrates ensemble robustness (machine learning contribution)

---

## V. Troubleshooting

### Issue: Strategy Generation Fails

**Symptoms**: Script exits with error, fewer than 20 strategies

**Possible Causes**:
1. GPU out of memory
2. Model path incorrect
3. Python environment issue

**Solutions**:
```bash
# Check GPU memory
nvidia-smi

# Verify model exists
ls -lh /root/autodl-tmp/models/Meta-Llama-3.1-8B-Instruct/

# Test EOH manually on one strategy
cd /root/autodl-fs/POM
/root/miniconda3/envs/eoh1/bin/python eoh_gpu_loop_fixed.py \
  --model-dir /root/autodl-tmp/models/Meta-Llama-3.1-8B-Instruct \
  --symbol SPY \
  --population 1 \
  --temperature 0.2 \
  --seed 42 \
  --outdir /root/autodl-tmp/test_strategy
```

### Issue: Quality Filter Returns No Strategies

**Symptoms**: `filter_ensemble_strategies.py` shows 0 strategies passing filter

**Possible Causes**:
1. All strategies performed poorly (unlikely)
2. Filter criteria too strict
3. Backtest results missing

**Solutions**:
```bash
# Relax filter criteria (edit filter_ensemble_strategies.py)
# Change line: min_sharpe: float = 0.5 → 0.3

# Or check if backtest results exist
ls /root/autodl-tmp/outputs/ensemble_pool/strategy_*/backtest_results.json
```

### Issue: Script Runs Too Slow

**Symptoms**: Generation taking > 1 hour per strategy

**Possible Causes**:
1. GPU not utilized
2. Large population size
3. Many generations

**Solutions**:
```bash
# Verify GPU usage during generation
nvidia-smi -l 1  # Monitor every 1 second

# Reduce if needed (edit generate_ensemble_pool.sh):
# NUM_GENERATIONS=1 → Already optimal
# POPULATION=1 → Already optimal
```

---

## VI. Monitoring and Logs

### Generation Logs

**Main log**: `/root/autodl-tmp/ensemble_generation.log`
- Overall progress
- Success/failure summary

**Individual strategy logs**: `/root/autodl-tmp/outputs/ensemble_pool/logs/strategy_XX.log`
- Detailed LLM generation process
- Backtest results
- Error messages (if any)

### Key Log Patterns

**Successful generation**:
```
✓ Strategy 01 generated successfully
  → Strategy file: OK
  → Backtest results: OK
  → Training Return: 3.45%
  → Training Sharpe: 0.78
```

**Failed generation**:
```
✗ Strategy 05 generation failed (exit code: 1)
  See log: /root/autodl-tmp/outputs/ensemble_pool/logs/strategy_05.log
```

### Checking Completion

**Generation complete when**:
```bash
# Check if generation finished
grep "Strategy Pool Generation Complete" /root/autodl-tmp/ensemble_generation.log

# Should see summary:
# Total Strategies Attempted: 20
# Successful: 18
# Failed: 2
# Success Rate: 90%
```

---

## VII. Integration Checklist

After completing all experiments:

### A. New Files to Add to Package

- [ ] `EOH_ENSEMBLE_IMPLEMENTATION_PLAN.md` (this plan)
- [ ] `code/generate_ensemble_pool.sh` (generation script)
- [ ] `code/filter_ensemble_strategies.py` (filtering script)
- [ ] `code/run_ensemble_backtest.py` (to be completed)
- [ ] `reports/LLM_ENSEMBLE_ANALYSIS.md` (S6, to be written)
- [ ] `data/ensemble_backtest_results.json` (results)
- [ ] `charts/ensemble_comparison.png` (visualization)

### B. Documents to Update

- [ ] `README_SUPPLEMENTARY_MATERIALS.md`: Add S6 section
- [ ] `COMPLETE_MATERIALS_SUMMARY.md`: Update statistics (625→901 backtests)
- [ ] `FILE_MANIFEST.md`: Add new files
- [ ] `PAPER_CITATION_TEMPLATES.md`: Add S6 BibTeX and citation examples

### C. Paper Main Text Updates

- [ ] Methods section: Add "LLM Strategy Ensemble" subsection
- [ ] Results section: Add ensemble performance comparison
- [ ] Discussion: Emphasize autonomous generation capability
- [ ] Abstract: Update experimental scale (625+→900+)

---

## VIII. Success Criteria Summary

### Minimum Success (Acceptable)

✅ 15+ strategies generated successfully (75% success rate)
✅ 8+ strategies pass quality filter
✅ Ensemble methods complete without errors
✅ S6 report documents results systematically

### Desired Success (Good)

✅ 18+ strategies generated (90% success rate)
✅ 10+ strategies pass quality filter
✅ Ensemble outperforms single-best by 5+pp
✅ Clear diversity demonstrated (correlation < 0.7)

### Outstanding Success (Excellent)

✅ 20 strategies generated (100% success rate)
✅ 12+ strategies pass quality filter
✅ Ensemble outperforms single-best by 10+pp
✅ Success rate 80%+ across all assets
✅ Clear demonstration of EOH's autonomous capability

---

## IX. Timeline Summary

**Total Time**: 2 weeks (10 working days)

| Phase | Days | Activities | Deliverables |
|-------|------|------------|--------------|
| **Generation** | 1-2 | Run ensemble pool generation | 20 strategies |
| **Filtering** | 3 | Select top strategies | top_strategies.json |
| **Testing** | 4-5 | Individual strategy backtests | 200 results |
| **Ensemble** | 6-7 | Ensemble method testing | 36 results |
| **Analysis** | 8-9 | Report writing + visualization | S6 report |
| **Integration** | 10 | Update documents + packaging | Complete package |

---

## X. Next Immediate Action

**Ready to Start?**

**Step 1**: Upload scripts to server
```bash
cd "C:\Users\Xing\Desktop\paper_supplementary_experiments_2025-11-27\code"
scp -P 18077 generate_ensemble_pool.sh filter_ensemble_strategies.py root@connect.westd.seetacloud.com:/root/autodl-tmp/
```

**Step 2**: Start generation
```bash
ssh -p 18077 root@connect.westd.seetacloud.com
cd /root/autodl-tmp
chmod +x generate_ensemble_pool.sh
nohup bash generate_ensemble_pool.sh > ensemble_generation.log 2>&1 &
```

**Step 3**: Monitor progress
```bash
# Check every few hours
tail -100 /root/autodl-tmp/ensemble_generation.log
```

**Expected Completion**: Tomorrow (if starting today)

---

## XI. Contact and Support

**Questions?**

- Review: `EOH_ENSEMBLE_IMPLEMENTATION_PLAN.md` for detailed design
- Check: Generation logs for troubleshooting
- Modify: Scripts are documented and modifiable

**Need Help?**

Common issues and solutions are documented in Section V (Troubleshooting).

---

**Guide Version**: v1.0

**Status**: ✅ **READY FOR EXECUTION**

**Created**: 2025-11-28

---

**END OF QUICK START GUIDE**
