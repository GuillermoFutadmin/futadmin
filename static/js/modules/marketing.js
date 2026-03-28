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
    }

    // --- NAVEGACIÓN ---

    initAvisosEditor() {
        this.activeMode = 'avisos';
        this.showEditor('marketing-editor-avisos');
        
        const canvas = document.getElementById(this.canvasId);
        if(canvas) {
            canvas.width = this.config.width;
            canvas.height = this.config.height;
            this.ctx = canvas.getContext('2d');
            this.bindEventsAvisos();
            this.updateConfigFromForm(); 
            this.draw();
        }
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
    }

    refreshCanvasSize() {
        const canvas = document.getElementById(this.canvasGenId);
        if(!canvas) return;
        
        const format = document.getElementById('mkt-format')?.value || '1:1';
        if(format === '16:9') {
            canvas.width = 1920;
            canvas.height = 1080;
        } else {
            canvas.width = 1080;
            canvas.height = 1080;
        }
        this.ctxGen = canvas.getContext('2d');
        this.drawDynamic();
    }

    // --- CARGA DE DATOS ---

    async loadTeamsForFilter() {
        const selector = document.getElementById('mkt-filter-team');
        if(!selector) return;
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
        } catch(e) { console.error("Error cargando filtros", e); }
    }

    async loadTournamentsForSelector() {
        const selector = document.getElementById('mkt-data-selector');
        selector.innerHTML = '<option value="">Cargando torneos...</option>';
        try {
            const res = await fetch('/api/torneos');
            const data = await res.json();
            
            selector.innerHTML = '<option value="">-- Elige un torneo --</option>';
            data.forEach(t => {
                const opt = document.createElement('option');
                opt.value = t.id;
                opt.textContent = t.nombre;
                selector.appendChild(opt);
            });
        } catch(e) { selector.innerHTML = '<option value="">Error al cargar</option>'; }
    }

    // --- EVENTOS ---

    bindEventsDynamic() {
        const list = ['mkt-gen-bg1', 'mkt-gen-bg2', 'mkt-glocal', 'mkt-gvisit', 'mkt-scorers', 
                      'mkt-mvp-name', 'mkt-mvp-team', 'mkt-mvp-goals', 'mkt-mvp-rating', 
                      'mkt-rol-title', 'mkt-rol-footer', 'mkt-rol-day', 'mkt-rol-date', 
                      'mkt-filter-team', 'mkt-format'];
        list.forEach(id => {
            const el = document.getElementById(id);
            if(el) el.oninput = () => {
                if(id === 'mkt-format') this.refreshCanvasSize();
                else this.drawDynamic();
            };
        });

        document.getElementById('mkt-data-selector').onchange = (e) => this.handleDataSelection(e.target.value);

        const imgInput = document.getElementById('mkt-image-file');
        if (imgInput) {
            imgInput.onchange = (e) => {
                const reader = new FileReader();
                reader.onload = (evt) => {
                    const img = new Image();
                    img.onload = () => { this.config.dynamicImg = img; this.drawDynamic(); };
                    img.src = evt.target.result;
                };
                if(e.target.files[0]) reader.readAsDataURL(e.target.files[0]);
            };
        }
    }

    async handleDataSelection(id) {
        if(!id) return;
        if(this.activeMode === 'resultado') {
            const match = this.data.matches.find(m => m.id == id);
            if(match) {
                document.getElementById('label-local').innerText = match.equipo_local;
                document.getElementById('label-visitante').innerText = match.equipo_visitante;
                document.getElementById('mkt-glocal').value = match.goles_local;
                document.getElementById('mkt-gvisit').value = match.goles_visitante;
            }
        } else if(this.activeMode === 'mvp') {
            const player = this.data.players.find(p => p.id == id);
            if(player) {
                document.getElementById('mkt-mvp-name').value = player.nombre.toUpperCase();
                document.getElementById('mkt-mvp-team').value = (player.equipo_nombre || 'FUTADMIN').toUpperCase();
            }
        } else if(this.activeMode === 'rol') {
            // Cargar partidos del torneo seleccionado
            try {
                const res = await fetch(`/api/torneos/${id}/partidos`);
                const data = await res.json();
                this.data.matches = data.items || data || [];
            } catch(e) { console.error(e); }
        }
        this.drawDynamic();
    }

    // --- DIBUJO ---

    drawDynamic() {
        if(!this.ctxGen) return;
        const ctx = this.ctxGen;
        const canvas = document.getElementById(this.canvasGenId);
        const width = canvas.width, height = canvas.height;
        const bg1 = document.getElementById('mkt-gen-bg1').value;
        const bg2 = document.getElementById('mkt-gen-bg2').value;

        this.drawBackground(ctx, width, height, bg1, bg2);

        if(this.activeMode === 'resultado') this.renderResultado(ctx, width, height);
        else if(this.activeMode === 'mvp') this.renderMVP(ctx, width, height);
        else if(this.activeMode === 'rol') this.renderRolGrid(ctx, width, height);

        this.drawFooter(ctx, width, height);
    }

    renderResultado(ctx, w, h) {
        const local = document.getElementById('label-local').innerText || 'LOCAL';
        const visita = document.getElementById('label-visitante').innerText || 'VISITA';
        const gl = document.getElementById('mkt-glocal').value;
        const gv = document.getElementById('mkt-gvisit').value;
        const notes = document.getElementById('mkt-scorers').value;

        this.drawText(ctx, 'RESULTADO FINAL', w/2, 150, '900 60px "Inter"', '#fff', true);
        
        ctx.fillStyle = 'rgba(255,255,255,0.05)';
        this.drawRoundRect(ctx, w/2 - 120, 350, 240, 180, 20);
        ctx.fill();
        this.drawText(ctx, `${gl} - ${gv}`, w/2, 480, '900 120px "Inter"', '#00ff88', true);

        this.drawText(ctx, local.toUpperCase(), w/4, 450, '800 45px "Inter"', '#fff');
        this.drawText(ctx, visita.toUpperCase(), (w*3)/4, 450, '800 45px "Inter"', '#fff');

        if(notes) {
            ctx.fillStyle = '#f59e0b';
            ctx.font = '500 30px "Inter"';
            this.wrapText(ctx, notes, w/2, 650, w - 200, 40);
        }
        if(this.config.dynamicImg) this.drawCenteredImage(ctx, this.config.dynamicImg, w/2, 850, 180);
    }

    renderMVP(ctx, w, h) {
        const name = document.getElementById('mkt-mvp-name').value || 'JUGADOR MVP';
        const team = document.getElementById('mkt-mvp-team').value || 'EQUIPO';
        const rating = document.getElementById('mkt-mvp-rating').value || '9.9';
        const goals = document.getElementById('mkt-mvp-goals').value || '0';

        const radial = ctx.createRadialGradient(w/2, 450, 50, w/2, 450, 500);
        radial.addColorStop(0, 'rgba(139,92,246,0.3)');
        radial.addColorStop(1, 'transparent');
        ctx.fillStyle = radial;
        ctx.fillRect(0,0,w,h);

        if(this.config.dynamicImg) this.drawCenteredImage(ctx, this.config.dynamicImg, w/2, 450, 600);

        this.drawText(ctx, name, w/2, 820, '900 80px "Inter"', '#fff', true);
        this.drawText(ctx, team, w/2, 880, '700 35px "Inter"', '#8b5cf6');
        
        this.drawText(ctx, `GOLES: ${goals}`, w/2 - 150, 960, '800 45px "Inter"', '#fff');
        this.drawText(ctx, `RATING: ${rating}`, w/2 + 150, 960, '800 45px "Inter"', '#f59e0b');
    }

    renderRolGrid(ctx, w, h) {
        const title = document.getElementById('mkt-rol-title').value || 'PROGRAMACIÓN OFICIAL';
        const day = document.getElementById('mkt-rol-day').value || '';
        const date = document.getElementById('mkt-rol-date').value || '';
        const filterTeam = document.getElementById('mkt-filter-team').value;
        const footer = document.getElementById('mkt-rol-footer').value || '';

        // HEADER PREMIUM
        ctx.fillStyle = '#00ff88';
        this.drawRoundRect(ctx, 80, 80, 250, 40, 5); ctx.fill();
        this.drawText(ctx, title, 205, 108, '900 20px "Inter"', '#000');
        
        this.drawText(ctx, 'FUTADMIN', 185, 160, '900 70px "Inter"', '#fff');
        
        // CARD FECHA (Arriba derecha)
        ctx.fillStyle = 'rgba(255,255,255,0.05)';
        this.drawRoundRect(ctx, w - 400, 80, 320, 120, 15); ctx.fill();
        this.drawText(ctx, day, w - 240, 135, '900 45px "Inter"', '#00ff88');
        this.drawText(ctx, date, w - 240, 175, '500 22px "Inter"', 'rgba(255,255,255,0.6)');

        // FILTRAR PARTIDOS
        let matches = this.data.matches;
        if(filterTeam) {
            matches = matches.filter(m => m.equipo_local.includes(filterTeam) || m.equipo_visitante.includes(filterTeam));
        }
        matches = matches.slice(0, 16); // Max 16 para que quepan

        const cardW = (w - 200) / (w > 1200 ? 4 : 2);
        const cardH = 200;
        const gap = 20;
        let startX = 100, startY = 250;

        matches.forEach((m, i) => {
            const col = i % (w > 1200 ? 4 : 2);
            const row = Math.floor(i / (w > 1200 ? 4 : 2));
            const x = startX + (col * (cardW + gap));
            const y = startY + (row * (cardH + gap));

            // Card BG
            ctx.fillStyle = 'rgba(255,255,255,0.03)';
            this.drawRoundRect(ctx, x, y, cardW, cardH, 12); ctx.fill();
            ctx.strokeStyle = 'rgba(255,255,255,0.1)'; ctx.lineWidth = 1; ctx.stroke();

            // Info Partido
            ctx.fillStyle = '#00ff88';
            ctx.font = '900 16px "Inter"'; ctx.textAlign = 'left';
            ctx.fillText("JORNADA " + (m.jornada || "-"), x + 20, y + 35);
            
            // Hora Central
            this.drawText(ctx, m.hora || "00:00", x + cardW/2, y + 100, '900 45px "Inter"', '#fff');
            
            // Equipos
            ctx.font = '800 18px "Inter"'; ctx.textAlign = 'center';
            ctx.fillText(this.truncate(m.equipo_local, 12), x + 60, y + 160);
            ctx.fillText(this.truncate(m.equipo_visitante, 12), x + cardW - 60, y + 160);
            
            // Lugar
            ctx.fillStyle = 'rgba(255,255,255,0.4)';
            ctx.font = '500 14px "Inter"';
            ctx.fillText(m.campo || "POR DEFINIR", x + cardW/2, y + 190);
        });

        if(footer) this.drawText(ctx, footer.toUpperCase(), w/2, h - 140, '700 35px "Inter"', '#00ff88');
    }

    // --- UTILS ---
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

    truncate(str, n) { return (str.length > n) ? str.substr(0, n-1) + '...' : str; }

    clearLogo() { this.config.logoImg = null; this.draw(); }
    clearDynamicImage() { this.config.dynamicImg = null; this.drawDynamic(); }

    downloadImage() { this.downloadFromCanvas(this.canvasId); }
    downloadDynamicImage() { this.downloadFromCanvas(this.canvasGenId); }

    downloadFromCanvas(id) {
        const canvas = document.getElementById(id);
        if(!canvas) return;
        const url = canvas.toDataURL('image/png', 1.0);
        const link = document.createElement('a');
        link.download = `FutAdmin_Graphic_${Date.now()}.png`;
        link.href = url;
        link.click();
        link.remove();
    }
}
