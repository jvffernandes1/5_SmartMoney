
from flask import Flask, render_template, redirect, url_for, request, flash
from flask_pymongo import PyMongo
from flask_login import LoginManager, login_user, login_required, logout_user, UserMixin, current_user
from werkzeug.security import generate_password_hash, check_password_hash
import os
from dotenv import load_dotenv
from bson import ObjectId

load_dotenv()

app = Flask(__name__)
app.config['MONGO_URI'] = os.getenv('MONGO_URI', 'mongodb://localhost:27017/smartmoney')
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'changeme')
mongo = PyMongo(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

class User(UserMixin):
    def __init__(self, user_doc):
        self.id = str(user_doc['_id'])
        self.username = user_doc['username']

    @staticmethod
    def get(user_id):
        user_doc = mongo.db.users.find_one({'_id': ObjectId(user_id)})
        return User(user_doc) if user_doc else None

@login_manager.user_loader
def load_user(user_id):
    user_doc = mongo.db.users.find_one({'_id': ObjectId(user_id)})
    return User(user_doc) if user_doc else None

@app.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
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
        username = request.form['username']
        password = request.form['password']
        if mongo.db.users.find_one({'username': username}):
            flash('Usuário já existe.')
        else:
            hashed_pw = generate_password_hash(password)
            mongo.db.users.insert_one({'username': username, 'password': hashed_pw})
            flash('Cadastro realizado! Faça login.')
            return redirect(url_for('login'))
    return render_template('register.html')


from collections import defaultdict
from datetime import datetime

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

@app.route('/api/cotacoes')
@login_required
def api_cotacoes():
    import requests
    url = 'https://economia.awesomeapi.com.br/json/last/USD-BRL,EUR-BRL,BTC-BRL?token=fa63ba9b800614afd38479ef0a06210a199d86bfea5fa979a407b725cf357ba3'
    try:
        response = requests.get(url)
        data = response.json()
        return data
    except Exception as e:
        return {'error': str(e)}, 500

# Configuração para Render
import os
if os.environ.get('RENDER'):
    app.config['DEBUG'] = False
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)

if __name__ == '__main__':
    app.run(debug=True)
