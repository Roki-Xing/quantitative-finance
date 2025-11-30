#!/usr/bin/env python3
"""
Day 51: Batch Validation and Auto-Fix Pipeline
批量验证和自动修复流水线 - 在真实LLM生成策略上测试

Pipeline:
1. Load all strategies from batch1
2. Run AST validation (Day 47)
3. Apply auto-fixes (Day 48)
4. Save fixed versions
5. Re-run backtest
6. Report improvement statistics
"""

import ast
import json
import shutil
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Tuple
from dataclasses import dataclass, asdict

# Import our validation tools
from day47_ast_validator import ASTStructureValidator
from day48_auto_fixer import AutomaticCodeFixer


@dataclass
class StrategyResult:
    """Single strategy validation result"""
    name: str
    # Pre-fix state
    syntax_valid: bool
    issues_found: int
    issue_categories: Dict[str, int]
    # Fix results
    fixes_generated: int
    fixes_applied: int
    remaining_issues: int
    # Post-fix state
    fixed_syntax_valid: bool
    # Backtest results
    backtest_before: Dict
    backtest_after: Dict


class BatchValidationPipeline:
    """Batch validation and fix pipeline"""

    def __init__(self, strategy_dir: Path, output_dir: Path):
        self.strategy_dir = Path(strategy_dir)
        self.output_dir = Path(output_dir)
        self.fixed_dir = self.output_dir / "fixed_strategies"
        self.fixed_dir.mkdir(parents=True, exist_ok=True)
        self.results = []

    def run_full_pipeline(self) -> List[StrategyResult]:
        """Run complete validation and fix pipeline"""
        print("="*80)
        print("DAY 51: BATCH VALIDATION AND AUTO-FIX PIPELINE")
        print("="*80)
        print(f"Strategy directory: {self.strategy_dir}")
        print(f"Output directory: {self.output_dir}")
        print()

        # Find all strategy files
        strategy_files = sorted(self.strategy_dir.glob("*.py"))
        print(f"Found {len(strategy_files)} strategy files\n")

        results = []
        for sf in strategy_files:
            result = self.process_single_strategy(sf)
            results.append(result)

        self.results = results
        return results

    def process_single_strategy(self, file_path: Path) -> StrategyResult:
        """Process a single strategy file"""
        print(f"\n{'-'*80}")
        print(f"Processing: {file_path.name}")
        print("-"*80)

        result = StrategyResult(
            name=file_path.stem,
            syntax_valid=False,
            issues_found=0,
            issue_categories={},
            fixes_generated=0,
            fixes_applied=0,
            remaining_issues=0,
            fixed_syntax_valid=False,
            backtest_before={},
            backtest_after={}
        )

        # Read source code
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                source_code = f.read()
        except Exception as e:
            print(f"  [ERROR] Cannot read file: {e}")
            return result

        # Step 1: Syntax check
        print("  [1] Syntax check...")
        try:
            ast.parse(source_code)
            result.syntax_valid = True
            print("      [OK] Syntax valid")
        except SyntaxError as e:
            print(f"      [FAIL] Syntax error at line {e.lineno}: {e.msg}")

        # Step 2: AST validation (even if syntax error, we can detect some issues)
        print("  [2] AST structure validation...")
        if result.syntax_valid:
            validator = ASTStructureValidator(source_code=source_code)
            issues = validator.validate()

            result.issues_found = len(issues)

            # Count by category
            for issue in issues:
                cat = issue.category
                result.issue_categories[cat] = result.issue_categories.get(cat, 0) + 1

            print(f"      Found {len(issues)} structural issues")
            for issue in issues[:5]:  # Show first 5
                print(f"        - Line {issue.line_number}: {issue.message[:50]}")
            if len(issues) > 5:
                print(f"        ... and {len(issues)-5} more")
        else:
            # Try to detect issues even with syntax error
            result.issues_found = 1  # At minimum the syntax error
            result.issue_categories['SYNTAX_ERROR'] = 1
            print("      [SKIP] Cannot validate - syntax error")

        # Step 3: Auto-fix
        print("  [3] Generating fixes...")

        # For syntax errors, try line-by-line fix
        if not result.syntax_valid:
            fixed_code = self._attempt_syntax_fix(source_code, file_path.name)
            if fixed_code and fixed_code != source_code:
                # Save temp file for fixer
                temp_file = self.output_dir / f"temp_{file_path.name}"
                with open(temp_file, 'w', encoding='utf-8') as f:
                    f.write(fixed_code)

                # Check if syntax fixed
                try:
                    ast.parse(fixed_code)
                    result.fixed_syntax_valid = True
                    source_code = fixed_code
                    print("      [OK] Syntax error auto-fixed!")

                    # Now run full validation
                    validator = ASTStructureValidator(source_code=fixed_code)
                    issues = validator.validate()
                    result.issues_found = len(issues)
                except:
                    print("      [WARN] Syntax fix attempt failed")

                temp_file.unlink(missing_ok=True)
        else:
            result.fixed_syntax_valid = True

        # Run standard fixer if we have valid syntax now
        if result.fixed_syntax_valid or result.syntax_valid:
            # Write to temp file
            temp_file = self.output_dir / f"temp_{file_path.name}"
            with open(temp_file, 'w', encoding='utf-8') as f:
                f.write(source_code)

            try:
                fixer = AutomaticCodeFixer()
                fixes, fixed_path = fixer.analyze_and_fix(
                    temp_file,
                    auto_apply=True,
                    confidence_threshold=0.75  # Lower threshold for batch
                )

                result.fixes_generated = len(fixes)
                result.fixes_applied = len(fixer.fixes_applied)

                # Check remaining issues
                if fixed_path and fixed_path.exists():
                    with open(fixed_path, 'r', encoding='utf-8') as f:
                        fixed_code = f.read()

                    validator_fixed = ASTStructureValidator(source_code=fixed_code)
                    remaining = validator_fixed.validate()
                    result.remaining_issues = len(remaining)

                    # Copy to fixed directory
                    final_path = self.fixed_dir / file_path.name
                    shutil.copy(fixed_path, final_path)
                    print(f"      Saved: {final_path}")

                    # Cleanup
                    fixed_path.unlink(missing_ok=True)
                else:
                    result.remaining_issues = result.issues_found

                print(f"      Fixes: {result.fixes_applied}/{result.fixes_generated}")
                print(f"      Issues: {result.issues_found} -> {result.remaining_issues}")

            except Exception as e:
                print(f"      [ERROR] Fixer failed: {e}")

            temp_file.unlink(missing_ok=True)

        return result

    def _attempt_syntax_fix(self, source: str, filename: str) -> str:
        """Attempt to fix common syntax errors"""
        lines = source.split('\n')
        fixed_lines = []
        in_class = False
        in_method = False

        for i, line in enumerate(lines):
            stripped = line.strip()

            # Track class/method context
            if stripped.startswith('class ') and ':' in stripped:
                in_class = True
                in_method = False
            elif stripped.startswith('def ') and ':' in stripped:
                in_method = True

            # Fix 1: Orphaned elif -> if
            if stripped.startswith('elif ') and in_method:
                # Check if previous non-empty line is not if/elif
                prev_idx = i - 1
                while prev_idx >= 0 and not lines[prev_idx].strip():
                    prev_idx -= 1

                if prev_idx >= 0:
                    prev = lines[prev_idx].strip()
                    if not prev.startswith(('if ', 'elif ', 'else:')):
                        # This is an orphaned elif
                        indent = len(line) - len(line.lstrip())
                        fixed_lines.append(' ' * indent + 'if ' + stripped[5:])
                        continue

            # Fix 2: Remove standalone data loading at module level
            if ('bt.feeds.PandasData' in stripped or
                'cerebro.adddata' in stripped or
                'cerebro.run()' in stripped) and not in_method:
                # Comment out module-level backtest code
                indent = len(line) - len(line.lstrip())
                fixed_lines.append(' ' * indent + '# REMOVED: ' + stripped)
                continue

            fixed_lines.append(line)

        return '\n'.join(fixed_lines)

    def generate_report(self, output_path: Path):
        """Generate summary report"""
        print("\n\n" + "="*80)
        print("BATCH VALIDATION REPORT")
        print("="*80)

        if not self.results:
            print("No results to report")
            return

        total = len(self.results)
        syntax_valid_before = sum(1 for r in self.results if r.syntax_valid)
        syntax_valid_after = sum(1 for r in self.results if r.fixed_syntax_valid)

        total_issues_before = sum(r.issues_found for r in self.results)
        total_issues_after = sum(r.remaining_issues for r in self.results)

        total_fixes_generated = sum(r.fixes_generated for r in self.results)
        total_fixes_applied = sum(r.fixes_applied for r in self.results)

        print(f"\nTotal strategies: {total}")
        print(f"\nSyntax Validity:")
        print(f"  Before: {syntax_valid_before}/{total} ({syntax_valid_before/total*100:.1f}%)")
        print(f"  After:  {syntax_valid_after}/{total} ({syntax_valid_after/total*100:.1f}%)")

        print(f"\nStructural Issues:")
        print(f"  Before: {total_issues_before}")
        print(f"  After:  {total_issues_after}")
        if total_issues_before > 0:
            reduction = (total_issues_before - total_issues_after) / total_issues_before * 100
            print(f"  Reduction: {reduction:.1f}%")

        print(f"\nFixes:")
        print(f"  Generated: {total_fixes_generated}")
        print(f"  Applied:   {total_fixes_applied}")

        # Issue category breakdown
        all_categories = {}
        for r in self.results:
            for cat, count in r.issue_categories.items():
                all_categories[cat] = all_categories.get(cat, 0) + count

        print(f"\nIssue Categories:")
        for cat, count in sorted(all_categories.items(), key=lambda x: -x[1]):
            print(f"  {cat}: {count}")

        # Per-strategy details
        print(f"\n{'='*80}")
        print("PER-STRATEGY DETAILS")
        print("="*80)

        for r in self.results:
            status = "[OK]" if r.remaining_issues == 0 and r.fixed_syntax_valid else "[NEEDS WORK]"
            print(f"\n{status} {r.name}")
            print(f"    Syntax: {'Valid' if r.syntax_valid else 'ERROR'} -> {'Valid' if r.fixed_syntax_valid else 'ERROR'}")
            print(f"    Issues: {r.issues_found} -> {r.remaining_issues}")
            print(f"    Fixes:  {r.fixes_applied}/{r.fixes_generated}")

        # Save JSON report
        report_data = {
            'date': datetime.now().isoformat(),
            'summary': {
                'total_strategies': total,
                'syntax_valid_before': syntax_valid_before,
                'syntax_valid_after': syntax_valid_after,
                'total_issues_before': total_issues_before,
                'total_issues_after': total_issues_after,
                'total_fixes_generated': total_fixes_generated,
                'total_fixes_applied': total_fixes_applied,
                'issue_reduction_rate': reduction if total_issues_before > 0 else 0
            },
            'issue_categories': all_categories,
            'strategies': [asdict(r) for r in self.results]
        }

        with open(output_path, 'w') as f:
            json.dump(report_data, f, indent=2)

        print(f"\n{'='*80}")
        print(f"Report saved: {output_path}")
        print("="*80)


def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(description='Day 51: Batch Validation Pipeline')
    parser.add_argument('--strategy-dir', type=Path,
                        default=Path('/root/autodl-tmp/eoh/strategy_library/batch1'),
                        help='Directory containing strategy files')
    parser.add_argument('--output-dir', type=Path,
                        default=Path('/root/autodl-tmp/eoh/validation_results'),
                        help='Output directory for results')

    args = parser.parse_args()

    # Ensure output directory exists
    args.output_dir.mkdir(parents=True, exist_ok=True)

    # Run pipeline
    pipeline = BatchValidationPipeline(args.strategy_dir, args.output_dir)
    results = pipeline.run_full_pipeline()

    # Generate report
    report_path = args.output_dir / "DAY51_BATCH_VALIDATION_REPORT.json"
    pipeline.generate_report(report_path)

    print("\n" + "="*80)
    print("DAY 51 BATCH VALIDATION COMPLETE")
    print("="*80)

    # Summary
    clean_count = sum(1 for r in results if r.remaining_issues == 0 and r.fixed_syntax_valid)
    print(f"\nFinal Status: {clean_count}/{len(results)} strategies are clean")

    return 0


if __name__ == '__main__':
    import sys
    sys.exit(main())
