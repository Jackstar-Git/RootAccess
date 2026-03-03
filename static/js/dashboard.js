// Line Chart (Main)
const lineCtx = document.getElementById('viewsLineChart').getContext('2d');
new Chart(lineCtx, {
    type: 'line',
    data: {
        labels: ['M', 'T', 'W', 'T', 'F', 'S', 'S'],
        datasets: [{
            data: [30, 25, 38, 22, 35, 18, 40],
            borderColor: '#5c67f2',
            backgroundColor: 'rgba(92, 103, 242, 0.05)',
            fill: true,
            tension: 0.4,
            pointRadius: 0
        }]
    },
    options: {
        plugins: { legend: { display: false } },
        scales: { x: { grid: { display: false } }, y: { display: false } }
    }
});

// Bar Chart (Side)
const barCtx = document.getElementById('topPostsBarChart').getContext('2d');
new Chart(barCtx, {
    type: 'bar',
    data: {
        labels: ['Post A', 'Post B', 'Post C', 'Post D'],
        datasets: [{
            data: [124, 86, 51, 46],
            backgroundColor: '#5c67f2',
            borderRadius: 5,
            barThickness: 15
        }]
    },
    options: {
        indexAxis: 'y',
        plugins: { legend: { display: false } },
        scales: { x: { display: false }, y: { grid: { display: false } } }
    }
});