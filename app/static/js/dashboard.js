// Dashboard charts and table logic
// Requires Chart.js

document.addEventListener('DOMContentLoaded', function() {
    // Dados vindos do template Flask
    const chartData = window.dashboardData;
    if (!chartData) return;

    // Gráfico de barras receitas/despesas por mês
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

    // Gráfico de pizza por categoria
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
