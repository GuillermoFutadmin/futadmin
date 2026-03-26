/**
 * Módulo de Utilidades y Clase Base
 */
export class Core {
    static async fetchAPI(url, options = {}) {
        try {
            const response = await fetch(url, options);
            if (!response.ok) {
                let errData = {};
                try {
                    errData = await response.json();
                } catch (e) {}
                const error = new Error(`HTTP error! status: ${response.status}`);
                error.data = errData;
                throw error;
            }
            return await response.json();
        } catch (error) {
            console.error(`Fetch error on ${url}:`, error);
            throw error;
        }
    }

    static closeModal(modalId = 'modal-container') {
        const modal = document.getElementById(modalId);
        if (modal) modal.classList.remove('active');
    }

    static openModal(modalId) {
        const modal = document.getElementById(modalId);
        if (modal) modal.classList.add('active');
    }

    static showNotification(message, type = 'success') {
        // Remove any existing notifications
        document.querySelectorAll('.toast-notification').forEach(n => n.remove());

        const toast = document.createElement('div');
        toast.className = 'toast-notification';
        const colors = { success: '#10b981', error: '#ef4444', warning: '#f59e0b', info: '#3b82f6' };
        const icons = { success: '✅', error: '❌', warning: '⚠️', info: 'ℹ️' };
        toast.innerHTML = `<span>${icons[type] || '🔔'}</span> ${message}`;
        toast.style.cssText = `
            position: fixed; bottom: 30px; right: 30px; z-index: 99999;
            background: ${colors[type] || colors.success};
            color: #fff; padding: 14px 22px; border-radius: 12px;
            font-weight: 600; font-size: 0.95rem;
            box-shadow: 0 8px 24px rgba(0,0,0,0.3);
            display: flex; align-items: center; gap: 10px;
            animation: slideInRight 0.3s ease;
            max-width: 380px;
        `;
        document.body.appendChild(toast);
        setTimeout(() => {
            toast.style.opacity = '0';
            toast.style.transition = 'opacity 0.4s';
            setTimeout(() => toast.remove(), 400);
        }, 3500);
    }

    static async handleGlobalFileUpload(event) {
        const file = event.target.files[0];
        const targetInputId = event.target.getAttribute('data-target');

        if (!file || !targetInputId) return;

        const formData = new FormData();
        formData.append('file', file);

        try {
            const response = await fetch('/api/upload', {
                method: 'POST',
                body: formData
            });
            const result = await response.json();

            if (result.url) {
                const targetInput = document.getElementById(targetInputId);
                if (targetInput) {
                    targetInput.value = result.url;
                    targetInput.dispatchEvent(new Event('input'));
                    alert('¡Foto subida con éxito!');
                }
            } else {
                alert('Error al subir la imagen: ' + (result.error || 'Desconocido'));
            }
        } catch (error) {
            console.error('Error en subida:', error);
            alert('Error de conexión al subir imagen.');
        } finally {
            event.target.value = '';
        }
    }

    static loadScript(url) {
        return new Promise((resolve, reject) => {
            if (document.querySelector(`script[src="${url}"]`)) {
                resolve();
                return;
            }
            const script = document.createElement('script');
            script.src = url;
            script.onload = resolve;
            script.onerror = reject;
            document.head.appendChild(script);
        });
    }
}
