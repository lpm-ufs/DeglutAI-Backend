// app.js
const WebSocket = require('ws'); // Importa a biblioteca ws

// Cria uma conexão WebSocket com o servidor
const websocket = new WebSocket('ws://localhost:8080');

websocket.on('open', () => {
    console.log('Conectado ao servidor WebSocket');

    // Envia uma mensagem para iniciar a calibração
    websocket.send(JSON.stringify({ action: 'start-calibration' }));
});

websocket.on('message', (data) => {
    const response = JSON.parse(data);
    console.log('Resposta do servidor:', response);

    if (response.status === 200) {
        console.log('Sucesso:', response.message);
    } else {
        console.error('Erro:', response.message);
    }
});

websocket.on('error', (error) => {
    console.error('Erro na conexão WebSocket:', error);
});

websocket.on('close', () => {
    console.log('Conexão WebSocket fechada');
});