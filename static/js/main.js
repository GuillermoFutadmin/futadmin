/**
 * Punto de entrada principal - FutAdmin ESM
 */
import { Core } from './modules/core.js';
import { LeaguesModule } from './modules/leagues.js?v=46';
import { TeamsModule } from './modules/teams.js?v=46';
import { PlayersModule } from './modules/players.js?v=46';
import { FinanceModule } from './modules/finance.js?v=46';
import { ArbitrosModule } from './modules/arbitros.js';
import { DashboardModule } from './modules/dashboard.js';
import EntrenamientosModule from './modules/entrenamientos.js?v=46';
import PagosAcademiaModule from './modules/pagos-academia.js';
import { CanchasModule } from './modules/canchas.js';
import { PagosCanchasModule } from './modules/pagos-canchas.js';
import { SettingsModule } from './modules/settings.js';
import { AnalyticsModule } from './modules/analytics.js';
import { PrivacyModule } from './modules/privacy.js';
import { DashboardMap } from './modules/dashboard_map.js';
import { MarketingModule } from './modules/marketing.js';

class FutAdminUI {
    constructor() {
        this.currentView = 'resumen';

        // Inicializar módulos
        this.leagues = new LeaguesModule(this);
        this.teams = new TeamsModule(this);
        this.players = new PlayersModule(this);
        this.finance = new FinanceModule(this);
        this.arbitros = new ArbitrosModule(this);
        this.dashboard = new DashboardModule(this);
        this.entrenamientos = new EntrenamientosModule(this);
        this.pagosAcademia = new PagosAcademiaModule(this);
        this.canchas = new CanchasModule(this);
        this.pagosCanchas = new PagosCanchasModule(this);
        this.settings = new SettingsModule(this);
        this.analytics = new AnalyticsModule(this);
        this.privacy = new PrivacyModule(this);
        this.map = new DashboardMap();
        this.marketing = new MarketingModule(this);

        this.initEventListeners();
        this.loadInitialStats();
        this.dashboard.init(); // Cargar selector de ligas desde el inicio


        // Global access for onclick events (compatibility)
        window.ui = this;
        window.Core = Core;
    }

    initEventListeners() {
        // Navegación Sidebar
        document.querySelectorAll('.nav-item').forEach(item => {
            item.addEventListener('click', () => {
                const view = item.getAttribute('data-view');
                if (view && !item.classList.contains('has-submenu')) {
                    this.switchView(view);
                    this.updateActiveNav(item);
                }
            });
        });

        // Evitar que el clic en submenús cierre el menú padre (stopPropagation)
        document.querySelectorAll('.submenu').forEach(sub => {
            sub.addEventListener('click', (e) => e.stopPropagation());
        });

        // Formularios
        const setupForm = (id, handler) => {
            const form = document.getElementById(id);
            if (form) form.addEventListener('submit', (e) => handler.call(this[id.split('-')[0] + 's'] || this, e));
        };

        document.getElementById('league-form')?.addEventListener('submit', (e) => this.leagues.handleLeagueSubmit(e));
        document.getElementById('team-form')?.addEventListener('submit', (e) => this.teams.handleEquipoSubmit(e));
        document.getElementById('player-form')?.addEventListener('submit', (e) => this.players.handleJugadorSubmit(e));
        document.getElementById('inscripcion-form')?.addEventListener('submit', (e) => this.finance.handleInscripcionSubmit(e));
        document.getElementById('pago-form')?.addEventListener('submit', (e) => this.finance.handlePagoSubmit(e));
        document.getElementById('arbitro-form')?.addEventListener('submit', (e) => this.arbitros.handleArbitroSubmit(e));
        document.getElementById('cancha-form')?.addEventListener('submit', (e) => this.canchas.handleCanchaSubmit(e));

        // Uploads globales
        document.querySelectorAll('input[type="file"][data-target]').forEach(input => {
            input.addEventListener('change', (e) => this.handleGlobalUpload(e));
        });
    }

    updateActiveNav(activeItem) {
        // Remover activo de todos los items principales y sub-items
        document.querySelectorAll('.nav-item, .submenu li').forEach(i => i.classList.remove('active'));

        if (activeItem.tagName === 'LI' && activeItem.parentElement.classList.contains('submenu')) {
            // Es un sub-item
            activeItem.classList.add('active');
            // Asegurar que el padre esté abierto
            const parentNavItem = activeItem.closest('.nav-item');
            if (parentNavItem) {
                parentNavItem.classList.add('active', 'open');
            }
        } else {
            // Es un item principal
            activeItem.classList.add('active');
        }
    }

    async switchView(viewId, tabId = null, element = null) {
        this.currentView = viewId;

        // Asegurar que las estadísticas estén frescas si entramos a vistas de límites
        if (viewId === 'torneos' || viewId === 'canchas') {
            await this.loadInitialStats();
        }

        if (element) {
            this.updateActiveNav(element);
        }
        document.querySelectorAll('.view-container, .sub-view').forEach(view => {
            view.style.display = 'none';
            view.classList.remove('active');
        });

        const targetView = document.getElementById(`view-${viewId}`);
        if (targetView) {
            // Pequeño retraso para permitir que el ojo note el cambio de estado
            setTimeout(() => {
                targetView.style.display = 'block';
                // La clase .active dispara la animación CSS fadeInUp
                setTimeout(() => targetView.classList.add('active'), 20);
            }, 50);
        }

        const titleMap = {
            'resumen': 'Estadísticas',
            'torneos': 'Gestión de Ligas',
            'inscripciones': 'Control de Inscripciones',
            'arbitrajes': 'Pagos de Arbitraje',
            'arbitros': 'Cuerpo Arbitral',
            'estadisticas': 'Estadísticas Globales',
            'ajustes': 'Ajustes del Sistema',
            'entrenamientos': 'Academias y Entrenamientos',
            'pagos-academia': 'Pagos de Academia',
            'canchas': 'Sedes y Canchas',
            'pagos-canchas': 'Pagos de Sedes',
            'archivo': 'Historial / Papelera'
        };
        document.getElementById('current-view-title').innerText = titleMap[viewId] || 'FutAdmin';

        // Cargar datos del módulo
        if (viewId === 'torneos') this.switchTorneosTab(tabId || 'torneos-lista');
        else if (viewId === 'inscripciones') this.finance.populateInscripcionLeagueSelect();
        else if (viewId === 'arbitrajes') this.finance.populateArbitrajeLeagueSelect();
        else if (viewId === 'arbitros') this.arbitros.loadArbitros();
        else if (viewId === 'resumen') this.dashboard.init();
        else if (viewId === 'entrenamientos') {
            document.querySelectorAll('#view-entrenamientos .tab-content').forEach(c => c.style.display = 'none');
            const target = document.getElementById(`entrenamientos-${tabId || 'grupos'}`);
            if (target) {
                target.style.display = 'block';
                if ((tabId || 'grupos') === 'grupos') this.entrenamientos.loadGrupos();
            }
        }
        else if (viewId === 'pagos-academia') this.pagosAcademia.init();
        else if (viewId === 'canchas') this.canchas.loadCanchas();
        else if (viewId === 'pagos-canchas') this.pagosCanchas.loadEstadosCuenta();
        else if (viewId === 'archivo') this.leagues.loadArchivedLeagues();
        else if (viewId === 'ajustes') {
            this.settings.init();
            if (tabId) this.settings.switchTab(tabId);
        }
    }

    switchTorneosTab(tabId) {
        document.querySelectorAll('.content-tab').forEach(tab => {
            tab.classList.remove('active');
            if (tab.getAttribute('data-tab') === tabId) tab.classList.add('active');
        });

        document.querySelectorAll('.torneos-tab-content').forEach(content => {
            content.style.display = 'none';
            content.classList.remove('active');
        });

        const targetContent = document.getElementById(`tab-${tabId}`);
        if (targetContent) {
            targetContent.style.display = 'block';
            setTimeout(() => targetContent.classList.add('active'), 10);
        }

        if (tabId === 'torneos-lista') this.leagues.loadLeagues();
        else if (tabId === 'equipos') this.teams.populateLeagueSelects();
        else if (tabId === 'jugadores') this.players.populateTeamSelects();
    }

    async loadInitialStats(forceUpdate = false) {
        // Evitar múltiples llamadas simultáneas (Singleton pattern)
        if (this._statsPromise && !forceUpdate) return this._statsPromise;
        if (forceUpdate) this._statsPromise = null;

        this._statsPromise = (async () => {
            try {
                const data = await Core.fetchAPI('/api/stats');
                
                // Guardar límites globales para control de UI
                window.FutAdminLimits = data.limits || {};
                window.FutAdminCounts = data.current_counts || {};
                window.futUserRol = data.user_rol || null;

                // Control dinámico de visibilidad para Entrenamientos
                const trainItem = document.getElementById('nav-item-entrenamientos');
                if (trainItem) {
                    if (window.FutAdminCounts.entrenadores > 0 || ['admin', 'ejecutivo'].includes(window.futUserRol?.toLowerCase())) {
                        trainItem.style.display = 'block';
                    } else {
                        trainItem.style.display = 'none';
                    }
                }
                
                // Disparar evento para que los módulos actualicen su UI si dependen de los límites
                document.dispatchEvent(new CustomEvent('futadmin:limitsLoaded'));

                // Render basic stats
                const container = document.getElementById('stats-dashboard');
                if (container) {
                    container.innerHTML = `
                        <div class="stat-card">
                            <p class="section-title">LIGAS ACTIVAS</p>
                            <div class="value" style="font-size: 2.5rem; font-weight: 700; color: var(--primary);">${data.torneos_activos || 0}</div>
                        </div>
                        <div class="stat-card">
                            <p class="section-title">EQUIPOS TOTALES</p>
                            <div class="value" style="font-size: 2.5rem; font-weight: 700;">${data.total_equipos || 0}</div>
                        </div>
                        <div class="stat-card">
                            <p class="section-title">JUGADORES REGISTRADOS</p>
                            <div class="value" style="font-size: 2.5rem; font-weight: 700;">${data.total_jugadores || 0}</div>
                        </div>
                    `;
                }

                // Render active tournaments detailed view in the welcome banner
                const banner = document.querySelector('.welcome-banner');
                if (banner && data.torneos_detalle && data.torneos_detalle.length > 0) {
                    let html = `<h2 style="font-size: 1.8rem; margin-bottom: 1.5rem;">Ligas Activas en Desarrollo</h2>
                                <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 1.5rem;">`;

                    data.torneos_detalle.forEach(t => {
                        const totalPartidos = t.partidos_jugados + t.partidos_pendientes;
                        const progress = totalPartidos > 0 ? Math.round((t.partidos_jugados / totalPartidos) * 100) : 0;

                        html += `
                        <div style="background: rgba(0,0,0,0.3); padding: 1.5rem; border-radius: 16px; border: 1px solid var(--border);">
                            <div style="display: flex; justify-content: space-between; align-items: start; margin-bottom: 12px;">
                                <h4 style="color: var(--primary); font-size: 1.1rem; margin: 0;">${t.nombre}</h4>
                                <span style="font-size: 0.8rem; background: rgba(255,255,255,0.1); padding: 4px 10px; border-radius: 20px;">${t.jornadas_totales} Jornadas</span>
                            </div>
                            <div style="font-size: 0.85rem; color: var(--text-muted); margin-bottom: 12px;">
                                <strong>${t.partidos_jugados}</strong> partidos jugados • <strong>${t.partidos_pendientes}</strong> pendientes
                            </div>
                            <div style="width: 100%; height: 6px; background: rgba(255,255,255,0.1); border-radius: 4px; overflow: hidden; position: relative;">
                                <div style="width: ${progress}%; height: 100%; background: var(--primary); transition: width 1s ease-in-out;"></div>
                            </div>
                        </div>`;
                    });

                    html += `</div>`;
                    banner.innerHTML = html;
                } else if (banner) {
                    banner.innerHTML = `
                        <h2>Bienvenido a FutAdmin Professional</h2>
                        <p>Aún no hay torneos activos. Ve a Gestión de Ligas para comenzar.</p>
                    `;
                }

                // Update Map
                if (data.geo_stats) {
                    this.map.update(Object.values(data.geo_stats));
                }

                return data;
            } catch (error) { 
                console.error('Error stats:', error); 
                this._statsPromise = null; // Permitir reintento
                throw error;
            }
        })();

        return this._statsPromise;
    }

    async handleGlobalUpload(event) {
        const input = event.target;
        if (!input.files || input.files.length === 0) return;
        const file = input.files[0];
        const targetId = input.getAttribute('data-target');
        const targetInputId = input.getAttribute('data-target');
        const formData = new FormData();
        formData.append('file', file);

        Core.fetchAPI('/api/upload', {
            method: 'POST',
            body: formData
        })
            .then(data => {
                if (data.url) {
                    const targetInput = document.getElementById(targetInputId);
                    if (targetInput) {
                        targetInput.value = data.url;
                        // Disparar evento change para que el onchange del input funcione
                        targetInput.dispatchEvent(new Event('change'));
                    }

                    // Si hay un contenedor de preview definido
                    const previewId = event.target.getAttribute('data-preview');
                    if (previewId) {
                        const img = document.getElementById(previewId);
                        if (img) {
                            img.src = data.url;
                            img.style.display = 'block';
                            // Ocultar el placeholder si existe
                            const placeholder = document.getElementById(previewId + '-placeholder');
                            if (placeholder) placeholder.style.display = 'none';
                        }
                    }

                    Core.showNotification('Imagen subida con éxito');
                } else {
                    alert('Error al subir la imagen.');
                }
            })
            .catch(error => {
                console.error('Error al subir la imagen:', error);
                alert('Error al subir la imagen.');
            })
            .finally(() => {
                input.value = '';
            });
    }

    toggleSubmenu(element) {
        element.classList.toggle('open');
    }
}

// Inicializar la App
document.addEventListener('DOMContentLoaded', () => {
    new FutAdminUI();
});
