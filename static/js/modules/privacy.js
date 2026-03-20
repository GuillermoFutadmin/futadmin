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
            privacy_policy: `AVISO DE PRIVACIDAD INTEGRAL - FUTADMIN

1. RESPONSABLE: La gestión de datos es responsabilidad compartida entre el Administrador de la Liga y FutAdmin (encargado).
2. FINALIDAD: Uso para estadísticas, calendarios, resultados y control de pagos e inscripciones.
3. DATOS: Se recaban nombres, correos, edades y fotografías deportivas.
4. PROTECCIÓN: FutAdmin NO vende ni comercializa bases de datos. La información es exclusiva de la organización.
5. DERECHOS ARCO: Acceso y rectificación directamente con el administrador de su liga.`,

            minors_photo_policy: `POLÍTICA DE PROTECCIÓN DE IMAGEN DE MENORES

1. CONSENTIMIENTO: Es OBLIGACIÓN del Delegado o Dueño de Liga recabar consentimiento escrito de padres/tutores antes de subir fotos de menores de 18 años.
2. USO: Exclusivamente para validación de identidad en campo (fichas) y registros históricos de torneos.
3. RESPONSABILIDAD: El uso inapropiado o distribución externa es responsabilidad penal directa de quien cargó el archivo.
4. EXENSIÓN: FutAdmin es la herramienta tecnológica; el Dueño de la Liga es el garante legal ante las autoridades.`,

            terms_conditions: `TÉRMINOS Y CONDICIONES DE USO

1. SERVICIO: FutAdmin es un software de administración deportiva (SaaS).
2. VERACIDAD: El usuario es responsable de la exactitud de marcadores y estados financieros capturados.
3. PAGOS: Los montos reportados son de control interno. Disputas monetarias se resuelven externamente entre liga y equipo.
4. DISPONIBILIDAD: No se garantiza continuidad absoluta ante fallos de infraestructura global o ataques externos.
5. PROPIEDAD: El código y marca FutAdmin son propiedad exclusiva. Prohibida su reproducción.`,

            app_scope: `ALCANCE OPERATIVO: COMPROMISOS Y LIMITACIONES

✅ LO QUE FUTADMIN SÍ HACE:
- Automatiza cálculos de tablas, calendarios y liguillas.
- Genera reportes financieros detallados de ingresos por equipo.
- Digitaliza fichas de jugadores para evitar suplantaciones de identidad.
- Permite captura de resultados en tiempo real vía Telegram.

❌ LO QUE FUTADMIN NO HACE:
- NO garantiza seguridad física en canchas ni resuelve disputas de campo.
- NO actúa como banco; los pagos son informativos para control administrativo.
- NO dictamina sanciones disciplinarias; eso es 100% responsabilidad del organizador local.`
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
