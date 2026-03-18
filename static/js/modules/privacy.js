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
        if (!container) return;

        try {
            const data = await Core.fetchAPI('/api/config?clave=privacy_policy');
            const content = data.valor || '';
            
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
