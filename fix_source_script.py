#!/usr/bin/env python3
"""修复experiment1_generate_samples.py中的extract_code函数"""

# 读取原文件
with open('/root/autodl-tmp/eoh/experiment1_generate_samples.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# 找到extract_code函数的位置并替换
new_lines = []
skip_until_next_def = False
function_found = False

for i, line in enumerate(lines):
    if 'def extract_code(text):' in line and not function_found:
        function_found = True
        skip_until_next_def = True
        # 插入新的extract_code函数
        new_lines.append('def extract_code(text):\n')
        new_lines.append('    """从LLM输出中提取Python代码（修复版：提取最长的代码块）"""\n')
        new_lines.append('    blocks = []\n')
        new_lines.append('    pos = 0\n')
        new_lines.append('\n')
        new_lines.append('    # 找到所有```python代码块\n')
        new_lines.append('    while True:\n')
        new_lines.append('        start = text.find("```python", pos)\n')
        new_lines.append('        if start == -1:\n')
        new_lines.append('            break\n')
        new_lines.append('\n')
        new_lines.append('        code_start = start + len("```python")\n')
        new_lines.append('        code_end = text.find("```", code_start)\n')
        new_lines.append('\n')
        new_lines.append('        if code_end == -1:\n')
        new_lines.append('            break\n')
        new_lines.append('\n')
        new_lines.append('        code = text[code_start:code_end].strip()\n')
        new_lines.append('        blocks.append(code)\n')
        new_lines.append('        pos = code_end + 3\n')
        new_lines.append('\n')
        new_lines.append('    if blocks:\n')
        new_lines.append('        # 返回最长的代码块（通常是最后一个完整生成的代码）\n')
        new_lines.append('        return max(blocks, key=len)\n')
        new_lines.append('\n')
        new_lines.append('    # Fallback: 尝试提取```之间的代码\n')
        new_lines.append('    if "```" in text:\n')
        new_lines.append('        parts = text.split("```")\n')
        new_lines.append('        if len(parts) >= 3:\n')
        new_lines.append('            return parts[1].strip()\n')
        new_lines.append('\n')
        new_lines.append('    # 如果没有代码块标记，返回整个文本\n')
        new_lines.append('    return text.strip()\n')
        continue

    if skip_until_next_def:
        # 跳过旧函数，直到遇到下一个def或非缩进行
        if line.startswith('def ') or (line.strip() and not line.startswith(' ') and not line.startswith('\t')):
            skip_until_next_def = False
            new_lines.append(line)
    else:
        new_lines.append(line)

# 保存
with open('/root/autodl-tmp/eoh/experiment1_generate_samples.py', 'w', encoding='utf-8') as f:
    f.writelines(new_lines)

print('✅ 已修复 experiment1_generate_samples.py 中的 extract_code() 函数')
print('✅ 从"提取第一个代码块" → "提取最长的代码块"')
