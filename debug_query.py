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

def debug_query():
    with app.app_context():
        # Encontrar usuário smart01
        user = mongo.db.users.find_one({'username': 'smart01'})
        if not user:
            print("Usuário smart01 não encontrado!")
            return

        user_id_str = str(user['_id'])
        user_id_obj = user['_id']

        print(f"User ID string: {user_id_str}")
        print(f"User ID ObjectId: {user_id_obj}")

        # Testar query com string
        entries_str = list(mongo.db.entries.find({'user_id': user_id_str}))
        print(f"Query com string encontrou: {len(entries_str)} entradas")

        # Testar query com ObjectId
        entries_obj = list(mongo.db.entries.find({'user_id': user_id_obj}))
        print(f"Query com ObjectId encontrou: {len(entries_obj)} entradas")

        # Verificar como os dados foram armazenados
        sample_entry = mongo.db.entries.find_one({})
        if sample_entry:
            print(f"Tipo do user_id armazenado: {type(sample_entry['user_id'])}")
            print(f"Valor do user_id armazenado: {sample_entry['user_id']}")

if __name__ == '__main__':
    debug_query()
