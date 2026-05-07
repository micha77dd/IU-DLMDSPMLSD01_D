document.addEventListener('DOMContentLoaded', function () {
    let ws = null;

    function connectWs() {
        ws = new WebSocket(`ws://${window.location.host}/ws/retrain`);
        ws.onmessage = function (event) {
            const data = JSON.parse(event.data);
            if (data.action === 'complete') {
                const timeEl = document.getElementById('last-training-time');
                if (timeEl) {
                    timeEl.innerText = `Letztes Training: ${data.last_training_time}`;
                }
                return;
            }
            if (data.model === 'Random Forest') {
                const el = document.getElementById('ws-status-rf');
                if (el) {
                    el.innerText = `Random Forest: ${data.status}`;
                    el.style.color = data.status === 'abgeschlossen' ? 'green' : 'black';
                }
            } else if (data.model === 'SVM') {
                const el = document.getElementById('ws-status-svm');
                if (el) {
                    el.innerText = `SVM: ${data.status}`;
                    el.style.color = data.status === 'abgeschlossen' ? 'green' : 'black';
                }
            } else if (data.model === 'Logistic Regression') {
                const el = document.getElementById('ws-status-lr');
                if (el) {
                    el.innerText = `Logistic Regression: ${data.status}`;
                    el.style.color = data.status === 'abgeschlossen' ? 'green' : 'black';
                }
            }
        };
        ws.onclose = function () {
            setTimeout(connectWs, 2000);
        };
    }

    setTimeout(connectWs, 1000);

    document.addEventListener('click', function (e) {
        if (e.target && e.target.id === 'retrain-button') {
            if (ws && ws.readyState === WebSocket.OPEN) {
                const token = prompt('Bitte Admin-Token eingeben:'); if(token) { ws.send(JSON.stringify({action: 'retrain', token: token})); }
            }
        }
    });
});
