import requests
import json
import os
from datetime import datetime
import logging

# Set up logging
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')

class CryptoMarketData:
    def __init__(self):
        # Free API endpoints that don't require authentication
        self.apis = {
            'coingecko': {
                'global': 'https://api.coingecko.com/api/v3/global',
                'prices': 'https://api.coingecko.com/api/v3/simple/price',
                'trending': 'https://api.coingecko.com/api/v3/search/trending'
            },
            'coinpaprika': {
                'global': 'https://api.coinpaprika.com/v1/global',
                'tickers': 'https://api.coinpaprika.com/v1/tickers'
            }
        }
        
    def fetch_global_market_data(self):
        """Fetch global market data from CoinGecko"""
        try:
            response = requests.get(self.apis['coingecko']['global'], timeout=10)
            response.raise_for_status()
            data = response.json()['data']
            
            return {
                'market_cap': {
                    'value': self.format_large_number(data['total_market_cap']['usd']),
                    'change': round(data['market_cap_change_percentage_24h_usd'], 2),
                    'positive': data['market_cap_change_percentage_24h_usd'] > 0
                },
                'volume_24h': {
                    'value': self.format_large_number(data['total_volume']['usd']),
                    'change': 0,  # Volume change not provided by this endpoint
                    'positive': True
                },
                'btc_dominance': {
                    'value': f"{round(data['market_cap_percentage']['btc'], 1)}%",
                    'change': 0,  # Change not provided
                    'positive': True
                },
                'active_cryptos': {
                    'value': f"{data['active_cryptocurrencies']:,}",
                    'change': 0,
                    'positive': True
                }
            }
        except Exception as e:
            logging.error(f"Error fetching global market data: {e}")
            return None
    
    def fetch_top_cryptos(self):
        """Fetch top cryptocurrency prices"""
        try:
            # Get top 20 cryptos
            crypto_ids = 'bitcoin,ethereum,binancecoin,solana,ripple,cardano,avalanche-2,dogecoin,polkadot,polygon,chainlink,near,cosmos,arbitrum,optimism'
            params = {
                'ids': crypto_ids,
                'vs_currencies': 'usd',
                'include_24hr_change': 'true',
                'include_market_cap': 'true'
            }
            
            response = requests.get(self.apis['coingecko']['prices'], params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            # Format ticker data
            tickers = []
            symbol_map = {
                'bitcoin': 'BTC',
                'ethereum': 'ETH',
                'binancecoin': 'BNB',
                'solana': 'SOL',
                'ripple': 'XRP',
                'cardano': 'ADA',
                'avalanche-2': 'AVAX',
                'dogecoin': 'DOGE',
                'polkadot': 'DOT',
                'polygon': 'MATIC',
                'chainlink': 'LINK',
                'near': 'NEAR',
                'cosmos': 'ATOM',
                'arbitrum': 'ARB',
                'optimism': 'OP'
            }
            
            for coin_id, coin_data in data.items():
                symbol = symbol_map.get(coin_id, coin_id.upper()[:4])
                price = coin_data['usd']
                change = coin_data.get('usd_24h_change', 0)
                
                # Format price based on value
                if price >= 1000:
                    price_str = f"${int(price):,}"
                elif price >= 1:
                    price_str = f"${price:,.2f}"
                else:
                    price_str = f"${price:.4f}"
                
                ticker = {
                    'symbol': symbol,
                    'price': price_str,
                    'change': round(change, 2),
                    'positive': change > 0
                }
                tickers.append(ticker)
            
            return tickers
            
        except Exception as e:
            logging.error(f"Error fetching crypto prices: {e}")
            return None
    
    def fetch_trending_coins(self):
        """Fetch trending cryptocurrencies"""
        try:
            response = requests.get(self.apis['coingecko']['trending'], timeout=10)
            response.raise_for_status()
            data = response.json()
            
            trending = []
            for coin in data.get('coins', [])[:5]:
                item = coin['item']
                trending.append({
                    'name': item['name'],
                    'symbol': item['symbol'],
                    'rank': item['market_cap_rank']
                })
            
            return trending
            
        except Exception as e:
            logging.error(f"Error fetching trending coins: {e}")
            return None
    
    def format_large_number(self, num):
        """Format large numbers into readable format"""
        if num >= 1e12:
            return f"${num/1e12:.1f}T"
        elif num >= 1e9:
            return f"${num/1e9:.1f}B"
        elif num >= 1e6:
            return f"${num/1e6:.1f}M"
        else:
            return f"${num:,.0f}"
    
    def save_market_data(self, output_dir='../data'):
        """Fetch all market data and save to JSON"""
        logging.info("Fetching cryptocurrency market data...")
        
        # Ensure output directory exists
        os.makedirs(output_dir, exist_ok=True)
        
        market_data = {
            'global': self.fetch_global_market_data(),
            'tickers': self.fetch_top_cryptos(),
            'trending': self.fetch_trending_coins(),
            'last_updated': datetime.now().isoformat()
        }
        
        # Save to JSON file
        output_path = os.path.join(output_dir, 'market_data.json')
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(market_data, f, ensure_ascii=False, indent=2)
        
        logging.info(f"✓ Market data saved to {output_path}")
        
        # Print summary
        if market_data['global']:
            print("\n--- Market Overview ---")
            print(f"Market Cap: {market_data['global']['market_cap']['value']} ({market_data['global']['market_cap']['change']:+.2f}%)")
            print(f"24h Volume: {market_data['global']['volume_24h']['value']}")
            print(f"BTC Dominance: {market_data['global']['btc_dominance']['value']}")
            print(f"Active Cryptos: {market_data['global']['active_cryptos']['value']}")
        
        if market_data['tickers']:
            print("\n--- Top Movers ---")
            sorted_tickers = sorted(market_data['tickers'], key=lambda x: abs(x['change']), reverse=True)
            for ticker in sorted_tickers[:5]:
                arrow = '↑' if ticker['positive'] else '↓'
                print(f"{ticker['symbol']}: {ticker['price']} {arrow} {abs(ticker['change'])}%")


def main():
    """Main function to fetch and save market data"""
    fetcher = CryptoMarketData()
    fetcher.save_market_data()


if __name__ == '__main__':
    main()