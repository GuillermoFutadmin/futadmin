import { Core } from './core.js';

export class PagosCanchasModule {
    constructor(ui) {
        this.ui = ui;
        this.estadosCuenta = [];
    }

    async loadEstadosCuenta() {
        const container = document.getElementById('pagos-canchas-container');
        if (!container) return;

        container.innerHTML = '<p class="text-muted">Calculando donaciones pendientes con sedes...</p>';
        let deudaTotal = 0;
        let pagadoTotal = 0;

        try {
            // Obtener todas las canchas para luego pedir el estado de cuenta de cada una
            const res = await Core.fetchAPI('/api/canchas');
            const canchas = res.items || res;
            this.estadosCuenta = [];

            for (let c of canchas) {
                // Solo nos interesa llevar control financiero de las rentadas o las que generen cobro
                if (c.tipo === 'Rentada' || c.costo_renta > 0) {
                    try {
                        const edo = await Core.fetchAPI(`/api/canchas/${c.id}/estado_cuenta`);
                        this.estadosCuenta.push(edo);
                        deudaTotal += edo.saldo_pendiente > 0 ? edo.saldo_pendiente : 0;
                        pagadoTotal += edo.total_pagado;
                    } catch (e) {
                        console.error('Error loading estado cuenta para', c.nombre, e);
                    }
                }
            }

            document.getElementById('pagos-canchas-deuda-total').innerText = `$${deudaTotal.toFixed(2)}`;
            document.getElementById('pagos-canchas-pagado-total').innerText = `$${pagadoTotal.toFixed(2)}`;

            this.renderEstadosCuenta();
        } catch (error) {
            console.error(error);
            container.innerHTML = '<p class="error">Error al cargar la información financiera de las sedes.</p>';
        }
    }

    renderEstadosCuenta() {
        const container = document.getElementById('pagos-canchas-container');
        const statusFilter = document.getElementById('pagos-canchas-status-filter')?.value || 'all';
        if (!container) return;

        let filtered = this.estadosCuenta;
        if (statusFilter === 'pending') {
            filtered = this.estadosCuenta.filter(edo => edo.saldo_pendiente > 0);
        } else if (statusFilter === 'settled') {
            filtered = this.estadosCuenta.filter(edo => edo.saldo_pendiente <= 0);
        }

        // Actualizar Totales del Panel Superior Basado en Filtro
        const deudaTotal = filtered.reduce((s, edo) => s + (edo.saldo_pendiente > 0 ? edo.saldo_pendiente : 0), 0);
        const pagadoTotal = filtered.reduce((s, edo) => s + edo.total_pagado, 0);

        document.getElementById('pagos-canchas-deuda-total').innerText = `$${deudaTotal.toFixed(2)}`;
        document.getElementById('pagos-canchas-pagado-total').innerText = `$${pagadoTotal.toFixed(2)}`;

        if (filtered.length === 0) {
            container.innerHTML = `<div class="stat-card" style="text-align: center; padding: 2rem; grid-column: 1 / -1;">
                <p class="text-muted">No hay sedes que coincidan con el filtro "${statusFilter}".</p>
            </div>`;
            return;
        }

        container.innerHTML = filtered.map(edo => `
            <div class="stat-card" style="display: flex; flex-direction: column; gap: 10px; border-left: 4px solid ${edo.saldo_pendiente > 0 ? '#ff4444' : '#00ff88'};">
                <div style="display: flex; justify-content: space-between; align-items: flex-start;">
                    <div>
                        <h4 style="margin: 0; font-size: 1.2rem;">${edo.cancha_nombre}</h4>
                        <span style="font-size: 0.8rem; color: var(--text-muted);">$${edo.costo_renta.toFixed(2)} por ${edo.unidad_cobro.toLowerCase()}</span>
                    </div>
                    ${window.USER_ROL !== 'resultados' && window.USER_ROL !== 'arbitro' ? `
                    <button class="btn-primary" onclick="ui.pagosCanchas.abrirModalPago(${edo.cancha_id})" style="padding: 5px 10px; font-size: 0.85rem;">💸 Aportar / Donar</button>
                    ` : ''}
                </div>
                
                <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 10px; margin-top: 10px; background: rgba(0,0,0,0.2); padding: 10px; border-radius: 8px;">
                    <div>
                        <span style="font-size: 0.75rem; color: var(--text-muted); display: block;">Total Generado</span>
                        <strong style="color: #fff;">$${edo.total_uso.toFixed(2)}</strong>
                    </div>
                    <div>
                        <span style="font-size: 0.75rem; color: var(--text-muted); display: block;">Donación Pendiente</span>
                        <strong style="color: ${edo.saldo_pendiente > 0 ? '#ff4444' : '#00ff88'}; font-size: 1.1rem;">$${edo.saldo_pendiente.toFixed(2)}</strong>
                    </div>
                </div>

                ${edo.desglose_uso.length > 0 ? `
                <div style="margin-top: 10px;">
                    <details>
                        <summary style="font-size: 0.85rem; color: var(--primary); cursor: pointer; outline: none;">Ver Detalle de Uso (${edo.desglose_uso.length} usos)</summary>
                        <div style="max-height: 150px; overflow-y: auto; margin-top: 10px; font-size: 0.8rem; border-top: 1px solid var(--border); padding-top: 5px;">
                            ${edo.desglose_uso.slice(0, 50).map(u => `
                                <div style="display: flex; justify-content: space-between; border-bottom: 1px solid rgba(255,255,255,0.05); padding: 4px 0;">
                                    <span style="color: var(--text-muted);">${u.fecha}</span>
                                    <span>${u.descripcion}</span>
                                    <span style="color: #ff4444;">+$${u.monto.toFixed(2)}</span>
                                </div>
                            `).join('')}
                            ${edo.desglose_uso.length > 50 ? '<p class="text-muted" style="text-align:center; font-size:0.7rem;">...y más</p>' : ''}
                        </div>
                    </details>
                </div>
                ` : '<p style="font-size: 0.8rem; color: var(--text-muted); margin-top: 10px;">Sin uso registrado aún.</p>'}

                ${edo.pagos.length > 0 ? `
                <div style="margin-top: 10px;">
                    <details>
                        <summary style="font-size: 0.85rem; color: #00ff88; cursor: pointer; outline: none;">Ver Historial de Abonos (${edo.pagos.length})</summary>
                        <div style="max-height: 150px; overflow-y: auto; margin-top: 10px; font-size: 0.8rem; border-top: 1px solid var(--border); padding-top: 5px;">
                            ${edo.pagos.map(p => `
                                <div style="display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid rgba(255,255,255,0.05); padding: 5px 0;">
                                    <div>
                                        <span style="color: var(--text-muted); display: block;">${p.fecha}</span>
                                        ${p.notas ? `<span style="font-style: italic; font-size: 0.75rem;">${p.notas}</span>` : ''}
                                    </div>
                                    <div style="display: flex; align-items: center; gap: 10px;">
                                        <strong style="color: #00ff88;">-$${p.monto.toFixed(2)}</strong>
                                        ${p.comprobante_url ? `<a href="${p.comprobante_url}" target="_blank" title="Ver comprobante" style="text-decoration: none;">📄</a>` : ''}
                                        ${window.USER_ROL !== 'resultados' && window.USER_ROL !== 'arbitro' ? `
                                        <button onclick="ui.pagosCanchas.eliminarPago(${p.id})" style="background: none; border: none; color: #ff4444; cursor: pointer; padding: 0;" title="Cancelar Aportación">🗑️</button>
                                        ` : ''}
                                    </div>
                                </div>
                            `).join('')}
                        </div>
                    </details>
                </div>
                ` : ''}
            </div>
        `).join('');
    }

    abrirModalPago(canchaId) {
        const edo = this.estadosCuenta.find(e => e.cancha_id === canchaId);
        if (!edo) return;

        document.getElementById('form-pago-cancha').reset();
        document.getElementById('venue-pago-id').value = edo.cancha_id;
        document.getElementById('venue-pago-nombre').value = edo.cancha_nombre;
        document.getElementById('venue-pago-saldo').value = `$${edo.saldo_pendiente.toFixed(2)}`;
        document.getElementById('venue-pago-monto').value = edo.saldo_pendiente > 0 ? edo.saldo_pendiente.toFixed(2) : 0;

        Core.openModal('modal-pago-cancha');
    }

    async guardarPago(e) {
        e.preventDefault();

        const data = {
            cancha_id: parseInt(document.getElementById('venue-pago-id').value),
            monto: parseFloat(document.getElementById('venue-pago-monto').value),
            comprobante_url: document.getElementById('venue-pago-comprobante').value,
            notas: document.getElementById('venue-pago-notas').value
        };

        console.log("VENUE PAYMENT DATA COLLECTED:", data);

        if (isNaN(data.cancha_id) || isNaN(data.monto)) {
            alert('Por favor complete los datos obligatorios del abono a sede.');
            return;
        }

        try {
            const response = await fetch('/api/pagos_cancha', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(data)
            });

            if (response.ok) {
                Core.showNotification('Aportación registrada a la sede correctamente', 'success');
                Core.closeModal('modal-pago-cancha');
                this.loadEstadosCuenta(); // Recargar todo
            } else {
                const error = await response.json();
                Core.showNotification(error.error || 'Error al guardar el pago', 'error');
            }
        } catch (error) {
            console.error('Error al registrar abono:', error);
            Core.showNotification('Error de conexión', 'error');
        }
    }

    async eliminarPago(pagoId) {
        if (!confirm('¿Seguro que deseas eliminar esta aportación? La donación pendiente de la sede aumentará.')) return;

        try {
            const res = await fetch(`/api/pagos_cancha/${pagoId}`, { method: 'DELETE' });
            if (res.ok) {
                Core.showNotification('Aportación cancelada y eliminada', 'success');
                this.loadEstadosCuenta();
            } else {
                Core.showNotification('Error al eliminar abono', 'error');
            }
        } catch (e) {
            console.error(e);
            Core.showNotification('Error de red al eliminar', 'error');
        }
    }
}
