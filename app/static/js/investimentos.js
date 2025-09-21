// Função para buscar cotações da API
async function buscarCotacoes() {
    try {
        const response = await fetch('/api/cotacoes');
        const data = await response.json();

        // USD
        if (data.USDBRL) {
            document.getElementById('usd-valor').textContent = `R$ ${parseFloat(data.USDBRL.bid).toFixed(2)}`;
            document.getElementById('usd-pct').textContent = `${data.USDBRL.pctChange}%`;
            document.getElementById('usd-status').textContent = 'Atualizado';
            document.getElementById('usd-status').style.color = '#4CAF50';
        }

        // EUR
        if (data.EURBRL) {
            document.getElementById('eur-valor').textContent = `R$ ${parseFloat(data.EURBRL.bid).toFixed(2)}`;
            document.getElementById('eur-pct').textContent = `${data.EURBRL.pctChange}%`;
            document.getElementById('eur-status').textContent = 'Atualizado';
            document.getElementById('eur-status').style.color = '#4CAF50';
        }

        // BTC
        if (data.BTCBRL) {
            document.getElementById('btc-valor').textContent = `R$ ${parseFloat(data.BTCBRL.bid).toLocaleString('pt-BR', {minimumFractionDigits: 2})}`;
            document.getElementById('btc-pct').textContent = `${data.BTCBRL.pctChange}%`;
            document.getElementById('btc-status').textContent = 'Atualizado';
            document.getElementById('btc-status').style.color = '#4CAF50';
        }
    } catch (error) {
        console.error('Erro ao buscar cotações:', error);
        document.getElementById('usd-status').textContent = 'Erro';
        document.getElementById('eur-status').textContent = 'Erro';
        document.getElementById('btc-status').textContent = 'Erro';
        document.getElementById('usd-status').style.color = '#f44336';
        document.getElementById('eur-status').style.color = '#f44336';
        document.getElementById('btc-status').style.color = '#f44336';
    }
}

// Controle do Modal
const modal = document.getElementById('modal-ativo');
const abrirModalBtn = document.getElementById('abrir-modal-ativo');
const fecharModalBtn = document.getElementById('fechar-modal');
const cancelarBtn = document.getElementById('cancelar-ativo');

function abrirModal() {
    modal.style.display = 'flex';
    document.body.style.overflow = 'hidden'; // Impede scroll da página
}

function fecharModal() {
    modal.style.display = 'none';
    document.body.style.overflow = 'auto'; // Restaura scroll da página
    // Limpar formulário
    document.getElementById('tipo-ativo').value = '';
    document.getElementById('campos-acao').style.display = 'none';
    document.getElementById('campos-renda-fixa').style.display = 'none';
    document.getElementById('campos-cripto').style.display = 'none';
    document.getElementById('ticker-acao').value = '';
    document.getElementById('quantidade-acao').value = '';
    document.getElementById('nome-renda-fixa').value = '';
    document.getElementById('valor-renda-fixa').value = '';
    document.getElementById('tipo-cripto').value = '';
    document.getElementById('quantidade-cripto').value = '';
}

abrirModalBtn.addEventListener('click', abrirModal);
fecharModalBtn.addEventListener('click', fecharModal);
cancelarBtn.addEventListener('click', fecharModal);

// Fechar modal ao clicar fora dele
modal.addEventListener('click', function(e) {
    if (e.target === modal) {
        fecharModal();
    }
});

// Botão para atualizar cotações
document.getElementById('atualizar-cotacoes').addEventListener('click', () => {
    buscarCotacoes();
    // Feedback visual
    const btn = document.getElementById('atualizar-cotacoes');
    const originalText = btn.textContent;
    btn.textContent = 'Atualizando...';
    btn.disabled = true;
    setTimeout(() => {
        btn.textContent = originalText;
        btn.disabled = false;
    }, 2000);
});

// Controle dos campos dinâmicos
document.getElementById('tipo-ativo').addEventListener('change', function() {
    const tipo = this.value;

    // Esconder todos os campos específicos
    document.getElementById('campos-acao').style.display = 'none';
    document.getElementById('campos-renda-fixa').style.display = 'none';
    document.getElementById('campos-cripto').style.display = 'none';

    // Mostrar campos específicos do tipo selecionado
    if (tipo === 'acao') {
        document.getElementById('campos-acao').style.display = 'block';
    } else if (tipo === 'renda-fixa') {
        document.getElementById('campos-renda-fixa').style.display = 'block';
    } else if (tipo === 'cripto') {
        document.getElementById('campos-cripto').style.display = 'block';
    }
});

// Função para formatar valores monetários
function formatarMoeda(valor) {
    return new Intl.NumberFormat('pt-BR', {
        style: 'currency',
        currency: 'BRL'
    }).format(valor);
}

// Função para formatar números cripto
function formatarCripto(valor) {
    return parseFloat(valor).toFixed(8);
}

// Função para carregar ativos do localStorage
function carregarAtivos() {
    const ativos = JSON.parse(localStorage.getItem('carteira_ativos') || '[]');
    const listaAtivos = document.getElementById('lista-ativos');

    if (ativos.length === 0) {
        listaAtivos.innerHTML = '<p style="color: #666; text-align: center; padding: 2rem;">Nenhum ativo adicionado ainda. Adicione seu primeiro ativo acima!</p>';
        return;
    }

    listaAtivos.innerHTML = ativos.map((ativo, index) => {
        let detalhes = '';
        let tipoLabel = '';

        if (ativo.tipo === 'acao') {
            tipoLabel = 'Ação Nacional';
            detalhes = `${ativo.ticker} - ${ativo.quantidade} ações`;
        } else if (ativo.tipo === 'renda-fixa') {
            tipoLabel = 'Renda Fixa';
            detalhes = `${ativo.nome} - ${formatarMoeda(ativo.valor)}`;
        } else if (ativo.tipo === 'cripto') {
            tipoLabel = 'Criptomoeda';
            detalhes = `${ativo.moeda} - ${formatarCripto(ativo.quantidade)} ${ativo.moeda}`;
        }

        return `
            <div style="background: var(--cor-principal); padding: 1rem; border-radius: 6px; margin-bottom: 0.5rem; border: 1px solid var(--cor-destaque); display: flex; justify-content: space-between; align-items: center;">
                <div>
                    <div style="font-weight: bold; color: var(--cor-texto); margin-bottom: 0.25rem;">${tipoLabel}</div>
                    <div style="color: #666;">${detalhes}</div>
                </div>
                <button onclick="removerAtivo(${index})" style="background: #f44336; color: white; border: none; padding: 0.25rem 0.5rem; border-radius: 4px; cursor: pointer; font-size: 0.8rem;">Remover</button>
            </div>
        `;
    }).join('');
}

// Função para remover ativo
function removerAtivo(index) {
    if (confirm('Tem certeza que deseja remover este ativo?')) {
        const ativos = JSON.parse(localStorage.getItem('carteira_ativos') || '[]');
        ativos.splice(index, 1);
        localStorage.setItem('carteira_ativos', JSON.stringify(ativos));
        carregarAtivos();
    }
}

// Adicionar ativo
document.getElementById('adicionar-ativo').addEventListener('click', function() {
    const tipo = document.getElementById('tipo-ativo').value;

    if (!tipo) {
        alert('Por favor, selecione o tipo de ativo.');
        return;
    }

    let novoAtivo = { tipo };

    if (tipo === 'acao') {
        const ticker = document.getElementById('ticker-acao').value.toUpperCase();
        const quantidade = parseInt(document.getElementById('quantidade-acao').value);

        if (!ticker || !quantidade) {
            alert('Por favor, preencha o ticker e a quantidade.');
            return;
        }

        novoAtivo.ticker = ticker;
        novoAtivo.quantidade = quantidade;

    } else if (tipo === 'renda-fixa') {
        const nome = document.getElementById('nome-renda-fixa').value;
        const valor = parseFloat(document.getElementById('valor-renda-fixa').value.replace(',', '.'));

        if (!nome || !valor) {
            alert('Por favor, preencha o nome e o valor.');
            return;
        }

        novoAtivo.nome = nome;
        novoAtivo.valor = valor;

    } else if (tipo === 'cripto') {
        const moeda = document.getElementById('tipo-cripto').value;
        const quantidade = parseFloat(document.getElementById('quantidade-cripto').value);

        if (!moeda || !quantidade) {
            alert('Por favor, selecione a criptomoeda e a quantidade.');
            return;
        }

        novoAtivo.moeda = moeda;
        novoAtivo.quantidade = quantidade;
    }

    // Salvar no localStorage
    const ativos = JSON.parse(localStorage.getItem('carteira_ativos') || '[]');
    ativos.push(novoAtivo);
    localStorage.setItem('carteira_ativos', JSON.stringify(ativos));

    // Fechar modal
    fecharModal();

    // Recarregar lista
    carregarAtivos();

    alert('Ativo adicionado com sucesso!');
});

// Formatação automática do campo valor renda fixa
document.getElementById('valor-renda-fixa').addEventListener('input', function(e) {
    let value = e.target.value.replace(/\D/g, '');
    value = (value / 100).toFixed(2);
    value = value.replace('.', ',');
    value = value.replace(/\B(?=(\d{3})+(?!\d))/g, '.');
    e.target.value = 'R$ ' + value;
});

// Carregar cotações ao carregar a página
document.addEventListener('DOMContentLoaded', buscarCotacoes);

// Carregar ativos ao carregar a página
document.addEventListener('DOMContentLoaded', carregarAtivos);