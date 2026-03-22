export class MarketingModule {
    constructor(ui) {
        this.ui = ui;
        this.canvasId = 'marketing-canvas';
        this.ctx = null;
        
        // Configuraciones base para Avisos Oficiales
        this.config = {
            width: 1080,
            height: 1080,
            bgColor1: '#0f172a',
            bgColor2: '#020617',
            title: 'AVISO IMPORTANTE',
            subtitle: 'COMUNICADO OFICIAL',
            body: 'Escribe aquí tu mensaje detallado para la comunidad, equipos o jugadores de la liga.',
            logoUrl: '',
            logoImg: null
        };
    }

    initAvisosEditor() {
        document.getElementById('marketing-grid').style.display = 'none';
        document.getElementById('marketing-editor-logos').style.display = 'none';
        document.getElementById('marketing-editor-avisos').style.display = 'flex';
        
        const canvas = document.getElementById(this.canvasId);
        if(canvas) {
            canvas.width = this.config.width;
            canvas.height = this.config.height;
            this.ctx = canvas.getContext('2d');
            this.bindEvents();
            this.updateConfigFromForm(); // Inicializar con valores en los forms
            this.draw();
        }
    }

    closeEditor() {
        document.getElementById('marketing-editor-avisos').style.display = 'none';
        document.getElementById('marketing-editor-logos').style.display = 'none';
        document.getElementById('marketing-grid').style.display = 'grid';
    }

    initLogosGallery() {
        document.getElementById('marketing-grid').style.display = 'none';
        document.getElementById('marketing-editor-avisos').style.display = 'none';
        document.getElementById('marketing-editor-logos').style.display = 'flex';
    }

    closeLogosGallery() {
        this.closeEditor();
    }

    bindEvents() {
        const attachList = ['mkt-title', 'mkt-subtitle', 'mkt-body', 'mkt-bg1', 'mkt-bg2'];
        attachList.forEach(id => {
            const el = document.getElementById(id);
            if(el) {
                // 'input' para que se actualice mientras el usuario teclea o arrastra la rueda de color
                el.addEventListener('input', () => this.updateConfigFromForm());
            }
        });

        const logoInput = document.getElementById('mkt-logo');
        if (logoInput) {
            // Un 'change' capta la modificación tras subir foto por global-file-upload
            logoInput.addEventListener('change', () => {
                const url = logoInput.value;
                if(url) {
                    const img = new Image();
                    img.crossOrigin = "Anonymous"; // Prevenir error de canvas manchado (Tainted canvas) CORS
                    img.onload = () => {
                        this.config.logoImg = img;
                        this.draw();
                    };
                    img.onerror = () => {
                        console.error("Error cargando logo en Canvas: CORS o URL fallida.");
                        this.config.logoImg = null;
                        this.draw();
                    };
                    img.src = url;
                } else {
                    this.config.logoImg = null;
                    this.draw();
                }
            });
            // Si ya hay un valor de arranque
            logoInput.dispatchEvent(new Event('change'));
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

    draw() {
        if(!this.ctx) return;
        const ctx = this.ctx;
        const { width, height } = this.config;
        
        // 1. DIBUJAR FONDO DEGRADADO
        const grad = ctx.createLinearGradient(0, 0, width, height); // Diagonal
        grad.addColorStop(0, this.config.bgColor1);
        grad.addColorStop(1, this.config.bgColor2);
        ctx.fillStyle = grad;
        ctx.fillRect(0, 0, width, height);

        // Textura fina en el fondo (Opcional, Da look Pro/Gamer)
        ctx.strokeStyle = 'rgba(255,255,255,0.02)';
        ctx.lineWidth = 1;
        for(let i=0; i<width; i+=50) {
            ctx.beginPath(); ctx.moveTo(i, 0); ctx.lineTo(i, height); ctx.stroke();
            ctx.beginPath(); ctx.moveTo(0, i); ctx.lineTo(width, i); ctx.stroke();
        }

        // Borde exterior / Safe zone
        ctx.strokeStyle = 'rgba(255,255,255,0.1)';
        ctx.lineWidth = 4;
        ctx.strokeRect(60, 60, width - 120, height - 120);

        // 2. ESCUDO / LOGOTIPO
        let yOffset = 180;
        if(this.config.logoImg) {
            const imgSize = 240;
            const ix = (width/2) - (imgSize/2);
            const iy = yOffset;
            try {
                // Sombra suave en logo
                ctx.shadowColor = "rgba(0,0,0,0.5)";
                ctx.shadowBlur = 20;
                ctx.shadowOffsetX = 0;
                ctx.shadowOffsetY = 10;
                ctx.drawImage(this.config.logoImg, ix, iy, imgSize, imgSize);
                // Reset sombra
                ctx.shadowColor = "transparent";
                ctx.shadowBlur = 0;
                ctx.shadowOffsetX = 0;
                ctx.shadowOffsetY = 0;
                
                yOffset += imgSize + 60;
            } catch(e) { console.error(e); yOffset += 50; }
        } else {
            yOffset += 120; // Espaciado extra si no hay foto
        }

        // 3. TEXTOS
        // Subtítulo
        if(this.config.subtitle) {
            ctx.fillStyle = '#f59e0b'; // Color oro o secundario
            ctx.font = '700 32px "Inter", Arial, sans-serif';
            ctx.textAlign = 'center';
            ctx.fillText(this.config.subtitle, width/2, yOffset);
            yOffset += 60;
        }

        // Título Principal
        if(this.config.title) {
            ctx.fillStyle = '#ffffff';
            ctx.font = '900 80px "Inter", Arial, sans-serif';
            // Trazo fino para resaltar 
            ctx.lineWidth = 2;
            ctx.strokeStyle = '#000000';
            ctx.strokeText(this.config.title, width/2, yOffset);
            ctx.fillText(this.config.title, width/2, yOffset);
            yOffset += 80;
            
            // Línea divisoria abajo del titulo
            ctx.fillStyle = '#f59e0b';
            ctx.fillRect((width/2) - 80, yOffset - 30, 160, 6);
            yOffset += 40;
        }

        // Cuerpo / Mensaje. Lógica de Párrafos Multi-línea (Word Wrap)
        if(this.config.body) {
            ctx.fillStyle = 'rgba(255,255,255,0.9)';
            ctx.font = '400 42px "Inter", Arial, sans-serif';
            ctx.textAlign = 'center'; // Queda centrado siempre el aviso
            
            const maxWidth = width - 180;
            const lineHeight = 55;
            const paragraphs = this.config.body.split('\n');
            
            paragraphs.forEach(p => {
                const words = p.split(' ');
                let line = '';
                for(let n = 0; n < words.length; n++) {
                    let testLine = line + words[n] + ' ';
                    let metrics = ctx.measureText(testLine);
                    let testWidth = metrics.width;
                    if (testWidth > maxWidth && n > 0) {
                        ctx.fillText(line, width/2, yOffset);
                        line = words[n] + ' ';
                        yOffset += lineHeight;
                    } else {
                        line = testLine;
                    }
                }
                ctx.fillText(line, width/2, yOffset);
                yOffset += lineHeight;
            });
        }

        // Footer Brand (Marca de agua o pie de imagen)
        ctx.fillStyle = 'rgba(255,255,255,0.3)';
        ctx.font = '700 24px "Inter", Arial, sans-serif';
        ctx.fillText('CREADO POR FUTADMIN.COM.MX', width/2, height - 85);
    }

    downloadImage() {
        const canvas = document.getElementById(this.canvasId);
        if(!canvas) return;
        
        try {
            const url = canvas.toDataURL('image/png', 1.0);
            const link = document.createElement('a'); // Elemento 'A' para descargas
            link.download = `FutAdmin_Aviso_${Date.now()}.png`;
            link.href = url;
            link.click();
            link.remove();
        } catch(e) {
            alert('Aviso de Seguridad del Navegador: ¡Foto bloqueada por CORS CORS Tainted Canvas! Asegúrate de subir escudos propios válidos.');
        }
    }
}
