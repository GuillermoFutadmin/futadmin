class EntrenamientosModule {
    constructor(ui) {
        this.ui = ui;
        this.currentGrupoId = null;
        this.paginationGrupos = null;
        this.paginationAlumnos = null;

        // Desacoplamiento v72.0: Auto-inicialización vía eventos
        window.addEventListener('futadmin:view-change', (e) => {
            const { viewId, tabId } = e.detail;
            if (viewId === 'entrenamientos') {
                // Manejar lógica de pestañas interna de entrenamientos
                document.querySelectorAll('#view-entrenamientos .tab-content').forEach(c => c.style.display = 'none');
                const target = document.getElementById(`entrenamientos-${tabId || 'grupos'}`);
                if (target) {
                    target.style.display = 'block';
                    if ((tabId || 'grupos') === 'grupos') this.loadGrupos();
                    else if (tabId === 'alumnos') this.loadAlumnos();
                }
            }
        });
    }

    async changeGruposPage(page) {
        await this.loadGrupos(page);
        window.scrollTo({ top: 0, behavior: 'smooth' });
    }

    async changeAlumnosPage(page) {
        await this.loadAlumnos(page);
        window.scrollTo({ top: 0, behavior: 'smooth' });
    }

    init() {
        this.loadGrupos();
    }

    // --- Tab Switching in Modal ---
    switchTab(tabId, btn) {
        document.querySelectorAll('#form-grupo-entrenamiento .modal-tab').forEach(b => b.classList.remove('active'));
        document.querySelectorAll('#form-grupo-entrenamiento .modal-tab-content').forEach(c => {
            c.classList.remove('active');
            c.style.display = 'none';
        });
        if (btn) btn.classList.add('active');
        const target = document.getElementById(`grupo-tab-${tabId}`);
        if (target) { target.classList.add('active'); target.style.display = 'block'; }
    }

    // --- Grupos de Entrenamiento ---
    async loadGrupos(page = 1) {
        try {
            const res = await fetch(`/api/entrenamientos/grupos?page=${page}`);
            const data = await res.json();
            this.paginationGrupos = data.pagination;
            this.renderGrupos(data.items, this.paginationGrupos);
            this.loadProfesoresSelect();
        } catch (e) {
            console.error("Error al cargar grupos de entrenamiento:", e);
        }
    }

    renderGrupos(grupos, pagination) {
        const container = document.getElementById('grupos-entrenamiento-list');
        if (!container) return;

        if (grupos.length === 0) {
            container.innerHTML = `
                <div class="empty-state" style="grid-column: 1 / -1; text-align: center; padding: 3rem;">
                    <div style="font-size: 3rem; margin-bottom: 1rem;">⚽</div>
                    <h3>No hay Grupos Registrados</h3>
                    <p style="color: var(--text-muted);">Crea tu primer grupo de entrenamiento (ej. Categoría 2014)</p>
                </div>`;
            return;
        }

        const typeColors = {
            'Alto Rendimiento': '#f59e0b',
            'Porteros': '#8b5cf6',
            'Femenil': '#ec4899',
            'Libre': '#6b7280',
            'default': '#10b981'
        };

        container.innerHTML = grupos.map(g => {
            const color = typeColors[g.tipo] || typeColors['default'];
            return `
            <div class="league-card fade-in-up" onclick="if(!event.target.closest('button')) ui.entrenamientos.goToAlumnos(${g.id}, '${g.nombre.replace(/'/g, "\\'")}')" 
                style="padding: 1.5rem; display: flex; align-items: stretch; justify-content: space-between; gap: 1.5rem; cursor: pointer; min-height: 180px; margin-bottom: 1rem; position: relative;">
                <div style="flex: 1; text-align: left; display: flex; flex-direction: column; justify-content: space-between;">
                    <div>
                        <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 4px;">
                            <span class="league-badge" style="margin-bottom: 0; background: ${color}22; color: ${color}; border: 1px solid ${color}44;">${g.tipo || 'General'}</span>
                            <span class="league-badge" style="background: rgba(255,255,255,0.05); color: #fff; border: 1px solid rgba(255,255,255,0.1); margin-left: 5px;">${g.categoria || ''}</span>
                            <span style="font-size: 0.75rem; color: ${g.activo ? 'var(--primary)' : '#ff4444'}; font-weight: 700; text-transform: uppercase;">● ${g.activo ? 'Activo' : 'Inactivo'}</span>
                        </div>
                        <h4 style="margin: 0; font-size: 1.5rem; color: #fff; font-weight: 700;">${g.nombre}</h4>
                        
                        <div style="display: flex; gap: 8px; flex-wrap: wrap; margin: 10px 0;">
                            <div style="background: rgba(255,255,255,0.02); padding: 4px 10px; border-radius: 6px; border: 1px solid rgba(255,255,255,0.05);">
                                <span style="display: block; font-size: 0.55rem; color: var(--text-muted); text-transform: uppercase;">Inscripción</span>
                                <strong style="color: #00ff88; font-size: 0.9rem;">$${(g.costo_inscripcion || 0).toFixed(0)}</strong>
                            </div>
                            <div style="background: rgba(255,255,255,0.02); padding: 4px 10px; border-radius: 6px; border: 1px solid rgba(255,255,255,0.05);">
                                <span style="display: block; font-size: 0.55rem; color: var(--text-muted); text-transform: uppercase;">Mensualidad</span>
                                <strong style="color: #00ff88; font-size: 0.9rem;">$${(g.costo_mensual || 0).toFixed(0)}</strong>
                            </div>
                            <div style="background: rgba(255,255,255,0.02); padding: 4px 10px; border-radius: 6px; border: 1px solid rgba(255,255,255,0.05);">
                                <span style="display: block; font-size: 0.55rem; color: var(--text-muted); text-transform: uppercase;">Alumnos</span>
                                <strong style="color: #fff; font-size: 0.9rem;">${g.alumnos_count} / ${g.capacidad || '∞'}</strong>
                            </div>
                        </div>

                        <div style="font-size: 0.85rem; color: var(--text-muted); display: grid; grid-template-columns: 1fr 1fr; gap: 10px;">
                            <span>⏰ ${g.horario || 'N/A'}</span>
                            <span>📅 ${g.dias || 'N/A'}</span>
                            <span>👨‍🏫 ${g.profesor_nombre || 'Sin asignar'}</span>
                            ${g.cancha ? `<span>🏟️ ${g.cancha}</span>` : ''}
                        </div>
                    </div>

                    <div class="card-actions" onclick="event.stopPropagation()" style="display: flex; gap: 10px; margin-top: 15px;">
                        ${window.USER_ROL !== 'resultados' && window.USER_ROL !== 'arbitro' ? `
                        <button onclick="ui.entrenamientos.editGrupo(${g.id})" class="btn-secondary" style="padding: 6px 14px; font-size: 0.85rem; border-radius: 8px; display: flex; align-items: center; gap: 6px;">
                            <span>✏️</span> Editar
                        </button>
                        <button onclick="ui.entrenamientos.deleteGrupo(${g.id})" class="btn-secondary" style="padding: 6px 14px; font-size: 0.85rem; border-radius: 8px; display: flex; align-items: center; gap: 6px; color: #ff4444; border-color: rgba(255,68,68,0.2);">
                            <span>🗑️</span> Borrar
                        </button>
                        ` : ''}
                    </div>
                </div>
                <div style="flex-shrink: 0; width: 160px; height: 160px;">
                    ${g.foto_url ? `
                        <div style="background-image: url('${g.foto_url}'); height: 100%; width: 100%; background-size: cover; background-position: center; border-radius: 16px; border: 2px solid var(--border); box-shadow: 0 10px 25px rgba(0,0,0,0.4);"></div>
                    ` : `
                        <div style="height: 100%; width: 100%; background: rgba(255,255,255,0.05); display: flex; align-items: center; justify-content: center; font-size: 4rem; border-radius: 16px; border: 1px dashed var(--border);">⚽</div>
                    `}
                </div>
            </div>`;
        }).join('');

        if (pagination && pagination.total_pages > 1) {
            container.innerHTML += `
                <div class="pagination-controls">
                    <button class="btn-pagination" ${!pagination.has_prev ? 'disabled' : ''} 
                        onclick="ui.entrenamientos.changeGruposPage(${pagination.page - 1})">
                        &laquo; Anterior
                    </button>
                    <span class="pagination-info">Página ${pagination.page} de ${pagination.total_pages}</span>
                    <button class="btn-pagination" ${!pagination.has_next ? 'disabled' : ''} 
                        onclick="ui.entrenamientos.changeGruposPage(${pagination.page + 1})">
                        Siguiente &raquo;
                    </button>
                </div>
            `;
        }
    }

    async loadProfesoresSelect() {
        try {
            const res = await fetch('/api/arbitros');
            const response = await res.json();
            const profes = response.items || response || [];
            const select = document.getElementById('grupo-profesor');
            if (select) {
                const current = select.value;
                select.innerHTML = '<option value="">Sin asignar...</option>' +
                    (Array.isArray(profes) ? profes.map(p => `<option value="${p.id}">${p.nombre}</option>`).join('') : '');
                if (current) select.value = current;
            }
        } catch (e) { console.error(e); }
    }

    async loadCanchasSelect() {
        try {
            const res = await fetch('/api/canchas');
            const data = await res.json();
            const canchas = data.items || data;
            const select = document.getElementById('grupo-cancha');
            if (select) {
                const current = select.value;
                select.innerHTML = '<option value="">-- Sin Cancha Asignada --</option>' +
                    canchas.map(c => `<option value="${c.nombre}">${c.nombre} (${c.tipo})</option>`).join('');
                if (current) select.value = current;
            }
        } catch (e) { console.error(e); }
    }

    _getDiasFromCheckboxes() {
        return Array.from(document.querySelectorAll('.grupo-day-cb:checked')).map(cb => cb.value).join(', ');
    }

    _setDiasCheckboxes(diasStr) {
        document.querySelectorAll('.grupo-day-cb').forEach(cb => cb.checked = false);
        if (!diasStr) return;
        diasStr.split(',').map(d => d.trim()).forEach(d => {
            const cb = document.querySelector(`.grupo-day-cb[value="${d}"]`);
            if (cb) cb.checked = true;
        });
    }

    _getPayload() {
        return {
            nombre: document.getElementById('grupo-nombre').value,
            tipo: document.getElementById('grupo-tipo').value,
            categoria: document.getElementById('grupo-categoria').value,
            profesor_id: document.getElementById('grupo-profesor').value || null,
            capacidad: document.getElementById('grupo-capacidad').value || 0,
            fecha_inicio: document.getElementById('grupo-fecha-inicio').value || null,
            fecha_fin: document.getElementById('grupo-fecha-fin').value || null,
            dias: this._getDiasFromCheckboxes(),
            horario: document.getElementById('grupo-horario').value,
            cancha: document.getElementById('grupo-cancha').value,
            costo_inscripcion: parseFloat(document.getElementById('grupo-costo-inscripcion').value || 0),
            costo_mensual: parseFloat(document.getElementById('grupo-costo').value || 0),
            foto_url: document.getElementById('grupo-foto').value || ""
        };
    }

    async saveGrupo(e) {
        e.preventDefault();
        const id = document.getElementById('grupo-id').value;
        const payload = this._getPayload();

        const method = id ? 'PUT' : 'POST';
        const url = id ? `/api/entrenamientos/grupos/${id}` : '/api/entrenamientos/grupos';

        try {
            const res = await fetch(url, {
                method,
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload)
            });
            if (res.ok) {
                Core.closeModal('modal-grupo-entrenamiento');
                Core.showNotification(`Grupo ${id ? 'actualizado' : 'creado'} correctamente`, 'success');
                this.loadGrupos();
            }
        } catch (err) {
            console.error(err);
            Core.showNotification('Error al guardar el grupo', 'error');
        }
    }

    editGrupo(id) {
        fetch('/api/entrenamientos/grupos')
            .then(r => r.json())
            .then(grupos => {
                const g = grupos.find(x => x.id === parseInt(id));
                if (!g) return;
                document.getElementById('grupo-id').value = g.id;
                document.getElementById('grupo-modal-title').textContent = '✏️ Editar Grupo: ' + g.nombre;
                document.getElementById('grupo-nombre').value = g.nombre;
                document.getElementById('grupo-tipo').value = g.tipo || 'Fútbol Base';
                document.getElementById('grupo-categoria').value = g.categoria || 'Infantil';
                document.getElementById('grupo-capacidad').value = g.capacidad || '';
                document.getElementById('grupo-fecha-inicio').value = g.fecha_inicio || '';
                document.getElementById('grupo-fecha-fin').value = g.fecha_fin || '';
                document.getElementById('grupo-foto').value = g.foto_url || '';

                const preview = document.getElementById('grupo-foto-preview');
                const placeholder = document.getElementById('grupo-foto-placeholder');
                if (g.foto_url) {
                    if (preview) {
                        preview.src = g.foto_url;
                        preview.style.display = 'block';
                    }
                    if (placeholder) placeholder.style.display = 'none';
                } else {
                    if (preview) {
                        preview.src = '';
                        preview.style.display = 'none';
                    }
                    if (placeholder) placeholder.style.display = 'block';
                }

                this._setDiasCheckboxes(g.dias);
                document.getElementById('grupo-horario').value = g.horario || '';
                this.loadCanchasSelect().then(() => {
                    document.getElementById('grupo-cancha').value = g.cancha || '';
                });

                document.getElementById('grupo-costo-inscripcion').value = g.costo_inscripcion || 0;
                document.getElementById('grupo-costo').value = g.costo_mensual || 0;

                this.loadProfesoresSelect().then(() => {
                    document.getElementById('grupo-profesor').value = g.profesor_id || '';
                });
                // Reset to first tab
                this.switchTab('general', document.querySelector('#form-grupo-entrenamiento .modal-tab'));
                Core.openModal('modal-grupo-entrenamiento');
            })
            .catch(console.error);
    }

    deleteGrupo(id) {
        if (!confirm("¿Estás seguro de eliminar este grupo de entrenamiento? Todos los alumnos inscritos quedarán sin grupo.")) return;
        fetch(`/api/entrenamientos/grupos/${id}`, { method: 'DELETE' })
            .then(res => {
                if (res.ok) {
                    Core.showNotification('Grupo eliminado correctamente', 'success');
                    this.loadGrupos();
                } else {
                    Core.showNotification('Error al eliminar el grupo', 'error');
                }
            })
            .catch(e => {
                console.error(e);
                Core.showNotification('Error de red al eliminar el grupo', 'error');
            });
    }

    openNuevoGrupoModal() {
        document.getElementById('form-grupo-entrenamiento').reset();
        document.getElementById('grupo-id').value = '';
        document.getElementById('grupo-modal-title').textContent = '⚽ Nuevo Grupo de Entrenamiento';
        document.getElementById('grupo-foto').value = '';
        const preview = document.getElementById('grupo-foto-preview');
        if (preview) {
            preview.src = '';
            preview.style.display = 'none';
        }
        const placeholder = document.getElementById('grupo-foto-placeholder');
        if (placeholder) placeholder.style.display = 'block';

        this._setDiasCheckboxes('');
        this.loadProfesoresSelect();
        this.loadCanchasSelect();
        this.switchTab('general', document.querySelector('#form-grupo-entrenamiento .modal-tab'));
        Core.openModal('modal-grupo-entrenamiento');
    }

    // --- Alumnos ---
    goToAlumnos(grupoId, grupoNombre) {
        this.currentGrupoId = grupoId;
        document.getElementById('current-grupo-title').textContent = `Alumnos: ${grupoNombre}`;
        ui.switchView('entrenamientos', 'alumnos');
        this.loadAlumnos();
    }

    goToGrupos() {
        this.currentGrupoId = null;
        ui.switchView('entrenamientos', 'grupos');
        this.loadGrupos();
    }

    async loadAlumnos(page = 1) {
        if (!this.currentGrupoId) return;
        try {
            const res = await fetch(`/api/entrenamientos/alumnos?grupo_id=${this.currentGrupoId}&page=${page}`);
            const data = await res.json();
            this.paginationAlumnos = data.pagination;
            this.renderAlumnos(data.items, this.paginationAlumnos);
        } catch (e) { console.error("Error cargando alumnos:", e); }
    }

    renderAlumnos(alumnos, pagination) {
        const container = document.getElementById('alumnos-entrenamiento-list');
        if (!container) return;

        if (alumnos.length === 0) {
            container.innerHTML = `
                <div class="empty-state" style="grid-column: 1 / -1; text-align: center; padding: 3rem;">
                    <div style="font-size: 3rem; margin-bottom: 1rem;">👥</div>
                    <h3>No hay Alumnos Inscritos</h3>
                    <p style="color: var(--text-muted);">Inscribe a tu primer alumno en este grupo.</p>
                </div>`;
            return;
        }

        const calculateAge = (birthDate) => {
            if (!birthDate) return null;
            const today = new Date();
            const birth = new Date(birthDate);
            let age = today.getFullYear() - birth.getFullYear();
            const m = today.getMonth() - birth.getMonth();
            if (m < 0 || (m === 0 && today.getDate() < birth.getDate())) age--;
            return age;
        };

        container.innerHTML = alumnos.map(a => {
            const edad = calculateAge(a.fecha_nacimiento);
            return `
            <div class="league-card fade-in-up" 
                style="padding: 1.5rem; display: flex; align-items: center; justify-content: space-between; gap: 1.5rem; min-height: 140px; margin-bottom: 1rem; position: relative; border-left: 4px solid ${a.activo ? 'var(--primary)' : '#ef4444'};">
                <div style="flex: 1; text-align: left;">
                    <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 4px;">
                        <span class="league-badge" style="background: ${a.activo ? 'rgba(0,255,136,0.1)' : 'rgba(239,68,68,0.1)'}; color: ${a.activo ? 'var(--primary)' : '#ef4444'}; border: 1px solid ${a.activo ? 'rgba(0,255,136,0.2)' : 'rgba(239,68,68,0.2)'}; margin-bottom: 0;">${a.activo ? 'Activo' : 'Inactivo'}</span>
                        <span style="font-size: 0.8rem; color: var(--text-muted); font-weight: 500;">ID: #${a.id}</span>
                    </div>
                    <h4 style="margin: 0 0 4px 0; font-size: 1.4rem; color: #fff; font-weight: 700;">${a.nombre}</h4>
                    <div style="font-size: 0.85rem; color: var(--text-muted); display: flex; flex-direction: column; gap: 4px; margin-bottom: 1rem;">
                        <span>🎂 ${a.fecha_nacimiento || 'S/N'} ${edad !== null ? `(${edad} años)` : ''}</span>
                        <span>👤 Tutor: ${a.nombre_tutor || 'Sin tutor'}</span>
                        <span>📱 Tel: ${a.telefono_contacto || 'Sin teléfono'}</span>
                    </div>
                    <div style="display: flex; gap: 8px;">
                        ${window.USER_ROL !== 'resultados' && window.USER_ROL !== 'arbitro' ? `
                        <button onclick="ui.entrenamientos.editAlumno(${a.id})" class="btn-secondary" style="padding: 6px 12px; font-size: 0.8rem; border-radius: 8px;">✏️ Editar</button>
                        <button onclick="ui.entrenamientos.deleteAlumno(${a.id})" class="btn-secondary" style="padding: 6px 12px; font-size: 0.8rem; border-radius: 8px; color: #ef4444; border-color: rgba(239,68,68,0.2);">🗑️ Borrar</button>
                        ` : ''}
                    </div>
                </div>
                <div style="flex-shrink: 0;">
                    ${a.foto_url ?
                    `<div style="background-image: url('${a.foto_url}'); height: 100px; width: 100px; background-size: cover; background-position: center; border-radius: 50%; border: 3px solid var(--glass); box-shadow: 0 4px 15px rgba(0,0,0,0.5);"></div>` :
                    `<div style="height: 100px; width: 100px; background: rgba(255,255,255,0.05); display: flex; align-items: center; justify-content: center; font-size: 2.5rem; border-radius: 50%; border: 1px dashed var(--border);">🧑</div>`
                }
                </div>
            </div>`;
        }).join('');

        if (pagination && pagination.total_pages > 1) {
            container.innerHTML += `
                <div class="pagination-controls">
                    <button class="btn-pagination" ${!pagination.has_prev ? 'disabled' : ''} 
                        onclick="ui.entrenamientos.changeAlumnosPage(${pagination.page - 1})">
                        &laquo; Anterior
                    </button>
                    <span class="pagination-info">Página ${pagination.page} de ${pagination.total_pages}</span>
                    <button class="btn-pagination" ${!pagination.has_next ? 'disabled' : ''} 
                        onclick="ui.entrenamientos.changeAlumnosPage(${pagination.page + 1})">
                        Siguiente &raquo;
                    </button>
                </div>
            `;
        }
    }

    openAlumnoModal() {
        document.getElementById('form-alumno-entrenamiento').reset();
        document.getElementById('alumno-id').value = '';
        document.getElementById('alumno-grupo-id').value = this.currentGrupoId;
        Core.openModal('modal-alumno-entrenamiento');
    }

    async saveAlumno(e) {
        e.preventDefault();
        const id = document.getElementById('alumno-id').value;
        const payload = {
            grupo_id: document.getElementById('alumno-grupo-id').value,
            nombre: document.getElementById('alumno-nombre').value,
            fecha_nacimiento: document.getElementById('alumno-fechanac').value || null,
            nombre_tutor: document.getElementById('alumno-tutor').value,
            telefono_contacto: document.getElementById('alumno-telefono').value,
            foto_url: document.getElementById('alumno-foto').value,
            pago_inicial: parseFloat(document.getElementById('alumno-pago-inicial').value || 0),
            metodo_pago: document.getElementById('alumno-metodo-pago').value,
            activo: true
        };

        const method = id ? 'PUT' : 'POST';
        const url = id ? `/api/entrenamientos/alumnos/${id}` : '/api/entrenamientos/alumnos';

        try {
            const res = await fetch(url, { method, headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(payload) });
            if (res.ok) {
                const data = await res.json();
                Core.closeModal('modal-alumno-entrenamiento');
                Core.showNotification(`Alumno ${id ? 'actualizado' : 'inscrito'} correctamente`, 'success');

                if (data.ticket) {
                    this.showTicket(data.ticket);
                }

                this.loadAlumnos();
                this.loadGrupos();
            }
        } catch (err) {
            console.error(err);
            Core.showNotification('Error guardando alumno', 'error');
        }
    }

    async deleteAlumno(id) {
        if (!confirm("¿Estás seguro de dar de baja a este alumno?")) return;
        try {
            const res = await fetch(`/api/entrenamientos/alumnos/${id}`, { method: 'DELETE' });
            if (res.ok) {
                Core.showNotification('Alumno eliminado', 'success');
                this.loadAlumnos();
                this.loadGrupos();
            }
        } catch (e) { Core.showNotification('Error al eliminar alumno', 'error'); }
    }

    async editAlumno(id) {
        if (!this.currentGrupoId) return;
        try {
            const res = await fetch(`/api/entrenamientos/alumnos?grupo_id=${this.currentGrupoId}`);
            const alumnos = await res.json();
            const a = alumnos.find(x => x.id === id);
            if (a) {
                document.getElementById('alumno-id').value = a.id;
                document.getElementById('alumno-grupo-id').value = a.grupo_id;
                document.getElementById('alumno-nombre').value = a.nombre;
                document.getElementById('alumno-fechanac').value = a.fecha_nacimiento;
                document.getElementById('alumno-tutor').value = a.nombre_tutor;
                document.getElementById('alumno-telefono').value = a.telefono_contacto;
                document.getElementById('alumno-foto').value = a.foto_url || '';
                Core.openModal('modal-alumno-entrenamiento');
            }
        } catch (e) { console.error(e); }
    }

    showTicket(ticket) {
        const container = document.getElementById('digital-ticket-content');
        if (!container) return;

        container.innerHTML = `
            <div style="text-align:center; padding:20px; color:#fff; font-family:'Inter', sans-serif;">
                <div style="font-size:3rem; margin-bottom:10px;">🏆</div>
                <h2 style="margin:0 0 5px; color:var(--primary);">FutAdmin</h2>
                <p style="margin:0 0 20px; font-size:0.8rem; color:var(--text-muted); text-transform:uppercase; letter-spacing:1px;">Comprobante de Inscripción</p>
                
                <div style="background:rgba(255,255,255,0.05); border-radius:12px; padding:20px; text-align:left; border:1px solid rgba(255,255,255,0.1);">
                    <div style="margin-bottom:15px; border-bottom:1px solid rgba(255,255,255,0.05); padding-bottom:10px;">
                        <span style="display:block; font-size:0.7rem; color:var(--text-muted); text-transform:uppercase;">Alumno</span>
                        <strong style="font-size:1.1rem; color:#fff;">${ticket.alumno}</strong>
                    </div>
                    
                    <div style="display:grid; grid-template-columns:1fr 1fr; gap:15px; margin-bottom:15px;">
                        <div>
                            <span style="display:block; font-size:0.7rem; color:var(--text-muted); text-transform:uppercase;">Grupo</span>
                            <strong style="color:#fff;">${ticket.grupo}</strong>
                        </div>
                        <div>
                            <span style="display:block; font-size:0.7rem; color:var(--text-muted); text-transform:uppercase;">Categoría</span>
                            <strong style="color:#fff;">${ticket.categoria}</strong>
                        </div>
                    </div>
                    
                    <div style="margin-bottom:15px; border-bottom:1px solid rgba(255,255,255,0.05); padding-bottom:10px;">
                        <span style="display:block; font-size:0.7rem; color:var(--text-muted); text-transform:uppercase;">Entrenador</span>
                        <strong style="color:#fff;">${ticket.profesor}</strong>
                    </div>

                    <div style="display:grid; grid-template-columns:1fr 1fr; gap:15px; margin-bottom:15px;">
                        <div>
                            <span style="display:block; font-size:0.7rem; color:var(--text-muted); text-transform:uppercase;">Días</span>
                            <strong style="color:#fff;">${ticket.dias}</strong>
                        </div>
                        <div>
                            <span style="display:block; font-size:0.7rem; color:var(--text-muted); text-transform:uppercase;">Horario</span>
                            <strong style="color:#fff;">${ticket.horario}</strong>
                        </div>
                    </div>
                    
                    <div style="background:var(--primary); color:#000; padding:15px; border-radius:10px; margin-top:10px; text-align:center;">
                        <span style="display:block; font-size:0.7rem; font-weight:700; text-transform:uppercase; margin-bottom:5px;">Monto Pagado</span>
                        <strong style="font-size:1.8rem;">$${parseFloat(ticket.monto_pagado).toFixed(2)}</strong>
                        <p style="margin:5px 0 0; font-size:0.75rem; opacity:0.8;">Método: ${ticket.metodo}</p>
                    </div>
                </div>
                
                <p style="margin:20px 0 10px; font-size:0.75rem; color:var(--text-muted);">Fecha: ${ticket.fecha}</p>
                <div style="display:flex; gap:10px; justify-content:center; margin-top:20px;">
                    <button class="btn-primary" onclick="window.print()" style="padding:10px 25px;">🖨️ Imprimir</button>
                    <button class="btn-secondary" onclick="Core.closeModal('modal-ticket-digital')" style="padding:10px 25px;">Cerrar</button>
                </div>
            </div>
        `;
        Core.openModal('modal-ticket-digital');
    }
}

export default EntrenamientosModule;
