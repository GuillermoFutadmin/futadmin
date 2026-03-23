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
            // Optimización: Fetch directo por ID en lugar de cargar toda la lista
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
                    // El UID es de solo lectura a menos que se use el botón Generar
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
                ${!isReader ? `
                <div style="margin-bottom: 20px; display: flex; gap: 10px;">
                    </div>` : ''}
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
                            ${e.tiene_usuario ? `
                                <span class="badge-premium" style="font-size: 0.6rem; background: rgba(0, 191, 255, 0.1); color: #00bfff; border: 1px solid rgba(0, 191, 255, 0.3); padding: 2px 6px;">
                                    🔗 Cuenta
                                </span>
                            ` : ''}
                        </div>
                        
                        <div style="margin-bottom: 1.2rem; display: flex; flex-wrap: wrap; gap: 4px; max-height: 60px; overflow-y: auto; padding-right: 5px;" class="custom-scrollbar">
                            ${e.jugadores && e.jugadores.length > 0
                    ? e.jugadores.map(j => `<span style="font-size: 0.7rem; color: #fff; background: ${e.color ? e.color + '1a' : 'rgba(0,255,136,0.1)'}; padding: 2px 6px; border-radius: 4px; border: 1px solid ${e.color ? e.color + '33' : 'rgba(0,255,136,0.2)'};">${j}</span>`).join('')
                    : '<span style="font-size: 0.7rem; color: var(--text-muted); font-style: italic;">Sin jugadores registrados</span>'
                }
                        </div>

                        ${!isReader ? `
                        <div style="display:flex; gap:8px;" onclick="event.stopPropagation()">
                            <button onclick="ui.teams.editEquipo(${e.id})" title="Editar" style="background: rgba(99,102,241,0.15); color:#818cf8; border: 1px solid rgba(99,102,241,0.3); cursor:pointer; border-radius: 8px; padding: 6px 12px; font-size: 0.85rem; display: flex; align-items: center; gap: 4px;">✏️ <span>Editar</span></button>
                            <button onclick="ui.teams.deleteEquipo(${e.id})" title="Eliminar" style="background: rgba(239,68,68,0.15); color:#ef4444; border: 1px solid rgba(239,68,68,0.3); cursor:pointer; border-radius: 8px; padding: 6px 12px; font-size: 0.85rem; display: flex; align-items: center; gap: 4px;">🗑️ <span>Borrar</span></button>
                        </div>
                        ` : ''}
                    </div>
                    <div style="flex-shrink: 0;">
                        ${e.escudo_url ?
                    `<div style="background-image: url('${e.escudo_url}'); height: 100px; width: 100px; background-size: cover; background-position: center; border-radius: 20px; border: 2px solid var(--border); box-shadow: 0 8px 20px rgba(0,0,0,0.3);"></div>` :
                    `<div style="height: 100px; width: 100px; background: rgba(255,255,255,0.05); display: flex; align-items: center; justify-content: center; font-size: 3rem; border-radius: 20px; border: 1px dashed var(--border);">🛡️</div>`
                }
                    </div>
                </div>
            `).join('') : '<p>No hay equipos registrados en este torneo.</p>';

            if (page === 1) {
                container.innerHTML = html;
            } else {
                container.innerHTML = html;
            }

            if (this.pagination && this.pagination.total_pages > 1) {
                container.innerHTML += `
                    <div class="pagination-controls">
                        <button class="btn-pagination" ${!this.pagination.has_prev ? 'disabled' : ''} 
                            onclick="ui.teams.changePage(${this.pagination.page - 1})">
                            &laquo; Anterior
                        </button>
                        <span class="pagination-info">Página ${this.pagination.page} de ${this.pagination.total_pages}</span>
                        <button class="btn-pagination" ${!this.pagination.has_next ? 'disabled' : ''} 
                            onclick="ui.teams.changePage(${this.pagination.page + 1})">
                            Siguiente &raquo;
                        </button>
                    </div>
                `;
            }
        } catch (error) {
            container.innerHTML = '<p class="error">Error al cargar equipos.</p>';
        }
    }

    goToJugadores(equipoId) {
        // Precargar la información
        const filterSelect = document.getElementById('player-team-filter');
        if (filterSelect) {
            filterSelect.value = equipoId;
            setTimeout(() => {
                this.ui.players.loadJugadores();
            }, 0);
        }

        // Cambiar la pestaña directamente
        this.ui.switchTorneosTab('jugadores');
    }

    async generateNewUID() {
        const id = document.getElementById('team-id').value;
        if (!id) {
            // Si es un equipo nuevo, solo generamos uno localmente por ahora (aunque el backend lo hará al guardar)
            // Pero para consistencia, podemos pedir uno al backend si quisiéramos.
            // Por simplicidad, si es nuevo, el backend lo genera al POST si viene vacío.
            // Pero si el usuario pulsa "Generar" en uno nuevo, podemos inventar uno.
            const chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789';
            let res = '';
            for (let i = 0; i < 15; i++) res += chars.charAt(Math.floor(Math.random() * chars.length));
            document.getElementById('team-uid').value = res;
            return;
        }

        if (!confirm('¿Deseas generar una nueva clave de acceso para este equipo? La anterior dejará de funcionar.')) return;

        try {
            const res = await Core.fetchAPI(`/api/equipos/${id}/generate_uid`, { method: 'POST' });
            if (res.success) {
                document.getElementById('team-uid').value = res.uid;
                Core.showNotification('Nueva clave generada con éxito');
            } else {
                alert('Error: ' + (res.error || 'No se pudo generar la clave'));
            }
        } catch (error) {
            console.error('Error generating UID:', error);
            alert('Error de conexión.');
        }
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
            colonia: document.getElementById('team-colonia') ? document.getElementById('team-colonia').value : '',
            colonia_geojson: document.getElementById('team-colonia-geojson') ? document.getElementById('team-colonia-geojson').value : '',
            abono_inicial: !id ? parseFloat(document.getElementById('team-abono').value || 0) : 0,
            metodo_pago: !id ? document.getElementById('team-metodo').value : 'Efectivo'
        };

        try {
            // Asegurar que las sugerencias se oculten al procesar
            const suggestions = document.getElementById('team-colonia-suggestions');
            if(suggestions) suggestions.style.display = 'none';

            const response = await fetch(url, {
                method: method,
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(data)
            });
            if (response.ok) {
                const resData = await response.json();
                Core.showNotification(id ? 'Equipo actualizado con éxito' : 'Equipo registrado con éxito');
                Core.closeModal('modal-equipo');
                this.loadEquipos();
                this.ui.loadInitialStats();
                if (resData.ticket) {
                    this.ui.finance.showTicket(resData.ticket);
                }
            } else {
                const err = await response.json();
                alert('Error al guardar el equipo: ' + (err.error || 'Error desconocido'));
            }
        } catch (error) { 
            console.error('Error:', error); 
            alert('Error de conexión o fallo al procesar la respuesta del servidor.');
        }
    }

    async autoDistribuir() {
        const torneoId = document.getElementById('team-league-filter').value;
        if (!torneoId) return alert("Selecciona una liga primero");
        const num = prompt("¿En cuántos grupos deseas distribuir los equipos? (Ej: 2, 4)", "2");
        if (!num || isNaN(num)) return;
        if (!confirm(`Se repartirán los equipos aleatoriamente en ${num} grupos. ¿Continuar?`)) return;
        try {
            const res = await Core.fetchAPI(`/api/torneos/${torneoId}/auto_grupos`, {
                method: 'POST',
                body: JSON.stringify({ num_grupos: parseInt(num) })
            });
            if (res.success) {
                alert(res.message);
                this.loadEquipos();
            } else alert("Error: " + res.message);
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
            if(val.length < 3) {
                suggestions.style.display = 'none';
                hidden.value = '';
                return;
            }
            
            // Si el usuario cambia el texto borramos el geojson para obligarlo a seleccionar de la lista si quiere poligono
            hidden.value = '';

            timeout = setTimeout(async () => {
                try {
                    // Obtener el municipio del Torneo Destino seleccionado
                    const selectTorneo = document.getElementById('team-torneo-id');
                    let ciudad = 'Tijuana'; // Fallback
                    if (selectTorneo && selectTorneo.value) {
                        try {
                            const response = await Core.fetchAPI('/api/torneos');
                            const torneos = response.items || response;
                            const currentTorneo = Array.isArray(torneos) ? torneos.find(t => String(t.id) === String(selectTorneo.value)) : null;
                            if (currentTorneo && currentTorneo.cancha_municipio) {
                                ciudad = currentTorneo.cancha_municipio;
                            }
                        } catch(err) {
                            console.error('Error fetching torneos for autocomplete', err);
                        }
                    }

                    // Nominatim prohíbe mezclar el parámetro 'q' con parámetros estructurados (city, state).
                    // Lo correcto es concatenar la búsqueda en un solo string 'q'.
                    const searchQuery = `${val}, ${ciudad}, Baja California, Mexico`;
                    // Agregamos featuretype=settlement para tratar de priorizar áreas
                    const searchUrl = `https://nominatim.openstreetmap.org/search?format=json&polygon_geojson=1&q=${encodeURIComponent(searchQuery)}&addressdetails=1`;
                    
                    const res = await fetch(searchUrl, {
                        headers: {
                            'Accept-Language': 'es'
                        }
                    });

                    if (!res.ok) {
                        throw new Error(`Nominatim error: ${res.status}`);
                    }

                    const data = await res.json();
                    
                    suggestions.innerHTML = '';
                    
                    // Filtrar: Queremos colonias (suburb, neighbourhood, hamlet, quarter)
                    // y que tengan polígono si es posible
                    const filtered = data.filter(item => {
                        const type = item.type || '';
                        const cls = item.class || '';
                        // Evitar calles (highway) y puntos de interés específicos (amenity, shop, etc)
                        if (cls === 'highway' || cls === 'amenity' || cls === 'shop' || cls === 'office') return false;
                        return true;
                    });

                    if(filtered.length > 0) {
                        filtered.forEach(item => {
                            const div = document.createElement('div');
                            div.className = 'suggestions-dropdown-item';
                            div.style.padding = '10px';
                            div.style.cursor = 'pointer';
                            div.style.color = 'white';
                            div.style.borderBottom = '1px solid rgba(255,255,255,0.1)';
                            div.style.fontSize = '0.9rem';
                            
                            // Simplificar texto: Tomar el nombre principal y el municipio/ciudad
                            const addr = item.address || {};
                            const mainName = addr.suburb || addr.neighbourhood || addr.quarter || addr.village || item.name;
                            const city = addr.city || addr.town || addr.municipality || '';
                            
                            div.innerText = city ? `${mainName} (${city})` : mainName;
                            
                            div.onmouseover = () => div.style.background = 'var(--primary)';
                            div.onmouseout = () => div.style.background = 'transparent';
                            div.onclick = () => {
                                input.value = mainName;
                                // Forzamos que sea un polígono. Nominatim a veces devuelve Point en geojson si no encuentra área.
                                if (item.geojson && (item.geojson.type === 'Polygon' || item.geojson.type === 'MultiPolygon')) {
                                    hidden.value = JSON.stringify(item.geojson);
                                } else {
                                    // Si no es polígono, guardamos vacío para que el mapa no pinte un marcador feo
                                    hidden.value = '';
                                    Core.showNotification('Aviso: Esta zona no tiene perímetro definido, no se verá en el mapa.', 'warning');
                                }
                                suggestions.style.display = 'none';
                            };
                            suggestions.appendChild(div);
                        });
                        suggestions.style.display = 'block';
                    } else {
                        suggestions.style.display = 'none';
                    }
                } catch(err) {
                    console.error('Nominatim error', err);
                }
            }, 600);
        });

        document.addEventListener('click', (e) => {
            if(e.target !== input && e.target !== suggestions) {
                suggestions.style.display = 'none';
            }
        });
    }

    downloadTemplate() {
        window.location.href = '/api/import/sample-excel';
    }

    async importExcel(input) {
        if (!input.files || !input.files[0]) return;
        const torneoId = document.getElementById('team-league-filter').value;
        if (!torneoId) {
            alert("Selecciona un torneo primero.");
            input.value = '';
            return;
        }

        const file = input.files[0];
        const formData = new FormData();
        formData.append('file', file);

        try {
            Core.showNotification('Procesando archivo... No recargues.', 'info');
            const res = await fetch(`/api/torneos/${torneoId}/import-excel`, {
                method: 'POST',
                body: formData
            });

            if (res.ok) {
                const summary = await res.json();
                let msg = `¡Importación exitosa!\n\nEquipos creados: ${summary.equipos_creados}\nJugadores creados: ${summary.jugadores_creados}`;
                if (summary.errores && summary.errores.length > 0) {
                    msg += `\n\nErrores encontrados:\n- ${summary.errores.join('\n- ')}`;
                }
                alert(msg);
                this.loadEquipos();
                this.ui.loadInitialStats();
            } else {
                const err = await res.json();
                alert('Error al importar: ' + (err.error || 'Error desconocido'));
            }
        } catch (error) {
            console.error('Import error:', error);
            alert('Error de conexión.');
        } finally {
            input.value = '';
        }
    }

    // --- REGISTRO MASIVO IN-APP ---
    showBulkModal() {
        const torneoId = document.getElementById('team-league-filter').value;
        if (!torneoId) {
            alert('Por favor selecciona una liga/torneo primero.');
            return;
        }

        const body = document.getElementById('bulk-teams-body');
        body.innerHTML = '';
        this.bulkTeams = []; // Almacén de datos en memoria para V3
        
        // Iniciamos con 5 filas vacías
        for (let i = 0; i < 5; i++) {
            this.addBulkRow();
        }

        Core.openModal('modal-bulk-teams');
        this.updateBulkCounter();
    }

    addBulkRow() {
        const body = document.getElementById('bulk-teams-body');
        const index = body.children.length;
        
        // Inicializar datos del equipo en memoria
        this.bulkTeams[index] = {
            nombre: '',
            email: '',
            grupo: '',
            jugadores: []
        };

        const tr = document.createElement('tr');
        tr.className = 'bulk-row fade-in';
        tr.dataset.index = index;
        tr.style.borderBottom = '1px solid var(--border)';
        
        tr.innerHTML = `
            <td style="padding: 12px; color: var(--text-muted); font-weight: bold;">${index + 1}</td>
            <td style="padding: 8px;">
                <input type="text" class="bulk-team-name" placeholder="Ej. Los Galácticos" 
                    value="${this.bulkTeams[index].nombre}"
                    style="width: 100%; padding: 8px; background: rgba(255,255,255,0.03); border: 1px solid var(--border); border-radius: 6px; color: #fff;"
                    oninput="ui.teams.updateBulkTeamData(${index}, 'nombre', this.value)">
            </td>
            <td style="padding: 8px; text-align: center;">
                <button onclick="ui.teams.editBulkPlayers(${index})" 
                    class="btn-outline" style="padding: 4px 10px; font-size: 0.8rem; display: flex; align-items: center; gap: 5px; margin: 0 auto; min-width: 80px; justify-content: center;">
                    👥 <span id="team-players-count-${index}">0</span>
                </button>
            </td>
            <td style="padding: 8px; text-align: center; color: var(--primary); font-weight: bold;" id="team-sum-goles-${index}">0</td>
            <td style="padding: 8px; text-align: center; color: #fbbf24;" id="team-sum-amarillas-${index}">0</td>
            <td style="padding: 8px; text-align: center; color: #ef4444;" id="team-sum-rojas-${index}">0</td>
            <td style="padding: 8px;">
                <input type="email" class="bulk-team-email" placeholder="delegado@correo.com" 
                    value="${this.bulkTeams[index].email}"
                    style="width: 100%; padding: 8px; background: rgba(255,255,255,0.03); border: 1px solid var(--border); border-radius: 6px; color: #fff;"
                    oninput="ui.teams.updateBulkTeamData(${index}, 'email', this.value)">
            </td>
            <td style="padding: 8px;">
                <input type="text" class="bulk-team-grupo" placeholder="A, B..." 
                    value="${this.bulkTeams[index].grupo}"
                    style="width: 100%; padding: 8px; background: rgba(255,255,255,0.03); border: 1px solid var(--border); border-radius: 6px; color: #fff;"
                    oninput="ui.teams.updateBulkTeamData(${index}, 'grupo', this.value)">
            </td>
            <td style="padding: 8px; text-align: center;">
                <button onclick="this.closest('tr').remove(); ui.teams.updateBulkCounter();" 
                    style="background: rgba(239,68,68,0.1); color: #ef4444; border: 1px solid rgba(239,68,68,0.2); border-radius: 6px; padding: 4px 8px; cursor: pointer;">
                    ✕
                </button>
            </td>
        `;
        body.appendChild(tr);
        this.updateBulkCounter();
    }

    updateBulkTeamData(index, field, value) {
        if (this.bulkTeams[index]) {
            this.bulkTeams[index][field] = value;
        }
        this.updateBulkCounter();
    }

    // Modal de Jugadores (V3)
    editBulkPlayers(index) {
        this.currentEditingTeamIndex = index;
        const team = this.bulkTeams[index];
        const title = document.getElementById('bulk-players-title');
        title.innerText = `👥 Plantilla: ${team.nombre || 'Equipo ' + (index+1)}`;
        
        const body = document.getElementById('bulk-players-body');
        body.innerHTML = '';
        
        if (team.jugadores.length === 0) {
            // Empezamos con 3 filas vacías si no hay nada
            for (let i = 0; i < 3; i++) this.addBulkPlayerRow();
        } else {
            team.jugadores.forEach(j => this.addBulkPlayerRow(j.nombre, j.goles, j.amarillas, j.rojas));
        }
        
        Core.openModal('modal-bulk-players');
    }

    addBulkPlayerRow(nombre = '', goles = 0, amarillas = 0, rojas = 0) {
        const body = document.getElementById('bulk-players-body');
        const tr = document.createElement('tr');
        tr.style.borderBottom = '1px solid rgba(255,255,255,0.05)';
        
        tr.innerHTML = `
            <td style="padding: 8px;">
                <input type="text" class="p-name" placeholder="Nombre completo" value="${nombre}"
                    style="width: 100%; padding: 6px; background: rgba(0,0,0,0.2); border: 1px solid var(--border); border-radius: 4px; color: #fff;">
            </td>
            <td style="padding: 8px; width: 60px;">
                <input type="number" class="p-goles" value="${goles}" min="0" title="Goles Históricos"
                    style="width: 100%; padding: 6px; background: rgba(0,0,0,0.2); border: 1px solid var(--border); border-radius: 4px; color: #fff; text-align: center;">
            </td>
            <td style="padding: 8px; width: 60px;">
                <input type="number" class="p-amarillas" value="${amarillas}" min="0" title="Amarillas"
                    style="width: 100%; padding: 6px; background: rgba(0,0,0,0.2); border: 1px solid var(--border); border-radius: 4px; color: #fff; text-align: center;">
            </td>
            <td style="padding: 8px; width: 60px;">
                <input type="number" class="p-rojas" value="${rojas}" min="0" title="Rojas"
                    style="width: 100%; padding: 6px; background: rgba(0,0,0,0.2); border: 1px solid var(--border); border-radius: 4px; color: #fff; text-align: center;">
            </td>
            <td style="padding: 8px; text-align: center; width: 40px;">
                <button onclick="this.closest('tr').remove()" style="color: #ef4444; background: none; border: none; cursor: pointer;">✕</button>
            </td>
        `;
        body.appendChild(tr);
    }

    saveBulkPlayerList() {
        const index = this.currentEditingTeamIndex;
        const rows = document.querySelectorAll('#bulk-players-body tr');
        const jugadores = [];
        
        rows.forEach(row => {
            const nombre = row.querySelector('.p-name').value.trim();
            const goles = parseInt(row.querySelector('.p-goles').value) || 0;
            const amarillas = parseInt(row.querySelector('.p-amarillas').value) || 0;
            const rojas = parseInt(row.querySelector('.p-rojas').value) || 0;
            
            if (nombre) {
                jugadores.push({ nombre, goles, amarillas, rojas });
            }
        });
        
        this.bulkTeams[index].jugadores = jugadores;
        this.syncTeamStats(index);
        Core.closeModal('modal-bulk-players');
    }

    syncTeamStats(index) {
        const team = this.bulkTeams[index];
        const jugadores = team.jugadores;
        
        const sumGoles = jugadores.reduce((acc, j) => acc + j.goles, 0);
        const sumAmarillas = jugadores.reduce((acc, j) => acc + j.amarillas, 0);
        const sumRojas = jugadores.reduce((acc, j) => acc + j.rojas, 0);
        
        const countSpan = document.getElementById(`team-players-count-${index}`);
        if (countSpan) countSpan.innerText = jugadores.length;
        
        const golesTd = document.getElementById(`team-sum-goles-${index}`);
        if (golesTd) golesTd.innerText = sumGoles;
        
        const amarillasTd = document.getElementById(`team-sum-amarillas-${index}`);
        if (amarillasTd) amarillasTd.innerText = sumAmarillas;
        
        const rojasTd = document.getElementById(`team-sum-rojas-${index}`);
        if (rojasTd) rojasTd.innerText = sumRojas;
    }

    updateBulkCounter() {
        if (!this.bulkTeams) return;
        let count = 0;
        this.bulkTeams.forEach(t => {
            if (t.nombre && t.nombre.trim().length > 0) count++;
        });
        const counter = document.getElementById('bulk-counter');
        if (counter) counter.innerText = `${count} equipo(s) listo(s) para registrar`;
    }

    async saveBulkTeams() {
        const torneoId = document.getElementById('team-league-filter').value;
        const finalEquipos = this.bulkTeams.filter(t => t.nombre.trim().length > 0);

        if (finalEquipos.length === 0) {
            alert('Por favor agrega al menos un equipo con nombre.');
            return;
        }

        try {
            Core.showNotification('🚀 Registrando equipos y estadísticas históricas...', 'info');
            const response = await fetch('/api/equipos/bulk', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    torneo_id: torneoId,
                    equipos: finalEquipos
                })
            });

            if (response.ok) {
                const res = await response.json();
                Core.showNotification(`✨ ${res.creados} equipos registrados con éxito`, 'success');
                Core.closeModal('modal-bulk-teams');
                this.loadEquipos();
                this.ui.loadInitialStats();
            } else {
                const err = await response.json();
                alert('Error al registrar: ' + (err.error || 'Error desconocido'));
            }
        } catch (error) {
            console.error('Bulk save error:', error);
            alert('Hubo un error al procesar la solicitud.');
        }
    }
}
