export class MarketingModule {
    constructor(ui) {
        this.ui = ui;
        this.canvasId = 'marketing-canvas';
        this.canvasGenId = 'marketing-canvas-gen';
        this.ctx = null;
        this.ctxGen = null;

        // Estado actual del editor dinámico
        this.activeMode = 'avisos'; // 'resultado', 'mvp', 'rol'

        // Configuraciones base para Avisos Oficiales
        this.config = {
            width: 1080,
            height: 1080,
            bgColor1: '#0f172a',
            bgColor2: '#020617',
            title: 'AVISO IMPORTANTE',
            subtitle: 'COMUNICADO OFICIAL',
            body: 'Escribe aquí tu mensaje detallado para la comunidad, equipos o jugadores de la liga.',
            logoImg: null,
            dynamicImg: null // Para fotos de jugadores o banners personalizados
        };

        // Datos cargados para selectores
        this.data = {
            matches: [],
            players: [],
            leagues: []
        };

        // Desacoplamiento v72.0: Auto-inicialización vía eventos
        window.addEventListener('futadmin:view-change', (e) => {
            if (e.detail.viewId === 'marketing') this.init();
        });
    }

    /**
     * Método de inicialización llamado por main.js al navegar al Estudio Creativo.
     * Garantiza que siempre se muestre la grilla principal y no un editor previo.
     */
    init() {
        const grid = document.getElementById('marketing-grid');
        const editorAvisos = document.getElementById('marketing-editor-avisos');
        const editorContainer = document.getElementById('marketing-editor-container');
        const editorLogos = document.getElementById('marketing-editor-logos');

        if (grid) grid.style.display = 'grid';
        if (editorAvisos) editorAvisos.style.display = 'none';
        if (editorContainer) editorContainer.style.display = 'none';
        if (editorLogos) editorLogos.style.display = 'none';
    }

    // --- NAVEGACIÓN ---

    initAvisosEditor() {
        this.activeMode = 'avisos';
        this.showEditor('marketing-editor-avisos');

        const canvas = document.getElementById(this.canvasId);
        if (canvas) {
            canvas.width = this.config.width;
            canvas.height = this.config.height;
            this.ctx = canvas.getContext('2d');
            this.bindEventsAvisos();
            this.updateConfigFromForm();
            this.draw();
        }
    }

    initResultadoEditor() {
        this.activeMode = 'resultado';
        this.setupDynamicEditor('RESULTADO DEL PARTIDO', 'Selecciona el Partido Finalizado');
        this.loadMatchesForSelector('Finished');
        this.showDynamicControls('mkt-ctrl-resultado');
    }

    initMVPEditor() {
        this.activeMode = 'mvp';
        this.setupDynamicEditor('JUGADOR MVP', 'Selecciona al Jugador Destacado');
        this.loadPlayersForSelector();
        this.showDynamicControls('mkt-ctrl-mvp');
    }

    initRolEditor() {
        this.activeMode = 'rol';
        this.setupDynamicEditor('CARTELERA OFICIAL', 'Selecciona el Torneo');
        this.loadTournamentsForSelector();
        this.loadTeamsForFilter();
        this.showDynamicControls('mkt-ctrl-rol');
    }

    setupDynamicEditor(title, label) {
        document.getElementById('mkt-editor-title').innerText = title;
        document.getElementById('mkt-selector-label').innerText = label;
        document.getElementById('mkt-data-selector-group').style.display = 'block';
        this.showEditor('marketing-editor-container');
        this.refreshCanvasSize();
        this.bindEventsDynamic();
    }

    refreshCanvasSize() {
        const canvas = document.getElementById(this.canvasGenId);
        if (!canvas) return;

        const format = document.getElementById('mkt-format')?.value || '1:1';
        if (format === '16:9') {
            canvas.width = 1920;
            canvas.height = 1080;
        } else {
            canvas.width = 1080;
            canvas.height = 1080;
        }
        this.ctxGen = canvas.getContext('2d');
        this.drawDynamic();
    }

    showEditor(id) {
        document.getElementById('marketing-grid').style.display = 'none';
        document.getElementById('marketing-editor-logos').style.display = 'none';
        document.getElementById('marketing-editor-avisos').style.display = 'none';
        document.getElementById('marketing-editor-container').style.display = 'none';
        document.getElementById(id).style.display = 'flex';
    }

    showDynamicControls(id) {
        document.getElementById('mkt-ctrl-resultado').style.display = 'none';
        document.getElementById('mkt-ctrl-mvp').style.display = 'none';
        document.getElementById('mkt-ctrl-rol').style.display = 'none';
        document.getElementById(id).style.display = 'block';
    }

    closeEditor() {
        document.getElementById('marketing-editor-container').style.display = 'none';
        document.getElementById('marketing-editor-avisos').style.display = 'none';
        document.getElementById('marketing-editor-logos').style.display = 'none';
        document.getElementById('marketing-grid').style.display = 'grid';
    }

    initLogosGallery() {
        document.getElementById('marketing-grid').style.display = 'none';
        document.getElementById('marketing-editor-avisos').style.display = 'none';
        document.getElementById('marketing-editor-logos').style.display = 'flex';
    }

    closeLogosGallery() { this.closeEditor(); }

    // --- CARGA DE DATOS ---

    async loadMatchesForSelector(status = null) {
        const selector = document.getElementById('mkt-data-selector');
        selector.innerHTML = '<option value="">Cargando partidos...</option>';
        try {
            let url = '/api/partidos?limit=50';
            if (status) url += `&estado=${status}`;
            const res = await fetch(url);
            const data = await res.json();
            this.data.matches = data.items || [];

            selector.innerHTML = '<option value="">-- Elige un partido --</option>';
            this.data.matches.forEach(m => {
                const opt = document.createElement('option');
                opt.value = m.id;
                opt.textContent = `${m.equipo_local} vs ${m.equipo_visitante} (${m.fecha})`;
                selector.appendChild(opt);
            });
            this.mktOptionsCache = Array.from(selector.options);
        } catch (e) { selector.innerHTML = '<option value="">Error al cargar</option>'; }
    }

    async loadPlayersForSelector() {
        const selector = document.getElementById('mkt-data-selector');
        selector.innerHTML = '<option value="">Cargando jugadores...</option>';
        try {
            const res = await fetch('/api/jugadores?limit=100');
            const data = await res.json();
            this.data.players = data.items || [];

            selector.innerHTML = '<option value="">-- Elige un jugador --</option>';
            this.data.players.forEach(p => {
                const opt = document.createElement('option');
                opt.value = p.id;
                opt.textContent = `${p.nombre} (${p.equipo_nombre || 'Sin equipo'})`;
                selector.appendChild(opt);
            });
            this.mktOptionsCache = Array.from(selector.options);
        } catch (e) { selector.innerHTML = '<option value="">Error al cargar</option>'; }
    }

    async loadTeamsForFilter() {
        const selector = document.getElementById('mkt-filter-team');
        if (!selector) return;
        try {
            const res = await fetch('/api/equipos?limit=100');
            const data = await res.json();
            selector.innerHTML = '<option value="">TODOS LOS EQUIPOS</option>';
            data.items.forEach(t => {
                const opt = document.createElement('option');
                opt.value = t.nombre;
                opt.textContent = t.nombre;
                selector.appendChild(opt);
            });
        } catch (e) { console.error("Error cargando filtros", e); }
    }

    async loadTournamentsForSelector() {
        const selector = document.getElementById('mkt-data-selector');
        selector.innerHTML = '<option value="">Cargando torneos...</option>';
        try {
            const res = await fetch('/api/torneos');
            const data = await res.json();
            const items = data.items || data || [];

            selector.innerHTML = '<option value="">-- Elige un torneo --</option>';
            items.forEach(t => {
                const opt = document.createElement('option');
                opt.value = t.id;
                opt.textContent = t.nombre;
                selector.appendChild(opt);
            });
            this.mktOptionsCache = Array.from(selector.options);
        } catch (e) { selector.innerHTML = '<option value="">Error al cargar</option>'; }
    }

    // --- EVENTOS ---

    bindEventsAvisos() {
        const list = ['mkt-title', 'mkt-subtitle', 'mkt-body', 'mkt-bg1', 'mkt-bg2'];
        list.forEach(id => {
            const el = document.getElementById(id);
            if (el) el.oninput = () => this.updateConfigFromForm();
        });

        const logoInput = document.getElementById('mkt-logo-file');
        if (logoInput) {
            logoInput.onchange = (e) => {
                const reader = new FileReader();
                reader.onload = (evt) => {
                    const img = new Image();
                    img.onload = () => { this.config.logoImg = img; this.draw(); };
                    img.src = evt.target.result;
                };
                reader.readAsDataURL(e.target.files[0]);
            };
        }
    }

    bindEventsDynamic() {
        const list = ['mkt-gen-bg1', 'mkt-gen-bg2', 'mkt-glocal', 'mkt-gvisit', 'mkt-scorers',
            'mkt-mvp-name', 'mkt-mvp-team', 'mkt-mvp-goals', 'mkt-mvp-rating', 'mkt-mvp-gp',
            'mkt-rol-title', 'mkt-rol-footer', 'mkt-rol-day', 'mkt-rol-date',
            'mkt-filter-team', 'mkt-format'];
        list.forEach(id => {
            const el = document.getElementById(id);
            if (el) el.oninput = () => {
                if (id === 'mkt-format') this.refreshCanvasSize();
                else this.drawDynamic();
            };
        });

        // BUSCADOR DINÁMICO REFACTORIZADO
        const searchInput = document.getElementById('mkt-data-search');
        if (searchInput) {
            searchInput.oninput = (e) => {
                const term = e.target.value.toLowerCase();
                const selector = document.getElementById('mkt-data-selector');
                if (!this.mktOptionsCache) return;

                // Vaciar el selector y reconstruirlo con los elementos cacheados filtrados
                selector.innerHTML = '';
                this.mktOptionsCache.forEach((opt, idx) => {
                    // Mantener el primer elemento (placeholder) siempre visible, o si coincide
                    if (idx === 0 || opt.textContent.toLowerCase().includes(term)) {
                        selector.appendChild(opt.cloneNode(true));
                    }
                });
            };
        }

        document.getElementById('mkt-data-selector').onchange = (e) => {
            this.handleDataSelection(e.target.value);
        };

        const imgInput = document.getElementById('mkt-image-file');
        if (imgInput) {
            imgInput.onchange = (e) => {
                const reader = new FileReader();
                reader.onload = (evt) => {
                    const img = new Image();
                    img.onload = () => { this.config.dynamicImg = img; this.drawDynamic(); };
                    img.src = evt.target.result;
                };
                if (e.target.files[0]) reader.readAsDataURL(e.target.files[0]);
            };
        }
    }

    async handleDataSelection(id) {
        if (!id) return;

        // MOSTRAR LOADING O FEEDBACK SI ES NECESARIO
        const selector = document.getElementById('mkt-data-selector');
        selector.classList.add('loading-pulse');

        try {
            if (this.activeMode === 'resultado') {
                const res = await fetch(`/api/partido/${id}/detalles`);
                const details = await res.json();

                document.getElementById('label-local').innerText = this.data.matches.find(m => m.id == id)?.equipo_local || 'LOCAL';
                document.getElementById('label-visitante').innerText = this.data.matches.find(m => m.id == id)?.equipo_visitante || 'VISITA';

                document.getElementById('mkt-glocal').value = details.goles_local || 0;
                document.getElementById('mkt-gvisit').value = details.goles_visitante || 0;

                // GENERAR STRING DE GOLEADORES AUTOMATICAMENTE
                if (details.goles && details.goles.length > 0) {
                    const goalMap = {};
                    details.goles.forEach(g => {
                        const name = g.jugador || 'Anonimo';
                        goalMap[name] = (goalMap[name] || 0) + 1;
                    });
                    const scorerStr = Object.entries(goalMap).map(([name, count]) => `${name}${count > 1 ? ` (${count})` : ''}`).join(', ');
                    document.getElementById('mkt-scorers').value = scorerStr;
                } else {
                    document.getElementById('mkt-scorers').value = '';
                }

            } else if (this.activeMode === 'mvp') {
                const res = await fetch(`/api/jugadores/${id}/stats`);
                const stats = await res.json();

                document.getElementById('mkt-mvp-name').value = stats.nombre.toUpperCase();
                document.getElementById('mkt-mvp-team').value = stats.equipo.toUpperCase();
                document.getElementById('mkt-mvp-goals').value = stats.total_goles || 0;
                document.getElementById('mkt-mvp-gp').value = stats.partidos_jugados || 1;
                document.getElementById('mkt-mvp-rating').value = stats.rating || 9.5;

                // CARGAR FOTO AUTOMÁTICA SI EXISTE
                if (stats.foto_url) {
                    const img = new Image();
                    img.crossOrigin = "anonymous";
                    img.onload = () => { this.config.dynamicImg = img; this.drawDynamic(); };
                    img.src = stats.foto_url;
                } else {
                    this.config.dynamicImg = null;
                }

            } else if (this.activeMode === 'rol') {
                const res = await fetch(`/api/torneos/${id}/partidos`);
                const data = await res.json();
                this.data.matches = data.items || data || [];

                // AUTO-LLENAR FECHA DEL PRIMER PARTIDO
                if (this.data.matches.length > 0) {
                    const first = this.data.matches[0];
                    if (first.fecha) {
                        const dateObj = new Date(first.fecha + 'T12:00:00');
                        const days = ['DOMINGO', 'LUNES', 'MARTES', 'MIÉRCOLES', 'JUEVES', 'VIERNES', 'SÁBADO'];
                        const months = ['ENERO', 'FEBRERO', 'MARZO', 'ABRIL', 'MAYO', 'JUNIO', 'JULIO', 'AGOSTO', 'SEPTIEMBRE', 'OCTUBRE', 'NOVIEMBRE', 'DICIEMBRE'];

                        document.getElementById('mkt-rol-day').value = days[dateObj.getDay()];
                        document.getElementById('mkt-rol-date').value = `${dateObj.getDate()} DE ${months[dateObj.getMonth()]}, ${dateObj.getFullYear()}`;
                    }
                }
            }
        } catch (e) {
            console.error("Error fetching automation data:", e);
        } finally {
            selector.classList.remove('loading-pulse');
            this.drawDynamic();
        }
    }

    updateConfigFromForm() {
        this.config.title = document.getElementById('mkt-title').value.toUpperCase();
        this.config.subtitle = document.getElementById('mkt-subtitle').value.toUpperCase();
        this.config.body = document.getElementById('mkt-body').value || '';
        this.config.bgColor1 = document.getElementById('mkt-bg1').value || '#0f172a';
        this.config.bgColor2 = document.getElementById('mkt-bg2').value || '#020617';
        this.draw();
    }

    // --- DIBUJO ---

    draw() {
        if (!this.ctx) return;
        const ctx = this.ctx;
        const { width, height } = this.config;
        this.drawBackground(ctx, width, height, this.config.bgColor1, this.config.bgColor2);

        let y = 180;
        if (this.config.logoImg) {
            this.drawCenteredImage(ctx, this.config.logoImg, width / 2, y, 240);
            y += 300;
        } else y += 120;

        this.drawText(ctx, this.config.subtitle, width / 2, y, '700 32px "Inter"', '#f59e0b');
        y += 60;
        this.drawText(ctx, this.config.title, width / 2, y, '900 80px "Inter"', '#ffffff', true);
        y += 40;
        ctx.fillStyle = '#f59e0b';
        ctx.fillRect((width / 2) - 80, y - 30, 160, 6);
        y += 40;

        if (this.config.body) {
            ctx.fillStyle = 'rgba(255,255,255,0.9)';
            ctx.font = '400 42px "Inter"';
            this.wrapText(ctx, this.config.body, width / 2, y, width - 180, 55);
        }
        this.drawFooter(ctx, width, height);
    }

    drawDynamic() {
        if (!this.ctxGen) return;
        const ctx = this.ctxGen;
        const canvas = document.getElementById(this.canvasGenId);
        const width = canvas.width, height = canvas.height;
        const bg1 = document.getElementById('mkt-gen-bg1').value;
        const bg2 = document.getElementById('mkt-gen-bg2').value;

        this.drawBackground(ctx, width, height, bg1, bg2);

        if (this.activeMode === 'resultado') this.renderResultado(ctx, width, height);
        else if (this.activeMode === 'mvp') this.renderMVP(ctx, width, height);
        else if (this.activeMode === 'rol') this.renderRolGrid(ctx, width, height);

        this.drawFooter(ctx, width, height);
    }

    renderResultado(ctx, w, h) {
        const local = document.getElementById('label-local').innerText || 'LOCAL';
        const visita = document.getElementById('label-visitante').innerText || 'VISITA';
        const gl = document.getElementById('mkt-glocal').value;
        const gv = document.getElementById('mkt-gvisit').value;
        const notes = document.getElementById('mkt-scorers').value;

        this.drawText(ctx, 'RESULTADO FINAL', w / 2, 150, '900 60px "Inter"', '#fff', true);

        ctx.fillStyle = 'rgba(255,255,255,0.05)';
        this.drawRoundRect(ctx, w / 2 - 120, 350, 240, 180, 20);
        ctx.fill();
        this.drawText(ctx, `${gl} - ${gv}`, w / 2, 480, '900 120px "Inter"', '#00ff88', true);

        this.drawText(ctx, local.toUpperCase(), w / 4, 450, '800 45px "Inter"', '#fff');
        this.drawText(ctx, visita.toUpperCase(), (w * 3) / 4, 450, '800 45px "Inter"', '#fff');

        if (notes) {
            ctx.fillStyle = '#f59e0b';
            ctx.font = '500 30px "Inter"';
            this.wrapText(ctx, notes, w / 2, 650, w - 200, 40);
        }
        if (this.config.dynamicImg) this.drawCenteredImage(ctx, this.config.dynamicImg, w / 2, 850, 180);
    }

    renderMVP(ctx, w, h) {
        const name = document.getElementById('mkt-mvp-name').value || 'JUGADOR MVP';
        const team = document.getElementById('mkt-mvp-team').value || 'EQUIPO';
        const rating = document.getElementById('mkt-mvp-rating').value || '9.5';
        const goals = document.getElementById('mkt-mvp-goals').value || '0';
        const gp = document.getElementById('mkt-mvp-gp').value || '1';

        const radial = ctx.createRadialGradient(w / 2, 450, 50, w / 2, 450, 500);
        radial.addColorStop(0, 'rgba(139,92,246,0.3)');
        radial.addColorStop(1, 'transparent');
        ctx.fillStyle = radial;
        ctx.fillRect(0, 0, w, h);

        if (this.config.dynamicImg) this.drawCenteredImage(ctx, this.config.dynamicImg, w / 2, 450, 600);

        this.drawText(ctx, name, w / 2, 820, '900 80px "Inter"', '#fff', true);
        this.drawText(ctx, team, w / 2, 880, '700 35px "Inter"', '#8b5cf6');

        const statsY = 960;
        this.drawText(ctx, `G: ${goals}`, w / 2 - 200, statsY, '800 50px "Inter"', '#fff');
        this.drawText(ctx, `GP: ${gp}`, w / 2, statsY, '800 50px "Inter"', '#00ff88');
        this.drawText(ctx, `RTG: ${rating}`, w / 2 + 200, statsY, '800 50px "Inter"', '#f59e0b');
    }

    renderRolGrid(ctx, w, h) {
        const title = document.getElementById('mkt-rol-title').value || 'PROGRAMACIÓN OFICIAL';
        const day = (document.getElementById('mkt-rol-day').value || 'SÁBADO').toUpperCase();
        const date = (document.getElementById('mkt-rol-date').value || 'SETIEMBRE 2026').toUpperCase();
        const filterTeam = document.getElementById('mkt-filter-team').value;
        const footerText = document.getElementById('mkt-rol-footer').value || '¡No faltes! - futbol en vivo';

        // HEADER PRO (Logo FutAdmin y Subtítulo)
        ctx.fillStyle = '#00ff88';
        this.drawRoundRect(ctx, 80, 80, 240, 42, 6); ctx.fill();
        this.drawText(ctx, title, 200, 110, '900 22px "Inter"', '#000');

        ctx.fillStyle = '#fff';
        ctx.font = '900 85px "Inter"'; ctx.textAlign = 'left';
        ctx.fillText("FUTADMIN", 80, 200);

        ctx.fillStyle = 'rgba(255,255,255,0.6)';
        ctx.font = '500 24px "Inter"';
        ctx.fillText("| Tu liga en la palma de tu mano", 80, 240);

        // DATE CARD PRO (Esquina Superior Derecha)
        const dateW = 380, dateH = 140;
        const dateX = w - dateW - 80, dateY = 80;
        ctx.fillStyle = 'rgba(255,255,255,0.05)';
        this.drawRoundRect(ctx, dateX, dateY, dateW, dateH, 18); ctx.fill();
        ctx.strokeStyle = 'rgba(255,255,255,0.1)'; ctx.stroke();

        this.drawText(ctx, day, dateX + dateW / 2, dateY + 65, '900 65px "Inter"', '#00ff88');
        this.drawText(ctx, date, dateX + dateW / 2, dateY + 110, '600 26px "Inter"', 'rgba(255,255,255,0.7)');

        // FILTRADO DE PARTIDOS
        let matches = this.data.matches;
        if (filterTeam && filterTeam !== 'TODOS LOS EQUIPOS!') {
            matches = matches.filter(m => m.equipo_local.includes(filterTeam) || m.equipo_visitante.includes(filterTeam));
        }
        matches = matches.slice(0, 16);

        // CONFIGURACIÓN DE REJILLA (Adaptive)
        const cols = (w > 1200) ? 4 : 2;
        const gap = 25;
        const cardW = (w - 180 - (gap * (cols - 1))) / cols; // Ajuste fino de ancho
        const cardH = 220;
        let startX = 80, startY = 320;

        matches.forEach((m, i) => {
            const col = i % cols;
            const row = Math.floor(i / cols);
            const x = startX + (col * (cardW + gap));
            const y = startY + (row * (cardH + gap));

            // Card BG Pro
            ctx.fillStyle = 'rgba(255,255,255,0.04)';
            this.drawRoundRect(ctx, x, y, cardW, cardH, 15); ctx.fill();
            ctx.strokeStyle = 'rgba(255,255,255,0.12)'; ctx.lineWidth = 1.5; ctx.stroke();

            // Jornada Badge
            ctx.fillStyle = '#00ff88';
            ctx.font = '900 18px "Inter"'; ctx.textAlign = 'left';
            ctx.fillText("JORNADA " + (m.jornada || "5"), x + 25, y + 42);

            // Sede Info
            ctx.fillStyle = 'rgba(255,255,255,0.4)';
            ctx.font = '500 15px "Inter"'; ctx.textAlign = 'right';
            ctx.fillText("📍 " + (m.cancha || "CANCHA #1"), x + cardW - 25, y + 42);

            // Time Divider
            this.drawText(ctx, m.hora || "10:00", x + cardW / 2, y + 115, '900 55px "Inter"', '#fff');
            ctx.fillStyle = 'rgba(255,255,255,0.1)';
            ctx.font = '700 14px "Inter"';
            ctx.fillText("VS", x + cardW / 2, y + 140);

            // Team Names & Fake Logos
            ctx.font = '800 20px "Inter"'; ctx.textAlign = 'center';
            ctx.fillStyle = '#fff';
            ctx.fillText(this.truncate(m.equipo_local.toUpperCase(), 14), x + cardW * 0.25, y + 190);
            ctx.fillText(this.truncate(m.equipo_visitante.toUpperCase(), 14), x + cardW * 0.75, y + 190);

            // Circles for logos
            ctx.fillStyle = '#00ff88';
            ctx.beginPath(); ctx.arc(x + cardW * 0.25, y + 105, 35, 0, Math.PI * 2); ctx.fill();
            ctx.fillStyle = '#0ea5e9';
            ctx.beginPath(); ctx.arc(x + cardW * 0.75, y + 105, 35, 0, Math.PI * 2); ctx.fill();
            this.drawText(ctx, m.equipo_local[0], x + cardW * 0.25, y + 118, '900 35px "Inter"', '#000');
            this.drawText(ctx, m.equipo_visitante[0], x + cardW * 0.75, y + 118, '900 35px "Inter"', '#000');
        });

        // FOOTER PRO
        const footerY = h - 120;
        this.drawText(ctx, footerText.toUpperCase(), w / 2, footerY - 50, '700 35px "Inter"', '#fff');

        ctx.fillStyle = '#00ff88';
        ctx.font = '900 28px "Inter"'; ctx.textAlign = 'center';
        ctx.fillText("futadmin.com.mx", w / 2 + 80, footerY);

        ctx.fillStyle = 'rgba(255,255,255,0.4)';
        ctx.font = '500 22px "Inter"';
        ctx.fillText("Si quieres ver el resumen detallado de tu liga, miralo en", w / 2 - 180, footerY);

        this.drawText(ctx, "RESULTADOS • ESTADÍSTICAS • POSICIONES • FOTOS", w / 2, footerY + 50, '600 20px "Inter"', 'rgba(255,255,255,0.4)');
    }

    // --- UTILS ---
    drawBackground(ctx, w, h, c1, c2) {
        const grad = ctx.createLinearGradient(0, 0, w, h);
        grad.addColorStop(0, c1);
        grad.addColorStop(1, c2);
        ctx.fillStyle = grad;
        ctx.fillRect(0, 0, w, h);

        // Grid pattern sutil y pro
        ctx.strokeStyle = 'rgba(0,255,136,0.04)';
        ctx.lineWidth = 1.5;
        for (let i = 0; i < w; i += 80) {
            ctx.beginPath(); ctx.moveTo(i, 0); ctx.lineTo(i, h); ctx.stroke();
            ctx.beginPath(); ctx.moveTo(0, i); ctx.lineTo(w, i); ctx.stroke();
        }

        // Borde interior de estilo 'Broadcast'
        ctx.strokeStyle = 'rgba(0,0,0,0.6)';
        ctx.lineWidth = 40;
        ctx.strokeRect(20, 20, w - 40, h - 40);

        ctx.strokeStyle = '#00ff88';
        ctx.lineWidth = 4;
        ctx.strokeRect(40, 40, w - 80, h - 80);
    }

    drawCenteredImage(ctx, img, x, y, size) {
        ctx.shadowColor = "rgba(0,0,0,0.6)"; ctx.shadowBlur = 30;
        ctx.drawImage(img, x - size / 2, y - size / 2, size, size);
        ctx.shadowColor = "transparent"; ctx.shadowBlur = 0;
    }

    drawText(ctx, text, x, y, font, color, stroke = false) {
        if (!text) return;
        ctx.fillStyle = color;
        ctx.font = font;
        ctx.textAlign = 'center';
        if (stroke) {
            ctx.lineWidth = 3; ctx.strokeStyle = '#000';
            ctx.strokeText(text, x, y);
        }
        ctx.fillText(text, x, y);
    }

    wrapText(ctx, text, x, y, maxWidth, lineHeight) {
        if (!text) return;
        const paragraphs = text.split('\n');
        paragraphs.forEach(p => {
            const words = p.split(' ');
            let line = '';
            for (let n = 0; n < words.length; n++) {
                let testLine = line + words[n] + ' ';
                if (ctx.measureText(testLine).width > maxWidth && n > 0) {
                    ctx.fillText(line, x, y);
                    line = words[n] + ' ';
                    y += lineHeight;
                } else line = testLine;
            }
            ctx.fillText(line, x, y);
            y += lineHeight;
        });
    }

    drawFooter(ctx, w, h) {
        // Footer genérico solo para Avisos
        if (this.activeMode === 'avisos') {
            ctx.fillStyle = 'rgba(255,255,255,0.2)';
            ctx.font = '700 22px "Inter"';
            ctx.textAlign = 'center';
            ctx.fillText('POWERED BY FUTADMIN.COM.MX', w / 2, h - 80);
        }
    }

    drawRoundRect(ctx, x, y, w, h, r) {
        ctx.beginPath();
        ctx.moveTo(x + r, y);
        ctx.lineTo(x + w - r, y);
        ctx.quadraticCurveTo(x + w, y, x + w, y + r);
        ctx.lineTo(x + w, y + h - r);
        ctx.quadraticCurveTo(x + w, y + h, x + w - r, y + h);
        ctx.lineTo(x + r, y + h);
        ctx.quadraticCurveTo(x, y + h, x, y + h - r);
        ctx.lineTo(x, y + r);
        ctx.quadraticCurveTo(x, y, x + r, y);
        ctx.closePath();
    }

    truncate(str, n) {
        if (!str) return "";
        return (str.length > n) ? str.substr(0, n - 1) + '...' : str.substring(0, n);
    }

    clearLogo() { this.config.logoImg = null; this.draw(); }
    clearDynamicImage() { this.config.dynamicImg = null; this.drawDynamic(); }

    downloadImage() { this.downloadFromCanvas(this.canvasId); }
    downloadDynamicImage() { this.downloadFromCanvas(this.canvasGenId); }

    downloadFromCanvas(id) {
        const canvas = document.getElementById(id);
        if (!canvas) return;
        const url = canvas.toDataURL('image/png', 1.0);
        const link = document.createElement('a');
        link.download = `FutAdmin_Pro_${Date.now()}.png`;
        link.href = url;
        link.click();
        link.remove();
    }
}
