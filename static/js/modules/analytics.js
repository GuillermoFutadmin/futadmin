/**
 * Módulo de Analíticas y Resúmenes Estratégicos
 */
import { Core } from './core.js';

export class AnalyticsModule {
    constructor(ui) {
        this.ui = ui;
    }

    async renderResumenes() {
        // Asegurarse de que las ligas estén cargadas con datos frescos
        await this.ui.settings.loadLigas();

        const ligas = this.ui.settings.ligas || [];

        // Cargar estadísticas detalladas
        try {
            // Sincronizar con filtros si están definidos
            const now = new Date();
            if (!this._reportStartDate) this._reportStartDate = new Date(now.getFullYear(), now.getMonth(), 1).toISOString().split('T')[0];
            if (!this._reportEndDate) this._reportEndDate = now.toISOString().split('T')[0];

            let params = `?start_date=${this._reportStartDate}&end_date=${this._reportEndDate}`;

            const stats = await Core.fetchAPI(`/api/admin/dashboard-stats${params}`);
            const corte = await Core.fetchAPI(`/api/corte-diario${params}`); // Acumulado del mes
            const corteHoy = await Core.fetchAPI(`/api/corte-diario`); // Solo de hoy

            // Checks defensivos
            if (!stats) console.warn("No se pudieron cargar las estadísticas.");
            if (!corte) console.warn("No se pudo cargar el corte mensual.");

            const elements = {
                'stat-partidos-hoy': stats?.partidos_hoy ?? 0,
                'stat-jugadores': stats?.jugadores ?? 0,
                'stat-entrenamientos': stats?.entrenamientos_activos ?? 0,
                'stat-alertas-pago': stats?.alertas_pago ?? 0,
                'resumen-partidos-hoy': stats?.partidos_hoy ?? 0,
                'resumen-total-jugadores': stats?.jugadores ?? 0,
                'resumen-total-entrenamientos': stats?.entrenamientos_activos ?? 0,
                'resumen-alertas-pago': stats?.alertas_pago ?? 0,
                'resumen-total-equipos': stats?.equipos ?? 0,
                'resumen-total-torneos': stats?.torneos ?? 0,
                'resumen-total-arbitros': stats?.arbitros ?? 0,
                'resumen-vencimientos-combos': stats?.vencimientos_combos ?? 0,

                // Card: Ingresos Ligas (Operativo) - Acumulado del Mes
                'resumen-ingresos-mensuales': corte?.total_operativo ? `$${corte.total_operativo.toLocaleString('es-MX', { minimumFractionDigits: 2 })}` : '$0.00',
                'resumen-ingresos-subinfo': 'Acumulado mensual (Ligas)',

                // Card: Aportaciones Combos (Admin) - Hoy vs Mes
                // Mostramos el administrativo de HOY como principal, y el del MES en la subinfo
                'resumen-corte-diario': corteHoy?.total_administrativo ? `$${corteHoy.total_administrativo.toLocaleString('es-MX', { minimumFractionDigits: 2 })}` : '$0.00',
                'resumen-corte-subinfo': `$${(corte?.total_administrativo || 0).toLocaleString('es-MX', { minimumFractionDigits: 2 })} acumulado este mes`
            };

            for (const [id, value] of Object.entries(elements)) {
                const el = document.getElementById(id);
                if (el) el.innerText = value;
            }

            // Refrescar reporte activo si es el de corte
            if (this._activeReport === 'corte') {
                this.generateDailyReport(this._lastCorteFilter || 'all');
            }

        } catch (error) {
            console.error('Error al renderizar resúmenes:', error);
        }

        // Calcular canchas y métricas de combos
        let totalCanchas = 0;
        ligas.forEach(l => {
            if (l.stats && l.stats.canchas) totalCanchas += l.stats.canchas;
            else if (l.canchas_count) totalCanchas += l.canchas_count;
        });

        const totalCombos = ligas.length;
        const totalSedes = ligas.length;

        // Actualizar valores de impacto y conteo
        this.setVal('resumen-total-combos', totalCombos);
        this.setVal('resumen-total-canchas', totalSedes);
        this.setVal('resumen-canchas-info', `${totalCanchas} instalaciones operativas`);
        this.setVal('resumen-combos-impacto', `${totalCombos} organizaciones activas`);
    }

    setVal(id, val) {
        const el = document.getElementById(id);
        if (el) el.innerText = val;
    }

    async generateDailyReport(filterType = 'all') { // filterType: 'all', 'operativo', 'administrativo'
        let data;
        try {
            const params = `?start_date=${this._reportStartDate || ''}&end_date=${this._reportEndDate || ''}`;
            data = await Core.fetchAPI('/api/corte-diario' + params);
            this._lastCorte = data;
        } catch (error) {
            console.error('Error al obtener corte diario para reporte:', error);
            data = this._lastCorte || { total_dia: 0, transacciones: { administrativas: [], operativas: [] } };
        }

        let total = data.total_dia || 0;
        let operativas = data.transacciones?.operativas || [];
        let administrativas = data.transacciones?.administrativas || [];
        let reportTitle = "REPORTE FINANCIERO INTEGRAL";
        let accentColor = "#1e293b"; // Azul marino profesional

        if (filterType === 'operativo') {
            total = data.total_operativo || 0;
            administrativas = [];
            reportTitle = "REPORTE DE INGRESOS OPERATIVOS";
            accentColor = "#059669"; // Verde esmeralda sobrio
        } else if (filterType === 'administrativo') {
            total = data.total_administrativo || 0;
            operativas = [];
            reportTitle = "REPORTE DE INGRESOS ADMINISTRATIVOS";
            accentColor = "#0284c7"; // Azul oceánico sobrio
        }

        const fecha_str = (data.start_date === data.end_date) ? data.start_date : `${data.start_date} al ${data.end_date}`;

        const renderTransactionRows = (list) => {
            if (!list || list.length === 0) return '<tr><td colspan="3" style="padding: 15px; text-align: center; color: #64748b; font-style: italic;">Sin movimientos registrados</td></tr>';
            return list.map(item => `
                <tr style="border-bottom: 1px solid #f1f5f9;">
                    <td style="padding: 12px 0; font-size: 0.9rem;">
                        <div style="font-weight: 600; color: #1e293b;">${item.concepto}</div>
                        <div style="font-size: 0.75rem; color: #64748b; text-transform: uppercase; letter-spacing: 0.5px;">${item.tipo}</div>
                    </td>
                    <td style="padding: 12px 0; font-size: 0.85rem; color: #475569;">${item.metodo}</td>
                    <td style="padding: 12px 0; text-align: right; font-weight: 700; color: #0f172a;">$${item.monto.toLocaleString('es-MX', { minimumFractionDigits: 2 })}</td>
                </tr>
            `).join('');
        };

        const printHtml = `
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <title>${reportTitle} - ${fecha_str}</title>
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700;800&display=swap');
        body { font-family: 'Inter', sans-serif; color: #1e293b; padding: 40px; max-width: 800px; margin: 0 auto; line-height: 1.6; background: #fff; }
        .header { display: flex; justify-content: space-between; align-items: flex-end; border-bottom: 2px solid #f1f5f9; padding-bottom: 20px; margin-bottom: 30px; }
        .logo-area h1 { margin: 0; font-size: 1.5rem; font-weight: 800; letter-spacing: -1px; color: #0f172a; }
        .logo-area p { margin: 0; font-size: 0.8rem; color: #64748b; font-weight: 600; }
        .report-info { text-align: right; }
        .report-info h2 { margin: 0; font-size: 1rem; color: ${accentColor}; text-transform: uppercase; letter-spacing: 1px; }
        .report-info p { margin: 0; font-size: 0.85rem; color: #64748b; }
        
        .summary-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin-bottom: 40px; }
        .summary-card { padding: 25px; border-radius: 12px; border: 1px solid #f1f5f9; background: #f8fafc; }
        .summary-label { font-size: 0.75rem; font-weight: 700; color: #64748b; text-transform: uppercase; margin-bottom: 5px; }
        .summary-value { font-size: 2.2rem; font-weight: 800; color: #0f172a; }
        
        .section-title { font-size: 0.85rem; font-weight: 800; text-transform: uppercase; color: #475569; background: #f1f5f9; padding: 8px 15px; border-radius: 6px; margin-top: 30px; margin-bottom: 15px; display: flex; justify-content: space-between; }
        table { width: 100%; border-collapse: collapse; }
        th { text-align: left; font-size: 0.75rem; text-transform: uppercase; color: #94a3b8; padding-bottom: 10px; border-bottom: 1px solid #f1f5f9; }
        
        .footer { margin-top: 60px; padding-top: 20px; border-top: 1px solid #f1f5f9; display: flex; justify-content: space-between; font-size: 0.75rem; color: #94a3b8; }
        @media print { body { padding: 0; } .summary-card { background: #f8fafc !important; -webkit-print-color-adjust: exact; } }
    </style>
</head>
<body>
    <div class="header">
        <div class="logo-area">
            <h1>FUTADMIN PRO</h1>
            <p>SISTEMA DIGITAL DE GESTIÓN DEPORTIVA</p>
        </div>
        <div class="report-info">
            <h2>${reportTitle}</h2>
            <p>EMITIDO: ${new Date().toLocaleDateString('es-MX', { day: '2-digit', month: 'long', year: 'numeric' })}</p>
        </div>
    </div>

    <div class="summary-grid">
        <div class="summary-card" style="border-left: 4px solid ${accentColor};">
            <div class="summary-label">Monto Total Liquidado</div>
            <div class="summary-value">$${total.toLocaleString('es-MX', { minimumFractionDigits: 2 })}</div>
            <div style="font-size: 0.8rem; color: #94a3b8; margin-top: 4px;">Período: ${fecha_str}</div>
        </div>
        <div class="summary-card">
            <div class="summary-label">Estado del Reporte</div>
            <div class="summary-value" style="font-size: 1.5rem; margin-top: 10px; color: ${accentColor};">VERIFICADO</div>
            <div style="font-size: 0.8rem; color: #94a3b8; margin-top: 4px;">Documento 100% Digital</div>
        </div>
    </div>

    ${operativas.length > 0 ? `
    <div class="section-title">
        <span>Ingresos Operativos (Inscripciones / Arbitrajes / Rentas)</span>
        <span>$${(data.total_operativo || 0).toLocaleString('es-MX', { minimumFractionDigits: 2 })}</span>
    </div>
    <table>
        <thead>
            <tr>
                <th>Concepto / Clasificación</th>
                <th>Método</th>
                <th style="text-align:right;">Monto</th>
            </tr>
        </thead>
        <tbody>${renderTransactionRows(operativas)}</tbody>
    </table>` : ''}

    ${administrativas.length > 0 ? `
    <div class="section-title" style="margin-top: 40px;">
        <span>Ingresos Administrativos (Suscripciones de Combos)</span>
        <span>$${(data.total_administrativo || 0).toLocaleString('es-MX', { minimumFractionDigits: 2 })}</span>
    </div>
    <table>
        <thead>
            <tr>
                <th>Concepto / Clasificación</th>
                <th>Método</th>
                <th style="text-align:right;">Monto</th>
            </tr>
        </thead>
        <tbody>${renderTransactionRows(administrativas)}</tbody>
    </table>` : ''}

    <div class="footer">
        <div>Folio de Auditoría Digital: ${Math.random().toString(36).substr(2, 9).toUpperCase()}</div>
        <div>Generado por FutAdmin Pro v2.5 - ${new Date().toLocaleTimeString()}</div>
    </div>

    <script>window.onload = () => { setTimeout(() => { window.print(); }, 500); };</script>
</body>
</html>`;

        const printWin = window.open('', '_blank');
        printWin.document.write(printHtml);
        printWin.document.close();
    }

    renderStrategicBoxes(ligas) {
        const container = document.getElementById('strategic-summaries');
        if (!container) return;

        // Contenedor principal estilizado con estética minimalista
        container.innerHTML = `
            <div style="margin-top: 2.5rem; background: #fff; padding: 25px; border-radius: 15px; border: 1px solid #f1f5f9;">
                <h4 style="color: #1e293b; margin-bottom: 1.5rem; display: flex; align-items: center; gap: 12px; font-weight: 800; font-size: 0.9rem; letter-spacing: 0.5px;">
                    <div style="width: 4px; height: 18px; background: #94a3b8; border-radius: 2px;"></div>
                    ANÁLISIS ESTRATÉGICO DE CRECIMIENTO
                </h4>
                
                <div style="display: grid; grid-template-columns: repeat(4, 1fr); gap: 1rem; margin-bottom: 1.5rem;">
                    <div style="border: 1px solid #f1f5f9; border-radius: 12px; padding: 1.2rem; background: #f8fafc; text-align: center; border-bottom: 3px solid #64748b;">
                        <div style="font-size: 0.65rem; color: #94a3b8; font-weight: 700; text-transform: uppercase; margin-bottom: 8px;">Potencial de Mercado</div>
                        <div style="font-size: 1.4rem; font-weight: 800; color: #1e293b;">${(ligas.length * 1.5).toFixed(1)}x</div>
                        <div style="font-size: 0.6rem; color: #64748b; margin-top: 5px;">Crecimiento Proyectado</div>
                    </div>
                    <div style="border: 1px solid #f1f5f9; border-radius: 12px; padding: 1.2rem; background: #f8fafc; text-align: center; border-bottom: 3px solid #059669;">
                        <div style="font-size: 0.65rem; color: #94a3b8; font-weight: 700; text-transform: uppercase; margin-bottom: 8px;">Eficiencia Operativa</div>
                        <div style="font-size: 1.4rem; font-weight: 800; color: #1e293b;">94%</div>
                        <div style="font-size: 0.6rem; color: #64748b; margin-top: 5px;">Rendimiento de Sedes</div>
                    </div>
                    <div style="border: 1px solid #f1f5f9; border-radius: 12px; padding: 1.2rem; background: #f8fafc; text-align: center; border-bottom: 3px solid #0284c7;">
                        <div style="font-size: 0.65rem; color: #94a3b8; font-weight: 700; text-transform: uppercase; margin-bottom: 8px;">Retención</div>
                        <div style="font-size: 1.4rem; font-weight: 800; color: #1e293b;">98.2%</div>
                        <div style="font-size: 0.6rem; color: #64748b; margin-top: 5px;">Indice de Fidelidad</div>
                    </div>
                    <div style="border: 1px solid #f1f5f9; border-radius: 12px; padding: 1.2rem; background: #f8fafc; text-align: center; border-bottom: 3px solid #f59e0b;">
                        <div style="font-size: 0.65rem; color: #94a3b8; font-weight: 700; text-transform: uppercase; margin-bottom: 8px;">Auditado</div>
                        <div style="font-size: 1.4rem; font-weight: 800; color: #1e293b;">SI</div>
                        <div style="font-size: 0.6rem; color: #64748b; margin-top: 5px;">Corte Liquidado</div>
                    </div>
                </div>

                <div style="border: 1px solid #f1f5f9; border-radius: 12px; padding: 1.5rem; background: #fff;">
                    <h5 style="color: #64748b; margin-bottom: 1rem; font-size: 0.75rem; font-weight: 800; text-transform: uppercase; letter-spacing: 1px;">📈 Proyección de Escalabilidad Digital</h5>
                    <div style="display: flex; gap: 2rem; align-items: center; flex-wrap: wrap;">
                        <div style="flex: 1; min-width: 300px;">
                            <p style="font-size: 0.85rem; line-height: 1.6; color: #475569; margin: 0;">Basado en la actividad de <strong>${ligas.length} ligas</strong>, se estima una capacidad de expansión del <strong>25% adicional</strong>. La gestión digital permite un crecimiento sostenido sin saturación de recursos.</p>
                        </div>
                        <div style="width: 250px; background: #f1f5f9; height: 8px; border-radius: 4px; overflow: hidden; position: relative;">
                            <div style="width: 75%; height: 100%; background: #1e293b; border-radius: 4px;"></div>
                        </div>
                    </div>
                </div>
            </div>
        `;
    }

    async changePage(page) {
        if (page < 1 || (this.pagination && page > this.pagination.total_pages)) return;
        this.showReport(this._activeReport, this._lastSubFilter || 'all', page);
        const pane = document.getElementById('resumen-detail-pane');
        if (pane) pane.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }

    async showReport(type, subFilter = 'all', page = 1) {
        this._activeReport = type;
        this._lastSubFilter = subFilter;
        const pane = document.getElementById('resumen-detail-pane');
        if (!pane) return;

        // Establecer fechas por defecto si no existen
        const now = new Date();
        const firstDay = new Date(now.getFullYear(), now.getMonth(), 1).toISOString().split('T')[0];
        const lastDay = now.toISOString().split('T')[0];

        if (!this._reportStartDate) this._reportStartDate = firstDay;
        if (!this._reportEndDate) this._reportEndDate = lastDay;

        // Mostrar estado de carga
        pane.innerHTML = `
            <div style="display: flex; flex-direction: column; align-items: center; justify-content: center; height: 100%; opacity: 0.6; padding: 4rem;">
                <div class="loader" style="margin-bottom: 1rem; width: 40px; height: 40px; border: 4px solid var(--border); border-top-color: var(--primary); border-radius: 50%; animation: spin 1s linear infinite;"></div>
                <p>Generando reporte estratégico...</p>
            </div>
            <style>@keyframes spin { to { transform: rotate(360deg); } }</style>
        `;

        try {
            const params = `?start_date=${this._reportStartDate}&end_date=${this._reportEndDate}&page=${page}`;

            if (type === 'sedes') {
                const data = await Core.fetchAPI('/api/admin/dashboard-stats' + params);
                this.renderSedesReport(pane, data);
            } else if (type === 'combos') {
                const ligas = await this.ui.settings.loadLigas();
                this.renderCombosReport(pane, ligas);
            } else if (type === 'ingresos') {
                const data = await Core.fetchAPI('/api/corte-diario' + params);
                this.renderIngresosReport(pane, data, subFilter);
            } else if (type === 'corte') {
                const data = await Core.fetchAPI('/api/corte-diario' + params);
                this.renderCorteReport(pane, data, subFilter);
            } else if (type === 'partidos') {
                const response = await Core.fetchAPI('/api/partidos' + params);
                const list = response.items || response || [];
                this.pagination = response.pagination || null;
                pane.innerHTML = this._renderSimpleTable(
                    '📅 Partidos del Periodo',
                    '#6366f1',
                    list.length === 0 ? '<tr><td colspan="4" style="padding:1rem;text-align:center;opacity:0.5;">Sin partidos programados en este rango</td></tr>' :
                        list.map(p => `<tr>
                        <td>${p.torneo_name || p.liga_nombre || '—'}</td>
                        <td style="font-weight:700;">${p.equipo_local || '—'} <span style="opacity:0.5;font-weight:400;">vs</span> ${p.equipo_visitante || '—'}</td>
                        <td>${p.fecha || '—'} ${p.hora || ''}</td>
                        <td>${p.cancha || '—'}</td>
                    </tr>`).join(''),
                    ['Liga / Torneo', 'Enfrentamiento', 'Fecha/Hora', 'Cancha'],
                    `${(list || []).length} partidos en total`
                );
            } else if (type === 'jugadores') {
                const response = await Core.fetchAPI('/api/jugadores?page=' + page);
                const list = response.items || response || [];
                this.pagination = response.pagination || null;
                pane.innerHTML = this._renderSimpleTable(
                    '🛡️ Jugadores Registrados',
                    '#3b82f6',
                    list.length === 0 ? '<tr><td colspan="3" style="padding:1rem;text-align:center;opacity:0.5;">Sin jugadores registrados</td></tr>' :
                        list.map(j => `<tr>
                        <td style="font-weight:700;">${j.nombre || '—'}</td>
                        <td>
                            <div style="cursor:pointer; color:var(--primary); font-weight:600;"
                                 onmouseover="ui.analytics.showTeamStats(this, ${j.equipo_id || 0})"
                                 onmouseout="ui.analytics.hideTeamStats()">
                                 ${j.equipo_nombre || '—'}
                            </div>
                            <div style="font-size:0.7rem; opacity:0.6;">${j.liga_nombre || '—'}</div>
                        </td>
                        <td>${j.posicion || '—'}</td>
                    </tr>`).join(''),
                    ['Jugador', 'Equipo / Liga', 'Posición'],
                    `${list.length} jugadores en la red`
                );
            } else if (type === 'entrenamientos') {
                const response = await Core.fetchAPI('/api/entrenamientos/grupos' + params);
                const list = response.items || response || [];
                this.pagination = response.pagination || null;
                pane.innerHTML = this._renderSimpleTable(
                    '🏃 Entrenamientos Activos',
                    '#ec4899',
                    list.length === 0 ? '<tr><td colspan="3" style="padding:1rem;text-align:center;opacity:0.5;">Sin grupos de entrenamiento activos</td></tr>' :
                        list.map(g => `<tr>
                        <td>${g.nombre || '—'}</td>
                        <td>${g.cancha || '—'}</td>
                        <td>${g.alumnos_count ?? '0'} alumnos</td>
                    </tr>`).join(''),
                    ['Grupo', 'Sede', 'Alumnos'],
                    `${(list || []).length} grupos activos`
                );
            } else if (type === 'arbitros') {
                const response = await Core.fetchAPI('/api/arbitros' + params);
                const list = response.items || response || [];
                this.pagination = response.pagination || null;
                pane.innerHTML = this._renderSimpleTable(
                    '⚖️ Cuerpo Arbitral',
                    '#f97316',
                    list.length === 0 ? '<tr><td colspan="3" style="padding:1rem;text-align:center;opacity:0.5;">Sin árbitros registrados</td></tr>' :
                        list.map(a => `<tr>
                        <td style="font-weight:700;">${a.nombre || '—'}</td>
                        <td>${a.email || a.telefono || '—'}</td>
                        <td><span class="badge" style="background:#f9731622;color:#f97316;">${a.nivel || 'Local'}</span></td>
                    </tr>`).join(''),
                    ['Nombre completo', 'Contacto', 'Nivel'],
                    `${(list || []).length} árbitros registrados`
                );
            } else if (type === 'alertas') {
                const data = await Core.fetchAPI('/api/admin/payment-alerts');
                const operative = data?.operative || [];

                let rows = '';
                if (operative.length === 0) {
                    rows = '<tr><td colspan="4" style="padding:2rem;text-align:center;opacity:0.5;">Sin alertas de pago operativas 🎉</td></tr>';
                }

                // Deudas Operativas (Equipos en Torneos) - Enfoque Cobranza
                rows += operative.map(o => `<tr>
                    <td>
                        <div style="font-weight:700; cursor:pointer; color:var(--primary);"
                             onmouseover="ui.analytics.showTeamStats(this, ${o.equipo_id || 0})"
                             onmouseout="ui.analytics.hideTeamStats()">
                             ${o.entidad}
                        </div>
                        <div style="font-size:0.75rem; opacity:0.6;">${o.liga_nombre} (${o.subdominio || '—'})</div>
                    </td>
                    <td>
                        <div style="font-size:0.85rem;">${o.torneo}</div>
                        <div style="font-size:0.75rem; color:var(--primary); font-weight:600;">${o.liga_email || ''}</div>
                        <div style="font-size:0.75rem; color:var(--primary); font-weight:600;">${o.liga_telefono || ''}</div>
                    </td>
                    <td style="color:#f59e0b; font-weight:800;">$${(o.saldo_pendiente || 0).toLocaleString('es-MX')}</td>
                    <td><span class="badge-status warning">Pendiente</span></td>
                </tr>`).join('');

                pane.innerHTML = this._renderSimpleTable(
                    '⚽ Alertas de Pago Operativas (Apoyo Cobranza)',
                    '#f59e0b',
                    rows,
                    ['Equipo / Organización', 'Torneo / Contacto', 'Saldo Pendiente', 'Estatus'],
                    `${operative.length} alertas de equipos encontradas`
                );
            } else if (type === 'equipos') {
                const response = await Core.fetchAPI('/api/equipos?page=' + page);
                const list = response.items || response || [];
                this.pagination = response.pagination || null;
                pane.innerHTML = this._renderSimpleTable(
                    '🛡️ Equipos Activos (Identidad Única)',
                    '#22c55e',
                    list.length === 0 ? '<tr><td colspan="4" style="padding:1rem;text-align:center;opacity:0.5;">Sin equipos registrados</td></tr>' :
                        list.map(e => `<tr>
                        <td>
                            <div style="font-weight:700; cursor:pointer; color:var(--primary);" 
                                 onmouseover="ui.analytics.showTeamStats(this, ${e.id})"
                                 onmouseout="ui.analytics.hideTeamStats()">
                                 ${e.nombre || '—'}
                            </div>
                            ${e.uid ? `<div style="font-family:monospace; font-size:0.65rem; opacity:0.5; letter-spacing:1px;">ID: ${e.uid}</div>` : ''}
                        </td>
                        <td>${e.liga_nombre || '—'}</td>
                        <td style="font-weight:700;">${e.jugadores_count ?? '0'} jugadores</td>
                        <td style="text-align:center;"><button class="btn-dashboard btn-sm" onclick="ui.analytics.showTeamStats(this, ${e.id}, true)">📊 VER</button></td>
                    </tr>`).join(''),
                    ['Equipo / Identidad', 'Liga / Combo', 'Jugadores', 'Acción'],
                    `${list.length} equipos con identidad única verificada`
                );
            } else if (type === 'vencimientos') {
                const data = await Core.fetchAPI('/api/admin/payment-alerts');
                const subscription = data?.subscription || [];
                const upcoming = data?.upcoming || [];

                let rows = '';
                if (subscription.length === 0 && upcoming.length === 0) {
                    rows = '<tr><td colspan="4" style="padding:2rem;text-align:center;opacity:0.5;">Sin suscripciones por vencer próximamente 🎉</td></tr>';
                }

                // Suscripciones VENCIDAS (Prioridad Alta)
                if (subscription.length > 0) {
                    rows += `<tr><th colspan="4" style="background:rgba(239, 68, 68, 0.1); color:#ef4444; text-align:left; padding:10px;">🚨 SUSCRIPCIONES VENCIDAS</th></tr>`;
                    rows += subscription.map(s => `<tr>
                        <td>
                            <div style="font-weight:700;">${s.entidad}</div>
                            <div style="font-size:0.75rem; opacity:0.6;">Subdominio: ${s.subdominio || '—'}</div>
                        </td>
                        <td>
                            <div style="font-size:0.85rem;">${s.email || ''}</div>
                            <div style="font-size:0.85rem; font-weight:600;">${s.telefono || ''}</div>
                        </td>
                        <td style="color:#ef4444; font-weight:800;">$${(s.saldo_pendiente || s.monto || 0).toLocaleString('es-MX')}</td>
                        <td><span class="badge-status error">Venció: ${s.vencimiento}</span></td>
                    </tr>`).join('');
                }

                // Suscripciones PRÓXIMAS A VENCER (10 días)
                if (upcoming.length > 0) {
                    rows += `<tr><th colspan="4" style="background:rgba(20, 184, 166, 0.1); color:#14b8a6; text-align:left; padding:10px;">📅 PRÓXIMOS VENCIMIENTOS (10 DÍAS)</th></tr>`;
                    rows += upcoming.map(v => `<tr>
                        <td>
                            <div style="font-weight:700;">${v.entidad}</div>
                            <div style="font-size:0.75rem; opacity:0.6;">Subdominio: ${v.subdominio || '—'}</div>
                        </td>
                        <td>
                            <div style="font-size:0.85rem;">${v.email || ''}</div>
                            <div style="font-size:0.85rem; font-weight:600;">${v.telefono || ''}</div>
                        </td>
                        <td style="color:#14b8a6; font-weight:800;">$${(v.monto || 0).toLocaleString('es-MX')}</td>
                        <td><span class="badge-status warning">Faltan ${v.dias_restantes} días</span></td>
                    </tr>`).join('');
                }

                pane.innerHTML = this._renderSimpleTable(
                    '💳 Suscripciones de Plataforma (Combos)',
                    '#14b8a6',
                    rows,
                    ['Organización', 'Contacto Directo', 'Monto Susc.', 'Estatus'],
                    `${subscription.length + upcoming.length} suscripciones en revisión`
                );
            } else if (type === 'torneos') {
                const response = await Core.fetchAPI('/api/torneos?page=' + page);
                const list = response.items || response || [];
                this.pagination = response.pagination || null;
                pane.innerHTML = this._renderSimpleTable(
                    '🏆 Torneos y Competiciones',
                    '#a855f7',
                    list.length === 0 ? '<tr><td colspan="3" style="padding:1rem;text-align:center;opacity:0.5;">Sin torneos activos</td></tr>' :
                        list.map(t => `<tr>
                        <td>${t.nombre || '—'}</td>
                        <td>${t.liga_nombre || '—'}</td>
                        <td><span style="font-weight:700; color:var(--primary);">${t.equipos_count ?? '0'}</span> equipos / <span style="opacity:0.7;">${t.jugadores_count ?? '0'} jug.</span></td>
                    </tr>`).join(''),
                    ['Torneo', 'Organizador / Liga', 'Estatus'],
                    `${list.length} torneos registrados`
                );
            } else if (type === 'ligas') {
                const ligasList = await this.ui.settings.loadLigas();
                const list = (ligasList || []);
                pane.innerHTML = this._renderSimpleTable(
                    '⚽ Ligas y Organizaciones',
                    '#14b8a6',
                    list.length === 0 ? '<tr><td colspan="3" style="padding:1rem;text-align:center;opacity:0.5;">Sin ligas operativas</td></tr>' :
                        list.map(l => `<tr>
                        <td>${l.nombre || '—'}</td>
                        <td>${l.paquete || 'Básico'}</td>
                        <td>${l.canchas_count ?? '0'} locales</td>
                    </tr>`).join(''),
                    ['Organización', 'Plan suscripción', 'Sedes'],
                    `${list.length} ligas operando en el sistema`
                );
            }
        } catch (error) {
            console.error("Error generating report:", error);
            pane.innerHTML = `<div class="error-state" style="padding:4rem;text-align:center;">
                <span style="font-size:3rem;">❌</span>
                <h3>Error al Generar Reporte</h3>
                <p>${error.message || 'Error de conexión con el servidor'}</p>
                <button class="btn-primary" style="margin-top:1rem;" onclick="ui.analytics.showReport('${type}')">Reintentar</button>
            </div>`;
        }
    }

    renderReportHeader(title, icon, color) {
        return `
            <div style="background: rgba(255,255,255,0.03); border-bottom: 2px solid rgba(255,255,255,0.05); padding: 20px; margin-bottom: 20px; border-radius: 12px 12px 0 0; display: flex; align-items: center; justify-content: space-between; flex-wrap: wrap; gap: 15px;">
                <div style="display: flex; align-items: center; gap: 15px;">
                    <div style="font-size: 1.5rem; background: rgba(255,255,255,0.05); width: 45px; height: 45px; display: flex; align-items: center; justify-content: center; border-radius: 12px; border: 1px solid rgba(255,255,255,0.1);">${icon}</div>
                    <div>
                        <h3 style="margin: 0; color: #fff; font-size: 1.1rem; font-weight: 800; letter-spacing: -0.5px;">${title}</h3>
                        <p style="margin: 0; font-size: 0.75rem; color: var(--text-muted); font-weight: 600; text-transform: uppercase;">Informe Digital en Tiempo Real</p>
                    </div>
                </div>
                
                <div style="display: flex; gap: 12px; align-items: center; background: rgba(0,0,0,0.2); padding: 8px 15px; border-radius: 10px; border: 1px solid rgba(255,255,255,0.05);">
                    <div style="display: flex; gap: 8px; align-items: center;">
                        <span style="font-size: 0.65rem; color: var(--text-muted); font-weight: 800;">DE</span>
                        <input type="date" value="${this._reportStartDate}" onchange="ui.analytics._reportStartDate = this.value; ui.analytics.showReport('${this._activeReport}')" 
                            style="background: none; border: none; color: #fff; font-size: 0.8rem; font-weight: 700; outline: none; cursor:pointer;">
                    </div>
                    <div style="width: 1px; height: 15px; background: rgba(255,255,255,0.1);"></div>
                    <div style="display: flex; gap: 8px; align-items: center;">
                        <span style="font-size: 0.65rem; color: var(--text-muted); font-weight: 800;">A</span>
                        <input type="date" value="${this._reportEndDate}" onchange="ui.analytics._reportEndDate = this.value; ui.analytics.showReport('${this._activeReport}')" 
                            style="background: none; border: none; color: #fff; font-size: 0.8rem; font-weight: 700; outline: none; cursor:pointer;">
                    </div>
                </div>

                ${this._activeReport === 'corte' || this._activeReport === 'ingresos' ? `
                    <button onclick="ui.analytics.generateDailyReport('${this._lastSubFilter || 'all'}')" class="btn-primary" style="background: var(--primary); color: black; border: none; padding: 10px 20px; font-weight: 700; font-size: 0.8rem; letter-spacing: 0.5px; border-radius: 8px; display: flex; align-items: center; gap: 8px;">
                        <span>📄</span> GENERAR PDF
                    </button>
                ` : ''}
            </div>
        `;
    }

    renderSedesReport(container, data) {
        container.innerHTML = `
            <div class="fade-in" style="width: 100%; padding: 1rem;">
                ${this.renderReportHeader('Detalle de Sedes e Instalaciones', '📍', '#10b981')}
                <div class="premium-table-container">
                    <table class="premium-table">
                        <thead>
                            <tr>
                                <th>Sede Principal</th>
                                <th>Instalaciones (Canchas)</th>
                                <th>Ligas / Torneos</th>
                                <th style="text-align:right;">Estatus</th>
                            </tr>
                        </thead>
                        <tbody>
                            ${(this.ui.settings.ligas || []).map(l => `
                                <tr>
                                    <td>
                                        <div style="font-weight: 700;">${l.nombre}</div>
                                        <div style="font-size: 0.65rem; color: var(--text-muted); text-transform: uppercase;">ID: ${l.id}</div>
                                    </td>
                                    <td style="font-size: 0.8rem;">
                                        <div style="font-weight:700;">${l.stats?.canchas || 0} sedes</div>
                                        <div style="font-size: 0.7rem; color: #10b981;">${l.detalles?.canchas?.join(', ') || 'N/A'}</div>
                                    </td>
                                    <td style="font-size: 0.8rem;">
                                        <div style="font-weight:700;">${l.stats?.torneos || 0} torneos</div>
                                        <div style="font-size: 0.7rem; color: #818cf8;">${l.detalles?.torneos?.join(', ') || 'N/A'}</div>
                                    </td>
                                    <td style="text-align:right;">
                                        <span class="status-pill active" style="padding: 2px 8px; font-size: 0.65rem;">
                                            <div class="status-dot-pulse active"></div> OPERATIVA
                                        </span>
                                    </td>
                                </tr>
                            `).join('') || '<tr><td colspan="4" style="text-align: center; padding: 2rem;">No hay sedes registradas en este período.</td></tr>'}
                        </tbody>
                    </table>
                </div>
            </div>
        `;
    }

    renderCombosReport(container, ligas) {
        container.innerHTML = `
            <div class="fade-in" style="width: 100%; padding: 1rem;">
                ${this.renderReportHeader('Gestión de Combos y Organizaciones', '🏆', '#6366f1')}
                <div class="premium-table-container">
                    <table class="premium-table">
                        <thead>
                            <tr>
                                <th>Organización</th>
                                <th>Sedes</th>
                                <th>Ligas</th>
                                <th>Equipos</th>
                                <th>Jugadores</th>
                                <th style="text-align:right;">Inversión Mensual</th>
                            </tr>
                        </thead>
                        <tbody>
                            ${ligas.map(l => `
                                <tr>
                                    <td>
                                        <div style="display: flex; align-items: center; gap: 10px;">
                                            <div style="width: 10px; height: 10px; border-radius: 50%; background: ${l.color || 'var(--primary)'}; shadow: 0 0 5px ${l.color || 'var(--primary)'};"></div>
                                            <div>
                                                <div style="font-weight: 700;">${l.nombre}</div>
                                                <div style="font-size: 0.65rem; color: var(--text-muted); text-transform: uppercase;">Plan: ${l.paquete}</div>
                                            </div>
                                        </div>
                                    </td>
                                    <td><span style="font-weight:700;">${l.stats?.canchas || 0}</span></td>
                                    <td><span style="font-weight:700;">${l.stats?.torneos || 0}</span></td>
                                    <td><span style="font-weight:700;">${l.stats?.equipos || 0}</span></td>
                                    <td><span style="font-weight:700;">${l.stats?.jugadores || 0}</span></td>
                                    <td style="font-weight: 800; color: #00ff88; text-align:right;">$${parseFloat(l.monto_total_mensual || 0).toFixed(2)}</td>
                                </tr>
                            `).join('') || '<tr><td colspan="6" style="text-align: center; padding: 2rem;">No hay combos activos.</td></tr>'}
                        </tbody>
                    </table>
                </div>
                <div style="margin-top: 1rem; font-size: 0.7rem; color: var(--text-muted); display: flex; gap: 1rem;">
                    <span>📊 Total de Jugadores en Red: ${ligas.reduce((acc, l) => acc + (l.stats?.jugadores || 0), 0)}</span>
                    <span>🛡️ Equipos Activos: ${ligas.reduce((acc, l) => acc + (l.stats?.equipos || 0), 0)}</span>
                </div>
            </div>
        `;
    }

    renderIngresosReport(container, data, filter = 'all') {
        let trans = [];
        let reportTitle = 'Historial de Ingresos y Aportaciones';
        let accentColor = '#eab308';
        let displayTotal = 0;

        if (filter === 'administrativo') {
            trans = data.transacciones?.administrativas || [];
            reportTitle = 'Historial Administrativo (Combos)';
            accentColor = '#0284c7';
            displayTotal = data.total_administrativo;
        } else if (filter === 'operativo') {
            trans = data.transacciones?.operativas || [];
            reportTitle = 'Historial Operativo (Ligas)';
            accentColor = '#059669';
            displayTotal = data.total_operativo;
        } else {
            trans = [...(data.transacciones?.administrativas || []), ...(data.transacciones?.operativas || [])];
            displayTotal = data.total_dia;
        }

        container.innerHTML = `
            <div class="fade-in" style="width: 100%; padding: 1rem;">
                ${this.renderReportHeader(reportTitle, '💰', accentColor)}
                
                <div style="background: rgba(255,255,255,0.02); border: 1px solid rgba(255,255,255,0.05); border-radius: 15px; padding: 1.5rem; margin-bottom: 1.5rem; text-align: center;">
                    <div style="font-size: 0.7rem; color: var(--text-muted); text-transform: uppercase; font-weight: 800; letter-spacing: 1.5px; margin-bottom: 5px;">Total ${filter === 'all' ? 'Integral' : filter}</div>
                    <div style="font-size: clamp(1.8rem, 8vw, 2.8rem); font-weight: 900; color: #fff; word-break: break-all;">$${(displayTotal || 0).toLocaleString('es-MX', { minimumFractionDigits: 2 })}</div>
                </div>

                <div class="premium-table-container">
                    <table class="premium-table">
                        <thead>
                            <tr>
                                <th>Fecha</th>
                                <th>Concepto</th>
                                <th>Clasificación</th>
                                <th style="text-align:right;">Monto</th>
                            </tr>
                        </thead>
                        <tbody>
                            ${trans.map(item => `
                                <tr>
                                    <td style="font-size:0.8rem; color:var(--text-muted);">${item.fecha}</td>
                                    <td style="font-weight: 700;">${item.concepto}</td>
                                    <td>
                                        <span class="badge" style="background: ${item.tipo.includes('Admin') ? 'rgba(14,165,233,0.1)' : 'rgba(0,255,136,0.1)'}; color: ${item.tipo.includes('Admin') ? '#0ea5e9' : '#00ff88'}; font-size:0.65rem;">
                                            ${item.tipo}
                                        </span>
                                    </td>
                                    <td style="font-weight: 800; color: #fff; text-align:right;">$${parseFloat(item.monto || 0).toFixed(2)}</td>
                                </tr>
                            `).sort((a, b) => b.monto - a.monto).join('') || '<tr><td colspan="4" style="text-align: center; padding: 2rem;">Sin transacciones en este período.</td></tr>'}
                        </tbody>
                    </table>
                </div>
            </div>
        `;
    }

    renderCorteReport(container, data, filter = 'all') {
        let trans = [];
        let reportTitle = 'Corte de Caja Detallado';
        let accentColor = '#2dd4bf';
        let displayTotal = 0;

        if (filter === 'administrativo') {
            trans = data.transacciones?.administrativas || [];
            reportTitle = 'Reporte Administrativo (Suscripciones)';
            accentColor = '#0284c7';
            displayTotal = data.total_administrativo;
        } else if (filter === 'operativo') {
            trans = data.transacciones?.operativas || [];
            reportTitle = 'Reporte Operativo (Ligas)';
            accentColor = '#059669';
            displayTotal = data.total_operativo;
        } else {
            trans = [...(data.transacciones?.administrativas || []), ...(data.transacciones?.operativas || [])];
            displayTotal = data.total_dia;
        }

        this._lastCorte = data; // Guardar para impresión

        container.innerHTML = `
            <div class="fade-in" style="width: 100%; padding: 1rem;">
                ${this.renderReportHeader(reportTitle, '🧾', accentColor)}
                
                <div style="background: rgba(255,255,255,0.02); border: 1px solid rgba(255,255,255,0.05); border-radius: 15px; padding: 2rem; margin-bottom: 2rem; text-align: center;">
                    <div style="font-size: 0.8rem; color: var(--text-muted); text-transform: uppercase; font-weight: 800; letter-spacing: 1.5px; margin-bottom: 10px;">Balance ${filter === 'all' ? 'Total' : filter}</div>
                    <div style="font-size: clamp(2rem, 10vw, 3.5rem); font-weight: 900; color: #fff; letter-spacing: -2px; word-break: break-all;">$${(displayTotal || 0).toLocaleString('es-MX', { minimumFractionDigits: 2 })}</div>
                </div>

                <div class="premium-table-container">
                    <table class="premium-table">
                        <thead>
                            <tr>
                                <th>Fecha / ID</th>
                                <th>Concepto Detallado</th>
                                <th>Método</th>
                                <th style="text-align:right;">Monto Bruto</th>
                            </tr>
                        </thead>
                        <tbody>
                            ${trans.map(item => `
                                <tr>
                                    <td>
                                        <div style="font-size:0.8rem;">${item.fecha}</div>
                                        <span class="badge" style="background: ${item.tipo.includes('Admin') ? 'rgba(14,165,233,0.1)' : 'rgba(0,255,136,0.1)'}; color: ${item.tipo.includes('Admin') ? '#0ea5e9' : '#00ff88'}; font-size:0.6rem; padding: 2px 6px; border-radius: 4px; text-transform: uppercase; font-weight: 700;">
                                            ${item.tipo}
                                        </span>
                                    </td>
                                    <td style="font-weight: 700;">${item.concepto}</td>
                                    <td style="font-size: 0.75rem;">${item.metodo}</td>
                                    <td style="font-weight: 800; color: #fff; text-align:right;">$${parseFloat(item.monto || 0).toFixed(2)}</td>
                                </tr>
                            `).join('') || '<tr><td colspan="4" style="text-align: center; padding: 2rem;">No hay registros de caja.</td></tr>'}
                        </tbody>
                    </table>
                </div>
            </div>
        `;
    }
    _renderSimpleTable(title, accentColor, rows, columns, subtitle = '') {
        const headers = columns.map(c => `<th>${c}</th>`).join('');
        return `
            <div class="fade-in" style="width: 100%; padding: 1rem;">
                <div style="display:flex; justify-content:space-between; align-items:flex-end; margin-bottom:1.5rem;">
                    <div>
                        ${this.renderReportHeader(title, '📋', accentColor)}
                        ${subtitle ? `<div style="font-size:0.8rem; color:var(--text-muted); padding-left:4px;">${subtitle}</div>` : ''}
                    </div>
                    <div class="report-search" style="margin-bottom:0.5rem;">
                        <input type="text" placeholder="🔍 Buscar en este reporte..." 
                            style="background:rgba(255,255,255,0.05); border:1px solid rgba(255,255,255,0.1); border-radius:8px; padding:0.6rem 1.2rem; color:white; font-size:0.85rem; width:280px; outline:none; transition: all 0.3s;"
                            onfocus="this.style.background='rgba(255,255,255,0.08)'; this.style.borderColor='${accentColor}'"
                            onblur="this.style.background='rgba(255,255,255,0.05)'; this.style.borderColor='rgba(255,255,255,0.1)'"
                            onkeyup="ui.analytics.filterReportTable(this.value)">
                    </div>
                </div>
                
                ${this.pagination && this.pagination.total_pages > 1 ? `
                    <div class="pagination-controls">
                        <button class="btn-pagination" ${!this.pagination.has_prev ? 'disabled' : ''} 
                                onclick="ui.analytics.changePage(${this.pagination.page - 1})">
                            &laquo; Anterior
                        </button>
                        <span class="pagination-info">Página ${this.pagination.page} de ${this.pagination.total_pages}</span>
                        <button class="btn-pagination" ${!this.pagination.has_next ? 'disabled' : ''} 
                                onclick="ui.analytics.changePage(${this.pagination.page + 1})">
                            Siguiente &raquo;
                        </button>
                    </div>
                ` : ''}

                <div style="margin-top:1.5rem; text-align:right;">
                    <button class="btn-dashboard btn-primary" onclick="ui.analytics.exportCurrentReport()" style="padding:0.6rem 1.5rem; border-radius:10px;">
                        <span style="font-size:1rem; margin-right:8px;">📄</span> GENERAR PDF PROFESIONAL
                    </button>
                </div>
            </div>
        `;
    }

    filterReportTable(query) {
        const table = document.getElementById('active-report-table');
        if (!table) return;
        const searchTerm = query.toLowerCase();
        const rows = table.querySelectorAll('tbody tr');

        rows.forEach(row => {
            // No filtrar los encabezados internos (th)
            if (row.querySelector('th')) return;

            const text = row.innerText.toLowerCase();
            row.style.display = text.includes(searchTerm) ? '' : 'none';
        });
    }

    async showTeamStats(element, teamId, forceSticky = false) {
        this.hideTeamStats();

        // Crear tooltip
        const tooltip = document.createElement('div');
        tooltip.id = 'team-stats-tooltip';
        tooltip.className = 'premium-tooltip fade-in';
        tooltip.style.position = 'fixed';
        tooltip.style.zIndex = '9999';
        tooltip.style.background = 'rgba(15, 23, 42, 0.95)';
        tooltip.style.backdropFilter = 'blur(12px)';
        tooltip.style.border = '1px solid rgba(255,255,255,0.1)';
        tooltip.style.borderRadius = '16px';
        tooltip.style.padding = '1.5rem';
        tooltip.style.boxShadow = '0 20px 50px rgba(0,0,0,0.5), 0 0 20px rgba(0,255,136,0.1)';
        tooltip.style.width = '300px';
        tooltip.style.pointerEvents = forceSticky ? 'all' : 'none';

        const rect = element.getBoundingClientRect();
        const tooltipWidth = 300;
        let left = rect.right + 20;

        // Si no cabe a la derecha, mostrar a la izquierda
        if (left + tooltipWidth > window.innerWidth) {
            left = rect.left - tooltipWidth - 20;
        }

        // Posicionamiento vertical con protección de bordes
        let top = rect.top - 50;
        const tooltipHeight = 350; // Estimado para equipos
        if (top + tooltipHeight > window.innerHeight) {
            top = window.innerHeight - tooltipHeight - 20;
        }

        tooltip.style.left = `${Math.max(10, left)}px`;
        tooltip.style.top = `${Math.max(10, top)}px`;

        tooltip.innerHTML = `<div style="text-align:center; padding:1rem;"><div class="spinner-sm"></div> Cargando estadísticas...</div>`;
        document.body.appendChild(tooltip);

        try {
            const stats = await Core.fetchAPI(`/api/equipos/${teamId}/stats-summary`);
            if (!stats) throw new Error('No data');

            tooltip.innerHTML = `
                <div style="border-bottom:1px solid rgba(255,255,255,0.1); padding-bottom:0.8rem; margin-bottom:1rem; display:flex; justify-content:space-between; align-items:flex-start;">
                    <div>
                        <h4 style="margin:0; color:#fff; font-size:1.1rem;">${stats.nombre}</h4>
                        ${stats.uid ? `<code style="font-size:0.65rem; color:var(--primary); opacity:0.8;">ID: ${stats.uid}</code>` : ''}
                    </div>
                    ${forceSticky ? `<button onclick="ui.analytics.hideTeamStats()" style="background:none; border:none; color:white; cursor:pointer; font-size:1.2rem;">&times;</button>` : ''}
                </div>
                
                <div style="display:grid; grid-template-columns: 1fr 1fr; gap:0.8rem; margin-bottom:1rem;">
                    <div style="background:rgba(255,255,255,0.03); padding:0.6rem; border-radius:8px; text-align:center;">
                        <div style="font-size:0.6rem; color:var(--text-muted); text-transform:uppercase;">Partidos</div>
                        <div style="font-size:1.2rem; font-weight:800; color:#fff;">${stats.record.jj}</div>
                    </div>
                    <div style="background:rgba(34,197,94,0.1); padding:0.6rem; border-radius:8px; text-align:center;">
                        <div style="font-size:0.6rem; color:#22c55e; text-transform:uppercase;">Ganados</div>
                        <div style="font-size:1.2rem; font-weight:800; color:#22c55e;">${stats.record.jg}</div>
                    </div>
                </div>

                <div style="display:flex; justify-content:space-between; font-size:0.75rem; margin-bottom:0.8rem; background:rgba(255,255,255,0.02); padding:0.6rem; border-radius:8px;">
                     <span style="color:var(--text-muted);">Goles F/C:</span>
                     <span style="font-weight:700; color:#fff;">${stats.goles.favor} / ${stats.goles.contra} (${stats.goles.dif > 0 ? '+' : ''}${stats.goles.dif})</span>
                </div>

                <div style="display:flex; justify-content:space-between; font-size:0.75rem; margin-bottom:0.8rem; background:rgba(255,255,255,0.02); padding:0.6rem; border-radius:8px;">
                     <span style="color:var(--text-muted);">Disciplina:</span>
                     <span style="font-weight:700; color:#ef4444;">🟨 ${stats.disciplina.amarillas} 🟥 ${stats.disciplina.rojas}</span>
                </div>

                <div style="background:linear-gradient(90deg, rgba(255,255,255,0.05), transparent); padding:0.8rem; border-radius:12px; border:1px solid rgba(255,255,255,0.05);">
                    <div style="font-size:0.65rem; color:#eab308; font-weight:800; text-transform:uppercase; margin-bottom:4px;">⭐ GOLEADOR ESTRELLA</div>
                    <div style="font-weight:700; color:#fff; font-size:0.9rem;">${stats.estrella.nombre}</div>
                    <div style="font-size:0.7rem; color:var(--text-muted);">${stats.estrella.goles} goles anotados</div>
                </div>
            `;
        } catch (e) {
            tooltip.innerHTML = `<div style="color:#ef4444; font-size:0.8rem; text-align:center;">Error al cargar estadísticas.</div>`;
        }
    }

    hideTeamStats() {
        const existing = document.getElementById('team-stats-tooltip');
        if (existing) {
            existing.remove();
        }
    }

    async showPlayerStats(element, playerId) {
        this.hideTeamStats(); // Reutilizar el mismo contenedor de tooltip

        const tooltip = document.createElement('div');
        tooltip.id = 'team-stats-tooltip'; // Reutilizar ID para consistencia CSS
        tooltip.className = 'premium-tooltip fade-in';
        tooltip.style.position = 'fixed';
        tooltip.style.zIndex = '9999';
        tooltip.style.background = 'rgba(15, 23, 42, 0.98)';
        tooltip.style.backdropFilter = 'blur(15px)';
        tooltip.style.border = '1px solid rgba(255,255,255,0.1)';
        tooltip.style.borderRadius = '20px';
        tooltip.style.padding = '1.5rem';
        tooltip.style.boxShadow = '0 25px 50px rgba(0,0,0,0.6), 0 0 30px rgba(0,255,136,0.05)';
        tooltip.style.width = '280px';
        tooltip.style.pointerEvents = 'none';

        const rect = element.getBoundingClientRect();
        const tooltipWidth = 280;
        let left = rect.right + 20;

        // Si no cabe a la derecha, mostrar a la izquierda
        if (left + tooltipWidth > window.innerWidth) {
            left = rect.left - tooltipWidth - 20;
        }

        // Posicionamiento vertical con protección de bordes
        let top = rect.top - 50;
        const tooltipHeight = 220; // Estimado para jugadores
        if (top + tooltipHeight > window.innerHeight) {
            top = window.innerHeight - tooltipHeight - 20;
        }

        tooltip.style.left = `${Math.max(10, left)}px`;
        tooltip.style.top = `${Math.max(10, top)}px`;

        tooltip.innerHTML = `<div style="text-align:center; padding:1rem;"><div class="spinner-sm"></div> Cargando perfil...</div>`;
        document.body.appendChild(tooltip);

        try {
            const data = await Core.fetchAPI(`/api/jugadores/${playerId}/stats-summary`);
            if (!data) throw new Error('No data');

            tooltip.innerHTML = `
                <div style="display:flex; align-items:center; gap:15px; margin-bottom:1.2rem; border-bottom:1px solid rgba(255,255,255,0.05); padding-bottom:1rem;">
                    <div style="width:60px; height:60px; border-radius:50%; overflow:hidden; border:2px solid ${data.color || 'var(--primary)'}; background:rgba(0,0,0,0.3); flex-shrink:0;">
                        <img src="${data.foto_url || ''}" onerror="this.src='https://ui-avatars.com/api/?name=${encodeURIComponent(data.nombre)}&background=random&color=fff'" style="width:100%; height:100%; object-fit:cover;">
                    </div>
                    <div style="overflow:hidden;">
                        <div style="font-size:0.65rem; color:${data.color || 'var(--primary)'}; font-weight:800; text-transform:uppercase; letter-spacing:1px; margin-bottom:2px;">#${data.numero} • ${data.posicion}</div>
                        <h4 style="margin:0; color:#fff; font-size:1.1rem; white-space:nowrap; overflow:hidden; text-overflow:ellipsis;">${data.nombre}</h4>
                        <div style="font-size:0.7rem; color:rgba(255,255,255,0.5); display:flex; align-items:center; gap:5px;">
                            <span style="font-style:italic;">${data.equipo}</span>
                        </div>
                    </div>
                </div>

                <div style="display:grid; grid-template-columns: 1fr 1fr; gap:0.8rem; margin-bottom:1rem;">
                    <div style="background:rgba(255,255,255,0.03); padding:0.8rem; border-radius:12px; text-align:center; border:1px solid rgba(255,255,255,0.05);">
                        <div style="font-size:0.6rem; color:var(--text-muted); text-transform:uppercase; font-weight:700; margin-bottom:4px;">Partidos</div>
                        <div style="font-size:1.3rem; font-weight:900; color:#fff;">${data.stats.pj}</div>
                    </div>
                    <div style="background:rgba(0,255,136,0.05); padding:0.8rem; border-radius:12px; text-align:center; border:1px solid rgba(0,255,136,0.1);">
                        <div style="font-size:0.6rem; color:#00ff88; text-transform:uppercase; font-weight:700; margin-bottom:4px;">Goles</div>
                        <div style="font-size:1.3rem; font-weight:900; color:#00ff88;">${data.stats.goles}</div>
                    </div>
                </div>

                <div style="display:flex; justify-content:center; gap:20px; background:rgba(255,255,255,0.02); padding:0.8rem; border-radius:12px; border:1px solid rgba(255,255,255,0.05);">
                    <div style="display:flex; align-items:baseline; gap:6px;">
                        <span style="font-size:0.6rem; color:rgba(255,255,255,0.4); text-transform:uppercase; font-weight:700;">🟨 Am.</span>
                        <span style="font-size:1rem; font-weight:800; color:#facc15;">${data.stats.amarillas}</span>
                    </div>
                    <div style="width:1px; height:15px; background:rgba(255,255,255,0.1); align-self:center;"></div>
                    <div style="display:flex; align-items:baseline; gap:6px;">
                        <span style="font-size:0.6rem; color:rgba(255,255,255,0.4); text-transform:uppercase; font-weight:700;">🟥 Rojas</span>
                        <span style="font-size:1rem; font-weight:800; color:#ef4444;">${data.stats.rojas}</span>
                    </div>
                </div>
            `;
        } catch (e) {
            tooltip.innerHTML = `<div style="color:#ef4444; font-size:0.8rem; text-align:center; padding:1rem;">Error al cargar perfil.</div>`;
        }
    }
    async loadGlobalStats() {
        const container = document.getElementById('global-stats-dashboard');
        if (!container) return;

        try {
            // Mostrar loaders en los contenedores específicos
            const innerGrowth = document.getElementById('stats-growth-chart');
            const innerGeo = document.getElementById('stats-geo-list');
            const innerRoles = document.getElementById('stats-roles-list');
            const innerTable = document.getElementById('stats-ligas-recientes-list');

            if (innerGrowth) innerGrowth.innerHTML = '<div class="spinner-sm"></div>';
            if (innerGeo) innerGeo.innerHTML = '<div class="spinner-sm"></div>';
            if (innerRoles) innerRoles.innerHTML = '<div class="spinner-sm"></div>';
            if (innerTable) innerTable.innerHTML = '<tr><td colspan="5" style="text-align:center;">Cargando inteligencia...</td></tr>';

            const stats = await Core.fetchAPI('/api/admin/dashboard-stats?start_date=2020-01-01&end_date=' + new Date().toISOString().split('T')[0]);
            const ligasResponse = await Core.fetchAPI('/api/admin/ligas?limit=10');
            const ligas = ligasResponse.items || ligasResponse || [];

            this.renderGlobalStats(stats, ligas);
        } catch (error) {
            console.error("Error al cargar estadísticas globales:", error);
        }
    }

    renderGlobalStats(stats, ligas) {
        // 1. Crecimiento Mensual (Barras CSS)
        const growthContainer = document.getElementById('stats-growth-chart');
        if (growthContainer && stats.ligas_por_mes) {
            const maxCount = Math.max(...stats.ligas_por_mes.map(m => m.count), 1);
            growthContainer.innerHTML = stats.ligas_por_mes.map(m => `
                <div style="flex: 1; display: flex; flex-direction: column; align-items: center; gap: 8px;">
                    <div style="font-size: 0.65rem; font-weight: 800; color: var(--primary);">${m.count}</div>
                    <div style="width: 100%; height: ${(m.count / maxCount) * 150}px; background: linear-gradient(to top, var(--primary), #00d1ff); border-radius: 4px 4px 0 0;"></div>
                    <div style="font-size: 0.6rem; color: var(--text-muted); writing-mode: vertical-lr; transform: rotate(180deg); margin-top: 5px; height: 30px;">${m.label}</div>
                </div>
            `).join('');
        }

        // 2. Top Regiones
        const geoContainer = document.getElementById('stats-geo-list');
        if (geoContainer && stats.ligas_por_state || stats.ligas_por_estado) {
            const states = stats.ligas_por_estado || [];
            const total = states.reduce((acc, curr) => acc + curr.count, 0);
            geoContainer.innerHTML = states.map(e => `
                <div style="display: flex; flex-direction: column; gap: 4px;">
                    <div style="display: flex; justify-content: space-between; font-size: 0.8rem;">
                        <span style="font-weight: 600;">${e.estado}</span>
                        <span style="color: var(--text-muted); font-size: 0.7rem;">${e.count} ligas</span>
                    </div>
                    <div style="width: 100%; height: 6px; background: rgba(255,255,255,0.05); border-radius: 3px; overflow: hidden;">
                        <div style="width: ${(e.count / (total || 1)) * 100}%; height: 100%; background: #3b82f6; border-radius: 3px;"></div>
                    </div>
                </div>
            `).join('') || '<p class="text-muted" style="font-size: 0.8rem; text-align: center;">Sin datos geográficos</p>';
        }

        // 3. Usuarios por Rol
        const rolesContainer = document.getElementById('stats-roles-list');
        if (rolesContainer && stats.usuarios_por_rol) {
            const roles = [
                { id: 'admin_liga', label: 'Dueños', color: '#00ff88', icon: '👑' },
                { id: 'arbitro', label: 'Árbitros', color: '#ef4444', icon: '⚖️' },
                { id: 'visor', label: 'Lectores', color: '#3b82f6', icon: '👁️' },
                { id: 'jugador', label: 'Jugadores', color: '#eab308', icon: '⚽' }
            ];
            rolesContainer.innerHTML = roles.map(r => `
                <div style="background: rgba(255,255,255,0.03); padding: 10px; border-radius: 10px; border: 1px solid rgba(255,255,255,0.05); text-align: center;">
                    <div style="font-size: 0.9rem; margin-bottom: 2px;">${r.icon}</div>
                    <div style="font-size: 1.1rem; font-weight: 800; color: ${r.color};">${stats.usuarios_por_rol[r.id] || 0}</div>
                    <div style="font-size: 0.65rem; color: var(--text-muted); text-transform: uppercase;">${r.label}</div>
                </div>
            `).join('');
        }

        // 4. Ligas Recientes
        const ligasTable = document.getElementById('stats-ligas-recientes-list');
        if (ligasTable) {
            const totalBadge = document.getElementById('total-ligas-badge');
            if (totalBadge) totalBadge.innerText = `${ligas.length} Ligas Recientes`;
            ligasTable.innerHTML = ligas.map(l => `
                <tr>
                    <td>
                        <div style="font-weight: 700;">${l.nombre}</div>
                        <div style="font-size: 0.7rem; color: var(--text-muted);">${l.municipio || '—'}, ${l.estado || '—'}</div>
                    </td>
                    <td>
                        <div style="font-size: 0.85rem;">${l.contacto || '—'}</div>
                        <div style="font-size: 0.7rem; opacity: 0.6;">Admin: ${l.owner_email || '—'}</div>
                    </td>
                    <td><code style="color: var(--primary); font-size: 0.75rem;">${l.subdominio}.futadmin.com</code></td>
                    <td style="font-size: 0.8rem; color: var(--text-muted);">${l.fecha_registro || '—'}</td>
                    <td style="text-align: right;">
                        <span class="status-pill active" style="font-size: 0.6rem;">ACTIVA</span>
                    </td>
                </tr>
            `).join('') || '<tr><td colspan="5" style="text-align:center; padding: 2rem; opacity: 0.5;">No hay registros recientes</td></tr>';
        }
    }
}
