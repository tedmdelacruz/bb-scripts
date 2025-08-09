# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a collection of bug bounty and reconnaissance scripts for security testing. The repository contains Python utilities and bash scripts for subdomain enumeration, web reconnaissance, and security assessment workflows.

## Key Components

### Python Scripts
- **cname_domain_finder.py**: Multi-threaded CNAME record gathering tool that reads domains from stdin and outputs unique CNAME records. Supports concurrent processing with `-t` flag.
- **js_downloader.py**: JavaScript file discovery and download tool using BeautifulSoup. Filters out common libraries and saves JS files with source attribution.

### Bash Script Categories

**Reconnaissance Tools** (`bin/`):
- `scan`: Primary subdomain enumeration using subfinder, with httpx probing and anew for filtering new results
- `probe`: Web server fuzzing using waybackurls, ffuf with multiple wordlists, and arjun for parameter discovery
- `apiprobe`: Simplified version of probe focused on API endpoints
- `livemonitor`: Daily monitoring for new HTTP 200 responses, with diff tracking and notifications
- `jsmonitor`: Hourly JS/JSON file monitoring with diff detection using js-beautify

**Utility Tools**:
- `403bypass`: Generates URL variations for HTTP 403 bypass attempts
- `screenshot`: Takes screenshots using gowitness from http.txt files
- `github-search`: Generates GitHub/Gist search URLs for code analysis
- `dorks`: Comprehensive GitHub dorking for secrets and integration discovery

## Directory Structure

- `bin/`: Executable bash scripts for reconnaissance workflows
- `js-files/`: Output directory for downloaded JavaScript files (created by js_downloader.py)
- Python scripts are in root directory

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

### Python Script Usage
```bash
# CNAME gathering with threading
cat domains.txt | python3 cname_domain_finder.py -t 10 output.txt

# JS file downloading
cat urls.txt | python3 js_downloader.py -t 5 -v
```

### Monitoring Setup
Scripts are designed for cron automation:
- `livemonitor`: Daily execution for new subdomain discovery
- `jsmonitor`: Hourly for JS file change detection

## Security Context

These are defensive security research tools for authorized testing only. All scripts implement standard reconnaissance techniques used in bug bounty programs and security assessments.