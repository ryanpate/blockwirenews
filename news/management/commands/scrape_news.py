from django.core.management.base import BaseCommand
from scraper.tasks import (
    scrape_coindesk, scrape_cointelegraph, scrape_bitcoin_magazine,
    scrape_decrypt, scrape_the_block, scrape_cryptoslate,
    scrape_bitcoinist, scrape_crypto_news, scrape_crypto_briefing,
    scrape_newsbtc
)

class Command(BaseCommand):
    help = 'Manually trigger news scraping from all sources'

    def add_arguments(self, parser):
        parser.add_argument(
            '--source',
            type=str,
            help='Scrape only from a specific source',
        )

    def handle(self, *args, **options):
        source = options.get('source')
        
        if source:
            source_map = {
                'coindesk': scrape_coindesk,
                'cointelegraph': scrape_cointelegraph,
                'bitcoin-magazine': scrape_bitcoin_magazine,
                'decrypt': scrape_decrypt,
                'the-block': scrape_the_block,
                'cryptoslate': scrape_cryptoslate,
                'bitcoinist': scrape_bitcoinist,
                'crypto-news': scrape_crypto_news,
                'crypto-briefing': scrape_crypto_briefing,
                'newsbtc': scrape_newsbtc,
            }
            
            if source in source_map:
                self.stdout.write(f'Scraping from {source}...')
                source_map[source]()
                self.stdout.write(self.style.SUCCESS(f'Successfully scraped {source}'))
            else:
                self.stdout.write(self.style.ERROR(f'Unknown source: {source}'))
                self.stdout.write('Available sources: ' + ', '.join(source_map.keys()))
        else:
            self.stdout.write('Scraping from all sources...')
            
            # Run all scrapers
            scrape_coindesk()
            scrape_cointelegraph()
            scrape_bitcoin_magazine()
            scrape_decrypt()
            scrape_the_block()
            scrape_cryptoslate()
            scrape_bitcoinist()
            scrape_crypto_news()
            scrape_crypto_briefing()
            scrape_newsbtc()
            
            self.stdout.write(self.style.SUCCESS('Successfully triggered scraping from all sources'))