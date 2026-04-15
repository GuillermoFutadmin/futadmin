export class OnboardingModule {
    constructor() {
        if (window.driver) {
            this.driver = window.driver.js.driver;
        }
    }

    async init() {
        if (!document.querySelector('.sidebar')) return;
        const allowedRoles = ['admin', 'ejecutivo', 'dueño_liga'];
        if (!allowedRoles.includes(window.USER_ROL)) return;

        const tourCompletado = localStorage.getItem('futadmin_tour_v2_completado');
        if (!tourCompletado) {
            setTimeout(() => this.startTour(), 1200);
        }
    }

    _expandMenus() {
        document.querySelectorAll('li.has-submenu').forEach(el => {
            if (!el.classList.contains('open')) {
                el.classList.add('open');
                const ul = el.querySelector('ul');
                if (ul) ul.style.display = 'block';
            }
        });
    }

    startTour() {
        if (!this.driver) {
            console.warn('[FutAdmin] Driver.js no está cargado, no se puede iniciar el tour.');
            return;
        }

        this._expandMenus();

        const driverObj = this.driver({
            showProgress: true,
            animate: true,
            smoothScroll: true,
            allowClose: true,
            overlayOpacity: 0.75,
            stagePadding: 8,
            stageRadius: 8,
            popoverClass: 'futadmin-tour-popover',
            nextBtnText: 'Siguiente →',
            prevBtnText: '← Atrás',
            doneBtnText: '¡Empezar ahora! 🚀',
            steps: [
                // 0 - Bienvenida
                {
                    popover: {
                        title: '🏆 ¡Bienvenido a FutAdmin Pro!',
                        description: `
                            <div style="text-align:center; padding: 4px 0;">
                                <div style="font-size:2.5rem; margin-bottom:12px;">⚽</div>
                                <p style="margin:0 0 10px; line-height:1.6;">
                                    Tu plataforma profesional para administrar ligas de fútbol.<br>
                                    <strong>Te guiaremos en 10 pasos clave</strong> para que en minutos tengas tu liga lista.
                                </p>
                                <div style="display:flex; justify-content:center; gap:20px; margin-top:12px; flex-wrap:wrap;">
                                    <span style="background:rgba(0,255,136,0.1); border: 1px solid rgba(0,255,136,0.3); padding:4px 10px; border-radius:20px; font-size:0.75rem;">🏟️ Sedes</span>
                                    <span style="background:rgba(0,255,136,0.1); border: 1px solid rgba(0,255,136,0.3); padding:4px 10px; border-radius:20px; font-size:0.75rem;">🏆 Torneos</span>
                                    <span style="background:rgba(0,255,136,0.1); border: 1px solid rgba(0,255,136,0.3); padding:4px 10px; border-radius:20px; font-size:0.75rem;">📋 Resultados</span>
                                    <span style="background:rgba(0,255,136,0.1); border: 1px solid rgba(0,255,136,0.3); padding:4px 10px; border-radius:20px; font-size:0.75rem;">💰 Finanzas</span>
                                </div>
                            </div>`,
                        align: 'center'
                    }
                },
                // 1 - Dashboard / Estadísticas
                {
                    element: '#view-resumen',
                    popover: {
                        title: '📊 Panel de Estadísticas',
                        description: `
                            <p>Esta es tu <strong>pantalla de inicio</strong>. De un vistazo verás:</p>
                            <ul style="margin:8px 0; padding-left:18px; line-height:1.8;">
                                <li>⚽ Ligas activas y equipos registrados</li>
                                <li>📅 Partidos jugados esta semana</li>
                                <li>💰 Estado de inscripciones y pagos</li>
                                <li>🗺️ Mapa de cobertura nacional</li>
                            </ul>
                            <p style="color:#00ff88; font-size:0.8rem; margin:0;">💡 Selecciona una liga en el filtro superior para ver su detalle.</p>`,
                        side: 'bottom', align: 'start'
                    }
                },
                // 2 - Sedes y Canchas
                {
                    element: `li[onclick*="switchView('canchas'"]`,
                    popover: {
                        title: '🏟️ Paso 1: Registra tus Sedes',
                        description: `
                            <p><strong>Lo primero siempre es registrar dónde se juega.</strong></p>
                            <ul style="margin:8px 0; padding-left:18px; line-height:1.8;">
                                <li>📍 Dale nombre y ubicación a la sede</li>
                                <li>🥅 Agrega las canchas individuales de esa sede</li>
                                <li>🔢 Define cuántos campos simultáneos hay</li>
                            </ul>
                            <p style="color:#fbbf24; font-size:0.8rem; margin:0;">⚠️ Sin una sede registrada, no podrás crear jornadas.</p>`,
                        side: 'right', align: 'start'
                    }
                },
                // 3 - Crear Torneo / Liga
                {
                    element: `li[onclick*="switchView('torneos'"]`,
                    popover: {
                        title: '🏆 Paso 2: Crea tu Torneo / Liga',
                        description: `
                            <p>Configura las reglas de tu torneo:</p>
                            <ul style="margin:8px 0; padding-left:18px; line-height:1.8;">
                                <li>📝 Nombre, categoría y formato (Liga / Liguilla / Copa)</li>
                                <li>📅 Fechas de inicio y fin</li>
                                <li>💵 Costo de inscripción y arbitraje por partido</li>
                                <li>🏅 Premios y reglamento interno</li>
                            </ul>
                            <p style="color:#00ff88; font-size:0.8rem; margin:0;">💡 Puedes tener varios torneos activos al mismo tiempo.</p>`,
                        side: 'right', align: 'start'
                    }
                },
                // 4 - Equipos
                {
                    element: `li[onclick*="switchView('torneos', 'equipos'"]`,
                    popover: {
                        title: '👕 Paso 3: Equipos y Jugadores',
                        description: `
                            <p>Agrega los equipos a tu torneo:</p>
                            <ul style="margin:8px 0; padding-left:18px; line-height:1.8;">
                                <li>📦 <strong>Carga masiva</strong> — importa múltiples equipos con Excel</li>
                                <li>✏️ Agrega equipos uno a uno con nombre y color</li>
                                <li>👤 Registra jugadores individualmente por equipo</li>
                                <li>📷 Sube foto de los jugadores (Portal Web)</li>
                            </ul>
                            <p style="color:#00ff88; font-size:0.8rem; margin:0;">💡 También puedes agregar jugadores desde la app Telegram del árbitro.</p>`,
                        side: 'right', align: 'start'
                    }
                },
                // 5 - Calendario y Jornadas
                {
                    element: 'a[href="/calendario"]',
                    popover: {
                        title: '📅 Paso 4: Calendario y Jornadas',
                        description: `
                            <p>El corazón de tu liga. Desde aquí:</p>
                            <ul style="margin:8px 0; padding-left:18px; line-height:1.8;">
                                <li>🤖 <strong>Genera jornadas automáticamente</strong> con Round Robin</li>
                                <li>⚽ Registra resultados y goles partido por partido</li>
                                <li>🔴 Reporta tarjetas y sanciones</li>
                                <li>📲 Los árbitros pueden registrar desde su celular</li>
                            </ul>
                            <p style="color:#00ff88; font-size:0.8rem; margin:0;">💡 Haz clic en cualquier partido para ver su detalle o editarlo.</p>`,
                        side: 'right', align: 'start'
                    }
                },
                // 6 - Resultados y Tabla de Posiciones
                {
                    element: '#leagues-container',
                    popover: {
                        title: '📊 Paso 5: Ver Resultados y Tabla',
                        description: `
                            <p>En la sección <strong>Gestión de Ligas</strong>, cada tarjeta de torneo tiene botones para:</p>
                            <ul style="margin:8px 0; padding-left:18px; line-height:1.8;">
                                <li>🏅 <strong>Ver Tabla de Posiciones</strong> — clasificación en tiempo real</li>
                                <li>📈 Estadísticas de goleadores y tarjetas por jugador</li>
                                <li>📋 Historial completo de partidos jugados</li>
                                <li>🔗 Comparte el link público de tu liga con los equipos</li>
                            </ul>
                            <p style="color:#00ff88; font-size:0.8rem; margin:0;">💡 La tabla se actualiza en automático al guardar cada resultado.</p>`,
                        side: 'top', align: 'start'
                    }
                },
                // 7 - Inscripciones
                {
                    element: `li[onclick*="switchView('inscripciones'"]`,
                    popover: {
                        title: '💰 Paso 6: Control de Inscripciones',
                        description: `
                            <p>Lleva el control de pagos de cada equipo:</p>
                            <ul style="margin:8px 0; padding-left:18px; line-height:1.8;">
                                <li>💵 Ve quién ha pagado y quién debe</li>
                                <li>🧾 Genera comprobantes digitales (tickets)</li>
                                <li>📩 Envía recibos por correo automáticamente</li>
                                <li>🎓 Marca equipos como "Becados" si aplica</li>
                            </ul>
                            <p style="color:#fbbf24; font-size:0.8rem; margin:0;">⚠️ Filtra por liga para ver el estado de cada equipo.</p>`,
                        side: 'right', align: 'start'
                    }
                },
                // 8 - Arbitrajes
                {
                    element: `li[onclick*="switchView('arbitrajes'"]`,
                    popover: {
                        title: '⚖️ Paso 7: Control de Arbitrajes',
                        description: `
                            <p>Gestiona los pagos de arbitraje por jornada:</p>
                            <ul style="margin:8px 0; padding-left:18px; line-height:1.8;">
                                <li>📊 Ve el desglose de lo que debe cada equipo por partido</li>
                                <li>✅ Marca pagos de jornada completados</li>
                                <li>🔔 Identifica rápido quién tiene saldo pendiente</li>
                            </ul>
                            <p style="color:#00ff88; font-size:0.8rem; margin:0;">💡 El monto se calcula automáticamente según la tarifa configurada en el torneo.</p>`,
                        side: 'right', align: 'start'
                    }
                },
                // 9 - Árbitros
                {
                    element: `li[onclick*="switchView('arbitros'"]`,
                    popover: {
                        title: '🙋 Paso 8: Cuerpo Arbitral',
                        description: `
                            <p>Administra a tus árbitros:</p>
                            <ul style="margin:8px 0; padding-left:18px; line-height:1.8;">
                                <li>➕ Registra árbitros y asócialos a tu liga</li>
                                <li>📲 Comparte su acceso para que registren partidos desde el celular</li>
                                <li>📊 Ve su historial de partidos arbitrados</li>
                            </ul>
                            <p style="color:#00ff88; font-size:0.8rem; margin:0;">💡 Los árbitros tienen un portal móvil dedicado para registrar resultados en campo.</p>`,
                        side: 'right', align: 'start'
                    }
                },
                // 10 - Estudio Creativo
                {
                    element: `li[onclick*="switchView('marketing'"]`,
                    popover: {
                        title: '🎨 Paso 9: Estudio Creativo',
                        description: `
                            <p>Genera gráficos pro para tus redes sociales:</p>
                            <ul style="margin:8px 0; padding-left:18px; line-height:1.8;">
                                <li>📸 Tarjetas de partido con datos automáticos</li>
                                <li>👤 Tarjeta de jugador con foto y estadísticas</li>
                                <li>🏆 Gráfico de tabla de posiciones para Instagram</li>
                                <li>🖼️ Descarga en HD con el logo de tu liga</li>
                            </ul>
                            <p style="color:#00ff88; font-size:0.8rem; margin:0;">💡 ¡Solo selecciona el partido y los datos se llenan solos!</p>`,
                        side: 'right', align: 'start'
                    }
                },
                // 11 - Cierre
                {
                    popover: {
                        title: '✅ ¡Ya sabes todo!',
                        description: `
                            <div style="text-align:center; padding: 4px 0;">
                                <div style="font-size:2rem; margin-bottom:10px;">🎉</div>
                                <p style="margin:0 0 12px; line-height:1.6;">
                                    Ahora tienes lo necesario para administrar tu liga profesionalmente.
                                </p>
                                <div style="background:rgba(0,255,136,0.08); border:1px solid rgba(0,255,136,0.2); border-radius:10px; padding:12px; font-size:0.82rem; text-align:left;">
                                    <strong style="color:#00ff88;">🛟 Botón de Ayuda</strong><br>
                                    <span style="color:#ccc;">Puedes repetir este tour en cualquier momento pulsando <strong>AYUDA</strong> en la barra superior.</span>
                                </div>
                                <p style="color:#aaa; font-size:0.75rem; margin-top:10px;">FutAdmin Pro — Administración deportiva de alto nivel.</p>
                            </div>`,
                        align: 'center'
                    }
                }
            ],
            onDestroyed: () => {
                localStorage.setItem('futadmin_tour_v2_completado', 'true');
            }
        });

        driverObj.drive();
    }
}
