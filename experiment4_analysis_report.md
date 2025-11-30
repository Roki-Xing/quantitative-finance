# Experiment 4 Analysis Report: Trading Strategy Generation

**Date:** 2025-11-24
**Experiment:** LLM Trading Strategy Generation (Extended Data)
**Model:** Meta-Llama-3.1-8B-Instruct (Local)
**Dataset:** 18 stocks, 15 years (2010-2025)

---

## Executive Summary

Experiment 4 compared **baseline** vs **multilayer** prompts for generating trading strategies. Paradoxically, the simpler baseline prompt produced better results:

| Metric | Baseline | Multilayer |
|--------|----------|------------|
| Syntax Valid | 29/30 (96.7%) | 28/30 (93.3%) |
| Runnable | 7/30 (23.3%) | 4/30 (13.3%) |
| Avg Return | -0.18% | -26,995% |
| Avg Code Length | 1,774 chars | 3,208 chars |

**Key Finding:** More detailed prompts led to more complex code that was harder for the LLM to generate correctly.

---

## Error Pattern Analysis

### Phase 1: AST Validation (60 strategies analyzed)

Using the custom AST validator, we identified these systematic error patterns:

#### 🔴 CRITICAL Issues (Baseline: ~30, Multilayer: ~21)

**1. Incomplete Code Blocks (Most Common)**
- **Problem:** elif/else statements with no body
- **Example:**
  ```python
  if condition:
      do_something()
  elif other_condition:  # ← Missing code block!
  # Next statement here causes SyntaxError
  ```
- **Root Cause:** LLM generated control flow structure but failed to complete implementation
- **Impact:** Prevents code compilation

**2. Indentation Mismatches**
- **Problem:** elif/else not aligned with parent if
- **Example:**
  ```python
  if self.crossover > 0:
      self.buy()
  elif self.crossover < 0:  # ← Wrong indent
      self.sell()
  ```
- **Impact:** Python syntax error

#### 🟡 MEDIUM Issues (Baseline: ~90, Multilayer: ~45)

**3. Missing Import Statements**
- Missing: `import backtrader.indicators as btind`
- Variables referenced: `btind.SMA`, `btind.RSI`, `btind.MACD`
- Impact: NameError at runtime

**4. Missing self.order Initialization**
- Missing: `self.order = None` in `__init__`
- Impact: Causes AttributeError when checking pending orders

#### 🟢 LOW Issues (All: ~30)

**5. Missing Pending Order Checks**
- Missing: `if self.order: return` at start of `next()`
- Impact: Potential duplicate order errors

---

## Phase 2: Auto-Fix Application

Created `day48_auto_fix_strategies.py` to automatically repair common errors:

### Baseline Strategies (30 files)

```
✅ Success:      2/30 (6.7%)
⚠️  Partial:     26/30 (86.7%)
⏭️  No Changes:   2/30 (6.7%)

Total Fixes Applied: 37
```

**Fix Distribution:**
- Indentation corrections: 35
- Added `self.order = None`: 2

**Remaining Issues:**
- 26 strategies still have incomplete code blocks after elif/else
- These require manual completion or advanced LLM-based code completion

### Multilayer Strategies (30 files)

```
✅ Success:      0/30 (0%)
⚠️  Partial:     21/30 (70%)
⏭️  No Changes:   9/30 (30%)

Total Fixes Applied: 24
```

**Fix Distribution:**
- All 24 fixes were indentation corrections
- More strategies had no structural issues (9 vs 2 in baseline)
- But **none** were fully fixed to runnable state

---

## Root Cause Analysis

### Why Did Baseline Outperform Multilayer?

1. **Complexity Amplification**
   - Multilayer prompt: "implement risk management, order management, exception handling..."
   - LLM attempted all features simultaneously → incomplete implementations
   - Baseline: Simpler requirements → more focused, complete code

2. **Token Budget Exhaustion**
   - Multilayer average: 3,208 chars (longer context)
   - More likely to hit generation limits mid-function
   - Incomplete elif/else blocks suggest premature truncation

3. **Hallucination in Advanced Features**
   - Multilayer prompted for sophisticated features
   - LLM hallucinated non-existent backtrader APIs:
     - `cerebro._exactbars`
     - `broker.set_stoploss()`
     - `btind.HighestHigh`

---

## Specific Error Examples

### From experiment4_results.json:

**Baseline #1 (ID: 1):**
```json
{
  "strategy_type": "Trend Following Strategy using Moving Averages",
  "backtest": {
    "success": false,
    "error": "'Cerebro' object has no attribute 'addfeed'"
  }
}
```
→ LLM used incorrect API (should be `adddata`)

**Baseline #2 (ID: 2):**
```json
{
  "strategy_type": "Mean Reversion Strategy using Bollinger Bands",
  "backtest": {
    "success": false,
    "error": "name 'datetime' is not defined"
  }
}
```
→ Missing import statement

**Multilayer #9 (ID: 9):**
```json
{
  "strategy_type": "Momentum Strategy using RSI and MACD",
  "backtest": {
    "success": true,
    "return_pct": -107996.77,
    "sharpe": -0.10,
    "max_drawdown": 5555.51,
    "trades": 2
  }
}
```
→ Runnable but catastrophic losses (-108,000%)!

---

## Actionable Recommendations

### Short-term (Fix Current Strategies)

1. **Manual Code Completion** (High-ROI)
   - Focus on 2 baseline successes + 9 multilayer no-changes
   - Manually complete the incomplete elif/else blocks
   - Estimated time: 2-3 hours
   - Expected gain: +5-10 runnable strategies

2. **LLM-Assisted Completion** (Medium-ROI)
   - Use LLM to complete partial strategies one-by-one
   - Provide partial code + specific completion instructions
   - Template: "Complete this elif block with mean-reversion logic"

### Mid-term (Improve Generation)

3. **Revised Prompt Engineering**
   - **Insight:** Simpler prompts → better results
   - New approach: "Minimalist detailed prompt"
     - Specify *what* to implement, not *how*
     - Remove qualitative requirements ("comprehensive logging")
     - Add constraints: "Use only bt.indicators.SMA, RSI, MACD"

4. **Few-Shot Examples**
   - Include 2-3 complete, working strategy examples in prompt
   - Use the 7 successful baseline strategies as templates
   - Format: Problem → Complete Code → Explanation

5. **Iterative Generation with Validation**
   - Generate → Validate → Fix → Regenerate cycle
   - Use AST validator in the loop
   - Stop when syntax_valid=True

### Long-term (System Improvements)

6. **Hybrid LLM + Template Approach**
   - Provide complete strategy template skeleton
   - LLM only fills in specific logic blocks
   - Example: Template has `def next(self):` → LLM generates body only

7. **Multi-Model Ensemble**
   - Generate with multiple models (Llama, Qwen, Deepseek)
   - Use voting or selection based on AST validation scores
   - Expected improvement: 10-20% better runnable rate

8. **Reinforcement Learning from Backtest Feedback**
   - Score strategies by runnability + performance
   - Fine-tune model to maximize score
   - Requires substantial compute resources

---

## Next Steps

### Recommended Execution Plan:

**Step 1:** Run manual completion on high-potential strategies (2-3 hours)
- Target: 11 strategies (2 baseline success + 9 multilayer no-changes)
- Goal: Achieve 20-25/60 runnable rate (33-42%)

**Step 2:** Design and test Experiment 5 with improved prompts
- Use minimalist approach with Few-Shot examples
- Generate 30 new strategies
- Compare runnable rate vs Experiment 4

**Step 3:** If Experiment 5 improves to 40%+ runnable:
- Scale to 100+ strategies
- Run comprehensive backtest on extended dataset
- Analyze performance patterns

**Step 4:** If runnable rate remains <40%:
- Pivot to hybrid template-based approach
- Consider switching to more capable model (Qwen-2.5-72B, GPT-4)

---

## Files Generated

1. `day47_ast_validator.py` - AST structure analysis tool
2. `day48_auto_fix_strategies.py` - Automated error correction
3. `experiment4_trading_extended/baseline_backup/` - Original files
4. `experiment4_trading_extended/multilayer_backup/` - Original files
5. `baseline_fix_report.json` - Detailed fix log (baseline)
6. `multilayer_fix_report.json` - Detailed fix log (multilayer)
7. `ast_validation_multilayer.txt` - Full AST report

---

## Conclusion

The experiment revealed a critical insight: **prompt complexity inversely correlates with code quality** for smaller LLMs. The 8B parameter Llama model performs better with focused, minimal instructions than comprehensive detailed specifications.

The auto-fix pipeline successfully corrected 61 structural issues (37 baseline + 24 multilayer), primarily indentation errors. However, **incomplete code blocks remain the primary barrier to runnability**, requiring either manual intervention or advanced code completion techniques.

**Immediate Priority:** Execute Step 1 (manual completion) to unlock 10+ additional strategies for performance analysis.

**Strategic Priority:** Design Experiment 5 with minimalist Few-Shot prompts, targeting >40% runnable rate.
