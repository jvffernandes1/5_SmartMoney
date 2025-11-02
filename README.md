# Smart Money

Smart Money é uma aplicação web para gestão de finanças pessoais, desenvolvida com Flask e MongoDB. O projeto inclui sistema de login, interface acessível, integração com API, scripts web (JavaScript), controle de versão, testes automatizados e estrutura para deploy em nuvem. O CSS utiliza variáveis no :root para fácil customização de cores.

## Tecnologias
- Flask
- MongoDB
- JavaScript
- HTML5/CSS3
- Testes automatizados (pytest)
- Controle de versão (git)
- Estrutura para deploy em nuvem

## Cores principais (editáveis via CSS :root)
- --cor-principal: #2C3639
- --cor-secundaria: #3F4E4F
- --cor-texto: #DCD7C9
- --cor-link_hover: #dcc797
- --cor-destaque: #A27B5C
- --cor-menu: #1b2225

## Funcionalidades
- Cadastro e login de usuários
- Homepage com visão geral do Smart Money
- Dashboard de finanças pessoais
- Lançamento de receitas e despesas
- Relatórios, gráficos e análises de tendências
- Carteira de investimentos com cotações em tempo real (yfinance + AwesomeAPI)
- API para integração
- Acessibilidade

## Variáveis de Ambiente
Configure um arquivo `.env` com as chaves abaixo (veja `.env.example`):

- `MONGO_URI`: String de conexão do MongoDB Atlas/Cluster
- `SECRET_KEY`: Chave secreta para sessões Flask
- `AWESOME_API_TOKEN`: Token da AwesomeAPI (opcional, usa padrão do projeto)

## Como rodar o projeto
1. Instale as dependências: `pip install -r requirements.txt`
2. Configure o MongoDB (local ou Atlas) e o arquivo `.env`
3. Execute o servidor: `python app.py`
4. Acesse `http://localhost:5000`

## Testes
- Execute `pytest` para rodar os testes automatizados.

## Deploy no Render.com

1. **Configure as variáveis de ambiente no Render:**
   - `MONGO_URI`: String de conexão do MongoDB Atlas
   - `SECRET_KEY`: Chave secreta forte (gere uma aleatória)
   - `RENDER`: `true`

2. **Configurações do Render:**
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `python app.py`

3. **Banco de dados:** Use MongoDB Atlas (gratuito) para produção.

---

> Personalize as variáveis de cor no arquivo `static/css/style.css` conforme desejar.
