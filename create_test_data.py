from flask import Flask
from flask_pymongo import PyMongo
from werkzeug.security import generate_password_hash
import os
from dotenv import load_dotenv
from datetime import datetime
from bson import ObjectId

# Carregar variáveis de ambiente
load_dotenv()

# Configurar Flask e MongoDB
app = Flask(__name__)
app.config['MONGO_URI'] = os.getenv('MONGO_URI', 'mongodb://localhost:27017/smartmoney')
mongo = PyMongo(app)

def create_test_user():
    with app.app_context():
        # Verificar se usuário já existe
        if mongo.db.users.find_one({'username': 'smart01'}):
            print("Usuário smart01 já existe!")
            return

        # Criar usuário
        hashed_pw = generate_password_hash('teste2025')
        user_result = mongo.db.users.insert_one({
            'username': 'smart01',
            'password': hashed_pw
        })
        user_id = user_result.inserted_id
        print(f"Usuário criado com ID: {user_id}")

        # Dados de teste - lançamentos de junho a setembro
        test_entries = [
            # JUNHO 2025
            {'user_id': user_id, 'descricao': 'Salário', 'valor': 2000.00, 'categoria': 'Salário', 'tipo': 'receita', 'data': datetime(2025, 6, 1)},
            {'user_id': user_id, 'descricao': 'Aluguel', 'valor': 800.00, 'categoria': 'Contas', 'tipo': 'despesa', 'data': datetime(2025, 6, 5)},
            {'user_id': user_id, 'descricao': 'Supermercado', 'valor': 450.00, 'categoria': 'Alimentação', 'tipo': 'despesa', 'data': datetime(2025, 6, 10)},
            {'user_id': user_id, 'descricao': 'Combustível', 'valor': 200.00, 'categoria': 'Contas', 'tipo': 'despesa', 'data': datetime(2025, 6, 15)},
            {'user_id': user_id, 'descricao': 'Restaurante', 'valor': 120.00, 'categoria': 'Lazer', 'tipo': 'despesa', 'data': datetime(2025, 6, 20)},
            {'user_id': user_id, 'descricao': 'Farmácia', 'valor': 80.00, 'categoria': 'Alimentação', 'tipo': 'despesa', 'data': datetime(2025, 6, 25)},

            # JULHO 2025
            {'user_id': user_id, 'descricao': 'Salário', 'valor': 2000.00, 'categoria': 'Salário', 'tipo': 'receita', 'data': datetime(2025, 7, 1)},
            {'user_id': user_id, 'descricao': 'Aluguel', 'valor': 800.00, 'categoria': 'Contas', 'tipo': 'despesa', 'data': datetime(2025, 7, 5)},
            {'user_id': user_id, 'descricao': 'Supermercado', 'valor': 520.00, 'categoria': 'Alimentação', 'tipo': 'despesa', 'data': datetime(2025, 7, 8)},
            {'user_id': user_id, 'descricao': 'Internet', 'valor': 100.00, 'categoria': 'Contas', 'tipo': 'despesa', 'data': datetime(2025, 7, 12)},
            {'user_id': user_id, 'descricao': 'Cinema', 'valor': 60.00, 'categoria': 'Lazer', 'tipo': 'despesa', 'data': datetime(2025, 7, 18)},
            {'user_id': user_id, 'descricao': 'Academia', 'valor': 150.00, 'categoria': 'Lazer', 'tipo': 'despesa', 'data': datetime(2025, 7, 22)},
            {'user_id': user_id, 'descricao': 'Combustível', 'valor': 180.00, 'categoria': 'Contas', 'tipo': 'despesa', 'data': datetime(2025, 7, 28)},

            # AGOSTO 2025
            {'user_id': user_id, 'descricao': 'Salário', 'valor': 2000.00, 'categoria': 'Salário', 'tipo': 'receita', 'data': datetime(2025, 8, 1)},
            {'user_id': user_id, 'descricao': 'Aluguel', 'valor': 800.00, 'categoria': 'Contas', 'tipo': 'despesa', 'data': datetime(2025, 8, 5)},
            {'user_id': user_id, 'descricao': 'Supermercado', 'valor': 480.00, 'categoria': 'Alimentação', 'tipo': 'despesa', 'data': datetime(2025, 8, 7)},
            {'user_id': user_id, 'descricao': 'Energia elétrica', 'valor': 120.00, 'categoria': 'Contas', 'tipo': 'despesa', 'data': datetime(2025, 8, 10)},
            {'user_id': user_id, 'descricao': 'Restaurante', 'valor': 95.00, 'categoria': 'Lazer', 'tipo': 'despesa', 'data': datetime(2025, 8, 15)},
            {'user_id': user_id, 'descricao': 'Farmácia', 'valor': 65.00, 'categoria': 'Alimentação', 'tipo': 'despesa', 'data': datetime(2025, 8, 20)},
            {'user_id': user_id, 'descricao': 'Combustível', 'valor': 220.00, 'categoria': 'Contas', 'tipo': 'despesa', 'data': datetime(2025, 8, 25)},
            {'user_id': user_id, 'descricao': 'Shopping', 'valor': 300.00, 'categoria': 'Lazer', 'tipo': 'despesa', 'data': datetime(2025, 8, 30)},

            # SETEMBRO 2025
            {'user_id': user_id, 'descricao': 'Salário', 'valor': 2000.00, 'categoria': 'Salário', 'tipo': 'receita', 'data': datetime(2025, 9, 1)},
            {'user_id': user_id, 'descricao': 'Bônus', 'valor': 500.00, 'categoria': 'Recebidos', 'tipo': 'receita', 'data': datetime(2025, 9, 1)},
            {'user_id': user_id, 'descricao': 'Aluguel', 'valor': 800.00, 'categoria': 'Contas', 'tipo': 'despesa', 'data': datetime(2025, 9, 5)},
            {'user_id': user_id, 'descricao': 'Supermercado', 'valor': 410.00, 'categoria': 'Alimentação', 'tipo': 'despesa', 'data': datetime(2025, 9, 8)},
            {'user_id': user_id, 'descricao': 'Internet', 'valor': 100.00, 'categoria': 'Contas', 'tipo': 'despesa', 'data': datetime(2025, 9, 12)},
            {'user_id': user_id, 'descricao': 'Academia', 'valor': 150.00, 'categoria': 'Lazer', 'tipo': 'despesa', 'data': datetime(2025, 9, 15)},
            {'user_id': user_id, 'descricao': 'Restaurante', 'valor': 85.00, 'categoria': 'Lazer', 'tipo': 'despesa', 'data': datetime(2025, 9, 20)},
            {'user_id': user_id, 'descricao': 'Farmácia', 'valor': 90.00, 'categoria': 'Alimentação', 'tipo': 'despesa', 'data': datetime(2025, 9, 25)},
            {'user_id': user_id, 'descricao': 'Combustível', 'valor': 190.00, 'categoria': 'Contas', 'tipo': 'despesa', 'data': datetime(2025, 9, 28)},
        ]

        # Inserir lançamentos
        result = mongo.db.entries.insert_many(test_entries)
        print(f"Inseridos {len(result.inserted_ids)} lançamentos de teste")

        print("\n=== RESUMO DOS DADOS DE TESTE ===")
        print("Usuário: smart01")
        print("Senha: teste2025")
        print("\nLançamentos por mês:")
        print("- JUNHO: Salário R$ 2.000 + 5 despesas = R$ 1.650")
        print("- JULHO: Salário R$ 2.000 + 6 despesas = R$ 1.810")
        print("- AGOSTO: Salário R$ 2.000 + 7 despesas = R$ 2.080")
        print("- SETEMBRO: Salário R$ 2.000 + Bônus R$ 500 + 7 despesas = R$ 2.425")
        print("\nTotal de meses com dados: 4")
        print("Agora você pode testar todas as funcionalidades!")

if __name__ == '__main__':
    create_test_user()
