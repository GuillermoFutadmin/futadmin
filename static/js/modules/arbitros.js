import { Core } from './core.js';

export class ArbitrosModule {
    constructor(ui) {
        this.ui = ui;
        this.ligas = [];
        this.arbitros = []; // Caché local para evitar fetch redundantes
        this.pagination = null;
    }

    async changePage(page) {
        await this.loadArbitros(page);
        window.scrollTo({ top: 0, behavior: 'smooth' });
    }

    async loadArbitros(page = 1) {
        const container = document.getElementById('arbitros-container');
        if (!container) return;
        
        if (this.arbitros.length === 0) {
            container.innerHTML = '<p>Cargando cuerpo arbitral...</p>';
        }

        if (this.ligas.length === 0) {
            try {
                this.ligas = await Core.fetchAPI('/api/ligas');
            } catch (e) { console.error("Error cargando ligas en arbitros:", e); }
        }

        try {
            const response = await fetch(`/api/arbitros?page=${page}`);
            if (!response.ok) {
                this.arbitros = [];
                this.renderPlaceholder(container);
                return;
            }
            const data = await response.json();
            this.arbitros = data.items;
            this.pagination = data.pagination;
            this.renderArbitros(this.arbitros, this.pagination);
        } catch (error) {
            container.innerHTML = '<p class="error">Error al conectar con el servidor.</p>';
        }
    }

    renderPlaceholder(container) {
        const userRol = (window.USER_ROL || '').toLowerCase();
        const canAdd = ['admin', 'ejecutivo', 'dueño_liga', 'super_arbitro', 'equipo', 'dueno_cancha'].includes(userRol);
        
        container.innerHTML = `
            <div class="stat-card" style="text-align: center; padding: 3rem; grid-column: 1 / -1;">
                <span style="font-size: 3rem;">🏁</span>
                <h4 style="margin-top: 1rem;">Sin Árbitros Registrados</h4>
                <p class="text-muted">Comienza agregando personal al cuerpo arbitral.</p>
                ${canAdd ? `
                    <button class="btn-primary" style="margin-top: 1rem;" onclick="ui.arbitros.showArbitroModal()">+ Agregar Miembro</button>
                ` : ''}
            </div>
        `;
    }

    renderArbitros(arbitros) {
        const container = document.getElementById('arbitros-container');
        if (!container) return;
        
        if (arbitros.length === 0) {
            this.renderPlaceholder(container);
            return;
        }

        const userRol = (window.USER_ROL || '').toLowerCase();
        const isPrincipal = ['admin', 'ejecutivo', 'dueño_liga', 'super_arbitro', 'equipo', 'dueno_cancha'].includes(userRol);

        // Agrupar por Liga
        const groups = {};
        arbitros.forEach(a => {
            const key = a.liga_id || 'independiente';
            if (!groups[key]) {
                groups[key] = {
                    nombre: a.liga_nombre || 'Independientes',
                    color: a.liga_color || 'var(--primary)',
                    items: []
                };
            }
            groups[key].items.push(a);
        });

        // Ordenar: Ligas primero, luego independientes
        const sortedKeys = Object.keys(groups).sort((a, b) => {
            if (a === 'independiente') return 1;
            if (b === 'independiente') return -1;
            return groups[a].nombre.localeCompare(groups[b].nombre);
        });

        container.innerHTML = sortedKeys.map(key => {
            const group = groups[key];
            const itemsHtml = group.items.map(a => {
                const isActive = a.activo !== false;
                const toggleIcon = isActive ? '⏸️ Suspender' : '▶️ Activar';

                return `
                <div class="stat-card" style="padding: 1.2rem; display: flex; align-items: center; justify-content: space-between; gap: 1rem; ${!isActive ? 'opacity: 0.6;' : ''} border-left: 4px solid ${group.color};">
                    <div style="flex: 1; text-align: left;">
                        <div style="display: flex; gap: 12px; align-items: center;">
                            <div style="width: 45px; height: 45px; border-radius: 50%; background-image: url('${a.foto_url || 'https://via.placeholder.com/50'}'); background-size: cover; border: 2px solid rgba(255,255,255,0.1);"></div>
                            <div style="flex: 1;">
                                <h4 style="margin: 0; font-size: 0.95rem;">${a.nombre}</h4>
                                <div style="display: flex; align-items: center; gap: 6px; margin-top: 3px;">
                                    <span class="badge" style="background: ${group.color}22; color: ${group.color}; font-size: 0.65rem; border: 1px solid ${group.color}33;">${a.nivel || 'Local'}</span>
                                    ${a.tiene_usuario ? `
                                        <span class="badge-premium" style="font-size: 0.6rem; background: rgba(0, 191, 255, 0.1); color: #00bfff; border: 1px solid rgba(0, 191, 255, 0.3); padding: 2px 6px;">
                                            🔗 Cuenta
                                        </span>
                                    ` : ''}
                                </div>
                            </div>
                        </div>
                        <div style="margin-top: 8px; display: grid; grid-template-columns: auto auto; gap: 8px;">
                            <p style="font-size: 0.75rem; color: var(--text-muted); margin: 0;">📞 ${a.telefono || 'Sin tel.'}</p>
                            ${a.telegram_id ? `<p style="font-size: 0.75rem; color: #24A1DE; margin: 0;">🔹 TG: ${a.telegram_id}</p>` : ''}
                        </div>
                        ${isPrincipal ? `
                        <div style="display:flex; gap:6px; margin-top: 10px;">
                            <button onclick="ui.arbitros.toggleStatus(${a.id}, ${isActive})" class="btn-secondary" style="padding: 3px 6px; font-size: 0.75rem;">${toggleIcon}</button>
                            <button onclick="ui.arbitros.editArbitro(${a.id})" class="btn-secondary" style="padding: 3px 6px; font-size: 0.75rem;">✏️</button>
                            <button onclick="ui.arbitros.deleteArbitro(${a.id})" class="btn-secondary" style="padding: 3px 6px; font-size: 0.75rem; color: #ff4444; border-color: rgba(255,68,68,0.2);">🗑️</button>
                        </div>
                        ` : ''}
                    </div>
                </div>
                `;
            }).join('');

            return `
            <div style="grid-column: 1 / -1; margin-top: 1.5rem; margin-bottom: 0.5rem;">
                <div style="display: flex; align-items: center; gap: 10px;">
                    <div style="width: 12px; height: 12px; border-radius: 50%; background: ${group.color}; box-shadow: 0 0 10px ${group.color};"></div>
                    <h3 style="margin: 0; font-size: 1.1rem; letter-spacing: 0.5px;">${group.nombre.toUpperCase()}</h3>
                    <div style="flex: 1; height: 1px; background: linear-gradient(90deg, ${group.color}44, transparent); margin-left: 10px;"></div>
                </div>
            </div>
            ${itemsHtml}
            `;
        }).join('');

        if (this.pagination && this.pagination.total_pages > 1) {
            container.innerHTML += `
                <div class="pagination-controls">
                    <button class="btn-pagination" ${!this.pagination.has_prev ? 'disabled' : ''} 
                        onclick="ui.arbitros.changePage(${this.pagination.page - 1})">
                        &laquo; Anterior
                    </button>
                    <span class="pagination-info">Página ${this.pagination.page} de ${this.pagination.total_pages}</span>
                    <button class="btn-pagination" ${!this.pagination.has_next ? 'disabled' : ''} 
                        onclick="ui.arbitros.changePage(${this.pagination.page + 1})">
                        Siguiente &raquo;
                    </button>
                </div>
            `;
        }
    }

    showArbitroModal(ligaId = null) {
        document.getElementById('arbitro-modal-title').innerText = 'Nuevo Miembro Arbitral';
        document.getElementById('arbitro-form').reset();
        document.getElementById('arbitro-id').value = '';
        document.getElementById('arbitro-foto').value = '';
        document.getElementById('arbitro-telegram').value = '';
        document.getElementById('arbitro-password').value = ''; 
        document.getElementById('arbitro-email').value = ''; 

        const ligaSelect = document.getElementById('arbitro-liga-id');
        if (ligaSelect) {
            ligaSelect.value = (ligaId === 'global' || !ligaId) ? '' : ligaId;
        }

        const ligaContainer = document.getElementById('arbitro-liga-container');
        const userRol = (window.USER_ROL || '').toLowerCase();
        
        if (['admin', 'ejecutivo'].includes(userRol)) {
            if (ligaContainer && ligaSelect) {
                ligaContainer.style.display = 'block';
                ligaSelect.innerHTML = '<option value="">-- Sin Liga / Independiente --</option>' + 
                    this.ligas.map(l => `<option value="${l.id}">${l.nombre}</option>`).join('');
            }
        } else {
            if (ligaContainer) ligaContainer.style.display = 'none';
        }

        Core.openModal('modal-arbitro');
    }

    async editArbitro(id) {
        // Usar caché si está disponible, si no, cargar
        if (this.arbitros.length === 0) await this.loadArbitros();
        
        const a = this.arbitros.find(x => x.id === id);

        if (a) {
            document.getElementById('arbitro-modal-title').innerText = 'Editar Árbitro';
            document.getElementById('arbitro-id').value = a.id;
            document.getElementById('arbitro-nombre').value = a.nombre;
            document.getElementById('arbitro-email').value = a.email || '';
            document.getElementById('arbitro-telefono').value = a.telefono || '';
            document.getElementById('arbitro-nivel').value = a.nivel || 'Local';
            document.getElementById('arbitro-foto').value = a.foto_url || '';
            document.getElementById('arbitro-telegram').value = a.telegram_id || '';
            document.getElementById('arbitro-password').value = a.password || '';

            const ligaContainer = document.getElementById('arbitro-liga-container');
            const ligaSelect = document.getElementById('arbitro-liga-id');
            const userRol = (window.USER_ROL || '').toLowerCase();

            if (['admin', 'ejecutivo'].includes(userRol)) {
                if (ligaContainer && ligaSelect) {
                    ligaContainer.style.display = 'block';
                    ligaSelect.innerHTML = '<option value="">-- Sin Liga / Independiente --</option>' + 
                        this.ligas.map(l => `<option value="${l.id}">${l.nombre}</option>`).join('');
                    ligaSelect.value = a.liga_id || '';
                }
            } else {
                if (ligaContainer) ligaContainer.style.display = 'none';
            }

            Core.openModal('modal-arbitro');
        }
    }

    async handleArbitroSubmit(e) {
        e.preventDefault();
        const id = document.getElementById('arbitro-id').value;
        const data = {
            nombre: document.getElementById('arbitro-nombre').value,
            email: document.getElementById('arbitro-email').value,
            telefono: document.getElementById('arbitro-telefono').value,
            nivel: document.getElementById('arbitro-nivel').value,
            foto_url: document.getElementById('arbitro-foto').value,
            telegram_id: document.getElementById('arbitro-telegram').value.trim(),
            password: document.getElementById('arbitro-password').value,
            liga_id: document.getElementById('arbitro-liga-id').value || null
        };

        const method = id ? 'PUT' : 'POST';
        const url = id ? `/api/arbitros/${id}` : '/api/arbitros';

        try {
            const response = await fetch(url, {
                method: method,
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(data)
            });

            if (response.ok) {
                Core.closeModal('modal-arbitro');
                this.loadArbitros();
            } else {
                const err = await response.json();
                alert('Error al guardar árbitro: ' + (err.error || 'Desconocido'));
            }
        } catch (error) { alert('Error de conexión'); }
    }

    async toggleStatus(id, currentStatus) {
        try {
            const response = await fetch(`/api/arbitros/${id}`, {
                method: 'PUT',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ activo: !currentStatus })
            });
            if (response.ok) {
                this.loadArbitros();
            } else {
                const err = await response.json();
                alert('Error: ' + (err.error || 'No se pudo cambiar el estado.'));
            }
        } catch (error) {
            console.error('Error toggling status:', error);
            alert('Error de conexión');
        }
    }

    async deleteArbitro(id) {
        if (!confirm('¿Eliminar a este árbitro del sistema?')) return;
        try {
            const response = await fetch(`/api/arbitros/${id}`, { method: 'DELETE' });
            if (response.ok) {
                this.loadArbitros();
            } else {
                const err = await response.json();
                alert('Error al eliminar: ' + (err.error || 'Desconocido'));
            }
        } catch (error) { alert('Error de conexión'); }
    }
}
