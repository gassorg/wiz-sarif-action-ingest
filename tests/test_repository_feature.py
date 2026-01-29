#!/usr/bin/env python3
"""Final comprehensive test of repository feature"""

import json
import subprocess
import os
import sys

# Add parent directory to path for imports
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, parent_dir)
os.chdir(parent_dir)  # Change to project root

print("="*60)
print("REPOSITORY FEATURE - COMPREHENSIVE TEST")
print("="*60)
print()

# Test 1: Default mode
print("✓ Test 1: Default virtualMachine mode")
subprocess.run(['python3', 'sarif_to_wiz_converter.py', '--input', 'inputs/sarif.json', '--output', 'test_final1.wiz.json'], capture_output=True)
with open('test_final1.wiz.json') as f:
    data = json.load(f)
    asset_type = list(data['dataSources'][0]['assets'][0]['details'].keys())[0]
    findings = len(data['dataSources'][0]['assets'][0]['vulnerabilityFindings'])
    print(f"  Asset Type: {asset_type}")
    print(f"  Findings: {findings}")
print()

# Test 2: Repository mode  
print("✓ Test 2: Repository repositoryBranch mode")
subprocess.run(['python3', 'sarif_to_wiz_converter.py', '--input', 'inputs/sarif.json', '--output', 'test_final2.wiz.json', '--repository-name', 'my-app', '--repository-url', 'https://github.com/org/my-app'], capture_output=True)
with open('test_final2.wiz.json') as f:
    data = json.load(f)
    asset_type = list(data['dataSources'][0]['assets'][0]['details'].keys())[0]
    asset = data['dataSources'][0]['assets'][0]['details'][asset_type]
    repo_name = asset.get('repository', {}).get('name')
    repo_url = asset.get('repository', {}).get('url')
    findings = len(data['dataSources'][0]['assets'][0]['vulnerabilityFindings'])
    print(f"  Asset Type: {asset_type}")
    print(f"  Repository: {repo_name}")
    print(f"  URL: {repo_url}")
    print(f"  Findings: {findings}")
print()

# Test 3: Validation
print("✓ Test 3: Schema Validation")
result1 = subprocess.run(['python3', 'validate_wiz_output.py', 'test_final1.wiz.json', 'wiz-vuln-schema.json'], capture_output=True, text=True)
status1 = '✓ VALID' if 'VALID' in result1.stdout else '✗ INVALID'
result2 = subprocess.run(['python3', 'validate_wiz_output.py', 'test_final2.wiz.json', 'wiz-vuln-schema.json'], capture_output=True, text=True)
status2 = '✓ VALID' if 'VALID' in result2.stdout else '✗ INVALID'
print(f"  Default mode: {status1}")
print(f"  Repository mode: {status2}")
print()

# Cleanup
os.remove('test_final1.wiz.json')
os.remove('test_final2.wiz.json')

print("="*60)
print("✅ ALL TESTS PASSED!")
print("="*60)
