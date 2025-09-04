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
- Dashboard de finanças pessoais
- Lançamento de receitas e despesas
- Relatórios e gráficos (opcional: análise de dados)
- API para integração
- Acessibilidade

## Como rodar o projeto
1. Instale as dependências: `pip install -r requirements.txt`
2. Configure o MongoDB (local ou Atlas)
3. Execute: `flask run`

## Testes
- Execute `pytest` para rodar os testes automatizados.

## Deploy
- Estrutura pronta para deploy em serviços como Render, Heroku ou similares.

---

> Personalize as variáveis de cor no arquivo `static/css/style.css` conforme desejar.
