import { Core } from './core.js';

export class FinanceModule {
    constructor(ui) {
        this.ui = ui;
        this.allInscripciones = [];
        this.allArbitrajes = [];
    }

    async populateInscripcionLeagueSelect() {
        try {
            const response = await Core.fetchAPI('/api/torneos');
            const torneos = response.items || response;
            const select = document.getElementById('report-league-id');
            if (select) {
                select.innerHTML = '<option value="">Seleccionar Liga...</option>' +
                    (Array.isArray(torneos) ? torneos.map(t => `<option value="${t.id}">${t.nombre}</option>`).join('') : '');
            }
            // The original target was 'inscripciones-league-filter'.
            // Keeping the original target as well, assuming the user wants to add 'report-league-id' but not remove the original functionality.
            // If the intention was to replace, the original line should be removed.
            // Given the instruction, I'm interpreting it as adding the new target.
            const originalSelect = document.getElementById('inscripciones-league-filter');
            if (originalSelect) {
                originalSelect.innerHTML = '<option value="">Seleccionar Liga...</option>' +
                    (Array.isArray(torneos) ? torneos.map(t => `<option value="${t.id}">${t.nombre}</option>`).join('') : '');
            }
        } catch (error) {
            console.error('Error al cargar ligas para inscripciones:', error);
        }
    }

    async populateArbitrajeLeagueSelect() {
        try {
            const response = await Core.fetchAPI('/api/torneos');
            const torneos = response.items || response;
            const select = document.getElementById('arbitrajes-league-filter');
            if (!select) return;
            select.innerHTML = '<option value="">Seleccionar Liga...</option>' +
                (Array.isArray(torneos) ? torneos.map(t => `<option value="${t.id}">${t.nombre}</option>`).join('') : '');
        } catch (error) {
            console.error('Error al cargar ligas para arbitrajes:', error);
        }
    }

    async changePage(type, page) {
        if (page < 1 || (this.pagination && page > this.pagination.total_pages)) return;
        if (type === 'arbitraje') {
            this.loadArbitrajes(page);
        } else {
            this.loadInscripciones(page);
        }
        window.scrollTo({ top: 0, behavior: 'smooth' });
    }

    async loadArbitrajes(page = 1) {
        const torneoId = document.getElementById('arbitrajes-league-filter').value;
        const container = document.getElementById('arbitrajes-container');
        if (!container) return;
        if (!torneoId) {
            container.innerHTML = '<p class="text-muted">Selecciona una liga para gestionar aportaciones de arbitraje.</p>';
            return;
        }
        if (page === 1) container.innerHTML = '<p>Cargando estados de arbitraje...</p>';
        try {
            const response = await Core.fetchAPI(`/api/inscripciones?torneo_id=${torneoId}&page=${page}`);
            const inscritos = response.items || response;
            this.pagination = response.pagination || null;

            if (!inscritos.length) {
                container.innerHTML = '<p>No hay equipos registrados en este torneo para arbitraje.</p>';
                return;
            }

            let html = `
                <div style="grid-column: 1 / -1; width: 100%; overflow-x: auto; background: var(--card); border-radius: 12px; border: 1px solid var(--border);">
                    <table style="width: 100%; border-collapse: collapse; text-align: left;">
                        <thead>
                            <tr style="background: rgba(0,0,0,0.3); border-bottom: 2px solid var(--border);">
                                <th style="padding: 12px 14px; color: var(--text-muted); font-size: 0.72rem; font-weight: 700; text-transform: uppercase;">Equipo</th>
                                <th style="padding: 12px 14px; color: var(--text-muted); font-size: 0.72rem; font-weight: 700; text-transform: uppercase; text-align: center;">⚽ Jugados</th>
                                <th style="padding: 12px 14px; color: var(--text-muted); font-size: 0.72rem; font-weight: 700; text-transform: uppercase;">Aportación/Jgo</th>
                                <th style="padding: 12px 14px; color: var(--text-muted); font-size: 0.72rem; font-weight: 700; text-transform: uppercase;">Meta</th>
                                <th style="padding: 12px 14px; color: var(--text-muted); font-size: 0.72rem; font-weight: 700; text-transform: uppercase;">Aportado</th>
                                <th style="padding: 12px 14px; color: var(--text-muted); font-size: 0.72rem; font-weight: 700; text-transform: uppercase;">Pendiente</th>
                                <th style="padding: 12px 14px; color: var(--text-muted); font-size: 0.72rem; font-weight: 700; text-transform: uppercase;">Avance</th>
                                <th style="padding: 12px 14px; color: var(--text-muted); font-size: 0.72rem; font-weight: 700; text-transform: uppercase; text-align: right;">Acciones</th>
                            </tr>
                        </thead>
                        <tbody>
            `;

            html += inscritos.map((ins, index) => {
                const esperado = Number(ins.esperado_arbitraje || 0);
                const pagado = Number(ins.pagado_arbitraje || 0);
                const saldo = Number(ins.saldo_arbitraje ?? (esperado - pagado));
                const tarifa = Number(ins.tarifa_arbitraje || 0);
                const jugados = ins.partidos_jugados || 0;
                const colorSaldo = saldo > 0 ? '#ffae00' : '#00ff88';
                const pct = esperado > 0 ? Math.min(100, Math.round((pagado / esperado) * 100)) : (pagado > 0 ? 100 : 0);
                const barColor = pct === 100 ? '#00ff88' : pct > 50 ? '#ffae00' : '#ff4d4d';
                const bgRow = index % 2 === 0 ? 'transparent' : 'rgba(255,255,255,0.02)';

                // Sub-tabla de detalles de jornadas
                let detallesHtml = '';
                if (ins.detalle_partidos && ins.detalle_partidos.length > 0) {
                    detallesHtml = `
                    <div style="padding: 15px; background: rgba(0,0,0,0.5); border-radius: 8px; margin-top: 5px;">
                        <h4 style="margin: 0 0 10px 0; font-size: 0.9rem; color: var(--primary);">Desglose por Jornada</h4>
                        <table style="width: 100%; border-collapse: collapse; font-size: 0.8rem;">
                            <thead>
                                <tr style="border-bottom: 1px solid rgba(255,255,255,0.1);">
                                    <th style="padding: 8px; text-align: left; color: #aaa;">Jor</th>
                                    <th style="padding: 8px; text-align: left; color: #aaa;">Rival</th>
                                    <th style="padding: 8px; text-align: left; color: #aaa;">Estado</th>
                                    <th style="padding: 8px; text-align: right; color: #aaa;">Aportación</th>
                                    <th style="padding: 8px; text-align: right; color: #aaa;">Aportado</th>
                                    <th style="padding: 8px; text-align: right; color: #aaa;">Pendiente</th>
                                </tr>
                            </thead>
                            <tbody>
                                ${ins.detalle_partidos.map(dp => {
                        const estadoColor = dp.estado === 'Played' ? '#00ff88' : (dp.estado === 'Live' ? '#ffae00' : '#aaa');
                        const estadoText = dp.estado === 'Played' || dp.estado === 'Jugado' ? 'Jugado' : (dp.estado === 'Live' || dp.estado === 'En Vivo' ? 'En Vivo' : 'Pendiente');
                        const abonadoColor = dp.pagado >= dp.tarifa ? '#00ff88' : (dp.pagado > 0 ? '#ffae00' : '#fff');
                        const saldoColor = dp.saldo > 0 ? '#ff4d4d' : '#00ff88';

                        return `
                                    <tr style="border-bottom: 1px solid rgba(255,255,255,0.05);">
                                        <td style="padding: 8px;">J${dp.jornada}</td>
                                        <td style="padding: 8px; font-weight: bold;">${dp.rival}</td>
                                        <td style="padding: 8px;"><span style="color: ${estadoColor}; font-size: 0.75rem; border: 1px solid ${estadoColor}; padding: 2px 6px; border-radius: 4px;">${estadoText}</span></td>
                                        <td style="padding: 8px; text-align: right;">$${dp.tarifa.toFixed(2)}</td>
                                        <td style="padding: 8px; text-align: right; color: ${abonadoColor};">$${dp.pagado.toFixed(2)}</td>
                                        <td style="padding: 8px; text-align: right; font-weight: bold; color: ${saldoColor};">$${dp.saldo.toFixed(2)}</td>
                                    </tr>`;
                    }).join('')}
                            </tbody>
                        </table>
                    </div>`;
                } else {
                    detallesHtml = `<div style="padding: 15px; color: #aaa; text-align: center;">No hay jornadas programadas aún.</div>`;
                }

                return `
                <tr style="border-bottom:1px solid rgba(255,255,255,0.05); background:${bgRow}; transition:background 0.2s; border-left:3px solid ${colorSaldo}; cursor: pointer;" 
                    onmouseover="this.style.background='rgba(255,255,255,0.06)'" 
                    onmouseout="this.style.background='${bgRow}'"
                    onclick="ui.finance.toggleDetalle('detalles-${ins.id}')">
                    <td style="padding:10px 14px;">
                        <span style="font-weight:700; font-size:0.9rem; color:#fff; display:flex; align-items:center; gap:6px;">
                            <span id="icon-detalles-${ins.id}" style="font-size: 0.7rem; transition: transform 0.2s;">▶</span>
                            ${ins.equipo_nombre}
                        </span>
                    </td>
                    <td style="padding:10px 14px; text-align:center;">
                        <span style="font-size:1.1rem; font-weight:800; color:#fff;">${jugados}</span>
                        <span style="font-size:0.65rem; color:var(--text-muted); display:block;">partidos</span>
                    </td>
                    <td style="padding:10px 14px;"><span style="color:var(--text-muted); font-size:0.85rem;">$${tarifa.toFixed(2)}</span></td>
                    <td style="padding:10px 14px;"><span style="color:#fff; font-size:0.85rem; font-weight:600;">$${esperado.toFixed(2)}</span></td>
                    <td style="padding:10px 14px;"><span style="color:#00ff88; font-size:0.85rem; font-weight:700;">$${pagado.toFixed(2)}</span></td>
                    <td style="padding:10px 14px;"><strong style="color:${colorSaldo}; font-size:0.95rem;">${saldo > 0 ? '-' : ''}$${Math.abs(saldo).toFixed(2)}</strong></td>
                    <td style="padding:10px 14px; min-width:90px;">
                        <div style="background:rgba(255,255,255,0.1); border-radius:999px; height:5px; overflow:hidden;">
                            <div style="width:${pct}%; height:100%; background:${barColor}; border-radius:999px;"></div>
                        </div>
                        <span style="font-size:0.65rem; color:var(--text-muted); display:block; margin-top:2px;">${pct}% cubierto</span>
                    </td>
                    <td style="padding:10px 14px; text-align:right;" onclick="event.stopPropagation();">
                        <div style="display:flex; gap:4px; justify-content:flex-end;">
                            ${['admin', 'ejecutivo', 'dueño_liga', 'super_arbitro', 'equipo'].includes(window.USER_ROL) ? `
                                <button onclick="ui.finance.promptEditInscripcion(${ins.id}, '${ins.equipo_nombre}', ${ins.monto_pactado || 0})" class="btn-secondary" style="font-size:0.7rem; padding:4px 8px; border-radius:4px;" title="Editar">&#x270F;&#xFE0F;</button>
                                <button onclick="ui.finance.promptBecarInscripcion(${ins.id}, '${ins.equipo_nombre}', ${torneoId})" class="btn-secondary" style="font-size:0.7rem; padding:4px 8px; border-radius:4px;" title="Becar">🎓</button>
                            ` : ''}
                            <button onclick="ui.finance.showAndPrintHistoryReport(${ins.id}, ${torneoId})" class="btn-secondary" style="font-size:0.7rem; padding:4px 8px; border-radius:4px;" title="Imprimir">🖨️</button>
                            ${['admin', 'ejecutivo', 'dueño_liga', 'super_arbitro', 'equipo'].includes(window.USER_ROL) ? `
                                <button onclick="ui.finance.showPagoModal(${ins.id}, '${ins.equipo_nombre}', 'Arbitraje', ${ins.equipo_id})" class="btn-primary" style="font-size:0.7rem; font-weight:700; padding:4px 10px; border-radius:4px; display:inline-flex; align-items:center; gap:4px; margin-left:4px;">
                                    <span>+</span> DONACIÓN
                                </button>
                            ` : ''}
                        </div>
                    </td>
                </tr>
                <tr id="detalles-${ins.id}" style="display:none; background: rgba(0,0,0,0.2);">
                    <td colspan="8" style="padding: 10px 14px;">
                        ${detallesHtml}
                    </td>
                </tr>
                `;
            }).join('');

            html += `
                        </tbody>
                    </table>
                </div>
            `;

            // Agregar Controles de Paginación
            if (this.pagination && this.pagination.total_pages > 1) {
                html += `
                    <div class="pagination-controls" style="grid-column: 1 / -1; width: 100%;">
                        <button class="btn-pagination" ${!this.pagination.has_prev ? 'disabled' : ''} 
                                onclick="ui.finance.changePage('arbitraje', ${this.pagination.page - 1})">
                            &laquo; Anterior
                        </button>
                        <span class="pagination-info">Página ${this.pagination.page} de ${this.pagination.total_pages}</span>
                        <button class="btn-pagination" ${!this.pagination.has_next ? 'disabled' : ''} 
                                onclick="ui.finance.changePage('arbitraje', ${this.pagination.page + 1})">
                            Siguiente &raquo;
                        </button>
                    </div>
                `;
            }

            container.innerHTML = html;
        } catch (error) {
            container.innerHTML = '<p class="error">Error al cargar datos de arbitraje.</p>';
        }
    }

    async loadInscripciones(page = 1) {
        const torneoId = document.getElementById('inscripciones-league-filter').value;
        const container = document.getElementById('inscripciones-container');
        if (!container) return;
        if (!torneoId) {
            container.innerHTML = '<p class="text-muted">Selecciona una liga para gestionar sus inscripciones.</p>';
            return;
        }
        if (page === 1) container.innerHTML = '<p>Cargando inscripciones...</p>';
        try {
            const response = await Core.fetchAPI(`/api/inscripciones?torneo_id=${torneoId}&page=${page}`);
            this.allInscripciones = response.items || response;
            this.pagination = response.pagination || null;
            this.renderInscripcionesTable();
        } catch (error) {
            console.error('Error:', error);
            container.innerHTML = '<p class="error">Error al cargar inscripciones.</p>';
        }
    }

    renderInscripcionesTable() {
        const container = document.getElementById('inscripciones-container');
        const summaryContainer = document.getElementById('inscripciones-summary');
        const statusFilter = document.getElementById('inscripciones-status-filter')?.value || 'all';

        if (!container) return;

        let filtered = this.allInscripciones;
        if (statusFilter === 'pending') {
            filtered = this.allInscripciones.filter(ins => ins.saldo_inscripcion > 0);
        } else if (statusFilter === 'settled') {
            filtered = this.allInscripciones.filter(ins => ins.saldo_inscripcion <= 0);
        }

        // Calcular Totales Rápidos
        const totalPactado = filtered.reduce((s, i) => s + (i.monto_pactado || 0), 0);
        const totalDonado = filtered.reduce((s, i) => s + (i.pagado_inscripcion || 0), 0);
        const totalPendiente = filtered.reduce((s, i) => s + (i.saldo_inscripcion || 0), 0);

        if (summaryContainer) {
            summaryContainer.style.display = 'grid';
            summaryContainer.innerHTML = `
                <div class="stat-card">
                    <div class="stat-label">Equipos Filtrados</div>
                    <div class="stat-value" style="color: var(--primary);">${filtered.length}</div>
                </div>
                <div class="stat-card">
                    <div class="stat-label">Total Pactado</div>
                    <div class="stat-value" style="color: #fff;">$${totalPactado.toFixed(2)}</div>
                </div>
                <div class="stat-card">
                    <div class="stat-label">Total Donado</div>
                    <div class="stat-value" style="color: #00ff88;">$${totalDonado.toFixed(2)}</div>
                </div>
                <div class="stat-card" style="border-left: 4px solid #ff4444;">
                    <div class="stat-label">Donación Pendiente Total</div>
                    <div class="stat-value" style="color: #ff4444;">$${totalPendiente.toFixed(2)}</div>
                </div>
            `;
        }

        if (!filtered.length) {
            container.innerHTML = `<div class="stat-card" style="text-align: center; padding: 2rem; grid-column: 1 / -1;">
                <p class="text-muted">No hay inscripciones que coincidan con el filtro "${statusFilter}".</p>
            </div>`;
            return;
        }

        let html = `
                <div style="grid-column: 1 / -1; width: 100%; overflow-x: auto; background: var(--card); border-radius: 12px; border: 1px solid var(--border);">
                    <table style="width: 100%; border-collapse: collapse; text-align: left;">
                        <thead>
                            <tr style="background: rgba(0,0,0,0.3); border-bottom: 2px solid var(--border);">
                                <th style="padding: 14px 20px; color: var(--text-muted); font-size: 0.75rem; font-weight: 700; text-transform: uppercase;">Equipo</th>
                                <th style="padding: 14px 20px; color: var(--text-muted); font-size: 0.75rem; font-weight: 700; text-transform: uppercase;">Aportación Pactada</th>
                                <th style="padding: 14px 20px; color: var(--text-muted); font-size: 0.75rem; font-weight: 700; text-transform: uppercase;">Total Donado</th>
                                <th style="padding: 14px 20px; color: var(--text-muted); font-size: 0.75rem; font-weight: 700; text-transform: uppercase;">Donación Pendiente</th>
                                <th style="padding: 14px 20px; color: var(--text-muted); font-size: 0.75rem; font-weight: 700; text-transform: uppercase;">Donaciones</th>
                                <th style="padding: 14px 20px; color: var(--text-muted); font-size: 0.75rem; font-weight: 700; text-transform: uppercase; text-align: right;">Acciones</th>
                            </tr>
                        </thead>
                        <tbody>
                  `;
            html += filtered.map((ins, index) => {
            const colorSaldo = ins.saldo_inscripcion > 0 ? '#ffae00' : '#00ff88';

            let abonosHtml = '<span style="font-size: 0.7rem; color: var(--text-muted); font-style: italic;">Sin donaciones</span>';
            if (ins.historial_pagos && ins.historial_pagos.length > 0) {
                abonosHtml = '<div style="max-height: 50px; overflow-y: auto; font-size: 0.7rem;" class="custom-scrollbar">' +
                    ins.historial_pagos.map(p => `
                        <div style="display: flex; justify-content: space-between; gap: 10px; border-bottom: 1px solid rgba(255,255,255,0.05); padding-bottom: 2px; margin-bottom: 2px;">
                            <span style="color: var(--text-muted);">${p.fecha.substring(0, 10)}</span>
                            <span style="color: #fff;">$${p.monto.toFixed(2)}</span>
                        </div>
                    `).join('') +
                    '</div>';
            }

            const torneoId = document.getElementById('inscripciones-league-filter').value;

            return `
                        <tr style="border-bottom: 1px solid rgba(255,255,255,0.05); background: ${index % 2 === 0 ? 'transparent' : 'rgba(255,255,255,0.02)'}; transition: background 0.2s; border-left: 3px solid ${colorSaldo};"
                            onmouseover="this.style.background='rgba(255,255,255,0.06)'"
                            onmouseout="this.style.background='${index % 2 === 0 ? 'transparent' : 'rgba(255,255,255,0.02)'}'">

                            <td style="padding: 12px 20px;">
                                <span style="font-weight: 700; font-size: 0.95rem; color: #fff;">${ins.equipo_nombre}</span>
                            </td>
                            <td style="padding: 12px 20px;">
                                <span style="color: #fff; font-size: 0.9rem;">$${ins.monto_pactado.toFixed(2)}</span>
                            </td>
                            <td style="padding: 12px 20px;">
                                <span style="color: #00ff88; font-size: 0.9rem; font-weight: bold;">$${ins.pagado_inscripcion.toFixed(2)}</span>
                            </td>
                            <td style="padding: 12px 20px;">
                                <strong style="color: ${colorSaldo}; font-size: 1.05rem;">$${ins.saldo_inscripcion.toFixed(2)}</strong>
                            </td>
                            <td style="padding: 8px 20px; min-width: 150px;">
                                ${abonosHtml}
                            </td>
                            <td style="padding: 12px 20px; text-align: right;">
                                <div style="display: flex; gap: 4px; justify-content: flex-end;">
                                    ${['admin', 'ejecutivo', 'dueño_liga', 'super_arbitro', 'equipo'].includes(window.USER_ROL) ? `
                                        <button onclick="ui.finance.promptEditInscripcion(${ins.id}, '${ins.equipo_nombre}', ${ins.monto_pactado || 0})" class="btn-secondary" style="font-size: 0.7rem; padding: 4px 8px; border-radius: 4px;" title="Editar Donación">✏️</button>
                                        <button onclick="ui.finance.promptBecarInscripcion(${ins.id}, '${ins.equipo_nombre}', ${torneoId})" class="btn-secondary" style="font-size: 0.7rem; padding: 4px 8px; border-radius: 4px;" title="Becar Equipo">🎓</button>
                                    ` : ''}
                                    <button onclick="ui.finance.showAndPrintHistoryReport(${ins.id}, ${torneoId})" class="btn-secondary" style="font-size: 0.7rem; padding: 4px 8px; border-radius: 4px;" title="Imprimir Histórico y Reglamento">🖨️</button>
                                    ${['admin', 'ejecutivo', 'dueño_liga', 'super_arbitro', 'equipo'].includes(window.USER_ROL) ? `
                                        <button onclick="ui.finance.showPagoModal(${ins.id}, '${ins.equipo_nombre}', 'Inscripcion', ${ins.equipo_id})"
                                            class="btn-primary"
                                            style="font-size: 0.7rem; font-weight: 700; padding: 4px 10px; border-radius: 4px; display: inline-flex; align-items: center; gap: 4px; margin-left: 4px;">
                                            <span>💰</span> APORTAR
                                        </button>
                                    ` : ''}
                                </div>
                            </td>
                        </tr>
        `}).join('');

        html += `
                    </tbody>
                </table>
            </div>
        `;

        // Agregar Controles de Paginación
        if (this.pagination && this.pagination.total_pages > 1) {
            html += `
                <div class="pagination-controls" style="grid-column: 1 / -1; width: 100%;">
                    <button class="btn-pagination" ${!this.pagination.has_prev ? 'disabled' : ''}
                            onclick="ui.finance.loadInscripciones(${this.pagination.page - 1})">
                        &laquo; Anterior
                    </button>
                    <span class="pagination-info">Página ${this.pagination.page} de ${this.pagination.total_pages}</span>
                    <button class="btn-pagination" ${!this.pagination.has_next ? 'disabled' : ''}
                            onclick="ui.finance.loadInscripciones(${this.pagination.page + 1})">
                        Siguiente &raquo;
                    </button>
                </div>
            `;
        }

        container.innerHTML = html;
    }

    async showInscripcionModal() {
        const torneoId = document.getElementById('inscripciones-league-filter').value;
        if (!torneoId) {
            alert('Primero selecciona una liga en el filtro principal.');
            return;
        }

        try {
            const equipos = await Core.fetchAPI('/api/all_equipos');
            const select = document.getElementById('ins-equipo-id');
            select.innerHTML = equipos.map(e => `<option value="${e.id}">${e.nombre}</option>`).join('');

            const torneos = await Core.fetchAPI('/api/torneos');
            const t = torneos.find(x => x.id == torneoId);
            document.getElementById('ins-monto-pactado').value = t ? t.costo_inscripcion : 0;

            Core.openModal('modal-inscripcion');
        } catch (error) {
            const equipos = await Core.fetchAPI(`/api/equipos?torneo_id=${torneoId}`);
            const select = document.getElementById('ins-equipo-id');
            select.innerHTML = equipos.map(e => `<option value="${e.id}">${e.nombre}</option>`).join('');
            Core.openModal('modal-inscripcion');
        }
    }

    // This block was inserted by the user's instruction.
    // It seems to be a new function or a modification to an existing one,
    // but the instruction placed it inside the catch block of showInscripcionModal.
    // To maintain syntactic correctness and fulfill the instruction, it's placed here
    // as a separate, new method, assuming it was intended to be a new utility function.
    // The original instruction had a syntax error in the middle of the `Core.fetchAPI` call.
    // I've corrected it to be a standalone block.
    async populateLeagueDetailsSelect() {
        const response = await Core.fetchAPI('/api/torneos');
        const torneos = response.items || response;
        const select = document.getElementById('league-details-filter');
        if (select) {
            select.innerHTML = '<option value="">Seleccionar Organización...</option>' +
                (Array.isArray(torneos) ? torneos.map(t => `<option value="${t.id}">${t.nombre}</option>`).join('') : '');
        }
    }

    async handleInscripcionSubmit(e) {
        e.preventDefault();
        const torneoId = document.getElementById('inscripciones-league-filter').value;
        const data = {
            torneo_id: parseInt(torneoId),
            equipo_id: parseInt(document.getElementById('ins-equipo-id').value),
            monto_pactado: parseFloat(document.getElementById('ins-monto-pactado').value),
            abono_inicial: parseFloat(document.getElementById('ins-abono-inicial').value || 0),
            metodo_pago: document.getElementById('ins-metodo-pago').value
        };

        try {
            const response = await fetch('/api/inscripciones', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(data)
            });
            if (response.ok) {
                const resData = await response.json();
                Core.closeModal('modal-inscripcion');
                this.loadInscripciones();

                if (resData.ticket) {
                    this.showTicket(resData.ticket);
                }
            } else {
                const err = await response.json();
                alert(err.error || 'Error al inscribir equipo');
            }
        } catch (error) { alert('Error de conexión'); }
    }

    toggleDetalle(id) {
        const tr = document.getElementById(id);
        const icon = document.getElementById('icon-' + id);
        if (tr) {
            if (tr.style.display === 'none') {
                tr.style.display = 'table-row';
                if (icon) icon.style.transform = 'rotate(90deg)';
            } else {
                tr.style.display = 'none';
                if (icon) icon.style.transform = 'rotate(0deg)';
            }
        }
    }

    async showPagoModal(inscripcionId, equipoNombre, tipoSugerido = 'Inscripcion', equipoId = null) {
        document.getElementById('dash-pago-id').value = inscripcionId;
        document.getElementById('dash-pago-tipo').value = tipoSugerido;
        document.getElementById('dash-pago-equipo-info').innerHTML = `
            <span style="font-size: 0.7rem; color: var(--text-muted); text-transform: uppercase;">Abonando a:</span>
            <h4 style="margin: 4px 0 0 0; color: #fff;">${equipoNombre}</h4>
        `;
        document.getElementById('pago-form').reset();

        // Restaurar valor después de reset
        document.getElementById('dash-pago-id').value = inscripcionId;
        const tipoSelect = document.getElementById('dash-pago-tipo');
        tipoSelect.value = tipoSugerido;

        const containerPartido = document.getElementById('dash-pago-partido-container');
        const selectPartido = document.getElementById('dash-pago-partido');

        // Función para actualizar visibilidad
        const updateVisibility = () => {
            if (tipoSelect.value === 'Arbitraje') {
                containerPartido.style.display = 'block';
            } else {
                containerPartido.style.display = 'none';
                selectPartido.value = '';
            }
        };

        // Asignar evento al cambiar de tipo
        tipoSelect.onchange = updateVisibility;
        updateVisibility();

        // Cargar partidos del equipo si estamos en Arbitraje y tenemos el ID del equipo
        if (equipoId) {
            selectPartido.innerHTML = '<option value="">Cargando partidos...</option>';
            try {
                const partidos = await Core.fetchAPI(`/api/partidos?equipo_id=${equipoId}`);
                selectPartido.innerHTML = '<option value="">-- Sin vincular a partido específico --</option>';
                if (partidos && partidos.length > 0) {
                    partidos.forEach(p => {
                        const esLocal = Number(p.equipo_local_id) === Number(equipoId);
                        const rival = esLocal ? p.equipo_visitante : p.equipo_local;
                        const fecha = p.fecha ? ` | ${p.fecha}` : '';
                        const estado = p.estado === 'Played' ? ' ✓' : '';
                        selectPartido.innerHTML += `<option value="${p.id}">J${p.jornada} vs ${rival}${fecha}${estado}</option>`;
                    });
                } else {
                    selectPartido.innerHTML = '<option value="">-- Sin partidos registrados --</option>';
                }
            } catch (e) {
                console.error("Error loading matches for payment modal", e);
                selectPartido.innerHTML = '<option value="">-- Sin vincular a partido específico --</option>';
            }
        }

        Core.openModal('modal-pago');
    }

    async handlePagoSubmit(e) {
        e.preventDefault();

        const partidoSelect = document.getElementById('dash-pago-partido');
        const partidoVinculadoId = document.getElementById('dash-pago-partido-container').style.display !== 'none' && partidoSelect.value
            ? parseInt(partidoSelect.value)
            : null;

        const data = {
            inscripcion_id: parseInt(document.getElementById('dash-pago-id').value),
            monto: parseFloat(document.getElementById('dash-pago-monto').value),
            tipo: document.getElementById('dash-pago-tipo').value,
            metodo: document.getElementById('dash-pago-metodo').value,
            comentario: document.getElementById('dash-pago-comentario').value,
            partido_id: partidoVinculadoId
        };

        console.log("DASHBOARD PAYMENT DATA COLLECTED:", data);

        if (isNaN(data.inscripcion_id) || isNaN(data.monto) || !data.tipo) {
            alert('Por favor complete todos los datos del pago correctamente.');
            return;
        }

        try {
            const response = await fetch('/api/pagos', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(data)
            });
            if (response.ok) {
                const ticketData = await response.json();
                Core.closeModal('modal-pago');
                this.loadInscripciones();
                this.showTicket(ticketData);
            } else {
                const errData = await response.json();
                alert('Error al procesar la donación: ' + (errData.error || 'Desconocido'));
            }
        } catch (error) { 
            console.error('Payment Error:', error);
            alert('Error de conexión al procesar la donación'); 
        }
    }

    showTicket(data) {
        const content = document.getElementById('ticket-visual-content');
        if (!content) return;

        // Guardar data para PDF
        this._lastTicket = data;

        const premiosHtml = data.premios ? `
            <div style="border: 1px solid #e2e8f0; border-radius: 8px; padding: 15px; margin-bottom: 20px; background: #fff9f0;">
                <p style="font-size: 0.85rem; font-weight: 800; margin: 0 0 10px 0; color: #0f172a; text-transform: uppercase; border-bottom: 2px solid #fbbf24; padding-bottom: 8px;">🏆 Premios del Torneo</p>
                <div style="white-space: pre-wrap; font-family: sans-serif; line-height: 1.5; font-size: 0.85rem; color: #475569;">${data.premios}</div>
            </div>` : '';

        content.innerHTML = `
                <div style="font-family: 'Outfit', sans-serif; color: #333; padding: 25px; background: #fff; border-radius: 8px;">
                <div style="text-align: center; border-bottom: 3px solid #0ea5e9; padding-bottom: 15px; margin-bottom: 25px; text-transform: uppercase;">
                    <h2 style="margin: 0; font-size: 1.8rem; color: #0f172a; font-weight: 800;">FUTADMIN PRO</h2>
                    <p style="font-size: 1rem; color: #0ea5e9; margin: 5px 0; font-weight: 700; letter-spacing: 1px;">FICHA T&Eacute;CNICA DE INSCRIPCI&Oacute;N</p>
                    <p style="font-size: 0.7rem; color: #64748b; margin: 0; font-weight: 600;">FOLIO &Uacute;NICO DE SEGUIMIENTO O ACLARACIONES: ${data.folio || ('FUT-' + String(data.pago_id).padStart(6, '0'))}</p>
                </div>
                
                <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 15px; margin-bottom: 25px;">
                    <div style="background: #f8fafc; padding: 12px; border-radius: 8px; border: 1px solid #e2e8f0;">
                        <span style="display: block; font-size: 0.7rem; color: #64748b; font-weight: 700; margin-bottom: 4px;">TORNEO / LIGA</span>
                        <span style="font-size: 1rem; color: #0f172a; font-weight: 700;">${data.torneo}</span>
                    </div>
                    <div style="background: #f8fafc; padding: 12px; border-radius: 8px; border: 1px solid #e2e8f0;">
                        <span style="display: block; font-size: 0.7rem; color: #64748b; font-weight: 700; margin-bottom: 4px;">EQUIPO INSCRITO</span>
                        <span style="font-size: 1rem; color: #0ea5e9; font-weight: 800;">${data.equipo}</span>
                    </div>
                </div>

                <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 10px; margin-bottom: 25px; font-size: 0.85rem;">
                    <div>
                        <span style="display: block; color: #64748b; font-weight: 600; font-size: 0.7rem;">FECHA DE REGISTRO</span>
                        <span style="font-weight: 600; color: #333;">${data.fecha}</span>
                    </div>
                    <div>
                        <span style="display: block; color: #64748b; font-weight: 600; font-size: 0.7rem;">M&Eacute;TODO DE APORTACI&Oacute;N</span>
                        <span style="font-weight: 600; color: #333;">${data.metodo}</span>
                    </div>
                    <div>
                        <span style="display: block; color: #64748b; font-weight: 600; font-size: 0.7rem;">INICIO DEL TORNEO</span>
                        <span style="font-weight: 700; color: #0284c7;">${data.fecha_inicio_torneo || 'Pendiente'}</span>
                    </div>
                    <div>
                        <span style="display: block; color: #64748b; font-weight: 600; font-size: 0.7rem;">SEDE ASIGNADA</span>
                        <span style="font-weight: 700; color: #0284c7;">${data.sede || 'Por definir'}</span>
                    </div>
                </div>

                <div style="background: linear-gradient(135deg, #0ea5e9, #0284c7); padding: 15px; border-radius: 10px; margin-bottom: 20px; color: #fff; display: flex; justify-content: space-between; align-items: center; box-shadow: 0 4px 10px rgba(14, 165, 233, 0.2);">
                    <div style="font-weight: 700; font-size: 1.1rem; text-transform: uppercase;">Contribución Registrada:</div>
                    <div style="font-weight: 800; font-size: 1.5rem;">$${data.monto_abonado.toFixed(2)}</div>
                </div>

                <div style="border: 1px solid #e2e8f0; border-radius: 8px; padding: 15px; margin-bottom: 20px; background: #fafafa;">
                    <p style="font-size: 0.85rem; font-weight: 800; margin: 0 0 10px 0; color: #0f172a; text-transform: uppercase; border-bottom: 2px solid #e2e8f0; padding-bottom: 8px;">Resumen de Donaciones</p>
                    <div style="font-size: 0.9rem;">
                        <div style="display: flex; justify-content: space-between; margin-bottom: 8px;">
                            <span style="color: #64748b; font-weight: 600;">Donación Pactada:</span> <span style="font-weight: 700;">$${data.monto_pactado.toFixed(2)}</span>
                        </div>
                        <div style="display: flex; justify-content: space-between; margin-bottom: 8px;">
                            <span style="color: #64748b; font-weight: 600;">Total Donado a la Fecha:</span> <span style="font-weight: 700;">$${data.total_pagado.toFixed(2)}</span>
                        </div>
                        <div style="display: flex; justify-content: space-between; font-weight: 800; border-top: 1px solid #cbd5e1; margin-top: 8px; padding-top: 8px; color: #ef4444; font-size: 1rem;">
                            <span>DONACIÓN PENDIENTE:</span> <span>$${data.saldo_pendiente.toFixed(2)}</span>
                        </div>
                    </div>
                </div>

                ${premiosHtml}

                <div style="border: 1px solid #e2e8f0; border-radius: 8px; padding: 15px; font-size: 0.8rem; background: #f8fafc; margin-bottom: 10px; color: #475569;">
                    <p style="font-weight: 800; text-align: center; margin: 0 0 12px 0; color: #0f172a; text-transform: uppercase; letter-spacing: 0.5px;">Reglamento y Cl&aacute;usulas Aceptadas</p>
                    <div style="white-space: pre-wrap; font-family: sans-serif; line-height: 1.4;">
${data.reglamento ? `<strong style="color:#0f172a;">REGLAMENTO:</strong>\n${data.reglamento}\n\n` : ''}${data.clausulas ? `<strong style="color:#0f172a;">CL&Aacute;USULAS:</strong>\n${data.clausulas}` : ''}
                    </div>
                </div>

                <div style="text-align: center; margin-top: 25px; font-size: 0.8rem; border-top: 1px solid #e2e8f0; padding-top: 20px; color: #64748b;">
                    <p style="margin: 0; font-weight: 800; color: #0ea5e9; font-size: 0.95rem;">&#161;REGISTRO EXITOSO!</p>
                    <p style="margin: 5px 0 0 0;">Esta Ficha T&eacute;cnica es un documento oficial emitido por FUTADMIN PRO.</p>
                </div>
            </div>
                `;
        Core.openModal('modal-ticket');
    }

    downloadTicketPDF() {
        const data = this._lastTicket;
        if (!data) { alert('No hay ticket disponible.'); return; }

        const folio = data.folio || ('FUT-' + String(data.pago_id).padStart(6, '0'));
        const premiosSection = data.premios ? `
  <div class="section-title" style="color:#b45309; border-color:#fbbf24;">🏆 Premios del Torneo</div>
  <div class="reg-text" style="margin-bottom:20px;">${data.premios}</div>` : '';

        const printHtml = `<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8">
<title>Ficha T\u00e9cnica - ${data.equipo}</title>
<style>
  @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@400;600;700;800&display=swap');
  * { box-sizing: border-box; margin: 0; padding: 0; }
  body { font-family: 'Outfit', Arial, sans-serif; color: #1e293b; background: #fff; padding: 28px; font-size: 13px; }
  @page { size: letter; margin: 1.5cm; }
  .header { text-align: center; border-bottom: 3px solid #0ea5e9; padding-bottom: 14px; margin-bottom: 22px; }
  .header h1 { font-size: 24px; font-weight: 800; color: #0f172a; text-transform: uppercase; letter-spacing: 2px; }
  .header .sub { font-size: 13px; color: #0ea5e9; font-weight: 700; letter-spacing: 1px; margin: 4px 0; }
  .header .folio { font-size: 11px; color: #64748b; font-weight: 600; margin-top: 4px; }
  .info-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 12px; margin-bottom: 20px; }
  .info-box { background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 8px; padding: 10px 14px; }
  .info-box .lbl { display: block; font-size: 9px; color: #64748b; font-weight: 700; text-transform: uppercase; margin-bottom: 3px; }
  .info-box .val { font-size: 14px; font-weight: 700; color: #0f172a; }
  .info-box .val.blue { color: #0284c7; }
  .abono-bar { background: linear-gradient(135deg, #0ea5e9, #0284c7); border-radius: 10px; padding: 14px 20px; margin-bottom: 18px; color: #fff; display: flex; justify-content: space-between; align-items: center; }
  .abono-bar .label { font-weight: 700; font-size: 13px; text-transform: uppercase; }
  .abono-bar .amount { font-weight: 800; font-size: 20px; }
  .cuenta { border: 1px solid #e2e8f0; border-radius: 8px; padding: 14px; margin-bottom: 18px; background: #fafafa; }
  .cuenta-title { font-size: 11px; font-weight: 800; text-transform: uppercase; border-bottom: 2px solid #e2e8f0; padding-bottom: 6px; margin-bottom: 10px; color: #0f172a; }
  .cuenta-row { display: flex; justify-content: space-between; margin-bottom: 7px; font-size: 12px; }
  .cuenta-row.saldo { border-top: 1px solid #cbd5e1; padding-top: 7px; margin-top: 7px; font-weight: 800; font-size: 14px; color: #ef4444; }
  .section-title { font-size: 11px; font-weight: 800; text-transform: uppercase; letter-spacing: 1px; border-bottom: 2px solid #e2e8f0; padding-bottom: 4px; margin: 16px 0 8px 0; color: #0f172a; }
  .reg-text { white-space: pre-wrap; font-size: 11px; color: #475569; line-height: 1.5; text-align: justify; }
  .footer { margin-top: 30px; border-top: 1px solid #e2e8f0; padding-top: 14px; text-align: center; font-size: 10px; color: #94a3b8; }
  .footer .success { font-size: 13px; font-weight: 800; color: #0ea5e9; margin-bottom: 4px; }
  @media print { body { -webkit-print-color-adjust: exact; print-color-adjust: exact; } }
</style>
</head>
<body>

<div class="header">
  <h1>FUTADMIN PRO \u26bd</h1>
  <div class="sub">FICHA T\u00c9CNICA DE INSCRIPCI\u00d3N</div>
  <div class="folio">FOLIO &Uacute;NICO DE SEGUIMIENTO O ACLARACIONES: ${folio}</div>
</div>

<div class="info-grid">
  <div class="info-box">
    <span class="lbl">Torneo / Liga</span>
    <span class="val">${data.torneo}</span>
  </div>
  <div class="info-box">
    <span class="lbl">Equipo Inscrito</span>
    <span class="val blue">${data.equipo}</span>
  </div>
  <div class="info-box">
    <span class="lbl">Fecha de Registro</span>
    <span class="val">${data.fecha}</span>
  </div>
  <div class="info-box">
    <span class="lbl">M\u00e9todo de Aportaci\u00f3n</span>
    <span class="val">${data.metodo}</span>
  </div>
  <div class="info-box">
    <span class="lbl">Inicio del Torneo</span>
    <span class="val blue">${data.fecha_inicio_torneo || 'Pendiente'}</span>
  </div>
  <div class="info-box">
    <span class="lbl">Sede Asignada</span>
    <span class="val blue">${data.sede || 'Por definir'}</span>
  </div>
</div>

<div class="abono-bar">
  <span class="label">Contribución Registrada</span>
  <span class="amount">$${data.monto_abonado.toFixed(2)}</span>
</div>

<div class="cuenta">
  <div class="cuenta-title">Resumen de Donaciones</div>
  <div class="cuenta-row"><span>Donación Pactada:</span><span>$${data.monto_pactado.toFixed(2)}</span></div>
  <div class="cuenta-row"><span>Total Donado a la Fecha:</span><span>$${data.total_pagado.toFixed(2)}</span></div>
  <div class="cuenta-row saldo"><span>DONACIÓN PENDIENTE:</span><span>$${data.saldo_pendiente.toFixed(2)}</span></div>
</div>

${premiosSection}

${data.reglamento || data.clausulas ? `<div class="section-title">Reglamento y Cl\u00e1usulas Aceptadas</div>
<div class="reg-text">${data.reglamento ? '<strong>REGLAMENTO:</strong>\n' + data.reglamento + '\n\n' : ''}${data.clausulas ? '<strong>CL\u00c1USULAS:</strong>\n' + data.clausulas : ''}</div>` : ''}

<div class="footer">
  <div class="success">\u00a1REGISTRO EXITOSO!</div>
  <div>Esta Ficha T\u00e9cnica es un documento oficial emitido por FUTADMIN PRO.</div>
  <div>Al participar, el equipo acepta el reglamento y las cl\u00e1usulas descritas.</div>
</div>

</body>
</html>`;

        const printWin = window.open('', '_blank', 'width=820,height=960,top=40,left=60');
        if (!printWin) { alert('Por favor permita ventanas emergentes para imprimir.'); return; }
        printWin.document.open();
        printWin.document.write(printHtml);
        printWin.document.close();
        setTimeout(() => { printWin.focus(); printWin.print(); }, 600);
    }

    async promptEditInscripcion(id, equipo, montoActual) {
        const nuevoMontoStr = prompt(`✏️ Editando Donación (Inscripción) para: ${equipo} \n\nDonación actual: $${montoActual} \n\nIngrese la nueva donación (EJ: 500): `, montoActual);
        if (nuevoMontoStr === null) return;

        const nuevoMonto = parseFloat(nuevoMontoStr);
        if (isNaN(nuevoMonto) || nuevoMonto < 0) {
            alert("Monto inválido. Debe ser un número mayor o igual a cero.");
            return;
        }

        try {
            const response = await fetch(`/ api / inscripciones / ${id} `, {
                method: 'PUT',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ monto_pactado: nuevoMonto })
            });

            if (response.ok) {
                // Determine if we are on Inscripciones or Arbitrajes tab and reload
                if (document.getElementById('tab-inscripciones-lista') && document.getElementById('tab-inscripciones-lista').style.display !== 'none') {
                    this.loadInscripciones();
                } else {
                    this.loadArbitrajes();
                }
            } else {
                alert('Hubo un error al actualizar el monto.');
            }
        } catch (err) {
            alert('Error de conexión.');
        }
    }

    async promptBecarInscripcion(id, equipo, torneoId) {
        const tipoBeca = prompt(`🎓 Opciones de Beca para: ${equipo} \n\nSeleccione el descuento a aplicar sobre el monto original: \n\n1 = 100 % de descuento(Beca total) \n2 = 50 % de descuento(Media beca) \n3 = Otro(Cancelar)`, "1");

        if (tipoBeca === null || (tipoBeca !== "1" && tipoBeca !== "2")) return;

        // Primero, obtener el monto base del torneo para este equipo
        // (Podríamos sacar el monto del DOM, pero en Beca recalculamos asumiendo que el torneo cuesta X original)
        // Para simplificar, le preguntaremos el nuevo monto al API pasándole el descuento.
        // Pero como el API PUT espera 'monto_pactado', calculémoslo en base al costo del torneo.

        try {
            // Conseguir los datos de la inscripción para saber el torneo
            const dataInscripciones = await Core.fetchAPI(`/ api / inscripciones ? torneo_id = ${torneoId} `);
            const insData = dataInscripciones.find(i => i.id === id);

            if (!insData) return;

            // Buscar el costo del torneo
            const torneos = await Core.fetchAPI('/api/torneos');
            const torneoInfo = torneos.find(t => t.id === insData.torneo_id);
            const costoOriginal = torneoInfo ? (torneoInfo.costo_inscripcion || 0) : 0;

            let nuevoMonto = costoOriginal;
            if (tipoBeca === "1") {
                nuevoMonto = 0; // 100% descuento
            } else if (tipoBeca === "2") {
                nuevoMonto = costoOriginal / 2; // 50% descuento
            }

            if (confirm(`Se aplicará la beca al equipo ${equipo}.\nSu cuota pasará de $${costoOriginal} a $${nuevoMonto}.\n\n¿Proceder ? `)) {
                const response = await fetch(`/ api / inscripciones / ${id} `, {
                    method: 'PUT',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ monto_pactado: nuevoMonto })
                });

                if (response.ok) {
                    if (document.getElementById('tab-inscripciones-lista') && document.getElementById('tab-inscripciones-lista').style.display !== 'none') {
                        this.loadInscripciones();
                    } else {
                        this.loadArbitrajes();
                    }
                } else {
                    alert('Hubo un error al aplicar la beca.');
                }
            }
        } catch (err) {
            alert('Error de conexión.');
        }
    }

    async showAndPrintHistoryReport(id, torneoId) {
        try {
            const responseInscripciones = await Core.fetchAPI(`/api/inscripciones?torneo_id=${torneoId}`);
            const dataInscripciones = responseInscripciones.items || responseInscripciones || [];
            const insData = Array.isArray(dataInscripciones) ? dataInscripciones.find(i => i.id === id) : null;
            if (!insData) { alert('No se encontraron datos del equipo.'); return; }

            const responseTorneos = await Core.fetchAPI('/api/torneos');
            const torneos = responseTorneos.items || responseTorneos || [];
            const torneoInfo = Array.isArray(torneos) ? torneos.find(t => t.id === (insData.torneo_id || torneoId)) : null;
            const reglamento = torneoInfo ? (torneoInfo.reglamento || 'Sin reglamento registrado.') : 'Sin reglamento registrado.';
            const clausulas = torneoInfo ? (torneoInfo.clausulas || '') : '';
            const nombreTorneo = torneoInfo ? torneoInfo.nombre : 'Liga/Torneo';

            const historialRows = insData.historial_pagos && insData.historial_pagos.length > 0
                ? insData.historial_pagos.map(p => `
                    <tr>
                        <td style="padding:8px; border-bottom:1px solid #e2e8f0;">${p.fecha}</td>
                        <td style="padding:8px; border-bottom:1px solid #e2e8f0;">${p.tipo}</td>
                        <td style="padding:8px; border-bottom:1px solid #e2e8f0;">${p.metodo}</td>
                        <td style="padding:8px; border-bottom:1px solid #e2e8f0; font-weight:bold; text-align:right;">$${Number(p.monto).toFixed(2)}</td>
                    </tr>`).join('')
                : '<tr><td colspan="4" style="padding:8px; text-align:center; font-style:italic; border-bottom:1px solid #e2e8f0;">No hay aportaciones registradas</td></tr>';

            const prog = insData.partidos_programados || 0;
            const jug = insData.partidos_jugados || 0;
            const pend = insData.partidos_pendientes || (prog - jug);
            const tarifa = Number(insData.tarifa_arbitraje || 0);
            const esperado = Number(insData.esperado_arbitraje || (prog * tarifa));
            const pagArb = Number(insData.pagado_arbitraje || 0);
            const saldoArb = Number(insData.saldo_arbitraje ?? (esperado - pagArb));
            const pctArb = esperado > 0 ? Math.min(100, Math.round((pagArb / esperado) * 100)) : (pagArb > 0 ? 100 : 0);

            const printHtml = `<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8">
<title>Reporte - ${insData.equipo_nombre}</title>
<style>
  body { font-family: Arial, sans-serif; color: #333; margin: 0; padding: 20px; line-height: 1.5; font-size: 13px; }
  @page { size: letter; margin: 1.5cm; }
  .header { text-align: center; border-bottom: 3px solid #1a1a1a; padding-bottom: 12px; margin-bottom: 18px; }
  .header h1 { margin: 0; font-size: 22px; text-transform: uppercase; letter-spacing: 2px; }
  .header p { margin: 4px 0 0 0; font-size: 11px; color: #666; }
  .info-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 16px; margin-bottom: 22px; }
  .info-box { background: #f8f9fa; border: 1px solid #dee2e6; padding: 12px; border-radius: 6px; }
  .info-box .lbl { display: block; font-size: 10px; color: #888; text-transform: uppercase; margin-bottom: 4px; font-weight: bold; }
  .info-box strong { font-size: 15px; color: #000; }
  .section-title { font-size: 12px; text-transform: uppercase; letter-spacing: 1px; font-weight: bold; border-bottom: 2px solid #dee2e6; padding-bottom: 4px; margin: 18px 0 10px 0; }
  table { width: 100%; border-collapse: collapse; margin-bottom: 22px; }
  th { text-align: left; padding: 8px 6px; background: #e9ecef; border-bottom: 2px solid #ced4da; font-size: 11px; text-transform: uppercase; }
  td { font-size: 12px; }
  .stats-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 10px; margin-bottom: 20px; }
  .stat-box { background: #f1f3f5; border: 1px solid #dee2e6; border-radius: 6px; padding: 10px; text-align: center; }
  .stat-box .num { font-size: 20px; font-weight: bold; color: #1a1a1a; }
  .stat-box .lbl { font-size: 10px; color: #666; text-transform: uppercase; }
  .balances { background: #f8f9fa; border: 1px solid #dee2e6; border-radius: 6px; padding: 12px; margin-bottom: 22px; }
  .bal-row { display: flex; justify-content: space-between; padding: 5px 0; border-bottom: 1px solid #e9ecef; font-size: 12px; }
  .bal-row:last-child { border-bottom: none; font-weight: bold; font-size: 14px; padding-top: 8px; }
  .progress-bar-bg { background: #dee2e6; border-radius: 999px; height: 8px; overflow: hidden; margin: 8px 0 3px; }
  .progress-bar-fill { height: 100%; border-radius: 999px; background: ${pctArb === 100 ? '#2e7d32' : pctArb > 50 ? '#f57f17' : '#c62828'}; }
  .reg-text { white-space: pre-wrap; font-size: 11px; color: #444; text-align: justify; }
  .footer { margin-top: 40px; text-align: center; border-top: 1px solid #ccc; padding-top: 15px; font-size: 10px; color: #999; }
  @media print { body { -webkit-print-color-adjust: exact; print-color-adjust: exact; } }
</style>
</head>
<body>

<div class="header">
  <h1>FUTADMIN PRO ⚽</h1>
  <p>REPORTE DE CONTROL DE APORTACIONES Y REGLAMENTO DE COMPETENCIA</p>
  <p>Folio: ${new Date().getTime().toString().substring(5)} &nbsp;|&nbsp; Fecha: ${new Date().toLocaleDateString('es-MX')}</p>
</div>

<div class="info-grid">
  <div class="info-box">
    <span class="lbl">Equipo</span>
    <strong>${insData.equipo_nombre}</strong>
  </div>
  <div class="info-box">
    <span class="lbl">Torneo / Liga</span>
    <strong>${nombreTorneo}</strong>
  </div>
</div>

<div class="section-title">Control de Arbitraje por Partido</div>
<div class="stats-grid">
  <div class="stat-box">
    <div class="num">${prog}</div>
    <div class="lbl">Programados</div>
  </div>
  <div class="stat-box">
    <div class="num">${jug}</div>
    <div class="lbl">Jugados</div>
  </div>
  <div class="stat-box">
    <div class="num">${pend}</div>
    <div class="lbl">Pendientes</div>
  </div>
  <div class="stat-box">
    <div class="num">$${tarifa.toFixed(2)}</div>
    <div class="lbl">Tarifa/Jgo</div>
  </div>
</div>

<div class="balances">
  <div class="bal-row"><span>Total Esperado (Arbitraje):</span><span>$${esperado.toFixed(2)}</span></div>
  <div class="bal-row"><span>Total Pagado (Arbitraje):</span><span style="color:#2e7d32;">$${pagArb.toFixed(2)}</span></div>
  <div class="bal-row"><span>Pactado Inscripción:</span><span>$${Number(insData.monto_pactado || 0).toFixed(2)}</span></div>
  <div class="bal-row"><span>Abonado Inscripción:</span><span style="color:#2e7d32;">$${Number(insData.pagado_inscripcion || 0).toFixed(2)}</span></div>
  <div class="bal-row" style="color:${insData.saldo_inscripcion > 0 ? '#c62828' : '#2e7d32'};"><span>Saldo Pendiente Inscripción:</span><span>$${Number(insData.saldo_inscripcion || 0).toFixed(2)}</span></div>
  <div class="bal-row" style="color:${saldoArb > 0 ? '#c62828' : '#2e7d32'};"><span>Saldo Pendiente Arbitraje:</span><span>$${saldoArb.toFixed(2)}</span></div>
</div>

<div class="section-title">Avance de Arbitraje: ${pctArb}% cubierto</div>
<div class="progress-bar-bg"><div class="progress-bar-fill" style="width:${pctArb}%;"></div></div>
<p style="font-size:11px; color:#666; margin:0 0 20px;">$${pagArb.toFixed(2)} pagados de $${esperado.toFixed(2)} esperados</p>

<div class="section-title">Historial de Abonos</div>
<table>
  <thead><tr><th>Fecha</th><th>Concepto</th><th>Método</th><th style="text-align:right;">Monto</th></tr></thead>
  <tbody>${historialRows}</tbody>
</table>

${reglamento !== 'Sin reglamento registrado.' ? `
<div class="section-title">Reglamento Oficial</div>
<div class="reg-text">${reglamento}</div>
` : ''}

${clausulas ? `
<div class="section-title" style="margin-top:16px;">Cláusulas Especiales</div>
<div class="reg-text">${clausulas}</div>
` : ''}

<div class="footer">
  Documento emitido por FUTADMIN PRO &mdash; Sistema de Control de Ligas.<br>
  Al participar, el equipo declara conformidad con los pagos mostrados y acatamiento total del reglamento.
</div>
</body>
</html>`;

            const printWin = window.open('', '_blank', 'width=820,height=960,top=40,left=60');
            if (!printWin) { alert('Por favor permita ventanas emergentes para imprimir.'); return; }
            printWin.document.open();
            printWin.document.write(printHtml);
            printWin.document.close();
            setTimeout(() => { printWin.focus(); printWin.print(); }, 600);

        } catch (e) {
            console.error('Error al preparar impresión:', e);
            alert('Error al preparar la impresión: ' + e.message);
        }
    }
}

