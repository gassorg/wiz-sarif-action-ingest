# Project Structure Guide

## Directory Organization

```
wiz-sarif-action-ingest/
├── Core Converter Files
│   ├── sarif_to_wiz_converter.py      # Main converter script
│   ├── validate_wiz_output.py         # Output validation tool
│   ├── diagnose_wiz_json.py           # JSON diagnostics tool
│   ├── example_usage.py               # Usage examples
│   ├── wiz_api_integration.py         # API integration template
│   └── upload_security_scan.py        # Upload utility
│
├── Configuration & Schemas
│   ├── sarif-schema.json              # SARIF 2.1.0 schema
│   ├── wiz-vuln-schema.json           # Wiz vulnerability schema
│   ├── requirements.txt               # Python dependencies
│   └── uploader_config.json           # Upload configuration template
│
├── Documentation
│   ├── README.md                      # Project overview
│   ├── README_CONVERTER.md            # Converter usage guide
│   ├── REPOSITORY_FEATURE.md          # Repository feature documentation
│   ├── REPOSITORY_FEATURE_QUICKREF.md # Quick reference
│   ├── TROUBLESHOOTING.md             # Troubleshooting guide
│   ├── RESOLUTION_SUMMARY.md          # Resolution documentation
│   └── PROJECT_STRUCTURE.md           # This file
│
├── tests/                             # Test Suite
│   ├── test_repository_feature.py     # Comprehensive test script
│   └── README.md                      # Test documentation
│
├── inputs/                            # Input Samples
│   ├── sarif.json                     # Sample SARIF file (31 findings)
│   ├── updated-sarif.json             # Updated SARIF file
│   └── README.md                      # Sample documentation
│
├── outputs/                           # Example Outputs & Test Results
│   ├── sample_wiz_output/             # Example Wiz format output
│   ├── test-schema/                   # Schema validation test results
│   ├── test_repo_output/              # Repository mode test results
│   ├── test_vm_output/                # Default mode test results
│   └── README.md                      # Outputs documentation
│
└── venv/                              # Python virtual environment

```

## File Categories

### Core Converter Files

| File | Purpose | Usage |
|------|---------|-------|
| `sarif_to_wiz_converter.py` | Main conversion engine | `python sarif_to_wiz_converter.py --help` |
| `validate_wiz_output.py` | Schema validation | `python validate_wiz_output.py <file> <schema>` |
| `diagnose_wiz_json.py` | JSON structure analysis | `python diagnose_wiz_json.py <file>` |
| `example_usage.py` | Usage examples | Reference or run directly |
| `wiz_api_integration.py` | API integration template | Template for future API work |
| `upload_security_scan.py` | Upload utility | For uploading to Wiz |

### Configuration Files

| File | Purpose |
|------|---------|
| `sarif-schema.json` | SARIF 2.1.0 format validation |
| `wiz-vuln-schema.json` | Wiz output format validation |
| `requirements.txt` | Python package dependencies |
| `uploader_config.json` | Upload configuration template |

### Documentation Files

All documentation files follow a specific purpose:

- **README.md** - Project overview and quick start
- **README_CONVERTER.md** - Complete converter usage guide with CI/CD examples
- **REPOSITORY_FEATURE.md** - Detailed repository feature documentation
- **REPOSITORY_FEATURE_QUICKREF.md** - Quick reference for repository feature
- **TROUBLESHOOTING.md** - Common issues and solutions
- **RESOLUTION_SUMMARY.md** - Complete resolution history
- **PROJECT_STRUCTURE.md** - This document

## Directory Purposes

### tests/
Contains all test-related files:
- `test_repository_feature.py` - Comprehensive test suite
- `README.md` - Test documentation and instructions

### inputs/
Contains example SARIF files for testing:
- `sarif.json` - Main sample with 31 findings
- `updated-sarif.json` - Alternative sample
- `README.md` - Sample documentation

### outputs/
Contains example outputs and test results:
- `sample_wiz_output/` - Example conversion output
- `test-schema/` - Schema validation test output
- `test_repo_output/` - Repository mode test output
- `test_vm_output/` - Default mode test output
- `README.md` - Output documentation

## Quick Navigation

### Running the Converter
```bash
# Default mode (virtualMachine assets)
python sarif_to_wiz_converter.py --input tests/data/inputs/sarif.json --output output.wiz.json

# Repository mode (repositoryBranch assets)
python sarif_to_wiz_converter.py --input samples/sarif.json --output output.wiz.json \
  --repository-name "my-app" --repository-url "https://github.com/org/my-app"
```

### Validating Output
```bash
python validate_wiz_output.py output.wiz.json wiz-vuln-schema.json
```

### Running Tests
```bash
python tests/test_repository_feature.py
```

### Diagnosing Issues
```bash
python diagnose_wiz_json.py output.wiz.json
```

## Dependencies

Python 3.9+ with:
- jsonschema >= 4.17.0

Install with:
```bash
pip install -r requirements.txt
```

## CI/CD Integration

The converter is designed for CI/CD pipelines. See:
- **README_CONVERTER.md** - GitHub Actions, GitLab CI, Jenkins examples
- **samples/** - Test data for pipeline validation

## Next Steps

1. **Getting Started**: Read [README.md](README.md)
2. **Using the Converter**: See [README_CONVERTER.md](README_CONVERTER.md)
3. **Repository Feature**: Check [REPOSITORY_FEATURE_QUICKREF.md](REPOSITORY_FEATURE_QUICKREF.md)
4. **Running Tests**: See [tests/README.md](tests/README.md)
5. **Troubleshooting**: Consult [TROUBLESHOOTING.md](TROUBLESHOOTING.md)
