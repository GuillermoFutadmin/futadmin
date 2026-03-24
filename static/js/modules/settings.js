/**
 * Módulo de Ajustes - Gestión de Roles y Usuarios
 */
import { Core } from './core.js';

export class SettingsModule {
    constructor(ui) {
        this.ui = ui;
        this.users = [];
        this.ligas = [];
        this.payments = [];
        this.statusPage = 1;
        this.paymentsPage = 1;
        this.statusLimit = 10;
        this.paymentsLimit = 10;
        document.addEventListener('futadmin:limitsLoaded', () => this.checkLimits());
    }

    async init() {
        this.canchas = [];
        await this.loadLigas();
        await this.loadUsers();
        await this.loadCanchas();
        this.setupEventListeners();
        this.checkLimits();
    }

    setupEventListeners() {
        const form = document.getElementById('user-form');
        if (form) {
            form.onsubmit = (e) => this.handleUserSubmit(e);
        }
        const comboForm = document.getElementById('combo-form');
        if (comboForm) {
            comboForm.onsubmit = (e) => this.handleComboSubmit(e);
        }
        const paymentForm = document.getElementById('combo-payment-form');
        if (paymentForm) {
            paymentForm.onsubmit = (e) => this.handleComboPaymentSubmit(e);
        }
        const editPaymentForm = document.getElementById('edit-combo-payment-form');
        if (editPaymentForm) {
            editPaymentForm.onsubmit = (e) => this.handleEditComboPaymentSubmit(e);
        }
    }

    checkLimits() {
        if (!window.FutAdminLimits || !window.FutAdminCounts) return;
        const btn = document.getElementById('btn-nuevo-usuario');
        if (!btn) return;

        const limit = window.FutAdminLimits.users;
        const count = window.FutAdminCounts.users || 0;

        if (limit !== undefined && count >= limit) {
            btn.style.display = 'none';
        } else {
            btn.style.display = 'inline-block';
        }
    }

    updateComboPriceInfo(rol) {
        const info = document.getElementById('combo-price-info');
        if (!info) return;
        
        const details = {
            'dueño_liga': 'Incluye 1 cancha + 5 ligas y 4 cuentas de acceso. Costo: $350/mes.',
            'super_arbitro': 'Incluye 1 cancha + 2 ligas y 4 cuentas de acceso. Costo: $150/mes.',
            'equipo': 'Incluye 1 cancha + 1 liga y 4 cuentas de acceso. Costo: $100/mes.'
        };
        
        info.innerText = details[rol] || 'Selecciona un plan para ver los detalles.';
    }

    showComboModal(ligaId = null) {
        const idInput = document.getElementById('combo-liga-id');
        const form = document.getElementById('combo-form');
        const planSection = document.getElementById('combo-section-plan');
        const ownerSection = document.getElementById('combo-section-owner');
        const submitBtn = document.getElementById('combo-submit-btn');
        const title = document.getElementById('combo-modal-title');

        form.reset();
        
        if (ligaId) {
            // Modo Edición
            const liga = this.ligas.find(l => l.id == ligaId);
            if (!liga) return;

            idInput.value = liga.id;
            document.getElementById('combo-nombre').value = liga.nombre;
            document.getElementById('combo-color').value = liga.color || '#00ff88';
            document.getElementById('combo-contacto').value = liga.contacto || '';
            
            // Cargar datos del titular
            document.getElementById('combo-owner-nombre').value = liga.nombre; // O el nombre del primer usuario
            document.getElementById('combo-owner-email').value = liga.owner_email || '';
            document.getElementById('combo-owner-pass').value = ''; // Mantener vacío al editar a menos que se quiera cambiar
            document.getElementById('combo-owner-pass').placeholder = 'Dejar vacío para no cambiar';

            title.innerText = '✏️ Editar Organización';
            submitBtn.innerText = 'Guardar Cambios';
            
            // Ajustar secciones para edición
            if (planSection) planSection.style.display = 'none';
            if (ownerSection) {
                ownerSection.style.display = 'block';
                const ownerTitle = document.getElementById('combo-owner-title');
                const ownerHelp = document.getElementById('combo-owner-help');
                const ownerNameGroup = document.getElementById('combo-owner-name-group');
                if (ownerTitle) ownerTitle.innerText = 'Credenciales de Acceso Principal';
                if (ownerHelp) ownerHelp.innerText = 'Si cambias la contraseña, se actualizarán las 4 cuentas vinculadas.';
                if (ownerNameGroup) ownerNameGroup.style.display = 'none'; // El nombre del titular suele ser el de la liga en el registro auto
            }
            
            // Los campos de owner no son requeridos en edición (para permitir no cambiar pass)
            document.getElementById('combo-owner-nombre').required = false;
            document.getElementById('combo-owner-email').required = true; // Email sí es necesario si se quiere cambiar
            document.getElementById('combo-owner-pass').required = false;
        } else {
            // Modo Creación
            idInput.value = '';
            document.getElementById('combo-color').value = '#00ff88';
            title.innerText = '✚ Nuevo Combo / Organización';
            submitBtn.innerText = '✚ Crear Combo';
            
            if (planSection) planSection.style.display = 'block';
            if (ownerSection) {
                ownerSection.style.display = 'block';
                const ownerTitle = document.getElementById('combo-owner-title');
                const ownerHelp = document.getElementById('combo-owner-help');
                const ownerNameGroup = document.getElementById('combo-owner-name-group');
                if (ownerTitle) ownerTitle.innerText = 'Cuenta del Responsable Titular';
                if (ownerHelp) ownerHelp.innerText = 'Se crearán automáticamente 3 subcuentas extra usando esta misma contraseña.';
                if (ownerNameGroup) ownerNameGroup.style.display = 'block';
            }
            
            document.getElementById('combo-owner-nombre').value = '';
            document.getElementById('combo-owner-email').value = '';
            document.getElementById('combo-owner-pass').value = '';
            document.getElementById('combo-owner-pass').placeholder = 'Mínimo 6 caracteres';
            document.getElementById('combo-contacto').value = '';
            document.getElementById('combo-owner-nombre').required = true;
            document.getElementById('combo-owner-email').required = true;
            document.getElementById('combo-owner-pass').required = true;
            
            this.updateComboPriceInfo('dueño_liga'); // Default
        }

        Core.openModal('modal-combo');
    }

    // Alias para ser consistente con otras entidades
    editCombo(id) {
        this.showComboModal(id);
    }

    async handleComboSubmit(e) {
        e.preventDefault();
        const id = document.getElementById('combo-liga-id').value;
        const isEdit = id && id !== '';

        const data = {
            nombre: document.getElementById('combo-nombre').value.trim(),
            color: document.getElementById('combo-color').value
        };

        if (!isEdit) {
            // Datos extra solo para creación
            data.owner_nombre = document.getElementById('combo-owner-nombre').value.trim();
            data.owner_email = document.getElementById('combo-owner-email').value.trim();
            data.owner_pass = document.getElementById('combo-owner-pass').value.trim();
            data.owner_rol = document.getElementById('combo-owner-rol').value;
        } else {
            // Datos extra para edición (opcionales)
            const newEmail = document.getElementById('combo-owner-email').value.trim();
            const newPass = document.getElementById('combo-owner-pass').value.trim();
            
            if (newEmail) data.owner_email = newEmail;
            if (newPass) data.owner_pass = newPass;
            
            // En edición, permitimos actualizar el contacto/email personal
            data.contacto = document.getElementById('combo-contacto').value.trim();
        }

        // Siempre enviamos el contacto si está presente (para creación o edición)
        data.contacto = document.getElementById('combo-contacto').value.trim();

        if (!data.nombre) { alert('El nombre de la organización es requerido.'); return; }

        try {
            const url = isEdit ? `/api/ligas/${id}` : '/api/combos';
            const method = isEdit ? 'PUT' : 'POST';

            const res = await Core.fetchAPI(url, {
                method: method,
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(data)
            });

            if (res.success || res.id) {
                Core.showNotification(`Combo "${data.nombre}" ${isEdit ? 'actualizado' : 'creado'} correctamente`);
                Core.closeModal('modal-combo');
                await this.loadLigas();
                await this.loadUsers();
                
                if (!isEdit) {
                    // Redigir a pagos de combos solo en creación
                    this.switchTab('payments');

                    // Opcional: Ticket
                    setTimeout(() => {
                        if (confirm('Combo Creado. ¿Deseas imprimir el ticket con todas las credenciales y accesos?')) {
                            this.printComboTicket(res.liga, data, res.pago, res.cuentas);
                        }
                    }, 500);
                } else {
                    this.renderLinkedAccounts();
                }
            } else {
                alert('Error: ' + (res.error || 'No se pudo procesar la solicitud'));
            }
        } catch (err) {
            console.error('Error procesando combo:', err);
            alert('Error técnico al procesar el combo');
        }
    }

    async deleteCombo(id, nombre) {
        if (!confirm(`¿Estás seguro de que deseas eliminar el combo "${nombre}"?\nEsta acción eliminará la liga, sus canchas y usuarios asociados.`)) return;
        try {
            const res = await Core.fetchAPI(`/api/ligas/${id}`, { method: 'DELETE' });
            if (res.success) {
                Core.showNotification(`Combo "${nombre}" eliminado`);
                await this.loadLigas();
                await this.loadUsers();
                this.renderLinkedAccounts();
            }
        } catch (err) {
            console.error(err);
            alert('Error al eliminar combo');
        }
    }

    async toggleComboStatus(id, nombre, currentStatus) {
        const action = currentStatus ? 'inhabilitar' : 'reactivar';
        if (!confirm(`¿Deseas ${action} el combo "${nombre}"?\n${currentStatus ? 'Esto desactivará el acceso a todos los usuarios vinculados.' : 'Esto restaurará el acceso a los usuarios vinculados.'}`)) return;
        
        try {
            const res = await Core.fetchAPI(`/api/ligas/${id}`, {
                method: 'PUT',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ activa: !currentStatus })
            });

            if (res.id) {
                Core.showNotification(`Combo "${nombre}" ${currentStatus ? 'inhabilitado' : 'reactivado'}`);
                await this.loadLigas();
                await this.loadUsers();
                this.renderLinkedAccounts();
            }
        } catch (err) {
            console.error(err);
            alert('Error al cambiar estatus del combo');
        }
    }

    async printComboTicket(liga, owner, pago, cuentas = []) {
        // Redirigir al nuevo generador profesional PDF
        await this.downloadComboPaymentPDF(pago.id, { 
            isActivation: true, 
            cuentas: cuentas,
            ownerRol: owner.owner_rol 
        });
    }

    async printExpansionTicket(liga, field, delta, cost) {
        // Generar un objeto de pago ficticio para la expansión
        const pagoObj = {
            id: Date.now() % 10000,
            liga_id: liga.id,
            liga_nombre: liga.nombre,
            fecha: new Date().toLocaleDateString(),
            mes_pagado: field === 'extra_canchas' ? 'Sede Extra' : 'Torneo Extra',
            monto: Math.abs(delta) * cost,
            metodo: 'Ajuste de Plan',
            notas: `Expansión de ${Math.abs(delta)} ${field === 'extra_canchas' ? 'sede(s)' : 'torneo(s)'}.`
        };
        await this.downloadComboPaymentPDF(null, { 
            isExpansion: true, 
            customPago: pagoObj 
        });
    }

    async updateLigaExtras(ligaId, field, delta) {
        const cost = field === 'extra_canchas' ? 290 : 85;
        const type = field === 'extra_canchas' ? 'SEDE EXTRA' : 'LIGA/TORNEO EXTRA';
        
        try {
            const res = await Core.fetchAPI('/api/ligas/extras', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ liga_id: ligaId, field, delta })
            });

            if (res.success) {
                Core.showNotification(`Aumento de ${type} registrado.`);
                this.loadLigas();
                this.renderLinkedAccounts();

                // Proactivamente ofrecer registrar el pago para que salga en el corte diario
                if (confirm(`Aumento de ${type} registrado.\n¿Deseas registrar el pago de esta expansión ahora para que aparezca en el corte del día?\n(Recomendado: Añade "Crecimiento de paquete" en las notas)`)) {
                    this.showComboPaymentModal(ligaId);
                    // Pre-llenar notas y monto
                    setTimeout(() => {
                        const notes = document.getElementById('settings-pago-notas');
                        const monto = document.getElementById('settings-pago-monto');
                        if (notes) notes.value = `Crecimiento de paquete: ${type} (+${delta})`;
                        if (monto) monto.value = (Math.abs(delta) * cost).toFixed(2);
                    }, 500);
                }
            }
        } catch (err) {
            console.error(err);
            Core.showNotification('Error al actualizar extras', 'error');
        }
    }

    async loadLigas() {
        try {
            this.ligas = await Core.fetchAPI('/api/ligas') || [];
            const select = document.getElementById('user-liga-id');
            if (select) {
                select.innerHTML = '<option value="">-- Sin Liga Asignada (Global) --</option>' +
                    this.ligas.map(l => `<option value="${l.id}">${l.nombre}</option>`).join('');
            }
            return this.ligas;
        } catch (error) {
            console.error('Error al cargar ligas:', error);
            return [];
        }
    }

    async loadCanchas() {
        try {
            const res = await Core.fetchAPI('/api/canchas');
            this.canchas = res.items || res;
        } catch (error) {
            console.error('Error al cargar canchas:', error);
        }
    }

    async loadUsers() {
        try {
            this.users = await Core.fetchAPI('/api/users');
            this.renderUsers();
        } catch (error) {
            console.error('Error al cargar usuarios:', error);
            Core.showNotification('Error al cargar usuarios', 'error');
        }
    }

    renderUsers() {
        const container = document.getElementById('settings-users-list');
        if (!container) return;

        const mainUsers = this.users.filter(u => ['admin', 'ejecutivo'].includes(u.rol));

        if (mainUsers.length === 0) {
            container.innerHTML = `<tr><td colspan="5" style="text-align:center; padding: 4rem; color: var(--text-muted);">
                <div style="font-size: 3rem; margin-bottom: 1rem; opacity: 0.3;">👥</div>
                No hay usuarios de administración registrados.
            </td></tr>`;
            return;
        }

        const roleIcons = {
            'admin': '👨‍💻',
            'ejecutivo': '💼',
            'dueño_liga': '👑',
            'super_arbitro': '🚀',
            'arbitro': '⚖️',
            'entrenador': '📋',
            'equipo': '🛡️'
        };

        const roleNames = {
            'admin': 'Administrador',
            'ejecutivo': 'Ejecutivo (Soporte)',
            'dueño_liga': 'Dueño de Liga',
            'super_arbitro': 'Super Árbitro',
            'arbitro': 'Árbitro Gral.',
            'entrenador': 'Entrenador',
            'equipo': 'Equipo/Jugador',
            'dueno_cancha': 'Dueño de Sede',
            'resultados': 'Resultados (Solo Leo)'
        };

        container.innerHTML = mainUsers.map(u => {
            const ligaName = u.liga_id ? (this.ligas.find(l => l.id === u.liga_id)?.nombre || 'Liga ID: ' + u.liga_id) : 'Acceso Global';
            const statusClass = u.activo ? 'active' : 'inactive';
            const statusText = u.activo ? 'En Línea' : 'Desactivado';
            const initial = u.nombre.charAt(0).toUpperCase();
            const icon = roleIcons[u.rol] || '👤';
            const roleName = roleNames[u.rol] || u.rol.toUpperCase();
            
            return `
                <tr>
                    <td>
                        <div class="user-identity">
                            <div class="user-avatar" style="background: ${u.color ? `linear-gradient(135deg, ${u.color}, #000)` : 'linear-gradient(135deg, var(--primary), #00c864)'};">${initial}</div>
                            <div class="user-info-stack">
                                <span class="user-primary-name">${u.nombre}</span>
                                <span class="user-secondary-info">${u.email}</span>
                            </div>
                        </div>
                    </td>
                    <td>
                        <span class="badge-premium badge-${u.rol}">
                            ${icon} ${roleName}
                        </span>
                    </td>
                    <td>
                        <div style="display:flex; align-items:center; gap:8px; color: var(--text-muted); font-size: 0.9rem;">
                            <span style="width: 8px; height: 8px; border-radius: 50%; background: ${u.color || 'var(--primary)'}; box-shadow: 0 0 5px ${u.color || 'var(--primary)'};"></span>
                            ${ligaName}
                        </div>
                    </td>
                    <td>
                        <div class="status-pill">
                            <div class="status-dot-pulse ${statusClass}"></div>
                            ${statusText}
                        </div>
                    </td>
                    <td>
                        <div style="display:flex; gap:6px;">
                            <button class="btn-icon" onclick="ui.settings.editUser(${u.id})" title="Editar Perfil" 
                                style="background: rgba(255,255,255,0.05); width: 34px; height: 34px; border-radius: 8px; border: 1px solid var(--border); transition: 0.3s; display: flex; align-items: center; justify-content: center; font-size: 0.9rem;">
                                ✏️
                            </button>
                            <button class="btn-icon" onclick="ui.settings.toggleUserStatus(${u.id}, '${u.nombre.replace(/'/g, "\\'")}', ${u.activo})" 
                                title="${u.activo ? 'Bloquear Acceso' : 'Reactivar Acceso'}"
                                style="background: rgba(255,255,255,0.05); width: 34px; height: 34px; border-radius: 8px; border: 1px solid var(--border); transition: 0.3s; display: flex; align-items: center; justify-content: center; font-size: 0.9rem;">
                                ${u.activo ? '🚫' : '✅'}
                            </button>
                            <button class="btn-icon" onclick="ui.settings.deleteUser(${u.id})" title="Eliminar Permanente" 
                                style="background: rgba(255,68,68,0.1); width: 34px; height: 34px; border-radius: 8px; border: 1px solid rgba(255,68,68,0.2); color: #ff4444; transition: 0.3s; display: flex; align-items: center; justify-content: center; font-size: 0.9rem;">
                                🗑️
                            </button>
                        </div>
                    </td>
                </tr>
            `;
        }).join('');
    }

    switchTab(tabId) {
        // Update buttons
        document.querySelectorAll('.tab-btn').forEach(btn => {
            btn.classList.remove('active');
            btn.style.color = 'var(--text-muted)';
            btn.style.borderBottomColor = 'transparent';
        });
        
        const activeBtn = document.getElementById(`tab-btn-${tabId}`);
        if (activeBtn) {
            activeBtn.classList.add('active');
            activeBtn.style.color = 'var(--text)';
            activeBtn.style.borderBottomColor = 'var(--primary)';
        }

        // Update content
        document.querySelectorAll('.settings-tab-content').forEach(content => {
            content.style.display = 'none';
        });
        
        const activeTab = document.getElementById(`settings-tab-${tabId}`);
        const tabsNav = document.querySelector('.tabs-nav');
        if (activeTab) {
            activeTab.style.display = 'block';
            // Ocultar la barra de pestañas si el usuario entró directo a pagos desde el sidebar
            // Ocultar la barra de pestañas en 'payments', 'resumenes' y 'privacidad'
            if (tabsNav) {
                const hiddenTabs = ['payments', 'resumenes', 'privacidad'];
                tabsNav.style.display = hiddenTabs.includes(tabId) ? 'none' : 'flex';
            }
        }

        if (tabId === 'linked') {
            this.renderLinkedAccounts();
        } else if (tabId === 'payments') {
            this.loadLigas().then(() => this.loadComboPayments());
        } else if (tabId === 'resumenes') {
            this.ui.analytics.renderResumenes();
        } else if (tabId === 'privacidad') {
            this.ui.privacy.init();
        }
    }

    async updateLigaExtras(ligaId, field, delta) {
        if (!confirm(`¿Deseas modificar los espacios extra para esta organización?\nRecuerda que esto afecta la capacidad permitida.`)) return;
        
        const liga = this.ligas.find(l => l.id == ligaId);
        if (!liga) return;
        
        const current = liga[field] || 0;
        const newValue = Math.max(0, current + delta);
        
        try {
            const data = {};
            data[field] = newValue;
            
            const res = await Core.fetchAPI(`/api/ligas/${ligaId}/extras`, {
                method: 'PUT',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(data)
            });
            
            if (res.success) {
                Core.showNotification(`Expansión de ${field.replace('_', ' ')} exitosa`);
                
                // Calcular costo para el ticket
                const cost = field === 'extra_canchas' ? 290 : 85;
                this.printExpansionTicket(res.liga || liga, field, delta, cost);
                
                await this.ui.loadInitialStats(); // Actualizar límites globales
                await this.loadLigas();       // Actualizar datos de ligas
                this.renderLinkedAccounts();   // Refrescar tarjetas inmediatamente
                this.renderComboStatus();      // Refrescar tabla de pagos
            } else {
                alert('Error al actualizar espacios: ' + (res.error || 'Desconocido'));
            }
        } catch (err) {
            console.error(err);
            alert('Error técnico al actualizar extras');
        }
    }

    async loadComboPayments() {
        try {
            this.payments = await Core.fetchAPI('/api/combo-pagos');
            this.renderComboPayments();
            this.renderComboStatus();
            
            // Llenar el select de ligas en el modal de pagos si es admin
            const user = JSON.parse(localStorage.getItem('user') || '{}');
            const actions = document.getElementById('combo-payment-actions');
            const select = document.getElementById('settings-pago-liga-id');
            
            if (['admin', 'ejecutivo'].includes(user.rol)) {
                if (actions) actions.style.display = 'block';
            } else {
                if (actions) actions.style.display = 'none';
            }

            // Poblar select independientemente del rol si hay ligas cargadas
            if (select && this.ligas.length > 0) {
                select.innerHTML = this.ligas.map(l => `<option value="${l.id}">${l.nombre}</option>`).join('');
            }
        } catch (error) {
            console.error('Error al cargar pagos de combos:', error);
        }
    }

    renderComboPayments() {
        const container = document.getElementById('settings-combo-payments-list');
        if (!container) return;

        const searchTerm = document.getElementById('combo-payment-search')?.value.toLowerCase() || '';

        const filtered = this.payments.filter(p => 
            p.liga_nombre.toLowerCase().includes(searchTerm) || 
            p.mes_pagado.toLowerCase().includes(searchTerm) ||
            p.metodo.toLowerCase().includes(searchTerm)
        );

        if (filtered.length === 0) {
            container.innerHTML = `<tr><td colspan="6" style="text-align:center; padding: 3rem; color: var(--text-muted);">
                ${searchTerm ? 'No se encontraron pagos con ese criterio.' : 'No hay registros de pagos.'}
            </td></tr>`;
            return;
        }

        container.innerHTML = filtered.map(p => `
            <tr>
                <td>${p.fecha}</td>
                <td>
                    <div style="font-weight:600;">${p.liga_nombre}</div>
                    <div style="font-size:0.75rem; color:var(--text-muted);">${p.notas || ''}</div>
                </td>
                <td><span class="badge" style="background: rgba(0,255,136,0.1); color: #00ff88;">${p.mes_pagado || 'N/A'}</span></td>
                <td style="font-weight:700; color: #00ff88;">$${p.monto.toFixed(2)}</td>
                <td>${p.metodo}</td>
                <td>
                    ${p.comprobante_url ? `<a href="${p.comprobante_url}" target="_blank" class="btn-icon" title="Ver Comprobante">📄</a>` : '—'}
                </td>
            </tr>
        `).join('');
    }

    showComboPaymentModal(ligaId = null) {
        document.getElementById('combo-payment-form').reset();
        document.getElementById('settings-pago-meses').value = 1;
        const select = document.getElementById('settings-pago-liga-id');
        if (select && select.options.length === 0 && this.ligas.length > 0) {
            select.innerHTML = this.ligas.map(l => `<option value="${l.id}">${l.nombre}</option>`).join('');
        }

        if (ligaId) {
            if (select) {
                select.value = ligaId;
                this.updateComboPaymentTotal();
            }
        }
        Core.openModal('modal-combo-payment');
    }

    getMesEspanol(date) {
        const meses = ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"];
        return `${meses[date.getMonth()]} ${date.getFullYear()}`;
    }

    updateComboPaymentTotal() {
        const ligaId = document.getElementById('settings-pago-liga-id').value;
        const meses = parseInt(document.getElementById('settings-pago-meses').value) || 1;
        const montoInput = document.getElementById('settings-pago-monto');
        const conceptoInput = document.getElementById('settings-pago-mes');
        
        const liga = this.ligas.find(l => l.id == ligaId);
        if (liga) {
            const precioUnitario = liga.monto_total_mensual || liga.monto_mensual || 0;
            const total = precioUnitario * meses;
            montoInput.value = total.toFixed(2);
            
            // Generar concepto automático
            const now = new Date();
            const mesesList = [];
            for (let i = 0; i < meses; i++) {
                const d = new Date(now.getFullYear(), now.getMonth() + i, 1);
                mesesList.push(this.getMesEspanol(d));
            }
            
            if (meses === 1) {
                conceptoInput.value = mesesList[0];
            } else {
                conceptoInput.value = `${meses} meses (${mesesList[0]} - ${mesesList[meses-1]})`;
            }
        }
    }

    filterPaymentsByLiga(nombre) {
        const searchInput = document.getElementById('combo-payment-search');
        if (searchInput) {
            searchInput.value = nombre;
            this.renderComboPayments();
            // Scroll to payments table
            searchInput.scrollIntoView({ behavior: 'smooth', block: 'center' });
        }
    }

    async downloadComboPDF(ligaId) {
        const liga = this.ligas.find(l => l.id == ligaId);
        if (!liga) return;

        Core.showNotification('Cargando motor de reporte...', 'info');
        try {
            await Core.loadScript('https://cdnjs.cloudflare.com/ajax/libs/jspdf/2.5.1/jspdf.umd.min.js');
            const { jsPDF } = window.jspdf;
            const doc = new jsPDF();
            
            const primaryColor = [0, 255, 136]; // FutAdmin Green
            const textColor = [40, 40, 40];
            const secondaryTextColor = [100, 100, 100];
            const lightGray = [245, 245, 245];

            // 1. Cabecera Premium
            doc.setFillColor(30, 30, 30);
            doc.rect(0, 0, 210, 45, 'F');
            
            doc.setTextColor(255, 255, 255);
            doc.setFontSize(26);
            doc.setFont("helvetica", "bold");
            doc.text("FutAdmin PRO", 20, 25);
            
            doc.setFontSize(10);
            doc.setFont("helvetica", "normal");
            doc.text("ESTADO DE CUENTA Y RESUMEN OPERATIVO", 20, 32);
            doc.text(`ORGANIZACIÓN: ${liga.nombre.toUpperCase()}`, 20, 38);
            
            doc.setFontSize(10);
            doc.text(`Generado: ${new Date().toLocaleDateString()}`, 155, 25);
            doc.text(`ID Cliente: ${ligaId}`, 155, 32);

            let currentY = 55;

            // --- SECCIÓN 1: RESUMEN DE MEMBRESÍA ---
            doc.setTextColor(...textColor);
            doc.setFontSize(14);
            doc.setFont('helvetica', 'bold');
            doc.text('RESUMEN DE MEMBRESÍA', 20, currentY);
            doc.setDrawColor(...primaryColor);
            doc.setLineWidth(0.8);
            doc.line(20, currentY + 3, 190, currentY + 3);
            currentY += 12;

            doc.setFontSize(10);
            const col1 = 20, col2 = 65, col3 = 110, col4 = 155;

            // Datos de membresía
            const membership = [
                ["Organización:", liga.nombre, "Plan Actual:", liga.paquete.toUpperCase()],
                ["Vencimiento:", liga.vencimiento || 'Pendiente', "Registrado el:", liga.fecha_registro || 'N/A'],
                ["Meses Pagados:", `${liga.stats?.total_meses_pagados || 0} Mes(es)`, "Costo Mensual:", `$${(liga.monto_total_mensual || 0).toFixed(2)} MXN`]
            ];

            membership.forEach(row => {
                doc.setFont('helvetica', 'bold'); doc.text(row[0], col1, currentY);
                doc.setFont('helvetica', 'normal'); doc.text(row[1], col2, currentY);
                doc.setFont('helvetica', 'bold'); doc.text(row[2], col3, currentY);
                doc.setFont('helvetica', 'normal'); doc.text(row[3], col4, currentY);
                currentY += 7;
            });

            // --- SECCIÓN 2: DESGLOSE DE OPERACIÓN ---
            currentY += 8;
            doc.setFontSize(14);
            doc.setFont('helvetica', 'bold');
            doc.text('INFRAESTRUCTURA ACTIVA', 20, currentY);
            doc.line(20, currentY + 3, 190, currentY + 3);
            currentY += 12;

            doc.setFontSize(10);
            doc.setFont('helvetica', 'bold');
            doc.text(`Sedes en Sistema (${liga.stats?.canchas || 0}):`, col1, currentY);
            doc.text(`Ligas/Torneos Activos (${liga.stats?.torneos || 0}):`, col3, currentY);
            doc.setFont('helvetica', 'normal');
            
            let listY_Sedes = currentY + 6;
            (liga.detalles?.canchas || ["Ninguna registrada"]).forEach(c => {
                doc.text(`• ${c}`, col1 + 2, listY_Sedes);
                listY_Sedes += 5;
            });

            let listY_Torneos = currentY + 6;
            (liga.detalles?.torneos || ["Ninguna registrada"]).forEach(t => {
                doc.text(`• ${t}`, col3 + 2, listY_Torneos);
                listY_Torneos += 5;
            });

            currentY = Math.max(listY_Sedes, listY_Torneos) + 10;

            // --- SECCIÓN 3: MÉTRICAS DE USO ---
            doc.setFillColor(...lightGray);
            doc.rect(20, currentY, 170, 15, 'F');
            doc.setFont('helvetica', 'bold');
            doc.text('Impacto Operativo:', 25, currentY + 10);
            doc.setFont('helvetica', 'normal');
            doc.text(`${liga.stats?.equipos || 0} Equipos Inscritos`, 65, currentY + 10);
            doc.text(`${liga.stats?.jugadores || 0} Jugadores Registrados`, 125, currentY + 10);
            currentY += 28;

            // --- SECCIÓN 4: HISTORIAL DE APORTACIONES ---
            doc.setFontSize(14);
            doc.setFont('helvetica', 'bold');
            doc.text('HISTORIAL DE APORTACIONES', 20, currentY);
            doc.line(20, currentY + 3, 190, currentY + 3);
            currentY += 10;

            // Cabecera de Tabla
            doc.setFillColor(50, 50, 50);
            doc.rect(20, currentY, 170, 8, 'F');
            doc.setTextColor(255, 255, 255);
            doc.setFontSize(9);
            doc.text('FECHA', 25, currentY + 6);
            doc.text('CONCEPTO / MES', 60, currentY + 6);
            doc.text('MÉTODO', 130, currentY + 6);
            doc.text('MONTO (MXN)', 165, currentY + 6);

            let rowY = currentY + 14;
            doc.setTextColor(...textColor);
            
            const payments = (this.payments || []).filter(p => p.liga_id == ligaId);
            if (payments.length === 0) {
                doc.text('No se han registrado pagos históricos para esta organización.', 25, rowY);
            } else {
                payments.forEach((p) => {
                    if (rowY > 265) { doc.addPage(); rowY = 30; }
                    doc.setFont('helvetica', 'normal');
                    doc.text(p.fecha || '', 25, rowY);
                    doc.text(p.mes_pagado || '', 60, rowY);
                    doc.text(p.metodo || '', 130, rowY);
                    doc.setFont('helvetica', 'bold');
                    doc.text(`$${p.monto.toFixed(2)}`, 165, rowY);
                    doc.setDrawColor(230, 230, 230);
                    doc.setLineWidth(0.1);
                    doc.line(20, rowY + 2, 190, rowY + 2);
                    rowY += 10;
                });
            }

            // Footer Legal (Términos cortos)
            doc.setFontSize(8);
            doc.setTextColor(...secondaryTextColor);
            const legalSummary = "FutAdmin es un sistema de gestión deportiva. Los datos y fotos son responsabilidad de la organización. Sin reembolsos.";
            doc.text(legalSummary, 105, 280, { align: "center" });
            
            doc.setTextColor(0, 150, 80);
            doc.setFont("helvetica", "bold");
            doc.text("WWW.FUTADMIN.COM.MX", 105, 288, { align: "center" });

            doc.save(`Estado_Cuenta_FutAdmin_${liga.nombre.replace(/\s+/g, '_')}.pdf`);
            Core.showNotification('Estado de cuenta generado correctamente');
        } catch (error) {
            console.error('Error generating PDF:', error);
            Core.showNotification('Error al generar el PDF', 'error');
        }
    }

    async handleComboPaymentSubmit(e) {
        e.preventDefault();
        const data = {
            liga_id: document.getElementById('settings-pago-liga-id').value,
            monto: parseFloat(document.getElementById('settings-pago-monto').value),
            mes_pagado: document.getElementById('settings-pago-mes').value,
            cantidad_meses: parseInt(document.getElementById('settings-pago-meses').value) || 1,
            metodo: document.getElementById('settings-pago-metodo').value,
            comprobante_url: document.getElementById('settings-pago-comprobante').value,
            notas: document.getElementById('settings-pago-notas').value
        };

        if (!data.liga_id || isNaN(data.monto) || !data.mes_pagado) {
            alert('Por favor complete todos los datos obligatorios del pago.');
            return;
        }

        try {
            const result = await Core.fetchAPI('/api/combo-pagos', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(data)
            });

            if (result.success || result.id) {
                Core.showNotification('Aportación registrada correctamente');
                Core.closeModal('modal-combo-payment');
                
                await this.loadLigas(); // Recargar para actualizar montos y estatus de pago
                this.loadComboPayments(); // Recargar historial
                this.renderComboStatus(); // Actualizar tabla de estatus
                this.renderLinkedAccounts(); // Actualizar tarjetas (Cuentas Vinculadas)
                
                // Ofrecer ticket si no es un pago de expansión (que ya tuvo su ticket)
                // O si el usuario lo desea
                if ((result.pago || result.id) && confirm('¿Deseas imprimir el comprobante de esta aportación?')) {
                    const liga = this.ligas.find(l => l.id == data.liga_id);
                    const owner = {
                        owner_rol: liga ? liga.paquete : 'Dueño de Liga',
                        owner_email: liga ? liga.contacto : 'Sistema',
                        owner_pass: 'Confirmado'
                    };
                    const pagoObj = (result.id && result.liga_nombre) ? result : { ...data, id: result.id || 'NUEVO', liga_nombre: (liga ? liga.nombre : 'Organización'), fecha: new Date().toLocaleDateString() };
                    // Usar el nuevo generador profesional PDF
                    this.downloadComboPaymentPDF(pagoObj.id, { 
                        isActivation: false, 
                        customPago: pagoObj,
                        ownerRol: owner.owner_rol
                    });
                }
            } else {
                alert('Error: ' + (result.error || 'No se pudo guardar el pago'));
            }
        } catch (err) {
            console.error('Error al registrar pago:', err);
            alert('Error técnico al registrar pago');
        }
    }

    renderLinkedAccounts() {
        const container = document.getElementById('settings-linked-container');
        if (!container) return;

        // Reset container to used grid from settings.html
        container.style.display = 'grid';
        container.style.gridTemplateColumns = 'repeat(auto-fill, minmax(350px, 1fr))';
        container.style.gap = '1.5rem';
        container.style.width = '100%';
        container.style.padding = '0 5px';

        const combos = {};

        // 1. Initialize with Ligas
        this.ligas.forEach(l => {
            combos[l.id] = {
                id: l.id,
                nombre: l.nombre,
                color: l.color || '#0ea5e9',
                canchas: [],
                users: []
            };
        });

        // 2. Add Canchas to combos
        this.canchas.forEach(c => {
            const lid = c.liga_id;
            if (lid && combos[lid]) {
                combos[lid].canchas.push(c);
            } else if (lid) {
                // Forzar conversión a string por si acaso la clave es numérica
                const lidStr = String(lid);
                if (combos[lidStr]) {
                    combos[lidStr].canchas.push(c);
                } else {
                    // Si aún no se encuentra, registrar como fallback
                    combos[lid] = { id: lid, nombre: `Liga ID ${lid}`, color: '#0ea5e9', canchas: [c], users: [] };
                }
            }
        });

        // 3. Add Users to combos (Clients Only)
        this.users.forEach(u => {
            // Excluir Roles Internos (Administrador y Colaborador) de Cuentas Vinculadas
            if (['admin', 'ejecutivo'].includes(u.rol)) return;

            let lid = u.liga_id || (u.cancha_id ? this.canchas.find(c => c.id == u.cancha_id)?.liga_id : null);
            if (lid && combos[lid]) {
                combos[lid].users.push(u);
            } else {
                // Global / Unassigned
                if (!combos['global']) {
                    combos['global'] = { id: 'global', nombre: 'Acceso Global / Sin Combo', color: '#888', canchas: [], users: [] };
                }
                combos['global'].users.push(u);
            }
        });

        // 4. Add unassigned canchas
        this.canchas.forEach(c => {
            if (!c.liga_id) {
                if (!combos['global']) {
                    combos['global'] = { id: 'global', nombre: 'Acceso Global / Sin Combo', color: '#888', canchas: [], users: [] };
                }
                combos['global'].canchas.push(c);
            }
        });

        const rolIcon = { 'dueno_cancha': '🏠', 'arbitro': '⚖️', 'dueño_liga': '👑', 'entrenador': '📋', 'super_arbitro': '🚀', 'equipo': '🛡️', 'resultados': '👁️', 'admin': '👨‍💻', 'ejecutivo': '💼' };
        const rolLabel = { 'dueno_cancha': 'Dueño de Sede', 'arbitro': 'Árbitro Vinculado', 'dueño_liga': 'Dueño de Liga', 'entrenador': 'Entrenador', 'super_arbitro': 'Super Árbitro', 'equipo': 'Equipo / Acceso Gral', 'resultados': 'Solo Vista / Lector', 'admin': 'Administrador', 'ejecutivo': 'Colaborador' };

        const userCard = (u) => `
            <div style="display:flex; align-items:center; gap:12px; padding:10px 14px; background: rgba(255,255,255,0.03); border-radius:10px; border: 1px solid var(--border); position: relative; overflow: hidden;">
                <div style="position: absolute; left: 0; top: 0; bottom: 0; width: 3px; background: ${u.color || 'var(--primary)'}; opacity: 0.5;"></div>
                <div style="width:38px; height:38px; border-radius:10px; background: ${u.color ? `${u.color}22` : 'var(--primary-glow)'}; color:${u.color || 'var(--primary)'}; display:flex; align-items:center; justify-content:center; font-weight:bold; font-size:1rem; flex-shrink:0; border: 1px solid ${u.color ? `${u.color}44` : 'var(--border)'};">
                    ${u.nombre.charAt(0).toUpperCase()}
                </div>
                <div style="flex:1; min-width:0;">
                    <div style="font-weight:600; font-size:0.9rem; white-space:nowrap; overflow:hidden; text-overflow:ellipsis;" title="${u.nombre}">${u.nombre}</div>
                    <div style="font-size:0.75rem; color:var(--text-muted); white-space:nowrap; overflow:hidden; text-overflow:ellipsis;" title="${u.email}">${u.email}</div>
                </div>
                <span style="background: rgba(255,255,255,0.05); border: 1px solid var(--border); padding:2px 8px; border-radius:6px; font-size:0.65rem; white-space:nowrap;">
                    ${rolIcon[u.rol] || '👤'} ${rolLabel[u.rol] || u.rol}
                </span>
                ${window.USER_ROL !== 'resultados' && window.USER_ROL !== 'arbitro' ? `
                <button class="btn-icon" onclick="ui.settings.editUser(${u.id})" title="Editar Perfil" style="background: none; border: none; padding: 4px; font-size:1rem; color: var(--text-muted); cursor: pointer; transition: 0.3s;" onmouseover="this.style.color='var(--primary)'" onmouseout="this.style.color='var(--text-muted)'">✏️</button>
                <button class="btn-icon" onclick="ui.settings.deleteUser(${u.id})" title="Eliminar Acceso" style="background: none; border: none; padding: 4px; font-size:1rem; color: var(--text-muted); cursor: pointer; transition: 0.3s;" onmouseover="this.style.color='#ff4444'" onmouseout="this.style.color='var(--text-muted)'">🗑️</button>
                ` : ''}
            </div>`;

        const filterOrg = document.getElementById('linked-filter-org')?.value.toLowerCase() || '';
        const filterOwner = document.getElementById('linked-filter-owner')?.value.toLowerCase() || '';
        const filterVenue = document.getElementById('linked-filter-venue')?.value.toLowerCase() || '';

        let finalHtml = Object.values(combos).filter(combo => {
            const lid = combo.id;
            const ligaData = lid !== 'global' ? this.ligas.find(l => l.id == lid) : null;
            const pacote = ligaData?.paquete || (lid === 'global' ? '' : 'equipo');

            // Filtro por Organización o Plan
            if (filterOrg) {
                const matchesOrg = combo.nombre.toLowerCase().includes(filterOrg);
                const matchesPlan = pacote.toLowerCase().includes(filterOrg);
                if (!matchesOrg && !matchesPlan) return false;
            }

            // Filtro por Dueño
            if (filterOwner) {
                const hasOwnerMatch = combo.users.some(u => u.nombre.toLowerCase().includes(filterOwner));
                if (!hasOwnerMatch) return false;
            }

            // Filtro por Sede
            if (filterVenue) {
                const hasVenueMatch = combo.canchas.some(c => c.nombre.toLowerCase().includes(filterVenue));
                if (!hasVenueMatch) return false;
            }

            // Mantener lógica original de no mostrar combos vacíos (a menos que haya filtros activos que los incluyan? No, mejor mantener consistencia)
            return (combo.users.length > 0 || combo.canchas.length > 0);

        }).map(combo => {
            const lid = combo.id;
            const ligaData = lid !== 'global' ? this.ligas.find(l => l.id == lid) : null;
            
            const pacote = ligaData?.paquete || 'equipo';
            
            // El "dueño" o acceso principal depende del paquete/plan
            const duenoLigas = combo.users.filter(u => u.rol === pacote);
            
            // Los demás se reparten en staff o equipos, excluyendo al que ya es dueño/principal
            const staffRoles = ['super_arbitro', 'arbitro', 'entrenador', 'dueno_cancha'];
            const staffUsers = combo.users.filter(u => staffRoles.includes(u.rol) && u.rol !== pacote);
            
            const equipoUsers = combo.users.filter(u => u.rol === 'equipo' && u.rol !== pacote);
            const otherUsers = combo.users.filter(u => u.rol !== pacote && !staffRoles.includes(u.rol) && u.rol !== 'equipo');

            const hasDueno = combo.users.some(u => u.rol === pacote);
            const arbCount = combo.users.filter(u => ['super_arbitro','arbitro'].includes(u.rol)).length;
            const hasEquipo = combo.users.some(u => u.rol === 'equipo' || u.rol === 'dueno_cancha');
            
            const hasPayments = ligaData?.has_payments;
            const stats = ligaData?.stats || { usuarios: combo.users.length, canchas: combo.canchas.length, torneos: 0 };
            
            // Límites base según paquete para visualización
            const limitBaseTorneos = pacote === 'dueño_liga' ? 5 : (pacote === 'super_arbitro' ? 2 : 1);

            return `
                <div class="stat-card premium-card" style="border:1px solid var(--border); border-radius:24px; overflow:hidden; background: var(--card-bg); position: relative; height: 100%; display: flex; flex-direction: column;">
                    <div class="combo-indicator" style="background: ${combo.color};"></div>
                    
                    <!-- Header: Liga -->
                    <div style="padding:20px; background: ${combo.color}11; border-bottom:1px solid var(--border); display:flex; align-items:center; gap:15px;">
                        <div style="font-size:2rem; filter: drop-shadow(0 0 10px ${combo.color}44);">🏆</div>
                        <div style="flex: 1; min-width: 0;">
                            <div style="font-weight:800; font-size:1.1rem; color: ${combo.color}; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;">${combo.nombre}</div>
                            <div style="display: flex; align-items: center; gap: 8px; flex-wrap: wrap;">
                                <div style="font-size:0.65rem; color:var(--text-muted); text-transform: uppercase; letter-spacing: 0.5px; font-weight: 700;">PLAN: ${pacote.replace('_', ' ')}</div>
                                <div style="font-size:0.65rem; color:${combo.color}; text-transform: uppercase; letter-spacing: 0.5px; font-weight: 800; margin-left: 5px; background: ${combo.color}22; padding: 2px 6px; border-radius: 4px;">TOTAL: $${(ligaData?.monto_total_mensual || 0).toFixed(2)}</div>
                                ${!hasPayments && lid !== 'global' ? `<span class="badge" style="background: rgba(255,68,68,0.15); color: #ff4444; font-size: 0.55rem; padding: 1px 5px; border: 1px solid rgba(255,68,68,0.3);">⚠️ SIN PAGOS</span>` : ''}
                            </div>
                            <!-- Desglose de Extras -->
                            ${(ligaData?.extra_canchas > 0 || ligaData?.extra_torneos > 0) ? `
                            <div style="font-size:0.6rem; color:var(--text-muted); margin-top: 4px; display: flex; gap: 8px;">
                                ${ligaData?.extra_canchas > 0 ? `<span style="border-left: 2px solid ${combo.color}; padding-left: 4px;">+${ligaData.extra_canchas} Sedes (+$${(ligaData.extra_canchas * 290).toFixed(0)})</span>` : ''}
                                ${ligaData?.extra_torneos > 0 ? `<span style="border-left: 2px solid ${combo.color}; padding-left: 4px;">+${ligaData.extra_torneos} Ligas (+$${(ligaData.extra_torneos * 85).toFixed(0)})</span>` : ''}
                            </div>` : ''}
                        </div>
                        <div style="display:flex; gap:6px; align-items:center; flex-shrink: 0;">
                            ${window.USER_ROL !== 'resultados' && window.USER_ROL !== 'arbitro' ? `
                            <button onclick="ui.settings.editCombo(${lid})" title="Editar Organización"
                                style="width: 32px; height: 32px; padding: 0; border-radius: 8px; display: flex; align-items: center; justify-content: center; font-size: 0.9rem; background: rgba(255,255,255,0.08); border: 1px solid var(--border); cursor: pointer; color:var(--text); transition: 0.2s;">
                                ✏️
                            </button>
                            <button onclick="ui.settings.showUserModal('${lid}')" title="Añadir Cuenta"
                                style="width: 32px; height: 32px; padding: 0; border-radius: 8px; display: flex; align-items: center; justify-content: center; font-size: 1.1rem; background: ${combo.color}; box-shadow: 0 0 10px ${combo.color}44; border: none; cursor: pointer; color:#fff;">
                                +
                            </button>
                            ${lid !== 'global' ? `
                            <button onclick="ui.settings.toggleComboStatus(${lid}, '${combo.nombre.replace(/'/g, "\\'")}', ${ligaData?.activa})"
                                title="${ligaData?.activa ? 'Inhabilitar' : 'Reactivar'}"
                                style="width: 32px; height: 32px; padding: 0; border-radius: 8px; display: flex; align-items: center; justify-content: center; font-size: 0.9rem; background: rgba(255,255,255,0.05); border: 1px solid var(--border); cursor: pointer; color:${ligaData?.activa ? 'var(--text)' : '#ff4444'};">
                                ${ligaData?.activa ? '🚫' : '✅'}
                            </button>
                            <button onclick="ui.settings.deleteCombo(${lid}, '${combo.nombre.replace(/'/g, "\\'")}')"
                                title="Eliminar"
                                style="width: 32px; height: 32px; padding: 0; border-radius: 8px; display: flex; align-items: center; justify-content: center; font-size: 0.9rem; background: rgba(255,68,68,0.1); border: 1px solid rgba(255,68,68,0.2); cursor: pointer; color:#ff4444;">
                                🗑️
                            </button>` : ''}
                            ` : ''}
                        </div>
                    </div>

                    <!-- Métricas de Registro con Control de Extras -->
                    <div style="padding: 12px 20px; border-bottom: 1px solid var(--border); background: rgba(255,255,255,0.02); display: flex; justify-content: space-around; font-size: 0.8rem;">
                        <div style="display: flex; flex-direction: column; align-items: center; gap: 4px;">
                            <span style="font-size: 0.65rem; color: var(--text-muted); font-weight: 700;">USUARIOS</span>
                            <div style="font-weight: 700;">👤 ${stats.usuarios}</div>
                        </div>
                        
                        <div style="display: flex; flex-direction: column; align-items: center; gap: 4px;">
                            <span style="font-size: 0.65rem; color: var(--text-muted); font-weight: 700;">SEDES</span>
                            <div style="display: flex; align-items: center; gap: 6px;">
                                <div style="font-weight: 700;">🏟️ ${stats.canchas} / ${1 + (ligaData?.extra_canchas || 0)}</div>
                                ${lid !== 'global' ? `
                                <div style="display: flex; gap: 2px;">
                                    <button onclick="ui.settings.updateLigaExtras(${lid}, 'extra_canchas', -1)" style="width:18px; height:18px; border-radius:4px; border:1px solid var(--border); background:rgba(255,255,255,0.05); color:#fff; cursor:pointer; font-size:0.7rem; display:flex; align-items:center; justify-content:center;">-</button>
                                    <button onclick="ui.settings.updateLigaExtras(${lid}, 'extra_canchas', 1)" title="Añadir Sede Extra ($290)" style="width:18px; height:18px; border-radius:4px; border:1px solid var(--primary); background:var(--primary-glow); color:var(--primary); cursor:pointer; font-size:0.7rem; display:flex; align-items:center; justify-content:center; font-weight:bold;">+</button>
                                </div>` : ''}
                            </div>
                        </div>

                        <div style="display: flex; flex-direction: column; align-items: center; gap: 4px;">
                            <span style="font-size: 0.65rem; color: var(--text-muted); font-weight: 700;">LIGAS</span>
                            <div style="display: flex; align-items: center; gap: 6px;">
                                <div style="font-weight: 700;">⚽ ${stats.torneos} / ${limitBaseTorneos + (ligaData?.extra_torneos || 0)}</div>
                                ${lid !== 'global' ? `
                                <div style="display: flex; gap: 2px;">
                                    <button onclick="ui.settings.updateLigaExtras(${lid}, 'extra_torneos', -1)" style="width:18px; height:18px; border-radius:4px; border:1px solid var(--border); background:rgba(255,255,255,0.05); color:#fff; cursor:pointer; font-size:0.7rem; display:flex; align-items:center; justify-content:center;">-</button>
                                    <button onclick="ui.settings.updateLigaExtras(${lid}, 'extra_torneos', 1)" title="Añadir Liga Extra ($85)" style="width:18px; height:18px; border-radius:4px; border:1px solid var(--primary); background:var(--primary-glow); color:var(--primary); cursor:pointer; font-size:0.7rem; display:flex; align-items:center; justify-content:center; font-weight:bold;">+</button>
                                </div>` : ''}
                            </div>
                        </div>
                    </div>

                    <!-- Slots de Acceso del Plan - Solo relevantes al paquete -->
                    <div style="padding: 14px 20px; background: rgba(0,0,0,0.15); border-bottom: 1px solid var(--border); display:flex; gap:10px; align-items:stretch;">
                        ${(() => {
                            const slot = (icon, label, filled, color) => `
                                <div style="flex:1; display:flex; flex-direction:column; align-items:center; gap:4px; padding:8px 4px; border-radius:10px; background:${filled ? color+'18' : 'rgba(255,255,255,0.03)'}; border:1px solid ${filled ? color+'44' : 'var(--border)'}; transition:0.3s;">
                                    <span style="font-size:1.1rem;">${icon}</span>
                                    <span style="font-size:0.55rem; text-transform:uppercase; font-weight:800; color:${filled ? color : 'var(--text-muted)'}; letter-spacing:0.5px; text-align:center; line-height:1.2;">${label}</span>
                                    <div style="width:6px; height:6px; border-radius:50%; background:${filled ? color : 'rgba(255,255,255,0.15)'}; box-shadow:${filled ? '0 0 6px '+color : 'none'};"></div>
                                </div>`;
                            
                            const slots = [];
                            // Mostrar exclusivamente la insignia de la cuenta principal del paquete
                            if (pacote === 'dueño_liga') {
                                slots.push(slot('👑','Dueño Liga', hasDueno, combo.color));
                            } else if (pacote === 'super_arbitro') {
                                slots.push(slot('🚀','Super Árbitro', arbCount >= 1, combo.color));
                            } else {
                                slots.push(slot('🛡️','Equipo / Jugador', hasEquipo, combo.color));
                            }
                            
                            return slots.join('');
                        })()}
                    </div>

                    <div style="padding:20px; flex: 1; display: flex; flex-direction: column; gap: 20px;">
                        
                        <!-- Sedes vinculadas -->
                        <div>
                            <div style="font-size:0.7rem; color:var(--text-muted); text-transform:uppercase; font-weight:800; letter-spacing:1px; margin-bottom:10px; display: flex; align-items: center; justify-content: space-between;">
                                <div style="display: flex; align-items: center; gap: 8px;">
                                    <span style="color:${combo.color}">🏟️</span> Sedes Vinculadas
                                </div>
                                ${window.USER_ROL !== 'resultados' && window.USER_ROL !== 'arbitro' ? `
                                <button onclick="ui.canchas.showModal(null, '${lid}')" class="btn-icon" title="Añadir Sede a este Combo" style="background: none; border: none; padding: 0; font-size: 1.1rem; color: ${combo.color}; cursor: pointer;">+</button>
                                ` : ''}
                            </div>
                            <div style="display: flex; flex-wrap: wrap; gap: 8px;">
                                ${combo.canchas.map(c => `
                                    <div style="background: ${combo.color}15; color: ${combo.color}; border: 1px solid ${combo.color}33; padding: 6px 12px; border-radius: 10px; font-size: 0.85rem; font-weight: 700;">
                                        ${c.nombre}
                                    </div>
                                `).join('')}
                            </div>
                            ${combo.canchas.length === 0 ? `<div class="text-muted" style="font-size:0.75rem; font-style:italic; border:1px dashed var(--border); padding:8px; border-radius:8px; text-align:center;">Sin sedes vinculadas</div>` : ''}
                        </div>

                        <!-- Staff y Accesos -->
                        <div>
                            <!-- Dueños -->
                            <div style="font-size:0.7rem; color:var(--text-muted); text-transform:uppercase; font-weight:800; letter-spacing:1px; margin-bottom:8px; display: flex; align-items: center; justify-content: space-between;">
                                <span>Dueños / Acceso Principal</span>
                                ${window.USER_ROL !== 'resultados' && window.USER_ROL !== 'arbitro' ? `
                                <button onclick="ui.settings.showUserModal('${lid}', '${pacote}')" class="btn-icon" title="Añadir Dueño" style="background: none; border: none; padding: 0; font-size: 1.1rem; color: var(--text-muted); cursor: pointer;">+</button>
                                ` : ''}
                            </div>
                            <div style="display: flex; flex-direction: column; gap: 8px; margin-bottom: 20px;">
                                ${duenoLigas.map(userCard).join('')}
                                ${duenoLigas.length === 0 ? `<div class="text-muted" style="font-size:0.7rem; font-style:italic; opacity:0.6;">Sin dueños registrados</div>` : ''}
                            </div>

                            <!-- Staff Operativo -->
                            <div style="font-size:0.7rem; color:var(--text-muted); text-transform:uppercase; font-weight:800; letter-spacing:1px; margin-bottom:8px; display: flex; align-items: center; justify-content: space-between;">
                                <span>Staff Operativo</span>
                                ${window.USER_ROL !== 'resultados' && window.USER_ROL !== 'arbitro' ? `
                                <button onclick="ui.arbitros.showArbitroModal('${lid}')" class="btn-icon" title="Añadir Staff / Árbitro" style="background: none; border: none; padding: 0; font-size: 1.1rem; color: var(--text-muted); cursor: pointer;">+</button>
                                ` : ''}
                            </div>
                            <div style="display: flex; flex-direction: column; gap: 8px; margin-bottom: 20px;">
                                ${staffUsers.map(userCard).join('')}
                                ${staffUsers.length === 0 ? `<div class="text-muted" style="font-size:0.7rem; font-style:italic; opacity:0.6;">Sin personal operativo</div>` : ''}
                            </div>

                            <!-- Equipos / Delegados -->
                            <div style="font-size:0.7rem; color:var(--text-muted); text-transform:uppercase; font-weight:800; letter-spacing:1px; margin-bottom:8px; display: flex; align-items: center; justify-content: space-between;">
                                <span>Equipos / Delegados</span>
                                ${window.USER_ROL !== 'resultados' && window.USER_ROL !== 'arbitro' ? `
                                <button onclick="ui.settings.showUserModal('${lid}', 'equipo')" class="btn-icon" title="Añadir Equipo / Delegado" style="background: none; border: none; padding: 0; font-size: 1.1rem; color: var(--text-muted); cursor: pointer;">+</button>
                                ` : ''}
                            </div>
                            <div style="display: flex; flex-direction: column; gap: 8px; margin-bottom: 10px;">
                                ${equipoUsers.map(userCard).join('')}
                                ${equipoUsers.length === 0 ? `<div class="text-muted" style="font-size:0.7rem; font-style:italic; opacity:0.6;">Sin equipos vinculados</div>` : ''}
                            </div>

                            <!-- Otros -->
                            ${otherUsers.length > 0 ? `
                                <div style="font-size:0.7rem; color:var(--text-muted); text-transform:uppercase; font-weight:800; letter-spacing:1px; margin-bottom:8px;">Otros Accesos</div>
                                <div style="display: flex; flex-direction: column; gap: 8px;">
                                    ${otherUsers.map(userCard).join('')}
                                </div>
                            ` : ''}
                        </div>
                    </div>

                    <div style="padding: 12px 20px; background: rgba(0,0,0,0.1); border-top: 1px solid var(--border); font-size: 0.75rem; color: var(--text-muted); display: flex; justify-content: space-between; align-items: center;">
                        <span>${combo.users.length} cuentas vinculadas</span>
                        <div style="display:flex; gap:8px; align-items:center;">
                            <div style="width: 8px; height: 8px; border-radius: 50%; background: ${combo.color}; box-shadow: 0 0 10px ${combo.color};"></div>
                        </div>
                    </div>
                </div>
            `;
        }).join('');

        if (!finalHtml) {
            container.innerHTML = `
                <div style="grid-column: 1/-1; padding: 4rem; text-align: center;">
                    <div style="font-size: 3rem; margin-bottom: 1rem; opacity: 0.3;">🔗</div>
                    <h4 style="color: var(--text-muted);">Sin cuentas vinculadas</h4>
                    <p class="text-muted" style="font-size:0.9rem;">Al registrar una cancha, liga, equipo o personal con cuentas atadas, aparecerán aquí agrupadas.</p>
                </div>`;
        } else {
            container.innerHTML = finalHtml;
        }
    }

    showUserModal(ligaId = null, defaultRol = null) {
        document.getElementById('user-modal-title').innerText = 'Nuevo Usuario';
        document.getElementById('user-id').value = '';
        document.getElementById('user-form').reset();
        document.getElementById('user-activo').checked = true;
        
        if (ligaId !== null && ligaId !== undefined) {
            // El valor 'global' se traduce a "" para el select
            document.getElementById('user-liga-id').value = (ligaId === 'global' || ligaId === '') ? '' : ligaId;
        }

        // Si se especificó un rol (desde los botones + de sección), aplicarlo
        if (defaultRol) {
            document.getElementById('user-rol').value = defaultRol;
        } else if (ligaId && ligaId !== 'global') {
            // Si solo hay liga (botón + principal del combo), default es dueño_liga
            document.getElementById('user-rol').value = 'dueño_liga';
        }

        this.onRolChange();
        Core.openModal('modal-user');
    }

    editUser(userId) {
        const user = this.users.find(u => u.id === userId);
        if (!user) return;

        document.getElementById('user-modal-title').innerText = 'Editar Usuario';
        document.getElementById('user-id').value = user.id;
        document.getElementById('user-nombre').value = user.nombre;
        document.getElementById('user-email').value = user.email;
        document.getElementById('user-rol').value = user.rol;
        document.getElementById('user-liga-id').value = user.liga_id || '';
        document.getElementById('user-activo').checked = user.activo;
        document.getElementById('user-password').value = ''; // Password always empty on edit

        this.onRolChange();
        Core.openModal('modal-user');
    }

    onRolChange() {
        const rol = document.getElementById('user-rol').value;
        const ligaContainer = document.getElementById('user-liga-container');
        // Admin y Ejecutivo suelen ser globales (sin liga específica)
        // Los nuevos roles de gestión y usuarios finales deben estar ligados a una liga
        const rolesConLiga = ['arbitro', 'equipo', 'entrenador', 'dueño_liga', 'super_arbitro', 'resultados'];
        
        if (rolesConLiga.includes(rol)) {
            ligaContainer.style.display = 'block';
        } else {
            ligaContainer.style.display = 'none';
        }
    }

    async handleUserSubmit(e) {
        e.preventDefault();
        const id = document.getElementById('user-id').value;
        const data = {
            nombre: document.getElementById('user-nombre').value,
            email: document.getElementById('user-email').value,
            rol: document.getElementById('user-rol').value,
            liga_id: document.getElementById('user-liga-id').value || null,
            activo: document.getElementById('user-activo').checked,
            password: document.getElementById('user-password').value
        };

        if (!id && !data.password) {
            alert('La contraseña es requerida para nuevos usuarios.');
            return;
        }

        try {
            const method = id ? 'PUT' : 'POST';
            const url = id ? `/api/users/${id}` : '/api/users';
            
            const result = await Core.fetchAPI(url, {
                method: method,
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(data)
            });

            if (result.success) {
                Core.showNotification(id ? 'Usuario actualizado' : 'Usuario creado');
                Core.closeModal('modal-user');
                await this.loadUsers();
                await this.ui.loadInitialStats(); // Refresh limits
                
                // Refrescar la vista de cuentas vinculadas si estamos en esa pestaña
                if (document.getElementById('settings-tab-linked').style.display !== 'none') {
                    this.renderLinkedAccounts();
                }
            } else {
                alert('Error: ' + result.error);
            }
        } catch (error) {
            console.error('Error saving user:', error);
            alert('Error al guardar el usuario.');
        }
    }

    async deleteUser(userId) {
        const user = this.users.find(u => u.id === userId);
        if (!user) return;

        if (!confirm(`¿Estás seguro de que deseas eliminar permanentemente el acceso de "${user.nombre}"?\nEsta acción es irreversible.`)) return;

        try {
            const result = await Core.fetchAPI(`/api/users/${userId}`, { method: 'DELETE' });
            if (result.success) {
                Core.showNotification('Acceso eliminado correctamente');
                await this.loadUsers();
                if (window.FutAdminLimits) await this.ui.loadInitialStats(); // Refresh limits if applicable
                if (document.getElementById('settings-tab-linked').style.display !== 'none') {
                    this.renderLinkedAccounts();
                }
            } else {
                alert('Error: ' + result.error);
            }
        } catch (error) {
            console.error('Error deleting user:', error);
            alert('Error al eliminar el usuario.');
        }
    }

    async toggleUserStatus(userId, userName, currentStatus) {
        const action = currentStatus ? 'BLOQUEAR' : 'REACTIVAR';
        if (!confirm(`¿Deseas ${action} el acceso para "${userName}"?`)) return;

        try {
            const result = await Core.fetchAPI(`/api/users/${userId}`, {
                method: 'PUT',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ activo: !currentStatus })
            });

            if (result.success) {
                Core.showNotification(`Usuario ${currentStatus ? 'bloqueado' : 'reactivado'} correctamente`);
                await this.loadUsers();
                if (document.getElementById('settings-tab-linked').style.display !== 'none') {
                    this.renderLinkedAccounts();
                }
            } else {
                alert('Error: ' + result.error);
            }
        } catch (error) {
            console.error('Error toggling user status:', error);
            alert('Error al cambiar el estatus del usuario.');
        }
    }

    renderComboStatus() {
        const container = document.getElementById('settings-combo-status-list');
        if (!container) return;

        const statusFilter = document.getElementById('settings-combo-status-filter')?.value || 'all';
        const searchTerm = document.getElementById('combo-status-search')?.value.toLowerCase() || '';

        const now = new Date();
        const currentMonthSp = this.getMesEspanol(now).toLowerCase();
        const currentMonthEn = now.toLocaleString('en-US', { month: 'long', year: 'numeric' }).toLowerCase();

        // 1. Aplicar Filtros
        let filtered = this.ligas.filter(l => {
            // Filtro por texto
            const matchesSearch = l.nombre.toLowerCase().includes(searchTerm) || 
                                 l.paquete.toLowerCase().includes(searchTerm);
            if (!matchesSearch) return false;

            // Filtro por estatus
            if (statusFilter === 'all') return true;
            
            const hasPayments = l.ultimo_pago && l.ultimo_pago.mes;
            const mesPagado = hasPayments ? l.ultimo_pago.mes.toLowerCase() : "";
            const isPaid = hasPayments && (
                mesPagado.includes(currentMonthSp) || 
                mesPagado.includes(currentMonthEn) ||
                mesPagado.includes("marzo")
            );
            return statusFilter === 'pending' ? !isPaid : isPaid;
        });

        // 2. Paginación
        const limit = parseInt(document.getElementById('settings-combo-status-limit')?.value) || this.statusLimit;
        this.statusLimit = limit;

        const totalItems = filtered.length;
        const totalPages = Math.ceil(totalItems / limit);
        if (this.statusPage > totalPages && totalPages > 0) this.statusPage = totalPages;
        
        const start = (this.statusPage - 1) * limit;
        const paginated = filtered.slice(start, start + limit);

        // 3. Renderizar Contenido
        if (paginated.length === 0) {
            container.innerHTML = `<tr><td colspan="6" style="text-align:center; padding: 2rem;">No hay organizaciones que coincidan con los criterios.</td></tr>`;
            this.renderPagination('settings-combo-status-pagination', 0, 0, 'status');
            return;
        }

        container.innerHTML = paginated.map(l => {
            // Calcular consumo del mes basado en el vencimiento cumulative
            let consumptionHtml = '';
            let isPaid = false;
            
            if (l.vencimiento) {
                const vencimientoDate = new Date(l.vencimiento + 'T23:59:59'); // Asegurar fin de día
                const diffTime = vencimientoDate - now;
                const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
                
                isPaid = diffDays > 0;
                
                // El porcentaje ahora es sobre un mes (30 días) para la barra visual, 
                // pero si tiene más de 30 días, se ve llena.
                const percent = Math.min(Math.max(Math.round(((30 - diffDays) / 30) * 100), 0), 100);
                
                // Color según urgencia (días restantes)
                let color = '#22c55e'; // Green
                if (diffDays <= 0) color = '#f43f5e'; // Red (Vencido)
                else if (diffDays <= 5) color = '#eab308'; // Yellow (Cerca)

                consumptionHtml = `
                    <div style="width: 100%; max-width: 120px; height: 6px; background: rgba(255,255,255,0.05); border-radius: 10px; margin-top: 6px; overflow: hidden; border: 1px solid rgba(255,255,255,0.05);">
                        <div style="width: ${100 - (diffDays > 30 ? 0 : percent)}%; height: 100%; background: ${color}; box-shadow: 0 0 10px ${color}44; transition: 0.5s;"></div>
                    </div>
                    <div style="font-size: 0.6rem; color: ${diffDays <= 0 ? '#f43f5e' : 'var(--text-muted)'}; margin-top: 2px; font-weight: ${diffDays <= 5 ? 'bold' : 'normal'}">
                        ${diffDays <= 0 ? 'Vencido' : `Vence en ~${diffDays} días`}
                    </div>
                `;
            }
            
            const isLate = !isPaid;

            return `
                <tr>
                    <td>
                        <div style="display:flex; align-items:center; gap:10px;">
                            <div style="width:10px; height:10px; border-radius:50%; background:${l.color};"></div>
                            <span style="font-weight:600;">${l.nombre}</span>
                        </div>
                    </td>
                    <td><span class="badge" style="background:rgba(255,255,255,0.05); color:var(--text);">${l.paquete}</span></td>
                    <td>
                        <div style="font-weight:700; color: #00ff88; font-size: 1rem;">$${(l.monto_total_mensual || 0).toFixed(2)}</div>
                        <div style="font-size: 0.65rem; color: var(--text-muted); margin-top: 4px; line-height: 1.2;">
                            <div>Base: $${(l.monto_mensual || 0).toFixed(2)}</div>
                            ${(l.expansiones || []).map(e => `
                                <div style="color: #eab308;">
                                    + ${e.cantidad} ${e.tipo === 'extra_canchas' ? 'Sede' : 'Liga'} 
                                    ($${e.monto_adicional.toFixed(2)}) 
                                    <span style="opacity:0.6; font-size: 0.6rem;">• ${e.fecha.split(' ')[0]}</span>
                                </div>
                            `).join('')}
                        </div>
                    </td>
                    <td>
                        <div style="font-size:0.85rem; font-weight:500;">${l.ultimo_pago ? l.ultimo_pago.mes : '<span style="color:var(--danger);">Sin Registros</span>'}</div>
                        ${l.ultimo_pago && l.ultimo_pago.fecha ? `<div style="font-size:0.7rem; color:var(--text-muted);">${l.ultimo_pago.fecha}</div>` : ''}
                        ${consumptionHtml}
                    </td>
                    <td>
                        <span class="status-pill ${isLate ? 'inactive' : 'active'}" style="padding: 4px 12px; border-radius: 20px; font-size: 0.75rem; display: inline-flex; align-items: center; gap: 6px;">
                            <div class="status-dot-pulse ${isLate ? 'inactive' : 'active'}"></div>
                            ${isLate ? 'PENDIENTE' : 'AL CORRIENTE'}
                        </span>
                    </td>
                    <td style="text-align: right;">
                        <div style="display: flex; gap: 6px; justify-content: flex-end;">
                            ${window.USER_ROL !== 'resultados' && window.USER_ROL !== 'arbitro' ? `
                            <button onclick="ui.settings.showComboPaymentModal('${l.id}')" class="btn-icon" title="Registrar Aportación / Contribución" style="background: rgba(0,255,136,0.1); color: #00ff88; border: 1px solid rgba(0,255,136,0.2); width: 30px; height: 30px; border-radius: 8px; cursor: pointer;">✚</button>
                            ` : ''}
                            <button onclick="ui.settings.downloadComboPDF('${l.id}')" class="btn-icon" title="Descargar Historial PDF" style="background: rgba(255,255,255,0.05); color: var(--text); border: 1px solid var(--border); width: 30px; height: 30px; border-radius: 8px; cursor: pointer;">📄</button>
                            ${window.USER_ROL !== 'resultados' && window.USER_ROL !== 'arbitro' ? `
                            <button onclick="ui.settings.filterPaymentsByLiga('${l.nombre}')" class="btn-icon" title="Ver Historial en pantalla" style="background: rgba(255,255,255,0.05); color: var(--text); border: 1px solid var(--border); width: 30px; height: 30px; border-radius: 8px; cursor: pointer;">📋</button>
                            <button onclick="ui.settings.deleteCombo(${l.id}, '${l.nombre.replace(/'/g, "\\'")}')" class="btn-icon" title="Eliminar Combo" style="background: rgba(239,68,68,0.1); color: #ef4444; border: 1px solid rgba(239,68,68,0.2); width: 30px; height: 30px; border-radius: 8px; cursor: pointer;">🗑️</button>
                            ` : ''}
                        </div>
                    </td>
                </tr>
            `;
        }).join('');

        this.renderPagination('settings-combo-status-pagination', this.statusPage, totalPages, 'status');
    }

    renderComboPayments() {
        const container = document.getElementById('settings-combo-payments-list');
        if (!container) return;

        const searchTerm = document.getElementById('combo-payment-search')?.value.toLowerCase() || '';
        const methodFilter = document.getElementById('settings-combo-payments-filter')?.value || 'all';

        const filtered = this.payments.filter(p => {
            const matchesSearch = p.liga_nombre.toLowerCase().includes(searchTerm) || 
                                p.mes_pagado.toLowerCase().includes(searchTerm) ||
                                p.metodo.toLowerCase().includes(searchTerm);
            const matchesMethod = methodFilter === 'all' || p.metodo === methodFilter;
            return matchesSearch && matchesMethod;
        });

        // Paginación
        const limit = parseInt(document.getElementById('settings-combo-payments-limit')?.value) || this.paymentsLimit;
        this.paymentsLimit = limit;

        const totalItems = filtered.length;
        const totalPages = Math.ceil(totalItems / limit);
        if (this.paymentsPage > totalPages && totalPages > 0) this.paymentsPage = totalPages;

        const start = (this.paymentsPage - 1) * limit;
        const paginated = filtered.slice(start, start + limit);

        if (paginated.length === 0) {
            container.innerHTML = `<tr><td colspan="6" style="text-align:center; padding: 3rem; color: var(--text-muted);">
                ${searchTerm ? 'No se encontraron pagos con ese criterio.' : 'No hay registros de pagos.'}
            </td></tr>`;
            this.renderPagination('settings-combo-payments-pagination', 0, 0, 'payments');
            return;
        }

        container.innerHTML = paginated.map(p => `
            <tr>
                <td>${p.fecha}</td>
                <td>
                    <div style="font-weight:600;">${p.liga_nombre}</div>
                    <div style="font-size:0.75rem; color:var(--text-muted);">${p.notas || ''}</div>
                </td>
                <td><span class="badge" style="background: rgba(0,255,136,0.1); color: #00ff88;">${p.mes_pagado || 'N/A'}</span></td>
                <td style="font-weight:700; color: #00ff88;">$${p.monto.toFixed(2)}</td>
                <td>${p.metodo}</td>
                <td>
                    <div style="display: flex; gap: 8px; justify-content: flex-end;">
                        ${p.comprobante_url ? `<a href="${p.comprobante_url}" target="_blank" class="btn-icon" title="Ver Comprobante">📄</a>` : ''}
                        <button onclick="ui.settings.downloadComboPaymentPDF(${p.id})" class="btn-icon" title="Imprimir Recibo" style="background: rgba(255,255,255,0.05); color: var(--text); border: 1px solid var(--border); width: 30px; height: 30px; border-radius: 8px; cursor: pointer;">🖨️</button>
                        <button onclick="ui.settings.editComboPayment(${p.id})" class="btn-icon" title="Editar" style="background: rgba(255,255,255,0.05); color: var(--text); border: 1px solid var(--border); width: 30px; height: 30px; border-radius: 8px; cursor: pointer;">✏️</button>
                        <button onclick="ui.settings.confirmDeleteComboPayment(${p.id})" class="btn-icon" title="Eliminar" style="background: rgba(239,68,68,0.1); color: #ef4444; border: 1px solid rgba(239,68,68,0.2); width: 30px; height: 30px; border-radius: 8px; cursor: pointer;">🗑️</button>
                    </div>
                </td>
            </tr>
        `).join('');

        this.renderPagination('settings-combo-payments-pagination', this.paymentsPage, totalPages, 'payments');
    }

    renderPagination(containerId, currentPage, totalPages, type) {
        const container = document.getElementById(containerId);
        if (!container) return;

        if (totalPages <= 1) {
            container.innerHTML = '';
            return;
        }

        container.innerHTML = `
            <div class="pagination-controls" style="display: flex; justify-content: center; align-items: center; gap: 15px; margin-top: 1rem;">
                <button class="btn-pagination" ${currentPage <= 1 ? 'disabled' : ''} 
                    onclick="ui.settings.changePage('${type}', ${currentPage - 1})"
                    style="background: rgba(255,255,255,0.05); border: 1px solid var(--border); color: var(--text); padding: 5px 12px; border-radius: 6px; cursor: ${currentPage <= 1 ? 'not-allowed' : 'pointer'}; opacity: ${currentPage <= 1 ? '0.5' : '1'};">
                    Anterior
                </button>
                <span class="pagination-info" style="font-size: 0.9rem; color: var(--text-muted);">
                    Página <b>${currentPage}</b> de ${totalPages}
                </span>
                <button class="btn-pagination" ${currentPage >= totalPages ? 'disabled' : ''} 
                    onclick="ui.settings.changePage('${type}', ${currentPage + 1})"
                    style="background: rgba(255,255,255,0.05); border: 1px solid var(--border); color: var(--text); padding: 5px 12px; border-radius: 6px; cursor: ${currentPage >= totalPages ? 'not-allowed' : 'pointer'}; opacity: ${currentPage >= totalPages ? '0.5' : '1'};">
                    Siguiente
                </button>
            </div>
        `;
    }

    changePage(type, page) {
        if (type === 'status') {
            this.statusPage = page;
            this.renderComboStatus();
        } else if (type === 'payments') {
            this.paymentsPage = page;
            this.renderComboPayments();
        }
    }

    updateItemsPerPage(value) {
        const limit = parseInt(value);
        // Identificar qué tabla refrescar basándose en el tab activo o el ID del select que disparó
        // Como ambos llaman a la misma función, refrescamos ambos o el que esté visible
        const activeTab = document.querySelector('.settings-tab-content:not([style*="display: none"])');
        
        if (activeTab && activeTab.id === 'settings-tab-payments') {
            // Estamos en la pestaña de pagos, pero dentro del mismo tab están ambas tablas
            // Generalmente, el usuario cambia el de la tabla que está viendo
            this.statusPage = 1;
            this.paymentsPage = 1;
            this.renderComboStatus();
            this.renderComboPayments();
        }
    }

    // --- Acciones de Historial ---

    editComboPayment(pagoId) {
        const pago = this.payments.find(p => p.id == pagoId);
        if (!pago) return;

        document.getElementById('edit-pago-id').value = pago.id;
        document.getElementById('edit-pago-liga-nombre').value = pago.liga_nombre;
        document.getElementById('edit-pago-meses').value = pago.cantidad_meses || 1;
        document.getElementById('edit-pago-monto').value = pago.monto;
        document.getElementById('edit-pago-mes').value = pago.mes_pagado;
        document.getElementById('edit-pago-metodo').value = pago.metodo;
        document.getElementById('edit-pago-comprobante').value = pago.comprobante_url || '';
        document.getElementById('edit-pago-notas').value = pago.notas || '';

        Core.openModal('modal-edit-combo-payment');
    }

    async handleEditComboPaymentSubmit(e) {
        e.preventDefault();
        const id = document.getElementById('edit-pago-id').value;
        const data = {
            monto: parseFloat(document.getElementById('edit-pago-monto').value),
            cantidad_meses: parseInt(document.getElementById('edit-pago-meses').value),
            mes_pagado: document.getElementById('edit-pago-mes').value,
            metodo: document.getElementById('edit-pago-metodo').value,
            comprobante_url: document.getElementById('edit-pago-comprobante').value,
            notas: document.getElementById('edit-pago-notas').value
        };

        try {
            await Core.fetchAPI(`/api/combo-pagos/${id}`, {
                method: 'PUT',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(data)
            });
            Core.showNotification('Aportación actualizada correctamente');
            Core.closeModal('modal-edit-combo-payment');
            await this.loadLigas(); // Recargar para ver cambios en estatus si aplica
            this.renderComboStatus();
            this.renderComboPayments();
        } catch (error) {
            Core.showNotification(error.message, 'error');
        }
    }

    async confirmDeleteComboPayment(pagoId) {
        const password = prompt('Esta acción requiere confirmación del Administrador General.\n\nPor favor, introduce tu contraseña para eliminar esta aportación:');
        if (!password) return;

        try {
            // 1. Verificar contraseña
            const verify = await Core.fetchAPI('/api/admin/verify-password', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ password })
            });

            if (!verify.success) {
                Core.showNotification('Contraseña incorrecta o no autorizado', 'error');
                return;
            }

            // 2. Proceder a eliminar
            if (!confirm('¿Estás seguro de que deseas eliminar permanentemente esta aportación?')) return;

            await Core.fetchAPI(`/api/combo-pagos/${pagoId}`, { method: 'DELETE' });
            Core.showNotification('Aportación eliminada correctamente');
            
            await this.loadLigas();
            this.renderComboStatus();
            this.renderComboPayments();
        } catch (error) {
            Core.showNotification(error.message, 'error');
        }
    }

    async downloadComboPaymentPDF(pagoId, options = {}) {
        let pago = options.customPago;
        if (!pago && pagoId) {
            pago = this.payments.find(p => p.id == pagoId);
        }
        if (!pago) return;

        Core.showNotification('Generando comprobante profesional...', 'info');
        
        try {
            await Core.loadScript('https://cdnjs.cloudflare.com/ajax/libs/jspdf/2.5.1/jspdf.umd.min.js');
            const { jsPDF } = window.jspdf;
            const doc = new jsPDF();
            const primaryColor = [0, 255, 136]; // FutAdmin Green
            const textColor = [40, 40, 40];
            const secondaryTextColor = [100, 100, 100];

            // Buscar la liga asociada para info extendida
            const liga = this.ligas.find(l => l.id == pago.liga_id) || {};

            // 1. Cabecera Premium
            doc.setFillColor(30, 30, 30);
            doc.rect(0, 0, 210, 45, 'F');
            
            doc.setTextColor(255, 255, 255);
            doc.setFontSize(26);
            doc.setFont("helvetica", "bold");
            doc.text("FutAdmin PRO", 20, 25);
            
            doc.setFontSize(10);
            doc.setFont("helvetica", "normal");
            doc.text("SISTEMA DE GESTIÓN DEPORTIVA INTEGRAL", 20, 32);
            
            const title = options.isActivation ? "ACTA DE ACTIVACIÓN DE SERVICIOS" : 
                         (options.isExpansion ? "COMPROBANTE DE EXPANSIÓN" : "COMPROBANTE OFICIAL DE APORTACIÓN");
            doc.text(title, 20, 38);
            
            doc.setFontSize(12);
            doc.text(`Folio: #CP-${pago.id.toString().padStart(5, '0')}`, 155, 25);
            doc.setFontSize(10);
            doc.text(`ID Cliente: ${pago.liga_id}`, 155, 32);

            // 2. Sección: Detalles
            doc.setTextColor(...textColor);
            doc.setFontSize(14);
            doc.setFont("helvetica", "bold");
            doc.text("DETALLES DE LA OPERACIÓN", 20, 60);
            doc.setDrawColor(...primaryColor);
            doc.setLineWidth(0.8);
            doc.line(20, 63, 190, 63);

            let currentY = 72;
            doc.setFontSize(11);
            const transDetails = [
                ["Organización / Combo:", pago.liga_nombre],
                ["Fecha de Operación:", pago.fecha],
                ["Concepto:", pago.mes_pagado],
                ["Método de Pago:", pago.metodo],
                ["Monto Total:", `$${(pago.monto || 0).toFixed(2)} MXN`],
                ["Estado:", "VERIFICADO Y ACTIVADO"]
            ];

            // Inyectar Email Personal si está presente
            if (liga.contacto) {
                transDetails.splice(1, 0, ["Email de Contacto:", liga.contacto]);
            }

            transDetails.forEach(row => {
                doc.setFont("helvetica", "bold");
                doc.text(String(row[0] || ''), 25, currentY);
                doc.setFont("helvetica", "normal");
                doc.text(String(row[1] || ''), 85, currentY);
                currentY += 8;
            });

            // 3. Sección: Información del Plan y Capacidad 
            currentY += 10;
            doc.setFont("helvetica", "bold");
            doc.setFontSize(14);
            doc.text("CAPACIDAD Y DETALLES DEL PLAN", 20, currentY);
            doc.line(20, currentY + 3, 190, currentY + 3);
            currentY += 12;

            const limits = {
                'dueno_liga': { u: 4, s: 1, t: 5 },
                'super_arbitro': { u: 4, s: 1, t: 2 },
                'equipo': { u: 4, s: 1, t: 1 }
            };
            const pName = (options.ownerRol || liga.paquete || 'dueño_liga').toLowerCase().replace(' ', '_');
            const base = limits[pName] || limits['dueno_liga'];
            const capUsers = base.u;
            const capSedes = base.s + (liga.extra_canchas || 0);
            const capTorneos = base.t + (liga.extra_torneos || 0);

            doc.setFontSize(11);
            const planDetails = [
                ["Paquete Suscrito:", (options.ownerRol || liga.paquete || "Dueño de Liga").toUpperCase()],
                ["Capacidad Usuarios:", `${capUsers} Cuentas Administrativas`],
                ["Capacidad Sedes:", `${capSedes} Sede(s) Activa(s)`],
                ["Capacidad Torneos:", `${capTorneos} Torneo(s) Simultáneo(s)`],
                ["Vigencia Estimada:", `${liga.vencimiento || 'Al Corriente'}`]
            ];

            planDetails.forEach(row => {
                doc.setFont("helvetica", "bold");
                doc.text(row[0], 25, currentY);
                doc.setFont("helvetica", "normal");
                doc.text(row[1], 85, currentY);
                currentY += 8;
            });

            // 4. Sección: Credenciales y Cuentas (NUEVO / REFINADO)
            currentY += 10;
            doc.setFillColor(245, 255, 250); // Lichte groen
            doc.rect(20, currentY, 170, options.cuentas?.length > 0 ? (20 + options.cuentas.length * 10) : 35, 'F');
            doc.setDrawColor(200, 230, 200);
            doc.rect(20, currentY, 170, options.cuentas?.length > 0 ? (20 + options.cuentas.length * 10) : 35, 'S');

            doc.setFont("helvetica", "bold");
            doc.text("Accesos Habilitados:", 25, currentY + 10);
            doc.setFont("helvetica", "normal");
            doc.setFontSize(10);
            
            if (options.cuentas && options.cuentas.length > 0) {
                options.cuentas.forEach((c, i) => {
                    doc.text(`${c.rol.toUpperCase()}: ${c.email}`, 25, currentY + 18 + (i * 8));
                });
                currentY += (options.cuentas.length * 8) + 12;
            } else {
                doc.text(`Email de Contacto: ${liga.contacto || 'Confirmado'}`, 25, currentY + 18);
                doc.text(`Contraseña Genérica: admin123`, 25, currentY + 26);
                currentY += 35;
            }

            // 5. Expansión y Mejoras
            currentY += 10;
            doc.setFontSize(11);
            doc.setFont("helvetica", "bold");
            doc.text("¿Necesitas más capacidad?", 20, currentY);
            doc.setFont("helvetica", "normal");
            doc.setFontSize(9);
            doc.text("Puedes añadir Sedes ($290) o Ligas ($85) extras directamente desde tu panel de Ajustes.", 20, currentY + 6);
            currentY += 15;

            // 6. Términos y Condiciones
            if (currentY > 210) {
                doc.addPage();
                currentY = 25; // Reiniciar Y en nueva página
                
                // Opcional: Mini cabecera en pág 2
                doc.setFillColor(30, 30, 30);
                doc.rect(0, 0, 210, 15, 'F');
                doc.setTextColor(255, 255, 255);
                doc.setFontSize(10);
                doc.text(`CONTINUACIÓN - RECIBO ${pago.liga_nombre.toUpperCase()}`, 20, 10);
                currentY += 15;
            }

            currentY += 5;
            doc.setTextColor(...secondaryTextColor);
            doc.setFontSize(10);
            doc.setFont("helvetica", "bold");
            doc.text("TÉRMINOS, CONDICIONES Y RESPONSABILIDADES:", 20, currentY);
            doc.setFont("helvetica", "normal");
            doc.setFontSize(8.5);
            const legalText = [
                "• FutAdmin es un sistema de gestión y control administrativo, no interviene en la organización física de los eventos deportivos ni en la logística de los mismos.",
                "• RESPONSABILIDAD DE DATOS (FOTOS DE MENORES): El Administrador de la Liga es el único responsable legal por el uso y publicación de imágenes y datos de menores de edad. FutAdmin recomienda contar con el consentimiento expreso de padres/tutores para el uso en la sección de Liguilla o perfiles públicos.",
                "• POLÍTICA DE CANCELACIÓN: El servicio puede darse de baja en cualquier momento notificando a soporte técnico. Los pagos realizados por periodos ya iniciados o activaciones no son reembolsables.",
                "• CREDENCIALES: Se recomienda encarecidamente cambiar la contraseña inicial tras el primer ingreso para garantizar la integridad de su información."
            ];
            
            legalText.forEach((line) => {
                const splitLine = doc.splitTextToSize(line, 170);
                if (currentY + (splitLine.length * 5) > 280) {
                    doc.addPage();
                    currentY = 25;
                }
                doc.text(splitLine, 20, currentY + 5);
                currentY += (splitLine.length * 4.5) + 2;
            });

            // Footer Final
            doc.setFontSize(9);
            doc.setTextColor(0, 150, 80);
            doc.setFont("helvetica", "bold");
            doc.text("WWW.FUTADMIN.COM.MX - EL CONTROL TOTAL DE TU LIGA", 105, 285, { align: "center" });

            const fileName = options.isActivation ? `Acta_Activacion_${pago.liga_nombre.replace(/\s+/g, '_')}.pdf` : 
                             `Recibo_FutAdmin_${pago.liga_nombre.replace(/\s+/g, '_')}_${pago.mes_pagado.replace(/\s+/g, '_')}.pdf`;
            doc.save(fileName);
            Core.showNotification('Documento profesional generado');
        } catch (error) {
            console.error(error);
            Core.showNotification('Error al crear PDF: ' + error.message, 'error');
        }
    }
}
