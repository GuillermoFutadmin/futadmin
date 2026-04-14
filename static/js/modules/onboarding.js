export class OnboardingModule {
    constructor() {
        // Asegurarnos de que driver.js cargó
        if (window.driver) {
            this.driver = window.driver.js.driver;
        }
    }

    async init() {
        // Pequeño retardo para asegurar que la UI principal (dashboard) esté visible
        // No corremos el tour en login o páginas donde no exista el sidebar
        if (!document.querySelector('.sidebar')) return;

        // Validamos si es Admin, Ejecutivo o Dueño de liga
        const allowedRoles = ['admin', 'ejecutivo', 'dueño_liga'];
        if (!allowedRoles.includes(window.USER_ROL)) return;

        // Comprobamos la bandera en localStorage
        const tourCompletado = localStorage.getItem('futadmin_tour_completado');
        if (!tourCompletado) {
            setTimeout(() => {
                this.startTour();
            }, 1000);
        }
    }

    startTour() {
        if (!this.driver) return;

        // Función auxiliar para expandir menús si están cerrados
        const expandMenu = (selector) => {
            const el = document.querySelector(selector);
            if (el && !el.classList.contains('open')) {
                el.classList.add('open');
                const ul = el.querySelector('ul');
                if (ul) ul.style.display = 'block';
            }
        };

        const driverObj = this.driver({
            showProgress: true,
            allowClose: false, // Forzar que no cierren dando click fuera
            nextBtnText: 'Siguiente 👉',
            prevBtnText: '👈 Atrás',
            doneBtnText: '¡Entendido! 🚀',
            steps: [
                {
                    popover: {
                        title: '¡Bienvenido a FutAdmin Pro! 🏆',
                        description: 'Te hemos preparado un tour rápido de 5 pasos para que sepas por dónde empezar a configurar tu liga.',
                        align: 'center'
                    }
                },
                {
                    element: 'li.has-submenu', // El menú de Gestión de Ligas
                    popover: {
                        title: 'Paso 1: El Menú Principal',
                        description: 'Aquí encontrarás todo. Haz clic para desplegar las opciones de configuración.',
                        side: "right", align: 'start'
                    },
                    onHighlightStarted: () => {
                        // Expandir automáticamente
                        expandMenu('li.has-submenu');
                    }
                },
                {
                    element: `span[onclick*="ui.switchView('canchas'"]`,
                    popover: {
                        title: 'Paso 2: Registra tus Sedes',
                        description: 'Lo primero es agregar físicamente las sedes o canchas donde se jugarán los partidos de tu liga.',
                        side: "right", align: 'start'
                    }
                },
                {
                    element: `li[onclick*="ui.switchView('torneos', 'torneos-lista'"]`,
                    popover: {
                        title: 'Paso 3: Crea el Torneo',
                        description: 'Una vez tengas la sede, entra aquí para configurar las reglas, costos y nombre de tu torneo (Liguilla, Eliminatoria, etc).',
                        side: "right", align: 'start'
                    }
                },
                {
                    element: `li[onclick*="ui.switchView('torneos', 'equipos'"]`,
                    popover: {
                        title: 'Paso 4: Equipos y Jugadores',
                        description: '¡Ahora ingresa los equipos! Puedes hacerlo manual o importando un Excel para ser más rápido.',
                        side: "right", align: 'start'
                    }
                },
                {
                    element: 'a[href="/calendario"]',
                    popover: {
                        title: 'Paso 5: El Calendario',
                        description: 'Finalmente, ve a Calendario para generar las jornadas de forma automática y registrar los resultados.',
                        side: "right", align: 'start'
                    }
                },
                {
                    popover: {
                        title: '¡Todo listo! ⚽',
                        description: 'Puedes repetir este tour en cualquier momento desde el botón de ayuda (?). ¡A administrar tu liga!',
                        align: 'center'
                    }
                }
            ],
            onDestroyed: () => {
                // Marcar como completado
                localStorage.setItem('futadmin_tour_completado', 'true');
            }
        });

        driverObj.drive();
    }
}
