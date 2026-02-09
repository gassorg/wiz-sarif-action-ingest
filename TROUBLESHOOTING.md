# SARIF to Wiz Vulnerability Schema Converter - Troubleshooting Guide

## Issue: "additionalProperties 'assetEndpoint' not allowed"

### Root Cause
When uploading to Wiz's API, you receive an error indicating that `assetEndpoint` is not allowed under `details`. This typically indicates one of these issues:

1. **Schema Version Mismatch**: Your local `wiz-vuln-schema.json` may be older than what Wiz API currently expects
2. **API Restrictions**: The Wiz API may have stricter validation than the published schema
3. **Incorrect Asset Type**: The asset structure may need a different type for your finding type

### Solutions

#### Solution 1: Update Schema File
Download the latest schema from Wiz:
```bash
# Get the current schema from Wiz (if available publicly)
curl -o wiz-vuln-schema.json https://api.wiz.io/schemas/ingestion-model.json
```

#### Solution 2: Validate Output Locally
Use the diagnostic tool to identify issues before uploading:
```bash
python3 diagnose_wiz_json.py ./sample_wiz_output/sarif.wiz.json
python3 validate_wiz_output.py ./sample_wiz_output/sarif.wiz.json wiz-vuln-schema.json
```

#### Solution 3: Check API Documentation
Verify your request format matches Wiz API expectations:
- Review Wiz API documentation for vulnerability ingestion
- Check if there are example payloads provided
- Verify integration ID format and structure

#### Solution 4: Simplify Asset Structure
If `assetEndpoint` is not working, try alternative approaches:

**Option A: Use minimal required fields only**
```json
{
  "details": {
    "assetEndpoint": {
      "assetId": "file-path",
      "assetName": "filename"
    }
  }
}
```

**Option B: Use networkAddress for IP-based assets**
```json
{
  "details": {
    "networkAddress": {
      "assetId": "ip-address",
      "name": "hostname",
      "addressType": "IPV4",
      "address": "192.168.1.1"
    }
  }
}
```

**Option C: Use virtualMachine for host-based assets**
```json
{
  "details": {
    "virtualMachine": {
      "assetId": "vm-id",
      "name": "vm-name",
      "hostname": "hostname"
    }
  }
}
```

### Debugging Steps

1. **Validate JSON Structure Locally**
   ```bash
   python3 validate_wiz_output.py ./sample_wiz_output/sarif.wiz.json
   ```

2. **Run Diagnostic Analysis**
   ```bash
   python3 diagnose_wiz_json.py ./sample_wiz_output/sarif.wiz.json
   ```

3. **Check Converter Output**
   - Look at the generated JSON to ensure it matches expectations
   - Verify all required fields are present
   - Check for null/empty values

4. **Enable Verbose Logging**
   ```bash
   python3 sarif_to_wiz_converter.py --input tests/data/inputs/sarif.json --output test.json --verbose
   ```

5. **Contact Wiz Support**
   If issues persist:
   - Share the diagnostic output
   - Include the schema version you're using
   - Provide sample SARIF and converted JSON
   - Include the exact API error message

### Known Issues

#### SARIF Dependency Scanning
If your SARIF file contains dependency/license findings (like from dependency scanners):
- These don't map well to `assetEndpoint` (which is for network services)
- Consider using different asset types or creating minimal assets
- The converter currently uses `assetEndpoint` as a fallback

**Recommended for dependency findings:**
```json
{
  "details": {
    "assetEndpoint": {
      "assetId": "package-name-version",
      "assetName": "package-name"
    }
  }
}
```

#### SAST/Code Analysis Findings
For code findings pointing to source files:
- File paths don't map naturally to network assets
- Current approach: group by file path and create minimal assetEndpoint
- Future: Could implement file-based asset types or exclude assets entirely

### File Structure Examples

#### Minimal Valid Structure
```json
{
  "integrationId": "my-scanner",
  "dataSources": [
    {
      "id": "scan-1",
      "assets": [
        {
          "details": {
            "assetEndpoint": {
              "assetId": "file.js",
              "assetName": "file.js"
            }
          },
          "vulnerabilityFindings": [
            {
              "name": "CVE-2024-1234"
            }
          ]
        }
      ]
    }
  ]
}
```

#### With All Optional Fields
```json
{
  "integrationId": "my-scanner",
  "dataSources": [
    {
      "id": "scan-1",
      "analysisDate": "2026-01-26T08:42:51.912Z",
      "assets": [
        {
          "analysisDate": "2026-01-26T08:42:51.912Z",
          "details": {
            "assetEndpoint": {
              "assetId": "file.js",
              "assetName": "src/file.js",
              "host": "src/file.js"
            }
          },
          "vulnerabilityFindings": [
            {
              "name": "CVE-2024-1234",
              "description": "Security vulnerability",
              "severity": "High",
              "externalDetectionSource": "SASTScan"
            }
          ]
        }
      ]
    }
  ]
}
```

### Next Steps

1. Run the diagnostic tools to identify specific issues
2. Update your local schema if needed
3. Try the simplified structure if issues persist
4. Check if alternative asset types work better for your use case
5. Reach out to Wiz support with diagnostic output if issues continue

## CVE-Only Filtering

The --cve-only flag filters findings to only include CVE-YYYY-NNNNN format vulnerabilities.
