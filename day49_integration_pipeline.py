#!/usr/bin/env python3
"""
Day 49: Complete Pipeline Integration Testing
完整流程集成测试：LLM生成 → AST验证 → 自动修复 → 运行时测试

Pipeline:
1. Generate strategies (or load test samples)
2. AST structure validation (Day 47)
3. Automatic fixing (Day 48)
4. Runtime backtest validation
5. Metrics collection and reporting
"""

import ast
import json
from pathlib import Path
from typing import List, Dict, Tuple
from datetime import datetime
from dataclasses import dataclass, asdict

# Optional imports for runtime testing
try:
    import backtrader as bt
    import pandas as pd
    BACKTRADER_AVAILABLE = True
except ImportError:
    BACKTRADER_AVAILABLE = False
    print("WARNING: backtrader not available - runtime testing will be skipped")

from day47_ast_validator import ASTStructureValidator
from day48_auto_fixer import AutomaticCodeFixer


@dataclass
class PipelineResult:
    """Pipeline测试结果"""
    strategy_name: str
    stage1_syntax: bool  # 语法检查
    stage2_structure: Dict  # 结构验证
    stage3_autofix: Dict  # 自动修复
    stage4_runtime: Dict  # 运行时测试
    overall_success: bool
    processing_time: float


class IntegrationTestPipeline:
    """完整流程集成测试引擎"""

    def __init__(self, test_data_path: Path = None):
        self.test_data = test_data_path
        self.results = []
        self.validator = None
        self.fixer = None

    def run_complete_pipeline(self, code: str, name: str) -> PipelineResult:
        """运行完整流程测试单个策略"""
        import time
        start_time = time.time()

        print(f"\n{'='*80}")
        print(f"TESTING STRATEGY: {name}")
        print('='*80)

        result = PipelineResult(
            strategy_name=name,
            stage1_syntax=False,
            stage2_structure={},
            stage3_autofix={},
            stage4_runtime={},
            overall_success=False,
            processing_time=0.0
        )

        # Stage 1: Syntax Check
        print("\n[STAGE 1] Syntax Validation")
        print("-" * 80)
        try:
            ast.parse(code)
            result.stage1_syntax = True
            print("[OK] Syntax check passed")
        except SyntaxError as e:
            print(f"[FAIL] Syntax error: {e}")
            result.processing_time = time.time() - start_time
            return result

        # Stage 2: AST Structure Validation
        print("\n[STAGE 2] AST Structure Validation (Day 47)")
        print("-" * 80)
        validator = ASTStructureValidator(source_code=code)
        issues = validator.validate()

        result.stage2_structure = {
            'issues_found': len(issues),
            'critical': len([i for i in issues if i.severity == 'CRITICAL']),
            'high': len([i for i in issues if i.severity == 'HIGH']),
            'medium': len([i for i in issues if i.severity == 'MEDIUM']),
            'categories': {}
        }

        # Count by category
        for issue in issues:
            cat = issue.category
            result.stage2_structure['categories'][cat] = \
                result.stage2_structure['categories'].get(cat, 0) + 1

        if issues:
            print(f"[WARN] Found {len(issues)} structural issues:")
            for issue in issues:
                print(f"   - Line {issue.line_number}: {issue.message[:60]}")
        else:
            print("[OK] No structural issues found")
            # Skip to Stage 4 if no issues
            result.stage3_autofix = {'skipped': True, 'reason': 'No issues found'}
            result = self._run_runtime_test(code, result)
            result.processing_time = time.time() - start_time
            return result

        # Stage 3: Automatic Fixing
        print("\n[STAGE 3] Automatic Code Fixing (Day 48)")
        print("-" * 80)

        # Save temporary file for fixer
        temp_file = Path(f"temp_{name}.py")
        with open(temp_file, 'w', encoding='utf-8') as f:
            f.write(code)

        fixer = AutomaticCodeFixer()
        fixes, fixed_path = fixer.analyze_and_fix(
            temp_file,
            auto_apply=True,
            confidence_threshold=0.80
        )

        result.stage3_autofix = {
            'fixes_generated': len(fixes),
            'fixes_applied': len(fixer.fixes_applied),
            'auto_fixes': len([f for f in fixes if f.fix_type == 'AUTO']),
            'semi_auto': len([f for f in fixes if f.fix_type == 'SEMI_AUTO']),
            'manual': len([f for f in fixes if f.fix_type == 'MANUAL_ONLY']),
            'fixed_file': str(fixed_path) if fixed_path else None
        }

        print(f"Generated {len(fixes)} fixes, applied {len(fixer.fixes_applied)}")

        # Load fixed code
        if fixed_path and fixed_path.exists():
            with open(fixed_path, 'r', encoding='utf-8') as f:
                fixed_code = f.read()

            # Re-validate fixed code
            validator_fixed = ASTStructureValidator(source_code=fixed_code)
            remaining_issues = validator_fixed.validate()
            result.stage3_autofix['remaining_issues'] = len(remaining_issues)

            print(f"Issues after fixing: {len(issues)} → {len(remaining_issues)}")

            # Use fixed code for runtime test
            code = fixed_code
        else:
            print("[WARN]  No fixes were applied")
            result.stage3_autofix['remaining_issues'] = len(issues)

        # Cleanup temp files
        if temp_file.exists():
            temp_file.unlink()
        if fixed_path and fixed_path.exists():
            # Keep fixed file for review
            pass

        # Stage 4: Runtime Test
        result = self._run_runtime_test(code, result)
        result.processing_time = time.time() - start_time

        # Overall success: syntax + structure clean + runtime success
        if BACKTRADER_AVAILABLE:
            # Full pipeline success
            result.overall_success = (
                result.stage1_syntax and
                (result.stage2_structure['issues_found'] == 0 or
                 result.stage3_autofix.get('remaining_issues', 999) == 0) and
                result.stage4_runtime.get('success', False)
            )
        else:
            # Pipeline success without runtime (syntax + structure only)
            result.overall_success = (
                result.stage1_syntax and
                (result.stage2_structure['issues_found'] == 0 or
                 result.stage3_autofix.get('remaining_issues', 999) == 0)
            )

        return result

    def _run_runtime_test(self, code: str, result: PipelineResult) -> PipelineResult:
        """Stage 4: Runtime backtest test"""
        print("\n[STAGE 4] Runtime Backtest Test")
        print("-" * 80)

        if not BACKTRADER_AVAILABLE:
            result.stage4_runtime = {
                'success': None,
                'skipped': True,
                'reason': 'backtrader not available'
            }
            print("WARNING: Skipped - backtrader not installed")
            return result

        try:
            # Import strategy dynamically
            namespace = {}
            exec(code, namespace)

            # Find strategy class
            strategy_class = None
            for name, obj in namespace.items():
                if isinstance(obj, type) and issubclass(obj, bt.Strategy) and obj != bt.Strategy:
                    strategy_class = obj
                    break

            if not strategy_class:
                result.stage4_runtime = {
                    'success': False,
                    'error': 'No strategy class found'
                }
                print("[FAIL] No strategy class found")
                return result

            # Simple backtest
            cerebro = bt.Cerebro()
            cerebro.addstrategy(strategy_class)

            # Create dummy data
            dates = pd.date_range('2024-01-01', '2024-11-22', freq='D')
            df = pd.DataFrame({
                'open': 100.0,
                'high': 102.0,
                'low': 98.0,
                'close': 101.0,
                'volume': 1000000
            }, index=dates)

            data = bt.feeds.PandasData(dataname=df)
            cerebro.adddata(data)

            cerebro.broker.setcash(100000.0)
            cerebro.broker.setcommission(commission=0.001)

            initial = cerebro.broker.getvalue()
            cerebro.run()
            final = cerebro.broker.getvalue()

            result.stage4_runtime = {
                'success': True,
                'initial_capital': initial,
                'final_capital': final,
                'return': (final - initial) / initial * 100
            }

            print(f"[OK] Runtime test passed")
            print(f"   Initial: ${initial:,.2f}")
            print(f"   Final: ${final:,.2f}")
            print(f"   Return: {result.stage4_runtime['return']:.2f}%")

        except Exception as e:
            result.stage4_runtime = {
                'success': False,
                'error': str(e)
            }
            print(f"[FAIL] Runtime error: {e}")

        return result

    def batch_test(self, test_cases: List[Tuple[str, str]]) -> List[PipelineResult]:
        """批量测试多个策略"""
        print("\n" + "="*80)
        print("DAY 49: INTEGRATION PIPELINE - BATCH TEST")
        print("="*80)
        print(f"Testing {len(test_cases)} strategies\n")

        results = []
        for name, code in test_cases:
            result = self.run_complete_pipeline(code, name)
            results.append(result)

        self.results = results
        return results

    def generate_report(self, output_path: Path):
        """生成测试报告"""
        print("\n\n" + "="*80)
        print("PIPELINE TEST REPORT")
        print("="*80)

        if not self.results:
            print("No test results available")
            return

        total = len(self.results)
        syntax_pass = sum(1 for r in self.results if r.stage1_syntax)
        structure_clean = sum(1 for r in self.results if r.stage2_structure.get('issues_found', 999) == 0)
        fixed_clean = sum(1 for r in self.results if r.stage3_autofix.get('remaining_issues', 999) == 0)
        runtime_success = sum(1 for r in self.results if r.stage4_runtime.get('success', False))
        overall_success = sum(1 for r in self.results if r.overall_success)

        print(f"\n{'='*80}")
        print("SUMMARY STATISTICS")
        print('='*80)
        print(f"Total Strategies Tested: {total}")
        print(f"\nStage Success Rates:")
        print(f"  Stage 1 (Syntax):     {syntax_pass}/{total} ({syntax_pass/total*100:.1f}%)")
        print(f"  Stage 2 (Structure):  {structure_clean}/{total} ({structure_clean/total*100:.1f}%)")
        print(f"  Stage 3 (Auto-Fix):   {fixed_clean}/{total} ({fixed_clean/total*100:.1f}%)")
        print(f"  Stage 4 (Runtime):    {runtime_success}/{total} ({runtime_success/total*100:.1f}%)")
        print(f"\n  Overall Success:      {overall_success}/{total} ({overall_success/total*100:.1f}%)")

        # Structural issues breakdown
        total_issues_found = sum(r.stage2_structure.get('issues_found', 0) for r in self.results)
        total_fixes_applied = sum(r.stage3_autofix.get('fixes_applied', 0) for r in self.results)
        total_remaining = sum(r.stage3_autofix.get('remaining_issues', 0) for r in self.results)

        print(f"\n{'='*80}")
        print("AUTO-FIX PERFORMANCE")
        print('='*80)
        print(f"Total Issues Detected:    {total_issues_found}")
        print(f"Fixes Applied:            {total_fixes_applied}")
        print(f"Issues Remaining:         {total_remaining}")
        if total_issues_found > 0:
            fix_rate = (total_issues_found - total_remaining) / total_issues_found * 100
            print(f"Fix Success Rate:         {fix_rate:.1f}%")

        # Processing time
        avg_time = sum(r.processing_time for r in self.results) / total
        print(f"\nAverage Processing Time:  {avg_time:.2f} seconds/strategy")

        # Detailed results
        print(f"\n{'='*80}")
        print("DETAILED RESULTS")
        print('='*80)

        for i, r in enumerate(self.results, 1):
            status = "[OK]" if r.overall_success else "[FAIL]"
            print(f"\n{i}. {status} {r.strategy_name}")
            print(f"   Syntax: {r.stage1_syntax} | " +
                  f"Struct Issues: {r.stage2_structure.get('issues_found', 0)} | " +
                  f"Fixes: {r.stage3_autofix.get('fixes_applied', 0)} | " +
                  f"Runtime: {r.stage4_runtime.get('success', False)}")

            if not r.stage4_runtime.get('success', False):
                error = r.stage4_runtime.get('error', 'Unknown')
                print(f"   Error: {error[:70]}")

        # Save JSON report
        report_data = {
            'date': datetime.now().isoformat(),
            'total_tested': total,
            'summary': {
                'syntax_pass_rate': syntax_pass / total,
                'structure_clean_rate': structure_clean / total,
                'auto_fix_rate': fixed_clean / total if total_issues_found > 0 else 1.0,
                'runtime_success_rate': runtime_success / total,
                'overall_success_rate': overall_success / total
            },
            'metrics': {
                'total_issues_found': total_issues_found,
                'total_fixes_applied': total_fixes_applied,
                'total_remaining_issues': total_remaining,
                'avg_processing_time': avg_time
            },
            'results': [asdict(r) for r in self.results]
        }

        with open(output_path, 'w') as f:
            json.dump(report_data, f, indent=2, default=str)

        print(f"\n{'='*80}")
        print(f"Report saved: {output_path}")
        print('='*80)


def create_test_samples() -> List[Tuple[str, str]]:
    """创建测试样本：包含不同类型的错误"""

    # Sample 1: Clean code (no issues)
    clean_code = '''import backtrader as bt

class CleanStrategy(bt.Strategy):
    """Clean strategy with no issues"""

    params = (('period', 20),)

    def __init__(self):
        self.sma = bt.indicators.SMA(self.data.close, period=self.p.period)
        self.order = None

    def notify_order(self, order):
        if order.status in [order.Submitted, order.Accepted]:
            return
        if order.status == order.Completed:
            if order.isbuy():
                pass
        elif order.status in [order.Canceled, order.Margin]:
            pass
        self.order = None

    def next(self):
        if self.order:
            return
        if self.data.close[0] > self.sma[0]:
            self.order = self.buy()
'''

    # Sample 2: Orphaned elif (fixable)
    orphaned_elif_code = '''import backtrader as bt

class OrphanedElifStrategy(bt.Strategy):
    """Strategy with orphaned elif bug"""

    params = (('period', 20),)

    def __init__(self):
        self.sma = bt.indicators.SMA(self.data.close, period=self.p.period)
        self.order = None

        # BUG: Orphaned elif
        elif self.data.close[0] > self.sma[0]:
            pass

    def next(self):
        if self.order:
            return
        if self.data.close[0] > self.sma[0]:
            self.order = self.buy()
'''

    # Sample 3: Missing initialization (fixable)
    missing_init_code = '''import backtrader as bt

class MissingInitStrategy(bt.Strategy):
    """Strategy with missing self.order initialization"""

    params = (('period', 20),)

    def __init__(self):
        self.sma = bt.indicators.SMA(self.data.close, period=self.p.period)
        # BUG: Missing self.order = None

    def next(self):
        if self.order:
            return
        if self.data.close[0] > self.sma[0]:
            self.order = self.buy()
'''

    # Sample 4: Multiple issues (mixed fixability)
    multi_bug_code = '''import backtrader as bt

class MultiBugStrategy(bt.Strategy):
    """Strategy with multiple bugs"""

    params = (('period', 20),)

    def __init__(self):
        self.sma = bt.indicators.SMA(self.data.close, period=self.p.period)

        # BUG 1: Orphaned elif (fixable)
        elif order.status == order.Completed:
            self.entry_price = order.price

        # BUG 2: Missing self.order (fixable by MissingInitFixer)

    def next(self):
        if self.order:
            return

        # BUG 3: Undefined variable 'price' (manual fix needed)
        size = int(self.broker.get_cash() / price)

        if self.data.close[0] > self.sma[0]:
            self.order = self.buy(size=size)
'''

    return [
        ("1_clean", clean_code),
        ("2_orphaned_elif", orphaned_elif_code),
        ("3_missing_init", missing_init_code),
        ("4_multi_bug", multi_bug_code)
    ]


def main():
    """Main test execution"""
    print("="*80)
    print("DAY 49: COMPLETE PIPELINE INTEGRATION TEST")
    print("="*80)
    print("\nPipeline Stages:")
    print("  1. Syntax Check (ast.parse)")
    print("  2. AST Structure Validation (Day 47)")
    print("  3. Automatic Code Fixing (Day 48)")
    print("  4. Runtime Backtest Test")
    print()

    # Create test samples
    test_cases = create_test_samples()

    # Run pipeline
    pipeline = IntegrationTestPipeline()
    results = pipeline.batch_test(test_cases)

    # Generate report
    report_path = Path("DAY49_PIPELINE_TEST_REPORT.json")
    pipeline.generate_report(report_path)

    print("\n" + "="*80)
    print("DAY 49 INTEGRATION TEST COMPLETE")
    print("="*80)

    return 0


if __name__ == '__main__':
    import sys
    sys.exit(main())
