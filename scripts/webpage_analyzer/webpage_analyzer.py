#!/usr/bin/env python3

"""
Webpage Analyzer - AI-powered Website Classification Tool

This script analyzes web pages using Claude Haiku to categorize and classify content based on
configurable categories. It handles dynamic content with Selenium and sends Discord notifications
for specific categories of interest. Designed for automated content analysis workflows.

Features:
- Dynamic content analysis with Selenium WebDriver
- AI-powered categorization using Claude Haiku via PydanticAI
- Configurable category definitions and notification filters
- Discord notifications via discord-notify library
- Integration with reconnaissance pipelines

Usage:
    python3 webpage_analyzer.py -u https://example.com -c config.yaml
    echo "https://example.com" | python3 webpage_analyzer.py
"""

import sys
import yaml
import argparse
import requests
import os
from urllib.parse import urljoin, urlparse
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import time
from discord_notify import Notifier
from pydantic_ai import Agent
from pydantic_ai.models.anthropic import AnthropicModel
from pydantic_ai.providers.anthropic import AnthropicProvider
from pydantic import BaseModel
from typing import List, Dict, Optional

class CategoryAnalysis(BaseModel):
    """Result structure for webpage analysis"""
    matched_category: str
    confidence_score: float
    summary: str

class WebpageAnalyzer:
    def __init__(self, config_file='config.yaml'):
        self.config = self.load_config(config_file)
        self.driver = None
        self.finding = None
        self.agent = None

    def load_config(self, config_file):
        try:
            with open(config_file, 'r') as f:
                return yaml.safe_load(f)
        except FileNotFoundError:
            print(f"Config file {config_file} not found. Please create it using the sample config.")
            sys.exit(1)

    def setup_ai_agent(self):
        """Initialize PydanticAI agent with Claude Haiku"""
        api_key = self.config.get('anthropic_api_key')
        if not api_key or 'YOUR_API_KEY' in api_key:
            print("Anthropic API key not configured, AI analysis disabled")
            return False
            
        try:
            self.agent = Agent(
                model=AnthropicModel(
                    'claude-3-haiku-20240307',
                    provider=AnthropicProvider(api_key=api_key)
                ),
                output_type=CategoryAnalysis,
                system_prompt="""You are a webpage content analyzer. Your job is to categorize web pages based on their content, title, and URL. 
                
Analyze the webpage content and determine which predefined categories apply. Consider:
- Page title and headings
- Form elements and input fields
- Navigation and UI elements
- Technical terminology and jargon
- URLs and link patterns
- Overall page purpose and functionality

Provide confidence scores between 0.0 and 1.0 for each matching category. Only include categories with confidence >= 0.3.
Summarize the page purpose in 1-2 sentences."""
            )
            return True
            
        except Exception as e:
            print(f"Failed to initialize AI agent: {e}")
            return False

    def setup_webdriver(self):
        options = Options()
        options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-gpu')
        options.add_argument('--window-size=1920,1080')
        options.add_argument('--user-agent=Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36')
        
        self.driver = webdriver.Chrome(options=options)
        self.driver.set_page_load_timeout(30)

    def extract_content(self, url):
        """Extract and clean webpage content for analysis"""
        try:
            # Load page with Selenium to handle dynamic content
            self.driver.get(url)
            
            # Wait for page to load and execute JavaScript
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            
            # Wait a bit more for async content to load
            time.sleep(3)
            
            # Get final page source after JS execution
            page_source = self.driver.page_source
            soup = BeautifulSoup(page_source, 'html.parser')
            
            # Extract text content and metadata
            title = soup.find('title').get_text() if soup.find('title') else ''
            
            # Remove script and style elements
            for script in soup(["script", "style"]):
                script.decompose()
                
            # Get main text content
            text_content = soup.get_text()
            
            # Clean up text
            lines = (line.strip() for line in text_content.splitlines())
            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
            text_content = ' '.join(chunk for chunk in chunks if chunk)
            
            return {
                'title': title.strip(),
                'content': text_content[:5000],  # Limit content for AI analysis
                'url': url
            }
            
        except Exception as e:
            print(f"Error extracting content from {url}: {e}")
            return None

    def analyze_content(self, content_data):
        """Analyze webpage content using Claude Haiku"""
        if not self.agent:
            print("AI agent not configured, skipping analysis")
            return None
            
        categories = self.config.get('categories', {})
        if not categories:
            print("No categories configured")
            return None
            
        # Prepare prompt with category definitions
        category_definitions = "\n".join([
            f"- {cat_id}: {cat_info['description']}" 
            for cat_id, cat_info in categories.items()
        ])
        
        available_categories = list(categories.keys())
        
        prompt = f"""Analyze the following webpage and categorize it using ONLY these predefined categories:

AVAILABLE CATEGORIES:
{category_definitions}

WEBPAGE DATA:
Title: {content_data['title']}
URL: {content_data['url']}
Content: {content_data['content'][:3000]}

IMPORTANT: You must select the matched_category from this exact list: {available_categories}

If none of the predefined categories fit well, choose the closest match from the available options.

Return the results in the specified format with:
- matched_category: Must be one of these exact category IDs: {available_categories}
- confidence_score: Confidence score (0.0-1.0) for the matched category
- summary: Brief description of what this webpage appears to be (1-2 sentences)

Choose only ONE category from the predefined list that best represents the primary purpose or nature of this webpage."""
        
        try:
            result = self.agent.run_sync(prompt)
            return result.output
            
        except Exception as e:
            print(f"Error during AI analysis: {e}")
            return CategoryAnalysis(
                matched_category="",
                confidence_score=0.0,
                summary=f"Analysis failed: {str(e)}",
            )

    def analyze_url(self, url):
        """Main analysis function for a single URL"""
        print(f"Analyzing webpage: {url}")
        
        # Extract content
        content_data = self.extract_content(url)
        if not content_data:
            return
            
        # Analyze with AI
        analysis = self.analyze_content(content_data)
        if analysis:
            self.finding = {
                'url': url,
                'title': content_data['title'],
                'analysis': analysis,
                'timestamp': time.time()
            }

    def should_notify(self, analysis):
        """Check if analysis results warrant notification"""
        notify_categories = self.config.get('notify_categories', [])
        if not notify_categories:
            return False
            
        return analysis.matched_category in notify_categories

    def output_findings(self):
        """Output findings to STDOUT"""
        if not self.finding:
            print("No analysis results.")
            return
            
        print(f"\n=== WEBPAGE ANALYSIS RESULTS ===")
        
        print(f"🌐 {self.finding['title']}")
        print(f"   URL: {self.finding['url']}")
        print(f"   Category: {self.finding['analysis'].matched_category} (confidence: {self.finding['analysis'].confidence_score:.2f})")
        print(f"   Summary: {self.finding['analysis'].summary}")
        print()

    def notify_discord(self):
        """Send findings to Discord via discord_notify"""
        if not self.finding:
            return
            
        # Check if finding should be notified
        if not self.should_notify(self.finding['analysis']):
            print("Finding does not match notification criteria")
            return
            
        webhook_url = self.config.get('discord_webhook_url')
        if not webhook_url or 'YOUR_WEBHOOK_URL' in webhook_url:
            print("Discord webhook not configured, skipping Discord notification")
            return
            
        # Prepare Discord message
        message = f"🤖 **Webpage Analysis Result** \n\n"
        message += f"**{self.finding['title']}**\n"
        message += f"• Category: {self.finding['analysis'].matched_category} (confidence: {self.finding['analysis'].confidence_score:.2f})\n"
        message += f"• URL: {self.finding['url']}\n"
        message += f"• Summary: {self.finding['analysis'].summary}\n\n"
        
        try:
            # Use discord-notify library
            notifier = Notifier(webhook_url)
            notifier.send(message, print_message=False)
            print("Discord notification sent successfully")
                
        except Exception as e:
            print(f"Error sending Discord notification: {e}")

    def cleanup(self):
        """Cleanup webdriver"""
        if self.driver:
            self.driver.quit()

def main():
    parser = argparse.ArgumentParser(description="Analyze and categorize webpages using AI")
    parser.add_argument('-u', '--url', help='URL to analyze')
    parser.add_argument('-c', '--config', default='config.yaml', help='Config file path')
    
    args = parser.parse_args()
    
    # If config path is relative, make it relative to script directory
    if not os.path.isabs(args.config):
        script_dir = os.path.dirname(os.path.abspath(__file__))
        args.config = os.path.join(script_dir, args.config)
    
    # Get URL from argument or stdin
    if args.url:
        url = args.url
    else:
        url = sys.stdin.read().strip()
        
    if not url:
        print("Error: No URL provided. Use -u parameter or pipe URL to stdin.")
        sys.exit(1)
        
    # Validate URL
    if not url.startswith(('http://', 'https://')):
        url = 'https://' + url
    
    analyzer = WebpageAnalyzer(args.config)
    
    try:
        analyzer.setup_ai_agent()
        analyzer.setup_webdriver()
        analyzer.analyze_url(url)
        analyzer.output_findings()
        analyzer.notify_discord()
        
    except KeyboardInterrupt:
        print("\nInterrupted by user")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        analyzer.cleanup()

if __name__ == '__main__':
    main()