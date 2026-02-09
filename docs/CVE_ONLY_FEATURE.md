# CVE-Only Filtering Feature

## Overview

The `--cve-only` flag enables you to filter findings to include only those with CVE identifiers in the standard CVE-YYYY-NNNNN format. This is useful for focusing on known vulnerabilities while excluding proprietary or unidentified issues.

## Usage

### Basic Command

```bash
python sarif_to_wiz_converter.py \
  --input scan.sarif \
  --output scan.wiz.json \
  --cve-only
```

### With Repository Information

```bash
python sarif_to_wiz_converter.py \
  --input scan.sarif \
  --output scan.wiz.json \
  --repository-name "my-repo" \
  --repository-url "https://github.com/org/my-repo" \
  --cve-only
```

### Batch Processing

```bash
python sarif_to_wiz_converter.py \
  --input-dir ./sarif-results \
  --output-dir ./wiz-results \
  --cve-only
```

## How It Works

### CVE Detection

The converter searches for CVE patterns (CVE-YYYY-NNNNN) in:

1. **ruleId field** - Primary location for vulnerability identifiers
   - Example: `CVE-2022-0235_node-fetch_2.6.1`

2. **message.text field** - Vulnerability description
   - Example: `[CVE-2022-0235] moo-cdk-lib 51.5.0 (all-builds)`

3. **properties dict values** - Additional metadata
   - Searches all string values in the properties object

### Pattern Matching

- Pattern: `CVE-\d{4}-\d{4,}` (case-insensitive)
- Valid examples: `CVE-2022-0235`, `CVE-2024-12345`
- Invalid examples: `CVE-22-0235`, `CVE-2022-123` (insufficient digits)

## Output Behavior

### Filtering

When `--cve-only` is enabled:
- Only findings containing the CVE pattern are included in output
- Non-matching findings are excluded
- A log message shows how many findings were filtered

### Name Simplification

Finding names are simplified to include only the CVE identifier:

| Input Name | Output Name |
|---|---|
| `CVE-2022-0235_node-fetch_2.6.1` | `CVE-2022-0235` |
| `CVE-2024-12345_library_version` | `CVE-2024-12345` |
| `CVE-2022-5678_pkg_1.0.0_fix_1.1.0` | `CVE-2022-5678` |

The same simplification is applied to the finding `id` field.

## Logging

When using `--cve-only`, the converter logs filtering statistics:

```
CVE-only filter: Excluded 30 non-CVE findings
```

This helps you understand the impact of the filtering on your results.

### Example Output with Verbose Mode

```
2026-02-04 13:15:06,378 - INFO - Processing: inputs/sarif.json
2026-02-04 13:15:06,393 - INFO - ✓ SARIF input validation passed
2026-02-04 13:15:06,394 - INFO - CVE-only filter: Excluded 30 non-CVE findings
2026-02-04 13:15:06,394 - INFO - ✓ Wiz output validation passed
2026-02-04 13:15:06,396 - INFO - ✓ Successfully converted to: scan.wiz.json
```

## Use Cases

### 1. Focus on Known Vulnerabilities

When you only want to track officially identified CVE vulnerabilities:

```bash
python sarif_to_wiz_converter.py \
  --input dependency-scan.sarif \
  --output known-cves.wiz.json \
  --cve-only
```

### 2. Compliance Reporting

Many compliance frameworks (PCI-DSS, HIPAA, SOC2) focus on CVE-based vulnerabilities:

```bash
python sarif_to_wiz_converter.py \
  --input-dir ./scans \
  --output-dir ./compliance-cves \
  --cve-only
```

### 3. Reduce Alert Noise

Filter out proprietary or research-grade findings to reduce alert fatigue:

```bash
python sarif_to_wiz_converter.py \
  --input scan.sarif \
  --output cves-only.wiz.json \
  --cve-only \
  --verbose
```

### 4. CVE Database Integration

Prepare findings for correlation with external CVE databases:

```bash
# Convert and filter to CVEs only
python sarif_to_wiz_converter.py \
  --input security-scan.sarif \
  --output cve-findings.wiz.json \
  --cve-only

# Then integrate with NIST NVD, VulnDB, or other CVE sources
```

## Examples

### Example 1: Simple Conversion

**Input SARIF** (simplified):
```json
{
  "runs": [{
    "results": [
      {
        "ruleId": "CVE-2022-0235_node-fetch_2.6.1",
        "message": {"text": "[CVE-2022-0235] moo-cdk-lib..."},
        "locations": [{"physicalLocation": {"artifactLocation": {"uri": "package.json"}}}]
      },
      {
        "ruleId": "CUSTOM-ISSUE-001",
        "message": {"text": "Custom security finding"},
        "locations": [...]
      }
    ]
  }]
}
```

**Command**:
```bash
python sarif_to_wiz_converter.py --input input.sarif --output output.wiz.json --cve-only
```

**Output**:
```
Processing: input.sarif
CVE-only filter: Excluded 1 non-CVE findings
✓ Successfully converted to: output.wiz.json
```

The resulting output contains only the CVE-2022-0235 finding.

### Example 2: Batch Processing with Repository Info

```bash
python sarif_to_wiz_converter.py \
  --input-dir ./sarif-results \
  --output-dir ./wiz-results \
  --repository-name "security-scanner" \
  --repository-url "https://github.com/org/security-scanner" \
  --cve-only \
  --verbose
```

## Combining with Other Flags

The `--cve-only` flag works with all other converter options:

```bash
# With custom schemas
python sarif_to_wiz_converter.py \
  --input scan.sarif \
  --output output.wiz.json \
  --sarif-schema custom-sarif-schema.json \
  --wiz-schema custom-wiz-schema.json \
  --cve-only

# With custom integration ID and repository
python sarif_to_wiz_converter.py \
  --input scan.sarif \
  --output output.wiz.json \
  --integration-id my-scanner-v2 \
  --repository-name my-repo \
  --repository-url https://github.com/org/my-repo \
  --cve-only

# With verbose logging
python sarif_to_wiz_converter.py \
  --input-dir ./scans \
  --output-dir ./results \
  --cve-only \
  --verbose
```

## Troubleshooting

### No findings in output

If your output has no findings after using `--cve-only`:

1. **Check your SARIF input**: Verify that the findings contain CVE patterns
   ```bash
   grep -i "cve-" input.sarif
   ```

2. **Check pattern locations**: CVE identifiers may be in different fields
   - Look in `ruleId`, `message.text`, and `properties` fields
   - Ensure the format matches CVE-YYYY-NNNNN

3. **Use verbose mode** to see filtering details:
   ```bash
   python sarif_to_wiz_converter.py --input scan.sarif --output out.wiz.json --cve-only --verbose
   ```

### Unexpected findings excluded

If valid CVE findings are being excluded:

1. **Verify the CVE format**: Check that CVE identifiers follow CVE-YYYY-NNNNN format
   - Must have exactly 4 digits for year
   - Must have 4+ digits for sequence number
   - Example: `CVE-2022-0235` ✓, `CVE-22-235` ✗

2. **Check field locations**: Ensure the CVE identifier is in one of these fields:
   - `result.ruleId`
   - `result.message.text`
   - `result.properties.*`

3. **Inspect the SARIF file** to understand your data structure

## Performance Considerations

- **Filtering overhead**: Minimal - adds only regex pattern matching
- **Output size**: Typically 50-90% reduction in file size with CVE-only filtering
- **Processing time**: Negligible impact; main processing time is schema validation

## Related Features

- **Repository Mode**: Use with `--repository-name` and `--repository-url` for code-based findings
- **Custom Mapping**: Combine with `--mapping-config` for field customization
- **Verbose Logging**: Use `--verbose` for detailed execution information
- **Custom Schemas**: Use `--sarif-schema` and `--wiz-schema` for schema customization
