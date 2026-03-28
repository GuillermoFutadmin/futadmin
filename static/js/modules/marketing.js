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
        this.setupDynamicEditor('ROL DE JUEGOS', 'Selecciona el Torneo');
        this.loadTournamentsForSelector();
        this.showDynamicControls('mkt-ctrl-rol');
    }

    setupDynamicEditor(title, label) {
        document.getElementById('mkt-editor-title').innerText = title;
        document.getElementById('mkt-selector-label').innerText = label;
        document.getElementById('mkt-data-selector-group').style.display = 'block';
        this.showEditor('marketing-editor-container');
        
        const canvas = document.getElementById(this.canvasGenId);
        if(canvas) {
            canvas.width = this.config.width;
            canvas.height = this.config.height;
            this.ctxGen = canvas.getContext('2d');
            this.bindEventsDynamic();
            this.drawDynamic();
        }
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
            if(status) url += `&estado=${status}`;
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
        } catch(e) { selector.innerHTML = '<option value="">Error al cargar</option>'; }
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
        } catch(e) { selector.innerHTML = '<option value="">Error al cargar</option>'; }
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

    bindEventsAvisos() {
        const list = ['mkt-title', 'mkt-subtitle', 'mkt-body', 'mkt-bg1', 'mkt-bg2'];
        list.forEach(id => {
            const el = document.getElementById(id);
            if(el) el.oninput = () => this.updateConfigFromForm();
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
        // Inputs generales
        const list = ['mkt-gen-bg1', 'mkt-gen-bg2', 'mkt-glocal', 'mkt-gvisit', 'mkt-scorers', 'mkt-mvp-name', 'mkt-mvp-team', 'mkt-mvp-goals', 'mkt-mvp-rating', 'mkt-rol-title', 'mkt-rol-footer'];
        list.forEach(id => {
            const el = document.getElementById(id);
            if(el) el.oninput = () => this.drawDynamic();
        });

        // Selector de datos
        document.getElementById('mkt-data-selector').onchange = (e) => this.handleDataSelection(e.target.value);

        // Upload de imagen dinámica
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

    handleDataSelection(id) {
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
        }
        this.drawDynamic();
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
        if(!this.ctx) return;
        const ctx = this.ctx;
        const { width, height } = this.config;
        this.drawBackground(ctx, width, height, this.config.bgColor1, this.config.bgColor2);

        let y = 180;
        if(this.config.logoImg) {
            this.drawCenteredImage(ctx, this.config.logoImg, width/2, y, 240);
            y += 300;
        } else y += 120;

        this.drawText(ctx, this.config.subtitle, width/2, y, '700 32px "Inter"', '#f59e0b');
        y += 60;
        this.drawText(ctx, this.config.title, width/2, y, '900 80px "Inter"', '#ffffff', true);
        y += 40;
        ctx.fillStyle = '#f59e0b';
        ctx.fillRect((width/2) - 80, y - 30, 160, 6);
        y += 40;

        if(this.config.body) {
            ctx.fillStyle = 'rgba(255,255,255,0.9)';
            ctx.font = '400 42px "Inter"';
            this.wrapText(ctx, this.config.body, width/2, y, width - 180, 55);
        }
        this.drawFooter(ctx, width, height);
    }

    drawDynamic() {
        if(!this.ctxGen) return;
        const ctx = this.ctxGen;
        const width = 1080, height = 1080;
        const bg1 = document.getElementById('mkt-gen-bg1').value;
        const bg2 = document.getElementById('mkt-gen-bg2').value;

        this.drawBackground(ctx, width, height, bg1, bg2);

        if(this.activeMode === 'resultado') this.renderResultado(ctx, width, height);
        else if(this.activeMode === 'mvp') this.renderMVP(ctx, width, height);
        else if(this.activeMode === 'rol') this.renderRol(ctx, width, height);

        this.drawFooter(ctx, width, height);
    }

    renderResultado(ctx, w, h) {
        const local = document.getElementById('label-local').innerText || 'LOCAL';
        const visita = document.getElementById('label-visitante').innerText || 'VISITA';
        const gl = document.getElementById('mkt-glocal').value;
        const gv = document.getElementById('mkt-gvisit').value;
        const notes = document.getElementById('mkt-scorers').value;

        this.drawText(ctx, 'RESULTADO FINAL', w/2, 150, '900 60px "Inter"', '#fff', true);
        
        // Marcador Central
        ctx.fillStyle = 'rgba(255,255,255,0.05)';
        ctx.roundRect ? ctx.roundRect(w/2 - 120, 350, 240, 180, 20) : ctx.fillRect(w/2 - 120, 350, 240, 180);
        ctx.fill();
        this.drawText(ctx, `${gl} - ${gv}`, w/2, 480, '900 120px "Inter"', '#00ff88', true);

        // Nombres de equipos
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

        // Brillo de fondo para el jugador
        const radial = ctx.createRadialGradient(w/2, 450, 50, w/2, 450, 400);
        radial.addColorStop(0, 'rgba(139,92,246,0.2)');
        radial.addColorStop(1, 'transparent');
        ctx.fillStyle = radial;
        ctx.fillRect(0,0,w,h);

        if(this.config.dynamicImg) {
            this.drawCenteredImage(ctx, this.config.dynamicImg, w/2, 450, 500);
        }

        this.drawText(ctx, name, w/2, 780, '900 70px "Inter"', '#fff', true);
        this.drawText(ctx, team, w/2, 840, '700 30px "Inter"', '#8b5cf6');
        
        // Stats
        this.drawText(ctx, `GOLES: ${goals}`, w/2 - 150, 930, '800 40px "Inter"', '#fff');
        this.drawText(ctx, `RATING: ${rating}`, w/2 + 150, 930, '800 40px "Inter"', '#f59e0b');
    }

    renderRol(ctx, w, h) {
        const title = document.getElementById('mkt-rol-title').value || 'PRÓXIMA JORNADA';
        const footer = document.getElementById('mkt-rol-footer').value || '';

        this.drawText(ctx, title, w/2, 150, '900 60px "Inter"', '#fff', true);
        
        // Simular tabla básica
        ctx.fillStyle = 'rgba(255,255,255,0.1)';
        ctx.fillRect(100, 250, w - 200, 600);
        
        this.drawText(ctx, "DISPONIBLE EN MINI APP TELEGRAM", w/2, 550, '500 35px "Inter"', 'rgba(255,255,255,0.5)');
        
        if(footer) this.drawText(ctx, footer, w/2, 900, '700 40px "Inter"', '#10b981');
    }

    // --- UTILS DE DIBUJO ---

    drawBackground(ctx, w, h, c1, c2) {
        const grad = ctx.createLinearGradient(0, 0, w, h);
        grad.addColorStop(0, c1);
        grad.addColorStop(1, c2);
        ctx.fillStyle = grad;
        ctx.fillRect(0, 0, w, h);
        
        ctx.strokeStyle = 'rgba(255,255,255,0.02)';
        ctx.lineWidth = 1;
        for(let i=0; i<w; i+=50) {
            ctx.beginPath(); ctx.moveTo(i, 0); ctx.lineTo(i, h); ctx.stroke();
            ctx.beginPath(); ctx.moveTo(0, i); ctx.lineTo(w, i); ctx.stroke();
        }
        ctx.strokeStyle = 'rgba(255,255,255,0.1)';
        ctx.lineWidth = 4;
        ctx.strokeRect(60, 60, w - 120, h - 120);
    }

    drawCenteredImage(ctx, img, x, y, size) {
        ctx.shadowColor = "rgba(0,0,0,0.5)"; ctx.shadowBlur = 20;
        ctx.drawImage(img, x - size/2, y - size/2, size, size);
        ctx.shadowColor = "transparent"; ctx.shadowBlur = 0;
    }

    drawText(ctx, text, x, y, font, color, stroke = false) {
        if(!text) return;
        ctx.fillStyle = color;
        ctx.font = font;
        ctx.textAlign = 'center';
        if(stroke) {
            ctx.lineWidth = 2; ctx.strokeStyle = '#000';
            ctx.strokeText(text, x, y);
        }
        ctx.fillText(text, x, y);
    }

    wrapText(ctx, text, x, y, maxWidth, lineHeight) {
        const paragraphs = text.split('\n');
        paragraphs.forEach(p => {
            const words = p.split(' ');
            let line = '';
            for(let n = 0; n < words.length; n++) {
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
        ctx.fillStyle = 'rgba(255,255,255,0.3)';
        ctx.font = '700 24px "Inter"';
        ctx.textAlign = 'center';
        ctx.fillText('CREADO POR FUTADMIN.COM.MX', w/2, h - 85);
    }

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
