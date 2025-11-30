#!/usr/bin/env python3
"""
Analysis script to understand the extraction issue
"""
import json

with open('generation_metadata.json') as f:
    data = json.load(f)

# Analyze first multilayer sample
sample = data['samples'][30]
raw = sample['raw_output']
code = sample['code']

print("="*80)
print("GENERATION ANALYSIS")
print("="*80)
print(f"Sample ID: {sample['id']}")
print(f"Prompt Type: {sample['prompt_type']}")
print(f"Raw output length: {len(raw)} chars")
print(f"Extracted code length: {len(code)} chars")
print()

# Find code blocks
python_start = raw.find('```python')
if python_start != -1:
    print(f"Found ```python at position {python_start}")

    # Find end of code block
    code_start = python_start + len('```python')
    code_end = raw.find('```', code_start)

    if code_end != -1:
        extracted = raw[code_start:code_end].strip()
        print(f"Code block ends at position {code_end}")
        print(f"Extracted block length: {len(extracted)} chars")
        print()
        print("="*80)
        print("EXPECTED EXTRACTED CODE (first 500 chars):")
        print("="*80)
        print(extracted[:500])
        print()
        print("="*80)
        print("ACTUAL EXTRACTED CODE:")
        print("="*80)
        print(code)
        print()
        print("="*80)
        print("CONCLUSION:")
        print("="*80)
        if len(extracted) > 100:
            print("LLM generated complete code!")
            print(f"Expected: {len(extracted)} chars")
            print(f"Got: {len(code)} chars")
            print("Problem: extract_code() function is BROKEN!")
        else:
            print("LLM generation failed")
