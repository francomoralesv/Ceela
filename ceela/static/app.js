// Energy Calculator Frontend - Temporal.io
class EnergyCalculatorApp {
    constructor() {
        this.baseUrl = 'http://localhost:8000/api/v1';
        this.wsUrl = 'ws://localhost:8000/api/v1';
        this.currentCalculationId = null;
        this.ws = null;
        this.wsReconnectAttempts = 0;
        this.maxReconnectAttempts = 5;
        
        this.initializeEventListeners();
        this.log('Aplicación iniciada', 'info');
        
        // Test WebSocket connection on startup
        this.testWebSocketConnection();
    }

    initializeEventListeners() {
        // Form submission
        document.getElementById('calculationForm').addEventListener('submit', (e) => {
            e.preventDefault();
            this.startCalculation();
        });

        // Cancel button
        document.getElementById('cancelBtn').addEventListener('click', () => {
            this.cancelCalculation();
        });

        // Window beforeunload
        window.addEventListener('beforeunload', () => {
            if (this.ws) {
                this.ws.close();
            }
        });
    }

    async startCalculation() {
        const form = document.getElementById('calculationForm');
        const formData = new FormData(form);
        
        // Debug: Show all form data
        this.log('📋 Datos del formulario:', 'info');
        for (let [key, value] of formData.entries()) {
            this.log(`  ${key}: ${value}`, 'info');
        }
        
        const projectId = parseInt(formData.get('projectId'));
        const userId = formData.get('userId') ? parseInt(formData.get('userId')) : null;
        const version = formData.get('version');
        const forceData = formData.has('forceData');
        
        this.log(`🔍 projectId parsed: ${projectId} (type: ${typeof projectId})`, 'info');
        
        // Validate projectId
        if (!projectId || isNaN(projectId)) {
            this.log('❌ Project ID es requerido y debe ser un número', 'error');
            return;
        }

        const payload = {
            force_data: forceData,
            version: version,
            user_id: userId
        };

        this.log(`Iniciando cálculo para proyecto ${projectId}...`, 'info');
        this.log(`Payload: ${JSON.stringify(payload)}`, 'info');
        this.setButtonsState(true);

        try {
            const response = await fetch(`${this.baseUrl}/calculate/temporal/${projectId}`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(payload)
            });

            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }

            const result = await response.json();
            this.currentCalculationId = result.calculation_id;
            
            this.log(`✅ Cálculo iniciado: ${result.calculation_id}`, 'success');
            this.showStatusCard(result);
            this.connectWebSocket(result.calculation_id);

        } catch (error) {
            this.log(`❌ Error al iniciar cálculo: ${error.message}`, 'error');
            this.setButtonsState(false);
        }
    }

    async cancelCalculation() {
        if (!this.currentCalculationId) return;

        this.log(`Cancelando cálculo ${this.currentCalculationId}...`, 'warning');

        try {
            const response = await fetch(`${this.baseUrl}/calculate/cancel/${this.currentCalculationId}`, {
                method: 'POST'
            });

            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }

            const result = await response.json();
            this.log(`✅ Cálculo cancelado: ${result.message}`, 'warning');

        } catch (error) {
            this.log(`❌ Error al cancelar: ${error.message}`, 'error');
        }
    }

    connectWebSocket(calculationId) {
        if (this.ws) {
            this.ws.close();
        }

        const wsUrl = `${this.wsUrl}/ws/calculation/${calculationId}`;
        this.log(`Conectando WebSocket: ${wsUrl}`, 'info');

        this.ws = new WebSocket(wsUrl);

        this.ws.onopen = () => {
            this.wsReconnectAttempts = 0;
            this.updateConnectionStatus(true);
            this.log('✅ WebSocket conectado', 'success');
        };

        this.ws.onmessage = (event) => {
            try {
                const data = JSON.parse(event.data);
                this.handleWebSocketMessage(data);
            } catch (error) {
                this.log(`❌ Error procesando mensaje WebSocket: ${error.message}`, 'error');
            }
        };

        this.ws.onclose = (event) => {
            this.updateConnectionStatus(false);
            if (event.wasClean) {
                this.log('WebSocket cerrado correctamente', 'info');
            } else {
                this.log(`WebSocket cerrado inesperadamente: ${event.code}`, 'warning');
                this.attemptReconnect(calculationId);
            }
        };

        this.ws.onerror = (error) => {
            this.log('❌ Error en WebSocket', 'error');
        };
    }

    attemptReconnect(calculationId) {
        if (this.wsReconnectAttempts < this.maxReconnectAttempts) {
            this.wsReconnectAttempts++;
            const delay = Math.pow(2, this.wsReconnectAttempts) * 1000; // Exponential backoff
            
            this.log(`Reintentando conexión WebSocket en ${delay/1000}s (intento ${this.wsReconnectAttempts})`, 'warning');
            
            setTimeout(() => {
                this.connectWebSocket(calculationId);
            }, delay);
        } else {
            this.log('❌ Máximo de reintentos alcanzado. WebSocket desconectado.', 'error');
        }
    }

    handleWebSocketMessage(data) {
        this.log(`📨 Mensaje WebSocket: ${data.status} - ${data.message || ''}`, 'info');
        
        if (data.calculation_id) {
            this.updateStatus(data);
        }

        // Handle completion
        if (data.status === 'completed') {
            this.setButtonsState(false);
            this.loadResults(data.calculation_id);
        } else if (data.status === 'error' || data.status === 'cancelled') {
            this.setButtonsState(false);
        }
    }

    showStatusCard(data) {
        const card = document.getElementById('statusCard');
        card.style.display = 'block';
        
        document.getElementById('calculationId').textContent = data.calculation_id;
        document.getElementById('workflowId').textContent = data.workflow_id || '-';
        document.getElementById('runId').textContent = data.run_id || '-';
        
        this.updateStatus({
            status: data.status,
            progress: 0,
            message: data.message
        });
    }

    updateStatus(data) {
        const card = document.getElementById('statusCard');
        const statusText = document.getElementById('statusText');
        const progressBar = document.getElementById('progressBar');
        const statusMessage = document.getElementById('statusMessage');
        const timestamp = document.getElementById('timestamp');

        // Update status text and card style
        statusText.textContent = this.getStatusText(data.status);
        card.className = `card mb-3 status-card status-${data.status}`;
        
        // Update progress
        const progress = data.progress || 0;
        progressBar.style.width = `${progress}%`;
        progressBar.className = `progress-bar ${this.getProgressBarClass(data.status)}`;
        
        if (data.status === 'running') {
            progressBar.classList.add('progress-animated');
        }

        // Update message and timestamp
        statusMessage.textContent = data.message || '';
        timestamp.textContent = new Date().toLocaleTimeString();
    }

    async loadResults(calculationId) {
        this.log(`Cargando resultados para ${calculationId}...`, 'info');
        
        try {
            const response = await fetch(`${this.baseUrl}/calculate/results/${calculationId}`);
            
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }

            const data = await response.json();
            console.log("Results data:", JSON.parse(data.results));
            this.showResults(JSON.parse(data.results));
            
        } catch (error) {
            this.log(`❌ Error cargando resultados: ${error.message}`, 'error');
        }
    }

    showResults(results) {
        const card = document.getElementById('resultsCard');
        const content = document.getElementById('resultsContent');
        
        if (!results) {
            return;
        }

        let html = '';
        
        // Final Indicators
        if (results.final_indicators) {
            html += '<h6>Indicadores Finales</h6>';
            html += '<div class="row mb-3">';
            
            Object.entries(results.final_indicators).forEach(([key, value]) => {
                html += `
                    <div class="col-md-6 mb-2">
                        <div class="card bg-light">
                            <div class="card-body p-2">
                                <small class="text-muted">${key.replace(/_/g, ' ').toUpperCase()}</small>
                                <div class="fw-bold">${typeof value === 'number' ? value.toFixed(2) : value}</div>
                            </div>
                        </div>
                    </div>
                `;
            });
            
            html += '</div>';
        }

        // CO2 Equivalente
        if (results.co2_eq_energia_primaria) {
            html += `
                <div class="alert alert-info">
                    <i class="bi bi-cloud"></i>
                    <strong>CO2 Equiv. Energía Primaria:</strong> ${results.co2_eq_energia_primaria.toFixed(2)}
                </div>
            `;
        }

        // Metadata
        if (results.calculation_metadata) {
            const meta = results.calculation_metadata;
            html += `
                <div class="mt-3 p-2 bg-light rounded">
                    <small class="text-muted">
                        <strong>Versión:</strong> ${meta.version} | 
                        <strong>Recintos:</strong> ${meta.enclosures_processed} | 
                        <strong>Timestamp:</strong> ${new Date(meta.timestamp).toLocaleString()}
                    </small>
                </div>
            `;
        }

        content.innerHTML = html;
        card.style.display = 'block';
        this.log('✅ Resultados mostrados', 'success');
    }

    async loadHistory() {
        const projectId = document.getElementById('projectId').value;
        if (!projectId) return;

        this.log(`Cargando historial para proyecto ${projectId}...`, 'info');

        try {
            const response = await fetch(`${this.baseUrl}/calculate/projects/${projectId}/history?limit=10`);
            
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }

            const data = await response.json();
            this.showHistory(data.calculations);
            
        } catch (error) {
            this.log(`❌ Error cargando historial: ${error.message}`, 'error');
        }
    }

    showHistory(calculations) {
        const card = document.getElementById('historyCard');
        const content = document.getElementById('historyContent');
        
        if (!calculations || calculations.length === 0) {
            content.innerHTML = '<p class="text-muted">No hay cálculos en el historial.</p>';
            card.style.display = 'block';
            return;
        }

        let html = '<div class="list-group list-group-flush">';
        
        calculations.forEach(calc => {
            const statusClass = this.getStatusBadgeClass(calc.status);
            const createdAt = new Date(calc.created_at).toLocaleString();
            
            html += `
                <div class="list-group-item">
                    <div class="d-flex justify-content-between align-items-start">
                        <div class="ms-2 me-auto">
                            <div class="fw-bold">${calc.calculation_id}</div>
                            <small class="text-muted">${createdAt}</small>
                            <div class="mt-1">
                                <small class="text-muted">${calc.message || 'Sin mensaje'}</small>
                            </div>
                        </div>
                        <div class="text-end">
                            <span class="badge ${statusClass}">${calc.status}</span>
                            <div class="mt-1">
                                <small class="text-muted">${calc.progress || 0}%</small>
                            </div>
                        </div>
                    </div>
                </div>
            `;
        });
        
        html += '</div>';
        content.innerHTML = html;
        card.style.display = 'block';
        this.log(`✅ Historial mostrado: ${calculations.length} cálculos`, 'success');
    }

    async checkHealth() {
        this.log('Verificando estado del sistema...', 'info');

        try {
            const response = await fetch(`${this.baseUrl.replace('/api/v1', '')}/health`);
            
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }

            const data = await response.json();
            
            let message = '✅ Sistema saludable\n';
            message += `Database: ${data.database}\n`;
            message += `Redis: ${data.redis}\n`;
            message += `Temporal: ${data.temporal}`;
            
            this.log(message, 'success');
            
        } catch (error) {
            this.log(`❌ Health check falló: ${error.message}`, 'error');
        }
    }

    // Utility methods
    getStatusText(status) {
        const statusTexts = {
            'queued': 'En Cola',
            'running': 'Ejecutando',
            'completed': 'Completado',
            'error': 'Error',
            'cancelled': 'Cancelado',
            'not_found': 'No Encontrado'
        };
        return statusTexts[status] || status;
    }

    getProgressBarClass(status) {
        const classes = {
            'queued': 'bg-warning',
            'running': 'bg-info',
            'completed': 'bg-success',
            'error': 'bg-danger',
            'cancelled': 'bg-secondary'
        };
        return classes[status] || 'bg-primary';
    }

    getStatusBadgeClass(status) {
        const classes = {
            'queued': 'bg-warning',
            'running': 'bg-info',
            'completed': 'bg-success',
            'error': 'bg-danger',
            'cancelled': 'bg-secondary'
        };
        return classes[status] || 'bg-primary';
    }

    setButtonsState(calculating) {
        const startBtn = document.getElementById('startBtn');
        const cancelBtn = document.getElementById('cancelBtn');

        if (calculating) {
            startBtn.disabled = true;
            startBtn.innerHTML = '<i class="bi bi-hourglass-split"></i> Calculando...';
            cancelBtn.classList.remove('d-none');
        } else {
            startBtn.disabled = false;
            startBtn.innerHTML = '<i class="bi bi-play-fill"></i> Iniciar Cálculo';
            cancelBtn.classList.add('d-none');
            this.currentCalculationId = null;
        }
    }

    updateConnectionStatus(connected) {
        const indicator = document.getElementById('wsStatus');
        const text = document.getElementById('wsStatusText');
        
        if (connected) {
            indicator.className = 'connection-indicator connected';
            text.textContent = 'Conectado';
        } else {
            indicator.className = 'connection-indicator disconnected';
            text.textContent = 'Desconectado';
        }
    }

    log(message, type = 'info') {
        const container = document.getElementById('logContainer');
        const timestamp = new Date().toLocaleTimeString();
        
        const icons = {
            'info': 'bi-info-circle text-info',
            'success': 'bi-check-circle text-success',
            'warning': 'bi-exclamation-triangle text-warning',
            'error': 'bi-x-circle text-danger'
        };
        
        const icon = icons[type] || icons.info;
        
        const logEntry = document.createElement('div');
        logEntry.className = 'mb-1';
        logEntry.innerHTML = `
            <span class="text-muted">[${timestamp}]</span>
            <i class="bi ${icon}"></i>
            ${message}
        `;
        
        container.appendChild(logEntry);
        container.scrollTop = container.scrollHeight;
        
        // Keep only last 100 log entries
        while (container.children.length > 100) {
            container.removeChild(container.firstChild);
        }
    }

    clearLogs() {
        document.getElementById('logContainer').innerHTML = '<div class="text-muted">Logs limpiados...</div>';
    }

    testWebSocketConnection() {
        this.log('Probando conexión WebSocket...', 'info');
        this.connectWebSocket('test');
    }
}

// Initialize app when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    try {
        window.app = new EnergyCalculatorApp();
        
        // Verificar si hay un calculation_id en la URL y cargar resultados
        const urlParams = new URLSearchParams(window.location.search);
        const calculationId = urlParams.get('calculation_id');
        
        if (calculationId) {
            // Mostrar la pestaña de resultados
            const resultsTab = document.getElementById('results-tab');
            if (resultsTab) {
                resultsTab.click();
            }
            
            // Cargar los resultados
            window.app.loadResults(calculationId);
        }
    } catch (error) {
        console.error('Error al inicializar la aplicación:', error);
        const errorContainer = document.createElement('div');
        errorContainer.className = 'alert alert-danger m-3';
        errorContainer.innerHTML = `
            <h4 class="alert-heading">Error al iniciar la aplicación</h4>
            <p>${error.message || 'Error desconocido'}</p>
            <p>Por favor, recarga la página e intenta nuevamente.</p>
        `;
        document.body.prepend(errorContainer);
    }
});

// Global functions for quick access
function checkHealth() {
    window.app.checkHealth();
}

function loadHistory() {
    window.app.loadHistory();
}

function clearLogs() {
    window.app.clearLogs();
}