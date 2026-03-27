import { Core } from './core.js';

/**
 * Módulo de Perfil y Gestión de Cuentas (Combos)
 */
export const Perfil = {
    init() {
        console.log("Perfil module initialized");
    },

    async openModal() {
        // Bloqueo para cuentas genéricas/públicas
        const userRol = (window.USER_ROL || '').toLowerCase().replace('ñ', 'n');
        if (['resultados', 'espectador', 'visor'].includes(userRol)) {
            console.warn("Acceso a perfil restringido para esta cuenta pública.");
            return;
        }
        Core.openModal('modal-perfil');
        this.renderComboManagement();
    },

    async changeSelfPassword() {
        const newPass = document.getElementById('perf-new-pass').value;
        const confirmPass = document.getElementById('perf-confirm-pass').value;

        if (!newPass || newPass.length < 6) {
            alert("La contraseña debe tener al menos 6 caracteres.");
            return;
        }

        if (newPass !== confirmPass) {
            alert("Las contraseñas no coinciden.");
            return;
        }

        try {
            const res = await fetch('/api/user/self/change_password', {
                method: 'POST',
                headers: { 
                    'Content-Type': 'application/json',
                    'X-CSRFToken': Core.getCsrfToken()
             },
                body: JSON.stringify({ new_password: newPass })
            });
            const data = await res.json();
            if (data.success) {
                alert("¡Contraseña actualizada con éxito!");
                document.getElementById('perf-new-pass').value = '';
                document.getElementById('perf-confirm-pass').value = '';
            } else {
                alert("Error: " + data.error);
            }
        } catch (e) {
            console.error(e);
            alert("Error de conexión.");
        }
    },

    async renderComboManagement() {
        const container = document.getElementById('combo-accounts-container');
        if (!container) return;

        // Solo mostrar si es dueño, ejecutivo o super_arbitro (roles de gestión)
        const canManage = ['dueño_liga', 'super_arbitro', 'equipo'].includes(window.USER_ROL);
        if (!canManage) {
            container.style.display = 'none';
            return;
        }

        container.innerHTML = '<p style="text-align:center; opacity:0.6;">Cargando colaboradores...</p>';
        
        try {
            const res = await fetch('/api/user/combo/collaborators');
            const collabs = await res.json();
            
            if (!collabs || collabs.length === 0) {
                container.innerHTML = '<p style="text-align:center; opacity:0.6; font-size:0.8rem;">No se encontraron cuentas adicionales en tu paquete.</p>';
                return;
            }

            container.innerHTML = `
                <h4 style="margin: 20px 0 10px 0; color: var(--primary); font-size: 0.9rem; border-top: 1px solid rgba(255,255,255,0.05); padding-top: 15px;">
                    Gestionar Colaboradores (Paquete Combo)
                </h4>
                <div class="combo-list" style="display: flex; flex-direction: column; gap: 10px;">
                    ${collabs.map(c => `
                        <div class="card" style="padding: 12px; display: flex; justify-content: space-between; align-items: center; background: rgba(255,255,255,0.02);">
                            <div>
                                <div style="font-weight: 600; font-size: 0.85rem;">${c.nombre}</div>
                                <div style="font-size: 0.75rem; opacity: 0.6;">${c.email}</div>
                                <div style="font-size: 0.7rem; color: var(--secondary); font-weight: 700; text-transform: uppercase;">${c.rol}</div>
                            </div>
                            <button class="btn-ghost" onclick="ui.perfil.promptCollaboratorPassword(${c.id}, '${c.nombre}')" style="font-size: 0.7rem; padding: 5px 10px; border: 1px solid rgba(255,255,255,0.1);">
                                🔑 CAMBIAR PASS
                            </button>
                        </div>
                    `).join('')}
                </div>
            `;
        } catch (e) {
            container.innerHTML = '<p style="color: var(--error);">Error al cargar colaboradores.</p>';
        }
    },

    async promptCollaboratorPassword(id, nombre) {
        const newPass = prompt(`Ingresa la nueva contraseña para ${nombre}:`);
        if (!newPass) return;
        if (newPass.length < 6) {
            alert("La contraseña debe tener al menos 6 caracteres.");
            return;
        }

        try {
            const res = await fetch(`/api/user/collaborator/${id}/password`, {
                method: 'PUT',
                headers: { 
                    'Content-Type': 'application/json',
                    'X-CSRFToken': Core.getCsrfToken()
                },
                body: JSON.stringify({ password: newPass })
            });
            const data = await res.json();
            if (data.success) {
                alert(`¡Contraseña de ${nombre} actualizada!`);
            } else {
                alert("Error: " + data.error);
            }
        } catch (e) {
            alert("Error de conexión.");
        }
    }
};
