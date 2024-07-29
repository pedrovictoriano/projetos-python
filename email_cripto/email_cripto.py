import requests
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from datetime import datetime, timezone, timedelta
import pytz
import plotly.graph_objs as go
import plotly.io as pio
import base64
from io import BytesIO

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

# Função para obter eventos importantes da CoinMarketCal


def get_events(api_key):
    url = 'https://developers.coinmarketcal.com/v1/events?page=1'
    headers = {
        'x-api-key': api_key,
        'Accept-Encoding': 'deflate, gzip',
        'Accept': 'application/json'
    }
    response = requests.get(url, headers=headers)
    data = response.json()
    return data

# Função para formatar dados para o e-mail


def format_crypto_data(crypto, data):
    try:
        coin_data = data['data'][crypto]['quote']['USD']
        formatted_data = (
            f"<h2>{crypto}</h2>"
            f"<ul>"
            f"<li><strong>Preço:</strong> ${coin_data['price']:.8f}</li>"
            f"<li><strong>Volume (24h):</strong> ${
                format_large_number(coin_data['volume_24h'])}</li>"
            f"<li><strong>Mudança (24h):</strong> {
                coin_data['percent_change_24h']:.2f}%</li>"
            f"<li><strong>Capitalização de Mercado:</strong> ${
                format_large_number(coin_data['market_cap'])}</li>"
            f"<li><strong>Dominância de Mercado:</strong> {
                coin_data['market_cap_dominance']:.6f}%</li>"
            f"<li><strong>Última Atualização:</strong> {
                format_timestamp(coin_data['last_updated'])}</li>"
            f"</ul>"
        )
        return formatted_data
    except KeyError:
        return f"<h2>{crypto}</h2><p>Dados não disponíveis</p>"

# Função para formatar índice de Medo e Ganância


def format_fear_greed_index(fgi):
    formatted_fgi = (
        f"<h2>Índice de Medo e Ganância</h2>"
        f"<ul>"
        f"<li><strong>Índice Atual:</strong> {fgi['value']}</li>"
        f"<li><strong>Descrição:</strong> {fgi['value_classification']}</li>"
        f"<li><strong>Data:</strong> {
            convert_fng_timestamp(fgi['timestamp'])}</li>"
        f"</ul>"
    )
    return formatted_fgi

# Função para formatar eventos importantes


def format_events(events):
    formatted_events = "<h2>Eventos Importantes</h2><ul>"
    # Ajuste a chave para acessar os dados de eventos corretamente
    for event in events.get('body', []):
        description = event.get('description', 'Sem descrição')
        event_date = datetime.strptime(
            event['date_event'], "%Y-%m-%dT%H:%M:%SZ")
        event_date_brazil = event_date.astimezone(pytz.timezone(
            'America/Sao_Paulo')).strftime('%Y-%m-%d %H:%M:%S')
        formatted_events += f"<li><strong>{event['title']['en']
                                           }:</strong> {event_date_brazil} - {description}</li>"
    formatted_events += "</ul>"
    return formatted_events

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


# Configurações
# Certifique-se de que os símbolos das criptomoedas estão corretos
cryptos = ['BTC', 'SOL', 'ETH', 'DOG', 'MYRO', 'RENDER', 'NAKA', 'WOLF', 'BANANA', 'IO', 'LISTA', 'NOT']
coinmarketcap_api_key = '24be4c62-be1a-4dcb-96d5-6e88293e65c4'
coinmarketcal_api_key = 'behsx2Qt8t5bNPwQ4pCdV9dvhMNAFV267nSAGbIp'
to_email = "pedro.hsilvapro@outlook.com"
from_email = "pedro.hsilvapro@outlook.com"
from_password = "06090202p"

# Obter dados e formatar e-mail
crypto_data = get_crypto_data(cryptos, coinmarketcap_api_key)
fgi_data = get_fear_greed_index()
events_data = get_events(coinmarketcal_api_key)

crypto_info = "".join([format_crypto_data(crypto, crypto_data)
                      for crypto in cryptos])
fgi_info = format_fear_greed_index(fgi_data)
events_info = format_events(events_data)

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
    {events_info}
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
send_email("Atualização Diária de Criptomoedas",
           email_body, to_email, from_email, from_password)
