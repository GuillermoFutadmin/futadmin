/**
 * Módulo de Gestión de Privacidad y Términos
 */
import { Core } from './core.js';

export class PrivacyModule {
    constructor(ui) {
        this.ui = ui;
    }

    async init() {
        await this.loadPrivacyPolicy();
    }

    async loadPrivacyPolicy() {
        const container = document.getElementById('privacy-editor-container');
        // El container original de HTML no tiene el ID 'privacy-editor-container' sino el textarea directo, pero esta validación estaba ahí.
        
        try {
            const data = await Core.fetchAPI('/api/config?clave=privacy_policy');
            let content = data.valor || '';
            
            if (!content) {
                content = `AVISO DE PRIVACIDAD Y TÉRMINOS LEGALES DE FUTADMIN

1. OBJETIVO DE LA APLICACIÓN
FutAdmin es estrictamente una herramienta de software como servicio (SaaS) diseñada para facilitar el control estadístico, calendario de juegos, gestión de árbitros y administración de ingresos de las ligas deportivas que contratan la plataforma.

2. MARCO LEGAL Y PROTECCIÓN DE DATOS
La información recopilada (nombres, fotografías, estadísticas) es almacenada con estrictos fines deportivos e informativos para cada organización privada. FutAdmin no comercializa, distribuye ni comparte información de jugadores a terceros.

3. POLÍTICA DE FOTOS DE MENORES DE EDAD
En caso de registrar a participantes menores de 18 años, el Entrenador o el Dueño de la Liga tienen la estricta obligación de recabar el consentimiento explícito de los padres o tutores legales antes de subir o capturar cualquier fotografía en la aplicación.

4. EXENCIÓN DE RESPONSABILIDAD TOTAL DE LAS LIGAS
Se declara expresamente que la gestión, validación de jugadores, cobros internos y manejo de la información capturada es RESPONSABILIDAD TOTAL del Administrador o Dueño de la Liga. Mentir en temas legales de un menor es delito y es completa responsabilidad del dueño de equipo o liga. FutAdmin NO dictamina el manejo de información por equipo, solo brinda la herramienta digital para la gestión del espíritu deportivo. Las decisiones disciplinarias y operativas recaen 100% sobre los organizadores contratantes.`;
            }

            document.getElementById('privacy-content-editor').value = content;
        } catch (error) {
            console.error('Error loading privacy policy:', error);
        }
    }

    async savePrivacyPolicy() {
        const content = document.getElementById('privacy-content-editor').value;
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
                    clave: 'privacy_policy',
                    valor: content
                })
            });

            if (res.success) {
                Core.showNotification('Aviso de Privacidad actualizado correctamente');
            } else {
                alert('Error al guardar: ' + res.error);
            }
        } catch (error) {
            console.error('Error saving privacy policy:', error);
            alert('Error técnico al guardar el aviso de privacidad');
        } finally {
            if (btn) {
                btn.disabled = false;
                btn.innerText = '💾 Guardar Cambios';
            }
        }
    }
}
