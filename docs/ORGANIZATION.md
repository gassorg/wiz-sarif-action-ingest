# Directory Organization Summary

## Overview

The working directory has been reorganized for better maintainability and clarity. All test-related files, samples, and outputs are now organized in dedicated directories.

## Changes Made

### Directory Structure

**Before:**
```
wiz-sarif-action-ingest/
├── sample_sarif_files/
├── sample_wiz_output/
├── test-schema/
├── test_repo_output/
├── test_vm_output/
├── test_repository_feature.py
└── [all core files mixed with test files]
```

**After:**
```
wiz-sarif-action-ingest/
├── tests/
│   ├── test_repository_feature.py
│   └── README.md
├── inputs/
│   ├── sarif.json
│   ├── updated-sarif.json
│   └── README.md
├── outputs/
│   ├── sample_wiz_output/
│   ├── test-schema/
│   ├── test_repo_output/
│   ├── test_vm_output/
│   └── README.md
├── [Core converter files]
├── [Configuration files]
└── [Documentation files]
```

### Files Organized

**Tests Directory:**
- `tests/test_repository_feature.py` - Comprehensive test suite
- `tests/README.md` - Test documentation

**Inputs Directory:**
- `inputs/sarif.json` - Main SARIF sample (31 findings)
- `inputs/updated-sarif.json` - Alternative SARIF sample
- `inputs/README.md` - Sample documentation

**Outputs Directory:**
- `outputs/sample_wiz_output/` - Example conversion output
- `outputs/test-schema/` - Schema validation test output
- `outputs/test_repo_output/` - Repository mode test output
- `outputs/test_vm_output/` - Default mode test output
- `outputs/README.md` - Output documentation

### Temporary Files Removed

- `final_test_*.wiz.json` - Temporary test outputs
- `scan-results.sarif` - Temporary scan file
- `.DS_Store` - System files

### Documentation Created

New documentation files to explain the organization:
- `PROJECT_STRUCTURE.md` - Detailed project structure guide
- `tests/README.md` - Test suite documentation
- `inputs/README.md` - Sample data documentation
- `outputs/README.md` - Output examples documentation

### Documentation Updated

Updated existing files to reflect new paths:
- `TROUBLESHOOTING.md` - Updated sample file paths
- `RESOLUTION_SUMMARY.md` - Updated sample file paths

## Running Tests

The test suite now runs from the new location with proper path handling:

```bash
# From project root
python3 tests/test_repository_feature.py

# Or from within tests directory
cd tests
python3 test_repository_feature.py
```

The test automatically handles working directory and relative paths.

## Benefits of New Structure

1. **Clarity** - Core functionality, tests, and samples are clearly separated
2. **Scalability** - Easy to add more tests or samples without cluttering the root
3. **Organization** - Easier to navigate and find specific files
4. **Documentation** - Each directory has its own README explaining its purpose
5. **Cleanliness** - Root directory focused on core converter functionality

## File References

### Core Converter (Root Directory)
```
sarif_to_wiz_converter.py      # Main converter
validate_wiz_output.py         # Output validation
diagnose_wiz_json.py           # Diagnostics
example_usage.py               # Usage examples
upload_security_scan.py        # Upload utility
wiz_api_integration.py         # API template
```

### Configuration (Root Directory)
```
sarif-schema.json              # SARIF validation
wiz-vuln-schema.json           # Wiz validation
requirements.txt               # Dependencies
uploader_config.json           # Upload config
```

### Documentation (Root Directory)
```
README.md                       # Project overview
README_CONVERTER.md            # Converter guide
REPOSITORY_FEATURE.md          # Feature docs
REPOSITORY_FEATURE_QUICKREF.md # Quick reference
TROUBLESHOOTING.md             # Troubleshooting
RESOLUTION_SUMMARY.md          # Resolution history
PROJECT_STRUCTURE.md           # This structure guide
```

### Organized Directories
```
tests/                         # Test suite
inputs/                        # Input samples
outputs/                       # Example outputs
```

## Quick Navigation

### Start Here
- Read: `README.md`
- Then: `README_CONVERTER.md`

### Learn Features
- Repository Feature: `REPOSITORY_FEATURE_QUICKREF.md`
- Detailed: `REPOSITORY_FEATURE.md`

### Run Tests
- Command: `python3 tests/test_repository_feature.py`
- Details: `tests/README.md`

### View Examples
- Samples: `inputs/README.md`
- Outputs: `outputs/README.md`

### Troubleshooting
- Guide: `TROUBLESHOOTING.md`
- Structure: `PROJECT_STRUCTURE.md`

## Next Steps

1. Review the new structure: `PROJECT_STRUCTURE.md`
2. Run tests to verify: `python3 tests/test_repository_feature.py`
3. Continue using converter as normal from root directory
4. Consult directory READMEs for specific use cases

## Compatibility

✅ All paths updated to work from project root
✅ Tests automatically handle directory changes
✅ Converter works with new sample locations
✅ All outputs validate against schema
✅ Full backward compatibility maintained
