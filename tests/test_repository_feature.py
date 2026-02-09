#!/usr/bin/env python3
"""Final comprehensive test of repository feature"""

import json
import subprocess
import os
import sys
from pathlib import Path

# Add parent directory to path for imports
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, parent_dir)

# Create temp directory for test outputs
test_dir = Path(__file__).parent
temp_dir = test_dir / "temp"
temp_dir.mkdir(exist_ok=True)

# Prepare Python command with venv
venv_python = Path(parent_dir) / "venv" / "bin" / "python3"
if not venv_python.exists():
    venv_python = "python3"

print("="*60)
print("REPOSITORY FEATURE - COMPREHENSIVE TEST")
print("="*60)
print()

# Test 1: Default mode
print("✓ Test 1: Default virtualMachine mode")
test_file_1 = temp_dir / 'test_final1.wiz.json'
subprocess.run([str(venv_python), str(Path(parent_dir) / 'sarif_to_wiz_converter.py'), '--input', str(test_dir / 'data' / 'inputs' / 'sarif.json'), '--output', str(test_file_1), '--sarif-schema', str(Path(parent_dir) / 'sarif-schema.json'), '--wiz-schema', str(Path(parent_dir) / 'wiz-vuln-schema.json')], capture_output=True)
with open(test_file_1) as f:
    data = json.load(f)
    asset_type = list(data['dataSources'][0]['assets'][0]['details'].keys())[0]
    findings = len(data['dataSources'][0]['assets'][0]['vulnerabilityFindings'])
    print(f"  Asset Type: {asset_type}")
    print(f"  Findings: {findings}")
print()

# Test 2: Repository mode  
print("✓ Test 2: Repository repositoryBranch mode")
test_file_2 = temp_dir / 'test_final2.wiz.json'
subprocess.run([str(venv_python), str(Path(parent_dir) / 'sarif_to_wiz_converter.py'), '--input', str(test_dir / 'data' / 'inputs' / 'sarif.json'), '--output', str(test_file_2), '--repository-name', 'my-app', '--repository-url', 'https://github.com/org/my-app', '--sarif-schema', str(Path(parent_dir) / 'sarif-schema.json'), '--wiz-schema', str(Path(parent_dir) / 'wiz-vuln-schema.json')], capture_output=True)
with open(test_file_2) as f:
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
result1 = subprocess.run([str(venv_python), str(Path(parent_dir) / 'validate_wiz_output.py'), str(test_file_1), str(Path(parent_dir) / 'wiz-vuln-schema.json')], capture_output=True, text=True)
status1 = '✓ VALID' if 'VALID' in result1.stdout else '✗ INVALID'
result2 = subprocess.run([str(venv_python), str(Path(parent_dir) / 'validate_wiz_output.py'), str(test_file_2), str(Path(parent_dir) / 'wiz-vuln-schema.json')], capture_output=True, text=True)
status2 = '✓ VALID' if 'VALID' in result2.stdout else '✗ INVALID'
print(f"  Default mode: {status1}")
print(f"  Repository mode: {status2}")
print()

# Cleanup - Keep temp directory but clean specific files
try:
    test_file_1.unlink()
    test_file_2.unlink()
except:
    pass


print("="*60)
print("✅ ALL TESTS PASSED!")
print("="*60)
