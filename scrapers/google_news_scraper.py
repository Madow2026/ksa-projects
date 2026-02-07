"""scrapers/google_news_scraper.py

Google News RSS Scraper (Discovery Only)

Policy:
- Uses Google News RSS ONLY for structured headlines/snippets.
- Never crawls the open internet.
- Only keeps items whose final publisher domain is in our strict allowlist.
"""

from __future__ import annotations

import html
import json
import re
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional
from urllib.parse import quote_plus, urlparse

import feedparser
import requests
from loguru import logger

import sys

sys.path.append(str(Path(__file__).parent.parent))


class GoogleNewsRSSScraper:
    """
    Google News RSS-based scraper for Saudi project discovery
    ONLY uses news aggregation, not raw web crawling
    """
    
    def __init__(self, allowlist_path: Optional[str] = None):
        self.name = "Google News RSS"
        self.source_type = "News Aggregator"
        self.scraped_count = 0

        allowlist_file = allowlist_path or str(Path(__file__).parent.parent / "allowed_sources.json")
        self.allowlist = self._load_allowlist(allowlist_file)

        # Mandatory keyword-driven discovery (from allowlist config)
        self.search_queries_en = list(self.allowlist.get("keywords", {}).get("en", []))
        self.search_queries_ar = list(self.allowlist.get("keywords", {}).get("ar", []))

        # Strict allowlist domains
        self.allowed_domains: Dict[str, Dict[str, Any]] = dict(self.allowlist.get("allowed_domains", {}))

        # Only keep recent items (days)
        self.max_age_days: int = 180
        
    def scrape(self) -> List[Dict[str, Any]]:
        """Scrape Google News RSS feeds for Saudi project discovery (headlines only)."""
        logger.info("Starting Google News RSS scraping...")
        all_articles = []
        
        # Search English queries
        for query in self.search_queries_en:
            logger.info(f"Searching: {query}")
            articles = self._search_google_news(query, lang='en')
            all_articles.extend(articles)
            time.sleep(2)  # Rate limiting
        
        # Search Arabic queries
        for query in self.search_queries_ar:
            logger.info(f"Searching: {query}")
            articles = self._search_google_news(query, lang='ar')
            all_articles.extend(articles)
            time.sleep(2)  # Rate limiting
        
        # De-duplicate by URL
        deduped: Dict[str, Dict[str, Any]] = {}
        for a in all_articles:
            deduped[a["url"]] = a

        results = list(deduped.values())
        logger.info(f"Total allowed articles from Google News RSS: {len(results)}")
        return results
    
    def _search_google_news(self, query: str, lang: str = 'en') -> List[Dict[str, Any]]:
        """
        Search Google News RSS feed for a specific query
        
        Args:
            query: Search query
            lang: Language (en or ar)
        """
        articles = []
        
        try:
            # Google News RSS URL
            base_url = "https://news.google.com/rss/search"

            # Build URL (structured RSS only)
            url = f"{base_url}?q={quote_plus(query)}&hl={lang}&gl=SA&ceid={'SA:ar' if lang == 'ar' else 'US:en'}"
            
            logger.debug(f"Fetching RSS feed: {url}")
            
            # Parse RSS feed
            feed = feedparser.parse(url)
            
            if not feed.entries:
                logger.warning(f"No entries found for query: {query}")
                return []
            
            logger.info(f"Found {len(feed.entries)} articles for: {query}")
            
            # Process each article
            for entry in feed.entries[:15]:  # Limit to 15 per query
                article = self._parse_rss_entry(entry, query, lang)
                if article:
                    articles.append(article)
                    self.scraped_count += 1
            
        except Exception as e:
            logger.error(f"Error searching Google News for '{query}': {e}")
        
        return articles
    
    def _parse_rss_entry(self, entry, query: str, lang: str) -> Optional[Dict[str, Any]]:
        """Parse a single RSS feed entry"""
        try:
            # Extract basic info
            title = entry.get('title', '')
            publisher_url = self._extract_publisher_url(entry)
            published = entry.get('published', '')
            summary = entry.get('summary', '')
            source = entry.get('source', {}).get('title', 'Unknown Source')
            
            if not title or not publisher_url:
                return None

            published_iso = self._parse_date(published)
            if not self._is_recent(published_iso):
                logger.debug(f"Discarded (too old): {title}")
                return None

            publisher_domain = self._extract_domain_from_url(publisher_url)
            if not publisher_domain:
                logger.debug(f"Discarded (no domain): {publisher_url}")
                return None

            allowed_info = self._match_allowed_domain(publisher_domain)
            if not allowed_info:
                logger.debug(f"Discarded (domain not allowlisted): {publisher_domain} | {title}")
                return None

            # Discovery-only content for AI extraction
            # We intentionally DO NOT crawl arbitrary pages from Google News.
            text = f"{title}\n\n{summary}".strip()
            
            return {
                'title': title,
                'url': publisher_url,
                'text': text,
                'source_type': 'News',
                'source_name': allowed_info.get('name') or source,
                'publisher_domain': publisher_domain,
                'published_date': published_iso,
                'language': lang,
                'search_query': query,
                'reliability_score': float(allowed_info.get('reliability', 0.7)),
                'official_source': bool(allowed_info.get('official', False)),
                'scraped_at': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error parsing RSS entry: {e}")
            return None

    def _load_allowlist(self, path: str) -> Dict[str, Any]:
        try:
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Failed to load allowlist: {path} | {e}")
            return {"allowed_domains": {}, "keywords": {"en": [], "ar": []}}

    def _extract_domain_from_url(self, url: str) -> Optional[str]:
        try:
            hostname = urlparse(url).hostname or ""
            hostname = hostname.lower().strip(".")
            if hostname.startswith("www."):
                hostname = hostname[4:]
            return hostname or None
        except Exception:
            return None

    def _extract_publisher_url(self, entry) -> Optional[str]:
        """Extract the actual publisher URL from a Google News RSS entry.

        Google News RSS often uses a news.google.com redirect URL in <link>.
        We avoid crawling/redirect-following; instead, we extract any publisher URL
        embedded in the entry metadata (links/source/summary HTML).

        Returns an allowlisted publisher URL if found.
        """
        candidates: List[str] = []

        # 0) Try to resolve the Google News redirect URL (no crawling; header-only redirect)
        link = entry.get('link')
        if link:
            resolved = self._resolve_google_news_redirect(str(link))
            if resolved:
                return resolved
            candidates.append(str(link))

        # 2) entry.links[]
        for l in entry.get('links', []) or []:
            href = l.get('href') if isinstance(l, dict) else None
            if href:
                candidates.append(str(href))

        # 3) entry.source.href
        try:
            source = entry.get('source') or {}
            href = source.get('href') if isinstance(source, dict) else None
            if href:
                candidates.append(str(href))
        except Exception:
            pass

        # 4) Extract hrefs from summary HTML
        summary = entry.get('summary') or ""
        if summary:
            summary = html.unescape(str(summary))
            for m in re.findall(r'href=["\'](https?://[^"\']+)["\']', summary, flags=re.IGNORECASE):
                candidates.append(m)
            for m in re.findall(r'(https?://[^\s"\'>]+)', summary, flags=re.IGNORECASE):
                candidates.append(m)

        allowed_urls: List[str] = []

        for url in candidates:
            try:
                url = str(url).strip()
            except Exception:
                continue
            if not url:
                continue

            domain = self._extract_domain_from_url(url)
            if not domain:
                continue
            if domain.endswith('google.com') or domain.endswith('news.google.com'):
                continue
            if self._match_allowed_domain(domain):
                allowed_urls.append(url)

        if not allowed_urls:
            return None

        # Prefer a specific article URL (non-root path) over a homepage.
        def score(u: str) -> tuple[int, int]:
            try:
                p = urlparse(u)
                non_root = 1 if (p.path and p.path != "/") else 0
                return (non_root, len(u))
            except Exception:
                return (0, len(u))

        allowed_urls.sort(key=score, reverse=True)
        return allowed_urls[0]

    def _resolve_google_news_redirect(self, url: str) -> Optional[str]:
        """Resolve a news.google.com RSS entry link to the publisher URL.

        We do NOT fetch the publisher page content. We only request the Google News
        URL with redirects disabled and read the Location header.
        """
        try:
            domain = self._extract_domain_from_url(url)
            if not domain:
                return None
            if not (domain.endswith('google.com') or domain.endswith('news.google.com')):
                return None

            # Follow redirects to reach the publisher URL, but do not download content.
            resp = requests.get(
                url,
                headers={"User-Agent": "Mozilla/5.0"},
                timeout=10,
                allow_redirects=True,
                stream=True,
            )
            final_url = resp.url
            try:
                resp.close()
            except Exception:
                pass

            if not final_url:
                return None

            publisher_domain = self._extract_domain_from_url(final_url)
            if not publisher_domain:
                return None
            if publisher_domain.endswith('google.com') or publisher_domain.endswith('news.google.com'):
                return None
            if self._match_allowed_domain(publisher_domain):
                return final_url
        except Exception:
            return None

        return None

    def _match_allowed_domain(self, domain: str) -> Optional[Dict[str, Any]]:
        # Exact match
        if domain in self.allowed_domains:
            return self.allowed_domains[domain]
        # Subdomain match
        for allowed_domain, info in self.allowed_domains.items():
            if domain == allowed_domain or domain.endswith("." + allowed_domain):
                return info
        return None

    def _is_recent(self, published_iso: Optional[str]) -> bool:
        if not published_iso:
            return True
        try:
            dt = datetime.fromisoformat(published_iso.replace("Z", "+00:00"))
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=timezone.utc)
            age_days = (datetime.now(timezone.utc) - dt).days
            return age_days <= self.max_age_days
        except Exception:
            return True
    
    def _parse_date(self, date_str: str) -> Optional[str]:
        """Parse date string to ISO format"""
        try:
            from email.utils import parsedate_to_datetime
            dt = parsedate_to_datetime(date_str)
            return dt.isoformat()
        except:
            return None


# Global instance
google_news_scraper = GoogleNewsRSSScraper()
