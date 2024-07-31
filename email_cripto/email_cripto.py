import os
import requests
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from datetime import datetime, timezone, timedelta
import pytz

# Função para obter dados detalhados de criptomoedas da CoinMarketCap
def get_crypto_data(cryptos, api_key):
    url = 'https://pro-api.coinmarketcap.com/v1/cryptocurrency/quotes/latest'
    headers = {
        'X-CMC_PRO_API_KEY': api_key,
        'Accept': 'application/json'
    }
    params = {
        'symbol': ','.join(cryptos),
        'convert': 'USD'
    }
    response = requests.get(url, headers=headers, params=params)
    return response.json()

# Função para obter o índice de Medo e Ganância
def get_fear_greed_index():
    url = 'https://api.alternative.me/fng/'
    response = requests.get(url)
    data = response.json()
    return data['data'][0]

# Função para converter timestamp do Fear and Greed Index
def convert_fng_timestamp(timestamp):
    dt = datetime.fromtimestamp(int(timestamp), tz=timezone.utc)
    dt_brazil = dt.astimezone(pytz.timezone('America/Sao_Paulo'))
    return dt_brazil.strftime('%Y-%m-%d %H:%M:%S')

# Função para obter notícias de criptomoedas da NewsAPI
def get_crypto_news(api_key, queries, from_date, to_date):
    url = 'https://newsapi.org/v2/everything'
    headers = {
        'X-Api-Key': api_key,
        'Accept': 'application/json'
    }
    all_news = {}
    for query in queries:
        params = {
            'q': query,
            'from': from_date,
            'to': to_date,
            'sortBy': 'popularity',
            'language': 'en'
        }
        response = requests.get(url, headers=headers, params=params)
        news_data = response.json()
        if 'articles' in news_data:
            all_news[query] = news_data['articles'][:5]
        else:
            all_news[query] = []
    return all_news

# Função para obter notícias de curiosidades da NewsAPI
def get_top_headlines(api_key, country, category):
    url = 'https://newsapi.org/v2/top-headlines'
    headers = {
        'X-Api-Key': api_key,
        'Accept': 'application/json'
    }
    params = {
        'country': country,
        'category': category,
        'pageSize': 5
    }
    response = requests.get(url, headers=headers, params=params)
    return response.json()

# Função para formatar dados para o e-mail
def format_crypto_data(crypto, data):
    try:
        coin_data = data['data'][crypto]['quote']['USD']
        formatted_data = (
            f"<h2>{crypto.capitalize()}</h2>"
            f"<ul>"
            f"<li><strong>Preço:</strong> ${coin_data['price']:.8f}</li>"
            f"<li><strong>Volume (24h):</strong> {format_large_number(coin_data['volume_24h'])}</li>"
            f"<li><strong>Mudança (24h):</strong> {coin_data['percent_change_24h']:.2f}%</li>"
            f"<li><strong>Capitalização de Mercado:</strong> {format_large_number(coin_data['market_cap'])}</li>"
            f"<li><strong>Dominância de Mercado:</strong> {coin_data['market_cap_dominance']:.6f}%</li>"
            f"<li><strong>Última Atualização:</strong> {format_timestamp(coin_data['last_updated'])}</li>"
            f"</ul>"
        )
        return formatted_data
    except KeyError:
        return f"<h2>{crypto.capitalize()}</h2><p>Dados não disponíveis</p>"

# Função para formatar índice de Medo e Ganância
def format_fear_greed_index(fgi):
    formatted_fgi = (
        f"<h2>Índice de Medo e Ganância</h2>"
        f"<ul>"
        f"<li><strong>Índice Atual:</strong> {fgi['value']}</li>"
        f"<li><strong>Descrição:</strong> {fgi['value_classification']}</li>"
        f"<li><strong>Data:</strong> {convert_fng_timestamp(fgi['timestamp'])}</li>"
        f"</ul>"
    )
    return formatted_fgi

# Função para formatar notícias de criptomoedas
def format_crypto_news(news):
    formatted_news = "<h2>Últimas Notícias - Criptomoedas</h2>"
    for crypto, articles in news.items():
        formatted_news += f"<h3>{crypto.capitalize()}</h3><ul>"
        for article in articles:
            published_at_brazil = convert_to_brazil_time(article['publishedAt'])
            formatted_news += (
                f"<li><strong>Autor:</strong> {article.get('author', 'N/A')}<br>"
                f"<strong>Título:</strong> {article['title']}<br>"
                f"<strong>Data de Publicação:</strong> {published_at_brazil}<br>"
                f"<strong>URL:</strong> <a href='{article['url']}'>{article['url']}</a></li>"
            )
        formatted_news += "</ul>"
    return formatted_news

# Função para formatar notícias de curiosidades
def format_curiosity_news(news):
    formatted_news = "<h2>Últimas Notícias - Curiosidades</h2>"
    for category, articles in news.items():
        category_name = category.replace("-", " ").title()
        formatted_news += f"<h3>{category_name}</h3><ul>"
        for article in articles:
            published_at_brazil = convert_to_brazil_time(article['publishedAt'])
            formatted_news += (
                f"<li><strong>Autor:</strong> {article.get('author', 'N/A')}<br>"
                f"<strong>Título:</strong> {article['title']}<br>"
                f"<strong>Data de Publicação:</strong> {published_at_brazil}<br>"
                f"<strong>URL:</strong> <a href='{article['url']}'>{article['url']}</a></li>"
            )
        formatted_news += "</ul>"
    return formatted_news

# Função para formatar grandes números de forma legível
def format_large_number(num):
    if num >= 1_000_000_000_000:
        return f"{num / 1_000_000_000_000:.2f}T"
    elif num >= 1_000_000_000:
        return f"{num / 1_000_000_000:.2f}B"
    elif num >= 1_000_000:
        return f"{num / 1_000_000:.2f}M"
    elif num >= 1_000:
        return f"{num / 1_000:.2f}K"
    else:
        return f"{num:.2f}"

# Função para formatar Unix timestamp em data e hora legível com reconhecimento de fuso horário para o Brasil
def format_timestamp(timestamp):
    dt_utc = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
    dt_brazil = dt_utc.astimezone(pytz.timezone('America/Sao_Paulo'))
    return dt_brazil.strftime('%Y-%m-%d %H:%M:%S')

# Função para converter data e hora para o fuso horário do Brasil
def convert_to_brazil_time(timestamp):
    dt_utc = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
    dt_brazil = dt_utc.astimezone(pytz.timezone('America/Sao_Paulo'))
    return dt_brazil.strftime('%Y-%m-%d %H:%M:%S')

# Ler variáveis de ambiente
cryptos = ['BTC', 'SOL', 'ETH', 'DOG', 'MYRO', 'RENDER', 'NAKA', 'WOLF', 'BANANA', 'IO', 'LISTA', 'NOT']
crypto_queries = ['bitcoin', 'solana', 'ethereum', 'doggotothemoon', 'myro', 'render', 'landwolf']
coinmarketcap_api_key = os.getenv('COINMARKETCAP_API_KEY')
news_api_key = os.getenv('NEWS_API_KEY')
to_email = "pedro.hsilvapro@outlook.com"
from_email = "pedro.hsilvapro@outlook.com"
from_password = os.getenv('EMAIL_PASSWORD')

# Datas para busca de notícias
today = datetime.now().strftime('%Y-%m-%d')
yesterday = (datetime.now() - timedelta(1)).strftime('%Y-%m-%d')

# Obter dados e formatar e-mail
crypto_data = get_crypto_data(cryptos, coinmarketcap_api_key)
fgi_data = get_fear_greed_index()
crypto_news_data = get_crypto_news(news_api_key, crypto_queries, yesterday, today)
curiosity_news_data = {}
for country in ['br', 'us']:
    for category in ['technology', 'business']:
        curiosity_news_data[f"{country}-{category}"] = get_top_headlines(news_api_key, country, category)['articles']

crypto_info = "".join([format_crypto_data(crypto, crypto_data) for crypto in cryptos])
fgi_info = format_fear_greed_index(fgi_data)
crypto_news_info = format_crypto_news(crypto_news_data)
curiosity_news_info = format_curiosity_news(curiosity_news_data)

email_body = f"""
<html>
<head>
<style>
    body {{ font-family: Arial, sans-serif; }}
    h2 {{ color: #2e6c80; }}
    ul {{ list-style-type: none; padding: 0; }}
    li {{ margin: 5px 0; }}
    img {{ max-width: 100%; height: auto; }}
</style>
</head>
<body>
    <h1>Atualização Diária de Criptomoedas</h1>
    {crypto_info}
    {fgi_info}
    {crypto_news_info}
    {curiosity_news_info}
</body>
</html>
"""

# Função para enviar e-mail
def send_email(subject, body, to_email, from_email, from_password):
    msg = MIMEMultipart('alternative')
    msg['From'] = from_email
    msg['To'] = to_email
    msg['Subject'] = subject

    part = MIMEText(body, 'html')
    msg.attach(part)

    server = smtplib.SMTP('smtp.office365.com', 587)
    server.starttls()
    server.login(from_email, from_password)
    server.sendmail(from_email, to_email, msg.as_string())
    server.quit()

# Enviar e-mail
send_email("Atualização Diária de Criptomoedas", email_body, to_email, from_email, from_password)
