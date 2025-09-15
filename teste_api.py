import requests

def testar_api_cotacoes():
    try:
        response = requests.get('https://economia.awesomeapi.com.br/last/USD-BRL,EUR-BRL,BTC-BRL')
        data = response.json()

        print("=== TESTE DA API DE COTAÇÕES ===")
        print(f"Status da resposta: {response.status_code}")

        if 'USDBRL' in data:
            usd = data['USDBRL']
            print(f"\nUSD/BRL:")
            print(f"  Valor: R$ {usd['bid']}")
            print(f"  Variação: {usd['pctChange']}%")
            print(f"  Última atualização: {usd['create_date']}")

        if 'EURBRL' in data:
            eur = data['EURBRL']
            print(f"\nEUR/BRL:")
            print(f"  Valor: R$ {eur['bid']}")
            print(f"  Variação: {eur['pctChange']}%")
            print(f"  Última atualização: {eur['create_date']}")

        if 'BTCBRL' in data:
            btc = data['BTCBRL']
            print(f"\nBTC/BRL:")
            print(f"  Valor: R$ {btc['bid']}")
            print(f"  Variação: {btc['pctChange']}%")
            print(f"  Última atualização: {btc['create_date']}")

        print("\n✅ API funcionando corretamente!")

    except Exception as e:
        print(f"❌ Erro ao testar API: {e}")

if __name__ == '__main__':
    testar_api_cotacoes()
