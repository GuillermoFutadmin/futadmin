/**
 * DashboardModule - Gestión de Estadísticas Avanzadas
 */
import { Core } from './core.js';

export class DashboardModule {
    constructor(ui) {
        this.ui = ui;
        this.currentLeagueId = 'all';
        this.activeTab = 'resumen';
        this.leagueData = null;
        this._matchDetailsCache = {}; // cache: partido_id -> detail data
        this.liveInterval = null;
    }

    async init() {
        await this.populateLeagueFilter();
        // Sincronizar UI inicial (pestañas, datos, etc.)
        this.loadLeagueData();
    }

    async populateLeagueFilter() {
        try {
            const response = await Core.fetchAPI('/api/torneos');
            const torneos = response.items || response;
            const select = document.getElementById('dashboard-league-filter');
            if (!select) return;

            // Mantener la opción "all" y agregar las demás
            select.innerHTML = '<option value="all">📊 Resumen de Todas las Ligas</option>';
            if (Array.isArray(torneos)) {
                torneos.forEach(t => {
                    const opt = document.createElement('option');
                    opt.value = t.id;
                    opt.textContent = `🏆 ${t.nombre}`;
                    select.appendChild(opt);
                });
            }
        } catch (e) { console.error("Error al cargar el filtro de ligas:", e); }
    }

    async loadLeagueData() {
        const select = document.getElementById('dashboard-league-filter');
        if (!select) return;
        this.currentLeagueId = select.value;

        const tabsNav = document.querySelector('.dashboard-tabs');
        
        if (this.currentLeagueId === 'all') {
            if (tabsNav) tabsNav.style.setProperty('display', 'none', 'important');
            this.leagueData = null;
            const banner = document.querySelector('.welcome-banner');
            if (banner) banner.innerHTML = '';
            const container = document.getElementById('stats-dashboard');
            if (container) container.innerHTML = '';

            this.switchTab('resumen');
            this.ui.loadInitialStats(true); // Forzar actualización y renderizado
        } else {
            if (tabsNav) tabsNav.style.setProperty('display', 'flex', 'important');
            try {
                this.leagueData = await Core.fetchAPI(`/api/torneos/${this.currentLeagueId}`);
                this.refreshCurrentTab();
            } catch (e) {
                console.error("Error al cargar datos de la liga:", e);
                this.leagueData = null;
            }
        }
    }

    switchTab(tabId) {
        this.activeTab = tabId;

        // Actualización de UI
        document.querySelectorAll('.dashboard-tabs .content-tab').forEach(t => {
            t.classList.remove('active');
            if (t.getAttribute('data-dash-tab') === tabId) t.classList.add('active');
        });

        document.querySelectorAll('.dash-tab-content').forEach(c => {
            c.style.display = 'none';
        });

        const target = document.getElementById(`dash-view-${tabId}`);
        if (target) {
            target.style.display = 'block';
            this.refreshCurrentTab();
        }
    }

    async refreshCurrentTab() {
        if (!this.currentLeagueId || this.currentLeagueId === 'all') {
            // En modo "all", solo permitimos el resumen global (manejado por loadInitialStats)
            if (this.activeTab !== 'resumen') {
                this.switchTab('resumen');
            }
            return;
        }

        switch (this.activeTab) {
            case 'resumen': this.renderResumen(); break;
            case 'tabla': this.renderStandings(); break;
            case 'rol': this.renderSchedule(); break;
            case 'lideres': this.renderLeaderboards(); break;
        }

        if (this.activeTab === 'resumen') {
            this.startLiveUpdates();
        } else {
            this.stopLiveUpdates();
        }
    }

    startLiveUpdates() {
        this.stopLiveUpdates(); // Clear any existing
        this.fetchAndRenderLiveMatches(); // Initial fetch
        this.liveInterval = setInterval(() => {
            if (this.activeTab === 'resumen') {
                this.fetchAndRenderLiveMatches();
            } else {
                this.stopLiveUpdates();
            }
        }, 20000); // Poll every 20s
    }

    stopLiveUpdates() {
        if (this.liveInterval) {
            clearInterval(this.liveInterval);
            this.liveInterval = null;
        }
    }

    async fetchAndRenderLiveMatches() {
        const liveContainer = document.getElementById('live-matches-banner-container');
        if (!liveContainer) return;

        try {
            const torneoId = this.currentLeagueId === 'all' ? 0 : this.currentLeagueId;
            const liveMatches = await Core.fetchAPI(`/api/torneos/${torneoId}/partidos/live`);

            if (!liveMatches || liveMatches.length === 0) {
                liveContainer.innerHTML = '';
                liveContainer.style.display = 'none';
                return;
            }

            // Helper para calcular el minuto en tiempo real
            const getMatchMinute = (m) => {
                if (!m.timer_started_at) return '';
                const now = Date.now();
                const elapsedMs = now - m.timer_started_at;
                const totalSeconds = Math.floor(elapsedMs / 1000) + (m.tiempo_corrido_segundos || 0);
                const minutes = Math.floor(totalSeconds / 60);
                return `${minutes}'`;
            };

            liveContainer.style.display = 'flex';
            liveContainer.style.justifyContent = liveMatches.length === 1 ? 'center' : 'flex-start';
            
            liveContainer.innerHTML = `
                <div class="live-scroll-wrapper">
                    ${liveMatches.map(m => {
                        const minute = getMatchMinute(m);
                        const eventosArr = m.eventos || [];
                        const goalsCount = eventosArr.filter(e => e.tipo === 'Gol').length;
                        
                        return `
                        <div class="live-match-card-mini pulse-border">
                            <div class="live-header-row">
                                <div class="live-indicator-tag">
                                    <span class="dot-pulse"></span>
                                    <span>EN VIVO</span>
                                    ${m.jornada ? `<span style="margin-left: 8px; border-left: 1px solid rgba(255,255,255,0.2); padding-left: 8px; opacity: 0.8;">Jornada ${m.jornada}</span>` : ''}
                                </div>
                            </div>

                            <div class="live-teams-container">
                                <div class="live-team-box">
                                    <img src="${m.equipo_local_escudo || ''}" class="${!m.equipo_local_escudo ? 'white-placeholder' : ''}" onerror="this.src='https://cdn-icons-png.flaticon.com/512/53/53283.png'; this.classList.add('white-placeholder');">
                                    <span class="marquee-wrap"><span class="marquee-text">${m.equipo_local}</span></span>
                                </div>
                                <div class="live-score-box">
                                    ${minute ? `<div class="live-minute-badge" style="margin-bottom: 2px;">${minute}</div>` : ''}
                                    <div class="score-numerals">
                                        <span>${m.goles_local}</span>
                                        <span class="score-divider">-</span>
                                        <span>${m.goles_visitante}</span>
                                    </div>
                                    <div class="marquee-wrap" style="font-size: 0.65rem; color: rgba(255,255,255,0.6); text-transform: uppercase; letter-spacing: 1px; white-space: nowrap; font-weight: 700; margin-top: 2px; max-width: 120px; text-align: center;" title="${m.cancha || 'Por designar'}">
                                        <span class="marquee-text">📍 ${m.cancha || 'Por designar'}</span>
                                    </div>
                                </div>
                                <div class="live-team-box">
                                    <img src="${m.equipo_visitante_escudo || ''}" class="${!m.equipo_visitante_escudo ? 'white-placeholder' : ''}" onerror="this.src='https://cdn-icons-png.flaticon.com/512/53/53283.png'; this.classList.add('white-placeholder');">
                                    <span class="marquee-wrap"><span class="marquee-text">${m.equipo_visitante}</span></span>
                                </div>
                            </div>

                            <div class="live-footer-info">
                                <div class="referee-tag">
                                    <span>⚖️</span>
                                    <span>${m.arbitro_nombre || 'Sin asignar'}</span>
                                </div>
                                
                                <div class="live-events-list">
                                    ${eventosArr.sort((a, b) => b.minuto - a.minuto).map(e => {
                                        const tipoLow = (e.tipo || '').toLowerCase();
                                        let icon = '⚽';
                                        let classType = 'event-icon-goal-white';
                                        if (tipoLow.includes('amarilla') || tipoLow.includes('yellow')) {
                                            icon = '🟨'; classType = 'event-icon-yellow';
                                        } else if (tipoLow.includes('roja') || tipoLow.includes('red')) {
                                            icon = '🟥'; classType = 'event-icon-red';
                                        } else if (tipoLow.includes('azul') || tipoLow.includes('blue')) {
                                            icon = '🟦'; classType = 'event-icon-blue';
                                        }
                                        let nameContent = "";
                                        if (['inicio', 'fin', 'medio tiempo', 'reanudación'].includes(tipoLow) || tipoLow.includes('reanudaci')) {
                                            nameContent = e.tipo; // Solo texto del estado
                                        } else {
                                            let playerText = e.jugador_nombre && e.jugador_nombre !== "NN" ? e.jugador_nombre : "Desconocido";
                                            let numText = e.jugador_numero && e.jugador_numero !== "?" ? `<b>#${e.jugador_numero}</b> ` : "";
                                            let equipoText = (e.equipo_nombre && e.equipo_nombre !== "—") ? ` <small style="opacity:0.7;">(${e.equipo_nombre})</small>` : "";
                                            
                                            if (tipoLow.includes("cambio")) {
                                                playerText = e.nota || "Sustitución";
                                                nameContent = `${playerText}${equipoText}`;
                                            } else {
                                                nameContent = `${numText}${playerText}${equipoText}`;
                                                if (e.nota) nameContent += ` <small style="opacity:0.7;">- ${e.nota}</small>`;
                                            }
                                        }

                                        const finalNameHtml = `<span class="marquee-wrap"><span class="marquee-text">${nameContent}</span></span>`;

                                        return `
                                            <div class="event-row-mini">
                                                <span class="event-min-mini">${e.minuto}'</span>
                                                <span class="${classType}">${icon}</span>
                                                <span class="event-name-mini" style="display: flex; align-items: center; overflow: hidden; white-space: nowrap;">${finalNameHtml}</span>
                                            </div>
                                        `;
                                    }).join('')}
                                    ${eventosArr.length === 0 ? '<div class="no-events-label">Sin eventos</div>' : ''}
                                </div>
                            </div>
                        </div>
                        `;
                    }).join('')}
                </div>
            `;
            
            // Activar marquees dinámicos
            this.activateMarqueeIfNeeded(liveContainer);

        } catch (e) {
            console.error("Error al cargar partidos en vivo:", e);
        }
    }

    /**
     * Activa el efecto de desplazamiento para todos los .marquee-text dentro del contenedor
     * solo si el texto desborda el ancho del envoltorio (marquee-wrap).
     */
    activateMarqueeIfNeeded(container) {
        if (!container) return;
        requestAnimationFrame(() => {
            const elements = container.querySelectorAll('.marquee-text');
            elements.forEach(span => {
                const wrap = span.parentElement;
                if (!wrap.classList.contains('marquee-wrap')) return;

                const wrapWidth = wrap.offsetWidth;
                const textWidth = span.scrollWidth;

                if (textWidth > wrapWidth) {
                    const offset = -((textWidth - wrapWidth) + 20); // 20px de margen extra
                    const duration = Math.max(4, Math.floor(textWidth / 30)); // 30px per sec
                    
                    span.style.setProperty('--marquee-offset', `${offset}px`);
                    span.style.setProperty('--marquee-dur', `${duration}s`);
                    span.classList.add('scrolling');
                } else {
                    span.classList.remove('scrolling');
                }
            });
        });
    }

    async renderResumen() {
        const container = document.getElementById('stats-dashboard');
        const banner = document.querySelector('.welcome-banner');

        if (!this.leagueData) return;
        const data = this.leagueData;

        banner.innerHTML = `
            <div style="display: flex; flex-direction: column; gap: 20px;">
                <div style="display: flex; align-items: center; gap: 20px;">
                    <img src="${data.logo_url || 'https://cdn-icons-png.flaticon.com/512/53/53283.png'}" style="width: 80px; height: 80px; object-fit: contain;">
                    <div>
                        <h2 style="margin:0; font-size: 1.8rem;">${data.nombre}</h2>
                        <p style="margin:5px 0 0 0; color: var(--primary); font-weight: bold;">${data.tipo} • ${data.formato}</p>
                    </div>
                </div>
                <div id="live-matches-banner-container" style="display: none; flex-wrap: wrap; gap: 15px; margin-top: 10px; border-top: 1px solid rgba(255,255,255,0.1); padding-top: 20px;">
                    <!-- Cargados via polling -->
                </div>
            </div>
        `;

        container.innerHTML = `
            <div class="stat-card">
                <p class="section-title">FECHA INICIO</p>
                <div class="value">${data.fecha_inicio}</div>
            </div>
            <div class="stat-card">
                <p class="section-title">DURACIÓN PARTIDO</p>
                <div class="value">${data.duracion_tiempo} min</div>
            </div>
            <div class="stat-card">
                <p class="section-title">EQUIPOS</p>
                <div class="value">${data.stats?.equipos || 0}</div>
            </div>
        `;
    }

    async renderStandings() {
        const container = document.getElementById('standings-table-container');
        if (!container) return;

        try {
            // 1. Obtener todos los partidos para ver si hay Liguilla/Eliminatorias
            const matches = await Core.fetchAPI(`/api/torneos/${this.currentLeagueId}/partidos`);
            const hasKnockout = matches.some(p => p.fase && p.fase !== 'Fase de Grupos');
            const isPureKnockout = this.leagueData?.formato === 'Eliminación Directa';

            let html = '';

            // --- SECCIÓN 1: BRACKET (Si hay fases eliminatorias) ---
            if (hasKnockout) {
                const teamsMap = {};
                const eliminatedIds = new Set();
                const allTeams = new Set();

                matches.filter(p => p.fase && p.fase !== 'Fase de Grupos').forEach(p => {
                    const localId = p.equipo_local_id;
                    const visitanteId = p.equipo_visitante_id;
                    if (!teamsMap[localId]) teamsMap[localId] = { nombre: p.equipo_local, escudo: p.equipo_local_escudo, pj: 0, g: 0, p: 0, gf: 0, gc: 0 };
                    if (!teamsMap[visitanteId]) teamsMap[visitanteId] = { nombre: p.equipo_visitante, escudo: p.equipo_visitante_escudo, pj: 0, g: 0, p: 0, gf: 0, gc: 0 };
                    allTeams.add(localId); allTeams.add(visitanteId);

                    if (p.estado === 'Played') {
                        const gl = p.goles_local || 0;
                        const gv = p.goles_visitante || 0;
                        teamsMap[localId].pj++; teamsMap[visitanteId].pj++;
                        teamsMap[localId].gf += gl; teamsMap[localId].gc += gv;
                        teamsMap[visitanteId].gf += gv; teamsMap[visitanteId].gc += gl;

                        let ganadorID = p.ganador_id;
                        if (!ganadorID) {
                            if (gl > gv) ganadorID = localId;
                            else if (gv > gl) ganadorID = visitanteId;
                        }
                        if (ganadorID) {
                            const perdedorId = (ganadorID === localId) ? visitanteId : localId;
                            teamsMap[ganadorID].g++;
                            teamsMap[perdedorId].p++;
                            eliminatedIds.add(perdedorId);
                        }
                    }
                });

                const rounds = {};
                matches.filter(p => p.fase && p.fase !== 'Fase de Grupos').forEach(p => {
                    if (!rounds[p.jornada]) rounds[p.jornada] = [];
                    rounds[p.jornada].push(p);
                });
                const sortedRounds = Object.keys(rounds).sort((a, b) => b - a);

                html += `
                    <style>
                        .bracket-container { display: flex; gap: 30px; padding: 20px 10px; overflow-x: auto; min-height: 350px; align-items: center; background: rgba(0,0,0,0.4); border-radius: 12px; border: 1px solid rgba(255,255,255,0.05); margin-bottom: 30px; }
                        .bracket-round { display: flex; flex-direction: column; justify-content: space-around; gap: 15px; min-width: 180px; height: 100%; position: relative; }
                        .bracket-match { background: linear-gradient(135deg, rgba(45,45,45,0.98), rgba(25,25,25,0.98)); border: 2px solid rgba(255, 255, 255, 0.2); border-radius: 12px; overflow: hidden; box-shadow: 0 5px 15px rgba(0,0,0,0.4); transition: all 0.2s; position: relative; }
                        .bracket-match::before { content:''; position:absolute; left:0; top:0; bottom:0; width:3px; background:var(--primary); opacity:0.5; }
                        .bracket-match:hover { transform: scale(1.03); border-color: var(--primary); box-shadow: 0 0 20px rgba(0,255,136,0.2); }
                        .bracket-team { display: flex; align-items: center; justify-content: space-between; padding: 6px 10px; font-size: 0.75rem; border-bottom: 1px solid rgba(255, 255, 255, 0.08); }
                        .bracket-team:last-child { border-bottom: none; }
                        .bracket-team.winner { background: linear-gradient(90deg, rgba(0, 255, 136, 0.1), transparent); }
                        .bracket-team.winner span { font-weight: 900; color: var(--primary); }
                        .bracket-team.winner .bracket-score { font-weight: bold; color: #fff; }
                        .bracket-team.loser { opacity: 0.4; filter: grayscale(1); }
                        .bracket-score { font-weight: 900; min-width: 20px; text-align: center; color: var(--primary); background: rgba(255,255,255,0.05); border-radius: 4px; padding: 2px; }
                        .round-title { text-align: center; color: var(--primary); text-transform: uppercase; font-size: 0.75rem; font-weight: 900; margin-bottom: 10px; }
                    </style>
                    <div class="bracket-container">
                `;

                // Ganador final
                const firstRoundInList = rounds[sortedRounds[0]];
                if (firstRoundInList && firstRoundInList.length === 1 && firstRoundInList[0].estado === 'Played' && firstRoundInList[0].fase === 'Final') {
                    const finalMatch = firstRoundInList[0];
                    const campeonId = finalMatch.ganador_id;
                    const campeon = teamsMap[campeonId];
                    if (campeon) {
                        html += `
                            <div class="bracket-round" style="align-items: center;">
                                <div class="round-title">CAMPEÓN</div>
                                <div style="text-align: center; padding: 10px;">
                                    <div style="font-size: 1.5rem;">🏆</div>
                                    <div style="color: var(--primary); font-weight: bold; font-size: 0.8rem;">${campeon.nombre}</div>
                                </div>
                            </div>
                        `;
                    }
                }

                sortedRounds.forEach(r => {
                    const matchesInRound = rounds[r];
                    const faseName = matchesInRound[0].fase || `RONDA ${r}`;
                    html += `
                        <div class="bracket-round">
                            <div class="round-title">${faseName}</div>
                            ${matchesInRound.map(p => {
                        const isPlayed = p.estado === 'Played';
                        const localWinner = p.ganador_id === p.equipo_local_id;
                        const visitanteWinner = p.ganador_id === p.equipo_visitante_id;
                        return `
                                    <div class="bracket-match">
                                        <div class="bracket-team ${isPlayed ? (localWinner ? 'winner' : 'loser') : ''}">
                                            <div style="display:flex; align-items:center; gap:6px;">
                                                <img src="${p.equipo_local_escudo || ''}" class="shield-placeholder" style="width:16px; height:16px; object-fit:contain" onerror="this.src='https://cdn-icons-png.flaticon.com/512/53/53283.png'">
                                                <span>${p.equipo_local}</span>
                                            </div>
                                            <div class="bracket-score">${isPlayed ? (p.goles_local ?? '-') : '-'}</div>
                                        </div>
                                        <div class="bracket-team ${isPlayed ? (visitanteWinner ? 'winner' : 'loser') : ''}">
                                            <div style="display:flex; align-items:center; gap:6px;">
                                                <img src="${p.equipo_visitante_escudo || ''}" class="shield-placeholder" style="width:16px; height:16px; object-fit:contain" onerror="this.src='https://cdn-icons-png.flaticon.com/512/53/53283.png'">
                                                <span>${p.equipo_visitante}</span>
                                            </div>
                                            <div class="bracket-score">${isPlayed ? (p.goles_visitante ?? '-') : '-'}</div>
                                        </div>
                                    </div>
                                `;
                    }).join('')}
                        </div>
                    `;
                });

                html += `</div>`;
            }

            // --- SECCIÓN 2: TABLA DE ESTADÍSTICAS GENERALES ---
            const standings = await Core.fetchAPI(`/api/torneos/${this.currentLeagueId}/standings`);

            // Agrupar por grupo si corresponde
            const groups = {};
            standings.forEach(row => {
                const g = row.grupo || 'General';
                if (!groups[g]) groups[g] = [];
                groups[g].push(row);
            });

            const groupKeys = Object.keys(groups).sort();

            html += `<div style="margin-top: ${hasKnockout ? '20px' : '0'};">`;

            groupKeys.forEach(gKey => {
                const groupRows = groups[gKey];
                let groupTitle = `TABLA DE POSICIONES - ${gKey.toUpperCase()}`;

                if (gKey === 'General') {
                    if (isPureKnockout) {
                        groupTitle = 'ESTADÍSTICAS GENERALES';
                    } else if (hasKnockout) {
                        groupTitle = 'TABLA GENERAL DE LIGA';
                    } else {
                        groupTitle = 'CLASIFICACIÓN';
                    }
                }

                html += `
                        <h3 style="color:var(--text-muted); font-size:0.8rem; margin-top:25px; margin-bottom:15px; border-left:3px solid var(--primary); padding-left:10px;">${groupTitle}</h3>
                        <table class="standings-table">
                            <thead>
                                <tr>
                                    <th>POS</th>
                                    <th style="text-align:left">EQUIPO</th>
                                    <th>PTS</th>
                                    <th>PJ</th>
                                    <th>G</th>
                                    <th>E</th>
                                    <th>P</th>
                                    <th>GF</th>
                                    <th>GC</th>
                                    <th>DG</th>
                                    <th>FORMA</th>
                                </tr>
                            </thead>
                            <tbody>
                                ${groupRows.map((row, i) => `
                                    <tr>
                                        <td style="font-weight:bold">${i + 1}</td>
                                        <td style="text-align:left">
                                            <div style="display:flex; align-items:center; gap:8px;">
                                                <img src="${row.escudo_url || ''}" class="shield-placeholder" style="width:24px; height:24px; object-fit:contain" onerror="this.src='https://cdn-icons-png.flaticon.com/512/53/53283.png'">
                                                <span>${row.nombre}</span>
                                            </div>
                                        </td>
                                        <td style="font-weight:bold; color:var(--primary)">${row.pts}</td>
                                        <td>${row.pj}</td>
                                        <td>${row.g}</td>
                                        <td>${row.e}</td>
                                        <td>${row.p}</td>
                                        <td>${row.gf}</td>
                                        <td>${row.gc}</td>
                                        <td>${row.dg > 0 ? '+' : ''}${row.dg}</td>
                                        <td>
                                            <div style="display:flex; gap:4px; justify-content:center">
                                                ${row.recent.map(r => `<span class="form-badge ${r.toLowerCase()}">${r}</span>`).join('')}
                                            </div>
                                        </td>
                                    </tr>
                                `).join('')}
                            </tbody>
                        </table>
                    `;
            });
            html += `</div>`;

            container.innerHTML = html;
        } catch (e) {
            console.error("Error en renderStandings:", e);
            container.innerHTML = '<p class="text-error">Ocurrió un error al cargar la clasificación.</p>';
        }
    }

    async renderSchedule() {
        const container = document.getElementById('league-schedule-container');
        try {
            if (!this._scheduleData || this._scheduleDataLeagueId !== this.currentLeagueId) {
                this._scheduleData = await Core.fetchAPI(`/api/torneos/${this.currentLeagueId}/partidos`);
                this._scheduleDataLeagueId = this.currentLeagueId;
            }
            const data = this._scheduleData;

            // Agrupar por jornada
            const jornadas = {};
            data.forEach(p => {
                if (!jornadas[p.jornada]) jornadas[p.jornada] = [];
                jornadas[p.jornada].push(p);
            });

            const maxJornada = Math.max(...Object.keys(jornadas).map(Number), 0);

            // --- FILTRO DE JORNADAS ---
            const filterContainer = document.getElementById('jornadas-filter-container');
            if (filterContainer) {
                if (filterContainer.dataset.league !== this.currentLeagueId) {
                    filterContainer.dataset.league = this.currentLeagueId;
                    const sortedJ = Object.keys(jornadas).sort((a,b) => b - a);
                    let filterHtml = '';
                    sortedJ.forEach(j => {
                        const isChecked = (parseInt(j) === maxJornada) ? 'checked' : '';
                        filterHtml += `
                            <label style="display: inline-flex; align-items: center; gap: 5px; background: rgba(0,0,0,0.3); padding: 5px 12px; border-radius: 20px; cursor: pointer; border: 1px solid rgba(255,255,255,0.1); user-select: none;">
                                <input type="checkbox" class="jornada-dashboard-checkbox" value="${j}" ${isChecked} onchange="ui.dashboard.renderFilteredSchedule()">
                                Jornada ${j}
                            </label>
                        `;
                    });
                    filterContainer.innerHTML = filterHtml;
                }
            }

            this.renderFilteredSchedule();
        } catch (e) {
            console.error(e);
            container.innerHTML = '<p class="text-error">Error al cargar jornadas</p>';
        }
    }

    renderFilteredSchedule() {
        const container = document.getElementById('league-schedule-container');
        if (!container) return;
        
        const filterBoxes = document.querySelectorAll('.jornada-dashboard-checkbox:checked');
        const selectedJornadas = Array.from(filterBoxes).map(cb => Number(cb.value));

        const data = this._scheduleData || [];
        
        const jornadas = {};
        data.forEach(p => {
            if (!jornadas[p.jornada]) jornadas[p.jornada] = [];
            jornadas[p.jornada].push(p);
        });
        
        const isKnockout = this.leagueData?.formato === 'Eliminación Directa';
        const isLeague = !isKnockout;
        const maxJornada = Math.max(...Object.keys(jornadas).map(Number), 0);
        const allPlayedInLast = maxJornada > 0 && jornadas[maxJornada] && jornadas[maxJornada].every(p => p.estado === 'Played');
        const hasPendingSchedule = maxJornada > 0 && jornadas[maxJornada] && jornadas[maxJornada].some(p => p.estado === 'Scheduled' && (!p.fecha || !p.hora));
        const hasKnockoutPhases = data.some(p => p.fase && p.fase !== 'Regular' && p.fase !== 'Fase de Grupos' && p.fase !== 'Liga');

        let html = '';

        if (isKnockout && data.length === 0) {
            html += `
                <div style="grid-column: 1 / -1; padding: 40px; background: rgba(0,255,136,0.05); border-radius: 12px; border: 2px dashed var(--primary); text-align: center; margin: 20px;">
                    <h2 style="color: var(--primary); margin-bottom: 15px;">🎲 Sorteo Pendiente</h2>
                    <p style="margin-bottom: 25px; color: var(--text-muted);">Aún no se han generado los enfrentamientos para este torneo. El sistema mezclará a los equipos registrados y programará los horarios automáticamente.</p>
                    <button class="btn-primary" onclick="ui.dashboard.inicializarTorneo()" style="padding: 15px 30px; font-size: 1rem;">EFECTUAR SORTEO Y PROGRAMAR LLAVES</button>
                </div>
            `;
        }

        if ((isKnockout || (isLeague && hasKnockoutPhases)) && allPlayedInLast && maxJornada > 0) {
            html += `
                <div style="grid-column: 1 / -1; padding: 20px; background: rgba(0,255,136,0.1); border-radius: 12px; border: 1px dashed var(--primary); text-align: center; margin-bottom: 20px;">
                    <p style="margin-bottom: 10px; font-weight: bold;">✅ Ronda completada</p>
                    <button class="btn-primary" onclick="ui.dashboard.avanzarRonda()" style="background: var(--primary); color: #000;">GENERAR SIGUIENTE RONDA</button>
                </div>
            `;
        }

        if (isLeague && allPlayedInLast && maxJornada > 0 && !hasKnockoutPhases) {
            html += `
                <div style="grid-column: 1 / -1; padding: 20px; background: rgba(255,165,0,0.1); border-radius: 12px; border: 1px dashed orange; text-align: center; margin-bottom: 20px;">
                    <p style="margin-bottom: 5px; font-weight: bold; color: orange;">🏆 Fase regular completada</p>
                    <p style="font-size: 0.85rem; color: var(--text-muted); margin-bottom: 15px;">Todos los juegos de esta fase han terminado. Puedes iniciar la siguiente fase eliminatoria.</p>
                    <button class="btn-primary" onclick="ui.dashboard.startLiguilla()" style="background: orange; color: #000; border-color: orange;">INICIAR LIGUILLA / SIGUIENTE FASE</button>
                </div>
            `;
        }

        if (hasPendingSchedule) {
            html += `
                <div style="grid-column: 1 / -1; padding: 20px; background: rgba(59,130,246,0.1); border-radius: 12px; border: 1px dashed #3b82f6; text-align: center; margin-bottom: 20px;">
                    <p style="margin-bottom: 10px; font-weight: bold;">📅 Nuevos encuentros sin programar</p>
                    <button class="btn-primary" onclick="ui.dashboard.inicializarTorneo()" style="background: #3b82f6; color: #fff; border-color: #3b82f6;">INICIO DE SIGUIENTE RONDA (Programar Horarios)</button>
                </div>
            `;
        }

        if (selectedJornadas.length === 0 && data.length > 0) {
            html += '<p class="text-muted" style="grid-column: 1 / -1; text-align: center; margin-top: 20px;">Por favor, selecciona al menos una jornada en el filtro superior para ver los partidos.</p>';
        }

        Object.keys(jornadas).sort((a, b) => b - a).forEach(j => {
            if (selectedJornadas.length > 0 && !selectedJornadas.includes(Number(j))) return; // Omitir no seleccionadas

            const p0 = jornadas[j][0];
            let faseName = `JORNADA ${j}`;
            if (p0.fase && p0.fase !== 'Regular' && p0.fase !== 'Fase de Grupos') {
                faseName = `JORNADA ${j} - ${p0.fase}`;
            } else if (p0.fase === 'Fase de Grupos') {
                faseName = `JORNADA ${j} - FASE DE GRUPOS`;
            }

            html += `<div style="grid-column: 1 / -1; margin-top: 20px;"><p class="section-title">${faseName.toUpperCase()}</p></div>`;
            jornadas[j].forEach(p => {
                const isPlayed = p.estado === 'Played';
                const isLive = p.estado === 'Live';
                const hasPenalties = p.penales_local !== null;
                const showTooltip = isPlayed || isLive;

                const leagueColor = this.leagueData?.color || 'var(--primary)';
                html += `
                    <div class="stat-card match-card premium-card" data-match-id="${p.id}" style="position: relative;">
                        <div class="combo-indicator" style="background: ${leagueColor};"></div>
                        <div style="display:flex; justify-content:space-between; font-size:0.75rem; color:var(--text-muted); margin-bottom:10px;">
                            <span>${p.fecha || ''} ${p.hora || ''}</span>
                            <span style="color: ${isPlayed ? 'var(--primary)' : (isLive ? '#ff8c00' : 'var(--text-muted)')}">
                                ${p.estado === 'Played' ? 'Finalizado' : (p.estado === 'Live' ? 'En Vivo' : (p.estado === 'Scheduled' ? 'Programado' : p.estado))}
                            </span>
                        </div>
                        <div style="display:flex; align-items:center; justify-content:space-between; gap:10px;">
                            <div style="text-align:center; flex:1">
                                <img src="${p.equipo_local_escudo || ''}" class="shield-placeholder" style="width:30px; height:30px; object-fit:contain" onerror="this.src='https://cdn-icons-png.flaticon.com/512/53/53283.png'"><br>
                                <span style="font-size:0.8rem; ${p.ganador_id === p.equipo_local_id ? 'font-weight:bold; color:var(--primary)' : ''}">${p.equipo_local}</span>
                            </div>
                            <div style="text-align:center;">
                                <div style="font-size:1.5rem; font-weight:bold; display:flex; gap:8px;">
                                    ${isPlayed ? `<span>${(p.goles_local === null || p.goles_local === 'null') ? 0 : p.goles_local}</span><span>-</span><span>${(p.goles_visitante === null || p.goles_visitante === 'null') ? 0 : p.goles_visitante}</span>` : '<span>VS</span>'}
                                </div>
                                ${hasPenalties ? `<div style="font-size:0.7rem; color:var(--text-muted)">Pen: ${(p.penales_local === null || p.penales_local === 'null') ? 0 : p.penales_local}-${(p.penales_visitante === null || p.penales_visitante === 'null') ? 0 : p.penales_visitante}</div>` : ''}
                            </div>
                            <div style="text-align:center; flex:1">
                                <img src="${p.equipo_visitante_escudo || ''}" class="shield-placeholder" style="width:30px; height:30px; object-fit:contain" onerror="this.src='https://cdn-icons-png.flaticon.com/512/53/53283.png'"><br>
                                <span style="font-size:0.8rem; ${p.ganador_id === p.equipo_visitante_id ? 'font-weight:bold; color:var(--primary)' : ''}">${p.equipo_visitante}</span>
                            </div>
                        </div>
                        ${showTooltip ? `<div class="match-tooltip" id="tooltip-${p.id}"><span class="tooltip-loading">⏳ Cargando detalles...</span></div>` : ''}
                    </div>
                `;
            });
        });

        container.innerHTML = html || (data.length === 0 ? '<p class="text-muted">No hay partidos programados</p>' : '');

        // Attach hover events after DOM insertion
        container.querySelectorAll('.match-card[data-match-id]').forEach(card => {
            const matchId = card.dataset.matchId;
            const tooltip = card.querySelector('.match-tooltip');
            if (!tooltip) return; // only Played / Live cards have tooltip

            card.addEventListener('mouseenter', async () => {
                // Ensure the card being hovered has a higher z-index than its neighbors
                card.style.zIndex = '1000';

                // Detect viewport position to show tooltip on top if near bottom
                const rect = card.getBoundingClientRect();
                const spaceBelow = window.innerHeight - rect.bottom;
                if (spaceBelow < 250) { // If less than 250px below, show on top
                    tooltip.classList.add('on-top');
                } else {
                    tooltip.classList.remove('on-top');
                }
                if (this._matchDetailsCache[matchId]) {
                    this._renderTooltipContent(tooltip, this._matchDetailsCache[matchId]);
                    return;
                }
                try {
                    const data = await Core.fetchAPI(`/api/partido/${matchId}/detalles`);
                    this._matchDetailsCache[matchId] = data;
                    this._renderTooltipContent(tooltip, data);
                } catch (e) {
                    tooltip.innerHTML = '<span class="tooltip-empty">Error al cargar datos</span>';
                }
            });

            card.addEventListener('mouseleave', () => {
                card.style.zIndex = '';
            });
        });
    }

    selectAllJornadas() {
        const checkboxes = document.querySelectorAll('.jornada-dashboard-checkbox');
        checkboxes.forEach(cb => cb.checked = true);
        this.renderFilteredSchedule();
    }

    async avanzarRonda() {
        if (!confirm("¿Deseas generar los emparejamientos para la siguiente ronda con los ganadores actuales?")) return;

        try {
            const res = await Core.fetchAPI(`/api/torneos/${this.currentLeagueId}/avanzar_ronda`, { method: 'POST' });
            if (res.success) {
                alert(res.message);
                this.renderSchedule();
            }
        } catch (e) {
            alert("Error al avanzar ronda. Asegúrate de que no haya empates sin definir.");
        }
    }

    async renderLeaderboards() {
        const container = document.getElementById('leaderboards-container');
        try {
            const data = await Core.fetchAPI(`/api/torneos/${this.currentLeagueId}/leaderboard`);

            const renderList = (title, items, icon, unit) => `
                <div class="stat-card">
                    <p class="section-title">${title}</p>
                    <div style="margin-top:15px">
                        ${items && items.length > 0 ? items.map((it, i) => `
                            <div style="display:flex; align-items:center; justify-content:space-between; padding:10px 0; border-bottom:1px solid rgba(255,255,255,0.05)">
                                <div style="display:flex; align-items:center; gap:10px">
                                    <span style="color:var(--text-muted); font-size:0.8rem; width:15px">${i + 1}</span>
                                    <div>
                                        <div style="font-weight:bold; font-size:0.9rem">${it.jugador}</div>
                                        <div style="font-size:0.7rem; color:var(--text-muted)">${it.equipo}</div>
                                    </div>
                                </div>
                                <div style="display:flex; align-items:center; gap:5px">
                                    <span style="font-weight:bold; color:var(--primary)">${it.total}</span>
                                    <span style="font-size:0.7rem; color:var(--text-muted)">${unit}</span>
                                </div>
                            </div>
                        `).join('') : '<p class="text-muted" style="padding: 20px 0;">Sin datos todavía</p>'}
                    </div>
                </div>
            `;

            container.style.display = 'grid';
            container.style.gridTemplateColumns = 'repeat(auto-fit, minmax(280px, 1fr))';
            container.style.gap = '20px';

            container.innerHTML = `
                ${renderList('TOP GOLEADORES', data.goles, '⚽', 'GOLES')}
                ${renderList('PORTEROS MENOS GOLEADOS', data.porteros, '🧤', 'GC')}
                ${renderList('TARJETAS AMARILLAS', data.amarillas, '🟨', 'TA')}
                ${renderList('TARJETAS ROJAS', data.rojas, '🟥', 'TR')}
            `;
        } catch (e) { container.innerHTML = '<p class="text-error">Error al cargar líderes</p>'; }
    }

    async inicializarTorneo() {
        if (!confirm("¿Deseas realizar el sorteo aleatorio y programar los horarios automáticamente para todos los equipos registrados?")) return;

        try {
            const res = await Core.fetchAPI(`/api/torneos/${this.currentLeagueId}/inicializar`, { method: 'POST' });
            if (res.success) {
                alert(res.message);
                this.renderSchedule();
            } else {
                alert("Error: " + res.message);
            }
        } catch (e) {
            alert("Error al inicializar el torneo.");
            console.error(e);
        }
    }

    /**
     * Populates a tooltip element with match event details (goals & cards).
     * @param {HTMLElement} tooltip - The .match-tooltip container
     * @param {Object} data - Response from /api/partido/<id>/detalles
     */
    _renderTooltipContent(tooltip, data) {
        const golesHtml = data.goles && data.goles.length
            ? data.goles.map(g => `
                <div class="tooltip-event-row">
                    <span class="tooltip-minute">${g.minuto ?? '?'}'</span>
                    <span>⚽</span>
                    <span style="flex:1">${g.jugador}</span>
                    <span style="font-size:0.7rem; color:var(--text-muted); text-align:right">${g.equipo}</span>
                </div>`).join('')
            : '<div class="tooltip-empty">Sin goles registrados</div>';

        const tarjetasHtml = data.tarjetas && data.tarjetas.length
            ? data.tarjetas.map(t => `
                <div class="tooltip-event-row">
                    <span class="tooltip-minute">${t.minuto ?? '?'}'</span>
                    <span>${t.tipo === 'Amarilla' ? '🟨' : '🟥'}</span>
                    <span style="flex:1">${t.jugador}</span>
                    <span style="font-size:0.7rem; color:var(--text-muted); text-align:right">${t.equipo}</span>
                </div>`).join('')
            : '<div class="tooltip-empty">Sin tarjetas registradas</div>';

        tooltip.innerHTML = `
            <div class="tooltip-section-title">⚽ Goles</div>
            ${golesHtml}
            <div class="tooltip-section-title" style="margin-top:10px">🃏 Tarjetas</div>
            ${tarjetasHtml}
            <div style="margin-top:12px; padding-top:8px; border-top:1px solid rgba(255,255,255,0.1); font-size:0.75rem; color:var(--text-muted); display:flex; align-items:center; gap:6px;">
                <span>👤 Árbitro:</span>
                <span style="color:var(--primary); font-weight:700;">${data.arbitro || 'No asignado'}</span>
            </div>
        `;
    }

    async startLiguilla() {
        if (!this.currentLeagueId || this.currentLeagueId === 'all') {
            alert('Por favor seleccione una liga específica primero.');
            return;
        }
        const top_n = prompt('¿Cuántos equipos clasifican a la Liguilla? (Escriba 4 u 8)', '8');
        if (!top_n || !['4', '8'].includes(top_n)) {
            alert('Por favor ingrese 4 u 8.');
            return;
        }

        if (!confirm(`Se generarán emparejamientos de eliminación directa para los mejores ${top_n} equipos. ¿Continuar?`)) return;

        try {
            const res = await fetch(`/api/torneos/${this.currentLeagueId}/inicializar_liguilla`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ top_n: parseInt(top_n) })
            });
            const result = await res.json();
            if (result.success) {
                alert(result.message);
                // Redirigir al calendario despues de generar
                window.location.href = '/calendario';
            } else {
                alert('Error: ' + result.message);
            }
        } catch (e) {
            console.error(e);
            alert('Ocurrió un error al procesar la solicitud.');
        }
    }
}
