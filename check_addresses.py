"""Check all addresses in the job description"""
import json

with open('data/scraped_job_20251014_111612.json') as f:
    data = json.load(f)

desc = data['job_description']
lines = desc.split('\n')

print("="*80)
print("ALL ADDRESSES IN JOB DESCRIPTION")
print("="*80)

for i, line in enumerate(lines):
    if 'Infopro' in line and i < len(lines)-3:
        print(f'\nLine {i}: {line}')
        for j in range(1, 4):
            if i+j < len(lines):
                print(f'  +{j}: {lines[i+j]}')

print("\n" + "="*80)
print("EXTRACTED ADDRESS")
print("="*80)
print(f"Line 1: {data['company_address_line1']}")
print(f"Line 2: {data['company_address_line2']}")
print(f"Full: {data['company_address']}")
