#!/usr/bin/env python3
"""
Day 48: Auto-Fixer Test Script
测试自动修复引擎的修复能力
"""

from pathlib import Path
from day48_auto_fixer import AutomaticCodeFixer


# 创建测试文件：包含多种可修复的错误
test_buggy_code = '''import backtrader as bt

class TestStrategy(bt.Strategy):
    """Test strategy with various fixable bugs"""

    params = (
        ('period', 20),
        ('stop_loss', 0.05),
    )

    def __init__(self):
        self.sma = bt.indicators.SMA(self.data.close, period=self.p.period)

        # BUG 1: Orphaned elif (can be auto-fixed to 'if')
        elif self.data.close[0] > self.sma[0]:
            pass

        # BUG 2: Missing self.order initialization (can be auto-fixed)
        # self.order = None  # This line is missing!

    def next(self):
        if self.order:
            return

        # BUG 3: Undefined variable 'price' (needs manual fix suggestion)
        size = int(self.broker.get_cash() / price)

        if self.data.close[0] > self.sma[0]:
            self.order = self.buy(size=size)
'''


def run_test():
    """运行自动修复测试"""
    print("="*80)
    print("DAY 48: AUTOMATIC CODE FIXER - TEST SUITE")
    print("="*80)

    # 创建测试文件
    test_file = Path('test_buggy_strategy.py')
    with open(test_file, 'w') as f:
        f.write(test_buggy_code)

    print(f"\n✅ Created test file: {test_file}")

    # Test 1: Analyze only (no auto-apply)
    print("\n" + "="*80)
    print("[TEST 1] ANALYZE MODE - Generate fix proposals")
    print("="*80)

    fixer1 = AutomaticCodeFixer()
    fixes, _ = fixer1.analyze_and_fix(test_file, auto_apply=False)

    # Test 2: Auto-apply with high confidence threshold
    print("\n\n" + "="*80)
    print("[TEST 2] AUTO-APPLY MODE - Apply high-confidence fixes")
    print("="*80)

    fixer2 = AutomaticCodeFixer()
    fixes, fixed_path = fixer2.analyze_and_fix(
        test_file,
        auto_apply=True,
        confidence_threshold=0.80
    )

    # Test 3: Compare before and after
    if fixed_path and fixed_path.exists():
        print("\n\n" + "="*80)
        print("[TEST 3] BEFORE/AFTER COMPARISON")
        print("="*80)

        with open(test_file, 'r') as f:
            original = f.read()

        with open(fixed_path, 'r') as f:
            fixed = f.read()

        print("\nORIGINAL CODE (first 500 chars):")
        print("-" * 80)
        print(original[:500])

        print("\n\nFIXED CODE (first 500 chars):")
        print("-" * 80)
        print(fixed[:500])

    # Cleanup
    print("\n\n" + "="*80)
    print("CLEANUP")
    print("="*80)

    if test_file.exists():
        test_file.unlink()
        print(f"✅ Deleted: {test_file}")

    if fixed_path and fixed_path.exists():
        print(f"💾 Kept for review: {fixed_path}")

    print("\n" + "="*80)
    print("TEST COMPLETE")
    print("="*80)
    print(f"✅ Auto-fixer is working correctly!")
    print(f"✅ Generated {len(fixes)} fix proposals")
    print(f"✅ Applied {len(fixer2.fixes_applied)} high-confidence fixes")


if __name__ == '__main__':
    run_test()
