
from flask import Flask, render_template, redirect, url_for, request, flash
from flask_pymongo import PyMongo
from flask_login import LoginManager, login_user, login_required, logout_user, UserMixin, current_user
from werkzeug.security import generate_password_hash, check_password_hash
import os
from dotenv import load_dotenv
from bson import ObjectId
from collections import defaultdict
from datetime import datetime
import requests
import yfinance as yf
import pandas as pd

load_dotenv()

app = Flask(__name__)
app.config['MONGO_URI'] = os.getenv('MONGO_URI', 'mongodb://localhost:27017/smartmoney')
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'changeme')
AWESOME_API_TOKEN = os.getenv('AWESOME_API_TOKEN', 'fa63ba9b800614afd38479ef0a06210a199d86bfea5fa979a407b725cf357ba3')
mongo = PyMongo(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

YF_SESSION = requests.Session()
YF_SESSION.headers.update({
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36',
    'Accept': 'application/json,text/plain,*/*',
    'Accept-Language': 'pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7',
})

class User(UserMixin):
    def __init__(self, user_doc):
        self.id = str(user_doc['_id'])
        self.username = user_doc['username']
        self.name = user_doc.get('name', user_doc['username'])

    @staticmethod
    def get(user_id):
        user_doc = mongo.db.users.find_one({'_id': ObjectId(user_id)})
        return User(user_doc) if user_doc else None

@login_manager.user_loader
def load_user(user_id):
    user_doc = mongo.db.users.find_one({'_id': ObjectId(user_id)})
    return User(user_doc) if user_doc else None


def montar_url_awesome_api():
    base_url = 'https://economia.awesomeapi.com.br/json/last/USD-BRL,EUR-BRL,BTC-BRL'
    return f"{base_url}?token={AWESOME_API_TOKEN}" if AWESOME_API_TOKEN else base_url


def obter_cotacoes_moedas():
    resposta = requests.get(montar_url_awesome_api(), timeout=10)
    resposta.raise_for_status()
    return resposta.json()


def ticker_para_yfinance(ticker: str) -> str:
    ticker = (ticker or '').upper().strip()
    if not ticker:
        return ''
    if ticker.endswith('.SA'):
        return ticker
    return f"{ticker}.SA"


def extrair_ultimo_fechamento(df: pd.DataFrame | None, simbolo: str | None = None) -> float | None:
    if df is None or df.empty:
        return None

    try:
        dados = df
        if isinstance(dados.columns, pd.MultiIndex):
            if 'Close' in dados.columns.get_level_values(0):
                dados = dados.xs('Close', axis=1)
            elif 'close' in dados.columns.get_level_values(0):
                dados = dados.xs('close', axis=1)

        if isinstance(dados, pd.DataFrame):
            if simbolo and simbolo in dados.columns:
                serie = dados[simbolo]
            elif len(dados.columns) > 0:
                serie = dados.iloc[:, 0]
            else:
                return None
        else:
            serie = dados

        serie = serie.dropna()
        if serie.empty:
            return None
        return float(serie.iloc[-1])
    except Exception as exc:
        app.logger.debug('Erro ao extrair fechamento de %s: %s', simbolo or 'ticker', exc)
        return None


def consultar_preco_via_chart(simbolo: str, intervalo: str = '1d', periodo: str = '1mo') -> float | None:
    try:
        resposta = YF_SESSION.get(
            f'https://query1.finance.yahoo.com/v8/finance/chart/{simbolo}',
            params={'range': periodo, 'interval': intervalo},
            timeout=10,
        )
        resposta.raise_for_status()
        payload = resposta.json()
        resultados = payload.get('chart', {}).get('result') or []
        if not resultados:
            return None
        indicadores = resultados[0].get('indicators', {})
        quote = indicadores.get('quote') or []
        if not quote:
            return None
        closes = quote[0].get('close') or []
        closes = [c for c in closes if c is not None]
        if not closes:
            adj = indicadores.get('adjclose') or []
            if adj and isinstance(adj, list) and adj[0].get('adjclose'):
                closes = [c for c in adj[0]['adjclose'] if c is not None]
        if not closes:
            return None
        return float(closes[-1])
    except Exception as exc:
        app.logger.debug('Falha ao consultar chart API para %s: %s', simbolo, exc)
        return None


def obter_precos_acoes(tickers):
    precos = {}
    for ticker in tickers:
        simbolo = ticker_para_yfinance(ticker)
        if not simbolo:
            continue

        preco_encontrado = None

        try:
            ticker_obj = yf.Ticker(simbolo, session=YF_SESSION)

            fast_info = getattr(ticker_obj, 'fast_info', None)
            if fast_info:
                for chave in (
                    'last_price',
                    'regular_market_price',
                    'previous_close',
                    'regular_market_previous_close',
                ):
                    valor = fast_info.get(chave)
                    if valor is not None:
                        preco_encontrado = float(valor)
                        break

            if preco_encontrado is None:
                preco_encontrado = consultar_preco_via_chart(simbolo)

            if preco_encontrado is None:
                historico = ticker_obj.history(period='1mo', interval='1d', auto_adjust=False, raise_errors=False)
                preco_encontrado = extrair_ultimo_fechamento(historico, simbolo)

            if preco_encontrado is None:
                for periodo in ('1mo', '3mo', '6mo'):
                    historico_dl = yf.download(
                        simbolo,
                        period=periodo,
                        interval='1d',
                        auto_adjust=False,
                        progress=False,
                        threads=False,
                        group_by='column',
                        session=YF_SESSION,
                    )
                    preco_encontrado = extrair_ultimo_fechamento(historico_dl, simbolo)
                    if preco_encontrado is not None:
                        break

        except Exception as exc:
            app.logger.warning('Falha ao consultar preço de %s: %s', ticker, exc)

        if preco_encontrado is not None:
            precos[ticker] = preco_encontrado
        else:
            app.logger.warning('Não foi possível obter preço para %s', ticker)

    return precos


def obter_preco_cripto(moeda: str, cotacoes: dict, usd_brl: float | None) -> float | None:
    if not moeda:
        return None

    moeda = moeda.upper()

    if moeda == 'BTC' and cotacoes.get('BTCBRL'):
        try:
            return float(cotacoes['BTCBRL'].get('bid'))
        except (TypeError, ValueError):
            app.logger.debug('Cotação BTCBRL inválida no AwesomeAPI')

    simbolo = f'{moeda}-USD'
    preco_usd = None

    try:
        ticker_obj = yf.Ticker(simbolo, session=YF_SESSION)
        fast_info = getattr(ticker_obj, 'fast_info', None)
        if fast_info:
            for chave in (
                'last_price',
                'regular_market_price',
                'previous_close',
            ):
                valor = fast_info.get(chave)
                if valor is not None:
                    preco_usd = float(valor)
                    break

        if preco_usd is None:
            preco_usd = consultar_preco_via_chart(simbolo)

        if preco_usd is None:
            historico = ticker_obj.history(period='1mo', interval='1d', auto_adjust=False, raise_errors=False)
            preco_usd = extrair_ultimo_fechamento(historico, simbolo)

        if preco_usd is None:
            for periodo in ('1mo', '3mo', '6mo'):
                historico_dl = yf.download(
                    simbolo,
                    period=periodo,
                    interval='1d',
                    auto_adjust=False,
                    progress=False,
                    threads=False,
                    group_by='column',
                    session=YF_SESSION,
                )
                preco_usd = extrair_ultimo_fechamento(historico_dl, simbolo)
                if preco_usd is not None:
                    break

    except Exception as exc:
        app.logger.warning('Falha ao consultar preço de %s: %s', simbolo, exc)
        return None

    if preco_usd is None:
        return None

    if usd_brl:
        return preco_usd * usd_brl
    return preco_usd

@app.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username'].strip()
        password = request.form['password']
        user_doc = mongo.db.users.find_one({'username': username})
        if user_doc and check_password_hash(user_doc['password'], password):
            user = User(user_doc)
            login_user(user)
            return redirect(url_for('dashboard'))
        flash('Usuário ou senha inválidos.')
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')

        if not name:
            flash('Informe seu nome completo.')
        elif not username:
            flash('Escolha um nome de usuário.')
        elif len(password) < 6:
            flash('A senha deve ter pelo menos 6 caracteres.')
        elif mongo.db.users.find_one({'username': username}):
            flash('Usuário já existe.')
        else:
            hashed_pw = generate_password_hash(password)
            mongo.db.users.insert_one({
                'name': name,
                'username': username,
                'password': hashed_pw
            })
            flash('Cadastro realizado! Faça login.')
            return redirect(url_for('login'))
    return render_template('register.html')
@app.route('/dashboard')
@login_required
def dashboard():
    from datetime import datetime
    current_month = request.args.get('month', datetime.now().strftime('%Y-%m'))
    
    # Dicionário para traduzir nomes dos meses para português
    meses_pt = {
        'January': 'Janeiro', 'February': 'Fevereiro', 'March': 'Março',
        'April': 'Abril', 'May': 'Maio', 'June': 'Junho',
        'July': 'Julho', 'August': 'Agosto', 'September': 'Setembro',
        'October': 'Outubro', 'November': 'Novembro', 'December': 'Dezembro'
    }
    
    month_name_en = datetime.strptime(current_month, '%Y-%m').strftime('%B')
    month_name_pt = meses_pt.get(month_name_en, month_name_en)
    year = datetime.strptime(current_month, '%Y-%m').strftime('%Y')
    current_month_display = f"{month_name_pt}-{year}"

    entries = list(mongo.db.entries.find({'user_id': ObjectId(current_user.id)}))
    for e in entries:
        e['valor'] = float(e.get('valor', 0))
        e['tipo'] = e.get('tipo', 'despesa')
        e['categoria'] = e.get('categoria', 'Outros')
        if 'data' in e and isinstance(e['data'], str):
            try:
                e['data'] = datetime.strptime(e['data'], '%Y-%m-%d')
            except Exception:
                e['data'] = None
        elif 'data' not in e:
            e['data'] = None
        e['descricao'] = e.get('descricao', '')

    # Filtrar entries pelo mês selecionado
    filtered_entries = [e for e in entries if e['data'] and e['data'].strftime('%Y-%m') == current_month]

    meses = defaultdict(lambda: {'receita': 0, 'despesa': 0})
    for e in filtered_entries:
        if e['data']:
            mes = e['data'].strftime('%Y-%m')
        else:
            mes = 'Sem data'
        if e['tipo'] == 'receita':
            meses[mes]['receita'] += e['valor']
        else:
            meses[mes]['despesa'] += abs(e['valor'])

    months = sorted(meses.keys())
    receitas = [meses[m]['receita'] for m in months]
    despesas = [meses[m]['despesa'] for m in months]

    categoria_totais = defaultdict(float)
    for e in filtered_entries:
        if e['tipo'] == 'despesa':
            categoria_totais[e['categoria']] += abs(e['valor'])
    total_despesas = sum(categoria_totais.values())
    categorias = list(categoria_totais.keys())
    percentual_categoria = [round((v/total_despesas)*100, 1) if total_despesas else 0 for v in categoria_totais.values()]
    cores_categoria = [
         '#2196f3', '#ff9800', '#9c27b0', '#607d8b', '#4caf50', '#e53935'
    ][:len(categorias)]

    # Total
    total = sum(e['valor'] if e['tipo']=='receita' else -abs(e['valor']) for e in filtered_entries)

    dashboard_data = {
        'months': months,
        'receitas': receitas,
        'despesas': despesas,
        'categorias': categorias,
        'percentual_categoria': percentual_categoria,
        'cores_categoria': cores_categoria,
        'total': total
    }

    return render_template('dashboard.html', entries=filtered_entries, dashboard_data=dashboard_data, current_month=current_month, current_month_display=current_month_display)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/api/entries', methods=['GET'])
@login_required
def api_entries():
    entries = list(mongo.db.entries.find({'user_id': ObjectId(current_user.id)}))
    for e in entries:
        e['_id'] = str(e['_id'])
    return {'entries': entries}

@app.route('/add_entry', methods=['POST'])
@login_required
def add_entry():
    descricao = request.form.get('descricao')
    valor = float(request.form.get('valor', 0))
    categoria = request.form.get('categoria')
    tipo = request.form.get('tipo')
    data_str = request.form.get('data')
    try:
        data = datetime.strptime(data_str, '%Y-%m-%d')
    except Exception:
        data = None
    mongo.db.entries.insert_one({
        'user_id': ObjectId(current_user.id),
        'descricao': descricao,
        'valor': valor,
        'categoria': categoria,
        'tipo': tipo,
        'data': data
    })
    flash('Lançamento cadastrado com sucesso!')
    return redirect(url_for('dashboard'))

@app.route('/delete_entry/<entry_id>', methods=['DELETE'])
@login_required
def delete_entry(entry_id):
    mongo.db.entries.delete_one({'_id': ObjectId(entry_id), 'user_id': ObjectId(current_user.id)})
    return '', 204

@app.route('/tendencias')
@login_required
def tendencias():
    entries = list(mongo.db.entries.find({'user_id': ObjectId(current_user.id)}))
    
    # Processar datas dos lançamentos
    for e in entries:
        e['valor'] = float(e.get('valor', 0))
        e['tipo'] = e.get('tipo', 'despesa')
        if 'data' in e and isinstance(e['data'], str):
            try:
                e['data'] = datetime.strptime(e['data'], '%Y-%m-%d')
            except Exception:
                e['data'] = None
        elif 'data' not in e:
            e['data'] = None

    # Verificar se há pelo menos 3 meses de dados
    months_with_data = set()
    for e in entries:
        if e['data']:
            months_with_data.add(e['data'].strftime('%Y-%m'))
    
    if len(months_with_data) < 3:
        return render_template('tendencias.html', 
                             has_enough_data=False, 
                             months_needed=3 - len(months_with_data),
                             tendencias_data={'labels': [], 'receitas': [], 'despesas': [], 'saldos': []})

    # Calcular tendências mensais
    monthly_data = defaultdict(lambda: {'receita': 0, 'despesa': 0, 'total': 0})
    for e in entries:
        if e['data']:
            mes = e['data'].strftime('%Y-%m')
            if e['tipo'] == 'receita':
                monthly_data[mes]['receita'] += e['valor']
            else:
                monthly_data[mes]['despesa'] += abs(e['valor'])
            monthly_data[mes]['total'] = monthly_data[mes]['receita'] - monthly_data[mes]['despesa']

    # Ordenar por mês
    sorted_months = sorted(monthly_data.keys())
    
    # Preparar dados para o gráfico
    labels = []
    receitas = []
    despesas = []
    saldos = []
    
    # Dicionário para traduzir nomes dos meses
    meses_pt = {
        'January': 'Jan', 'February': 'Fev', 'March': 'Mar',
        'April': 'Abr', 'May': 'Mai', 'June': 'Jun',
        'July': 'Jul', 'August': 'Ago', 'September': 'Set',
        'October': 'Out', 'November': 'Nov', 'December': 'Dez'
    }
    
    for mes in sorted_months:
        year, month = mes.split('-')
        month_name_en = datetime.strptime(mes, '%Y-%m').strftime('%B')
        month_name_pt = meses_pt.get(month_name_en, month_name_en)
        labels.append(f"{month_name_pt}/{year[-2:]}")
        receitas.append(monthly_data[mes]['receita'])
        despesas.append(monthly_data[mes]['despesa'])
        saldos.append(monthly_data[mes]['total'])

    tendencias_data = {
        'labels': labels,
        'receitas': receitas,
        'despesas': despesas,
        'saldos': saldos
    }

    return render_template('tendencias.html', 
                         has_enough_data=True, 
                         tendencias_data=tendencias_data)

@app.route('/investimentos')
@login_required
def investimentos():
    return render_template('investimentos.html')

@app.route('/api/ativos', methods=['GET', 'POST'])
@login_required
def api_ativos():
    if request.method == 'GET':
        ativos = list(mongo.db.ativos.find({'user_id': ObjectId(current_user.id)}))

        tickers = {ativo.get('ticker') for ativo in ativos if ativo.get('tipo') == 'acao' and ativo.get('ticker')}
        precos_acoes = obter_precos_acoes(tickers) if tickers else {}

        try:
            cotacoes_moedas = obter_cotacoes_moedas()
        except Exception as exc:
            app.logger.warning('Falha ao buscar cotações de moedas: %s', exc)
            cotacoes_moedas = {}

        usd_brl = None
        try:
            usd_brl = float(cotacoes_moedas.get('USDBRL', {}).get('bid')) if cotacoes_moedas.get('USDBRL') else None
        except (TypeError, ValueError):
            usd_brl = None

        btc_brl = None
        try:
            btc_brl = float(cotacoes_moedas.get('BTCBRL', {}).get('bid')) if cotacoes_moedas.get('BTCBRL') else None
        except (TypeError, ValueError):
            btc_brl = None

        total_atual = 0.0
        total_investido = 0.0
        ativos_formatados = []

        for ativo in ativos:
            ativo_formatado = {k: v for k, v in ativo.items()}
            ativo_formatado['_id'] = str(ativo_formatado['_id'])
            ativo_formatado.pop('user_id', None)

            if 'created_at' in ativo_formatado and isinstance(ativo_formatado['created_at'], datetime):
                ativo_formatado['created_at'] = ativo_formatado['created_at'].isoformat()

            valor_atual = None
            valor_investido = ativo_formatado.get('valor_investido', 0.0)

            if ativo_formatado.get('tipo') == 'acao':
                ticker = ativo_formatado.get('ticker')
                preco_unitario = precos_acoes.get(ticker)
                if preco_unitario is not None:
                    valor_atual = float(preco_unitario) * int(ativo_formatado.get('quantidade', 0))
                    ativo_formatado['preco_unitario'] = round(float(preco_unitario), 2)
                    valor_investido = valor_investido or valor_atual

            elif ativo_formatado.get('tipo') == 'renda-fixa':
                if valor_investido is None:
                    valor_investido = 0.0
                valor_atual = float(valor_investido)

            elif ativo_formatado.get('tipo') == 'cripto':
                moeda = ativo_formatado.get('moeda')
                if moeda == 'BTC' and btc_brl:
                    preco_unitario = btc_brl
                else:
                    preco_unitario = obter_preco_cripto(moeda, cotacoes_moedas, usd_brl)
                if preco_unitario is not None:
                    valor_atual = float(preco_unitario) * float(ativo_formatado.get('quantidade', 0))
                    ativo_formatado['preco_unitario'] = round(float(preco_unitario), 2)
                    valor_investido = valor_investido or valor_atual

            if valor_atual is not None:
                valor_atual = round(float(valor_atual), 2)
                total_atual += valor_atual
            elif valor_investido:
                try:
                    valor_atual = round(float(valor_investido), 2)
                    ativo_formatado['valor_atual_estimado'] = True
                    total_atual += valor_atual
                except (TypeError, ValueError):
                    valor_atual = None

            if valor_investido:
                try:
                    total_investido += float(valor_investido)
                except (TypeError, ValueError):
                    pass

            ativo_formatado['valor_atual'] = valor_atual
            if 'valor_investido' in ativo_formatado and ativo_formatado['valor_investido'] is not None:
                ativo_formatado['valor_investido'] = round(float(ativo_formatado['valor_investido']), 2)

            ativos_formatados.append(ativo_formatado)

        resumo = {
            'total_atual': round(total_atual, 2),
            'total_investido': round(total_investido, 2),
            'quantidade_ativos': len(ativos_formatados),
            'ultima_atualizacao': datetime.utcnow().isoformat(),
        }

        return {'ativos': ativos_formatados, 'resumo': resumo}

    payload = request.get_json(force=True) or {}
    tipo = payload.get('tipo')
    if tipo not in {'acao', 'renda-fixa', 'cripto'}:
        return {'error': 'Tipo de ativo inválido.'}, 400

    documento = {
        'user_id': ObjectId(current_user.id),
        'tipo': tipo,
        'created_at': datetime.utcnow()
    }

    if tipo == 'acao':
        ticker = (payload.get('ticker') or '').upper()
        quantidade = payload.get('quantidade')
        if not ticker or quantidade is None:
            return {'error': 'Ticker e quantidade são obrigatórios.'}, 400
        try:
            quantidade = int(quantidade)
        except (TypeError, ValueError):
            return {'error': 'Quantidade inválida.'}, 400
        documento.update({'ticker': ticker, 'quantidade': quantidade})

    elif tipo == 'renda-fixa':
        nome = (payload.get('nome') or '').strip()
        valor_investido = payload.get('valor_investido') or payload.get('valor')
        if not nome or valor_investido is None:
            return {'error': 'Nome e valor investido são obrigatórios.'}, 400
        try:
            valor_investido = float(valor_investido)
        except (TypeError, ValueError):
            return {'error': 'Valor investido inválido.'}, 400
        documento.update({'nome': nome, 'valor_investido': valor_investido})

    elif tipo == 'cripto':
        moeda = (payload.get('moeda') or '').upper()
        quantidade = payload.get('quantidade')
        if not moeda or quantidade is None:
            return {'error': 'Criptomoeda e quantidade são obrigatórias.'}, 400
        try:
            quantidade = float(quantidade)
        except (TypeError, ValueError):
            return {'error': 'Quantidade inválida.'}, 400
        documento.update({'moeda': moeda, 'quantidade': quantidade})

    resultado = mongo.db.ativos.insert_one(documento)
    documento['_id'] = str(resultado.inserted_id)
    documento['created_at'] = documento['created_at'].isoformat()
    documento['user_id'] = str(documento['user_id'])
    return documento, 201


@app.route('/api/ativos/<ativo_id>', methods=['DELETE'])
@login_required
def api_ativos_delete(ativo_id):
    try:
        oid = ObjectId(ativo_id)
    except Exception:
        return {'error': 'Identificador inválido.'}, 400

    resultado = mongo.db.ativos.delete_one({'_id': oid, 'user_id': ObjectId(current_user.id)})
    if resultado.deleted_count == 0:
        return {'error': 'Ativo não encontrado.'}, 404
    return '', 204

@app.route('/api/cotacoes')
@login_required
def api_cotacoes():
    try:
        return obter_cotacoes_moedas()
    except Exception as e:
        return {'error': str(e)}, 500

# Configuração para Render
if os.environ.get('RENDER'):
    app.config['DEBUG'] = False
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)

if __name__ == '__main__':
    app.run(debug=True)
