
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
    entries = list(mongo.db.entries.find({'user_id': current_user.id}))
    # Garantir campos e converter datas
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

    # Gráfico de barras: receitas/despesas por mês
    meses = defaultdict(lambda: {'receita': 0, 'despesa': 0})
    for e in entries:
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

    # Gráfico de pizza: percentual por categoria
    categoria_totais = defaultdict(float)
    for e in entries:
        if e['tipo'] == 'despesa':
            categoria_totais[e['categoria']] += abs(e['valor'])
    total_despesas = sum(categoria_totais.values())
    categorias = list(categoria_totais.keys())
    percentual_categoria = [round((v/total_despesas)*100, 1) if total_despesas else 0 for v in categoria_totais.values()]
    cores_categoria = [
        '#A27B5C', '#3F4E4F', '#dcc797', '#2C3639', '#4caf50', '#e53935', '#2196f3', '#ff9800', '#9c27b0', '#607d8b'
    ][:len(categorias)]

    # Total
    total = sum(e['valor'] if e['tipo']=='receita' else -abs(e['valor']) for e in entries)

    dashboard_data = {
        'months': months,
        'receitas': receitas,
        'despesas': despesas,
        'categorias': categorias,
        'percentual_categoria': percentual_categoria,
        'cores_categoria': cores_categoria,
        'total': total
    }

    return render_template('dashboard.html', entries=entries, dashboard_data=dashboard_data)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

# API endpoint exemplo
@app.route('/api/entries', methods=['GET'])
@login_required
def api_entries():
    entries = list(mongo.db.entries.find({'user_id': current_user.id}))
    for e in entries:
        e['_id'] = str(e['_id'])
    return {'entries': entries}

# Cadastro de lançamentos
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
        'user_id': current_user.id,
        'descricao': descricao,
        'valor': valor,
        'categoria': categoria,
        'tipo': tipo,
        'data': data
    })
    flash('Lançamento cadastrado com sucesso!')
    return redirect(url_for('dashboard'))

# Exclusão de lançamentos
@app.route('/delete_entry/<entry_id>', methods=['DELETE'])
@login_required
def delete_entry(entry_id):
    mongo.db.entries.delete_one({'_id': ObjectId(entry_id), 'user_id': current_user.id})
    return '', 204

if __name__ == '__main__':
    app.run(debug=True)
