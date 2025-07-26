from celery import shared_task
from bs4 import BeautifulSoup
import requests
import feedparser
from datetime import datetime
from django.utils.text import slugify
from django.utils import timezone
from django.utils.html import strip_tags
from news.models import Article, Source, Category
import logging
import re

logger = logging.getLogger(__name__)


@shared_task
def scrape_coindesk():
    """Scrape CoinDesk RSS feed"""
    try:
        source, _ = Source.objects.get_or_create(
            name='CoinDesk',
            defaults={'url': 'https://www.coindesk.com'}
        )

        feed = feedparser.parse(
            'https://www.coindesk.com/arc/outboundfeeds/rss/')
        category, _ = Category.objects.get_or_create(
            name='Bitcoin News',
            defaults={'slug': 'bitcoin-news'}
        )

        articles_created = 0
        for entry in feed.entries[:20]:  # Get last 20 articles
            if not Article.objects.filter(source_url=entry.link).exists():
                # Clean up the content
                content = entry.get('summary', entry.get('description', ''))
                content = strip_tags(content)  # Remove HTML tags

                # Create a better excerpt
                excerpt = content[:300] + \
                    '...' if len(content) > 300 else content

                article = Article.objects.create(
                    title=entry.title,
                    slug=slugify(entry.title)[:290],
                    content=content,
                    excerpt=excerpt,
                    source=source,
                    source_url=entry.link,
                    article_type='aggregated',
                    category=category,
                    published_date=timezone.now(),
                    is_published=True
                )
                articles_created += 1
                logger.info(f"Created article: {article.title}")

        logger.info(f"CoinDesk: Created {articles_created} new articles")

    except Exception as e:
        logger.error(f"Error scraping CoinDesk: {str(e)}")


@shared_task
def scrape_cointelegraph():
    """Scrape CoinTelegraph RSS feed"""
    try:
        source, _ = Source.objects.get_or_create(
            name='CoinTelegraph',
            defaults={'url': 'https://cointelegraph.com'}
        )

        feed = feedparser.parse('https://cointelegraph.com/rss')
        category, _ = Category.objects.get_or_create(
            name='Cryptocurrency News',
            defaults={'slug': 'cryptocurrency-news'}
        )

        articles_created = 0
        for entry in feed.entries[:20]:
            if not Article.objects.filter(source_url=entry.link).exists():
                content = entry.get('description', entry.get('summary', ''))
                content = strip_tags(content)

                excerpt = content[:300] + \
                    '...' if len(content) > 300 else content

                article = Article.objects.create(
                    title=entry.title,
                    slug=slugify(entry.title)[:290],
                    content=content,
                    excerpt=excerpt,
                    source=source,
                    source_url=entry.link,
                    article_type='aggregated',
                    category=category,
                    published_date=timezone.now(),
                    is_published=True
                )
                articles_created += 1
                logger.info(f"Created article: {article.title}")

        logger.info(f"CoinTelegraph: Created {articles_created} new articles")

    except Exception as e:
        logger.error(f"Error scraping CoinTelegraph: {str(e)}")


@shared_task
def scrape_bitcoin_magazine():
    """Scrape Bitcoin Magazine RSS feed"""
    try:
        source, _ = Source.objects.get_or_create(
            name='Bitcoin Magazine',
            defaults={'url': 'https://bitcoinmagazine.com'}
        )

        feed = feedparser.parse('https://bitcoinmagazine.com/feed')
        category, _ = Category.objects.get_or_create(
            name='Bitcoin News',
            defaults={'slug': 'bitcoin-news'}
        )

        articles_created = 0
        for entry in feed.entries[:15]:
            if not Article.objects.filter(source_url=entry.link).exists():
                content = entry.get('summary', entry.get('description', ''))
                content = strip_tags(content)

                excerpt = content[:300] + \
                    '...' if len(content) > 300 else content

                article = Article.objects.create(
                    title=entry.title,
                    slug=slugify(entry.title)[:290],
                    content=content,
                    excerpt=excerpt,
                    source=source,
                    source_url=entry.link,
                    article_type='aggregated',
                    category=category,
                    published_date=timezone.now(),
                    is_published=True
                )
                articles_created += 1

        logger.info(
            f"Bitcoin Magazine: Created {articles_created} new articles")

    except Exception as e:
        logger.error(f"Error scraping Bitcoin Magazine: {str(e)}")


@shared_task
def scrape_decrypt():
    """Scrape Decrypt RSS feed"""
    try:
        source, _ = Source.objects.get_or_create(
            name='Decrypt',
            defaults={'url': 'https://decrypt.co'}
        )

        feed = feedparser.parse('https://decrypt.co/feed')
        category, _ = Category.objects.get_or_create(
            name='Crypto Analysis',
            defaults={'slug': 'crypto-analysis'}
        )

        articles_created = 0
        for entry in feed.entries[:15]:
            if not Article.objects.filter(source_url=entry.link).exists():
                content = entry.get('summary', entry.get('description', ''))
                content = strip_tags(content)

                excerpt = content[:300] + \
                    '...' if len(content) > 300 else content

                article = Article.objects.create(
                    title=entry.title,
                    slug=slugify(entry.title)[:290],
                    content=content,
                    excerpt=excerpt,
                    source=source,
                    source_url=entry.link,
                    article_type='aggregated',
                    category=category,
                    published_date=timezone.now(),
                    is_published=True
                )
                articles_created += 1

        logger.info(f"Decrypt: Created {articles_created} new articles")

    except Exception as e:
        logger.error(f"Error scraping Decrypt: {str(e)}")


@shared_task
def update_crypto_prices():
    """Update cryptocurrency prices from CoinGecko API"""
    from ticker.models import Cryptocurrency, PriceHistory

    try:
        # Extended list of cryptocurrencies
        coins = [
            'bitcoin', 'ethereum', 'binancecoin', 'ripple', 'cardano',
            'solana', 'polkadot', 'dogecoin', 'avalanche-2', 'chainlink',
            'polygon', 'uniswap', 'litecoin', 'cosmos', 'stellar'
        ]

        for coin_id in coins:
            response = requests.get(
                f'https://api.coingecko.com/api/v3/simple/price',
                params={
                    'ids': coin_id,
                    'vs_currencies': 'usd',
                    'include_market_cap': 'true',
                    'include_24hr_vol': 'true',
                    'include_24hr_change': 'true'
                }
            )

            if response.status_code == 200:
                data = response.json().get(coin_id, {})
                if data:
                    crypto, created = Cryptocurrency.objects.update_or_create(
                        symbol=coin_id.upper()[:10],
                        defaults={
                            'name': coin_id.replace('-', ' ').title(),
                            'current_price': data.get('usd', 0),
                            'market_cap': data.get('usd_market_cap', 0),
                            'volume_24h': data.get('usd_24h_vol', 0),
                            'percent_change_24h': data.get('usd_24h_change', 0)
                        }
                    )

                    # Store price history
                    PriceHistory.objects.create(
                        cryptocurrency=crypto,
                        price=data.get('usd', 0)
                    )

                    logger.info(
                        f"Updated price for {coin_id}: ${data.get('usd', 0)}")

    except Exception as e:
        logger.error(f"Error updating crypto prices: {str(e)}")


@shared_task
def scrape_the_block():
    """Scrape The Block RSS feed"""
    try:
        source, _ = Source.objects.get_or_create(
            name='The Block',
            defaults={'url': 'https://www.theblock.co'}
        )

        feed = feedparser.parse('https://www.theblock.co/rss.xml')
        category, _ = Category.objects.get_or_create(
            name='Blockchain News',
            defaults={'slug': 'blockchain-news'}
        )

        articles_created = 0
        for entry in feed.entries[:15]:
            if not Article.objects.filter(source_url=entry.link).exists():
                content = strip_tags(
                    entry.get('summary', entry.get('description', '')))
                excerpt = content[:300] + \
                    '...' if len(content) > 300 else content

                article = Article.objects.create(
                    title=entry.title,
                    slug=slugify(entry.title)[:290],
                    content=content,
                    excerpt=excerpt,
                    source=source,
                    source_url=entry.link,
                    article_type='aggregated',
                    category=category,
                    published_date=timezone.now(),
                    is_published=True
                )
                articles_created += 1

        logger.info(f"The Block: Created {articles_created} new articles")

    except Exception as e:
        logger.error(f"Error scraping The Block: {str(e)}")


@shared_task
def scrape_cryptoslate():
    """Scrape CryptoSlate RSS feed"""
    try:
        source, _ = Source.objects.get_or_create(
            name='CryptoSlate',
            defaults={'url': 'https://cryptoslate.com'}
        )

        feed = feedparser.parse('https://cryptoslate.com/feed/')
        category, _ = Category.objects.get_or_create(
            name='Crypto Analysis',
            defaults={'slug': 'crypto-analysis'}
        )

        articles_created = 0
        for entry in feed.entries[:15]:
            if not Article.objects.filter(source_url=entry.link).exists():
                content = strip_tags(entry.get('content', [{}])[
                                     0].get('value', entry.get('summary', '')))
                excerpt = content[:300] + \
                    '...' if len(content) > 300 else content

                article = Article.objects.create(
                    title=entry.title,
                    slug=slugify(entry.title)[:290],
                    content=content,
                    excerpt=excerpt,
                    source=source,
                    source_url=entry.link,
                    article_type='aggregated',
                    category=category,
                    published_date=timezone.now(),
                    is_published=True
                )
                articles_created += 1

        logger.info(f"CryptoSlate: Created {articles_created} new articles")

    except Exception as e:
        logger.error(f"Error scraping CryptoSlate: {str(e)}")


@shared_task
def scrape_bitcoinist():
    """Scrape Bitcoinist RSS feed"""
    try:
        source, _ = Source.objects.get_or_create(
            name='Bitcoinist',
            defaults={'url': 'https://bitcoinist.com'}
        )

        feed = feedparser.parse('https://bitcoinist.com/feed/')
        category, _ = Category.objects.get_or_create(
            name='Bitcoin News',
            defaults={'slug': 'bitcoin-news'}
        )

        articles_created = 0
        for entry in feed.entries[:15]:
            if not Article.objects.filter(source_url=entry.link).exists():
                content = strip_tags(
                    entry.get('summary', entry.get('description', '')))
                excerpt = content[:300] + \
                    '...' if len(content) > 300 else content

                article = Article.objects.create(
                    title=entry.title,
                    slug=slugify(entry.title)[:290],
                    content=content,
                    excerpt=excerpt,
                    source=source,
                    source_url=entry.link,
                    article_type='aggregated',
                    category=category,
                    published_date=timezone.now(),
                    is_published=True
                )
                articles_created += 1

        logger.info(f"Bitcoinist: Created {articles_created} new articles")

    except Exception as e:
        logger.error(f"Error scraping Bitcoinist: {str(e)}")


@shared_task
def scrape_crypto_news():
    """Scrape Crypto.News RSS feed"""
    try:
        source, _ = Source.objects.get_or_create(
            name='Crypto.News',
            defaults={'url': 'https://crypto.news'}
        )

        feed = feedparser.parse('https://crypto.news/feed/')
        category, _ = Category.objects.get_or_create(
            name='Cryptocurrency News',
            defaults={'slug': 'cryptocurrency-news'}
        )

        articles_created = 0
        for entry in feed.entries[:15]:
            if not Article.objects.filter(source_url=entry.link).exists():
                content = strip_tags(
                    entry.get('summary', entry.get('description', '')))
                excerpt = content[:300] + \
                    '...' if len(content) > 300 else content

                article = Article.objects.create(
                    title=entry.title,
                    slug=slugify(entry.title)[:290],
                    content=content,
                    excerpt=excerpt,
                    source=source,
                    source_url=entry.link,
                    article_type='aggregated',
                    category=category,
                    published_date=timezone.now(),
                    is_published=True
                )
                articles_created += 1

        logger.info(f"Crypto.News: Created {articles_created} new articles")

    except Exception as e:
        logger.error(f"Error scraping Crypto.News: {str(e)}")


@shared_task
def scrape_crypto_briefing():
    """Scrape Crypto Briefing RSS feed"""
    try:
        source, _ = Source.objects.get_or_create(
            name='Crypto Briefing',
            defaults={'url': 'https://cryptobriefing.com'}
        )

        feed = feedparser.parse('https://cryptobriefing.com/feed/')
        category, _ = Category.objects.get_or_create(
            name='DeFi News',
            defaults={'slug': 'defi-news'}
        )

        articles_created = 0
        for entry in feed.entries[:15]:
            if not Article.objects.filter(source_url=entry.link).exists():
                content = strip_tags(
                    entry.get('summary', entry.get('description', '')))
                excerpt = content[:300] + \
                    '...' if len(content) > 300 else content

                article = Article.objects.create(
                    title=entry.title,
                    slug=slugify(entry.title)[:290],
                    content=content,
                    excerpt=excerpt,
                    source=source,
                    source_url=entry.link,
                    article_type='aggregated',
                    category=category,
                    published_date=timezone.now(),
                    is_published=True
                )
                articles_created += 1

        logger.info(
            f"Crypto Briefing: Created {articles_created} new articles")

    except Exception as e:
        logger.error(f"Error scraping Crypto Briefing: {str(e)}")


@shared_task
def scrape_newsbtc():
    """Scrape NewsBTC RSS feed"""
    try:
        source, _ = Source.objects.get_or_create(
            name='NewsBTC',
            defaults={'url': 'https://www.newsbtc.com'}
        )

        feed = feedparser.parse('https://www.newsbtc.com/feed/')
        category, _ = Category.objects.get_or_create(
            name='Trading Analysis',
            defaults={'slug': 'trading-analysis'}
        )

        articles_created = 0
        for entry in feed.entries[:15]:
            if not Article.objects.filter(source_url=entry.link).exists():
                content = strip_tags(
                    entry.get('summary', entry.get('description', '')))
                excerpt = content[:300] + \
                    '...' if len(content) > 300 else content

                article = Article.objects.create(
                    title=entry.title,
                    slug=slugify(entry.title)[:290],
                    content=content,
                    excerpt=excerpt,
                    source=source,
                    source_url=entry.link,
                    article_type='aggregated',
                    category=category,
                    published_date=timezone.now(),
                    is_published=True
                )
                articles_created += 1

        logger.info(f"NewsBTC: Created {articles_created} new articles")

    except Exception as e:
        logger.error(f"Error scraping NewsBTC: {str(e)}")

@shared_task
def scrape_all_sources():
    """Run all scrapers"""
    logger.info("Starting comprehensive news scraping...")

    # Original sources
    scrape_coindesk.delay()
    scrape_cointelegraph.delay()
    scrape_bitcoin_magazine.delay()
    scrape_decrypt.delay()

    # New sources
    scrape_the_block.delay()
    scrape_cryptoslate.delay()
    scrape_bitcoinist.delay()
    scrape_crypto_news.delay()
    scrape_crypto_briefing.delay()
    scrape_newsbtc.delay()

    # Update crypto prices
    update_crypto_prices.delay()

    logger.info("All scraping tasks dispatched")

@shared_task
def cleanup_old_price_history():
    """Clean up old price history entries (keep last 7 days)"""
    from ticker.models import PriceHistory
    from datetime import timedelta

    cutoff_date = timezone.now() - timedelta(days=7)
    deleted_count = PriceHistory.objects.filter(
        timestamp__lt=cutoff_date).delete()[0]
    logger.info(f"Cleaned up {deleted_count} old price history entries")
