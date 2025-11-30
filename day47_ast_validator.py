#!/usr/bin/env python3
"""
Day 47: AST Structure Validator
自动化结构验证工具 - 检测LLM生成代码的结构性错误

解决Phase 3发现的关键问题：语法检查通过但代码无法运行

主要检测:
1. 方法边界混淆 (Method Boundary Confusion)
2. 孤立的elif/else语句 (Orphaned elif/else)
3. 变量引用完整性 (Variable Reference)
4. 类结构完整性 (Class Structure)
"""

import ast
import sys
from pathlib import Path
from typing import List, Dict, Tuple
from dataclasses import dataclass
from collections import defaultdict
import json
from datetime import datetime


@dataclass
class ValidationIssue:
    """验证问题数据结构"""
    severity: str  # 'CRITICAL', 'HIGH', 'MEDIUM', 'LOW'
    category: str  # 'METHOD_BOUNDARY', 'ORPHANED_STATEMENT', 'VARIABLE_REF', etc.
    line_number: int
    message: str
    code_snippet: str = ""
    fix_suggestion: str = ""


class MethodBoundaryChecker(ast.NodeVisitor):
    """检测方法边界混淆"""

    def __init__(self, source_lines):
        self.source_lines = source_lines
        self.issues = []
        self.current_function = None

    def visit_FunctionDef(self, node):
        """访问函数定义"""
        old_function = self.current_function
        self.current_function = node.name

        # 检查函数体中的elif/else是否在if块外
        self.check_orphaned_elif_else(node)

        self.generic_visit(node)
        self.current_function = old_function

    def check_orphaned_elif_else(self, func_node):
        """检测孤立的elif/else语句"""
        for stmt in ast.walk(func_node):
            if isinstance(stmt, ast.If):
                # 检查是否有elif但没有正确的结构
                self.validate_if_structure(stmt, func_node.name)

    def validate_if_structure(self, if_node, func_name):
        """验证if-elif-else结构完整性"""
        # 检查orelse链
        current = if_node
        has_proper_if = True

        while hasattr(current, 'orelse') and current.orelse:
            orelse = current.orelse
            if len(orelse) == 1 and isinstance(orelse[0], ast.If):
                # 这是elif情况
                current = orelse[0]
            elif len(orelse) > 0:
                # 这是else情况
                break
            else:
                break

    def visit_If(self, node):
        """检测孤立的elif (这在AST中表现为没有test的If)"""
        # 注意：elif在AST中实际上是嵌套的If节点
        # 真正的问题是在__init__等方法中直接出现elif/else关键字

        # 通过行号检查是否在正确的上下文中
        if self.current_function and node.lineno:
            line_content = self.source_lines[node.lineno - 1].strip()

            # 检测直接以elif开头的行（这不应该在AST中出现，但在源代码中会）
            if line_content.startswith('elif'):
                # 查找前面是否有if
                has_matching_if = self.find_matching_if(node.lineno)
                if not has_matching_if:
                    self.issues.append(ValidationIssue(
                        severity='CRITICAL',
                        category='METHOD_BOUNDARY',
                        line_number=node.lineno,
                        message=f"Orphaned 'elif' statement in function '{self.current_function}'",
                        code_snippet=line_content,
                        fix_suggestion="Remove or convert to 'if', or ensure proper if-elif chain"
                    ))

        self.generic_visit(node)

    def find_matching_if(self, elif_line):
        """向上查找匹配的if语句"""
        # 简化版：检查前面几行是否有if
        for i in range(max(0, elif_line - 10), elif_line - 1):
            if i < len(self.source_lines):
                line = self.source_lines[i].strip()
                if line.startswith('if ') and not line.startswith('elif'):
                    return True
        return False


class OrphanedStatementChecker(ast.NodeVisitor):
    """检测孤立的elif/else语句（通过文本分析）"""

    def __init__(self, source_lines):
        self.source_lines = source_lines
        self.issues = []

    def check_source(self):
        """通过文本分析检测孤立语句"""
        in_function = False
        function_name = ""
        indent_stack = []
        last_if_indent = None

        for line_num, line in enumerate(self.source_lines, start=1):
            stripped = line.lstrip()
            indent = len(line) - len(stripped)

            # 追踪函数定义
            if stripped.startswith('def '):
                in_function = True
                function_name = stripped.split('(')[0].replace('def ', '')
                indent_stack = [indent]
                last_if_indent = None

            # 检测elif/else
            if stripped.startswith('elif ') or stripped.startswith('else:'):
                # 检查是否在函数定义层级（不应该直接在函数体第一层）
                if in_function and last_if_indent is None:
                    self.issues.append(ValidationIssue(
                        severity='CRITICAL',
                        category='ORPHANED_STATEMENT',
                        line_number=line_num,
                        message=f"Orphaned '{stripped.split()[0]}' in function '{function_name}' - no matching 'if'",
                        code_snippet=stripped[:80],
                        fix_suggestion="Move to appropriate if-elif-else block or convert to 'if'"
                    ))
                elif last_if_indent is not None and indent != last_if_indent:
                    self.issues.append(ValidationIssue(
                        severity='HIGH',
                        category='INDENT_MISMATCH',
                        line_number=line_num,
                        message=f"Indentation mismatch for '{stripped.split()[0]}' statement",
                        code_snippet=stripped[:80],
                        fix_suggestion=f"Adjust indent to match 'if' at column {last_if_indent}"
                    ))

            # 追踪if语句
            if stripped.startswith('if '):
                last_if_indent = indent


class VariableReferenceChecker(ast.NodeVisitor):
    """检测变量引用完整性"""

    def __init__(self):
        self.issues = []
        self.defined_vars = defaultdict(set)  # scope -> set of variables
        self.current_scope = 'module'
        self.scope_stack = ['module']

    def visit_FunctionDef(self, node):
        """进入函数作用域"""
        old_scope = self.current_scope
        self.current_scope = f"function.{node.name}"
        self.scope_stack.append(self.current_scope)

        # 添加参数到作用域
        for arg in node.args.args:
            self.defined_vars[self.current_scope].add(arg.arg)

        self.generic_visit(node)

        self.scope_stack.pop()
        self.current_scope = old_scope

    def visit_Assign(self, node):
        """追踪变量赋值"""
        for target in node.targets:
            if isinstance(target, ast.Name):
                self.defined_vars[self.current_scope].add(target.id)
            elif isinstance(target, ast.Attribute):
                # self.var = value
                if isinstance(target.value, ast.Name):
                    if target.value.id == 'self':
                        self.defined_vars[self.current_scope].add(f"self.{target.attr}")

        self.generic_visit(node)

    def visit_Name(self, node):
        """检查变量使用"""
        if isinstance(node.ctx, ast.Load):  # 读取变量
            var_name = node.id

            # 检查是否在当前作用域或父作用域中定义
            found = False
            for scope in reversed(self.scope_stack):
                if var_name in self.defined_vars[scope]:
                    found = True
                    break

            # 检查builtins和common names
            builtins_and_common = {
                'True', 'False', 'None', 'self', 'range', 'len', 'str', 'int',
                'float', 'list', 'dict', 'set', 'tuple', 'print', 'type', 'isinstance',
                'abs', 'all', 'any', 'bin', 'bool', 'bytes', 'callable', 'chr',
                'classmethod', 'compile', 'complex', 'delattr', 'dir', 'divmod',
                'enumerate', 'eval', 'exec', 'filter', 'format', 'frozenset',
                'getattr', 'globals', 'hasattr', 'hash', 'help', 'hex', 'id',
                'input', 'iter', 'locals', 'map', 'max', 'memoryview', 'min',
                'next', 'object', 'oct', 'open', 'ord', 'pow', 'property',
                'repr', 'reversed', 'round', 'setattr', 'slice', 'sorted',
                'staticmethod', 'sum', 'super', 'vars', 'zip', 'Exception',
                # Common imported modules for trading strategies
                'bt', 'backtrader', 'pd', 'pandas', 'np', 'numpy',
                'logging', 'datetime', 'json', 'os', 'sys', 'math', 'time',
                'pathlib', 'Path', 're', 'collections', 'itertools', 'functools',
                # Common class names that may be referenced
                'Strategy', 'Cerebro', 'Order', 'Trade', 'Position',
                'DataFrame', 'Series', 'ndarray',
                # Common strategy class names (LLM-generated)
                'logger'
            }

            if not found and var_name not in builtins_and_common:
                # 可能的未定义变量使用
                if not var_name.startswith('_'):  # 忽略私有变量
                    self.issues.append(ValidationIssue(
                        severity='MEDIUM',
                        category='UNDEFINED_VARIABLE',
                        line_number=node.lineno,
                        message=f"Potentially undefined variable: '{var_name}'",
                        code_snippet=var_name,
                        fix_suggestion=f"Define '{var_name}' before use or check spelling"
                    ))

        self.generic_visit(node)


class ClassStructureChecker(ast.NodeVisitor):
    """检测类结构完整性（针对backtrader.Strategy）"""

    def __init__(self):
        self.issues = []
        self.strategy_classes = []

    def visit_ClassDef(self, node):
        """检查类定义"""
        # 检查是否继承自bt.Strategy
        for base in node.bases:
            if isinstance(base, ast.Attribute):
                if base.attr == 'Strategy':
                    self.strategy_classes.append(node.name)
                    self.check_strategy_structure(node)

        self.generic_visit(node)

    def check_strategy_structure(self, class_node):
        """检查Strategy类的必要方法"""
        required_methods = {'__init__', 'next'}
        found_methods = set()

        for item in class_node.body:
            if isinstance(item, ast.FunctionDef):
                found_methods.add(item.name)

                # 检查__init__方法
                if item.name == '__init__':
                    self.check_init_method(item, class_node.name)

                # 检查next方法
                if item.name == 'next':
                    self.check_next_method(item, class_node.name)

        # 检查缺失方法
        missing = required_methods - found_methods
        if missing:
            self.issues.append(ValidationIssue(
                severity='HIGH',
                category='MISSING_METHOD',
                line_number=class_node.lineno,
                message=f"Strategy class '{class_node.name}' missing required methods: {missing}",
                code_snippet="",
                fix_suggestion=f"Add methods: {', '.join(missing)}"
            ))

    def check_init_method(self, func_node, class_name):
        """检查__init__方法结构"""
        # 检查是否初始化了self.order
        has_order_init = False
        has_entry_price = False

        for stmt in ast.walk(func_node):
            if isinstance(stmt, ast.Assign):
                for target in stmt.targets:
                    if isinstance(target, ast.Attribute):
                        if isinstance(target.value, ast.Name) and target.value.id == 'self':
                            if target.attr == 'order':
                                has_order_init = True
                            if target.attr == 'entry_price':
                                has_entry_price = True

        if not has_order_init:
            self.issues.append(ValidationIssue(
                severity='MEDIUM',
                category='MISSING_INIT',
                line_number=func_node.lineno,
                message=f"__init__ in '{class_name}' should initialize self.order",
                code_snippet="",
                fix_suggestion="Add: self.order = None"
            ))

    def check_next_method(self, func_node, class_name):
        """检查next方法是否有正确的逻辑"""
        # 简单检查：是否有if self.order检查
        has_order_check = False

        for stmt in ast.walk(func_node):
            if isinstance(stmt, ast.If):
                # 检查test是否涉及self.order
                test_code = ast.unparse(stmt.test) if hasattr(ast, 'unparse') else ""
                if 'self.order' in test_code:
                    has_order_check = True
                    break

        if not has_order_check:
            self.issues.append(ValidationIssue(
                severity='LOW',
                category='MISSING_CHECK',
                line_number=func_node.lineno,
                message=f"next() in '{class_name}' should check for pending orders",
                code_snippet="",
                fix_suggestion="Add: if self.order: return"
            ))


class ASTStructureValidator:
    """主验证器"""

    def __init__(self, file_path=None, source_code=None):
        if file_path:
            self.file_path = Path(file_path)
            with open(file_path, 'r', encoding='utf-8') as f:
                self.source_code = f.read()
        elif source_code:
            self.file_path = None
            self.source_code = source_code
        else:
            raise ValueError("Must provide either file_path or source_code")

        self.source_lines = self.source_code.splitlines()
        self.issues = []
        self.tree = None

    def parse(self):
        """解析代码"""
        try:
            self.tree = ast.parse(self.source_code)
            return True, None
        except SyntaxError as e:
            return False, str(e)

    def validate(self):
        """执行所有验证检查"""
        # 1. 语法检查
        success, error = self.parse()
        if not success:
            self.issues.append(ValidationIssue(
                severity='CRITICAL',
                category='SYNTAX_ERROR',
                line_number=0,
                message=f"Syntax error: {error}",
                code_snippet="",
                fix_suggestion="Fix syntax errors first"
            ))
            return self.issues

        # 2. 方法边界检查
        boundary_checker = MethodBoundaryChecker(self.source_lines)
        boundary_checker.visit(self.tree)
        self.issues.extend(boundary_checker.issues)

        # 3. 孤立语句检查（文本分析）
        orphaned_checker = OrphanedStatementChecker(self.source_lines)
        orphaned_checker.check_source()
        self.issues.extend(orphaned_checker.issues)

        # 4. 变量引用检查
        var_checker = VariableReferenceChecker()
        var_checker.visit(self.tree)
        self.issues.extend(var_checker.issues)

        # 5. 类结构检查
        class_checker = ClassStructureChecker()
        class_checker.visit(self.tree)
        self.issues.extend(class_checker.issues)

        return self.issues

    def get_report(self):
        """生成验证报告"""
        total = len(self.issues)
        by_severity = defaultdict(int)
        by_category = defaultdict(int)

        for issue in self.issues:
            by_severity[issue.severity] += 1
            by_category[issue.category] += 1

        report = {
            'file': str(self.file_path) if self.file_path else 'source_code',
            'total_issues': total,
            'by_severity': dict(by_severity),
            'by_category': dict(by_category),
            'issues': [
                {
                    'severity': issue.severity,
                    'category': issue.category,
                    'line': issue.line_number,
                    'message': issue.message,
                    'snippet': issue.code_snippet,
                    'suggestion': issue.fix_suggestion
                }
                for issue in self.issues
            ]
        }

        return report

    def print_report(self):
        """打印可读的报告"""
        print("=" * 80)
        print("AST STRUCTURE VALIDATION REPORT")
        print("=" * 80)
        print(f"File: {self.file_path if self.file_path else 'source_code'}")
        print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print()

        if not self.issues:
            print("[OK] No structural issues found!")
            return

        # 按严重性分组
        by_severity = defaultdict(list)
        for issue in self.issues:
            by_severity[issue.severity].append(issue)

        severity_order = ['CRITICAL', 'HIGH', 'MEDIUM', 'LOW']
        severity_icons = {
            'CRITICAL': '[RED]',
            'HIGH': '🟠',
            'MEDIUM': '[YELLOW]',
            'LOW': '[GREEN]'
        }

        for severity in severity_order:
            if severity in by_severity:
                issues = by_severity[severity]
                print(f"\n{severity_icons[severity]} {severity} Issues ({len(issues)})")
                print("-" * 80)

                for i, issue in enumerate(issues, 1):
                    print(f"\n{i}. Line {issue.line_number}: {issue.message}")
                    print(f"   Category: {issue.category}")
                    if issue.code_snippet:
                        print(f"   Code: {issue.code_snippet}")
                    if issue.fix_suggestion:
                        print(f"   Fix: {issue.fix_suggestion}")

        # 摘要
        print("\n" + "=" * 80)
        print("SUMMARY")
        print("=" * 80)
        print(f"Total Issues: {len(self.issues)}")
        for severity in severity_order:
            count = len(by_severity[severity])
            if count > 0:
                print(f"{severity_icons[severity]} {severity}: {count}")


def main():
    """命令行接口"""
    if len(sys.argv) < 2:
        print("Usage: python day47_ast_validator.py <file_path>")
        print("       python day47_ast_validator.py <directory> (validates all .py files)")
        sys.exit(1)

    path = Path(sys.argv[1])

    if path.is_file():
        # 验证单个文件
        validator = ASTStructureValidator(file_path=path)
        validator.validate()
        validator.print_report()

        # 保存JSON报告
        report_path = path.with_suffix('.validation_report.json')
        with open(report_path, 'w') as f:
            json.dump(validator.get_report(), f, indent=2)
        print(f"\nJSON report saved: {report_path}")

    elif path.is_dir():
        # 批量验证目录中的所有.py文件
        py_files = list(path.glob('*.py'))
        print(f"Found {len(py_files)} Python files in {path}")
        print()

        all_reports = []

        for py_file in py_files:
            print(f"\n{'=' * 80}")
            print(f"Validating: {py_file.name}")
            print('=' * 80)

            validator = ASTStructureValidator(file_path=py_file)
            validator.validate()
            validator.print_report()

            all_reports.append(validator.get_report())

        # 保存批量报告
        batch_report_path = path / 'batch_validation_report.json'
        with open(batch_report_path, 'w') as f:
            json.dump({
                'date': datetime.now().isoformat(),
                'total_files': len(py_files),
                'reports': all_reports
            }, f, indent=2)
        print(f"\n\nBatch report saved: {batch_report_path}")

    else:
        print(f"Error: {path} is not a valid file or directory")
        sys.exit(1)


if __name__ == '__main__':
    main()
