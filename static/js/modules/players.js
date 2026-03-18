import { Core } from './core.js';

export class PlayersModule {
    constructor(ui) {
        this.ui = ui;
    }

    async populateTeamSelects() {
        try {
            const equipos = await Core.fetchAPI('/api/equipos');
            const options = '<option value="">Seleccionar Equipo...</option>' +
                equipos.map(e => `<option value="${e.id}">${e.nombre}</option>`).join('');

            const filterSelect = document.getElementById('player-team-filter');
            const modalSelect = document.getElementById('player-equipo-id');

            let currentFilterValue = filterSelect ? filterSelect.value : '';
            if (filterSelect) filterSelect.innerHTML = options;
            if (modalSelect) modalSelect.innerHTML = options;

            if (filterSelect && currentFilterValue) {
                filterSelect.value = currentFilterValue;
                this.loadJugadores();
            } else if (filterSelect && equipos.length > 0) {
                filterSelect.value = equipos[0].id;
                this.loadJugadores();
            }
        } catch (error) {
            console.error('Error cargando select de equipos:', error);
        }
    }

    showJugadorModal() {
        Core.openModal('modal-jugador');
        document.getElementById('player-form').reset();
        document.getElementById('player-id').value = '';
        document.getElementById('player-es-capitan').checked = false;
        document.querySelector('#modal-jugador h3').innerText = 'Nuevo Jugador';
        document.querySelector('#player-form .btn-primary').innerText = 'Registrar Jugador';

    }


    async loadJugadores() {
        const equipoId = document.getElementById('player-team-filter').value;
        const container = document.getElementById('jugadores-container');
        if (!container) return;
        if (!equipoId) {
            container.innerHTML = '<p class="text-muted">Selecciona un equipo para ver sus jugadores.</p>';
            return;
        }
        container.innerHTML = '<p>Cargando jugadores...</p>';
        const userRol = (window.USER_ROL || '').toLowerCase();
        const isReader = ['resultados', 'arbitro', 'solo vista'].includes(userRol);

        try {
            const jugadores = await Core.fetchAPI(`/api/jugadores?equipo_id=${equipoId}`);
            container.innerHTML = jugadores.length ? jugadores.map(j => `
                <div class="stat-card" style="padding: 1.5rem; display: flex; align-items: center; justify-content: space-between; gap: 1rem; position: relative; min-height: 140px; margin-bottom: 1rem; overflow: hidden; border-left: 4px solid ${j.color || 'var(--primary)'};">
                    <div style="flex: 1; text-align: left;">
                        <div style="display: flex; align-items: center; gap: 10px;">
                            <span style="font-size: 1.2rem; font-weight: 800; color: ${j.color || 'var(--primary)'}; opacity: 0.8; text-shadow: 0 0 10px ${j.color ? j.color + '4d' : 'transparent'};">#${j.numero || '--'}</span>
                            ${j.tiene_usuario ? `
                                <span class="badge-premium" style="font-size: 0.6rem; background: rgba(255, 255, 255, 0.1); color: #fff; border: 1px solid rgba(255, 255, 255, 0.2); padding: 2px 6px;">
                                    🔗 Cuenta
                                </span>
                            ` : ''}
                        </div>
                        <h4 style="margin: 4px 0; font-size: 1.3rem; color: #fff;">${j.nombre}</h4>
                        <span style="font-size: 0.85rem; color: var(--text-muted); display: block; margin-bottom: 1.2rem; font-weight: 500;">
                            ${j.posicion || 'Sin Posición'} 
                            ${j.es_portero ? `<span style="color:${j.color || 'var(--primary)'}; font-weight:700">🧤 Portero</span>` : ''} 
                            ${j.es_capitan ? '<span style="color:#fbbf24; font-weight:700">©️ Capitán</span>' : ''} 
                            ${j.edad ? `• ${j.edad} años` : ''}
                        </span>
                        ${!isReader ? `
                        <div style="display:flex; gap:8px;">
                            <button onclick="ui.players.editJugador(${j.id})" title="Editar" style="background: rgba(99,102,241,0.15); color:#818cf8; border: 0.5px solid rgba(99,102,241,0.3); cursor:pointer; border-radius: 6px; padding: 5px 10px; font-size: 0.8rem;">✏️ Editar</button>
                            <button onclick="ui.players.deleteJugador(${j.id})" title="Eliminar" style="background: rgba(239,68,68,0.15); color:#ef4444; border: 0.5px solid rgba(239,68,68,0.3); cursor:pointer; border-radius: 6px; padding: 5px 10px; font-size: 0.8rem;">🗑️ Borrar</button>
                        </div>
                        ` : ''}
                    </div>
                    <div style="flex-shrink: 0;">
                        ${j.foto_url ?
                    `<div style="background-image: url('${j.foto_url}'); height: 110px; width: 110px; background-size: cover; background-position: center; border-radius: 50%; border: 3px solid var(--glass); box-shadow: 0 4px 15px rgba(0,0,0,0.5);"></div>` :
                    `<div style="height: 110px; width: 110px; background: rgba(255,255,255,0.03); display: flex; align-items: center; justify-content: center; font-size: 2.5rem; font-weight: 800; border-radius: 50%; border: 2px solid ${j.color || 'var(--border)'}; color: ${j.color || 'var(--primary)'}; text-shadow: 0 0 15px ${j.color ? j.color + '66' : 'var(--primary-glow)'}; flex-direction: column;">
                        <span style="font-size: 0.8rem; opacity: 0.5; margin-bottom: -5px;">Nº</span>
                        ${j.numero || '--'}
                    </div>`
                }
                    </div>
                </div>
            `).join('') : '<p>No hay jugadores registrados en este equipo.</p>';
        } catch (error) {
            container.innerHTML = '<p class="error">Error al cargar jugadores.</p>';
        }
    }

    async editJugador(id) {
        try {
            const jugadores = await Core.fetchAPI('/api/jugadores');
            const j = jugadores.find(jug => jug.id === id);
            if (j) {
                document.getElementById('player-id').value = j.id;
                document.getElementById('player-name').value = j.nombre;
                document.getElementById('player-seudonimo').value = j.seudonimo || '';
                document.getElementById('player-phone').value = j.telefono || '';
                document.getElementById('player-pos').value = j.posicion || '';
                document.getElementById('player-number').value = j.numero || '';
                document.getElementById('player-age').value = j.edad || '';
                document.getElementById('player-image').value = j.foto_url || '';
                document.getElementById('player-equipo-id').value = j.equipo_id;
                document.getElementById('player-es-capitan').checked = j.es_capitan || false;
                document.querySelector('#modal-jugador h3').innerText = 'Editar Jugador';
                document.querySelector('#player-form .btn-primary').innerText = 'Guardar Cambios';

                Core.openModal('modal-jugador');
            }
        } catch (error) {

            console.error('Error al cargar jugador:', error);
        }
    }

    async deleteJugador(id) {
        if (!confirm('¿Eliminar este jugador del sistema?')) return;
        try {
            const res = await fetch(`/api/jugadores/${id}`, { method: 'DELETE' });
            if (res.ok) {
                this.loadJugadores();
                this.ui.loadInitialStats();
            } else alert('Error al eliminar el jugador.');
        } catch (e) { console.error(e); }
    }

    async handleJugadorSubmit(e) {
        e.preventDefault();
        const id = document.getElementById('player-id').value;
        const method = id ? 'PUT' : 'POST';
        const url = id ? `/api/jugadores/${id}` : '/api/jugadores';
        const data = {
            nombre: document.getElementById('player-name').value,
            seudonimo: document.getElementById('player-seudonimo').value,
            telefono: document.getElementById('player-phone').value,
            posicion: document.getElementById('player-pos').value,
            numero: document.getElementById('player-number').value,
            edad: document.getElementById('player-age').value,
            foto_url: document.getElementById('player-image').value,
            es_portero: document.getElementById('player-pos').value === 'Portero',
            es_capitan: document.getElementById('player-es-capitan').checked,
            equipo_id: document.getElementById('player-equipo-id').value
        };

        try {
            const response = await fetch(url, {
                method: method,
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(data)
            });
            if (response.ok) {
                Core.closeModal('modal-jugador');
                this.loadJugadores();
                this.ui.loadInitialStats();
            } else alert('Error al guardar el jugador.');
        } catch (error) { console.error('Error:', error); }
    }
}
