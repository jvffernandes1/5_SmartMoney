from flask import Flask
from flask_pymongo import PyMongo
import os
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

# Configurar Flask e MongoDB
app = Flask(__name__)
app.config['MONGO_URI'] = os.getenv('MONGO_URI', 'mongodb://localhost:27017/smartmoney')
mongo = PyMongo(app)

def check_users():
    with app.app_context():
        # Procurar por usuários que contenham "smart" no nome
        users = list(mongo.db.users.find({
            'username': {'$regex': 'smart', '$options': 'i'}
        }))

        if not users:
            print("❌ Nenhum usuário encontrado com 'smart' no nome")
            return

        print("=== USUÁRIOS ENCONTRADOS ===")
        for user in users:
            print(f"Usuário: {user['username']}")
            print(f"ID: {user['_id']}")
            print("---")

        # Verificar se há dados de teste
        print("\n=== VERIFICANDO DADOS DE TESTE ===")
        test_user = mongo.db.users.find_one({'username': 'smart01'})
        if test_user:
            entries_count = mongo.db.entries.count_documents({'user_id': test_user['_id']})
            print(f"✅ Usuário smart01 encontrado com {entries_count} lançamentos")
        else:
            print("❌ Usuário smart01 não encontrado")

if __name__ == '__main__':
    check_users()