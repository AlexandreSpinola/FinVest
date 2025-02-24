import requests
import logging
from AppFinVest.models import PrecoAtivo, TabelaGlobal
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Constante para evitar duplicação de string
TIME_SERIES_DAILY = "Time Series (Daily)"

# 🔧 Atualização de Ações usando Alpha Vantage
def atualizar_precos_acoes():
    tabela_global = TabelaGlobal.get_instance()
    acoes = tabela_global.ativos.filter(tipo="Ação")

    for ativo in acoes:       
        try:
            api_url = f"https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol={ativo.nome_ativo}&apikey=D27EWPB0P5IPZXCJ"
            resposta = requests.get(api_url)
            resposta.raise_for_status()

            dados = resposta.json()
            if TIME_SERIES_DAILY in dados:
                latest_date = next(iter(dados[TIME_SERIES_DAILY]))
                time_series = dados[TIME_SERIES_DAILY][latest_date]

                ativo.atualizar_ativo_acao(
                    data=datetime.strptime(latest_date, "%Y-%m-%d"),
                    abertura=float(time_series["1. open"]),
                    maximo=float(time_series["2. high"]),
                    minimo=float(time_series["3. low"]),
                    fechamento=float(time_series["4. close"]),
                    volume=int(time_series["5. volume"])
                )

        except requests.exceptions.RequestException as e:
            logger.error(f"Erro ao acessar API Alpha Vantage para {ativo.nome_ativo}: {str(e)}")

    logger.info("Atualização de ações concluída.")


# 🔧 Atualização de Criptomoedas usando CoinGecko
def atualizar_precos_criptomoedas():
    tabela_global = TabelaGlobal.get_instance()
    criptomoedas = tabela_global.ativos.filter(tipo="Criptomoeda")

    url = "https://api.coingecko.com/api/v3/coins/markets"
    params = {
        'vs_currency': 'usd',
        'order': 'market_cap_desc',
        'per_page': len(criptomoedas)+10,
        'page': 1,
        'sparkline': False
    }

    try:
        resposta = requests.get(url, params=params)
        resposta.raise_for_status()
        dados_criptomoedas = resposta.json()

        for cripto in dados_criptomoedas:
            ativo = criptomoedas.filter(nome_ativo=cripto['id']).first()
            if ativo:
                ativo.atualizar_ativo_criptomoeda(
                    preco_atual=cripto['current_price'],
                    capitalizacao_mercado=cripto['market_cap'],
                    volume_24h=cripto['total_volume']
                )


    except requests.exceptions.RequestException as e:
        logger.error(f"Erro ao acessar API CoinGecko: {str(e)}")

    logger.info("Atualização de criptomoedas concluída.")


# 🔧 Função principal que chama ambas as atualizações
def atualizar_precos():
    logger.info("Iniciando o processo de atualização de preços...")
    atualizar_precos_acoes()
    atualizar_precos_criptomoedas()
    logger.info("Processo de atualização de preços finalizado.")
