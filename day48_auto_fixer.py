#!/usr/bin/env python3
"""
Day 48: Automatic Code Fixer
自动修复引擎 - 基于Day 47检测结果自动修复代码结构性错误

修复能力:
1. METHOD_BOUNDARY - 移动错误位置的代码到正确方法
2. ORPHANED_STATEMENT - 修复孤立的elif/else
3. MISSING_INIT - 添加缺失的初始化
4. UNDEFINED_VARIABLE - 添加变量定义建议
"""

import ast
import re
from pathlib import Path
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass
from datetime import datetime
import json

from day47_ast_validator import ASTStructureValidator, ValidationIssue


@dataclass
class Fix:
    """修复操作数据结构"""
    issue: ValidationIssue
    fix_type: str  # 'AUTO', 'SEMI_AUTO', 'MANUAL_ONLY'
    confidence: float  # 0.0-1.0
    original_code: str
    fixed_code: str
    explanation: str
    applied: bool = False


class FixPattern:
    """修复模式基类"""

    def can_fix(self, issue: ValidationIssue) -> bool:
        """判断是否可以修复此问题"""
        raise NotImplementedError

    def generate_fix(self, issue: ValidationIssue, source_lines: List[str]) -> Optional[Fix]:
        """生成修复方案"""
        raise NotImplementedError

    def get_confidence(self, issue: ValidationIssue) -> float:
        """计算修复置信度"""
        raise NotImplementedError


class OrphanedElifFixer(FixPattern):
    """修复孤立elif/else的修复器"""

    def can_fix(self, issue: ValidationIssue) -> bool:
        return issue.category in ['ORPHANED_STATEMENT', 'METHOD_BOUNDARY']

    def generate_fix(self, issue: ValidationIssue, source_lines: List[str]) -> Optional[Fix]:
        line_idx = issue.line_number - 1
        if line_idx >= len(source_lines):
            return None

        original_line = source_lines[line_idx]
        stripped = original_line.strip()

        # 修复策略1: 将elif改为if
        if stripped.startswith('elif '):
            fixed_line = original_line.replace('elif ', 'if ', 1)

            return Fix(
                issue=issue,
                fix_type='AUTO',
                confidence=0.85,
                original_code=original_line,
                fixed_code=fixed_line,
                explanation="Converted orphaned 'elif' to 'if' statement"
            )

        # 修复策略2: 删除else (置信度较低)
        elif stripped.startswith('else:'):
            # 检查是否有缩进内容
            indent = len(original_line) - len(original_line.lstrip())
            has_body = False

            for i in range(line_idx + 1, min(line_idx + 5, len(source_lines))):
                next_line = source_lines[i]
                next_indent = len(next_line) - len(next_line.lstrip())
                if next_line.strip() and next_indent > indent:
                    has_body = True
                    break

            if not has_body:
                # 直接删除空else
                return Fix(
                    issue=issue,
                    fix_type='AUTO',
                    confidence=0.90,
                    original_code=original_line,
                    fixed_code='',  # 删除此行
                    explanation="Removed orphaned empty 'else' statement"
                )
            else:
                # 有内容的else需要人工处理
                return Fix(
                    issue=issue,
                    fix_type='MANUAL_ONLY',
                    confidence=0.30,
                    original_code=original_line,
                    fixed_code=original_line,  # 不修改
                    explanation="Orphaned 'else' with body requires manual review"
                )

        return None

    def get_confidence(self, issue: ValidationIssue) -> float:
        return 0.85


class MethodBoundaryFixer(FixPattern):
    """修复方法边界混淆的修复器"""

    def can_fix(self, issue: ValidationIssue) -> bool:
        return issue.category == 'METHOD_BOUNDARY'

    def generate_fix(self, issue: ValidationIssue, source_lines: List[str]) -> Optional[Fix]:
        """
        检测在__init__中的elif order.status，移动到notify_order
        """
        line_idx = issue.line_number - 1
        original_line = source_lines[line_idx]

        # 检查是否是notify_order相关代码
        if 'order.status' in original_line or 'order.isbuy' in original_line:
            return Fix(
                issue=issue,
                fix_type='SEMI_AUTO',
                confidence=0.75,
                original_code=original_line,
                fixed_code='# MOVED to notify_order: ' + original_line.strip(),
                explanation="Code block should be moved to notify_order() method. Commented out for manual move."
            )

        return None

    def get_confidence(self, issue: ValidationIssue) -> float:
        return 0.75


class MissingInitFixer(FixPattern):
    """修复缺失初始化的修复器"""

    def can_fix(self, issue: ValidationIssue) -> bool:
        return issue.category == 'MISSING_INIT'

    def generate_fix(self, issue: ValidationIssue, source_lines: List[str]) -> Optional[Fix]:
        """在__init__末尾添加self.order = None"""

        # 找到__init__方法的结束位置
        init_end_line = self._find_init_end(source_lines, issue.line_number)

        if init_end_line is None:
            return None

        # 获取缩进
        for i in range(issue.line_number - 1, len(source_lines)):
            line = source_lines[i]
            if line.strip() and not line.strip().startswith('#'):
                indent = len(line) - len(line.lstrip())
                break
        else:
            indent = 8  # 默认缩进

        fixed_code = ' ' * indent + 'self.order = None\n' + ' ' * indent + 'self.entry_price = 0.0'

        return Fix(
            issue=issue,
            fix_type='AUTO',
            confidence=0.95,
            original_code='',  # 插入新行
            fixed_code=fixed_code,
            explanation="Added missing self.order and self.entry_price initialization"
        )

    def _find_init_end(self, source_lines: List[str], start_line: int) -> Optional[int]:
        """找到__init__方法的最后一行"""
        in_init = False
        init_indent = 0

        for i, line in enumerate(source_lines):
            if 'def __init__' in line:
                in_init = True
                init_indent = len(line) - len(line.lstrip())
                continue

            if in_init:
                if line.strip() and not line.strip().startswith('#'):
                    current_indent = len(line) - len(line.lstrip())
                    if current_indent <= init_indent:
                        # 遇到下一个方法
                        return i - 1

        return None

    def get_confidence(self, issue: ValidationIssue) -> float:
        return 0.95


class UndefinedVariableFixer(FixPattern):
    """修复未定义变量的修复器"""

    def can_fix(self, issue: ValidationIssue) -> bool:
        return issue.category == 'UNDEFINED_VARIABLE'

    def generate_fix(self, issue: ValidationIssue, source_lines: List[str]) -> Optional[Fix]:
        """建议变量定义"""
        var_name = issue.code_snippet

        # 常见变量名修复建议
        suggestions = {
            'price': 'current_price = self.data.close[0]',
            'order': 'Check if this should be self.order',
            'size': 'size = int(self.broker.get_cash() * 0.95 / price)',
        }

        suggestion = suggestions.get(var_name, f'{var_name} = None  # Define this variable')

        return Fix(
            issue=issue,
            fix_type='MANUAL_ONLY',
            confidence=0.50,
            original_code=issue.code_snippet,
            fixed_code=suggestion,
            explanation=f"Variable '{var_name}' may be undefined. Suggested definition: {suggestion}"
        )

    def get_confidence(self, issue: ValidationIssue) -> float:
        return 0.50


class AutomaticCodeFixer:
    """自动修复引擎主类"""

    def __init__(self):
        self.fixers = [
            OrphanedElifFixer(),
            MethodBoundaryFixer(),
            MissingInitFixer(),
            UndefinedVariableFixer()
        ]
        self.fixes_generated = []
        self.fixes_applied = []

    def analyze_and_fix(self, file_path: Path, auto_apply=False, confidence_threshold=0.80):
        """分析文件并生成/应用修复"""
        print(f"\n{'='*80}")
        print(f"ANALYZING AND FIXING: {file_path.name}")
        print('='*80)

        # Step 1: Validate
        validator = ASTStructureValidator(file_path=file_path)
        issues = validator.validate()

        if not issues:
            print("[OK] No issues found - file is clean!")
            return [], None

        print(f"\nFound {len(issues)} issues")

        # Step 2: Generate fixes
        with open(file_path, 'r', encoding='utf-8') as f:
            source_lines = f.readlines()

        fixes = []
        for issue in issues:
            for fixer in self.fixers:
                if fixer.can_fix(issue):
                    fix = fixer.generate_fix(issue, source_lines)
                    if fix:
                        fixes.append(fix)
                        break

        self.fixes_generated = fixes

        # Step 3: Report fixes
        print(f"\nGenerated {len(fixes)} fix proposals:\n")

        auto_fixes = [f for f in fixes if f.fix_type == 'AUTO' and f.confidence >= confidence_threshold]
        semi_auto = [f for f in fixes if f.fix_type == 'SEMI_AUTO' or (f.fix_type == 'AUTO' and f.confidence < confidence_threshold)]
        manual = [f for f in fixes if f.fix_type == 'MANUAL_ONLY']

        print(f"[GREEN] AUTO-FIXABLE ({len(auto_fixes)}): Confidence >= {confidence_threshold}")
        for i, fix in enumerate(auto_fixes, 1):
            print(f"   {i}. Line {fix.issue.line_number}: {fix.explanation} (conf: {fix.confidence:.2f})")

        print(f"\n[YELLOW] SEMI-AUTO ({len(semi_auto)}): Requires review")
        for i, fix in enumerate(semi_auto, 1):
            print(f"   {i}. Line {fix.issue.line_number}: {fix.explanation} (conf: {fix.confidence:.2f})")

        print(f"\n[RED] MANUAL ONLY ({len(manual)}): Cannot auto-fix safely")
        for i, fix in enumerate(manual, 1):
            print(f"   {i}. Line {fix.issue.line_number}: {fix.explanation} (conf: {fix.confidence:.2f})")

        # Step 4: Apply auto-fixes if requested
        if auto_apply and auto_fixes:
            print(f"\n{'='*80}")
            print(f"APPLYING {len(auto_fixes)} AUTO-FIXES")
            print('='*80)

            fixed_code = self._apply_fixes(source_lines, auto_fixes)

            # Save fixed version
            fixed_path = file_path.with_suffix('.fixed.py')
            with open(fixed_path, 'w', encoding='utf-8') as f:
                f.write(fixed_code)

            print(f"\n[OK] Fixed code saved to: {fixed_path}")
            self.fixes_applied = auto_fixes

            # Validate fixed code
            print("\nValidating fixed code...")
            validator_fixed = ASTStructureValidator(source_code=fixed_code)
            remaining_issues = validator_fixed.validate()

            if len(remaining_issues) < len(issues):
                print(f"[OK] Issues reduced: {len(issues)} → {len(remaining_issues)}")
            else:
                print(f"[WARN]  Issues remain: {len(remaining_issues)}")

            return fixes, fixed_path
        else:
            print(f"\n[INFO] Run with --auto-apply to automatically apply high-confidence fixes")
            return fixes, None

    def _apply_fixes(self, source_lines: List[str], fixes: List[Fix]) -> str:
        """应用修复到源代码"""
        # 按行号倒序排序，从后往前修改避免行号变化
        fixes_sorted = sorted(fixes, key=lambda f: f.issue.line_number, reverse=True)

        modified_lines = source_lines.copy()

        for fix in fixes_sorted:
            line_idx = fix.issue.line_number - 1

            if fix.fixed_code == '':
                # 删除行
                del modified_lines[line_idx]
                fix.applied = True
            elif fix.original_code == '':
                # 插入行
                modified_lines.insert(line_idx, fix.fixed_code + '\n')
                fix.applied = True
            else:
                # 替换行
                modified_lines[line_idx] = fix.fixed_code + '\n'
                fix.applied = True

        return ''.join(modified_lines)

    def generate_report(self, output_path: Path):
        """生成修复报告"""
        report = {
            'date': datetime.now().isoformat(),
            'total_fixes_generated': len(self.fixes_generated),
            'total_fixes_applied': len(self.fixes_applied),
            'fixes': [
                {
                    'line': fix.issue.line_number,
                    'type': fix.fix_type,
                    'confidence': fix.confidence,
                    'category': fix.issue.category,
                    'explanation': fix.explanation,
                    'applied': fix.applied
                }
                for fix in self.fixes_generated
            ]
        }

        with open(output_path, 'w') as f:
            json.dump(report, f, indent=2)

        print(f"\nReport saved: {output_path}")


def main():
    """命令行接口"""
    import argparse

    parser = argparse.ArgumentParser(description='Automatic Code Fixer for LLM-generated strategies')
    parser.add_argument('file', type=Path, help='Python file to fix')
    parser.add_argument('--auto-apply', action='store_true', help='Automatically apply high-confidence fixes')
    parser.add_argument('--confidence', type=float, default=0.80, help='Confidence threshold for auto-apply (default: 0.80)')
    parser.add_argument('--report', type=Path, help='Path to save JSON report')

    args = parser.parse_args()

    if not args.file.exists():
        print(f"Error: File not found: {args.file}")
        return 1

    fixer = AutomaticCodeFixer()
    fixes, fixed_path = fixer.analyze_and_fix(
        args.file,
        auto_apply=args.auto_apply,
        confidence_threshold=args.confidence
    )

    if args.report:
        fixer.generate_report(args.report)

    print(f"\n{'='*80}")
    print("SUMMARY")
    print('='*80)
    print(f"Total fixes generated: {len(fixes)}")
    print(f"Auto-applied: {len(fixer.fixes_applied)}")
    print(f"Remaining for manual review: {len(fixes) - len(fixer.fixes_applied)}")

    if fixed_path:
        print(f"\n[OK] Fixed file: {fixed_path}")
        print("   Next step: Review and test the fixed code")

    return 0


if __name__ == '__main__':
    import sys
    sys.exit(main())
