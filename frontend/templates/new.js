document.getElementById('prediction-form').addEventListener('submit', async (event) => {
    event.preventDefault();

    const formData = new FormData(event.target);
    const data = Object.fromEntries(formData);

    const response = await fetch('http://127.0.0.1:8000/predict', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(data),
    });

    const result = await response.json();
    document.getElementById('result').innerText = `Predicted Price: $${result.predicted_value}`;
    loadPredictions();
});

async function loadPredictions() {
    const response = await fetch('http://127.0.0.1:8000/predictions');

    const predictions = await response.json();

    const tbody = document.querySelector('#predictions-table tbody');
    tbody.innerHTML = '';

    predictions.forEach(prediction => {
        const row = document.createElement('tr');
        row.innerHTML = `
            <td>${prediction.id}</td>
            <td>${prediction.longitude}</td>
            <td>${prediction.latitude}</td>
            <td>${prediction.predicted_price.toFixed(2)}</td>
            <td>${new Date(prediction.timestamp).toLocaleString()}</td>
        `;
        tbody.appendChild(row);
    });
}

document.addEventListener('DOMContentLoaded', loadPredictions);
