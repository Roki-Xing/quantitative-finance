#!/usr/bin/env python3
"""
Fix extract_code() bug and re-save multilayer samples
从元数据中提取正确的代码块并重新保存
"""
import json
from pathlib import Path

def extract_code_fixed(text):
    """
    修复后的代码提取函数：提取最长的代码块
    """
    blocks = []
    pos = 0

    while True:
        start = text.find('```python', pos)
        if start == -1:
            break

        code_start = start + len('```python')
        code_end = text.find('```', code_start)

        if code_end == -1:
            break

        code = text[code_start:code_end].strip()
        blocks.append(code)
        pos = code_end + 3

    if not blocks:
        # Fallback: 尝试提取```之间的代码
        if "```" in text:
            parts = text.split("```")
            if len(parts) >= 3:
                return parts[1].strip()
        return text.strip()

    # 返回最长的代码块 (通常是最后一个完整生成的代码)
    return max(blocks, key=len)


def main():
    print("="*80)
    print("FIXING MULTILAYER SAMPLES")
    print("="*80)

    # 加载元数据
    metadata_file = Path('/root/autodl-tmp/eoh/experiment1_web_scraper/generation_metadata.json')
    with open(metadata_file) as f:
        data = json.load(f)

    # 修复多层次样本 (样本30-59，索引30-59)
    multilayer_dir = Path('/root/autodl-tmp/eoh/experiment1_web_scraper/multilayer')

    fixed_count = 0
    for i, sample in enumerate(data['samples']):
        if sample['prompt_type'] != 'multilayer':
            continue

        sample_id = sample['id']
        raw_output = sample['raw_output']
        old_code = sample['code']

        # 使用修复后的函数提取代码
        new_code = extract_code_fixed(raw_output)

        print(f"\nSample #{sample_id}:")
        print(f"  Old code length: {len(old_code)} chars")
        print(f"  New code length: {len(new_code)} chars")

        if len(new_code) > len(old_code):
            # 更新元数据
            data['samples'][i]['code'] = new_code

            # 重新保存代码文件
            code_file = multilayer_dir / f"sample_{sample_id:03d}.py"
            with open(code_file, 'w', encoding='utf-8') as f:
                f.write(new_code)

            fixed_count += 1
            print(f"  ✅ Fixed and saved")
        else:
            print(f"  ⚠️ No improvement, skipped")

    # 保存更新后的元数据
    with open(metadata_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    print("\n" + "="*80)
    print(f"✅ Fixed {fixed_count} multilayer samples")
    print("="*80)
    print(f"Updated metadata: {metadata_file}")

    # 验证修复
    print("\n" + "="*80)
    print("VERIFICATION")
    print("="*80)

    for sample in data['samples'][30:33]:  # 检查前3个多层次样本
        code_file = multilayer_dir / f"sample_{sample['id']:03d}.py"
        with open(code_file, 'r', encoding='utf-8') as f:
            saved_code = f.read()

        print(f"\nSample #{sample['id']}:")
        print(f"  Metadata code length: {len(sample['code'])} chars")
        print(f"  File code length: {len(saved_code)} chars")
        print(f"  Match: {'✅' if len(sample['code']) == len(saved_code) else '❌'}")


if __name__ == '__main__':
    main()
