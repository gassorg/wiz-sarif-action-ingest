# SARIF to Wiz Vulnerability Schema Converter

A Python tool that converts SARIF (Static Analysis Results Format) output to Wiz vulnerability ingestion schema format. This tool is designed to work in CI/CD pipelines and validates both input and output against their respective JSON schemas.

## Overview

- **Input**: SARIF 2.1.0 format security findings
- **Output**: Wiz vulnerability ingestion format
- **Validation**: Both input and output are validated against JSON schemas
- **Pipeline Ready**: Designed for CI/CD integration with CLI-based operation
- **Extensible**: Architecture supports future API upload capabilities

## Installation

### Requirements
- Python 3.9+
- jsonschema library

### Setup

```bash
# Install dependencies
pip install -r requirements.txt

# Make script executable (optional)
chmod +x sarif_to_wiz_converter.py
```

## Documentation

All detailed documentation has been organized in the `docs/` directory. Here's a quick guide to find what you need:

### Quick Start & Setup
- **[GitHub Action Quick Start](docs/GITHUB_ACTION_QUICKSTART.md)** - 5-minute setup guide for GitHub Actions workflow
- **[Root Directory Guide](docs/ROOT_DIRECTORY_GUIDE.md)** - Understanding the project structure

### GitHub Actions Workflow
- **[GitHub Action Guide](docs/GITHUB_ACTION_GUIDE.md)** - Complete reference for the automated SARIF to Wiz workflow
- **[Environment Variables Guide](docs/UPLOAD_SCRIPT_ENV_VARS.md)** - Using GitHub Secrets for secure credential management

### Features & Configuration
- **[CVE-Only Feature](docs/CVE_ONLY_FEATURE.md)** - Filter findings to CVE identifiers only
- **[Repository Feature Guide](docs/REPOSITORY_FEATURE.md)** - Using repository context for asset tracking
- **[Repository Quick Reference](docs/REPOSITORY_FEATURE_QUICKREF.md)** - Quick syntax reference for repository options

### Advanced Topics
- **[Field Mapping Guide](docs/FIELD_MAPPING_GUIDE.md)** - Customizing SARIF to Wiz field mapping
- **[Field Mapping Implementation](docs/FIELD_MAPPING_IMPLEMENTATION.md)** - Technical details of field mapping engine
- **[Field Mapping Diagram](docs/FIELD_MAPPING_DIAGRAM.md)** - Visual representation of field mappings
- **[Field Mapping Visual Guide](docs/FIELD_MAPPING_VISUAL_GUIDE.md)** - Interactive guide for field mapping
- **[Mapping Quick Start](docs/MAPPING_QUICKSTART.md)** - Fast setup for custom field mappings

### Troubleshooting & Reference
- **[Troubleshooting Guide](docs/TROUBLESHOOTING.md)** - Solutions for common issues
- **[Project Structure](docs/PROJECT_STRUCTURE.md)** - Detailed project layout and organization
- **[Organization](docs/ORGANIZATION.md)** - Code organization and architecture
- **[Resolution Summary](docs/RESOLUTION_SUMMARY.md)** - Summary of recent changes and resolutions

## Usage

### Single File Conversion

```bash
python sarif_to_wiz_converter.py \
  --input path/to/scan.sarif \
  --output path/to/scan.wiz.json
```

### Batch Directory Conversion

```bash
python sarif_to_wiz_converter.py \
  --input-dir ./sarif-results \
  --output-dir ./wiz-results
```

### With Custom Integration ID

```bash
python sarif_to_wiz_converter.py \
  --input path/to/scan.sarif \
  --output path/to/scan.wiz.json \
  --integration-id my-org-sarif-scanner
```

### With Repository Information (repositoryBranch Asset Type)

Creates `repositoryBranch` assets instead of `virtualMachine` assets:

```bash
python sarif_to_wiz_converter.py \
  --input path/to/scan.sarif \
  --output path/to/scan.wiz.json \
  --repository-name "my-app" \
  --repository-url "https://github.com/org/my-app"
```

**Note**: Both `--repository-name` and `--repository-url` must be specified together. Omitting both will use the default `virtualMachine` asset type.

### Custom Schema Paths

```bash
python sarif_to_wiz_converter.py \
  --input scan.sarif \
  --output scan.wiz.json \
  --sarif-schema /path/to/sarif-schema.json \
  --wiz-schema /path/to/wiz-vuln-schema.json
```

### Verbose Output

```bash
python sarif_to_wiz_converter.py \
  --input scan.sarif \
  --output scan.wiz.json \
  --verbose
```

### CVE-Only Filtering

Filter findings to only include those with CVE identifiers (CVE-YYYY-NNNNN format):

```bash
python sarif_to_wiz_converter.py \
  --input scan.sarif \
  --output scan.wiz.json \
  --cve-only
```

When using `--cve-only`, finding names are simplified to include only the CVE identifier:
- **Without flag**: `CVE-2022-0235_node-fetch_2.6.1`
- **With flag**: `CVE-2022-0235`

This flag is useful for focusing on known vulnerabilities and filtering out proprietary or unidentified issues.

## Asset Types

The converter supports two asset types depending on your use case:

### virtualMachine (Default)
Used when repository information is not provided. Best for generic finding sources.

```json
{
  "details": {
    "virtualMachine": {
      "assetId": "package.json",
      "name": "package.json",
      "hostname": "package.json",
      "firstSeen": "2026-01-26T20:36:15Z"
    }
  }
}
```

### repositoryBranch
Used when `--repository-name` and `--repository-url` are provided. Best for code scanning results linked to repositories.

```json
{
  "details": {
    "repositoryBranch": {
      "assetId": "package.json",
      "assetName": "package.json",
      "branchName": "main",
      "repository": {
        "name": "my-app",
        "url": "https://github.com/org/my-app"
      },
      "vcs": "GitHub",
      "firstSeen": "2026-01-26T20:36:29Z"
    }
  }
}
```

## CI/CD Integration Examples

### GitHub Actions

A complete GitHub Action workflow is provided for batch SARIF conversion and upload to Wiz. 

**Workflow File**: [actions/workflows/sarif-to-wiz-batch-upload.yml](actions/workflows/sarif-to-wiz-batch-upload.yml)

#### Features:
- ✓ Batch converts all SARIF files in a directory
- ✓ Automatically uploads converted files to Wiz platform
- ✓ Supports manual trigger (workflow_dispatch) and automatic trigger (on SARIF file push)
- ✓ Integrates with GitHub Secrets for secure credential management
- ✓ Generates workflow summary report with results
- ✓ Stores artifacts for 30 days

#### Setup:
1. Add repository secrets (Settings → Secrets and variables → Actions):
   - `WIZ_CLIENT_ID`
   - `WIZ_CLIENT_SECRET`
   - `WIZ_TOKEN_URL`
   - `WIZ_API_ENDPOINT_URL`

2. Create `.sarif-reports/` directory and place SARIF files there

3. Trigger the workflow:
   - **Manual**: Go to Actions → Run workflow
   - **Automatic**: Commit SARIF files and push

#### Workflow Example:

For a complete, production-ready workflow with batch conversion and upload, use the provided GitHub Action:

```yaml
name: Call SARIF to Wiz Action
on:
  push:
    branches:
      - main

jobs:
  convert-upload:
    uses: gassorg/wiz-sarif-action-ingest/.github/workflows/action.yml@main
    with:
      sarif_input_dir: './sarif_data'
      repository_name: ${{ github.repository }}
      repository_url: ${{ github.server_url }}/${{ github.repository }}
      branch_name: ${{ github.ref_name }}
      cve_only: true
    secrets:
      WIZ_CLIENT_ID: ${{ secrets.WIZ_CLIENT_ID }}
      WIZ_CLIENT_SECRET: ${{ secrets.WIZ_CLIENT_SECRET }}
      WIZ_TOKEN_URL: ${{ secrets.WIZ_TOKEN_URL }}
      WIZ_API_ENDPOINT_URL: ${{ secrets.WIZ_API_ENDPOINT_URL }}
```

**For the full workflow with all features**, see [actions/workflows/sarif-to-wiz-batch-upload.yml](actions/workflows/sarif-to-wiz-batch-upload.yml).

**For GitHub Action setup and configuration**, see [docs/GITHUB_ACTION_GUIDE.md](docs/GITHUB_ACTION_GUIDE.md).

### GitLab CI

```yaml
convert_sarif:
  stage: analysis
  image: python:3.11
  script:
    - pip install -r requirements.txt
    - python sarif_to_wiz_converter.py
        --input-dir ./sarif-results
        --output-dir ./wiz-results
        --integration-id gitlab-ci-scan
  artifacts:
    paths:
      - wiz-results/
    expire_in: 30 days
```

### Jenkins

```groovy
pipeline {
    agent any
    
    stages {
        stage('Convert SARIF') {
            steps {
                script {
                    sh '''
                        python -m pip install -r requirements.txt
                        python sarif_to_wiz_converter.py \
                            --input-dir ./sarif-results \
                            --output-dir ./wiz-results \
                            --integration-id jenkins-scan
                    '''
                }
            }
        }
        
        stage('Upload to Wiz') {
            steps {
                script {
                    // Future: Upload to Wiz API
                    sh 'ls -la wiz-results/'
                }
            }
        }
    }
}
```

## Output

### Success Example

```
2024-01-22 10:30:45,123 - INFO - Processing: scan.sarif
2024-01-22 10:30:45,234 - DEBUG - ✓ SARIF input is valid
2024-01-22 10:30:45,456 - DEBUG - ✓ Wiz output is valid
2024-01-22 10:30:45,567 - INFO - ✓ Successfully converted to: scan.wiz.json
```

### Exit Codes

- `0`: Success (all files processed)
- `1`: Failure (validation error or processing issue)

## Output Format

The converter produces JSON files conforming to the Wiz vulnerability ingestion schema:

```json
{
  "integrationId": "sarif-integration",
  "dataSources": [
    {
      "id": "tool-run-0",
      "analysisDate": "2024-01-22T10:30:45.123Z",
      "assets": [
        {
          "analysisDate": "2024-01-22T10:30:45.123Z",
          "details": {
            "assetEndpoint": {
              "assetId": "file.js-0",
              "assetName": "src/file.js",
              "host": "src/file.js",
              "firstSeen": "2024-01-22T10:30:45.123Z"
            }
          },
          "vulnerabilityFindings": [
            {
              "name": "CWE-123",
              "description": "Potential vulnerability detected",
              "severity": "Medium",
              "detectionMethod": "SASTScan",
              "externalDetectionSource": "SASTScan"
            }
          ]
        }
      ]
    }
  ]
}
```

## Schema Mapping

### SARIF to Wiz Conversion Logic

| SARIF Element | Wiz Element | Notes |
|---|---|---|
| `runs[]` | `dataSources[]` | Each run becomes a data source |
| `results[]` | Grouped by asset location | Results are grouped by artifact URI |
| `result.message.text` | `vulnerabilityFinding.description` | Finding description |
| `result.ruleId` | `vulnerabilityFinding.name` | Finding name/identifier |
| `result.level` | `vulnerabilityFinding.severity` | Mapped: none→None, note→Low, warning→Medium, error→High |
| `result.locations[].physicalLocation.artifactLocation.uri` | `asset.assetEndpoint.host` | File path as asset identifier |

## Architecture

The tool is organized into modular components for extensibility:

- **SchemaValidator**: Handles JSON schema validation
- **SARIFtoWizConverter**: Core conversion logic
- **PipelineProcessor**: File processing and orchestration
- **CLI Interface**: Command-line argument handling

### Future Enhancement Points

1. **API Integration**: `PipelineProcessor` can be extended with API upload methods
2. **Asset Type Detection**: More sophisticated asset classification based on SARIF metadata
3. **Custom Mapping Rules**: Support for organization-specific conversion rules
4. **Filtering**: Add options to filter findings by severity, rule type, etc.
5. **Transformation Plugins**: Plugin system for tool-specific conversions

## Troubleshooting

### Schema Validation Errors

Ensure schema files are in the same directory as the script or specify paths:

```bash
python sarif_to_wiz_converter.py \
  --input scan.sarif \
  --output scan.wiz.json \
  --sarif-schema /path/to/sarif-schema.json \
  --wiz-schema /path/to/wiz-vuln-schema.json
```

### Invalid JSON in SARIF File

Verify the SARIF file is valid JSON:

```bash
python -m json.tool scan.sarif > /dev/null
```

### Enable Debug Logging

Use `--verbose` flag for detailed execution information:

```bash
python sarif_to_wiz_converter.py \
  --input scan.sarif \
  --output scan.wiz.json \
  --verbose
```

## Development

### Running Tests

```bash
# Future: Add test suite
pytest tests/
```

### Code Quality

```bash
# Future: Add linting
pylint sarif_to_wiz_converter.py
black sarif_to_wiz_converter.py
```

## License

See LICENSE file in the repository.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Validate with schema files
5. Submit a pull request

## Support

For issues, questions, or suggestions, please open an issue in the repository.
