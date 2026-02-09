# Root Directory Organization Guide

## Overview
This document describes the organization of the wiz-sarif-action-ingest repository to keep the root directory clean and focused.

## Root Directory Structure

### Core Application Files
- **sarif_to_wiz_converter.py** - Main converter application
- **mapping_engine.py** - Field mapping engine for SARIF to Wiz conversions
- **wiz_api_integration.py** - Wiz API integration utilities

### Configuration & Schemas
- **field_mappings.json** - Field mapping configuration
- **sarif-schema.json** - SARIF 2.1.0 specification schema
- **wiz-vuln-schema.json** - Wiz vulnerability ingestion schema
- **requirements.txt** - Python dependencies

### Documentation
- **README.md** - Main project README
- **CVE_ONLY_FEATURE.md** - Documentation for CVE-only filtering
- **REPOSITORY_FEATURE.md** - Documentation for repository/branch features
- **TROUBLESHOOTING.md** - Troubleshooting guide
- **PROJECT_STRUCTURE.md** - Project structure documentation
- **FIELD_MAPPING_*.md** - Field mapping guides and documentation

### Development
- **venv/** - Python virtual environment
- **__pycache__/** - Python cache (auto-generated)

## Tests & Examples Directory

All test files, examples, and sample data have been moved to the `tests/` directory to keep the root clean.

### tests/README.md
Entry point for understanding the test structure.

### tests/test_repository_feature.py
Main test suite validating:
- Default virtualMachine asset conversion
- Repository-based repositoryBranch asset conversion
- Schema validation

**Run tests:**
```bash
python3 tests/test_repository_feature.py
```

### tests/examples/
Example scripts and utilities:
- `example_usage.py` - Basic converter usage
- `example_mapping_usage.py` - Field mapping examples
- `diagnose_wiz_json.py` - JSON diagnostic utility
- `upload_security_scan.py` - Wiz API upload script
- `uploader_config.json` - Uploader configuration

### tests/data/
Test data and expected outputs:
- `inputs/` - Sample SARIF files for testing
- `outputs/` - Expected converter output examples

## Guidelines for Maintaining Clean Root

1. **All test-related files** → Move to `tests/`
2. **Test data and examples** → Place in `tests/data/` and `tests/examples/`
3. **Core functionality** → Keep in root (converter, engine, integration files)
4. **Schemas and configs** → Keep in root for easy CLI access
5. **Documentation** → Keep in root for visibility

## Common Usage Patterns

### Running the converter
```bash
python3 sarif_to_wiz_converter.py --input <sarif> --output <wiz-json>
```

### Running tests
```bash
python3 tests/test_repository_feature.py
```

### Using example data
```bash
python3 sarif_to_wiz_converter.py --input tests/data/inputs/sarif.json --output output.wiz.json
```

### Installing dependencies
```bash
pip install -r requirements.txt
```

## File Count Summary

- Root: ~14 core/config files + documentation
- Tests: ~40+ test files organized in subdirectories
- Keep the root focused on application code and configuration
