export class PrivacyModule {
    constructor(ui) {
        this.ui = ui;
        this.activeTab = 'privacy_policy';
        this.contents = {
            privacy_policy: '',
            minors_photo_policy: '',
            terms_conditions: '',
            app_scope: ''
        };
        this.titles = {
            privacy_policy: 'Aviso de Privacidad',
            minors_photo_policy: 'Protección de Menores (Fotos)',
            terms_conditions: 'Términos y Condiciones',
            app_scope: 'Alcance Operativo (SÍ/NO hace)'
        };
    }

    async init() {
        await this.loadAllPolicies();
    }

    async loadAllPolicies() {
        try {
            const data = await Core.fetchAPI('/api/config');
            // La API devuelve un objeto {clave: valor} si no se pasa clave
            this.contents.privacy_policy = data.privacy_policy || '';
            this.contents.minors_photo_policy = data.minors_photo_policy || '';
            this.contents.terms_conditions = data.terms_conditions || '';
            this.contents.app_scope = data.app_scope || '';
            
            this.updateEditor();
        } catch (error) {
            console.error('Error loading policies:', error);
        }
    }

    updateEditor() {
        const editor = document.getElementById('privacy-content-editor');
        const title = document.getElementById('privacy-editor-title');
        if (editor) editor.value = this.contents[this.activeTab];
        if (title) title.innerText = `📝 Editando: ${this.titles[this.activeTab]}`;
    }

    switchPrivacyTab(tabKey) {
        // Guardar progreso actual en memoria local
        const editor = document.getElementById('privacy-content-editor');
        if (editor) this.contents[this.activeTab] = editor.value;

        this.activeTab = tabKey;

        // Actualizar UI de botones
        document.querySelectorAll('.privacy-tab-btn').forEach(btn => {
            btn.classList.remove('active');
            btn.style.background = 'transparent';
            btn.style.color = 'var(--text-muted)';
            btn.style.fontWeight = '600';
        });

        const activeBtn = document.querySelector(`[onclick*="${tabKey}"]`);
        if (activeBtn) {
            activeBtn.classList.add('active');
            activeBtn.style.background = 'var(--primary)';
            activeBtn.style.color = '#000';
            activeBtn.style.fontWeight = '700';
        }

        this.updateEditor();
    }

    fillDefaultTemplate() {
        const templates = {
            privacy_policy: `AVISO DE PRIVACIDAD INTEGRAL - PLATAFORMA FUTADMIN PRO
VERSIÓN: 2.0 - MARZO 2024

1. IDENTIDAD Y DOMICILIO DEL RESPONSABLE
El uso y protección de sus datos personales es una prioridad. El Administrador de la Liga en conjunto con FutAdmin Pro, en su carácter de encargado del tratamiento, se comprometen a salvaguardar la información recabada.

2. DATOS PERSONALES QUE SERÁN SOMETIDOS A TRATAMIENTO
Para el funcionamiento óptimo de la gestión deportiva, se recabarán los siguientes datos:
- Identificación: Nombre completo, fotografía digitalizada, edad, fecha de nacimiento y género.
- Contacto: Correo electrónico, número de teléfono celular (opcional) y domicilio de equipo.
- Deportivos: Posición de juego, historial de goles, tarjetas, minutos jugados y equipos previos.
- Financieros: Registros de aportaciones, abonos de arbitraje y cuotas de inscripción.

3. FINALIDADES PRIMARIAS DEL TRATAMIENTO
Los datos personales serán utilizados para:
- Registro y validación de identidad en la cédula arbitral digital.
- Generación de estadísticas de juego en tiempo real y tablas de goleadores.
- Control administrativo de estados de cuenta por equipo y jugador.
- Notificaciones vía Telegram sobre programación de partidos y cambios de horario.
- Creación de fichas digitales para prevenir la suplantación de identidad (cachirules).

4. FINALIDADES SECUNDARIAS
No utilizaremos su información para fines mercadotécnicos, publicitarios o de prospección comercial externa. FutAdmin NO vende, ni alquila, ni comercializa su base de datos con terceros ajenos a la operación de la liga.

5. TRANSFERENCIA DE DATOS
Sus datos pueden ser compartidos con:
- El Cuerpo Arbitral: Para validar la elegibilidad antes de cada encuentro.
- Delegados de Equipo: Únicamente nombres y fotos para revisión de alineaciones contrarias.
- Proveedores de Infraestructura (Cloud): Únicamente para fines de almacenamiento seguro.

6. SEGURIDAD DE LA INFORMACIÓN
Implementamos medidas de seguridad técnicas y administrativas, incluyendo protocolos HTTPS, cifrado de contraseñas y backups diarios en bases de datos relacionales seguras.

7. DERECHOS ARCO (Acceso, Rectificación, Cancelación y Oposición)
Usted tiene derecho a conocer qué datos tenemos y para qué los utilizamos. Para ejercer estos derechos, debe contactar primeramente al Dueño/Administrador de su liga local. En caso de no recibir respuesta, puede contactar al soporte técnico de FutAdmin.

8. USO DE COOKIES Y TECNOLOGÍAS DE RASTREO
Utilizamos cookies esenciales para mantener las sesiones de usuario activas y optimizar la navegación. No se utilizan para rastreo de actividad fuera de la plataforma.

9. MODIFICACIONES AL AVISO
Cualquier cambio a este aviso será notificado en la pantalla de inicio de sesión de la plataforma.

10. ACEPTACIÓN DE LOS TÉRMINOS
Al registrarse o permitir su registro en esta plataforma, usted acepta el tratamiento de sus datos conforme a los términos aquí descritos.`,

            minors_photo_policy: `POLÍTICA DE PROTECCIÓN DE DATOS E IMAGEN DE MENORES DE EDAD
PROTOCOLOS DE SEGURIDAD Y CONSENTIMIENTO

1. MARCO LEGAL Y PROTECCIÓN PRIORITARIA
En FutAdmin Pro reconocemos que la protección de datos de niñas, niños y adolescentes es de orden público y de interés social. Esta política se alinea con las mejores prácticas internacionales de protección al menor en entornos digitales deportivos.

2. OBLIGATORIEDAD DEL CONSENTIMIENTO PARENTAL
Es responsabilidad ESTRICTA Y EXCLUSIVA del Administrador de la Liga o el Delegado del Equipo asegurar que cuenta con el consentimiento expreso, por escrito y firmado, del padre, madre o tutor legal antes de capturar la imagen o datos de cualquier menor de 18 años.

3. REQUERIMIENTO TÉCNICO DE FECHA DE NACIMIENTO
Nuestra plataforma solicita obligatoriamente la fecha de nacimiento. Si el sistema detecta que el jugador es menor de edad:
- Se activará una alerta visual en el panel de administrador.
- Se recomienda al usuario que registre que cuenta con el documento físico de autorización.
- Los datos de contacto del menor (email/teléfono) deben ser preferentemente los del tutor.

4. FINALIDAD DE LA FOTOGRAFÍA EN MENORES
El uso de imágenes de menores se limita estrictamente a:
- Validación de identidad en la ficha arbitral previa al inicio del partido.
- Evitar que adultos jueguen en categorías inferiores, protegiendo la integridad física de los menores.
- Reportes estadísticos internos del desempeño deportivo del menor.

5. RESTRICCIONES DE EXPOSICIÓN
Las fotografías de menores en FutAdmin:
- No son públicas en internet para búsqueda abierta.
- Solo son visibles para administradores autenticados y árbitros durante el encuentro.
- No se permite el uso de estas imágenes para flyers publicitarios sin un permiso adicional específico.

6. DERECHO DE ELIMINACIÓN INMEDIATA
En cualquier momento, el padre o tutor legal puede solicitar la eliminación inmediata de la fotografía del menor del sistema. El administrador de la liga está obligado a procesar dicha solicitud en un plazo no mayor a 24 horas.

7. PROHIBICIONES ESTRICTAS
Queda prohibido subir imágenes de menores que:
- No estén en un contexto deportivo (uniforme o ropa adecuada).
- Atenten contra la dignidad, integridad o pudor del menor.
- Muestren localizaciones privadas o datos sensibles innecesarios.

8. RESPONSABILIDAD LEGAL
FutAdmin Pro provee la infraestructura de almacenamiento, pero no supervisa el origen del consentimiento. La responsabilidad legal, civil o penal derivada del uso no autorizado de imágenes de menores recae directamente sobre la persona física o moral que realizó la carga del archivo (Dueño de la Liga o Delegado).

9. DENUNCIAS
Si usted detecta un perfil de un menor sin autorización, favor de reportarlo inmediatamente a través de los canales oficiales de soporte para proceder a la baja temporal del perfil mientras se aclara el estatus legal.

10. COMPROMISO ÉTICO
Como plataforma, nos comprometemos a mantener sistemas de purga de datos una vez que los torneos finalizan y los perfiles quedan inactivos por un periodo prolongado, minimizando la huella digital de los menores deportistas.`,

            terms_conditions: `TÉRMINOS Y CONDICIONES DE USO DE LA PLATAFORMA FUTADMIN PRO
REGLAMENTO PARA ADMINISTRADORES, EQUIPOS Y JUGADORES

1. ACEPTACIÓN DE TÉRMINOS
Al acceder y utilizar FutAdmin Pro, usted acepta cumplir con estos términos en su totalidad. Si no está de acuerdo, le rogamos se abstenga de utilizar el servicio.

2. NATURALEZA DEL SERVICIO
FutAdmin Pro es una herramienta tecnológica SaaS (Software como Servicio) diseñada para automatizar la gestión de ligas deportivas. El servicio incluye gestión de estadísticas, calendarios, finanzas e inscripciones.

3. RESPONSABILIDAD DE LA INFORMACIÓN
- El Administrador de la Liga es el único responsable de la veracidad de los resultados, calendarios y montos económicos capturados.
- FutAdmin no audita ni valida que los resultados de los partidos sean reales; somos un medio de registro.
- Error Humano: FutAdmin no se hace responsable por errores de captura (dedazos) que afecten tablas de posiciones o saldos económicos.

4. GESTIÓN DE PAGOS Y FINANZAS
- La plataforma permite registrar "Abonos", "Inscripciones" y "Arbitrajes" con fines de control administrativo.
- FutAdmin NO es un procesador de pagos bancarios. El dinero físico se maneja externamente entre equipos y ligas.
- El sistema es un registro informativo; las disputas por deudas o cobros son responsabilidad exclusiva de las partes involucradas.

5. PROPIEDAD INTELECTUAL
Todo el software, código fuente, diseño de interfaces, logotipos y algoritmos son propiedad de FutAdmin Pro. Queda estrictamente prohibida su copia, ingeniería inversa o uso en proyectos derivados sin autorización escrita.

6. DISPONIBILIDAD DEL SERVICIO
Aunque nos esforzamos por un uptime del 99.9%, no garantizamos disponibilidad ininterrumpida. Eventos de fuerza mayor, ataques DDoS, fallos en servidores globales (Railway/Heroku/AWS) o actualizaciones de mantenimiento pueden pausar el servicio temporalmente sin previo aviso.

7. CONDUCTA DEL USUARIO
Queda prohibido:
- Subir contenido obsceno, violento o ilegal.
- Intentar vulnerar la seguridad de otros usuarios o de la plataforma.
- Usar cuentas de otros usuarios sin permiso.
- Automatizar la extracción de datos (scraping) sin API oficial.

8. LIMITACIÓN DE RESPONSABILIDAD
Bajo ninguna circunstancia FutAdmin Pro, sus desarrolladores o socios serán responsables por daños indirectos, incidentales o especiales, incluyendo pérdida de ingresos deportivos, reputación de liga o errores en premiaciones derivados del uso de la app.

9. DURACIÓN Y RESCISIÓN DEL SERVICIO
FutAdmin se reserva el derecho de suspender cuentas que violen estos términos, que realicen actividades fraudulentas o que presenten adeudos en sus planes de suscripción.

10. LEGISLACIÓN APLICABLE
Para cualquier controversia técnica o legal relacionada con el software, las partes se someten a la legislación vigente y a los tribunales competentes en la materia.`,

            app_scope: `ALCANCE OPERATIVO: COMPROMISOS, SÍES Y NOES DE LA APP
DOCUMENTO DE EXPECTATIVAS PARA EL USUARIO FINAL

1. OBJETIVO PRIMORDIAL
FutAdmin Pro nace para profesionalizar el fútbol amateur y amateur-pro, transformando hojas de papel y excels complejos en una experiencia digital fluida para jugadores y organizadores.

2. LO QUE FUTADMIN ✅ SÍ HACE (NUESTROS COMPROMISOS):
- Procesamiento Matemático: Cálculo automático instantáneo de puntos, diferencia de goles, promedios y criterios de desempate en tablas de posiciones.
- Orden Estructural: Organización de torneos por grupos, jornadas y fases eliminatorias (liguilla) con configuración dinámica.
- Identidad Digital: Emisión de códigos de barras o QRs en fichas digitales para un control de acceso riguroso a cancha.
- Transparencia Financiera: Historial claro de quién ha pagado su inscripción y quién debe arbitrajes, descargable en PDF.
- Notificaciones: Envío de alertas programadas para que el jugador sepa cuándo y contra quién juega sin tener que preguntar al delegado.

3. LO QUE FUTADMIN ❌ NO HACE (NUESTRAS LIMITACIONES):
- No es Seguridad Pública: No garantizamos ni somos responsables de la seguridad física de los asistentes, jugadores o árbitros en las sedes deportivas.
- No es una Entidad Bancaria: No custodiamos dinero de las ligas. Si el sistema dice que un equipo pagó y no es verdad, es un error de captura del administrador, no del software.
- No resuelve Disputas en Campo: Si un partido se suspende por violencia o falta de garantías, el sistema solo registra lo que el árbitro/administrador reporte. No somos un tribunal de apelaciones.
- No garantiza Wi-Fi/Datos: La app requiere conexión a internet. La falta de señal en una cancha específica no es falla del sistema.

4. EL ROL DEL ADMINISTRADOR (TÚ)
El software es un martillo; tú eres el carpintero. La calidad de la liga digital depende 100% de la constancia y honestidad con la que captures los resultados. Si el administrador no captura, la app no puede mostrar magia.

5. SOPORTE TÉCNICO
Nuestro alcance incluye soporte para fallos de carga, errores de lógica en tablas y dudas de uso. No incluye "soporte de campo" para problemas entre jugadores o reglamentos internos de cada liga.

6. EVOLUCIÓN CONSTANTE
FutAdmin es un proyecto vivo. Escuchamos activamente tus sugerencias para añadir nuevas funciones, pero nos reservamos la prioridad de desarrollo según la estabilidad general del sistema.

7. COMPROMISO DE CALIDAD
Nos comprometemos a que el diseño sea premium, rápido y que la información esté disponible 24/7 para que tus jugadores se sientan en una liga profesional.`
        };

        if (confirm(`¿Deseas autollenar esta sección con el borrador profesional para "${this.titles[this.activeTab]}"?\n\nAdvertencia: Se reemplazará el contenido actual del editor.`)) {
            const editor = document.getElementById('privacy-content-editor');
            if (editor) {
                editor.value = templates[this.activeTab];
                this.contents[this.activeTab] = templates[this.activeTab];
            }
        }
    }

    async savePrivacyPolicy() {
        const editor = document.getElementById('privacy-content-editor');
        if (editor) this.contents[this.activeTab] = editor.value;

        const btn = document.getElementById('btn-save-privacy');
        if (btn) {
            btn.disabled = true;
            btn.innerText = 'Guardando...';
        }

        try {
            const res = await Core.fetchAPI('/api/config', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    clave: this.activeTab,
                    valor: this.contents[this.activeTab]
                })
            });

            if (res.success) {
                Core.showNotification(`${this.titles[this.activeTab]} actualizado correctamente`);
            } else {
                alert('Error al guardar: ' + res.error);
            }
        } catch (error) {
            console.error('Error saving policy:', error);
            alert('Error técnico al guardar el contenido legal');
        } finally {
            if (btn) {
                btn.disabled = false;
                btn.innerText = '💾 Guardar Cambios';
            }
        }
    }
}
