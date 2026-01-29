# Tests Directory

This directory contains all test-related files for the SARIF to Wiz converter project.

## Contents

### test_repository_feature.py
Comprehensive test script that validates:
- Default mode (virtualMachine asset type)
- Repository mode (repositoryBranch asset type)
- Schema validation for both modes
- Asset structure correctness

**Run the test:**
```bash
python test_repository_feature.py
```

## Usage

To run all tests from the parent directory:

```bash
cd ..
python tests/test_repository_feature.py
```

To run from the tests directory:

```bash
python test_repository_feature.py
```

## Test Coverage

The test suite validates:

1. **Default Conversion Mode**
   - Generates virtualMachine assets
   - Correct asset ID, name, and hostname fields
   - Valid timestamps in ISO 8601 format
   - Schema validation passes

2. **Repository Mode**
   - Generates repositoryBranch assets with repository information
   - Correct asset ID, name, and branch name fields
   - Repository details (name and URL) populated correctly
   - VCS type set to "GitHub"
   - Valid timestamps in ISO 8601 format
   - Schema validation passes

3. **Error Handling**
   - Partial repository parameters validation
   - Both parameters required together

## Expected Output

All tests should display:
```
✓ Test 1: Default virtualMachine mode
  Asset Type: virtualMachine
  Findings: 31

✓ Test 2: Repository repositoryBranch mode
  Asset Type: repositoryBranch
  Repository: my-app
  URL: https://github.com/org/my-app
  Findings: 31

✓ Test 3: Schema Validation
  Default mode: ✓ VALID
  Repository mode: ✓ VALID

✅ ALL TESTS PASSED!
```

## Related Files

- Main converter: `../sarif_to_wiz_converter.py`
- Sample data: `../inputs/`
- Output examples: `../outputs/`
