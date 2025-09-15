from flask import Flask
from flask_pymongo import PyMongo
import os
from dotenv import load_dotenv
from bson import ObjectId

# Carregar variáveis de ambiente
load_dotenv()

# Configurar Flask e MongoDB
app = Flask(__name__)
app.config['MONGO_URI'] = os.getenv('MONGO_URI', 'mongodb://localhost:27017/smartmoney')
mongo = PyMongo(app)

def check_test_data():
    with app.app_context():
        # Encontrar usuário smart01
        user = mongo.db.users.find_one({'username': 'smart01'})
        if not user:
            print("Usuário smart01 não encontrado!")
            return

        print(f"Usuário encontrado: {user['_id']}")

        # Contar entradas do usuário
        entries_count = mongo.db.entries.count_documents({'user_id': user['_id']})
        print(f"Total de entradas encontradas: {entries_count}")

        # Listar algumas entradas
        entries = list(mongo.db.entries.find({'user_id': user['_id']}).limit(5))
        print("\nPrimeiras 5 entradas:")
        for entry in entries:
            print(f"- {entry.get('descricao', 'N/A')}: R$ {entry.get('valor', 0)} ({entry.get('tipo', 'N/A')}) - {entry.get('data', 'N/A')}")

        # Verificar entradas por mês
        from datetime import datetime
        months = ['2025-06', '2025-07', '2025-08', '2025-09']
        for month in months:
            count = mongo.db.entries.count_documents({
                'user_id': user['_id'],
                'data': {'$gte': datetime(2025, int(month.split('-')[1]), 1), '$lt': datetime(2025, int(month.split('-')[1]) + 1, 1)}
            })
            print(f"Entradas em {month}: {count}")

if __name__ == '__main__':
    check_test_data()
