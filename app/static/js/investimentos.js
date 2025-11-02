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
    document.getElementById('ticker-acao-custom').value = '';
    document.getElementById('ticker-acao-custom').style.display = 'none';
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
        document.getElementById('ticker-acao').value = '';
        document.getElementById('ticker-acao-custom').value = '';
        document.getElementById('ticker-acao-custom').style.display = 'none';
    } else if (tipo === 'renda-fixa') {
        document.getElementById('campos-renda-fixa').style.display = 'block';
    } else if (tipo === 'cripto') {
        document.getElementById('campos-cripto').style.display = 'block';
    }
});

// Controle de exibição do campo customizado de ticker
document.getElementById('ticker-acao').addEventListener('change', function() {
    const customField = document.getElementById('ticker-acao-custom');
    if (this.value === 'custom') {
        customField.style.display = 'block';
        customField.focus();
    } else {
        customField.style.display = 'none';
        customField.value = '';
    }
});

// Função para formatar valores monetários
function formatarMoeda(valor) {
    if (valor === null || valor === undefined || Number.isNaN(valor)) {
        return '—';
    }
    return new Intl.NumberFormat('pt-BR', {
        style: 'currency',
        currency: 'BRL'
    }).format(Number(valor));
}

// Função para formatar números cripto
function formatarCripto(valor) {
    return parseFloat(valor).toFixed(8);
}

let carteiraAtivos = [];
let resumoCarteira = null;

const listaAtivosEl = document.getElementById('lista-ativos');
const loaderAtivosEl = document.getElementById('ativos-loading');
const adicionarAtivoBtn = document.getElementById('adicionar-ativo');

function definirEstadoCarregamentoAtivos(carregando = true) {
    if (!loaderAtivosEl) {
        return;
    }

    if (carregando) {
        loaderAtivosEl.classList.add('is-visible');
    } else {
        loaderAtivosEl.classList.remove('is-visible');
    }
}

function limparListaAtivos() {
    if (!listaAtivosEl) {
        return;
    }
    listaAtivosEl.innerHTML = '<p style="color: #666; text-align: center; padding: 2rem;">Nenhum ativo adicionado ainda. Adicione seu primeiro ativo acima!</p>';
}

function renderizarAtivos() {
    if (!listaAtivosEl) {
        return;
    }

    if (!carteiraAtivos || carteiraAtivos.length === 0) {
        limparListaAtivos();
        return;
    }

    listaAtivosEl.innerHTML = carteiraAtivos.map((ativo) => {
        let detalhes = '';
        let tipoLabel = '';

        if (ativo.tipo === 'acao') {
            tipoLabel = 'Ação Nacional';
            detalhes = `${ativo.ticker} · ${ativo.quantidade} ações`;
        } else if (ativo.tipo === 'renda-fixa') {
            tipoLabel = 'Renda Fixa';
            detalhes = `${ativo.nome} · ${formatarMoeda(ativo.valor_investido)}`;
        } else if (ativo.tipo === 'cripto') {
            tipoLabel = 'Criptomoeda';
            detalhes = `${ativo.moeda} · ${formatarCripto(ativo.quantidade)} ${ativo.moeda}`;
        }

        const valorAtual = formatarMoeda(ativo.valor_atual);
        const complementos = [];
        if (ativo.tipo === 'acao' && ativo.preco_unitario !== undefined) {
            complementos.push(`Cotação atual: ${formatarMoeda(ativo.preco_unitario)}`);
        } else if (ativo.tipo === 'cripto' && ativo.preco_unitario !== undefined) {
            complementos.push(`Cotação atual: ${formatarMoeda(ativo.preco_unitario)}`);
        } else if (ativo.tipo === 'renda-fixa' && ativo.valor_investido !== undefined) {
            complementos.push(`Valor aplicado: ${formatarMoeda(ativo.valor_investido)}`);
        }

        if (ativo.valor_atual_estimado) {
            complementos.push('Valor estimado com base no aporte');
        }

        const complementoValor = complementos.length ? complementos.join(' · ') : '';

        return `
            <div class="ativo-card">
                <div class="ativo-info">
                    <div class="ativo-tipo">${tipoLabel}</div>
                    <div class="ativo-detalhes">${detalhes}</div>
                    <div class="ativo-valores">
                        <span class="ativo-valor-total">${valorAtual}</span>
                        ${complementoValor ? `<span class="ativo-valor-complemento">${complementoValor}</span>` : ''}
                    </div>
                </div>
                <button class="btn-remover" onclick="removerAtivo('${ativo._id}')">Remover</button>
            </div>
        `;
    }).join('');
}

async function carregarAtivos() {
    if (listaAtivosEl) {
        definirEstadoCarregamentoAtivos(true);
        listaAtivosEl.innerHTML = '<p style="color: rgba(220, 215, 201, 0.6); text-align: center; padding: 2rem;">Carregando sua carteira...</p>';
    }
    try {
        const resposta = await fetch('/api/ativos');
        if (!resposta.ok) {
            throw new Error('Não foi possível carregar seus ativos.');
        }

        const dados = await resposta.json();
        carteiraAtivos = dados.ativos || [];
        resumoCarteira = dados.resumo || null;
        atualizarResumoCarteira();
        renderizarAtivos();
    } catch (erro) {
        console.error('Erro ao carregar ativos:', erro);
        limparListaAtivos();
        if (listaAtivosEl) {
            listaAtivosEl.innerHTML = '<p style="color: #f44336; text-align: center; padding: 2rem;">Erro ao carregar sua carteira. Tente novamente mais tarde.</p>';
        }
        atualizarResumoCarteira(true);
    } finally {
        definirEstadoCarregamentoAtivos(false);
    }
}

async function removerAtivo(id) {
    if (!confirm('Tem certeza que deseja remover este ativo?')) {
        return;
    }

    definirEstadoCarregamentoAtivos(true);
    try {
        const resposta = await fetch(`/api/ativos/${id}`, { method: 'DELETE' });
        if (!resposta.ok) {
            throw new Error('Não foi possível remover o ativo.');
        }

        await carregarAtivos();
    } catch (erro) {
        console.error('Erro ao remover ativo:', erro);
        alert('Ocorreu um erro ao remover o ativo. Tente novamente.');
    } finally {
        definirEstadoCarregamentoAtivos(false);
    }
}

window.removerAtivo = removerAtivo;

// Adicionar ativo
if (adicionarAtivoBtn) {
adicionarAtivoBtn.addEventListener('click', async function() {
    const tipo = document.getElementById('tipo-ativo').value;

    if (!tipo) {
        alert('Por favor, selecione o tipo de ativo.');
        return;
    }

    let novoAtivo = { tipo };

    if (tipo === 'acao') {
        const ticker = document.getElementById('ticker-acao').value.toUpperCase();
        const tickerCustom = document.getElementById('ticker-acao-custom').value.toUpperCase();
        const quantidade = parseInt(document.getElementById('quantidade-acao').value);

        const tickerFinal = ticker === 'CUSTOM' ? tickerCustom : ticker;

        if (!tickerFinal || !quantidade) {
            alert('Por favor, preencha o ticker e a quantidade.');
            return;
        }

        novoAtivo.ticker = tickerFinal;
        novoAtivo.quantidade = quantidade;

    } else if (tipo === 'renda-fixa') {
        const nome = document.getElementById('nome-renda-fixa').value;
        const valorCampo = document.getElementById('valor-renda-fixa').value;
        const valorNormalizado = valorCampo
            .replace(/[R$\.\s]/g, '')
            .replace(',', '.');
        const valor = parseFloat(valorNormalizado);

        if (!nome || !valor) {
            alert('Por favor, preencha o nome e o valor.');
            return;
        }

        novoAtivo.nome = nome;
        novoAtivo.valor_investido = valor;

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

    const textoOriginal = adicionarAtivoBtn.textContent;
    adicionarAtivoBtn.textContent = 'Adicionando...';
    adicionarAtivoBtn.disabled = true;

    try {
        const resposta = await fetch('/api/ativos', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(novoAtivo)
        });

        if (!resposta.ok) {
            const erro = await resposta.json().catch(() => ({}));
            throw new Error(erro.error || 'Não foi possível adicionar o ativo.');
        }

        await carregarAtivos();
        fecharModal();
        alert('Ativo adicionado com sucesso!');
    } catch (erro) {
        console.error('Erro ao adicionar ativo:', erro);
        alert(erro.message || 'Não foi possível adicionar o ativo. Tente novamente.');
    } finally {
        adicionarAtivoBtn.disabled = false;
        adicionarAtivoBtn.textContent = textoOriginal;
    }
});
}

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

function atualizarResumoCarteira(erro = false) {
    const totalEl = document.getElementById('resumo-total');
    const quantidadeEl = document.getElementById('resumo-quantidade');
    const atualizacaoEl = document.getElementById('resumo-atualizacao');

    if (!totalEl || !quantidadeEl || !atualizacaoEl) {
        return;
    }

    if (erro || !resumoCarteira) {
        totalEl.textContent = '—';
        quantidadeEl.textContent = '0';
        atualizacaoEl.textContent = '--';
        return;
    }

    totalEl.textContent = formatarMoeda(resumoCarteira.total_atual);
    quantidadeEl.textContent = resumoCarteira.quantidade_ativos || 0;

    if (resumoCarteira.ultima_atualizacao) {
        const data = new Date(resumoCarteira.ultima_atualizacao);
        if (!Number.isNaN(data.getTime())) {
            atualizacaoEl.textContent = new Intl.DateTimeFormat('pt-BR', {
                dateStyle: 'short',
                timeStyle: 'short'
            }).format(data);
        } else {
            atualizacaoEl.textContent = '--';
        }
    } else {
        atualizacaoEl.textContent = '--';
    }
}