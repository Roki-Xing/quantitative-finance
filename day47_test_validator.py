#!/usr/bin/env python3
"""
Day 47: AST Validator Test Script
测试AST验证工具对Phase 3发现的结构性错误的检测能力
"""

from day47_ast_validator import ASTStructureValidator
from pathlib import Path


# 创建测试样本：包含典型的LLM结构性错误
test_code_buggy = '''
import backtrader as bt

class DualMAStrategy(bt.Strategy):
    """
    Dual MA Crossover with LLM-generated bugs
    This code has METHOD_BOUNDARY error from Phase 3
    """

    params = (
        ('fast', 20),
        ('slow', 50),
        ('stop_loss', 0.05),
    )

    def __init__(self):
        self.fast_ma = bt.indicators.SMA(self.data.close, period=self.p.fast)
        self.slow_ma = bt.indicators.SMA(self.data.close, period=self.p.slow)
        self.order = None
        self.entry_price = 0.0

        # BUG 1: Orphaned elif in __init__ (典型的LLM错误)
        elif order.status in [order.Canceled, order.Margin]:
            logger.warning(f"Order failed: {order.status}")

        # BUG 2: Using undefined variable 'order'

    def next(self):
        if self.order:
            return

        # BUG 3: Using undefined variable 'price'
        size = int(self.broker.get_cash() / price)

        if self.fast_ma[0] > self.slow_ma[0]:
            self.order = self.buy(size=size)
'''


test_code_clean = '''
import backtrader as bt

class DualMAStrategy(bt.Strategy):
    """
    Dual MA Crossover - Clean version
    """

    params = (
        ('fast', 20),
        ('slow', 50),
        ('stop_loss', 0.05),
    )

    def __init__(self):
        self.fast_ma = bt.indicators.SMA(self.data.close, period=self.p.fast)
        self.slow_ma = bt.indicators.SMA(self.data.close, period=self.p.slow)
        self.order = None
        self.entry_price = 0.0

    def notify_order(self, order):
        if order.status in [order.Submitted, order.Accepted]:
            return
        if order.status == order.Completed:
            if order.isbuy():
                self.entry_price = order.executed.price
        elif order.status in [order.Canceled, order.Margin]:
            print(f"Order failed: {order.status}")
        self.order = None

    def next(self):
        if self.order:
            return

        current_price = self.data.close[0]
        size = int(self.broker.get_cash() * 0.95 / current_price)

        if self.fast_ma[0] > self.slow_ma[0]:
            if size > 0:
                self.order = self.buy(size=size)
'''


def test_validator():
    """测试验证器"""
    print("=" * 80)
    print("DAY 47: AST STRUCTURE VALIDATOR - TEST SUITE")
    print("=" * 80)
    print()

    # Test 1: Buggy Code
    print("\n[TEST 1] Validating BUGGY code (LLM-generated with errors)")
    print("-" * 80)
    validator_buggy = ASTStructureValidator(source_code=test_code_buggy)
    validator_buggy.validate()
    validator_buggy.print_report()

    # Test 2: Clean Code
    print("\n\n[TEST 2] Validating CLEAN code (manually fixed)")
    print("-" * 80)
    validator_clean = ASTStructureValidator(source_code=test_code_clean)
    validator_clean.validate()
    validator_clean.print_report()

    # Summary
    print("\n\n" + "=" * 80)
    print("TEST SUMMARY")
    print("=" * 80)
    buggy_issues = len(validator_buggy.issues)
    clean_issues = len(validator_clean.issues)

    print(f"Buggy Code Issues: {buggy_issues}")
    print(f"Clean Code Issues: {clean_issues}")

    if buggy_issues > 0 and clean_issues == 0:
        print("\n✅ VALIDATION SUCCESSFUL:")
        print("   - Detected issues in buggy code")
        print("   - No issues in clean code")
        print("   - Validator is working correctly!")
    elif buggy_issues > 0 and clean_issues > 0:
        print("\n⚠️  PARTIAL SUCCESS:")
        print("   - Detected issues in buggy code")
        print("   - Also found some issues in clean code (may be false positives)")
    else:
        print("\n❌ VALIDATION FAILED:")
        print("   - Did not detect issues in buggy code")


def validate_phase3_strategies():
    """验证Phase 3的策略文件"""
    print("\n\n" + "=" * 80)
    print("VALIDATING PHASE 3 STRATEGIES")
    print("=" * 80)

    # 检查day44_backtest_inline.py
    inline_file = Path("day44_backtest_inline.py")
    if inline_file.exists():
        print(f"\nValidating: {inline_file}")
        validator = ASTStructureValidator(file_path=inline_file)
        validator.validate()

        if len(validator.issues) == 0:
            print("✅ No issues found - code is clean!")
        else:
            validator.print_report()


if __name__ == '__main__':
    test_validator()
    validate_phase3_strategies()
