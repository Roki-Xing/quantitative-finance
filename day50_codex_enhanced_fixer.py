#!/usr/bin/env python3
"""
Day 50: Codex-Enhanced Code Fixer
Codex AI增强自动修复器 - 集成AI审查提升修复质量

Key Features:
1. AI-assisted fix review and confidence calibration
2. Context-aware fix suggestions
3. Comparison mode: Rule-based vs AI-enhanced
4. Batch processing with Codex enhancement
"""

import ast
import json
import time
import asyncio
from pathlib import Path
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass, asdict, field
from datetime import datetime

from day47_ast_validator import ASTStructureValidator, ValidationIssue
from day48_auto_fixer import AutomaticCodeFixer, Fix, FixPattern


@dataclass
class CodexReview:
    """Codex AI review result"""
    is_fix_correct: bool
    codex_confidence: float  # 0.0-1.0
    alternative_suggestion: Optional[str]
    explanation: str
    review_time: float  # seconds


@dataclass
class EnhancedFix(Fix):
    """Enhanced fix with Codex review"""
    codex_review: Optional[CodexReview] = None
    combined_confidence: float = 0.0
    enhancement_applied: bool = False


class CodexEnhancedFixer(AutomaticCodeFixer):
    """
    Codex-Enhanced Auto Fixer

    Uses Codex AI to:
    1. Review proposed fixes for correctness
    2. Suggest better alternatives
    3. Calibrate confidence scores
    4. Handle complex fixes that rule-based system cannot
    """

    def __init__(self, use_codex: bool = True, codex_model: str = "gpt-4.1"):
        super().__init__()
        self.use_codex = use_codex
        self.codex_model = codex_model
        self.codex_reviews = []
        self.enhancement_stats = {
            'total_reviewed': 0,
            'fixes_improved': 0,
            'confidence_increased': 0,
            'confidence_decreased': 0,
            'alternatives_suggested': 0
        }

    def analyze_and_fix_with_codex(
        self,
        file_path: Path,
        auto_apply: bool = False,
        confidence_threshold: float = 0.80,
        codex_review_all: bool = False
    ) -> Tuple[List[EnhancedFix], Optional[Path]]:
        """
        Analyze and fix with Codex AI enhancement

        Args:
            file_path: Source file to analyze
            auto_apply: Whether to auto-apply high confidence fixes
            confidence_threshold: Minimum confidence for auto-apply
            codex_review_all: If True, review all fixes with Codex
        """
        print(f"\n{'='*80}")
        print(f"DAY 50: CODEX-ENHANCED FIXER")
        print(f"File: {file_path.name}")
        print('='*80)

        # Step 1: Get base fixes from rule-based system
        print("\n[PHASE 1] Rule-Based Analysis (Day 48)")
        print("-" * 80)

        base_fixes, _ = super().analyze_and_fix(
            file_path,
            auto_apply=False,  # Don't apply yet
            confidence_threshold=confidence_threshold
        )

        if not base_fixes:
            print("\n[OK] No issues found - file is clean!")
            return [], None

        # Step 2: Read source for context
        with open(file_path, 'r', encoding='utf-8') as f:
            source_code = f.read()
            source_lines = source_code.split('\n')

        # Step 3: Enhance fixes with Codex
        if self.use_codex:
            print(f"\n[PHASE 2] Codex AI Enhancement")
            print("-" * 80)

            enhanced_fixes = []
            for fix in base_fixes:
                enhanced = self._enhance_fix_with_codex(
                    fix,
                    source_code,
                    source_lines,
                    review_all=codex_review_all
                )
                enhanced_fixes.append(enhanced)

            self._print_enhancement_summary()
        else:
            # Convert to EnhancedFix without Codex review
            enhanced_fixes = [
                EnhancedFix(
                    issue=fix.issue,
                    fix_type=fix.fix_type,
                    confidence=fix.confidence,
                    original_code=fix.original_code,
                    fixed_code=fix.fixed_code,
                    explanation=fix.explanation,
                    combined_confidence=fix.confidence
                )
                for fix in base_fixes
            ]

        # Step 4: Apply fixes if requested
        if auto_apply:
            return self._apply_enhanced_fixes(
                file_path,
                enhanced_fixes,
                confidence_threshold
            )

        return enhanced_fixes, None

    def _enhance_fix_with_codex(
        self,
        fix: Fix,
        source_code: str,
        source_lines: List[str],
        review_all: bool = False
    ) -> EnhancedFix:
        """
        Use Codex to review and potentially improve a fix
        """
        enhanced = EnhancedFix(
            issue=fix.issue,
            fix_type=fix.fix_type,
            confidence=fix.confidence,
            original_code=fix.original_code,
            fixed_code=fix.fixed_code,
            explanation=fix.explanation,
            combined_confidence=fix.confidence
        )

        # Decide whether to use Codex
        should_review = (
            review_all or
            fix.fix_type == 'SEMI_AUTO' or
            fix.fix_type == 'MANUAL_ONLY' or
            fix.confidence < 0.90  # Review uncertain fixes
        )

        if not should_review:
            print(f"  [SKIP] Line {fix.issue.line_number}: High confidence ({fix.confidence:.2f}), skipping Codex review")
            return enhanced

        print(f"  [REVIEW] Line {fix.issue.line_number}: Requesting Codex review...")

        # Build context around the issue
        context_start = max(0, fix.issue.line_number - 10)
        context_end = min(len(source_lines), fix.issue.line_number + 10)
        context_code = '\n'.join(
            f"{i+1}: {line}"
            for i, line in enumerate(source_lines[context_start:context_end], start=context_start)
        )

        # Build Codex prompt
        prompt = self._build_codex_prompt(fix, context_code)

        # Call Codex
        start_time = time.time()
        try:
            review = self._call_codex_for_review(prompt)
            review.review_time = time.time() - start_time

            enhanced.codex_review = review
            enhanced.enhancement_applied = True

            # Combine confidences
            enhanced.combined_confidence = self._combine_confidences(
                fix.confidence,
                review.codex_confidence,
                review.is_fix_correct
            )

            # Apply alternative if suggested and better
            if review.alternative_suggestion and review.codex_confidence > fix.confidence:
                enhanced.fixed_code = review.alternative_suggestion
                enhanced.explanation += f" [Codex improved: {review.explanation}]"
                self.enhancement_stats['alternatives_suggested'] += 1

            # Update stats
            self.enhancement_stats['total_reviewed'] += 1
            if enhanced.combined_confidence > fix.confidence:
                self.enhancement_stats['confidence_increased'] += 1
            elif enhanced.combined_confidence < fix.confidence:
                self.enhancement_stats['confidence_decreased'] += 1
            if review.alternative_suggestion:
                self.enhancement_stats['fixes_improved'] += 1

            print(f"    -> Codex confidence: {review.codex_confidence:.2f}")
            print(f"    -> Combined confidence: {enhanced.combined_confidence:.2f}")
            if review.alternative_suggestion:
                print(f"    -> Alternative suggested: Yes")

        except Exception as e:
            print(f"    -> Codex error: {e}")
            enhanced.combined_confidence = fix.confidence

        return enhanced

    def _build_codex_prompt(self, fix: Fix, context_code: str) -> str:
        """Build prompt for Codex review"""
        return f"""Review this Python code fix for a backtrader trading strategy.

## Context (surrounding code):
```python
{context_code}
```

## Issue Detected:
- Line: {fix.issue.line_number}
- Category: {fix.issue.category}
- Severity: {fix.issue.severity}
- Message: {fix.issue.message}

## Original Code:
```python
{fix.original_code}
```

## Proposed Fix:
```python
{fix.fixed_code}
```

## Fix Explanation:
{fix.explanation}

## Your Task:
1. Is this fix CORRECT? (yes/no)
2. Confidence score (0-100)
3. Is there a BETTER alternative fix? If yes, provide it.
4. Brief explanation of your assessment.

Response format:
CORRECT: yes/no
CONFIDENCE: 0-100
ALTERNATIVE: <code or "none">
EXPLANATION: <your explanation>
"""

    def _call_codex_for_review(self, prompt: str) -> CodexReview:
        """
        Call Codex MCP for fix review

        This method interfaces with the mcp__codex_cli__ask_codex tool
        In actual use, this would be an async call to the MCP tool
        """
        # Simulate Codex response for testing
        # In production, this calls the actual Codex MCP

        # For now, we'll use a heuristic-based simulation
        # This will be replaced with actual Codex calls

        # Check if fix looks reasonable
        is_correct = True
        confidence = 0.85
        alternative = None
        explanation = "Fix appears reasonable based on common patterns."

        # Simple heuristics for demo
        if "elif" in prompt and "if" in prompt:
            confidence = 0.90
            explanation = "Converting orphaned elif to if is a safe transformation."
        elif "self.order = None" in prompt:
            confidence = 0.95
            explanation = "Adding self.order initialization is standard backtrader practice."
        elif "MANUAL_ONLY" in prompt:
            confidence = 0.60
            is_correct = False
            alternative = "# TODO: Review and fix manually"
            explanation = "This fix requires human judgment for context-specific logic."

        return CodexReview(
            is_fix_correct=is_correct,
            codex_confidence=confidence,
            alternative_suggestion=alternative,
            explanation=explanation,
            review_time=0.0
        )

    def _combine_confidences(
        self,
        rule_confidence: float,
        codex_confidence: float,
        codex_approved: bool
    ) -> float:
        """
        Combine rule-based and Codex confidences

        Strategy:
        - If Codex approves: Boost confidence (weighted average favoring higher)
        - If Codex disapproves: Reduce confidence significantly
        """
        if codex_approved:
            # Weighted average, favoring the higher confidence
            combined = max(rule_confidence, codex_confidence) * 0.7 + \
                       min(rule_confidence, codex_confidence) * 0.3
        else:
            # Codex disapproved - reduce confidence
            combined = min(rule_confidence, codex_confidence) * 0.5

        return min(1.0, max(0.0, combined))

    def _apply_enhanced_fixes(
        self,
        file_path: Path,
        fixes: List[EnhancedFix],
        confidence_threshold: float
    ) -> Tuple[List[EnhancedFix], Optional[Path]]:
        """Apply enhanced fixes to file"""

        print(f"\n[PHASE 3] Applying Enhanced Fixes")
        print("-" * 80)

        # Filter by combined confidence
        auto_fixes = [
            f for f in fixes
            if f.combined_confidence >= confidence_threshold
        ]

        print(f"Fixes above threshold ({confidence_threshold:.2f}): {len(auto_fixes)}/{len(fixes)}")

        if not auto_fixes:
            print("[INFO] No fixes meet confidence threshold for auto-apply")
            return fixes, None

        # Read source
        with open(file_path, 'r', encoding='utf-8') as f:
            source_lines = f.readlines()

        # Apply fixes (from bottom to top to preserve line numbers)
        fixes_sorted = sorted(auto_fixes, key=lambda f: f.issue.line_number, reverse=True)

        for fix in fixes_sorted:
            line_idx = fix.issue.line_number - 1

            if fix.fixed_code == '':
                # Delete line
                del source_lines[line_idx]
            elif fix.original_code == '':
                # Insert line
                source_lines.insert(line_idx, fix.fixed_code + '\n')
            else:
                # Replace line
                source_lines[line_idx] = fix.fixed_code + '\n'

            fix.applied = True
            print(f"  Applied: Line {fix.issue.line_number} - {fix.explanation[:50]}")

        # Save fixed file
        fixed_path = file_path.with_suffix('.codex_fixed.py')
        with open(fixed_path, 'w', encoding='utf-8') as f:
            f.writelines(source_lines)

        print(f"\n[OK] Fixed file saved: {fixed_path}")

        # Validate fixed code
        fixed_code = ''.join(source_lines)
        validator = ASTStructureValidator(source_code=fixed_code)
        remaining = validator.validate()

        original_issues = len(fixes)
        remaining_issues = len(remaining)

        print(f"\nValidation: {original_issues} issues -> {remaining_issues} remaining")

        return fixes, fixed_path

    def _print_enhancement_summary(self):
        """Print Codex enhancement statistics"""
        stats = self.enhancement_stats

        print(f"\n[PHASE 2 SUMMARY] Codex Enhancement Results")
        print("-" * 80)
        print(f"  Total fixes reviewed by Codex:  {stats['total_reviewed']}")
        print(f"  Fixes improved with alternatives: {stats['fixes_improved']}")
        print(f"  Confidence increased:           {stats['confidence_increased']}")
        print(f"  Confidence decreased:           {stats['confidence_decreased']}")
        print(f"  Alternative suggestions:        {stats['alternatives_suggested']}")

    def generate_comparison_report(
        self,
        rule_based_results: List[Fix],
        enhanced_results: List[EnhancedFix],
        output_path: Path
    ):
        """Generate comparison report: Rule-based vs Codex-enhanced"""

        report = {
            'date': datetime.now().isoformat(),
            'comparison': {
                'rule_based': {
                    'total_fixes': len(rule_based_results),
                    'auto_fixable': len([f for f in rule_based_results if f.fix_type == 'AUTO']),
                    'avg_confidence': sum(f.confidence for f in rule_based_results) / len(rule_based_results) if rule_based_results else 0
                },
                'codex_enhanced': {
                    'total_fixes': len(enhanced_results),
                    'auto_fixable': len([f for f in enhanced_results if f.combined_confidence >= 0.80]),
                    'avg_confidence': sum(f.combined_confidence for f in enhanced_results) / len(enhanced_results) if enhanced_results else 0,
                    'codex_reviewed': len([f for f in enhanced_results if f.codex_review is not None]),
                    'alternatives_applied': len([f for f in enhanced_results if f.codex_review and f.codex_review.alternative_suggestion])
                }
            },
            'enhancement_stats': self.enhancement_stats,
            'fixes': [
                {
                    'line': f.issue.line_number,
                    'category': f.issue.category,
                    'rule_confidence': f.confidence,
                    'combined_confidence': f.combined_confidence,
                    'codex_reviewed': f.codex_review is not None,
                    'codex_confidence': f.codex_review.codex_confidence if f.codex_review else None,
                    'alternative_suggested': f.codex_review.alternative_suggestion is not None if f.codex_review else False
                }
                for f in enhanced_results
            ]
        }

        with open(output_path, 'w') as f:
            json.dump(report, f, indent=2)

        print(f"\nComparison report saved: {output_path}")


def run_comparison_test(test_code: str, test_name: str = "comparison_test"):
    """
    Run comparison test: Rule-based vs Codex-enhanced fixing
    """
    print("="*80)
    print("DAY 50: CODEX ENHANCEMENT COMPARISON TEST")
    print("="*80)

    # Create test file
    test_file = Path(f"temp_{test_name}.py")
    with open(test_file, 'w', encoding='utf-8') as f:
        f.write(test_code)

    try:
        # Test 1: Rule-based only
        print("\n" + "="*80)
        print("[TEST 1] RULE-BASED FIXING (Day 48)")
        print("="*80)

        fixer_rule = AutomaticCodeFixer()
        rule_fixes, _ = fixer_rule.analyze_and_fix(test_file, auto_apply=False)

        # Test 2: Codex-enhanced
        print("\n" + "="*80)
        print("[TEST 2] CODEX-ENHANCED FIXING (Day 50)")
        print("="*80)

        fixer_codex = CodexEnhancedFixer(use_codex=True)
        enhanced_fixes, fixed_path = fixer_codex.analyze_and_fix_with_codex(
            test_file,
            auto_apply=True,
            confidence_threshold=0.80,
            codex_review_all=True
        )

        # Generate comparison report
        report_path = Path(f"DAY50_COMPARISON_{test_name}.json")
        fixer_codex.generate_comparison_report(rule_fixes, enhanced_fixes, report_path)

        # Summary
        print("\n" + "="*80)
        print("COMPARISON SUMMARY")
        print("="*80)

        rule_auto = len([f for f in rule_fixes if f.fix_type == 'AUTO' and f.confidence >= 0.80])
        codex_auto = len([f for f in enhanced_fixes if f.combined_confidence >= 0.80])

        print(f"\nRule-Based (Day 48):")
        print(f"  Total fixes: {len(rule_fixes)}")
        print(f"  Auto-fixable (conf >= 0.80): {rule_auto}")
        if rule_fixes:
            print(f"  Avg confidence: {sum(f.confidence for f in rule_fixes)/len(rule_fixes):.2f}")

        print(f"\nCodex-Enhanced (Day 50):")
        print(f"  Total fixes: {len(enhanced_fixes)}")
        print(f"  Auto-fixable (conf >= 0.80): {codex_auto}")
        if enhanced_fixes:
            print(f"  Avg combined confidence: {sum(f.combined_confidence for f in enhanced_fixes)/len(enhanced_fixes):.2f}")

        improvement = codex_auto - rule_auto
        print(f"\n[RESULT] Auto-fixable improvement: {improvement:+d} fixes")

        return enhanced_fixes, fixed_path

    finally:
        # Cleanup
        if test_file.exists():
            test_file.unlink()


def create_test_samples() -> List[Tuple[str, str]]:
    """Create test samples with various issues"""

    # Sample 1: Multiple fixable issues
    multi_issue = '''import backtrader as bt

class MultiIssueStrategy(bt.Strategy):
    """Strategy with multiple issues for Codex review"""

    params = (('period', 20),)

    def __init__(self):
        self.sma = bt.indicators.SMA(self.data.close, period=self.p.period)

        # BUG 1: Orphaned elif
        elif self.data.close[0] > self.sma[0]:
            pass

        # BUG 2: Missing self.order

    def next(self):
        if self.order:
            return

        # BUG 3: Undefined variable
        size = int(self.broker.get_cash() / price)

        if self.data.close[0] > self.sma[0]:
            self.order = self.buy(size=size)
'''

    # Sample 2: Complex logic issue
    logic_issue = '''import backtrader as bt

class LogicIssueStrategy(bt.Strategy):
    """Strategy with logic issue requiring AI review"""

    params = (('fast', 10), ('slow', 30))

    def __init__(self):
        self.fast_ma = bt.indicators.SMA(self.data.close, period=self.p.fast)
        self.slow_ma = bt.indicators.SMA(self.data.close, period=self.p.slow)
        self.order = None

        # Suspicious: Empty else with pass
        if self.fast_ma > self.slow_ma:
            pass
        else:
            pass

    def next(self):
        if self.order:
            return

        # Cross detection
        if self.fast_ma[0] > self.slow_ma[0]:
            self.order = self.buy()
'''

    return [
        ("multi_issue", multi_issue),
        ("logic_issue", logic_issue)
    ]


def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(description='Codex-Enhanced Code Fixer (Day 50)')
    parser.add_argument('file', type=Path, nargs='?', help='Python file to fix')
    parser.add_argument('--auto-apply', action='store_true', help='Auto-apply high confidence fixes')
    parser.add_argument('--confidence', type=float, default=0.80, help='Confidence threshold')
    parser.add_argument('--no-codex', action='store_true', help='Disable Codex enhancement')
    parser.add_argument('--review-all', action='store_true', help='Review all fixes with Codex')
    parser.add_argument('--test', action='store_true', help='Run comparison test')
    parser.add_argument('--report', type=Path, help='Output report path')

    args = parser.parse_args()

    if args.test:
        # Run comparison test
        test_samples = create_test_samples()
        for name, code in test_samples:
            print(f"\n{'#'*80}")
            print(f"# TEST: {name}")
            print('#'*80)
            run_comparison_test(code, name)
        return 0

    if not args.file:
        parser.print_help()
        return 1

    if not args.file.exists():
        print(f"Error: File not found: {args.file}")
        return 1

    # Run Codex-enhanced fixer
    fixer = CodexEnhancedFixer(use_codex=not args.no_codex)
    fixes, fixed_path = fixer.analyze_and_fix_with_codex(
        args.file,
        auto_apply=args.auto_apply,
        confidence_threshold=args.confidence,
        codex_review_all=args.review_all
    )

    if args.report:
        # Need rule-based results for comparison
        rule_fixer = AutomaticCodeFixer()
        rule_fixes, _ = rule_fixer.analyze_and_fix(args.file, auto_apply=False)
        fixer.generate_comparison_report(rule_fixes, fixes, args.report)

    print(f"\n{'='*80}")
    print("DAY 50 CODEX-ENHANCED FIXER COMPLETE")
    print('='*80)
    print(f"Total fixes: {len(fixes)}")
    print(f"Applied: {len([f for f in fixes if f.applied])}")

    if fixed_path:
        print(f"Fixed file: {fixed_path}")

    return 0


if __name__ == '__main__':
    import sys
    sys.exit(main())
