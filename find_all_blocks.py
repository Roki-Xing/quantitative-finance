#!/usr/bin/env python3
"""Find all code blocks in raw output"""
import json

with open('generation_metadata.json') as f:
    data = json.load(f)

sample = data['samples'][30]
raw = sample['raw_output']

print("="*80)
print("FINDING ALL CODE BLOCKS")
print("="*80)

# Find all ```python blocks
pos = 0
block_num = 0
while True:
    start = raw.find('```python', pos)
    if start == -1:
        break

    block_num += 1
    code_start = start + len('```python')
    code_end = raw.find('```', code_start)

    if code_end == -1:
        print(f"\n❌ Block {block_num}: No closing ```")
        break

    code = raw[code_start:code_end].strip()
    print(f"\n{'='*80}")
    print(f"Block #{block_num}:")
    print(f"Position: {start} - {code_end}")
    print(f"Length: {len(code)} chars")
    print(f"Lines: {len(code.splitlines())}")
    print(f"{'='*80}")
    print("First 300 chars:")
    print(code[:300])

    if len(code) > 1000:
        print("\n...TRUNCATED...")
        print(f"\nLast 200 chars:")
        print(code[-200:])

    pos = code_end + 3

print(f"\n{'='*80}")
print(f"Total code blocks found: {block_num}")
print(f"{'='*80}")
