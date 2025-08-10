# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a collection of bug bounty and reconnaissance scripts for security testing. The repository contains Python utilities and bash scripts for subdomain enumeration, web reconnaissance, and security assessment workflows.

## Key Components

### Python Scripts (`scripts/`)
- **cname_domain_finder.py**: Multi-threaded CNAME record gathering tool that reads domains from stdin and outputs unique CNAME records. Supports concurrent processing with `-t` flag.
- **js_downloader.py**: JavaScript file discovery and download tool using BeautifulSoup. Filters out common libraries and saves JS files with source attribution.
- **keyword_hunter/keyword_hunter.py**: Selenium-based keyword hunting tool that analyzes web pages and JavaScript files for sensitive information using regex patterns. Supports Discord notifications via discord-notify library.
- **webpage_analyzer/webpage_analyzer.py**: AI-powered webpage classification tool using Claude Haiku via PydanticAI. Categorizes web content based on configurable categories with Discord notifications for matches.

### Bash Script Categories

**Reconnaissance Tools** (`bin/`):
- `scan`: Primary subdomain enumeration using subfinder, with httpx probing and anew for filtering new results
- `probe`: Web server fuzzing using waybackurls, ffuf with multiple wordlists, and arjun for parameter discovery
- `apiprobe`: Simplified version of probe focused on API endpoints
- `livemonitor`: Daily monitoring for new HTTP 200 responses, with diff tracking, notifications, automatic keyword hunting, and AI-powered webpage analysis on new discoveries
- `jsmonitor`: Hourly JS/JSON file monitoring with diff detection using js-beautify

**Utility Tools**:
- `403bypass`: Generates URL variations for HTTP 403 bypass attempts
- `screenshot`: Takes screenshots using gowitness from http.txt files
- `github-search`: Generates GitHub/Gist search URLs for code analysis
- `dorks`: Comprehensive GitHub dorking for secrets and integration discovery

## Directory Structure

- `bin/`: Executable bash scripts for reconnaissance workflows
- `scripts/`: Python utilities and configuration files
  - `cname_domain_finder.py`: CNAME record discovery tool
  - `js_downloader.py`: JavaScript file discovery and download tool
  - `keyword_hunter/`: Keyword hunting module
    - `keyword_hunter.py`: Main security analysis script
    - `config.yaml`: Configuration for keywords and Discord webhook
    - `config.yaml.sample`: Sample configuration with comprehensive security patterns
    - `requirements.txt`: Python dependencies
  - `webpage_analyzer/`: AI-powered webpage analysis module
    - `webpage_analyzer.py`: Claude Haiku-based webpage classification script
    - `config.yaml`: Configuration for categories and Discord webhook  
    - `config.yaml.sample`: Sample configuration with security-focused categories
    - `requirements.txt`: Python dependencies including PydanticAI
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
- `chromium-driver` for Selenium-based analysis tools
- Python packages: `selenium`, `beautifulsoup4`, `PyYAML`, `requests`, `discord-notify`, `pydantic-ai`

### Python Script Usage
```bash
# CNAME gathering with threading
cat domains.txt | python3 scripts/cname_domain_finder.py -t 10 output.txt

# JS file downloading
cat urls.txt | python3 scripts/js_downloader.py -t 5 -v

# Keyword hunting on single URL
python3 scripts/keyword_hunter/keyword_hunter.py -u https://example.com -c scripts/keyword_hunter/config.yaml

# Keyword hunting from stdin
echo "https://example.com" | python3 scripts/keyword_hunter/keyword_hunter.py -c scripts/keyword_hunter/config.yaml

# AI-powered webpage analysis
python3 scripts/webpage_analyzer/webpage_analyzer.py -u https://example.com -c scripts/webpage_analyzer/config.yaml

# Webpage analysis from stdin
echo "https://example.com" | python3 scripts/webpage_analyzer/webpage_analyzer.py
```

### Monitoring Setup
Scripts are designed for cron automation:
- `livemonitor`: Daily execution for new subdomain discovery with automatic keyword hunting and AI webpage analysis
- `jsmonitor`: Hourly for JS file change detection

### Keyword Hunting Configuration
The `keyword_hunter/keyword_hunter.py` script uses `config.yaml` for:
- **Discord webhook URL**: For automated notifications
- **Keyword patterns**: Regex patterns grouped by category (API keys, secrets, internal URLs, etc.)
- **Sample patterns included**: JWT tokens, AWS credentials, GitHub tokens

### Webpage Analysis Configuration
The `webpage_analyzer/webpage_analyzer.py` script uses `config.yaml` for:
- **Anthropic API key**: For Claude Haiku AI model access
- **Discord webhook URL**: For automated notifications
- **Category definitions**: Configurable website categories (login portals, admin panels, etc.)
- **Notification filters**: Specify which categories trigger Discord alerts

### Integration Features
- **Dual analysis workflow**: `livemonitor` automatically runs both keyword hunting and AI webpage analysis on newly discovered websites
- **AI-powered categorization**: Uses Claude Haiku to classify webpage content and purpose
- **Smart notifications**: Separate Discord channels for regex-based findings and AI classifications
- **Library filtering**: Ignores common JavaScript libraries to reduce noise
- **Async JS support**: Uses Selenium for dynamic content analysis
- **Self-contained configs**: Scripts automatically use config files from their own directories

## Security Context

These are defensive security research tools for authorized testing only. All scripts implement standard reconnaissance techniques used in bug bounty programs and security assessments.