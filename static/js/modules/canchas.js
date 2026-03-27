import { Core } from './core.js';

export class CanchasModule {
    constructor(ui) {
        this.ui = ui;
        this.canchas = [];
        document.addEventListener('futadmin:limitsLoaded', () => this.checkLimits());
    }

    async loadCanchas(page = 1) {
        const container = document.getElementById('canchas-container');
        if (!container) return;
        
        container.innerHTML = '<div class="loading-premium"><span>⌛</span> Cargando sedes...</div>';
        
        try {
            const data = await Core.fetchAPI(`/api/canchas?page=${page}`);
            this.canchas = data.items || data;
            this.pagination = data.pagination || null;
            this.renderCanchas(this.canchas);
            this.checkLimits();
        } catch (e) {
            container.innerHTML = '<div class="error-premium">Error al cargar sedes</div>';
            Core.showNotification('No se pudieron cargar las canchas', 'error');
        }
    }

    async loadCampos() {
        const container = document.getElementById('campos-container');
        if (!container) return;

        container.innerHTML = '<div class="loading-premium"><span>⌛</span> Cargando canchas...</div>';

        try {
            if (!this.canchas || this.canchas.length === 0) {
                const data = await Core.fetchAPI('/api/canchas?per_page=1000');
                this.canchas = data.items || data;
            }
            let allCampos = [];
            for (const sede of this.canchas) {
                try {
                    const camposData = await Core.fetchAPI(`/api/canchas/${sede.id}/campos`);
                    const campos = Array.isArray(camposData) ? camposData : (camposData.items || []);
                    campos.forEach(c => c._sede_nombre = sede.nombre);
                    allCampos = allCampos.concat(campos);
                } catch(e2) {}
            }
            this.renderCampos(allCampos);
        } catch (e) {
            container.innerHTML = '<div class="error-premium">Error al cargar las canchas</div>';
            Core.showNotification('No se pudieron cargar las canchas', 'error');
        }
    }

    renderCampos(campos) {
        const container = document.getElementById('campos-container');
        if (!container) return;

        if (campos.length === 0) {
            container.innerHTML = `
                <div style="text-align:center; padding:4rem; background:var(--card-bg); border-radius:20px; border:1px dashed var(--border); grid-column:1/-1;">
                    <div style="font-size:3rem; margin-bottom:1rem;">🥅</div>
                    <h4>No tienes canchas registradas</h4>
                    <p class="text-muted">Primero crea una Sede, luego agrega sus canchas individuales desde el botón de abajo.</p>
                    <button class="btn-primary" onclick="ui.canchas.showModalCampo()" style="margin-top:1rem;">+ Nueva Cancha</button>
                </div>`;
            return;
        }

        container.innerHTML = `
            <div style="grid-column:1/-1; width:100%; overflow-x:auto; background:var(--card); border-radius:14px; border:1px solid var(--border);">
                <table style="width:100%; border-collapse:collapse;">
                    <thead>
                        <tr style="background:rgba(0,0,0,0.3); border-bottom:2px solid var(--border);">
                            <th style="padding:12px 20px; color:var(--text-muted); font-size:0.75rem; text-transform:uppercase;">Cancha</th>
                            <th style="padding:12px 20px; color:var(--text-muted); font-size:0.75rem; text-transform:uppercase;">Sede / Predio</th>
                            <th style="padding:12px 20px; color:var(--text-muted); font-size:0.75rem; text-transform:uppercase;">Modalidad</th>
                            <th style="padding:12px 20px; color:var(--text-muted); font-size:0.75rem; text-transform:uppercase;">Superficie</th>
                            <th style="padding:12px 20px; color:var(--text-muted); font-size:0.75rem; text-transform:uppercase;">Techada</th>
                        </tr>
                    </thead>
                    <tbody>
                        ${campos.map((c, i) => `
                            <tr style="border-bottom:1px solid var(--border); background:${i % 2 === 0 ? 'transparent' : 'rgba(255,255,255,0.02)'};">
                                <td style="padding:14px 20px; font-weight:700; color:#fff;">🥅 ${c.nombre}</td>
                                <td style="padding:14px 20px; color:var(--text-muted);">🏟️ ${c._sede_nombre || 'N/A'}</td>
                                <td style="padding:14px 20px;">${c.modalidad || '—'}</td>
                                <td style="padding:14px 20px;">${c.superficie || '—'}</td>
                                <td style="padding:14px 20px;">${c.techada ? '✅ Sí' : '—'}</td>
                            </tr>
                        `).join('')}
                    </tbody>
                </table>
            </div>`;
    }

    filterCanchas() {
        const query = document.getElementById('cancha-search-filter').value.toLowerCase();
        if (!this.canchas) return;

        const filtered = this.canchas.filter(c => 
            c.nombre.toLowerCase().includes(query) || 
            (c.email_encargado && c.email_encargado.toLowerCase().includes(query)) ||
            (c.encargado && c.encargado.toLowerCase().includes(query))
        );
        
        this.renderCanchas(filtered);
    }

    checkLimits() {
        const btn = document.getElementById('btn-nueva-cancha');
        if (!btn) return;
        
        const userRol = (window.USER_ROL || '').toLowerCase();

        // Si el usuario es de solo vista o árbitro, ocultar botón siempre
        if (userRol === 'resultados' || userRol === 'arbitro' || userRol === 'solo vista') {
            btn.style.display = 'none';
            return;
        }

        if (!window.FutAdminLimits || !window.FutAdminCounts) return;
        
        const limit = window.FutAdminLimits.canchas;
        const count = window.FutAdminCounts.canchas || 0;
        
        // Actualizar contador visual
        const counterMain = document.getElementById('venue-counter-main');
        const counterModal = document.getElementById('venue-counter-modal');
        
        const isAdmin = userRol === 'admin' || userRol === 'ejecutivo';
        const displayLimit = isAdmin ? '∞' : limit;
        const counterText = limit !== undefined ? `${count} / ${displayLimit}` : `${count}`;
        if (counterMain) counterMain.innerText = counterText;
        if (counterModal) counterModal.innerText = counterText;

        if (limit !== undefined && count >= limit) {
            btn.style.display = 'none';
        } else {
            btn.style.display = 'inline-block';
        }
    }

    renderCanchas(canchasToRender = null) {
        const container = document.getElementById('canchas-container');
        if (!container) return;

        // Si no se pasa nada, usamos la lista completa guardada
        const list = canchasToRender || this.canchas;

        const userRol = (window.USER_ROL || '').toLowerCase();
        const canCreate = !['resultados', 'arbitro', 'solo vista'].includes(userRol);

        if (list.length === 0) {
            container.innerHTML = `
                <div class="empty-state" style="grid-column: 1/-1; padding: 4rem; text-align: center; background: var(--card-bg); border-radius: 20px; border: 1px dashed var(--border);">
                    <div style="font-size: 3rem; margin-bottom: 1rem;">🏟️</div>
                    <h4>No se encontraron sedes</h4>
                    <p class="text-muted">${canchasToRender ? 'No hay sedes que coincidan con tu búsqueda.' : 'Comienza agregando tu primera sede o complejo deportivo.'}</p>
                    ${canCreate && !canchasToRender ? `
                        <button class="btn-primary" onclick="ui.canchas.showModal()" style="margin-top: 1rem;">+ Nueva Sede</button>
                    ` : ''}
                </div>
            `;
            return;
        }

        container.innerHTML = list.map(c => {
            const hasPhoto = c.foto_url && c.foto_url.trim() !== '';
            return `
            <div class="stat-card premium-card" style="position: relative; display: flex; flex-direction: column; gap: 0; border: 1px solid var(--border); border-radius: 20px; overflow: hidden; background: var(--card-bg); transition: transform 0.3s ease;">
                <div class="combo-indicator" style="background: ${c.color || 'var(--primary)'}; opacity: 0.8;"></div>
                
                ${hasPhoto ? `
                <div style="width: 100%; height: 160px; position: relative; overflow: hidden; border-bottom: 1px solid rgba(255,255,255,0.05);">
                    <img src="${c.foto_url}" style="width: 100%; height: 100%; object-fit: cover;" alt="${c.nombre}" onerror="this.style.display='none'">
                    <div style="position: absolute; inset: 0; background: linear-gradient(to bottom, transparent, rgba(0,0,0,0.5));"></div>
                </div>
                ` : ''}

                <!-- Header Card -->
                <div style="padding: 15px 15px 15px 20px; background: rgba(255,255,255,0.01); display: flex; justify-content: space-between; align-items: start; border-bottom: 1px solid var(--border);">
                    <div>
                        <div style="display: flex; gap: 6px; align-items: center; margin-bottom: 5px;">
                            <span class="badge" style="background: ${this.getTipoColor(c.tipo)}; font-size: 0.65rem; padding: 2px 8px;">${c.tipo}</span>
                            <span class="badge" style="background: rgba(255,255,255,0.05); color: var(--text); font-size: 0.65rem; border: 1px solid var(--border); padding: 2px 8px;">${c.modalidad || 'Fútbol 7'}</span>
                        </div>
                        <h4 style="font-size: 1.25rem; margin: 0; color: #fff; font-weight: 700;">${c.nombre}</h4>
                        <small class="text-muted" style="font-size: 0.75rem;">Afiliado: ${c.fecha_afiliacion || 'N/A'}</small>
                    </div>
                </div>
                <!-- Stats Grid -->
                <div style="display: grid; grid-template-columns: repeat(5, 1fr); gap: 1px; background: var(--border); margin: 0;">
                    <div style="background: var(--card-bg); padding: 10px 2px; text-align: center;">
                        <div style="font-size: 1rem; font-weight: bold; color: var(--primary);">${c.ligas_count || 0}</div>
                        <div style="font-size: 0.5rem; text-transform: uppercase; color: var(--text-muted); white-space: nowrap;">Ligas</div>
                    </div>
                    <div style="background: var(--card-bg); padding: 10px 2px; text-align: center;">
                        <div style="font-size: 1rem; font-weight: bold; color: #fff;">${c.equipos_count || 0}</div>
                        <div style="font-size: 0.5rem; text-transform: uppercase; color: var(--text-muted); white-space: nowrap;">Equipos</div>
                    </div>
                    <div style="background: var(--card-bg); padding: 10px 2px; text-align: center;">
                        <div style="font-size: 1rem; font-weight: bold; color: #00ff88;">${c.partidos_count || 0}</div>
                        <div style="font-size: 0.5rem; text-transform: uppercase; color: var(--text-muted); white-space: nowrap;">Partidos</div>
                    </div>
                    <div style="background: var(--card-bg); padding: 10px 2px; text-align: center;">
                        <div style="font-size: 1rem; font-weight: bold; color: #3b82f6;">${c.jugadores_count || 0}</div>
                        <div style="font-size: 0.5rem; text-transform: uppercase; color: var(--text-muted); white-space: nowrap;">Jugadores</div>
                    </div>
                    <div style="background: var(--card-bg); padding: 10px 2px; text-align: center;">
                        <div style="font-size: 1rem; font-weight: bold; color: #f59e0b;">${(c.arbitros && c.arbitros.length) || 0}</div>
                        <div style="font-size: 0.5rem; text-transform: uppercase; color: var(--text-muted); white-space: nowrap;">Árbitros</div>
                    </div>
                </div>
                
                <!-- Details -->
                <div style="padding: 15px; display: grid; gap: 8px; font-size: 0.85rem; flex: 1;">
                    <div style="display: flex; align-items: center; gap: 8px;">
                        <span style="opacity: 0.7;">👤</span>
                        <span class="text-muted"><strong>${c.encargado || 'N/A'}</strong> ${c.tiene_usuario ? '<span style="color:var(--primary); font-size:0.7rem;">(Cuenta 🔗)</span>' : ''}</span>
                    </div>
                    <div style="display: flex; align-items: start; gap: 8px;">
                        <span style="opacity: 0.7;">📍</span>
                        <div style="overflow: hidden;">
                            <div class="text-muted" style="font-weight: 600; font-size: 0.75rem; color: var(--primary);">${c.municipio || 'N/A'}, ${c.estado || 'N/A'}</div>
                            <div class="text-muted" style="white-space: nowrap; overflow: hidden; text-overflow: ellipsis; font-size: 0.75rem;">${c.direccion || 'Sin dirección'}</div>
                        </div>
                    </div>
                    
                    ${c.arbitros && c.arbitros.length > 0 ? `
                        <div style="margin-top: 5px; padding-top: 8px; border-top: 1px dashed var(--border);">
                            <div style="font-size: 0.7rem; color: var(--text-muted); margin-bottom: 4px; text-transform: uppercase; font-weight: bold;">Árbitros Vinculados:</div>
                            <div style="display: flex; flex-wrap: wrap; gap: 4px;">
                                ${c.arbitros.map(a => `<span style="background: rgba(245, 158, 11, 0.1); color: #f59e0b; border: 1px solid rgba(245, 158, 11, 0.2); padding: 1px 6px; border-radius: 4px; font-size: 0.7rem;">${a}</span>`).join('')}
                            </div>
                        </div>
                    ` : ''}

                    ${c.torneos_asociados && c.torneos_asociados.length > 0 ? `
                        <div style="margin-top: 5px;">
                            <div style="font-size: 0.7rem; color: var(--text-muted); margin-bottom: 4px; text-transform: uppercase; font-weight: bold;">Ligas en casa:</div>
                            <div style="display: flex; flex-wrap: wrap; gap: 4px;">
                                ${c.torneos_asociados.map(t => `<span style="background: rgba(255,255,255,0.05); border: 1px solid var(--border); padding: 1px 6px; border-radius: 4px; font-size: 0.7rem;">${t}</span>`).join('')}
                            </div>
                        </div>
                    ` : ''}

                    ${c.usuarios && c.usuarios.length > 0 ? `
                        <div style="margin-top: 10px; padding-top: 8px; border-top: 1px solid rgba(255,255,255,0.05);">
                            <div style="font-size: 0.7rem; color: var(--text-muted); margin-bottom: 6px; text-transform: uppercase; font-weight: bold;">Cuentas con Acceso:</div>
                            <div style="display: flex; flex-direction: column; gap: 4px;">
                                ${c.usuarios.map(u => {
                                    const icons =    { 'dueno_cancha': '🏠', 'arbitro': '⚖️', 'dueño_liga': '👑', 'entrenador': '📋', 'super_arbitro': '🚀', 'equipo': '🛡️', 'resultados': '📊', 'admin': '⭐', 'ejecutivo': '💼' };
                                    const rolColors = {
                                        'dueno_cancha':  { bg: 'rgba(0,255,136,0.08)',  border: 'rgba(0,255,136,0.25)',  text: '#00ff88' },
                                        'dueño_liga':    { bg: 'rgba(255,215,0,0.08)',  border: 'rgba(255,215,0,0.25)',  text: '#ffd700' },
                                        'arbitro':       { bg: 'rgba(245,158,11,0.08)', border: 'rgba(245,158,11,0.25)', text: '#f59e0b' },
                                        'super_arbitro': { bg: 'rgba(251,146,60,0.08)', border: 'rgba(251,146,60,0.25)', text: '#fb923c' },
                                        'entrenador':    { bg: 'rgba(59,130,246,0.08)', border: 'rgba(59,130,246,0.25)', text: '#3b82f6' },
                                        'equipo':        { bg: 'rgba(167,139,250,0.08)', border: 'rgba(167,139,250,0.25)', text: '#a78bfa' },
                                        'resultados':    { bg: 'rgba(100,116,139,0.08)', border: 'rgba(100,116,139,0.25)', text: '#94a3b8' },
                                        'admin':         { bg: 'rgba(236,72,153,0.08)', border: 'rgba(236,72,153,0.25)', text: '#ec4899' },
                                        'ejecutivo':     { bg: 'rgba(20,184,166,0.08)', border: 'rgba(20,184,166,0.25)', text: '#14b8a6' },
                                    };
                                    const clr = rolColors[u.rol] || { bg: 'rgba(255,255,255,0.03)', border: 'rgba(255,255,255,0.08)', text: '#aaa' };
                                    return `
                                        <div style="display: flex; align-items: center; justify-content: space-between; padding: 4px 8px; background: ${clr.bg}; border-radius: 6px; border: 1px solid ${clr.border};">
                                            <span style="font-size: 0.75rem; color: ${clr.text}; font-weight: 600;">${u.nombre}</span>
                                            <span style="font-size: 0.8rem; padding: 1px 4px;">${icons[u.rol] || '👤'}</span>
                                        </div>
                                    `;
                                }).join('')}
                            </div>
                        </div>
                    ` : ''}
                </div>

                <div class="card-footer" onclick="event.stopPropagation()" style="display: flex; flex-direction: column; gap: 10px; padding: 15px; border-top: 1px solid rgba(255,255,255,0.05);">
                    ${window.USER_ROL !== 'resultados' && window.USER_ROL !== 'arbitro' ? `
                    <div style="display: flex; flex-direction: column; gap: 8px; width: 100%;">
                        <button onclick="ui.canchas.goToLeagues('${c.nombre}')" style="width: 100%; padding: 10px; background: rgba(59,130,246,0.1); color: #3b82f6; border: 1px solid rgba(59,130,246,0.2); border-radius: 12px; font-weight: 600; cursor: pointer; display: flex; align-items: center; justify-content: center; gap: 8px;">
                            <span>🏆</span> Ir a Ligas
                        </button>
                        <div style="display: flex; gap: 8px;">
                            <button onclick="ui.canchas.showModal(${c.id})" style="flex: 1; padding: 10px; background: rgba(0,255,136,0.1); color: #00ff88; border: 1px solid rgba(0,255,136,0.2); border-radius: 12px; font-weight: 600; cursor: pointer;">✏️ Editar</button>
                            <button onclick="ui.canchas.deleteCancha(${c.id})" style="width: 45px; background: rgba(255,68,68,0.1); color: #ff4444; border: 1px solid rgba(255,68,68,0.2); border-radius: 12px; cursor: pointer;">🗑️</button>
                        </div>
                    </div>
                    ` : `
                    <button onclick="ui.canchas.goToLeagues('${c.nombre}')" style="width: 100%; padding: 10px; background: rgba(59,130,246,0.1); color: #3b82f6; border: 1px solid rgba(59,130,246,0.2); border-radius: 12px; font-weight: 600; cursor: pointer;">🏆 Ir a Ligas</button>
                    `}
                </div>
            </div>
            `;
        }).join('');

        if (this.pagination && this.pagination.total_pages > 1) {
            container.innerHTML += `
                <div class="pagination-controls">
                    <button class="btn-pagination" ${!this.pagination.has_prev ? 'disabled' : ''} 
                        onclick="ui.canchas.loadCanchas(${this.pagination.page - 1})">
                        &laquo; Anterior
                    </button>
                    <span class="pagination-info">Página ${this.pagination.page} de ${this.pagination.total_pages}</span>
                    <button class="btn-pagination" ${!this.pagination.has_next ? 'disabled' : ''} 
                        onclick="ui.canchas.loadCanchas(${this.pagination.page + 1})">
                        Siguiente &raquo;
                    </button>
                </div>
            `;
        }
    }

    goToLeagues(canchaNombre) {
        const torneosNav = document.querySelector('.nav-item[data-view="torneos"]');
        // Cambiar a la vista 'torneos' y directamente a la pestaña 'torneos-lista'
        this.ui.switchView('torneos', 'torneos-lista', torneosNav);
        
        // Esperar un momento a que la vista se cargue y aplicar el filtro
        setTimeout(() => {
            if (this.ui.leagues) {
                this.ui.leagues.loadLeagues(canchaNombre);
            }
        }, 150);
    }

    getTipoColor(tipo) {
        switch (tipo) {
            case 'Propia': return 'var(--primary)';
            case 'Rentada': return '#f59e0b';
            case 'Gratuita': return '#10b981';
            default: return '#6b7280';
        }
    }

    switchModalTab(tabId, btn) {
        // Remover clases activas
        const modal = btn.closest('.modal');
        modal.querySelectorAll('.modal-tab').forEach(b => b.classList.remove('active'));
        modal.querySelectorAll('.modal-tab-content').forEach(c => c.classList.remove('active'));
        
        // Activar seleccionada
        btn.classList.add('active');
        document.getElementById(`cancha-tab-${tabId}`).classList.add('active');
    }

    toggleCostoField() {
        const tipo = document.getElementById('cancha-tipo').value;
        const container = document.getElementById('container-costo-cancha');
        if (tipo === 'Gratuita') {
            container.classList.add('hidden');
            document.getElementById('cancha-costo').value = 0;
        } else {
            container.classList.remove('hidden');
        }
    }

    initGeoSelectors() {
        const estadoSelect = document.getElementById('cancha-estado');
        if (!estadoSelect || estadoSelect.options.length > 1) return; // Ya inicializado
        
        const estados = Object.keys(window.MEXICO_GEO || {}).sort();
        estados.forEach(e => {
            const opt = document.createElement('option');
            opt.value = e;
            opt.textContent = e;
            estadoSelect.appendChild(opt);
        });
    }

    handleEstadoChange(selectedMunicipio = null) {
        const estadoSelect = document.getElementById('cancha-estado');
        const municipioSelect = document.getElementById('cancha-municipio');
        const estado = estadoSelect.value;
        
        municipioSelect.innerHTML = '<option value="">Selecciona Municipio...</option>';
        municipioSelect.disabled = !estado;

        if (estado && window.MEXICO_GEO[estado]) {
            const municipios = window.MEXICO_GEO[estado].sort();
            municipios.forEach(m => {
                const opt = document.createElement('option');
                opt.value = m;
                opt.textContent = m;
                municipioSelect.appendChild(opt);
            });
            
            if (selectedMunicipio) {
                municipioSelect.value = selectedMunicipio;
            }
        }
    }

    loadRulesTemplate() {
        const template = `📝 REGLAMENTO INTERNO - SEDE PRODUCTIVA

1. EQUIPAMIENTO:
- Uso obligatorio de calzado adecuado (tachones de goma o multitacos).
- Prohibido el uso de tacos de aluminio.
- Uso obligatorio de espinilleras durante los partidos.

2. COMPORTAMIENTO:
- Respeto total al cuerpo arbitral y personal de la sede.
- Prohibido el consumo de bebidas alcohólicas y tabaco en las áreas de juego.
- Cualquier riña o agresión resultará en expulsión inmediata de la sede.

3. PAGOS Y RESERVAS:
- Los pagos deben liquidarse antes del inicio del encuentro.
- Tolerancia máxima de espera: 10 minutos.

4. INSTALACIONES:
- Mantener las áreas comunes limpias.
- No se permite el ingreso de mascotas al terreno de juego.

"El deporte es salud y sana convivencia."`;
        
        const textarea = document.getElementById('cancha-notas');
        if (textarea.value.trim() && !confirm('¿Deseas reemplazar el contenido actual con la plantilla base?')) return;
        
        textarea.value = template;
        Core.showNotification('Plantilla cargada con éxito');
    }

    showModalCampo() {
        if (!this.canchas || this.canchas.length === 0) {
            alert('Aún no tienes Sedes registradas. Primero crea una Sede (Predio) en la pestaña "Sedes".');
            return;
        }

        const sedeSelect = document.getElementById('campo-sede-id');
        if (sedeSelect) {
            sedeSelect.innerHTML = '<option value="">-- Selecciona una Sede --</option>' + 
                this.canchas.map(sede => `<option value="${sede.id}">${sede.nombre}</option>`).join('');
        }

        const form = document.getElementById('campo-form');
        if (form) form.reset();
        
        document.getElementById('campo-id').value = '';
        document.getElementById('campo-modal-title').innerText = '🥅 Nuevo Campo de Juego';

        Core.openModal('modal-campo');
    }

    async handleCampoSubmit(e) {
        e.preventDefault();
        const sedeId = document.getElementById('campo-sede-id').value;
        const nombre = document.getElementById('campo-nombre').value;
        const modalidad = document.getElementById('campo-modalidad').value;
        const superficie = document.getElementById('campo-superficie').value;
        const techada = document.getElementById('campo-techada').checked;
        const capacidad = document.getElementById('campo-capacidad').value;
        const notas = document.getElementById('campo-notas').value;

        if (!sedeId) {
            Core.showNotification('Debes seleccionar una Sede', 'error');
            return;
        }

        const data = {
            nombre,
            modalidad,
            superficie,
            techada,
            capacidad_espectadores: parseInt(capacidad) || 0,
            notas
        };

        const btn = e.target.querySelector('button[type="submit"]');
        if (btn) btn.disabled = true;

        try {
            const result = await Core.fetchAPI(`/api/canchas/${sedeId}/campos`, {
                method: 'POST',
                body: JSON.stringify(data)
            });

            if (result.error) {
                Core.showNotification(result.error, 'error');
            } else {
                Core.showNotification('Campo guardado exitosamente', 'success');
                Core.closeModal('modal-campo');
                // Recargar según la vista activa
                if (document.getElementById('view-campos') && document.getElementById('view-campos').style.display !== 'none') {
                    await this.loadCampos();
                } else {
                    await this.loadCanchas();
                }
            }
        } catch (error) {
            Core.showNotification('Error al guardar el campo (Límite o Falla de Red)', 'error');
        } finally {
            if (btn) btn.disabled = false;
        }
    }

    showModal(canchaId = null, ligaId = null) {
        if (!canchaId) {
            // Bloqueo de seguridad: No permitir abrir si ya se alcanzó el límite
            const userRol = String(window.USER_ROL || '').toLowerCase().replace('ñ', 'n');
            const limits = window.FutAdminLimits || {};
            const final_limit = limits.canchas || limits.canchas_per_cancha; // Fallback
            const count = window.FutAdminCounts.canchas || 0;
            const isAdminByRol = userRol === 'admin' || userRol === 'ejecutivo';

            if (!isAdminByRol && final_limit !== undefined && count >= final_limit) {
                alert(`Límite alcanzado: Tu plan solo permite ${final_limit} sede(s). Contacta a soporte para expandir tu plan.`);
                return;
            }
        }
        
        // Toggle de permisos admin para límite de campos en la sede
        const userRolFallback = String(window.USER_ROL || '').toLowerCase().replace('ñ', 'n');
        const isAdminForUI = userRolFallback === 'admin' || userRolFallback === 'ejecutivo';
        
        const adminContainer = document.getElementById('admin-limite-campos-container');
        if (adminContainer) {
            adminContainer.style.display = isAdminForUI ? 'flex' : 'none';
        }
        
        const form = document.getElementById('cancha-form');
        form.reset();
        document.getElementById('cancha-id').value = '';
        document.getElementById('cancha-liga-id').value = (ligaId === 'global' || !ligaId) ? '' : ligaId;
        document.getElementById('cancha-modal-title').innerText = canchaId ? '🏟️ Editar Sede' : '🏟️ Nueva Sede';

        // Reset Tabs
        const firstTab = document.querySelector('#modal-cancha .modal-tab');
        if (firstTab) this.switchModalTab('general', firstTab);

        this.initGeoSelectors();

        if (canchaId) {
            const c = this.canchas.find(x => x.id === canchaId);
            if (c) {
                document.getElementById('cancha-id').value = c.id;
                document.getElementById('cancha-nombre').value = c.nombre;
                document.getElementById('cancha-encargado').value = c.encargado;
                document.getElementById('cancha-email').value = c.email_encargado || '';
                document.getElementById('cancha-telefono').value = c.telefono_encargado;
                document.getElementById('cancha-tipo').value = c.tipo;
                document.getElementById('cancha-modalidad').value = c.modalidad || 'Fútbol 7';
                document.getElementById('cancha-costo').value = c.costo_renta;
                document.getElementById('cancha-unidad-cobro').value = c.unidad_cobro || 'Partido';
                document.getElementById('cancha-direccion').value = c.direccion;
                
                // Geolocalización
                document.getElementById('cancha-estado').value = c.estado || '';
                this.handleEstadoChange(c.municipio);
                
                document.getElementById('cancha-notas').value = c.notas;
                document.getElementById('cancha-foto').value = c.foto_url || '';
                
                if (isAdminForUI && document.getElementById('cancha-limite-campos')) {
                    document.getElementById('cancha-limite-campos').value = c.limite_campos || 1;
                }
            }
        } else {
            document.getElementById('cancha-estado').value = '';
            if (isAdminForUI && document.getElementById('cancha-limite-campos')) {
                document.getElementById('cancha-limite-campos').value = 1;
            }
            this.handleEstadoChange();
        }

        this.toggleCostoField();
        Core.openModal('modal-cancha');
    }


    async handleCanchaSubmit(e) {
        e.preventDefault();
        const id = document.getElementById('cancha-id').value;
        const data = {
            nombre: document.getElementById('cancha-nombre').value,
            encargado: document.getElementById('cancha-encargado').value,
            email_encargado: document.getElementById('cancha-email').value,
            telefono_encargado: document.getElementById('cancha-telefono').value,
            tipo: document.getElementById('cancha-tipo').value,
            modalidad: document.getElementById('cancha-modalidad').value,
            costo_renta: parseFloat(document.getElementById('cancha-costo').value || 0),
            unidad_cobro: document.getElementById('cancha-unidad-cobro').value,
            direccion: document.getElementById('cancha-direccion').value,
            estado: document.getElementById('cancha-estado').value,
            municipio: document.getElementById('cancha-municipio').value,
            notas: document.getElementById('cancha-notas').value,
            foto_url: document.getElementById('cancha-foto').value,
            liga_id: document.getElementById('cancha-liga-id').value || null
        };

        const userRol = String(window.USER_ROL || '').toLowerCase().replace('ñ', 'n');
        if (userRol === 'admin' || userRol === 'ejecutivo') {
            const limiteEl = document.getElementById('cancha-limite-campos');
            if (limiteEl && limiteEl.value) {
                data.limite_campos = parseInt(limiteEl.value, 10);
            }
        }

        const method = id ? 'PUT' : 'POST';
        const url = id ? `/api/canchas/${id}` : '/api/canchas';

        try {
            const response = await fetch(url, {
                method: method,
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(data)
            });

            if (response.ok) {
                Core.showNotification(id ? 'Sede actualizada con éxito' : 'Sede registrada con éxito');
                Core.closeModal('modal-cancha');
                await this.ui.loadInitialStats();
                this.loadCanchas();
            } else {
                throw new Error('Server error');
            }
        } catch (e) {
            console.error('Save error:', e);
            Core.showNotification('Error al guardar la sede', 'error');
        }
    }

    async deleteCancha(id) {
        if (!confirm('¿Estás seguro de eliminar esta sede?')) return;
        try {
            const response = await fetch(`/api/canchas/${id}`, { method: 'DELETE' });
            if (response.ok) {
                Core.showNotification('Sede eliminada');
                await this.ui.loadInitialStats();
                this.loadCanchas();
            } else {
                throw new Error('Delete error');
            }
        } catch (e) {
            Core.showNotification('No se pudo eliminar la sede', 'error');
        }
    }
}
