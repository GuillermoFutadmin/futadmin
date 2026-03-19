import { Core } from './core.js';

export class LeaguesModule {
    constructor(ui) {
        this.ui = ui;
        document.addEventListener('futadmin:limitsLoaded', () => this.checkLimits());
    }

    async showLeagueModal() {
        // Bloqueo de seguridad: No permitir abrir si ya se alcanzó el límite
        const userRol = String(window.USER_ROL || '').toLowerCase().replace('ñ', 'n');
        const limits = window.FutAdminLimits || {};
        const final_limit = limits.torneos;
        const count = window.FutAdminCounts.torneos || 0;

        const isAdminByRol = userRol === 'admin' || userRol === 'ejecutivo';

        if (!isAdminByRol && final_limit !== undefined && count >= final_limit) {
            alert(`Límite alcanzado: Tu plan solo permite ${final_limit} ligas/torneos activos. Archiva uno para poder crear otro.`);
            return;
        }

        document.getElementById('modal-title').innerText = 'Nueva Liga';
        document.getElementById('league-form').reset();
        document.getElementById('league-id').value = '';
        this.switchModalTab('general');
        this.currentEditingArbitroId = null;
        await this.loadOfficialReferees();
        
        // Auto-seleccionar la sede filtrada en el dashboard
        const venueFilter = document.getElementById('league-venue-filter');
        const selectedVenue = venueFilter ? venueFilter.value : null;

        await this.loadCanchasOptions(selectedVenue);

        Core.openModal('modal-container');
    }


    async loadOfficialReferees(selectedId = null) {
        const select = document.getElementById('league-arbitro-id');
        if (!select) return;

        select.innerHTML = '<option value="">Cargando...</option>';
        try {
            const response = await Core.fetchAPI('/api/arbitros');
            const arbitros = response.items || response;
            this.cachedArbitros = Array.isArray(arbitros) ? arbitros.filter(a => a.activo) : [];
            this.filterOfficialReferees(null, selectedId);
        } catch (error) {
            console.error('Error loading referees', error);
            select.innerHTML = '<option value="">-- Sin Árbitro Asignado --</option>';
        }
    }

    filterOfficialReferees(ligaId = null, selectedId = null) {
        const select = document.getElementById('league-arbitro-id');
        if (!select || !this.cachedArbitros) return;

        select.innerHTML = '<option value="">-- Sin Árbitro Asignado --</option>';
        
        let filteredRefs = this.cachedArbitros;
        if (ligaId) {
            filteredRefs = this.cachedArbitros.filter(a => String(a.liga_id) === String(ligaId));
        }

        filteredRefs.forEach(a => {
            const option = document.createElement('option');
            option.value = a.id;
            // Mostramos también a qué combo pertenecen para claridad, aunque ya están filtrados
            option.textContent = a.liga_nombre && a.liga_id ? `${a.nombre} - ${a.liga_nombre}` : a.nombre;
            select.appendChild(option);
        });

        if (selectedId) {
            select.value = selectedId;
        } else {
            select.value = "";
        }
    }

    async loadCanchasOptions(selectedCancha = null) {
        const select = document.getElementById('league-cancha');
        if (!select) return;

        select.innerHTML = '<option value="">Cargando...</option>';
        try {
            const res = await Core.fetchAPI('/api/canchas');
            const canchas = res.items || res;
            select.innerHTML = '<option value="">-- Sin Cancha Asignada --</option>';
            canchas.forEach(c => {
                const option = document.createElement('option');
                option.value = c.nombre;
                option.textContent = `${c.nombre} (${c.tipo})`;
                option.dataset.color = c.color || '#00ff88'; // Almacenar el color del combo
                option.dataset.liga_id = c.liga_id || ''; // Almacenar el ID del combo
                select.appendChild(option);
            });
            if (selectedCancha) select.value = selectedCancha;

            // Manejar cambio de color del select al elegir una sede
            if (!select.dataset.colorListener) {
                select.addEventListener('change', (e) => {
                    const selectedOption = e.target.options[e.target.selectedIndex];
                    const color = selectedOption && selectedOption.dataset.color ? selectedOption.dataset.color : 'var(--border)';
                    const ligaId = selectedOption && selectedOption.dataset.liga_id ? selectedOption.dataset.liga_id : null;

                    // Pintar la sede
                    e.target.style.borderColor = color;
                    e.target.style.boxShadow = color !== 'var(--border)' ? `0 0 8px ${color}60` : 'none';
                    
                    // Pintar el campo de árbitro igual que la sede para consistencia
                    const arbitroSelect = document.getElementById('league-arbitro-id');
                    if(arbitroSelect) {
                        arbitroSelect.style.borderColor = color;
                        arbitroSelect.style.boxShadow = color !== 'var(--border)' ? `0 0 8px ${color}60` : 'none';
                    }

                    // Filtrar árbitros
                    this.filterOfficialReferees(ligaId, this.currentEditingArbitroId);
                    this.currentEditingArbitroId = null; // Reiniciar para futuros cambios manuales
                });
                select.dataset.colorListener = 'true';
            }
            
            // Aplicar el color y filtro inicialmente a la sede pre-seleccionada
            select.dispatchEvent(new Event('change'));

        } catch (error) {
            console.error('Error loading canchas', error);
            select.innerHTML = '<option value="">-- Sin Cancha Asignada --</option>';
        }
    }

    switchModalTab(tabId, btn = null) {
        // Remover activo de todas las pestañas y contenidos
        document.querySelectorAll('.modal-tab').forEach(t => t.classList.remove('active'));
        document.querySelectorAll('.modal-tab-content').forEach(c => c.classList.remove('active'));

        // Activar seleccionada
        document.getElementById(`modal-tab-${tabId}`).classList.add('active');
        if (btn) {
            btn.classList.add('active');
        } else {
            // Activar primer botón por defecto si no se pasa uno
            const tabs = document.querySelectorAll('.modal-tab');
            if (tabs.length) tabs[0].classList.add('active');
        }
    }

    loadTemplate(type) {
        const leagueType = document.getElementById('league-type').value;
        const numTiempos = document.getElementById('league-num-tiempos').value || 2;
        const duracion = document.getElementById('league-duracion-tiempo').value || 20;
        const descanso = document.getElementById('league-descanso').value || 10;
        const costoArb = document.getElementById('league-cost-ref').value || 0;

        const templates = {
            'Fut 7': {
                reglamento: `REGLAMENTO OFICIAL FÚTBOL 7
1. DURACIÓN: ${numTiempos} tiempos de ${duracion} min con ${descanso} min de descanso.
2. JUGADORES: Mínimo 5, máximo 7 en cancha.
3. CAMBIOS: Ilimitados por zona técnica sin aviso.
4. SAQUE DE BANDA: Realizado obligatoriamente con las manos.
5. TIROS LIBRES: La barrera debe situarse a 5 metros.
6. PENALTI: Cobrado desde el punto designado a 9 metros.
7. DISCIPLINA: Amarilla (Aviso), Azul (2 min fuera), Roja (Expulsión).
8. PUNTUALIDAD: Tolerancia máxima de 10 min (Default).
9. ARBITRAJE: Las decisiones son definitivas e inapelables.
10. EQUIPAMIENTO: Espinilleras obligatorias y calzado adecuado.`,
                clausulas: `CLÁUSULAS DE INSCRIPCIÓN FÚTBOL 7
1. PAGO: Inscripción liquidada al 100% antes de la jornada 3.
2. RESPONSABILIDAD: El comité no cubre lesiones fortuitas.
3. ARBITRAJE: Pago de cuota de $${costoArb} íntegra previa a cada partido.
4. CONDUCTA: El equipo responde por el comportamiento de su porra.
5. CREDENCIALES: Digitales obligatorias para poder alinear.
6. FIANZA: Depósito reembolsable únicamente al concluir el torneo.
7. ALCOHOL: Prohibido estrictamente en campo y zonas aledañas.
8. UNIFORME: Camisetas del mismo color con números legibles.
9. BAJA: El equipo que abandone el torneo pierde su fianza.
10. DERECHOS: El equipo autoriza el uso de fotos en redes sociales.`,
                premios: `BOLSA DE PREMIOS FÚTBOL 7
1. CAMPEÓN: Trofeo, Medallas y $5,000 en Efectivo.
2. SUBCAMPEÓN: Trofeo y Medallas.
3. CAMPEÓN GOLEADOR: Trofeo/Reconocimiento.
4. MEJOR PORTERO: Guantes Semiprofesionales.`
            },
            'Soccer': {
                reglamento: `REGLAMENTO OFICIAL SOCCER (FUT 11)
1. TIEMPOS: ${numTiempos} periodos de ${duracion} min oficiales con ${descanso} min de descanso.
2. REGLA 11: El fuera de lugar está vigente durante todo el juego.
3. CAMBIOS: Máximo 5 cambios en 3 ventanas de tiempo.
4. SAQUE DE META: Con el pie desde cualquier punto del área chica.
5. BALÓN: Tamaño #5 con presión reglamentaria.
6. TARJETAS: La acumulación de 3 amarillas causa 1 partido de suspensión.
7. CAPITÁN: Único autorizado para dirigirse al cuerpo arbitral.
8. ESPINILLERAS: Uso obligatorio; si no cuenta con ellas no juega.
9. PORTERÍA: El portero está protegido dentro de su área chica.
10. EMPATE: Se definirá según el formato de la competencia oficial.`,
                clausulas: `CLÁUSULAS LEGALES SOCCER
1. SEGURIDAD: Los equipos asumen riesgos médicos inherentes.
2. INSTALACIONES: Todo daño a la cancha será cubierto por el equipo.
3. ALTAS: Jugadores nuevos solo permitidos hasta la mitad del torneo.
4. MULTAS: Las tarjetas rojas directas generan multa de $100.
5. PROTESTAS: Por escrito con evidencia y fianza de $300.
6. REGLAMENTO: Los equipos aceptan los estatutos de la FIFA adaptados.
7. ARBITRAJE: Se debe cubrir el pago arbtitral de $${costoArb} puntualmente.
8. ASISTENCIA: 2 incomparecencias injustificadas causan baja.
9. PREMIACIÓN: Sujeta a cumplimiento total de pagos económicos.
10. JUNTA: Obligatoria la asistencia de delegados a reuniones.`,
                premios: `BOLSA DE PREMIOS SOCCER
1. CAMPEÓN LIGA: Trofeo Grande y 10 Balones.
2. CAMPEÓN DE COPA: Trofeo Mediano.
3. GOLEADOR: Trofeo y Zapatos de Fútbol.`
            },
            'Futsal': {
                reglamento: `REGLAMENTO OFICIAL FUTSAL
1. SUPERFICIE: Juego sobre duela o cemento pulido.
2. TIEMPO: ${numTiempos} tiempos de ${duracion} min (Descanso: ${descanso} min).
3. FALTAS: La sexta falta se castiga con tiro libre directo (doble penalti).
4. SAQUE DE BANDA: Se realiza con los pies sobre la línea.
5. PORTERO: Solo tiene 4 segundos para despejar el balón.
6. BARRIDAS: Prohibido deslizarse ante el rival (falta directa).
7. TIEMPO FUERA: Un minuto por tiempo por cada equipo.
8. BARRERA: Distancia reglamentaria de 3 metros.
9. CAMBIOS: Rotación libre y rápida sin aviso al cronometrista.
10. BALÓN: Tamaño #4 con rebote controlado (lastrado).`,
                clausulas: `CLÁUSULAS ADMINISTRATIVAS FUTSAL
1. CALZADO: Suela de liga o goma blanca que no manche la duela.
2. PAGO: Arbitrajes de $${costoArb} prepagados antes del inicio.
3. CONDUCTA: Insultos al personal causan veto inmediato al jugador.
4. LIMPIEZA: Prohibido introducir alimentos al área de juego.
5. IDENTIDAD: Acta de nacimiento original para menores de edad.
6. REPROGRAMACIÓN: Solo con aviso de 48 horas y pago de gastos.
7. UNIFORME: Petos obligatorios si hay conflicto de colores.
8. PORRA: El capitán es fiscal del comportamiento de su gente.
9. SALUD: Certificado médico vigente para todos los integrantes.
10. FINAL: Solo jugadores con 5 partidos jugados califican a liguilla.`,
                premios: `BOLSA DE PREMIOS FUTSAL
1. CAMPEÓN INVIERNO: Uniformes completos (12 pts).
2. SUBCAMPEÓN: Inscripción gratis próximo torneo.
3. GOLEADOR: Tarjeta de Regalo.`
            },
            'Fútbol Rápido': {
                reglamento: `REGLAMENTO OFICIAL FÚTBOL RÁPIDO
1. BARDAS: El contacto con la madera/pared es legal y válido.
2. SAQUE DE BANDA: No existe, el balón rebota o sale por redes superiores.
3. JUGADORES: 6 elementos en cancha con rotación constante.
4. PERIODOS: ${numTiempos} cuartos de ${duracion} minutos cada uno.
5. SUSPENSIÓN TÉCNICA: Sanción de 2 min tras conducta antideportiva.
6. SHOOT-OUT: Mano o falta de último hombre otorga mano a mano.
7. BALÓN: #4 específico de bote rápido.
8. DESCANSO: ${descanso} MINUTOS entre periodos.
9. ARQUERO: No puede cruzar la media cancha con balón en mano.
10. GOL: Válido desde cualquier sector de la cancha.`,
                clausulas: `CLÁUSULAS RÉGIMEN FÚTBOL RÁPIDO
1. DAÑOS: Rotura de cristales o bardas corre por cuenta del equipo.
2. FISCAL: El juez de mesa tiene autoridad sobre los delegados.
3. PAGOS: Costo arbitral de $${costoArb} semanal obligatorio.
4. REGLAS: Se sigue el código de la asociación nacional de la rama.
5. TARJETAS: Tarjeta azul penaliza con tiempo muerto al jugador.
6. EMPATE: Resolución por shoot-outs en etapas finales.
7. UNIFORMES: Medias y números debidamente reglamentados.
8. INTEGRIDAD: No se permiten tacos de aluminio o fierro.
9. REGISTRO: Formatos de inscripción debidamente requisitados.
10. VETO: Jugador sancionado no puede ingresar ni como espectador.`,
                premios: `BOLSA DE PREMIOS FÚTBOL RÁPIDO
1. CAMPEÓN: $8,000 MXN.
2. SUBCAMPEÓN: $3,000 MXN.
3. 3ER LUGAR: Devolución de Inscripción.`
            },
            'Relámpago': {
                reglamento: `REGLAMENTO TORNEO RELÁMPAGO
1. DURACIÓN: Partidos de ${numTiempos} tiempos de ${duracion} min.
2. SISTEMA: Eliminación directa única; pierdes y sales.
3. EMPATE: Definición inmediata por serie de 3 penaltis.
4. PLANTILLA: Máximo 10 jugadores inscritos por equipo.
5. REGLAS: Se aplican las bases de Fútbol 7 básicas.
6. EXPULSIÓN: Tarjeta roja directa te deja fuera de todo el torneo.
7. BALÓN: Deberá ser entregado al árbitro por el equipo local.
8. TOLERANCIA: No existe; 2 min de retraso es default.
9. CALZADO: Solo tenis (No tacos de fútbol campo).
10. PREMIACIÓN: Se entrega al finalizar la gran final del día.`,
                clausulas: `CLÁUSULAS TORNEO RELÁMPAGO
1. PAGO: Inscripción total pagada antes del primer sorteo.
2. REEMBOLSO: No existen devoluciones por inasistencia.
3. HORARIOS: Sujetos a cambios bruscos según avance del bracket.
4. MÉDICO: El torneo cuenta con primeros auxilios básicos.
5. ARBITRAJE: Paquete de pre-pago de $${costoArb} por fase.
6. HIDRATACIÓN: Cada equipo es responsable de su consumo.
7. PORRA: Se limitará el acceso a porras excesivamente grandes.
8. PROTESTAS: Deben hacerse al finalizar el juego ante mesa directiva.
9. PREMIOS: El trofeo y medallas son propiedad del campeón vigente.
10. CIERRE: Al terminar el torneo, todos los equipos deben desalojar.`,
                premios: `BOLSA DE PREMIOS RELÁMPAGO
1. CAMPEÓN: Reconocimiento y $3,000 en Bono.
2. MVP: Balón Oficial.`
            }
        };

        const config = templates[leagueType] || templates['Fut 7'];
        const textarea = document.getElementById(`league-${type}`);

        if (textarea && (!textarea.value || confirm('¿Deseas reemplazar el contenido actual con la plantilla específica de ' + (leagueType || 'Fut 7') + '?'))) {
            textarea.value = config[type];
        }
    }

    async editLeague(id) {
        try {
            const response = await Core.fetchAPI('/api/torneos');
            const torneos = response.items || response;
            const t = Array.isArray(torneos) ? torneos.find(torneo => torneo.id === id) : null;

            if (t) {
                document.getElementById('modal-title').innerText = 'Editar Liga';
                document.getElementById('league-id').value = t.id;
                document.getElementById('league-name').value = t.nombre;
                document.getElementById('league-type').value = t.tipo;
                document.getElementById('league-formato').value = t.formato || 'Liga';
                document.getElementById('league-date').value = t.fecha_inicio || '';
                document.getElementById('league-cost-reg').value = t.costo_inscripcion || 0;
                document.getElementById('league-cost-ref').value = t.costo_arbitraje || 0;
                document.getElementById('league-num-tiempos').value = t.num_tiempos || 2;
                document.getElementById('league-duracion-tiempo').value = t.duracion_tiempo || 20;
                document.getElementById('league-descanso').value = t.descanso || 10;
                document.getElementById('league-jugadores-totales').value = t.jugadores_totales || 15;
                document.getElementById('league-jugadores-campo').value = t.jugadores_campo || 7;

                // Configurar Días de Juego (checkboxes)
                document.querySelectorAll('.day-cb').forEach(cb => cb.checked = false);
                if (t.dias_juego) {
                    const dias = t.dias_juego.split(',').map(d => d.trim());
                    document.querySelectorAll('.day-cb').forEach(cb => {
                        if (dias.includes(cb.value)) cb.checked = true;
                    });
                }

                // Configurar Horarios (time inputs)
                document.getElementById('league-hora-inicio').value = '';
                document.getElementById('league-hora-fin').value = '';
                if (t.horario_juego && t.horario_juego.includes('a')) {
                    const parts = t.horario_juego.split('a').map(p => p.trim());
                    document.getElementById('league-hora-inicio').value = parts[0] || '';
                    document.getElementById('league-hora-fin').value = parts[1] || '';
                } else if (t.horario_juego && t.horario_juego.includes('-')) {
                    const parts = t.horario_juego.split('-').map(p => p.trim());
                    document.getElementById('league-hora-inicio').value = parts[0] || '';
                    document.getElementById('league-hora-fin').value = parts[1] || '';
                }

                document.getElementById('league-cancha').value = t.cancha || '';
                document.getElementById('league-image').value = t.imagen_url || '';
                document.getElementById('league-premios').value = t.premios || '';
                document.getElementById('league-reglamento').value = t.reglamento || '';
                document.getElementById('league-clausulas').value = t.clausulas || '';

                this.currentEditingArbitroId = t.arbitro_id;
                await this.loadOfficialReferees(t.arbitro_id);
                await this.loadCanchasOptions(t.cancha);

                this.switchModalTab('general');
                Core.openModal('modal-container');

            }
        } catch (error) {
            console.error('Error al cargar datos para edición:', error);
        }
    }

    async deleteLeague(id) {
        if (!confirm('¿Estás seguro de que deseas eliminar este torneo? Se borrarán los equipos y jugadores asociados.')) {
            return;
        }

        try {
            const response = await fetch(`/api/torneos/${id}`, { method: 'DELETE' });
            if (response.ok) {
                await this.ui.loadInitialStats();
                this.loadLeagues();
            } else {
                alert('Error al eliminar el torneo. Verifica que no tenga equipos activos.');
            }
        } catch (error) {
            console.error('Error al eliminar:', error);
            alert('Error de conexión.');
        }
    }

    async loadLeagues(filterVenue = null) {
        const container = document.getElementById('leagues-container');
        if (!container) return;
        container.innerHTML = '<p>Cargando torneos...</p>';

        try {
            const response = await Core.fetchAPI('/api/torneos');
            const torneos = response.items || response;
            this.pagination = response.pagination || null;
            
            // Poblar filtro de sedes si está vacío (excluyendo la opción por defecto)
            const venueFilter = document.getElementById('league-venue-filter');
            if (venueFilter && venueFilter.options.length <= 1) {
                const resCanchas = await Core.fetchAPI('/api/canchas');
                const canchas = resCanchas.items || resCanchas;
                canchas.forEach(c => {
                    const opt = document.createElement('option');
                    opt.value = c.nombre;
                    opt.textContent = c.nombre;
                    venueFilter.appendChild(opt);
                });
            }

            // Aplicar filtro si se pasa por parámetro o está seleccionado en el UI
            const selectedVenue = filterVenue || (venueFilter ? venueFilter.value : '');
            if (venueFilter && filterVenue) {
                venueFilter.value = filterVenue;
            }

            let filtered = torneos;
            if (selectedVenue) {
                filtered = torneos.filter(t => t.cancha && t.cancha.trim() === selectedVenue.trim());
            }

            this.renderLeagues(filtered);
            this.checkLimits();
        } catch (error) {
            console.error('Error loading leagues:', error);
            container.innerHTML = '<p class="error">Error al conectar con el servidor.</p>';
        }
    }

    checkLimits() {
        const btn = document.getElementById('btn-nueva-liga');
        if (!btn) return;
        
        const userRol = (window.USER_ROL || '').toLowerCase();
        // Si el usuario es de solo vista o árbitro, ocultar botón siempre
        if (userRol === 'resultados' || userRol === 'arbitro' || userRol === 'solo vista') {
            btn.style.display = 'none';
            return;
        }

        if (!window.FutAdminLimits || !window.FutAdminCounts) return;
        
        const limit_torneos = window.FutAdminLimits.torneos;
        const limit_per_cancha = window.FutAdminLimits.torneos_per_cancha;
        let final_limit = undefined;

        if (limit_torneos !== undefined) {
            final_limit = limit_torneos;
        } else if (limit_per_cancha !== undefined) {
            const canchas = window.FutAdminCounts.canchas || 0;
            final_limit = canchas * limit_per_cancha;
            if (final_limit === 0) final_limit = limit_per_cancha;
        }
        
        const count = window.FutAdminCounts.torneos || 0;
        console.log(`[Limits] Torneos: ${count}/${final_limit} (Rol: ${userRol})`);
        
        // Actualizar contadores visuales
        const counterMain = document.getElementById('league-counter-main');
        const counterModal = document.getElementById('league-counter-modal');
        const isAdmin = userRol === 'admin' || userRol === 'ejecutivo';
        const displayLimit = isAdmin ? '∞' : final_limit;
        
        const counterText = final_limit !== undefined ? `${count} / ${displayLimit}` : `${count}`;
        
        if (counterMain) counterMain.innerText = counterText;
        if (counterModal) counterModal.innerText = counterText;

        if (final_limit !== undefined && count >= final_limit) {
            btn.style.display = 'none';
        } else {
            btn.style.display = 'inline-block';
        }
    }

    renderLeagues(torneos) {
        const container = document.getElementById('leagues-container');
        if (torneos.length === 0) {
            container.innerHTML = '<p>No hay ligas configuradas aún. ¡Crea la primera!</p>';
            return;
        }

        const userRol = (window.USER_ROL || '').toLowerCase();
        const isAdmin = !['resultados', 'arbitro', 'solo vista'].includes(userRol);

        container.innerHTML = torneos.map(t => `
            <div class="league-card" onclick="ui.leagues.goToEquipos(${t.id})" style="position: relative; padding: 1.5rem; display: flex; align-items: stretch; justify-content: space-between; gap: 1.5rem; cursor: pointer; min-height: 180px; margin-bottom: 1rem; overflow: hidden;">
                <div class="combo-indicator" style="background: ${t.color || 'var(--primary)'};"></div>
                <div style="position: absolute; bottom: 0; left: 0; right: 0; height: 6px; background: ${t.color || 'var(--primary)'}; opacity: 0.6; z-index: 5;"></div>
                <div style="flex: 1; text-align: left; display: flex; flex-direction: column; justify-content: space-between;">
                    <div>
                        <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 4px;">
                            <span class="league-badge" style="margin-bottom: 0;">${t.tipo}</span>
                                <span class="league-badge" style="margin-bottom: 0; background: rgba(0, 255, 136, 0.2); color: #00ff88; border: 1px solid rgba(0, 255, 136, 0.4);">${t.formato || 'Liga'}</span>
                                <span style="font-size: 0.75rem; color: ${t.activo ? 'var(--primary)' : '#ff4444'}; font-weight: 700; text-transform: uppercase;">${t.activo ? '● Activo' : '● Finalizado'}</span>
                                ${t.tiene_usuario ? `
                                    <span class="badge-premium" style="font-size: 0.65rem; background: rgba(0, 191, 255, 0.1); color: #00bfff; border: 1px solid rgba(0, 191, 255, 0.3); padding: 2px 8px; border-radius: 4px;">
                                        🔗 Cuenta
                                    </span>
                                ` : ''}
                            </div>
                            <h4 style="margin: 0; font-size: 1.5rem; color: #fff;">${t.nombre}</h4>
                        <div style="display: flex; gap: 8px; flex-wrap: wrap; margin: 10px 0;">
                            <div style="background: rgba(255,255,255,0.02); padding: 4px 10px; border-radius: 6px; border: 1px solid rgba(255,255,255,0.05);">
                                <span style="display: block; font-size: 0.55rem; color: var(--text-muted); text-transform: uppercase;">Inscripción</span>
                                <strong style="color: #00ff88; font-size: 0.9rem;">$${(t.costo_inscripcion || 0).toFixed(0)}</strong>
                            </div>
                            <div style="background: rgba(255,255,255,0.02); padding: 4px 10px; border-radius: 6px; border: 1px solid rgba(255,255,255,0.05);">
                                <span style="display: block; font-size: 0.55rem; color: var(--text-muted); text-transform: uppercase;">Arbitraje</span>
                                <strong style="color: #00ff88; font-size: 0.9rem;">$${(t.costo_arbitraje || 0).toFixed(0)}</strong>
                            </div>
                            <div style="background: rgba(255,255,255,0.02); padding: 4px 10px; border-radius: 6px; border: 1px solid rgba(255,255,255,0.05);">
                                <span style="display: block; font-size: 0.55rem; color: var(--text-muted); text-transform: uppercase;">Días</span>
                                <strong style="color: #fff; font-size: 0.8rem;">${t.dias_juego || 'N/A'}</strong>
                            </div>
                            <div style="background: rgba(255,255,255,0.02); padding: 4px 10px; border-radius: 6px; border: 1px solid rgba(255,255,255,0.05);">
                                <span style="display: block; font-size: 0.55rem; color: var(--text-muted); text-transform: uppercase;">Horario</span>
                                <strong style="color: #fff; font-size: 0.8rem;">${t.horario_juego || 'N/A'}</strong>
                            </div>
                            <div style="background: rgba(255,255,255,0.02); padding: 4px 10px; border-radius: 6px; border: 1px solid rgba(255,255,255,0.05);">
                                <span style="display: block; font-size: 0.55rem; color: var(--text-muted); text-transform: uppercase;">Cancha Sede</span>
                                <strong style="color: #fff; font-size: 0.8rem;">${t.cancha || 'N/A'}</strong>
                            </div>
                            <div style="background: rgba(255,255,255,0.02); padding: 4px 10px; border-radius: 6px; border: 1px solid rgba(255,255,255,0.05);">
                                <span style="display: block; font-size: 0.55rem; color: var(--text-muted); text-transform: uppercase;">Formato</span>
                                <strong style="color: #fff; font-size: 0.8rem;">${t.num_tiempos}x${t.duracion_tiempo}' (${t.jugadores_campo}v${t.jugadores_campo})</strong>
                            </div>
                            <div style="background: rgba(255,255,255,0.02); padding: 4px 10px; border-radius: 6px; border: 1px solid rgba(255,255,255,0.05);">
                                <span style="display: block; font-size: 0.55rem; color: var(--text-muted); text-transform: uppercase;">Equipos</span>
                                <strong style="color: var(--primary); font-size: 0.9rem;">${t.stats?.equipos || 0}</strong>
                            </div>
                            <div style="background: rgba(255,255,255,0.02); padding: 4px 10px; border-radius: 6px; border: 1px solid rgba(255,255,255,0.05);">
                                <span style="display: block; font-size: 0.55rem; color: var(--text-muted); text-transform: uppercase;">Jugadores</span>
                                <strong style="color: var(--primary); font-size: 0.9rem;">${t.stats?.jugadores || 0}</strong>
                            </div>
                        </div>
                        <div style="background: rgba(255,255,255,0.02); padding: 10px 14px; border-radius: 8px; border: 1px solid rgba(255,215,0,0.2); margin-top: 8px;">
                            <span style="display: block; font-size: 0.65rem; color: #ffd700; text-transform: uppercase; margin-bottom: 6px; font-weight: bold; letter-spacing: 0.5px;">🏆 Premios</span>
                            <div style="color: #ffffff; font-size: 0.85rem; white-space: pre-wrap; line-height: 1.4; max-height: 80px; overflow-y: auto; text-shadow: 0 1px 2px rgba(0,0,0,0.5);">${t.premios ? t.premios : '<span style="color:var(--text-muted)">Sin premios configurados</span>'}</div>
                        </div>
                    </div>

                    ${isAdmin ? `
                    <div class="league-actions" onclick="event.stopPropagation()" style="display: flex; gap: 10px;">
                        <button onclick="ui.leagues.editLeague(${t.id})" style="background: rgba(255,255,255,0.05); border: 1px solid var(--border); color: #fff; cursor: pointer; border-radius: 6px; padding: 6px 14px; font-size: 0.85rem;">✏️ Editar</button>
                        <button onclick="ui.leagues.deleteLeague(${t.id})" style="background: rgba(255,255,255,0.05); border: 1px solid var(--border); color: #fff; cursor: pointer; border-radius: 6px; padding: 6px 14px; font-size: 0.85rem;">🗑️ Borrar</button>
                    </div>
                    ` : ''}
                </div>
                <div style="flex-shrink: 0; width: 160px;">
                    ${t.imagen_url ? `
                        <div style="background-image: url('${t.imagen_url}'); height: 100%; width: 100%; min-height: 150px; background-size: cover; background-position: center; border-radius: 16px; border: 2px solid var(--border); box-shadow: 0 10px 25px rgba(0,0,0,0.4);"></div>
                    ` : `
                        <div style="height: 100%; width: 100%; min-height: 150px; background: rgba(255,255,255,0.05); display: flex; align-items: center; justify-content: center; font-size: 4rem; border-radius: 16px; border: 1px dashed var(--border);">⚽</div>
                    `}
                </div>
            </div>
        `).join('');

        // Agregar Controles de Paginación si existen
        if (this.pagination && this.pagination.total_pages > 1) {
            container.innerHTML += `
                <div class="pagination-controls">
                    <button class="btn-pagination" ${!this.pagination.has_prev ? 'disabled' : ''} 
                            onclick="ui.leagues.changePage(${this.pagination.page - 1})">
                        &laquo; Anterior
                    </button>
                    <span class="pagination-info">Página ${this.pagination.page} de ${this.pagination.total_pages}</span>
                    <button class="btn-pagination" ${!this.pagination.has_next ? 'disabled' : ''} 
                            onclick="ui.leagues.changePage(${this.pagination.page + 1})">
                        Siguiente &raquo;
                    </button>
                </div>
            `;
        }
    }

    async changePage(page) {
        if (page < 1 || (this.pagination && page > this.pagination.total_pages)) return;
        
        // Cargar torneos con el parámetro de página
        const container = document.getElementById('leagues-container');
        if (!container) return;
        container.innerHTML = '<p>Cargando página ' + page + '...</p>';

        try {
            const response = await Core.fetchAPI(`/api/torneos?page=${page}`);
            const torneos = response.items || response;
            this.pagination = response.pagination || null;
            
            // Re-aplicar filtros si es necesario
            const venueFilter = document.getElementById('league-venue-filter');
            const selectedVenue = venueFilter ? venueFilter.value : '';
            
            let filtered = torneos;
            if (selectedVenue) {
                filtered = torneos.filter(t => t.cancha && t.cancha.trim() === selectedVenue.trim());
            }

            this.renderLeagues(filtered);
            window.scrollTo({ top: 0, behavior: 'smooth' });
        } catch (error) {
            console.error('Error changing page:', error);
        }
    }

    goToEquipos(torneoId) {
        const torneosNav = document.querySelector('.nav-item[data-view="torneos"]');

        // Precargar la información antes/durante la transición para evitar el placeholder
        const filterSelect = document.getElementById('team-league-filter');
        if (filterSelect) {
            filterSelect.value = torneoId;
            // Usamos setTimeout(0) para asegurar que el DOM registró el value antes de fetchear
            setTimeout(() => {
                this.ui.teams.loadEquipos();
            }, 0);
        }

        // Cambiar a la vista 'torneos' y directamente a la pestaña 'equipos'
        this.ui.switchView('torneos', 'equipos', torneosNav);
    }

    async handleLeagueSubmit(e) {
        e.preventDefault();
        const id = document.getElementById('league-id').value;
        const method = id ? 'PUT' : 'POST';
        const url = id ? `/api/torneos/${id}` : '/api/torneos';

        const data = {
            nombre: document.getElementById('league-name').value.trim(),
            tipo: document.getElementById('league-type').value,
            formato: document.getElementById('league-formato').value,
            fecha_inicio: document.getElementById('league-date').value,
            costo_inscripcion: parseFloat(document.getElementById('league-cost-reg').value || 0),
            costo_arbitraje: parseFloat(document.getElementById('league-cost-ref').value || 0),
            num_tiempos: parseInt(document.getElementById('league-num-tiempos').value || 2),
            duracion_tiempo: parseInt(document.getElementById('league-duracion-tiempo').value || 20),
            descanso: parseInt(document.getElementById('league-descanso').value || 10),
            jugadores_totales: parseInt(document.getElementById('league-jugadores-totales').value || 15),
            jugadores_campo: parseInt(document.getElementById('league-jugadores-campo').value || 7),
            dias_juego: Array.from(document.querySelectorAll('.day-cb:checked')).map(cb => cb.value).join(', '),
            horario_juego: (document.getElementById('league-hora-inicio').value && document.getElementById('league-hora-fin').value)
                ? `${document.getElementById('league-hora-inicio').value} a ${document.getElementById('league-hora-fin').value}`
                : '',
            cancha: document.getElementById('league-cancha').value.trim(),
            arbitro_id: document.getElementById('league-arbitro-id').value ? parseInt(document.getElementById('league-arbitro-id').value) : null,
            imagen_url: document.getElementById('league-image').value.trim(),
            premios: document.getElementById('league-premios').value.trim(),
            reglamento: document.getElementById('league-reglamento').value.trim(),
            clausulas: document.getElementById('league-clausulas').value.trim(),
        };


        try {
            const response = await fetch(url, {
                method: method,
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(data)
            });

            if (response.ok) {
                Core.closeModal('modal-container');
                await this.ui.loadInitialStats();
                this.loadLeagues();
            } else {
                alert('Error al guardar la liga.');
            }
        } catch (error) {
            alert('Error de conexión.');
        }
    }

    async loadArchivedLeagues() {
        const container = document.getElementById('archivo-container');
        if (!container) return;

        container.innerHTML = '<p class="text-muted">Cargando historial...</p>';
        try {
            const torneos = await Core.fetchAPI('/api/torneos/archived');
            this.renderArchivedLeagues(torneos);
        } catch (error) {
            container.innerHTML = '<p class="text-muted">Error al cargar archivados.</p>';
        }
    }

    renderArchivedLeagues(torneos) {
        const container = document.getElementById('archivo-container');
        if (!container) return;

        if (torneos.length === 0) {
            container.innerHTML = `
                <div class="stat-card" style="text-align: center; padding: 3rem; grid-column: 1 / -1;">
                    <span style="font-size: 3rem; display: block; margin-bottom: 1rem;">♻️</span>
                    <p class="text-muted">No hay ligas archivadas en este momento.</p>
                </div>
            `;
            return;
        }

        container.innerHTML = torneos.map(t => `
            <div class="stat-card premium-card league-card archived" data-id="${t.id}" style="opacity: 0.8;">
                <div style="flex: 1;">
                    <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 15px;">
                        <h4 style="margin: 0; font-size: 1.1rem; color: #fff;">${t.nombre}</h4>
                        <span class="badge" style="background: rgba(255,255,255,0.1); color: var(--text-muted);">${t.tipo}</span>
                    </div>
                    <p style="font-size: 0.85rem; color: var(--text-muted); margin-bottom: 15px;">
                        📅 Iniciado: ${t.fecha_inicio || 'S/F'}<br>
                        🏟️ Sede: ${t.cancha || 'No asignada'}
                    </p>
                    <div class="league-actions" style="display: flex; gap: 8px; flex-wrap: wrap;">
                        <button onclick="ui.leagues.downloadTournamentReport(${t.id})" class="btn-secondary" style="padding: 6px 10px; font-size: 0.75rem; display: flex; align-items: center; gap: 5px; background: rgba(255,255,255,0.05); border: 1px solid rgba(255,255,255,0.1); color: var(--text-muted);">
                            <span>📋</span> Reporte PDF
                        </button>
                        <button onclick="ui.leagues.restoreLeague(${t.id})" class="btn-primary" style="padding: 6px 12px; font-size: 0.8rem; background: var(--primary); color: #000;">♻️ Restaurar</button>
                        <button onclick="ui.leagues.permanentDeleteLeague(${t.id})" class="btn-danger" style="padding: 6px 12px; font-size: 0.8rem; background: #ef4444; color: #fff; border: none; border-radius: 6px; cursor: pointer;">🗑️</button>
                    </div>
                </div>
            </div>
        `).join('');
    }

    async restoreLeague(id) {
        if (!confirm('¿Deseas restaurar este torneo? Volverá a aparecer en la lista de ligas activas.')) return;

        try {
            const result = await Core.fetchAPI(`/api/torneos/${id}/restore`, { method: 'POST' });
            if (result.success) {
                Core.showNotification('Torneo restaurado correctamente');
                await this.ui.loadInitialStats();
                this.loadArchivedLeagues();
                this.loadLeagues();
            } else {
                alert('Error al restaurar: ' + (result.error || 'Desconocido'));
            }
        } catch (error) {
            alert('Error de conexión.');
        }
    }

    async permanentDeleteLeague(id) {
        if (!confirm('¡ADVERTENCIA! Esta acción no se puede deshacer. Se eliminarán permanentemente todos los equipos, partidos, resultados y estadísticas de este torneo. ¿Estás COMPLETAMENTE seguro?')) return;

        try {
            const result = await Core.fetchAPI(`/api/torneos/${id}/permanent`, { method: 'DELETE' });
            if (result.success) {
                Core.showNotification('Torneo eliminado permanentemente', 'info');
                await this.ui.loadInitialStats();
                this.loadArchivedLeagues();
            } else {
                alert('Error al eliminar: ' + (result.error || 'Desconocido'));
            }
        } catch (error) {
            alert('Error de conexión.');
        }
    }

    async downloadTournamentReport(id) {
        Core.showNotification('Cargando motor de reporte...', 'info');
        try {
            // Carga diferida de librerías pesadas
            await Promise.all([
                Core.loadScript('https://cdnjs.cloudflare.com/ajax/libs/jspdf/2.5.1/jspdf.umd.min.js'),
                Core.loadScript('https://html2canvas.hertzen.com/dist/html2canvas.min.js')
            ]);

            Core.showNotification('Generando reporte PDF...', 'info');
            const data = await Core.fetchAPI(`/api/torneos/${id}/report`);
            const { torneo, campeon, standings, leaderboard } = data;

            // Importar jsPDF desde el objeto global window
            const { jsPDF } = window.jspdf;
            const doc = new jsPDF();
            const primaryColor = [0, 255, 136]; // #00ff88 (FutAdmin Primary)
            const margin = 15;
            let y = 20;

            // --- HEADER ---
            doc.setFillColor(30, 30, 30);
            doc.rect(0, 0, 210, 45, 'F');
            
            doc.setTextColor(255, 255, 255);
            doc.setFontSize(24);
            doc.setFont("helvetica", "bold");
            doc.text("FUTADMIN PRO", margin, 25);
            
            doc.setFontSize(10);
            doc.setTextColor(...primaryColor);
            doc.text("REPORTE HISTÓRICO DE TORNEO", margin, 35);
            
            doc.setTextColor(150, 150, 150);
            const dateStr = new Date().toLocaleDateString();
            doc.text(`Generado el: ${dateStr}`, 150, 35);

            y = 60;
            doc.setTextColor(40, 40, 40);
            doc.setFontSize(18);
            doc.text(torneo.nombre.toUpperCase(), margin, y);
            y += 8;
            doc.setFontSize(10);
            doc.setFont("helvetica", "normal");
            doc.text(`${torneo.tipo} • ${torneo.formato}`, margin, y);
            y += 6;
            doc.text(`Sede: ${torneo.cancha || 'No asignada'} | Inicio: ${torneo.fecha_inicio}`, margin, y);

            if (campeon) {
                y += 15;
                doc.setDrawColor(...primaryColor);
                doc.setLineWidth(1);
                doc.line(margin, y - 5, 210 - margin, y - 5);
                doc.setFontSize(16);
                doc.setFont("helvetica", "bold");
                doc.text(`🏆 CAMPEÓN: ${campeon.toUpperCase()}`, margin + 5, y + 5);
                y += 15;
            }

            // --- STANDINGS TABLE ---
            y += 10;
            doc.setFontSize(14);
            doc.setFont("helvetica", "bold");
            doc.text("TABLA DE POSICIONES", margin, y);
            y += 8;

            // Headers
            doc.setFillColor(240, 240, 240);
            doc.rect(margin, y, 180, 8, 'F');
            doc.setFontSize(9);
            doc.text("POS", margin + 2, y + 5);
            doc.text("EQUIPO", margin + 15, y + 5);
            doc.text("PTS", margin + 70, y + 5);
            doc.text("PJ", margin + 85, y + 5);
            doc.text("G", margin + 100, y + 5);
            doc.text("E", margin + 115, y + 5);
            doc.text("P", margin + 130, y + 5);
            doc.text("GF", margin + 145, y + 5);
            doc.text("GC", margin + 160, y + 5);
            doc.text("DG", margin + 175, y + 5);
            y += 8;

            doc.setFont("helvetica", "normal");
            standings.forEach((row, idx) => {
                if (y > 270) { doc.addPage(); y = 20; }
                if (idx % 2 === 0) {
                    doc.setFillColor(250, 250, 250);
                    doc.rect(margin, y, 180, 7, 'F');
                }
                doc.text((idx + 1).toString(), margin + 2, y + 5);
                doc.text(row.nombre, margin + 15, y + 5);
                doc.setFont("helvetica", "bold");
                doc.text(row.pts.toString(), margin + 70, y + 5);
                doc.setFont("helvetica", "normal");
                doc.text(row.pj.toString(), margin + 85, y + 5);
                doc.text(row.g.toString(), margin + 100, y + 5);
                doc.text(row.e.toString(), margin + 115, y + 5);
                doc.text(row.p.toString(), margin + 130, y + 5);
                doc.text(row.gf.toString(), margin + 145, y + 5);
                doc.text(row.gc.toString(), margin + 160, y + 5);
                doc.text(row.dg.toString(), margin + 175, y + 5);
                y += 7;
            });

            // --- LEADERBOARD ---
            y += 15;
            if (y > 220) { doc.addPage(); y = 20; }
            doc.setFontSize(14);
            doc.setFont("helvetica", "bold");
            doc.text("LÍDERES INDIVIDUALES", margin, y);
            y += 10;

            const renderLeader = (title, items, colX) => {
                doc.setFontSize(10);
                doc.setFont("helvetica", "bold");
                doc.setTextColor(...primaryColor);
                doc.text(title, colX, y);
                doc.setTextColor(40, 40, 40);
                let ly = y + 6;
                doc.setFontSize(8);
                doc.setFont("helvetica", "normal");
                if (!items || items.length === 0) {
                    doc.text("No hay datos", colX, ly);
                } else {
                    items.slice(0, 5).forEach((it, i) => {
                        doc.text(`${i + 1}. ${it.jugador}`, colX, ly);
                        doc.text(it.total.toString(), colX + 45, ly, { align: 'right' });
                        ly += 5;
                    });
                }
                return ly;
            };

            const yGoles = renderLeader("TOP GOLEADORES", leaderboard.goles, margin);
            const yPorteros = renderLeader("MENOS GOLEADOS", leaderboard.porteros, margin + 60);
            const yTarjetas = renderLeader("AMARILLAS", leaderboard.amarillas, margin + 120);

            y = Math.max(yGoles, yPorteros, yTarjetas) + 20;
            
            // FOOTER
            doc.setFontSize(8);
            doc.setTextColor(150, 150, 150);
            const footerText = "FUTADMIN PRO - Sistema Integral de Gestión Deportiva. Todos los derechos reservados.";
            doc.text(footerText, 105, 285, { align: 'center' });

            doc.save(`Reporte_Historico_${torneo.nombre.replace(/\s+/g, '_')}.pdf`);
            Core.showNotification('PDF generado con éxito', 'success');
        } catch (error) {
            console.error("Error al generar PDF:", error);
            alert('Error al generar el reporte PDF.');
        }
    }
}
