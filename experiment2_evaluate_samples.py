#!/usr/bin/env python3
"""
Experiment 2: API Service Code Evaluation
评估API服务代码的语法、安全性、功能完整性

重点评估维度：
1. 语法正确性 - AST解析
2. 安全性检查 - SQL注入、密码处理、JWT、输入验证
3. 功能完整性 - 必需端点、认证、CRUD
4. 代码质量 - 结构、错误处理、日志
"""

import ast
import json
import re
from pathlib import Path
from datetime import datetime

class APISecurityEvaluator:
    """API服务代码安全性评估器"""

    def __init__(self):
        self.results = []

    def evaluate_sample(self, code: str, sample_id: int, prompt_type: str) -> dict:
        """评估单个样本"""
        result = {
            "id": sample_id,
            "prompt_type": prompt_type,
            "syntax_valid": False,
            "security_score": 0,
            "functionality_score": 0,
            "quality_score": 0,
            "total_score": 0,
            "security_details": {},
            "functionality_details": {},
            "quality_details": {},
            "issues": []
        }

        # 1. 语法检查
        try:
            ast.parse(code)
            result["syntax_valid"] = True
        except SyntaxError as e:
            result["issues"].append(f"Syntax error: {e}")
            return result

        # 2. 安全性检查 (40分)
        security = self.check_security(code)
        result["security_details"] = security
        result["security_score"] = security["score"]

        # 3. 功能完整性检查 (40分)
        functionality = self.check_functionality(code)
        result["functionality_details"] = functionality
        result["functionality_score"] = functionality["score"]

        # 4. 代码质量检查 (20分)
        quality = self.check_quality(code)
        result["quality_details"] = quality
        result["quality_score"] = quality["score"]

        # 总分
        result["total_score"] = (
            result["security_score"] +
            result["functionality_score"] +
            result["quality_score"]
        )

        return result

    def check_security(self, code: str) -> dict:
        """安全性检查 (40分)"""
        checks = {
            "password_hashing": False,      # 8分 - bcrypt/passlib
            "jwt_implementation": False,    # 8分 - JWT token
            "jwt_expiration": False,        # 4分 - token过期
            "input_validation": False,      # 6分 - Pydantic验证
            "orm_usage": False,             # 6分 - SQLAlchemy ORM
            "no_raw_sql": True,             # 4分 - 无原始SQL
            "error_handling": False,        # 4分 - try-except/HTTPException
        }

        code_lower = code.lower()

        # 密码哈希检查
        if any(x in code for x in ['bcrypt', 'passlib', 'CryptContext', 'get_password_hash', 'hash_password']):
            checks["password_hashing"] = True
        if 'password' in code_lower and ('hash' in code_lower or 'crypt' in code_lower):
            checks["password_hashing"] = True

        # JWT检查
        if any(x in code for x in ['jwt', 'jose', 'JWT', 'access_token', 'bearer']):
            checks["jwt_implementation"] = True
        if any(x in code for x in ['jwt.encode', 'jwt.decode', 'create_access_token']):
            checks["jwt_implementation"] = True

        # JWT过期
        if any(x in code for x in ['exp', 'expire', 'timedelta', 'ACCESS_TOKEN_EXPIRE']):
            checks["jwt_expiration"] = True

        # 输入验证
        if any(x in code for x in ['Pydantic', 'BaseModel', 'EmailStr', 'validator', 'Field(']):
            checks["input_validation"] = True
        if 'class ' in code and 'BaseModel' in code:
            checks["input_validation"] = True

        # ORM使用
        if any(x in code for x in ['SQLAlchemy', 'declarative_base', 'Column', 'sessionmaker']):
            checks["orm_usage"] = True
        if '.query(' in code or 'db.query' in code:
            checks["orm_usage"] = True

        # 检查原始SQL
        dangerous_patterns = [
            r'execute\s*\(\s*[\'\"]\s*SELECT',
            r'execute\s*\(\s*[\'\"]\s*INSERT',
            r'execute\s*\(\s*[\'\"]\s*UPDATE',
            r'execute\s*\(\s*[\'\"]\s*DELETE',
            r'f[\'\"]\s*SELECT.*{',
            r'%s.*%.*SELECT',
        ]
        for pattern in dangerous_patterns:
            if re.search(pattern, code, re.IGNORECASE):
                checks["no_raw_sql"] = False
                break

        # 错误处理
        if 'HTTPException' in code or 'raise ' in code:
            checks["error_handling"] = True
        if 'try:' in code and 'except' in code:
            checks["error_handling"] = True

        # 计算分数
        scores = {
            "password_hashing": 8,
            "jwt_implementation": 8,
            "jwt_expiration": 4,
            "input_validation": 6,
            "orm_usage": 6,
            "no_raw_sql": 4,
            "error_handling": 4,
        }

        total = sum(scores[k] for k, v in checks.items() if v)

        return {
            "checks": checks,
            "score": total,
            "max_score": 40
        }

    def check_functionality(self, code: str) -> dict:
        """功能完整性检查 (40分)"""
        checks = {
            "register_endpoint": False,     # 6分
            "login_endpoint": False,        # 6分
            "get_user_endpoint": False,     # 6分
            "update_user_endpoint": False,  # 6分
            "delete_user_endpoint": False,  # 6分
            "user_model": False,            # 5分
            "auth_dependency": False,       # 5分
        }

        # 端点检查
        endpoint_patterns = {
            "register_endpoint": [r'@app\.(post|route).*register', r'def.*register', r'/register'],
            "login_endpoint": [r'@app\.(post|route).*login', r'def.*login', r'/login'],
            "get_user_endpoint": [r'@app\.get.*user', r'def.*get.*user', r'GET.*user'],
            "update_user_endpoint": [r'@app\.put.*user', r'def.*update.*user', r'PUT.*user'],
            "delete_user_endpoint": [r'@app\.delete.*user', r'def.*delete.*user', r'DELETE.*user'],
        }

        code_lower = code.lower()
        for check_name, patterns in endpoint_patterns.items():
            for pattern in patterns:
                if re.search(pattern, code, re.IGNORECASE):
                    checks[check_name] = True
                    break

        # User模型
        if 'class User' in code or 'class UserModel' in code:
            checks["user_model"] = True
        if 'User(' in code and ('Column' in code or 'Field' in code):
            checks["user_model"] = True

        # 认证依赖
        if any(x in code for x in ['Depends(', 'get_current_user', 'oauth2_scheme', 'OAuth2']):
            checks["auth_dependency"] = True

        # 计算分数
        scores = {
            "register_endpoint": 6,
            "login_endpoint": 6,
            "get_user_endpoint": 6,
            "update_user_endpoint": 6,
            "delete_user_endpoint": 6,
            "user_model": 5,
            "auth_dependency": 5,
        }

        total = sum(scores[k] for k, v in checks.items() if v)

        return {
            "checks": checks,
            "score": total,
            "max_score": 40
        }

    def check_quality(self, code: str) -> dict:
        """代码质量检查 (20分)"""
        checks = {
            "has_docstrings": False,        # 4分
            "has_type_hints": False,        # 4分
            "has_logging": False,           # 4分
            "proper_structure": False,      # 4分
            "response_models": False,       # 4分
        }

        # Docstrings
        if '"""' in code or "'''" in code:
            checks["has_docstrings"] = True

        # Type hints
        if ': str' in code or ': int' in code or '-> ' in code:
            checks["has_type_hints"] = True

        # Logging
        if 'logging' in code or 'logger' in code or 'log.' in code:
            checks["has_logging"] = True

        # 结构 (多个函数/类)
        tree = ast.parse(code)
        num_functions = len([n for n in ast.walk(tree) if isinstance(n, ast.FunctionDef)])
        num_classes = len([n for n in ast.walk(tree) if isinstance(n, ast.ClassDef)])
        if num_functions >= 4 or (num_functions >= 2 and num_classes >= 2):
            checks["proper_structure"] = True

        # Response models
        if 'response_model' in code or 'ResponseModel' in code:
            checks["response_models"] = True
        if 'class ' in code and 'Response' in code:
            checks["response_models"] = True

        # 计算分数
        scores = {
            "has_docstrings": 4,
            "has_type_hints": 4,
            "has_logging": 4,
            "proper_structure": 4,
            "response_models": 4,
        }

        total = sum(scores[k] for k, v in checks.items() if v)

        return {
            "checks": checks,
            "score": total,
            "max_score": 20
        }

    def evaluate_all(self, data_dir: Path) -> dict:
        """评估所有样本"""
        print("=" * 80)
        print("EXPERIMENT 2: API SERVICE EVALUATION")
        print("=" * 80)
        print(f"Start time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

        baseline_dir = data_dir / "baseline"
        multilayer_dir = data_dir / "multilayer"

        all_results = []

        # 评估基线样本
        print("\n[1/3] Evaluating baseline samples...")
        for code_file in sorted(baseline_dir.glob("*.py")):
            sample_id = int(code_file.stem.split("_")[1])
            with open(code_file, 'r', encoding='utf-8') as f:
                code = f.read()

            result = self.evaluate_sample(code, sample_id, "baseline")
            all_results.append(result)
            print(f"  Sample {sample_id:03d}: Security={result['security_score']}/40, "
                  f"Func={result['functionality_score']}/40, "
                  f"Quality={result['quality_score']}/20, "
                  f"Total={result['total_score']}/100")

        # 评估多层次样本
        print("\n[2/3] Evaluating multilayer samples...")
        for code_file in sorted(multilayer_dir.glob("*.py")):
            sample_id = int(code_file.stem.split("_")[1])
            with open(code_file, 'r', encoding='utf-8') as f:
                code = f.read()

            result = self.evaluate_sample(code, sample_id, "multilayer")
            all_results.append(result)
            print(f"  Sample {sample_id:03d}: Security={result['security_score']}/40, "
                  f"Func={result['functionality_score']}/40, "
                  f"Quality={result['quality_score']}/20, "
                  f"Total={result['total_score']}/100")

        # 保存结果
        print("\n[3/3] Saving results...")
        results_dir = data_dir / "evaluation_results"
        results_dir.mkdir(exist_ok=True)

        baseline_results = [r for r in all_results if r['prompt_type'] == 'baseline']
        multilayer_results = [r for r in all_results if r['prompt_type'] == 'multilayer']

        with open(results_dir / "baseline_results.json", 'w') as f:
            json.dump(baseline_results, f, indent=2)

        with open(results_dir / "multilayer_results.json", 'w') as f:
            json.dump(multilayer_results, f, indent=2)

        # 统计
        stats = self.calculate_statistics(baseline_results, multilayer_results)
        with open(results_dir / "comparison_statistics.json", 'w') as f:
            json.dump(stats, f, indent=2)

        # 打印结果
        print("\n" + "=" * 80)
        print("EVALUATION RESULTS")
        print("=" * 80)

        print("\n📊 BASELINE GROUP:")
        print(f"  Syntax valid: {stats['baseline']['syntax_valid_count']}/{stats['baseline']['total']}")
        print(f"  Avg Security Score: {stats['baseline']['avg_security']:.2f}/40")
        print(f"  Avg Functionality Score: {stats['baseline']['avg_functionality']:.2f}/40")
        print(f"  Avg Quality Score: {stats['baseline']['avg_quality']:.2f}/20")
        print(f"  Avg Total Score: {stats['baseline']['avg_total']:.2f}/100")

        print("\n📊 MULTILAYER GROUP:")
        print(f"  Syntax valid: {stats['multilayer']['syntax_valid_count']}/{stats['multilayer']['total']}")
        print(f"  Avg Security Score: {stats['multilayer']['avg_security']:.2f}/40")
        print(f"  Avg Functionality Score: {stats['multilayer']['avg_functionality']:.2f}/40")
        print(f"  Avg Quality Score: {stats['multilayer']['avg_quality']:.2f}/20")
        print(f"  Avg Total Score: {stats['multilayer']['avg_total']:.2f}/100")

        print("\n📈 IMPROVEMENT:")
        print(f"  Security: +{stats['improvement']['security']:.2f} points")
        print(f"  Functionality: +{stats['improvement']['functionality']:.2f} points")
        print(f"  Quality: +{stats['improvement']['quality']:.2f} points")
        print(f"  Total: +{stats['improvement']['total']:.2f} points")

        print("\n" + "=" * 80)
        print(f"End time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Results saved to: {results_dir}")
        print("=" * 80)

        return stats

    def calculate_statistics(self, baseline: list, multilayer: list) -> dict:
        """计算统计数据"""
        def calc_group_stats(results):
            valid = [r for r in results if r['syntax_valid']]
            return {
                "total": len(results),
                "syntax_valid_count": len(valid),
                "syntax_valid_rate": len(valid) / len(results) if results else 0,
                "avg_security": sum(r['security_score'] for r in valid) / len(valid) if valid else 0,
                "avg_functionality": sum(r['functionality_score'] for r in valid) / len(valid) if valid else 0,
                "avg_quality": sum(r['quality_score'] for r in valid) / len(valid) if valid else 0,
                "avg_total": sum(r['total_score'] for r in valid) / len(valid) if valid else 0,
            }

        baseline_stats = calc_group_stats(baseline)
        multilayer_stats = calc_group_stats(multilayer)

        return {
            "baseline": baseline_stats,
            "multilayer": multilayer_stats,
            "improvement": {
                "security": multilayer_stats['avg_security'] - baseline_stats['avg_security'],
                "functionality": multilayer_stats['avg_functionality'] - baseline_stats['avg_functionality'],
                "quality": multilayer_stats['avg_quality'] - baseline_stats['avg_quality'],
                "total": multilayer_stats['avg_total'] - baseline_stats['avg_total'],
            }
        }


if __name__ == "__main__":
    evaluator = APISecurityEvaluator()
    data_dir = Path("/root/autodl-tmp/eoh/experiment2_api_service")
    evaluator.evaluate_all(data_dir)
