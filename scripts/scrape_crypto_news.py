import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import time

# List of websites and their AI-specific sections
sites = [
    ('TechCrunch', 'https://techcrunch.com/tag/ai-artificial-intelligence/'),
    ('MIT Tech Review', 'https://www.technologyreview.com/topic/artificial-intelligence/'),
    ('The Verge', 'https://www.theverge.com/ai-artificial-intelligence'),
    ('VentureBeat', 'https://venturebeat.com/category/ai/'),
    ('AI News', 'https://artificialintelligence-news.com/'),
    ('Towards Data Science', 'https://towardsdatascience.com/tagged/ai'),
    ('Wired', 'https://www.wired.com/tag/artificial-intelligence/'),
    ('ZDNet', 'https://www.zdnet.com/topic/artificial-intelligence/'),
    ('OpenAI Blog', 'https://openai.com/news/'),
    ('AI Trends', 'https://www.aitrends.com/')
]


def get_soup_selenium(url):
    options = Options()
    options.add_argument("--headless")
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    driver = webdriver.Chrome(options=options)

    driver.get(url)
    # wait for initial page load and scroll to load dynamic content
    time.sleep(3)
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(3)
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    driver.quit()
    return soup


def get_soup(url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                      'AppleWebKit/537.36 (KHTML, like Gecko) '
                      'Chrome/124.0.0.0 Safari/537.36',
        'Accept-Language': 'en-US,en;q=0.9',
    }
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    return BeautifulSoup(response.text, 'html.parser')


def scrape_techcrunch(url):
    soup = get_soup_selenium(url)
    articles = []
    for block in soup.select('div.post-block')[:5]:
        a = block.select_one('a.post-block__title__link')
        if a:
            title = a.get_text(strip=True)
            link = a['href']
            articles.append({'title': title, 'link': link})
    return articles


def scrape_venturebeat(url):
    soup = get_soup_selenium(url)
    articles = []
    for article in soup.select('div.article-item__title a')[:5]:
        title = article.get_text(strip=True)
        link = article['href']
        articles.append({'title': title, 'link': link})
    return articles


def scrape_mit_tech_review(url):
    soup = get_soup_selenium(url)
    articles = []
    for article in soup.select('a.card__link')[:5]:
        title = article.get_text(strip=True)
        link = article['href']
        if not link.startswith('http'):
            link = 'https://www.technologyreview.com' + link
        articles.append({'title': title, 'link': link})
    return articles


def scrape_the_verge(url):
    soup = get_soup_selenium(url)
    articles = []
    for article in soup.select('h2.c-entry-box--compact__title a')[:5]:
        title = article.get_text(strip=True)
        link = article['href']
        articles.append({'title': title, 'link': link})
    return articles


def scrape_ai_news(url):
    soup = get_soup_selenium(url)
    articles = []
    for article in soup.select('a.entry-title-link')[:5]:
        title = article.get_text(strip=True)
        link = article['href']
        articles.append({'title': title, 'link': link})
    return articles


def scrape_towards_data_science(url):
    soup = get_soup_selenium(url)
    articles = []
    for article in soup.select('h2.graf--title a')[:5]:
        title = article.get_text(strip=True)
        link = article['href']
        articles.append({'title': title, 'link': link})
    return articles


def scrape_wired(url):
    soup = get_soup_selenium(url)
    articles = []
    for article in soup.select('li.archive-item-component__info h3 a')[:5]:
        title = article.get_text(strip=True)
        link = article['href']
        if not link.startswith('http'):
            link = 'https://www.wired.com' + link
        articles.append({'title': title, 'link': link})
    return articles


def scrape_zdnet(url):
    soup = get_soup_selenium(url)
    articles = []
    for article in soup.select('div.listingItem__title a')[:5]:
        title = article.get_text(strip=True)
        link = article['href']
        if not link.startswith('http'):
            link = 'https://www.zdnet.com' + link
        articles.append({'title': title, 'link': link})
    return articles


def scrape_openai_blog(url):
    soup = get_soup_selenium(url)
    articles = []
    for article in soup.select('a.font-heading-xl')[:5]:
        title = article.get_text(strip=True)
        link = article['href']
        if not link.startswith('http'):
            link = 'https://openai.com' + link
        articles.append({'title': title, 'link': link})
    return articles


def scrape_ai_trends(url):
    soup = get_soup_selenium(url)
    articles = []
    for article in soup.select('h2.entry-title a')[:5]:
        title = article.get_text(strip=True)
        link = article['href']
        articles.append({'title': title, 'link': link})
    return articles


# Mapping site names to scraping functions
scrape_functions = {
    'TechCrunch': scrape_techcrunch,
    'VentureBeat': scrape_venturebeat,
    'MIT Tech Review': scrape_mit_tech_review,
    'The Verge': scrape_the_verge,
    'AI News': scrape_ai_news,
    'Towards Data Science': scrape_towards_data_science,
    'Wired': scrape_wired,
    'ZDNet': scrape_zdnet,
    'OpenAI Blog': scrape_openai_blog,
    'AI Trends': scrape_ai_trends,
}


def scrape_all_sites():
    all_articles = {}
    for name, url in sites:
        func = scrape_functions.get(name)
        if func:
            try:
                all_articles[name] = func(url)
            except Exception as e:
                print(f'Error scraping {name}: {e}')
        else:
            print(f'No scraping function defined for {name}')
    return all_articles


if __name__ == '__main__':
    articles = scrape_all_sites()
    for site, items in articles.items():
        print(f'\n--- Latest from {site} ---')
        for item in items:
            print(f"{item['title']} - {item['link']}")
