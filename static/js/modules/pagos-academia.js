/**
 * Módulo de Pagos de Academia - Semáforo de cobros por período
 */
const MESES = ['Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio',
    'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre'];

class PagosAcademiaModule {
    constructor() {
        this.resumenData = null;
    }

    async init() {
        await this.loadGruposSelect();
        this.buildPeriodoSelect();
        this.setupFormListener();
    }

    setupFormListener() {
        const form = document.getElementById('pago-academia-form');
        if (form && !form.dataset.listener) {
            form.addEventListener('submit', (e) => this.handlePagoSubmit(e));
            form.dataset.listener = 'true';
        }
    }

    async loadGruposSelect() {
        try {
            const res = await fetch('/api/entrenamientos/grupos');
            const data = await res.json();
            const items = Array.isArray(data) ? data : (data.items || []);
            const sel = document.getElementById('pagos-academia-grupo');
            if (!sel) return;
            sel.innerHTML = '<option value="">— Selecciona un Grupo —</option>' +
                items.map(g => `<option value="${g.id}">${g.nombre}</option>`).join('');
        } catch (e) { console.error(e); }
    }

    onGrupoChange() {
        this.loadResumen();
    }

    buildPeriodoSelect() {
        const modalidad = document.getElementById('pagos-academia-modalidad')?.value || 'Mensual';
        const sel = document.getElementById('pagos-academia-periodo');
        if (!sel) return;

        const now = new Date();
        const options = [];

        if (modalidad === 'Mensual') {
            // Muestra los últimos 6 meses + próximo mes
            for (let i = -1; i <= 5; i++) {
                const d = new Date(now.getFullYear(), now.getMonth() - i, 1);
                const label = `${MESES[d.getMonth()]} ${d.getFullYear()}`;
                options.push(`<option value="${label}" ${i === 0 ? 'selected' : ''}>${label}</option>`);
            }
        } else if (modalidad === 'Quincenal') {
            // Genera las quincenas de los últimos 3 meses
            for (let m = 0; m <= 3; m++) {
                const d = new Date(now.getFullYear(), now.getMonth() - m, 1);
                const base = `${MESES[d.getMonth()]} ${d.getFullYear()}`;
                options.unshift(`<option value="${base} - 2da Quincena">${base} — 2da Quincena (16-fin)</option>`);
                options.unshift(`<option value="${base} - 1ra Quincena">${base} — 1ra Quincena (1-15)</option>`);
            }
        } else { // Semanal
            // Las últimas 8 semanas
            for (let w = 0; w < 8; w++) {
                const start = new Date(now);
                start.setDate(start.getDate() - (w * 7));
                const end = new Date(start);
                end.setDate(end.getDate() + 6);
                const fmt = d => `${d.getDate()}/${d.getMonth() + 1}`;
                const label = `Semana ${fmt(start)}-${fmt(end)} ${start.getFullYear()}`;
                options.push(`<option value="${label}" ${w === 0 ? 'selected' : ''}>${label}</option>`);
            }
        }

        sel.innerHTML = options.join('');
        this.loadResumen();
    }

    async loadResumen() {
        const grupoId = document.getElementById('pagos-academia-grupo')?.value;
        const periodo = document.getElementById('pagos-academia-periodo')?.value;

        if (!grupoId || !periodo) return;

        try {
            const res = await fetch(`/api/entrenamientos/pagos/resumen?grupo_id=${grupoId}&periodo=${encodeURIComponent(periodo)}`);
            const data = await res.json();
            this.resumenData = data;
            this.renderStats(data);
            this.renderTabla(data);
        } catch (e) {
            console.error("Error cargando resumen:", e);
        }
    }

    renderStats(data) {
        const container = document.getElementById('pagos-academia-stats');
        if (!container) return;

        if (!data || !data.alumnos) {
            container.innerHTML = '<div style="color:#ef4444; padding:10px; background:rgba(239,68,68,0.1); border-radius:8px;">⚠️ Error al cargar estadísticas.</div>';
            return;
        }

        const pendientes = data.total_alumnos - data.total_pagados;
        const recaudado = data.alumnos.reduce((s, a) => s + (a.monto_pagado || 0), 0);
        const esperado = data.total_alumnos * data.costo_mensual;
        const pct = data.total_alumnos > 0 ? Math.round((data.total_pagados / data.total_alumnos) * 100) : 0;

        container.innerHTML = `
            <div class="stat-card">
                <div class="stat-icon" style="background: rgba(16,185,129,0.15);">✅</div>
                <div class="stat-info">
                    <div class="stat-value" style="color:#10b981;">${data.total_pagados}</div>
                    <div class="stat-label">Donaron (${pct}%)</div>
                </div>
            </div>
            <div class="stat-card">
                <div class="stat-icon" style="background: rgba(239,68,68,0.15);">⏳</div>
                <div class="stat-info">
                    <div class="stat-value" style="color:#ef4444;">${pendientes}</div>
                    <div class="stat-label">Pendientes</div>
                </div>
            </div>
            <div class="stat-card">
                <div class="stat-icon" style="background: rgba(59,130,246,0.15);">💰</div>
                <div class="stat-info">
                    <div class="stat-value" style="color:#3b82f6;">$${recaudado.toFixed(0)}</div>
                    <div class="stat-label">Total Aportado</div>
                </div>
            </div>
            <div class="stat-card">
                <div class="stat-icon" style="background: rgba(245,158,11,0.15);">🎯</div>
                <div class="stat-info">
                    <div class="stat-value" style="color:#f59e0b;">$${(esperado - recaudado).toFixed(0)}</div>
                    <div class="stat-label">Por Donar</div>
                </div>
            </div>`;
    }

    updateFilteredStats(filtered, costoMensual) {
        const container = document.getElementById('pagos-academia-stats');
        if (!container) return;

        const total = filtered.length;
        const pagados = filtered.filter(a => a.pagado).length;
        const pendientes = total - pagados;
        const recaudado = filtered.reduce((s, a) => s + (a.monto_pagado || 0), 0);
        const esperado = total * costoMensual;
        const pct = total > 0 ? Math.round((pagados / total) * 100) : 0;

        container.innerHTML = `
            <div class="stat-card">
                <div class="stat-icon" style="background: rgba(16,185,129,0.15);">✅</div>
                <div class="stat-info">
                    <div class="stat-value" style="color:#10b981;">${pagados}</div>
                    <div class="stat-label">Donaron (${pct}%)</div>
                </div>
            </div>
            <div class="stat-card">
                <div class="stat-icon" style="background: rgba(239,68,68,0.15);">⏳</div>
                <div class="stat-info">
                    <div class="stat-value" style="color:#ef4444;">${pendientes}</div>
                    <div class="stat-label">Pendientes</div>
                </div>
            </div>
            <div class="stat-card">
                <div class="stat-icon" style="background: rgba(59,130,246,0.15);">💰</div>
                <div class="stat-info">
                    <div class="stat-value" style="color:#3b82f6;">$${recaudado.toFixed(0)}</div>
                    <div class="stat-label">Total Aportado</div>
                </div>
            </div>
            <div class="stat-card">
                <div class="stat-icon" style="background: rgba(245,158,11,0.15);">🎯</div>
                <div class="stat-info">
                    <div class="stat-value" style="color:#f59e0b;">$${(esperado - recaudado).toFixed(0)}</div>
                    <div class="stat-label">Por Donar</div>
                </div>
            </div>`;
    }

    renderTabla(data) {
        const tbody = document.getElementById('pagos-academia-list');
        const statusFilter = document.getElementById('pagos-academia-status-filter')?.value || 'all';
        if (!tbody) return;

        if (!data || !data.alumnos || data.alumnos.length === 0) {
            tbody.innerHTML = `<tr><td colspan="7" style="text-align:center;padding:2rem;color:var(--text-muted);">${data && data.error ? `⚠️ Error: ${data.error}` : 'No hay alumnos en este grupo.'}</td></tr>`;
            return;
        }

        let filtered = data.alumnos;
        if (statusFilter === 'pending') {
            filtered = data.alumnos.filter(a => !a.pagado);
        } else if (statusFilter === 'settled') {
            filtered = data.alumnos.filter(a => a.pagado);
        }

        // Actualizar estadísticas con la lista filtrada
        this.updateFilteredStats(filtered, data.costo_mensual);

        // Ordenar: No pagados completo primero
        const sorted = [...filtered].sort((a, b) => a.pagado - b.pagado);

        tbody.innerHTML = sorted.map(a => {
            const faltante = data.costo_mensual - a.monto_pagado;
            const statusColor = a.pagado ? '#10b981' : (a.monto_pagado > 0 ? '#f59e0b' : '#ef4444');
            const statusIcon = a.pagado ? '✅' : (a.monto_pagado > 0 ? '🟠' : '🔴');

            return `
            <tr style="border-left: 4px solid ${statusColor};">
                <td>
                    <span style="font-size:1.4rem;" title="${a.pagado ? 'Donación Completa' : 'Donación Pendiente'}">
                        ${statusIcon}
                    </span>
                </td>
                <td style="font-weight:600;">${a.alumno_nombre}</td>
                <td style="font-size:0.85rem; color:var(--text-muted);">
                    ${a.tutor ? `<span>👤 ${a.tutor}</span><br>` : ''}
                    ${a.telefono ? `<span>📱 ${a.telefono}</span>` : '—'}
                </td>
                <td>
                    <div style="font-weight:600; color:${statusColor};">
                        $${a.monto_pagado.toFixed(2)} / $${data.costo_mensual.toFixed(2)}
                    </div>
                    ${faltante > 0 && a.monto_pagado > 0 ? `<div style="font-size:0.7rem; color:#ef4444;">Faltan $${faltante.toFixed(2)}</div>` : ''}
                </td>
                <td>${a.metodo || '—'}</td>
                <td style="font-size:0.85rem;">${a.fecha_pago || '—'}</td>
                <td>
                    <div style="display:flex; gap:5px; flex-wrap:wrap;">
                        ${!a.pagado
                    ? (window.USER_ROL !== 'resultados' && window.USER_ROL !== 'arbitro' ? `<button class="btn-primary" style="font-size:0.75rem;padding:4px 10px;" 
                                onclick="ui.pagosAcademia.registrarPago(${a.alumno_id}, '${a.alumno_nombre.replace(/'/g, "\\")}', ${faltante})">
                                💵 ${a.monto_pagado > 0 ? 'Aportar' : 'Donar'}
                               </button>` : `<span style="color:#f59e0b; font-weight:600; font-size:0.8rem;">⌛ Pendiente</span>`)
                    : `<span style="color:#10b981; font-weight:600; font-size:0.8rem;">✓ Donado</span>`
                }
                        
                        ${(a.pagos || []).map((p, idx) => `
                            <button class="btn-icon" title="Ver Ticket ${idx + 1}" style="color:var(--primary); background:rgba(0,255,136,0.1); border-radius:4px; padding:4px;" 
                                onclick='ui.entrenamientos.showTicket(${JSON.stringify(p.ticket_data).replace(/'/g, "&apos;")})'>
                                📄
                            </button>
                        `).join('')}
                    </div>
                </td>
            </tr>`;
        }).join('');
    }

    registrarPago(alumnoId, alumnoNombre, sugerido = null) {
        const periodo = document.getElementById('pagos-academia-periodo')?.value;
        const costoMensual = sugerido !== null ? sugerido : (this.resumenData?.costo_mensual || 0);

        // Poblar campos del modal
        document.getElementById('academy-pago-alumno-id').value = alumnoId;
        document.getElementById('academy-pago-alumno-nombre').innerText = alumnoNombre;
        document.getElementById('academy-pago-periodo-label').innerText = periodo;
        document.getElementById('academy-pago-monto-sugerido').innerText = `$${costoMensual.toFixed(2)}`;
        document.getElementById('academy-pago-monto').value = costoMensual;

        // Abrir modal
        Core.openModal('modal-pago-academia');
    }

    async handlePagoSubmit(e) {
        e.preventDefault();
        const alumnoId = document.getElementById('academy-pago-alumno-id').value;
        const alumnoNombre = document.getElementById('academy-pago-alumno-nombre').innerText;
        const periodo = document.getElementById('academy-pago-periodo-label').innerText;
        const monto = parseFloat(document.getElementById('academy-pago-monto').value);
        const metodo = document.getElementById('academy-pago-metodo').value;
        const comentario = document.getElementById('academy-pago-comentario').value;

        console.log("ACADEMY PAYMENT DATA COLLECTED:", { alumnoId, periodo, monto, metodo });

        if (!alumnoId || !periodo || isNaN(monto) || !metodo) {
            alert('Por favor complete todos los datos obligatorios del pago academia.');
            return;
        }

        try {
            const res = await fetch('/api/entrenamientos/pagos', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    alumno_id: alumnoId,
                    periodo: periodo,
                    monto: monto,
                    metodo: metodo,
                    comentario: comentario
                })
            });

            const data = await res.json();
            if (!res.ok) throw new Error(data.error || 'Error al registrar el pago');

            Core.closeModal('modal-pago-academia');
            Core.showNotification(`Donación de ${alumnoNombre} registrada correctamente`, 'success');

            if (data.ticket) {
                ui.entrenamientos.showTicket(data.ticket);
            }
            this.loadResumen();
            e.target.reset();
        } catch (e) {
            console.error("Error al registrar pago:", e);
            Core.showNotification(e.message, 'error');
        }
    }
}

export default PagosAcademiaModule;
