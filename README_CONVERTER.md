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

## CI/CD Integration Examples

### GitHub Actions

```yaml
name: Convert SARIF to Wiz Format

on: [push]

jobs:
  convert:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      
      - name: Install dependencies
        run: pip install -r requirements.txt
      
      - name: Convert SARIF results
        run: |
          python sarif_to_wiz_converter.py \
            --input-dir ./sarif-results \
            --output-dir ./wiz-results \
            --integration-id github-actions-scan
      
      - name: Upload Wiz format results
        uses: actions/upload-artifact@v3
        with:
          name: wiz-results
          path: wiz-results/
```

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
