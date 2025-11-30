#!/usr/bin/env python3
"""
Day 48: Auto-Fix Trading Strategies
根据AST验证结果自动修复常见错误
"""

import re
import ast
from pathlib import Path
from typing import List, Dict, Tuple
import shutil


class StrategyAutoFixer:
    """自动修复交易策略代码中的常见错误"""

    def __init__(self, backup_dir: Path = None):
        self.backup_dir = backup_dir
        self.fixes_applied = []

    def fix_file(self, file_path: Path) -> Dict:
        """修复单个文件并返回修复报告"""
        print(f"\n{'='*80}")
        print(f"Fixing: {file_path.name}")
        print('='*80)

        # 备份原文件
        if self.backup_dir:
            self.backup_dir.mkdir(parents=True, exist_ok=True)
            backup_path = self.backup_dir / file_path.name
            shutil.copy2(file_path, backup_path)

        # 读取文件
        with open(file_path, 'r', encoding='utf-8') as f:
            original = f.read()

        # 应用各种修复
        fixed_code = original
        fixes = []

        # 1. 修复缺失的import语句
        fixed_code, import_fixes = self.fix_missing_imports(fixed_code)
        fixes.extend(import_fixes)

        # 2. 修复缩进问题（特别是elif/else）
        fixed_code, indent_fixes = self.fix_indentation(fixed_code)
        fixes.extend(indent_fixes)

        # 3. 修复缺失的self.order初始化
        fixed_code, order_fixes = self.fix_missing_order_init(fixed_code)
        fixes.extend(order_fixes)

        # 4. 添加pending order检查（可选）
        # fixed_code, check_fixes = self.add_order_checks(fixed_code)
        # fixes.extend(check_fixes)

        # 保存修复后的文件
        if fixed_code != original:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(fixed_code)

            # 验证语法
            try:
                compile(fixed_code, str(file_path), 'exec')
                status = "✅ SUCCESS"
            except SyntaxError as e:
                status = f"⚠️  PARTIAL (SyntaxError: {e})"
        else:
            status = "⏭️  NO CHANGES"

        report = {
            'file': file_path.name,
            'status': status,
            'fixes': fixes,
            'fix_count': len(fixes)
        }

        print(f"Status: {status}")
        print(f"Fixes Applied: {len(fixes)}")
        for fix in fixes:
            print(f"  - {fix}")

        return report

    def fix_missing_imports(self, code: str) -> Tuple[str, List[str]]:
        """修复缺失的import语句"""
        fixes = []
        lines = code.split('\n')

        # 检查是否已有相关import
        has_bt = any('import backtrader' in line for line in lines)
        has_btind = any('backtrader.indicators as btind' in line for line in lines)

        # 检查代码中是否使用btind
        uses_btind = 'btind.' in code

        if not has_bt:
            # 找到第一个非注释、非空行
            insert_idx = 0
            for i, line in enumerate(lines):
                stripped = line.strip()
                if stripped and not stripped.startswith('#') and not stripped.startswith('"""'):
                    insert_idx = i
                    break

            lines.insert(insert_idx, 'import backtrader as bt')
            fixes.append('Added: import backtrader as bt')

        if uses_btind and not has_btind:
            # 在backtrader import后添加
            for i, line in enumerate(lines):
                if 'import backtrader' in line:
                    lines.insert(i + 1, 'import backtrader.indicators as btind')
                    fixes.append('Added: import backtrader.indicators as btind')
                    break

        return '\n'.join(lines), fixes

    def fix_indentation(self, code: str) -> Tuple[str, List[str]]:
        """修复缩进问题，特别是elif/else语句"""
        fixes = []
        lines = code.split('\n')
        fixed_lines = []

        i = 0
        while i < len(lines):
            line = lines[i]
            stripped = line.strip()

            # 检测elif/else可能的缩进错误
            if stripped.startswith(('elif ', 'else:')):
                # 找到前面的if语句
                if_indent = None
                for j in range(i - 1, -1, -1):
                    prev_stripped = lines[j].strip()
                    if prev_stripped.startswith('if '):
                        # 计算if的缩进
                        if_indent = len(lines[j]) - len(lines[j].lstrip())
                        break

                # 检查当前行的缩进
                current_indent = len(line) - len(line.lstrip())

                if if_indent is not None and current_indent != if_indent:
                    # 修复缩进
                    fixed_line = ' ' * if_indent + stripped
                    fixed_lines.append(fixed_line)
                    fixes.append(f'Line {i+1}: Fixed {stripped.split()[0]} indentation ({current_indent} -> {if_indent})')
                else:
                    fixed_lines.append(line)
            else:
                fixed_lines.append(line)

            i += 1

        return '\n'.join(fixed_lines), fixes

    def fix_missing_order_init(self, code: str) -> Tuple[str, List[str]]:
        """修复__init__方法中缺失的self.order = None"""
        fixes = []

        try:
            tree = ast.parse(code)
        except SyntaxError:
            return code, fixes

        # 查找Strategy类及其__init__方法
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                # 检查是否是Strategy子类
                is_strategy = any(
                    (isinstance(base, ast.Name) and 'Strategy' in base.id) or
                    (isinstance(base, ast.Attribute) and base.attr == 'Strategy')
                    for base in node.bases
                )

                if is_strategy:
                    # 查找__init__方法
                    for item in node.body:
                        if isinstance(item, ast.FunctionDef) and item.name == '__init__':
                            # 检查是否已有self.order = None
                            has_order_init = False
                            for stmt in ast.walk(item):
                                if isinstance(stmt, ast.Assign):
                                    for target in stmt.targets:
                                        if (isinstance(target, ast.Attribute) and
                                            isinstance(target.value, ast.Name) and
                                            target.value.id == 'self' and
                                            target.attr == 'order'):
                                            has_order_init = True
                                            break

                            if not has_order_init:
                                # 添加self.order = None
                                # 找到__init__方法的最后一行
                                init_line = item.lineno
                                lines = code.split('\n')

                                # 找到__init__定义行
                                for i in range(init_line - 1, len(lines)):
                                    if 'def __init__' in lines[i]:
                                        # 计算缩进
                                        next_line_idx = i + 1
                                        if next_line_idx < len(lines):
                                            # 找到第一个有内容的行来确定缩进
                                            while next_line_idx < len(lines) and not lines[next_line_idx].strip():
                                                next_line_idx += 1

                                            if next_line_idx < len(lines):
                                                indent = len(lines[next_line_idx]) - len(lines[next_line_idx].lstrip())
                                                # 在第一个实际语句前插入
                                                lines.insert(next_line_idx, ' ' * indent + 'self.order = None')
                                                code = '\n'.join(lines)
                                                fixes.append(f'Added: self.order = None in __init__ of {node.name}')
                                        break

        return code, fixes

    def add_order_checks(self, code: str) -> Tuple[str, List[str]]:
        """添加pending order检查（可选）"""
        fixes = []

        try:
            tree = ast.parse(code)
        except SyntaxError:
            return code, fixes

        # 查找next方法并添加if self.order: return
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                for item in node.body:
                    if isinstance(item, ast.FunctionDef) and item.name == 'next':
                        # 检查是否已有order检查
                        has_order_check = False
                        if item.body:
                            first_stmt = item.body[0]
                            if isinstance(first_stmt, ast.If):
                                # 简单检查是否包含self.order
                                has_order_check = 'self.order' in ast.unparse(first_stmt.test)

                        if not has_order_check:
                            next_line = item.lineno
                            lines = code.split('\n')

                            for i in range(next_line - 1, len(lines)):
                                if 'def next' in lines[i]:
                                    # 找到下一个非空行的缩进
                                    next_line_idx = i + 1
                                    while next_line_idx < len(lines) and not lines[next_line_idx].strip():
                                        next_line_idx += 1

                                    if next_line_idx < len(lines):
                                        indent = len(lines[next_line_idx]) - len(lines[next_line_idx].lstrip())
                                        lines.insert(next_line_idx, ' ' * indent + 'if self.order:')
                                        lines.insert(next_line_idx + 1, ' ' * (indent + 4) + 'return')
                                        lines.insert(next_line_idx + 2, '')
                                        code = '\n'.join(lines)
                                        fixes.append(f'Added: pending order check in next() of {node.name}')
                                    break

        return code, fixes


def main():
    """批量修复策略文件"""
    import sys
    import json
    from datetime import datetime

    if len(sys.argv) < 2:
        print("Usage: python day48_auto_fix_strategies.py <directory>")
        print("Example: python day48_auto_fix_strategies.py experiment4_trading_extended/baseline/")
        sys.exit(1)

    target_dir = Path(sys.argv[1])
    if not target_dir.exists():
        print(f"Error: Directory not found: {target_dir}")
        sys.exit(1)

    # 创建备份目录
    backup_dir = target_dir.parent / f"{target_dir.name}_backup"

    print("="*80)
    print("Auto-Fix Trading Strategies")
    print("="*80)
    print(f"Target: {target_dir}")
    print(f"Backup: {backup_dir}")
    print()

    # 获取所有Python文件
    py_files = sorted(target_dir.glob("*.py"))
    print(f"Found {len(py_files)} Python files\n")

    # 创建fixer
    fixer = StrategyAutoFixer(backup_dir=backup_dir)

    # 批量修复
    all_reports = []
    for py_file in py_files:
        report = fixer.fix_file(py_file)
        all_reports.append(report)

    # 汇总统计
    print("\n" + "="*80)
    print("SUMMARY")
    print("="*80)

    success = sum(1 for r in all_reports if '✅' in r['status'])
    partial = sum(1 for r in all_reports if '⚠️' in r['status'])
    no_change = sum(1 for r in all_reports if '⏭️' in r['status'])
    total_fixes = sum(r['fix_count'] for r in all_reports)

    print(f"\nFiles Processed: {len(all_reports)}")
    print(f"  ✅ Success: {success}")
    print(f"  ⚠️  Partial: {partial}")
    print(f"  ⏭️  No Changes: {no_change}")
    print(f"\nTotal Fixes Applied: {total_fixes}")

    # 按修复类型统计
    fix_types = {}
    for report in all_reports:
        for fix in report['fixes']:
            fix_type = fix.split(':')[0]
            fix_types[fix_type] = fix_types.get(fix_type, 0) + 1

    if fix_types:
        print("\nFix Types:")
        for fix_type, count in sorted(fix_types.items(), key=lambda x: -x[1]):
            print(f"  {fix_type}: {count}")

    # 保存详细报告
    report_file = target_dir.parent / f"{target_dir.name}_fix_report.json"
    with open(report_file, 'w') as f:
        json.dump({
            'date': datetime.now().isoformat(),
            'target_dir': str(target_dir),
            'backup_dir': str(backup_dir),
            'total_files': len(all_reports),
            'success': success,
            'partial': partial,
            'no_change': no_change,
            'total_fixes': total_fixes,
            'fix_types': fix_types,
            'details': all_reports
        }, f, indent=2)

    print(f"\nDetailed report saved: {report_file}")
    print(f"Backups saved to: {backup_dir}")
    print("="*80)


if __name__ == '__main__':
    main()
