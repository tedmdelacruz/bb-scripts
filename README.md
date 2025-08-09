# Bug Bounty Scripts

This is a collection of bug bounty and reconnaissance scripts for security testing. The repository contains Python utilities and bash scripts for subdomain enumeration, web reconnaissance, and security assessment workflows.

## Key Components

### Python Scripts (`python-scripts/`)
- **cname_domain_finder.py**: Multi-threaded CNAME record gathering tool that reads domains from stdin and outputs unique CNAME records. Supports concurrent processing with `-t` flag.
- **js_downloader.py**: JavaScript file discovery and download tool using BeautifulSoup. Filters out common libraries and saves JS files with source attribution.
- **keyword_hunter.py**: Selenium-based keyword hunting tool that analyzes web pages and JavaScript files for sensitive information using regex patterns. Supports Discord notifications via discord-notify library.

### Bash Script Categories

**Reconnaissance Tools** (`bin/`):
- `scan`: Primary subdomain enumeration using subfinder, with httpx probing and anew for filtering new results
- `probe`: Web server fuzzing using waybackurls, ffuf with multiple wordlists, and arjun for parameter discovery
- `apiprobe`: Simplified version of probe focused on API endpoints
- `livemonitor`: Daily monitoring for new HTTP 200 responses, with diff tracking, notifications, and automatic keyword hunting on new discoveries
- `jsmonitor`: Hourly JS/JSON file monitoring with diff detection using js-beautify

**Utility Tools**:
- `403bypass`: Generates URL variations for HTTP 403 bypass attempts
- `screenshot`: Takes screenshots using gowitness from http.txt files
- `github-search`: Generates GitHub/Gist search URLs for code analysis
- `dorks`: Comprehensive GitHub dorking for secrets and integration discovery

## Directory Structure

- `bin/`: Executable bash scripts for reconnaissance workflows
- `python-scripts/`: Python utilities and configuration files
  - `config.yaml`: Configuration for keyword_hunter.py (keywords, Discord webhook)
  - `config.yaml.sample`: Sample configuration with comprehensive security patterns
  - `requirements.txt`: Python dependencies
- `js-files/`: Output directory for downloaded JavaScript files (created by js_downloader.py)

## Common Usage Patterns

### Reconnaissance Workflow
Scripts expect a standardized directory structure under `$HOME/recon/$TARGET/`:
- `subdomains.txt`: Master list of discovered subdomains
- `http.txt`: Live web servers (HTTP responses)
- `wildcards.txt`: Wildcard domains for subfinder
- `.tmp/`: Temporary processing files
- `.history/`: Historical data for monitoring
- `screenshots/`: Screenshot output directory

### Dependencies
Scripts rely on external tools:
- `subfinder`, `httpx`, `anew` for subdomain work
- `ffuf`, `waybackurls`, `gau`, `arjun` for web fuzzing
- `gowitness` for screenshots
- `js-beautify` for JS monitoring
- `notify` for alerting
- `chromium-driver` for Selenium-based keyword hunting
- Python packages: `selenium`, `beautifulsoup4`, `PyYAML`, `requests`, `discord-notify`

### Python Script Usage
```bash
# CNAME gathering with threading
cat domains.txt | python3 python-scripts/cname_domain_finder.py -t 10 output.txt

# JS file downloading
cat urls.txt | python3 python-scripts/js_downloader.py -t 5 -v

# Keyword hunting on single URL
python3 python-scripts/keyword_hunter.py -u https://example.com -c python-scripts/config.yaml

# Keyword hunting from stdin
echo "https://example.com" | python3 python-scripts/keyword_hunter.py -c python-scripts/config.yaml
```

### Monitoring Setup
Scripts are designed for cron automation:
- `livemonitor`: Daily execution for new subdomain discovery with automatic keyword hunting
- `jsmonitor`: Hourly for JS file change detection

### Keyword Hunting Configuration
The `keyword_hunter.py` script uses `config.yaml` for:
- **Discord webhook URL**: For automated notifications
- **Keyword patterns**: Regex patterns grouped by category (API keys, secrets, internal URLs, etc.)
- **Sample patterns included**: JWT tokens, AWS credentials, Vite/Directus environment variables, GitHub tokens

### Integration Features
- **Automated workflow**: `livemonitor` automatically runs keyword hunting on newly discovered websites
- **Discord notifications**: Real-time alerts for security findings
- **Library filtering**: Ignores common JavaScript libraries to reduce noise
- **Async JS support**: Uses Selenium for dynamic content analysis

## Security Context

These are defensive security research tools for authorized testing only. All scripts implement standard reconnaissance techniques used in bug bounty programs and security assessments.