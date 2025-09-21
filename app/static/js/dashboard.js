document.addEventListener('DOMContentLoaded', function() {
    const chartData = window.dashboardData;
    if (!chartData) return;

    const ctxBar = document.getElementById('barChart').getContext('2d');
    new Chart(ctxBar, {
        type: 'bar',
        data: {
            labels: chartData.months,
            datasets: [
                {
                    label: 'Receitas',
                    data: chartData.receitas,
                    backgroundColor: '#4caf50',
                },
                {
                    label: 'Despesas',
                    data: chartData.despesas,
                    backgroundColor: '#e53935',
                }
            ]
        },
        options: {
            responsive: true,
            plugins: {
                legend: { position: 'top', labels: { color: getComputedStyle(document.body).getPropertyValue('--cor-texto') } },
                title: { display: true, text: 'Receitas e Despesas por Mês', color: getComputedStyle(document.body).getPropertyValue('--cor-texto') }
            },
            scales: {
                x: { ticks: { color: getComputedStyle(document.body).getPropertyValue('--cor-texto') } },
                y: { ticks: { color: getComputedStyle(document.body).getPropertyValue('--cor-texto') } }
            }
        }
    });

    const ctxPie = document.getElementById('pieChart').getContext('2d');
    new Chart(ctxPie, {
        type: 'pie',
        data: {
            labels: chartData.categorias,
            datasets: [{
                data: chartData.percentual_categoria,
                backgroundColor: chartData.cores_categoria,
            }]
        },
        options: {
            plugins: {
                legend: { labels: { color: getComputedStyle(document.body).getPropertyValue('--cor-texto') } },
                title: { display: true, text: 'Percentual por Categoria', color: getComputedStyle(document.body).getPropertyValue('--cor-texto') }
            }
        }
    });

    // Total
    const total = chartData.total;
    const totalEl = document.getElementById('total-indicador');
    if (totalEl) {
        totalEl.innerHTML = `${total >= 0 ? '<span style=\'color:#4caf50\'>&#9650;</span>' : '<span style=\'color:#e53935\'>&#9660;</span>'} R$ ${total.toFixed(2)}`;
    }
});

// Controle do formulário de lançamento
const btn = document.getElementById('abrir-form');
const form = document.getElementById('form-lancamento');

if (btn && form) {
    btn.addEventListener('click', () => {
        form.style.display = form.style.display === 'none' ? 'block' : 'none';
        if(form.style.display === 'block') {
            form.descricao.focus();
        }
    });

    form.addEventListener('submit', (e) => {
        let valor = valorInput.value.replace('R$ ', '').replace('.', '').replace(',', '.');
        valorInput.value = valor;
        setTimeout(() => { form.reset(); form.descricao.focus(); }, 100);
    });
}

// Formatação automática do campo valor
const valorInput = document.getElementById('valor');
if (valorInput) {
    valorInput.addEventListener('input', function(e) {
        let value = e.target.value.replace(/\D/g, '');
        value = (value / 100).toFixed(2);
        value = value.replace('.', ',');
        value = value.replace(/\B(?=(\d{3})+(?!\d))/g, '.');
        e.target.value = 'R$ ' + value;
    });
}

// Função para deletar entrada
function deleteEntry(id) {
    if (confirm('Tem certeza que deseja excluir este lançamento?')) {
        fetch('/delete_entry/' + id, { method: 'DELETE' })
            .then(response => {
                if (response.ok) {
                    location.reload();
                } else {
                    alert('Erro ao excluir.');
                }
            });
    }
}

// Navegação de mês
const prevBtn = document.getElementById('prev-month');
const nextBtn = document.getElementById('next-month');

function getCurrentMonth() {
    const urlParams = new URLSearchParams(window.location.search);
    const monthParam = urlParams.get('month');

    if (monthParam) {
        return monthParam;
    }

    // Se não há parâmetro month, usar o mês atual
    const now = new Date();
    const year = now.getFullYear();
    const month = now.getMonth() + 1; // getMonth() retorna 0-11
    return `${year}-${String(month).padStart(2, '0')}`;
}

function navigateMonth(direction) {
    const current = getCurrentMonth();
    const [year, month] = current.split('-').map(Number);
    let newMonth = month + direction;
    let newYear = year;
    if (newMonth > 12) {
        newMonth = 1;
        newYear++;
    } else if (newMonth < 1) {
        newMonth = 12;
        newYear--;
    }
    const newMonthStr = `${newYear}-${String(newMonth).padStart(2, '0')}`;
    window.location.href = `?month=${newMonthStr}`;
}

if (prevBtn && nextBtn) {
    prevBtn.addEventListener('click', () => navigateMonth(-1));
    nextBtn.addEventListener('click', () => navigateMonth(1));
}
