import { Core } from './core.js';

export class TeamsModule {
    constructor(ui) {
        this.ui = ui;
        setTimeout(() => this.initAutocomplete(), 1000);
    }

    async populateLeagueSelects() {
        try {
            const response = await Core.fetchAPI('/api/torneos');
            const torneos = response.items || response;

            const select = document.getElementById('inhouse-torneo-id');
            if (select) {
                select.innerHTML = '<option value="">Seleccionar Torneo...</option>' +
                    (Array.isArray(torneos) ? torneos.map(t => `<option value="${t.id}">${t.nombre}</option>`).join('') : '');
            }

            const active = Array.isArray(torneos) ? torneos.filter(t => t.activo) : [];
            const options = '<option value="">Seleccionar Liga...</option>' +
                active.map(t => `<option value="${t.id}">${t.nombre}</option>`).join('');

            const filterSelect = document.getElementById('team-league-filter');
            const modalSelect = document.getElementById('team-torneo-id');

            let currentFilterValue = filterSelect ? filterSelect.value : '';
            if (filterSelect) filterSelect.innerHTML = options;
            if (modalSelect) modalSelect.innerHTML = options;

            if (filterSelect && currentFilterValue) {
                filterSelect.value = currentFilterValue;
                this.loadEquipos();
            } else if (filterSelect && active.length > 0) {
                filterSelect.value = active[0].id;
                this.loadEquipos();
            }
        } catch (error) {
            console.error('Error cargando select de ligas:', error);
        }
    }

    showEquipoModal() {
        const currentFilterSelect = document.getElementById('team-league-filter');
        const currentLeagueId = currentFilterSelect ? currentFilterSelect.value : '';

        Core.openModal('modal-equipo');
        document.getElementById('team-form').reset();
        document.getElementById('team-id').value = '';

        if (currentLeagueId) {
            document.getElementById('team-torneo-id').value = currentLeagueId;
        }

        const finFields = document.getElementById('team-financial-fields');
        if (finFields) finFields.style.display = 'flex';
        if (document.getElementById('team-abono')) document.getElementById('team-abono').value = 0;

        const userRol = (window.futUserRol || '').toLowerCase();
        const isAdmin = ['admin', 'ejecutivo', 'dueño_liga'].includes(userRol);
        
        const uidContainer = document.getElementById('team-uid-container');
        if (uidContainer) {
            uidContainer.style.display = isAdmin ? 'block' : 'none';
        }
        
        if (document.getElementById('team-uid')) document.getElementById('team-uid').value = '';

        document.querySelector('#modal-equipo h3').innerText = 'Nuevo Equipo';
        document.querySelector('#team-form .btn-primary').innerText = 'Registrar Equipo';
    }

    async editEquipo(id) {
        try {
            const e = await Core.fetchAPI(`/api/equipos/${id}`);
            if (e) {
                document.getElementById('team-id').value = e.id;
                document.getElementById('team-name').value = e.nombre;
                document.getElementById('team-torneo-id').value = e.torneo_id;
                document.getElementById('team-image').value = e.escudo_url || '';
                document.getElementById('team-grupo').value = e.grupo || '';
                if (document.getElementById('team-colonia')) document.getElementById('team-colonia').value = e.colonia || '';
                if (document.getElementById('team-colonia-geojson')) document.getElementById('team-colonia-geojson').value = e.colonia_geojson || '';

                const finFields = document.getElementById('team-financial-fields');
                if (finFields) finFields.style.display = 'none';

                const userRol = (window.futUserRol || '').toLowerCase();
                const isAdmin = ['admin', 'ejecutivo', 'dueño_liga'].includes(userRol);

                const uidContainer = document.getElementById('team-uid-container');
                if (uidContainer) {
                    uidContainer.style.display = isAdmin ? 'block' : 'none';
                }
                
                if (document.getElementById('team-uid')) {
                    document.getElementById('team-uid').value = e.uid || '';
                    document.getElementById('team-uid').readOnly = true;
                }

                document.querySelector('#modal-equipo h3').innerText = 'Editar Equipo';
                document.querySelector('#team-form .btn-primary').innerText = 'Guardar Cambios';

                Core.openModal('modal-equipo');
            }
        } catch (error) {
            console.error('Error al cargar equipo:', error);
        }
    }

    async deleteEquipo(id) {
        if (!confirm('¿Eliminar este equipo? Se borrarán los jugadores asociados.')) return;
        try {
            const res = await fetch(`/api/equipos/${id}`, { method: 'DELETE' });
            if (res.ok) {
                this.loadEquipos();
                this.ui.loadInitialStats();
            } else alert('Error al eliminar el equipo.');
        } catch (e) { console.error(e); }
    }

    async changePage(page) {
        if (page < 1 || (this.pagination && page > this.pagination.total_pages)) return;
        this.loadEquipos(page);
        window.scrollTo({ top: 0, behavior: 'smooth' });
    }

    async loadEquipos(page = 1) {
        const torneoId = document.getElementById('team-league-filter').value;
        const container = document.getElementById('equipos-container');
        if (!container) return;
        if (!torneoId) {
            container.innerHTML = '<p class="text-muted">Selecciona una liga para ver sus equipos.</p>';
            return;
        }
        const userRol = (window.USER_ROL || '').toLowerCase();
        const isReader = ['resultados', 'arbitro', 'solo vista'].includes(userRol);

        if (page === 1) {
            container.innerHTML = `
                ${!isReader ? `<div style="margin-bottom: 20px; display: flex; gap: 10px;"></div>` : ''}
                <p>Cargando equipos...</p>
            `;
        } else {
            container.innerHTML = `<p>Cargando página ${page}...</p>`;
        }

        try {
            const response = await Core.fetchAPI(`/api/equipos?torneo_id=${torneoId}&page=${page}`);
            const equipos = response.items || response;
            this.pagination = response.pagination || null;

            let html = equipos.length ? equipos.map(e => `
                <div class="league-card" style="padding: 1.5rem; display: flex; align-items: center; justify-content: space-between; gap: 1rem; cursor: pointer; min-height: 140px; border-left: 4px solid ${e.color || 'var(--primary)'};" onclick="ui.teams.goToJugadores(${e.id})">
                    <div style="flex: 1; text-align: left;">
                        <h4 style="margin: 0 0 0.2rem 0; font-size: 1.4rem; color: ${e.color || 'var(--primary)'}; text-shadow: 0 0 10px ${e.color ? e.color + '33' : 'transparent'};" 
                            onmouseover="ui.analytics.showTeamStats(this, ${e.id})" onmouseout="ui.analytics.hideTeamStats()">${e.nombre}</h4>
                        <div style="display: flex; align-items: center; gap: 6px; margin-bottom: 0.8rem;">
                            <span style="font-size: 0.75rem; color: var(--text-muted); background: rgba(255,255,255,0.05); padding: 2px 8px; border-radius: 4px; border: 1px solid var(--border);">Plantilla: ${e.jugadores ? e.jugadores.length : 0}</span>
                            ${e.grupo ? `<span style="font-size: 0.75rem; color: ${e.color || 'var(--primary)'}; background: ${e.color ? e.color + '1a' : 'rgba(0,255,136,0.1)'}; padding: 2px 8px; border-radius: 4px; border: 1px solid ${e.color || 'var(--primary)'};">${e.grupo}</span>` : ''}
                            ${e.tiene_usuario ? `<span class="badge-premium" style="font-size: 0.6rem; background: rgba(0, 191, 255, 0.1); color: #00bfff; border: 1px solid rgba(0, 191, 255, 0.3); padding: 2px 6px;">🔗 Cuenta</span>` : ''}
                        </div>
                        <div style="margin-bottom: 1.2rem; display: flex; flex-wrap: wrap; gap: 4px; max-height: 60px; overflow-y: auto; padding-right: 5px;" class="custom-scrollbar">
                            ${e.jugadores && e.jugadores.length > 0
                    ? e.jugadores.map(j => `<span style="font-size: 0.7rem; color: #fff; background: ${e.color ? e.color + '1a' : 'rgba(0,255,136,0.1)'}; padding: 2px 6px; border-radius: 4px; border: 1px solid ${e.color ? e.color + '33' : 'rgba(0,255,136,0.2)'};">${j}</span>`).join('')
                    : '<span style="font-size: 0.7rem; color: var(--text-muted); font-style: italic;">Sin jugadores registrados</span>'}
                        </div>
                        ${!isReader ? `
                        <div style="display:flex; gap:8px;" onclick="event.stopPropagation()">
                            <button onclick="ui.teams.editEquipo(${e.id})" title="Editar" style="background: rgba(99,102,241,0.15); color:#818cf8; border: 1px solid rgba(99,102,241,0.3); cursor:pointer; border-radius: 8px; padding: 6px 12px; font-size: 0.85rem; display: flex; align-items: center; gap: 4px;">✏️ <span>Editar</span></button>
                            <button onclick="ui.teams.deleteEquipo(${e.id})" title="Eliminar" style="background: rgba(239,68,68,0.15); color:#ef4444; border: 1px solid rgba(239,68,68,0.3); cursor:pointer; border-radius: 8px; padding: 6px 12px; font-size: 0.85rem; display: flex; align-items: center; gap: 4px;">🗑️ <span>Borrar</span></button>
                        </div>` : ''}
                    </div>
                    <div style="flex-shrink: 0;">
                        ${e.escudo_url ?
                    `<div style="background-image: url('${e.escudo_url}'); height: 100px; width: 100px; background-size: cover; background-position: center; border-radius: 20px; border: 2px solid var(--border); box-shadow: 0 8px 20px rgba(0,0,0,0.3);"></div>` :
                    `<div style="height: 100px; width: 100px; background: rgba(255,255,255,0.05); display: flex; align-items: center; justify-content: center; font-size: 3rem; border-radius: 20px; border: 1px dashed var(--border);">🛡️</div>`}
                    </div>
                </div>
            `).join('') : '<p>No hay equipos registrados en este torneo.</p>';

            container.innerHTML = html;

            if (this.pagination && this.pagination.total_pages > 1) {
                container.innerHTML += `
                    <div class="pagination-controls">
                        <button class="btn-pagination" ${!this.pagination.has_prev ? 'disabled' : ''} onclick="ui.teams.changePage(${this.pagination.page - 1})">&laquo; Anterior</button>
                        <span class="pagination-info">Página ${this.pagination.page} de ${this.pagination.total_pages}</span>
                        <button class="btn-pagination" ${!this.pagination.has_next ? 'disabled' : ''} onclick="ui.teams.changePage(${this.pagination.page + 1})">Siguiente &raquo;</button>
                    </div>
                `;
            }
        } catch (error) {
            container.innerHTML = '<p class="error">Error al cargar equipos.</p>';
        }
    }

    goToJugadores(equipoId) {
        const filterSelect = document.getElementById('player-team-filter');
        if (filterSelect) {
            filterSelect.value = equipoId;
            setTimeout(() => this.ui.players.loadJugadores(), 0);
        }
        this.ui.switchTorneosTab('jugadores');
    }

    async generateNewUID() {
        const id = document.getElementById('team-id').value;
        if (!id) {
            const chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789';
            let res = '';
            for (let i = 0; i < 15; i++) res += chars.charAt(Math.floor(Math.random() * chars.length));
            document.getElementById('team-uid').value = res;
            return;
        }
        if (!confirm('¿Deseas generar una nueva clave de acceso para este equipo?')) return;
        try {
            const res = await Core.fetchAPI(`/api/equipos/${id}/generate_uid`, { method: 'POST' });
            if (res.success) {
                document.getElementById('team-uid').value = res.uid;
                Core.showNotification('Nueva clave generada');
            } else alert('Error: ' + (res.error || 'No se pudo generar'));
        } catch (error) { console.error(error); alert('Error de conexión.'); }
    }

    async handleEquipoSubmit(e) {
        e.preventDefault();
        const id = document.getElementById('team-id').value;
        const method = id ? 'PUT' : 'POST';
        const url = id ? `/api/equipos/${id}` : '/api/equipos';
        const data = {
            nombre: document.getElementById('team-name').value,
            email: document.getElementById('team-email').value,
            torneo_id: document.getElementById('team-torneo-id').value,
            escudo_url: document.getElementById('team-image').value,
            grupo: document.getElementById('team-grupo').value,
            uid: document.getElementById('team-uid').value,
            colonia: document.getElementById('team-colonia')?.value || '',
            colonia_geojson: document.getElementById('team-colonia-geojson')?.value || '',
            abono_inicial: !id ? parseFloat(document.getElementById('team-abono').value || 0) : 0,
            metodo_pago: !id ? document.getElementById('team-metodo').value : 'Efectivo'
        };

        try {
            const suggestions = document.getElementById('team-colonia-suggestions');
            if(suggestions) suggestions.style.display = 'none';

            const response = await fetch(url, {
                method: method,
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(data)
            });
            if (response.ok) {
                const resData = await response.json();
                Core.showNotification(id ? 'Actualizado' : 'Registrado');
                Core.closeModal('modal-equipo');
                this.loadEquipos();
                this.ui.loadInitialStats();
                if (resData.ticket) this.ui.finance.showTicket(resData.ticket);
            } else {
                const err = await response.json();
                alert('Error: ' + (err.error || 'Error desconocido'));
            }
        } catch (error) { console.error(error); alert('Error de conexión.'); }
    }

    async autoDistribuir() {
        const torneoId = document.getElementById('team-league-filter').value;
        if (!torneoId) return alert("Selecciona una liga primero");
        const num = prompt("¿Cuántos grupos?", "2");
        if (!num || isNaN(num)) return;
        try {
            const res = await Core.fetchAPI(`/api/torneos/${torneoId}/auto_grupos`, {
                method: 'POST',
                body: JSON.stringify({ num_groups: parseInt(num) })
            });
            if (res.success) { alert(res.message); this.loadEquipos(); }
            else alert("Error: " + res.message);
        } catch (e) { console.error(e); }
    }

    initAutocomplete() {
        const input = document.getElementById('team-colonia');
        const hidden = document.getElementById('team-colonia-geojson');
        const suggestions = document.getElementById('team-colonia-suggestions');
        if(!input || !suggestions) return;

        let timeout = null;
        input.addEventListener('input', (e) => {
            clearTimeout(timeout);
            const val = e.target.value.trim();
            if(val.length < 3) { suggestions.style.display = 'none'; hidden.value = ''; return; }
            hidden.value = '';
            timeout = setTimeout(async () => {
                try {
                    const selectTorneo = document.getElementById('team-torneo-id');
                    let ciudad = 'Tijuana';
                    if (selectTorneo?.value) {
                        const torneos = await Core.fetchAPI('/api/torneos');
                        const current = Array.isArray(torneos) ? torneos.find(t => String(t.id) === String(selectTorneo.value)) : null;
                        if (current?.cancha_municipio) ciudad = current.cancha_municipio;
                    }
                    const searchQuery = `${val}, ${ciudad}, Baja California, Mexico`;
                    const searchUrl = `https://nominatim.openstreetmap.org/search?format=json&polygon_geojson=1&q=${encodeURIComponent(searchQuery)}&addressdetails=1`;
                    const res = await fetch(searchUrl, { headers: { 'Accept-Language': 'es' } });
                    const data = await res.json();
                    suggestions.innerHTML = '';
                    const filtered = data.filter(item => (item.class || '') !== 'highway');
                    if(filtered.length > 0) {
                        filtered.forEach(item => {
                            const div = document.createElement('div');
                            div.className = 'suggestions-dropdown-item';
                            div.style.padding = '8px';
                            div.style.cursor = 'pointer';
                            div.innerText = item.display_name;
                            div.onclick = () => {
                                input.value = item.display_name.split(',')[0];
                                if (item.geojson?.type === 'Polygon' || item.geojson?.type === 'MultiPolygon') 
                                    hidden.value = JSON.stringify(item.geojson);
                                suggestions.style.display = 'none';
                            };
                            suggestions.appendChild(div);
                        });
                        suggestions.style.display = 'block';
                    }
                } catch(err) { console.error(err); }
            }, 600);
        });
    }

    downloadTemplate() { window.location.href = '/api/import/sample-excel'; }

    async importExcel(input) {
        if (!input.files?.[0]) return;
        const torneoId = document.getElementById('team-league-filter').value;
        if (!torneoId) { alert("Selecciona un torneo."); input.value = ''; return; }
        const formData = new FormData();
        formData.append('file', input.files[0]);
        try {
            Core.showNotification('Importando...', 'info');
            const res = await fetch(`/api/torneos/${torneoId}/import-excel`, { method: 'POST', body: formData });
            if (res.ok) { alert('Éxito'); this.loadEquipos(); this.ui.loadInitialStats(); }
            else alert('Error al importar');
        } catch (e) { console.error(e); } finally { input.value = ''; }
    }

    // --- REGISTRO MASIVO V4 (INLINE) ---
    showBulkModal() {
        const torneoId = document.getElementById('team-league-filter').value;
        if (!torneoId) { alert('Selecciona una liga.'); return; }
        const body = document.getElementById('bulk-teams-body');
        body.innerHTML = '';
        this.bulkTeams = [];
        for (let i = 0; i < 3; i++) this.addBulkRow();
        Core.openModal('modal-bulk-teams');
        this.updateBulkCounter();
    }

    addBulkRow() {
        const body = document.getElementById('bulk-teams-body');
        const index = this.bulkTeams.length;
        this.bulkTeams[index] = { nombre: '', email: '', grupo: '', jugadores: [] };
        
        const tr = document.createElement('tr');
        tr.className = 'bulk-team-row-v4';
        tr.style.background = index % 2 === 0 ? 'rgba(255,255,255,0.02)' : 'transparent';
        
        tr.innerHTML = `
            <td colspan="4" style="padding: 25px; border-bottom: 2px solid var(--border);">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 15px;">
                    <div style="display: flex; align-items: center; gap: 15px;">
                        <span style="background: var(--primary); color: #000; width: 30px; height: 30px; display: flex; align-items: center; justify-content: center; border-radius: 50%; font-weight: bold; font-size: 0.9rem;">${index + 1}</span>
                        <h4 style="margin: 0; color: #fff; text-transform: uppercase; letter-spacing: 1px; font-size: 1rem;">Configuración de Equipo</h4>
                    </div>
                    <button onclick="ui.teams.removeBulkRow(${index}, this)" 
                        style="color: #ef4444; background: rgba(239,68,68,0.1); border: 1px solid rgba(239,68,68,0.2); padding: 5px 15px; border-radius: 6px; cursor: pointer; font-size: 0.8rem;">
                        🗑️ Quitar Equipo
                    </button>
                </div>

                <div style="display: grid; grid-template-columns: 2fr 1.5fr 1fr; gap: 15px; margin-bottom: 20px;">
                    <div class="form-group" style="margin: 0;">
                        <label style="font-size: 0.7rem; color: #aaa; margin-bottom: 4px; display: block;">NOMBRE DEL EQUIPO *</label>
                        <input type="text" placeholder="Ej. Real Madrid" oninput="ui.teams.updateBulkTeamData(${index}, 'nombre', this.value)"
                            style="width: 100%; padding: 12px; background: #000; border: 1px solid var(--border); border-radius: 8px; color: #fff; font-weight: bold;">
                    </div>
                    <div class="form-group" style="margin: 0;">
                        <label style="font-size: 0.7rem; color: #aaa; margin-bottom: 4px; display: block;">EMAIL DELEGADO (Opcional)</label>
                        <input type="email" placeholder="correo@ejemplo.com" oninput="ui.teams.updateBulkTeamData(${index}, 'email', this.value)"
                            style="width: 100%; padding: 12px; background: #000; border: 1px solid var(--border); border-radius: 8px; color: #fff;">
                    </div>
                    <div class="form-group" style="margin: 0;">
                        <label style="font-size: 0.7rem; color: #aaa; margin-bottom: 4px; display: block;">GRUPO</label>
                        <input type="text" placeholder="A, B..." oninput="ui.teams.updateBulkTeamData(${index}, 'grupo', this.value)"
                            style="width: 100%; padding: 12px; background: #000; border: 1px solid var(--border); border-radius: 8px; color: #fff; text-align: center;">
                    </div>
                </div>

                <div style="background: rgba(255,255,255,0.02); border: 1px solid var(--border); border-radius: 12px; padding: 20px;">
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 15px;">
                        <div>
                            <span style="font-size: 0.85rem; font-weight: bold; color: var(--primary);">📋 PLANTILLA DE JUGADORES</span>
                            <span id="team-players-count-${index}" style="margin-left: 10px; color: #666; font-size: 0.8rem;">(0 jugadores)</span>
                            <div style="display: inline-flex; gap: 15px; margin-left: 30px; font-size: 0.75rem; color: #aaa;">
                                <span>⚽ Goles: <b id="team-sum-goles-${index}" style="color: #fff;">0</b></span>
                                <span>🟨 Amonestaciones: <b id="team-sum-amarillas-${index}" style="color: #fbbf24;">0</b></span>
                                <span>🟥 Expulsiones: <b id="team-sum-rojas-${index}" style="color: #ef4444;">0</b></span>
                            </div>
                        </div>
                        <button onclick="ui.teams.addInlinePlayer(${index})" 
                            style="background: var(--primary); color: #000; border: none; padding: 8px 18px; border-radius: 30px; font-size: 0.75rem; font-weight: bold; cursor: pointer; transition: all 0.2s;">
                            + Añadir Jugador
                        </button>
                    </div>
                    
                    <div style="overflow-x: auto;">
                        <table style="width: 100%; border-collapse: collapse;">
                            <thead>
                                <tr style="color: #444; font-size: 0.7rem; text-transform: uppercase; letter-spacing: 1px;">
                                    <th style="text-align: left; padding: 10px; border-bottom: 1px solid var(--border);">Nombre del Jugador</th>
                                    <th style="text-align: center; padding: 10px; border-bottom: 1px solid var(--border); width: 100px;">Goles</th>
                                    <th style="text-align: center; padding: 10px; border-bottom: 1px solid var(--border); width: 100px;">Amarillas</th>
                                    <th style="text-align: center; padding: 10px; border-bottom: 1px solid var(--border); width: 100px;">Rojas</th>
                                    <th style="width: 50px; border-bottom: 1px solid var(--border);"></th>
                                </tr>
                            </thead>
                            <tbody id="players-list-${index}"></tbody>
                        </table>
                    </div>
                </div>
            </td>
        `;
        body.appendChild(tr);
        
        const container = document.querySelector('#modal-bulk-teams .custom-scrollbar');
        if (container) container.scrollTo({ top: container.scrollHeight, behavior: 'smooth' });

        this.addInlinePlayer(index);
        this.updateBulkCounter();
    }

    removeBulkRow(index, btn) {
        if (this.bulkTeams[index]) {
            this.bulkTeams[index].nombre = ''; // Marcamos como vacío para que el filtro lo ignore
            this.bulkTeams[index].jugadores = [];
        }
        btn.closest('tr').remove();
        this.updateBulkCounter();
    }

    updateBulkTeamData(index, field, value) {
        if (this.bulkTeams[index]) this.bulkTeams[index][field] = value;
        this.updateBulkCounter();
    }

    addInlinePlayer(index, nombre = '', goles = 0, amarillas = 0, rojas = 0) {
        const list = document.getElementById(`players-list-${index}`);
        if (!list) return;
        const tr = document.createElement('tr');
        tr.className = 'player-inline-row fade-in';
        tr.innerHTML = `
            <td style="padding: 8px 10px;">
                <input type="text" placeholder="Nombre completo del jugador" class="p-name" 
                    oninput="ui.teams.syncInlinePlayerStats(${index})" 
                    style="width: 100%; background: rgba(0,0,0,0.2); border: 1px solid rgba(255,255,255,0.05); border-radius: 4px; padding: 8px; color: #fff; font-size: 0.85rem;">
            </td>
            <td style="padding: 8px 10px;">
                <input type="number" class="p-goles" value="${goles}" min="0" 
                    oninput="ui.teams.syncInlinePlayerStats(${index})" 
                    style="width: 100%; background: rgba(0,0,0,0.2); border: 1px solid rgba(255,255,255,0.05); border-radius: 4px; padding: 8px; color: #fff; text-align: center; font-weight: bold;">
            </td>
            <td style="padding: 8px 10px;">
                <input type="number" class="p-amarillas" value="${amarillas}" min="0" 
                    oninput="ui.teams.syncInlinePlayerStats(${index})" 
                    style="width: 100%; background: rgba(0,0,0,0.2); border: 1px solid rgba(255,255,255,0.05); border-radius: 4px; padding: 8px; color: #fbbf24; text-align: center; font-weight: bold;">
            </td>
            <td style="padding: 8px 10px;">
                <input type="number" class="p-rojas" value="${rojas}" min="0" 
                    oninput="ui.teams.syncInlinePlayerStats(${index})" 
                    style="width: 100%; background: rgba(0,0,0,0.2); border: 1px solid rgba(255,255,255,0.05); border-radius: 4px; padding: 8px; color: #ef4444; text-align: center; font-weight: bold;">
            </td>
            <td style="padding: 8px 10px; text-align: center;">
                <button onclick="this.closest('tr').remove(); ui.teams.syncInlinePlayerStats(${index})" 
                    style="color: #666; background: none; border: none; cursor: pointer; font-size: 1.2rem; transition: color 0.2s;"
                    onmouseover="this.style.color='#ef4444'" onmouseout="this.style.color='#666'">&times;</button>
            </td>
        `;
        list.appendChild(tr);
        
        const playerListContainer = list.parentElement.parentElement;
        if (playerListContainer) playerListContainer.scrollTo({ top: playerListContainer.scrollHeight, behavior: 'smooth' });

        this.syncInlinePlayerStats(index);
    }

    syncInlinePlayerStats(index) {
        const list = document.getElementById(`players-list-${index}`);
        if (!list) return;
        const rows = list.querySelectorAll('tr');
        const jugadores = [];
        let tg = 0, ta = 0, tr = 0;
        rows.forEach(row => {
            const nombre = row.querySelector('.p-name').value.trim();
            const goles = parseInt(row.querySelector('.p-goles').value) || 0;
            const amarillas = parseInt(row.querySelector('.p-amarillas').value) || 0;
            const rojas = parseInt(row.querySelector('.p-rojas').value) || 0;
            if (nombre || (goles + amarillas + rojas > 0)) {
                jugadores.push({ nombre, goles, amarillas, rojas });
                tg += goles; ta += amarillas; tr += rojas;
            }
        });
        if (this.bulkTeams[index]) this.bulkTeams[index].jugadores = jugadores;
        document.getElementById(`team-sum-goles-${index}`).innerText = tg;
        document.getElementById(`team-sum-amarillas-${index}`).innerText = ta;
        document.getElementById(`team-sum-rojas-${index}`).innerText = tr;
        document.getElementById(`team-players-count-${index}`).innerText = `(${jugadores.length})`;
    }

    updateBulkCounter() {
        if (!this.bulkTeams) return;
        const count = this.bulkTeams.filter(t => t.nombre.trim().length > 0).length;
        const c = document.getElementById('bulk-counter');
        if (c) c.innerText = `${count} equipo(s) listo(s)`;
    }

    async saveBulkTeams() {
        const torneoId = document.getElementById('team-league-filter').value;
        const eq = this.bulkTeams.filter(t => t.nombre.trim().length > 0);
        if (!eq.length) return alert('Agrega un equipo.');
        try {
            Core.showNotification('Enviando...', 'info');
            const res = await fetch('/api/equipos/bulk', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ torneo_id: torneoId, equipos: eq })
            });
            if (res.ok) { Core.closeModal('modal-bulk-teams'); this.loadEquipos(); }
            else alert('Error al guardar');
        } catch (e) { console.error(e); }
    }
}
