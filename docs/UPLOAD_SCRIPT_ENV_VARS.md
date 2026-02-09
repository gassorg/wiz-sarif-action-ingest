# Environment Variables Support in upload_security_scan.py

## Overview

`upload_security_scan.py` now supports Wiz API credentials via environment variables, enabling secure credential management in CI/CD pipelines without exposing secrets in configuration files.

## Environment Variables

The following environment variables are supported:

| Environment Variable | Script Variable | Description | Example |
|---------------------|-----------------|-------------|---------|
| `WIZ_CLIENT_ID` | `CLIENT_ID` | Wiz API client ID | `client_abc123xyz` |
| `WIZ_CLIENT_SECRET` | `CLIENT_SECRET` | Wiz API client secret | `secret_xyz789abc` |
| `WIZ_TOKEN_URL` | `TOKEN_URL` | Wiz authentication endpoint | `https://auth.app.wiz.io/oauth/token` |
| `WIZ_API_ENDPOINT_URL` | `API_ENDPOINT_URL` | Wiz API GraphQL endpoint | `https://api.us17.app.wiz.io/graphql` |

## Credential Resolution Priority

Credentials are resolved in the following order (first match wins):

1. **Environment Variables** (highest priority)
   - `WIZ_CLIENT_ID`, `WIZ_CLIENT_SECRET`, `WIZ_TOKEN_URL`, `WIZ_API_ENDPOINT_URL`
   
2. **Config File** (if provided via `-c` flag)
   - `uploader_config.json` or custom path
   
3. **Hardcoded Defaults** (lowest priority)
   - Empty strings defined at module level

### Example Resolution

```
Scenario: Environment variable + Config file + Hardcoded default

Step 1: Check environment variables
  WIZ_CLIENT_ID = "from_env"  ✓ Found, use this
  
Step 2: Check config file
  "CLIENT_ID": "from_config"  (not used, already have value)
  
Result: CLIENT_ID = "from_env" (environment variable wins)
```

## Usage Examples

### Local Development with Environment Variables

```bash
export WIZ_CLIENT_ID="your-client-id"
export WIZ_CLIENT_SECRET="your-client-secret"
export WIZ_TOKEN_URL="https://auth.app.wiz.io/oauth/token"
export WIZ_API_ENDPOINT_URL="https://api.us17.app.wiz.io/graphql"

# Run upload - uses environment variables
python3 upload_security_scan.py -f scan.wiz.json
```

### With Config File (Fallback)

```bash
# With environment variables (used if set)
python3 upload_security_scan.py -c uploader_config.json -f scan.wiz.json
```

### GitHub Actions Workflow

```yaml
jobs:
  upload-to-wiz:
    runs-on: ubuntu-latest
    env:
      WIZ_CLIENT_ID: ${{ secrets.WIZ_CLIENT_ID }}
      WIZ_CLIENT_SECRET: ${{ secrets.WIZ_CLIENT_SECRET }}
      WIZ_TOKEN_URL: ${{ secrets.WIZ_TOKEN_URL }}
      WIZ_API_ENDPOINT_URL: ${{ secrets.WIZ_API_ENDPOINT_URL }}
    steps:
      - name: Upload to Wiz
        run: python3 upload_security_scan.py -f scan.wiz.json
```

### Docker / Container

```dockerfile
FROM python:3.11

WORKDIR /app
COPY upload_security_scan.py requirements.txt ./

RUN pip install -r requirements.txt

# Pass credentials as build arguments or runtime environment variables
ENV WIZ_CLIENT_ID=""
ENV WIZ_CLIENT_SECRET=""
ENV WIZ_TOKEN_URL=""
ENV WIZ_API_ENDPOINT_URL=""

ENTRYPOINT ["python3", "upload_security_scan.py"]
```

Run with:
```bash
docker run -e WIZ_CLIENT_ID="id" -e WIZ_CLIENT_SECRET="secret" ... image
```

## Security Best Practices

### ✓ Do's

- ✓ Use environment variables in CI/CD pipelines (GitHub Actions, GitLab CI, Jenkins, etc.)
- ✓ Use GitHub Secrets/GitLab CI Variables for credential storage
- ✓ Rotate credentials periodically
- ✓ Use least-privilege API clients (minimal required permissions)
- ✓ Keep `uploader_config.json` out of version control (.gitignore)
- ✓ Audit credential access logs in Wiz

### ✗ Don'ts

- ✗ Don't hardcode credentials in scripts or configuration files
- ✗ Don't commit `uploader_config.json` with real credentials to git
- ✗ Don't log credentials in CI/CD output
- ✗ Don't share credentials between environments
- ✗ Don't use same credentials for multiple purposes

## Implementation Details

### Environment Variable Loading

```python
def load_config_from_env():
    """
    Load Wiz credentials from environment variables.
    Environment variables take precedence over all other sources.
    """
    env_config = {}
    env_mapping = {
        'WIZ_CLIENT_ID': 'CLIENT_ID',
        'WIZ_CLIENT_SECRET': 'CLIENT_SECRET',
        'WIZ_TOKEN_URL': 'TOKEN_URL',
        'WIZ_API_ENDPOINT_URL': 'API_ENDPOINT_URL'
    }
    
    for env_var, config_key in env_mapping.items():
        value = os.environ.get(env_var)
        if value:
            env_config[config_key] = value
    
    return env_config
```

### Config Resolution in Main

```python
# Load environment variables (highest priority)
env_config = load_config_from_env()

# Merge configs: env vars override config file, which overrides defaults
client_id = env_config.get("CLIENT_ID", config.get("CLIENT_ID", CLIENT_ID))
```

## Troubleshooting

### Issue: "Error authenticating to Wiz"

**Possible Causes:**
- Credentials not set (check environment variables)
- Incorrect token URL for your Wiz region
- Client credentials invalid or expired

**Solution:**
```bash
# Verify environment variables are set
echo $WIZ_CLIENT_ID
echo $WIZ_TOKEN_URL

# Test authentication manually
curl -X POST $WIZ_TOKEN_URL \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "grant_type=client_credentials&audience=wiz-api&client_id=$WIZ_CLIENT_ID&client_secret=$WIZ_CLIENT_SECRET"
```

### Issue: Config File Ignored

**Cause:** Environment variables take precedence

**Solution:** If you want to use config file exclusively, unset environment variables:
```bash
unset WIZ_CLIENT_ID
unset WIZ_CLIENT_SECRET
unset WIZ_TOKEN_URL
unset WIZ_API_ENDPOINT_URL

python3 upload_security_scan.py -c uploader_config.json -f scan.wiz.json
```

### Issue: Credentials Not Found

Check resolution priority:
```bash
# 1. Check environment variables
env | grep WIZ_

# 2. Check config file exists
ls -la uploader_config.json

# 3. Check hardcoded defaults (if applicable)
grep "^CLIENT_ID = " upload_security_scan.py
```

## Migration Guide

### From Config File Only → Environment Variables

**Before:**
```bash
python3 upload_security_scan.py -c uploader_config.json -f scan.wiz.json
```

**After (GitHub Secrets):**
1. Add repository secrets (WIZ_CLIENT_ID, etc.)
2. Update workflow to pass secrets as environment variables
3. Run without config file:
```bash
python3 upload_security_scan.py -f scan.wiz.json
```

### From Hardcoded Values → Environment Variables

**Before:**
```python
# In script
CLIENT_ID = "abc123"
CLIENT_SECRET = "xyz789"
```

**After:**
```bash
export WIZ_CLIENT_ID="abc123"
export WIZ_CLIENT_SECRET="xyz789"

python3 upload_security_scan.py -f scan.wiz.json
```

## Integration Examples

### GitHub Actions with Secrets

```yaml
name: Upload to Wiz

on: [push]

jobs:
  upload:
    runs-on: ubuntu-latest
    env:
      WIZ_CLIENT_ID: ${{ secrets.WIZ_CLIENT_ID }}
      WIZ_CLIENT_SECRET: ${{ secrets.WIZ_CLIENT_SECRET }}
      WIZ_TOKEN_URL: ${{ secrets.WIZ_TOKEN_URL }}
      WIZ_API_ENDPOINT_URL: ${{ secrets.WIZ_API_ENDPOINT_URL }}
    steps:
      - uses: actions/checkout@v3
      - name: Upload scan
        run: python3 upload_security_scan.py -f scan.wiz.json
```

### GitLab CI/CD

```yaml
upload_to_wiz:
  image: python:3.11
  script:
    - pip install -r requirements.txt
    - python3 upload_security_scan.py -f scan.wiz.json
  variables:
    WIZ_CLIENT_ID: $CI_JOB_TOKEN
    WIZ_CLIENT_SECRET: $WIZ_SECRET
    WIZ_TOKEN_URL: https://auth.app.wiz.io/oauth/token
    WIZ_API_ENDPOINT_URL: https://api.us17.app.wiz.io/graphql
```

### Jenkins Pipeline

```groovy
pipeline {
    agent any
    environment {
        WIZ_CLIENT_ID = credentials('wiz-client-id')
        WIZ_CLIENT_SECRET = credentials('wiz-client-secret')
        WIZ_TOKEN_URL = 'https://auth.app.wiz.io/oauth/token'
        WIZ_API_ENDPOINT_URL = 'https://api.us17.app.wiz.io/graphql'
    }
    stages {
        stage('Upload') {
            steps {
                sh 'python3 upload_security_scan.py -f scan.wiz.json'
            }
        }
    }
}
```

## See Also

- [SARIF to Wiz Converter](README.md)
- [GitHub Action Guide](GITHUB_ACTION_GUIDE.md)
- [Wiz API Documentation](https://docs.wiz.io/dev/api-overview)
