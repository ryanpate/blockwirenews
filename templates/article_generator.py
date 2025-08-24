#!/usr/bin/env python3
"""
Automated Article Generator for BlockWire News
Generates and publishes cryptocurrency articles using OpenAI API
"""

import os
import sys
import json
import random
import time
from datetime import datetime, timedelta
import openai
import requests
import re
from typing import List, Dict, Optional
import psycopg2
from psycopg2.extras import RealDictCursor
import hashlib
from urllib.parse import quote

# Add project directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Configuration
OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')

# OpenAI Configuration - Using GPT-4o-mini for cost efficiency
MODEL = "gpt-4o-mini"  # Most cost-effective: $0.150/1M input, $0.600/1M output tokens
MAX_TOKENS = 2000
TEMPERATURE = 0.7

class ArticleGenerator:
    """Handles article generation using OpenAI API"""
    
    def __init__(self):
        """Initialize the generator with OpenAI client"""
        if not OPENAI_API_KEY:
            raise ValueError("OPENAI_API_KEY environment variable not set")
        
        openai.api_key = OPENAI_API_KEY
        self.client = openai.OpenAI(api_key=OPENAI_API_KEY)
        self.db_conn = None
        self.connect_db()
    
    def connect_db(self):
        """Connect to PostgreSQL database"""
        try:
            self.db_conn = psycopg2.connect(DATABASE_URL)
            print("✓ Connected to database")
        except Exception as e:
            print(f"✗ Database connection failed: {e}")
            raise
    
    def load_topics(self) -> List[Dict]:
        """Load topics from JSON file"""
        try:
            with open('article_topics.json', 'r') as f:
                data = json.load(f)
                return data['topics']
        except FileNotFoundError:
            print("✗ article_topics.json not found")
            return []
    
    def fetch_trending_news(self) -> List[Dict]:
        """Fetch recent news from database to identify trends"""
        query = """
        SELECT title, summary, source 
        FROM news_items 
        WHERE scraped_at >= NOW() - INTERVAL '24 hours'
        ORDER BY scraped_at DESC 
        LIMIT 20
        """
        
        try:
            with self.db_conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(query)
                return cur.fetchall()
        except Exception as e:
            print(f"Error fetching news: {e}")
            return []
    
    def extract_trending_topics(self, news_items: List[Dict]) -> List[str]:
        """Extract trending topics from recent news"""
        topics = []
        
        # Common crypto terms to look for
        crypto_terms = [
            'Bitcoin', 'Ethereum', 'DeFi', 'NFT', 'Web3', 'blockchain',
            'regulation', 'institutional', 'adoption', 'mining', 'staking',
            'Layer 2', 'altcoin', 'market analysis', 'price prediction',
            'crypto exchange', 'wallet', 'security', 'hack', 'ETF', 'SEC'
        ]
        
        # Count occurrences
        term_counts = {}
        for item in news_items:
            text = f"{item['title']} {item['summary']}".lower()
            for term in crypto_terms:
                if term.lower() in text:
                    term_counts[term] = term_counts.get(term, 0) + 1
        
        # Get top trending terms
        sorted_terms = sorted(term_counts.items(), key=lambda x: x[1], reverse=True)
        return [term for term, count in sorted_terms[:5]]
    
    def generate_seo_metadata(self, title: str, content: str) -> Dict:
        """Generate SEO metadata for article"""
        # Extract keywords from title and content
        words = re.findall(r'\b\w+\b', f"{title} {content[:500]}".lower())
        word_freq = {}
        for word in words:
            if len(word) > 3:  # Skip short words
                word_freq[word] = word_freq.get(word, 0) + 1
        
        # Get top keywords
        keywords = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)[:10]
        keyword_list = [word for word, freq in keywords]
        
        # Add crypto-specific keywords
        crypto_keywords = ['cryptocurrency', 'blockchain', 'crypto news', 'digital assets']
        keyword_list.extend([k for k in crypto_keywords if k not in keyword_list])
        
        # Generate meta description (155 chars max)
        meta_description = content.split('.')[0][:152] + '...'
        
        return {
            'keywords': ', '.join(keyword_list[:15]),
            'description': meta_description,
            'og_title': title,
            'og_description': meta_description,
            'twitter_card': 'summary_large_image',
            'canonical_url': f"/article/{self.create_slug(title)}"
        }
    
    def create_slug(self, title: str) -> str:
        """Create URL-friendly slug from title"""
        slug = re.sub(r'[^\w\s-]', '', title.lower())
        slug = re.sub(r'[-\s]+', '-', slug)
        slug = slug.strip('-')[:50]
        
        # Add timestamp hash to ensure uniqueness
        timestamp_hash = hashlib.md5(str(time.time()).encode()).hexdigest()[:6]
        return f"{slug}-{timestamp_hash}"
    
    def generate_article(self, topic: str, context: str = "") -> Optional[Dict]:
        """Generate article using OpenAI API"""
        
        # Construct the prompt
        system_prompt = """You are an expert cryptocurrency journalist writing for BlockWire News, 
        a professional crypto news platform. Write engaging, informative, and SEO-optimized articles 
        that provide value to both beginners and experienced crypto enthusiasts. 
        
        Your articles should:
        1. Be factual and well-researched
        2. Include current market context when relevant
        3. Be between 600-800 words
        4. Have clear sections with subheadings
        5. Include actionable insights or takeaways
        6. Be optimized for SEO with natural keyword usage
        7. Maintain a professional but accessible tone
        8. Include a compelling introduction and conclusion
        9. Reference recent developments when applicable
        10. Avoid speculation presented as fact"""
        
        user_prompt = f"""Write a comprehensive article about: {topic}

{f'Current market context: {context}' if context else ''}

Format the article with:
- An attention-grabbing title (max 60 characters)
- A brief summary (2-3 sentences, max 160 characters)
- The main content with 3-4 sections using markdown headers (##)
- Natural integration of relevant keywords
- A conclusion with key takeaways

Focus on providing educational value and actionable insights."""
        
        try:
            response = self.client.chat.completions.create(
                model=MODEL,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                max_tokens=MAX_TOKENS,
                temperature=TEMPERATURE
            )
            
            # Parse the response
            content = response.choices[0].message.content
            
            # Extract title (first line)
            lines = content.split('\n')
            title = lines[0].replace('#', '').strip()
            
            # Extract summary (look for summary section or use first paragraph)
            summary_match = re.search(r'Summary:(.+?)(?:\n|$)', content, re.IGNORECASE)
            if summary_match:
                summary = summary_match.group(1).strip()
            else:
                # Use first substantial paragraph
                paragraphs = [p.strip() for p in content.split('\n\n') if len(p.strip()) > 50]
                summary = paragraphs[0][:160] if paragraphs else ""
            
            # Clean up content (remove title from content)
            article_content = '\n'.join(lines[1:]).strip()
            
            # Generate SEO metadata
            seo_data = self.generate_seo_metadata(title, article_content)
            
            return {
                'title': title[:200],  # Max title length
                'slug': self.create_slug(title),
                'summary': summary[:500],  # Max summary length
                'content': article_content,
                'keywords': seo_data['keywords'],
                'meta_description': seo_data['description'],
                'generated_at': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            print(f"Error generating article: {e}")
            return None
    
    def save_article(self, article: Dict, author_id: int = 1) -> bool:
        """Save article to database"""
        query = """
        INSERT INTO articles (title, slug, content, summary, author_id, published, published_at, created_at, updated_at)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        ON CONFLICT (slug) DO NOTHING
        RETURNING id
        """
        
        try:
            with self.db_conn.cursor() as cur:
                cur.execute(query, (
                    article['title'],
                    article['slug'],
                    article['content'],
                    article['summary'],
                    author_id,
                    True,  # Published
                    datetime.utcnow(),  # Published at
                    datetime.utcnow(),  # Created at
                    datetime.utcnow()   # Updated at
                ))
                
                result = cur.fetchone()
                self.db_conn.commit()
                
                if result:
                    print(f"✓ Article saved: {article['title']}")
                    return True
                else:
                    print(f"✗ Article already exists: {article['title']}")
                    return False
                    
        except Exception as e:
            print(f"Error saving article: {e}")
            self.db_conn.rollback()
            return False
    
    def run(self, num_articles: int = 3):
        """Main execution function"""
        print(f"\n{'='*60}")
        print(f"BlockWire News - Article Generator")
        print(f"{'='*60}\n")
        
        # Load predefined topics
        topics = self.load_topics()
        
        # Fetch trending news for context
        trending_news = self.fetch_trending_news()
        trending_topics = self.extract_trending_topics(trending_news)
        
        print(f"📊 Found {len(topics)} predefined topics")
        print(f"📈 Identified {len(trending_topics)} trending topics\n")
        
        # Combine topics
        all_topics = []
        
        # Add trending topics
        for trend in trending_topics[:2]:  # Use top 2 trending topics
            all_topics.append({
                'topic': f"Latest developments in {trend}",
                'type': 'trending'
            })
        
        # Add random predefined topics
        if topics:
            random_topics = random.sample(topics, min(num_articles - len(all_topics), len(topics)))
            for topic_data in random_topics:
                all_topics.append({
                    'topic': topic_data['topic'],
                    'type': 'predefined',
                    'keywords': topic_data.get('keywords', [])
                })
        
        # Generate articles
        generated_count = 0
        for i, topic_data in enumerate(all_topics[:num_articles], 1):
            print(f"\n[{i}/{num_articles}] Generating article: {topic_data['topic']}")
            
            # Add context for trending topics
            context = ""
            if topic_data['type'] == 'trending' and trending_news:
                context = f"Recent news headlines: {', '.join([n['title'][:50] for n in trending_news[:3]])}"
            
            # Generate article
            article = self.generate_article(topic_data['topic'], context)
            
            if article:
                # Save to database
                if self.save_article(article):
                    generated_count += 1
                    print(f"   → Published: {article['slug']}")
                
                # Rate limiting (to avoid API rate limits)
                time.sleep(2)
            else:
                print(f"   ✗ Failed to generate article")
        
        print(f"\n{'='*60}")
        print(f"✅ Generated and published {generated_count} articles")
        print(f"{'='*60}\n")
        
        # Close database connection
        if self.db_conn:
            self.db_conn.close()

def main():
    """Main entry point"""
    try:
        # Check for API key
        if not os.environ.get('OPENAI_API_KEY'):
            print("Error: OPENAI_API_KEY environment variable not set")
            print("Please set it using: export OPENAI_API_KEY='your-key-here'")
            sys.exit(1)
        
        # Parse arguments
        num_articles = 3  # Default
        if len(sys.argv) > 1:
            try:
                num_articles = int(sys.argv[1])
                num_articles = max(1, min(10, num_articles))  # Limit between 1-10
            except ValueError:
                print("Invalid number of articles. Using default: 3")
        
        # Run generator
        generator = ArticleGenerator()
        generator.run(num_articles)
        
    except Exception as e:
        print(f"Fatal error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
