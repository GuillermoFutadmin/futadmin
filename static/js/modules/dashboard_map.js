
export class DashboardMap {
    constructor() {
        this.map = null;
        this.markers = [];
        this.geoLayer = null; // Grupo para los polígonos de perímetros
        this.stateGeoData = {}; // Caché de datos GeoJSON por estado
        this.initialViewSet = false; // Bandera para evitar saltos en actualizaciones
    }

    init() {
        const mapContainer = document.getElementById('mexico-map');
        if (!mapContainer || this.map) return;

        if (typeof L === 'undefined') {
            console.warn('Leaflet (L) no está disponible. El mapa ha sido deshabilitado.');
            return;
        }

        // Inicializar mapa centrado en México
        this.map = L.map('mexico-map', {
            center: [23.6345, -102.5528],
            zoom: 5,
            zoomControl: false,
            attributionControl: false
        });

        // Capa de mapa oscuro (CartoDB Dark Matter)
        L.tileLayer('https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png', {
            subdomains: 'abcd',
            maxZoom: 19
        }).addTo(this.map);

        // Grupo para perímetros (debajo de los marcadores)
        this.geoLayer = L.featureGroup().addTo(this.map);

        // Añadir control de zoom en una posición más discreta
        L.control.zoom({ position: 'bottomleft' }).addTo(this.map);
    }

    async loadStateGeoJSON(stateName) {
        if (this.stateGeoData[stateName]) return this.stateGeoData[stateName];
        
        try {
            // URL oficial de PhantomInsights para los límites municipales de México (2023)
            const url = `https://raw.githubusercontent.com/PhantomInsights/mexico-geojson/main/2023/states/${encodeURIComponent(stateName)}.json`;
            const response = await fetch(url);
            if (!response.ok) throw new Error('GeoJSON no encontrado');
            const data = await response.json();
            this.stateGeoData[stateName] = data;
            return data;
        } catch (error) {
            console.error(`Error cargando GeoJSON para ${stateName}:`, error);
            return null;
        }
    }

    async update(geoStatsList) {
        if (!this.map) this.init();
        if (!this.map || typeof L === 'undefined') return;

        // Limpiar marcadores y polígonos previos
        try {
            this.markers.forEach(m => this.map.removeLayer(m));
        } catch(e) {}
        this.markers = [];
        this.geoLayer.clearLayers();

        const stateCoords = window.MEXICO_STATE_COORDS || {};
        const munCoords = window.MEXICO_MUN_COORDS || {};

        const applyJitter = (coords) => {
            const jitter = 0.05; 
            return [
                coords[0] + (Math.random() - 0.5) * jitter,
                coords[1] + (Math.random() - 0.5) * jitter
            ];
        };

        for (const stat of geoStatsList) {
            const munKey = `${stat.estado}|${stat.municipio}`;
            const baseCoords = munCoords[munKey] || stateCoords[stat.estado];

            if (baseCoords) {
                // --- 1. Renderizar Perímetro (GeoJSON) ---
                const geoData = await this.loadStateGeoJSON(stat.estado);
                if (geoData) {
                    // Filtrar la entidad del municipio
                    // Las propiedades comunes son NOMGEO o municipio
                    const feature = geoData.features.find(f => 
                        f.properties.NOMGEO.toLowerCase().includes(stat.municipio.toLowerCase()) ||
                        stat.municipio.toLowerCase().includes(f.properties.NOMGEO.toLowerCase())
                    );

                    if (feature) {
                        L.geoJSON(feature, {
                            style: {
                                color: '#00ff88', 
                                weight: 2,
                                opacity: 0.8,
                                fillColor: '#00ff88',
                                fillOpacity: 0.15
                            },
                            onEachFeature: (f, layer) => {
                                const sedesHtml = stat.sedes_lista && stat.sedes_lista.length > 0 
                                    ? `<ul style="margin: 5px 0; padding-left: 15px; font-size: 0.85rem; color: #00ff88; list-style-type: disc;">
                                        ${stat.sedes_lista.map(s => `<li>${s}</li>`).join('')}
                                       </ul>`
                                    : '<p style="font-size: 0.85rem; color: var(--text-muted); font-style: italic;">Sin sedes registradas</p>';

                                layer.bindPopup(`
                                    <div style="color: #fff; padding: 15px; font-family: 'Outfit', sans-serif; min-width: 200px;">
                                        <strong style="font-size: 1.1rem; display: block; margin-bottom: 8px; color: #00ff88; border-bottom: 1px solid rgba(0,255,136,0.2); padding-bottom: 5px;">${stat.municipio}</strong>
                                        <div style="font-size: 0.9rem; margin-bottom: 5px; font-weight: 600;">
                                            🏟️ Sedes Activas (${stat.sedes}):
                                        </div>
                                        ${sedesHtml}
                                        <div style="margin-top: 10px; padding-top: 8px; border-top: 1px solid rgba(255,255,255,0.1); display: flex; justify-content: space-between; align-items: center;">
                                            <span style="font-size: 0.85rem; color: #3b82f6;">👥 Equipos:</span>
                                            <span style="font-size: 1rem; font-weight: bold; color: #3b82f6;">${stat.equipos}</span>
                                        </div>
                                        <div style="font-size: 0.7rem; color: #00ff88; margin-top: 8px; text-align: center; font-style: italic;">(Haz clic para ampliar e info)</div>
                                    </div>
                                `, { className: 'premium-popup', closeButton: true, offset: [0, -5], autoPan: false });

                                layer.on({
                                    mouseover: (e) => {
                                        const l = e.target;
                                        l.setStyle({ fillOpacity: 0.4, weight: 3, color: '#00ff88' });
                                    },
                                    mouseout: (e) => {
                                        const l = e.target;
                                        l.setStyle({ fillOpacity: 0.15, weight: 2, color: '#00ff88' });
                                    },
                                    click: (e) => {
                                        // Comentado para evitar desplazamientos molestos al hacer clic
                                        // this.map.fitBounds(e.target.getBounds(), { padding: [20, 20] });
                                    }
                                });
                            }
                        }).addTo(this.geoLayer);
                    }
                }

                // --- 2. Renderizar Equipos (Agrupados por Colonia/GeoJSON para evitar solapamientos) ---
                if (stat.equipos_lista && stat.equipos_lista.length > 0) {
                    // Agrupar equipos que comparten el mismo GeoJSON exacto
                    const groupedByGeo = {};
                    stat.equipos_lista.forEach(equipo => {
                        if (equipo.colonia_geojson) {
                            if (!groupedByGeo[equipo.colonia_geojson]) {
                                groupedByGeo[equipo.colonia_geojson] = [];
                            }
                            groupedByGeo[equipo.colonia_geojson].push(equipo);
                        }
                    });

                    Object.keys(groupedByGeo).forEach(geojsonStr => {
                        const equiposInGeo = groupedByGeo[geojsonStr];
                        const count = equiposInGeo.length;
                        const firstEquipo = equiposInGeo[0];
                        const color = firstEquipo.color || '#3b82f6';
                        const coloniaName = firstEquipo.colonia || 'Sin Colonia';

                        // Construir Popup Multiequipo o Simple
                        let popupContent = `
                        <div style="color: #fff; padding: 15px; font-family: 'Outfit', sans-serif; min-width: 260px;">
                            <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 10px; color: var(--primary);">
                                <span style="font-size: 1.2rem;">📍</span>
                                <strong style="font-size: 1rem;">${coloniaName}</strong>
                            </div>
                            <div style="font-size: 0.8rem; color: var(--text-muted); margin-bottom: 15px; border-bottom: 1px solid rgba(255,255,255,0.1); padding-bottom: 8px;">
                                ${stat.municipio}, ${stat.estado}
                            </div>
                        `;

                        equiposInGeo.forEach(eq => {
                            const st = eq.stats || { goles: 0, pj: 0, victorias: 0 };
                            popupContent += `
                                <div style="margin-bottom: 12px; padding: 10px; background: rgba(255,255,255,0.05); border-radius: 8px; border-left: 4px solid ${eq.color || color};">
                                    <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 8px;">
                                        <img src="${eq.escudo_url || ''}" style="width: 35px; height: 35px; object-fit: contain; border-radius: 6px; background: rgba(255,255,255,0.1);">
                                        <div style="display: flex; flex-direction: column;">
                                            <span style="font-size: 0.95rem; font-weight: 700; color: #fff; line-height: 1.1;">${eq.nombre}</span>
                                            <span style="font-size: 0.75rem; color: #00ff88; font-weight: 500;">${eq.liga_nombre || 'Independiente'}</span>
                                        </div>
                                    </div>
                                    <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 5px; text-align: center;">
                                        <div style="background: rgba(0,0,0,0.3); padding: 4px; border-radius: 4px;">
                                            <div style="font-size: 0.6rem; color: var(--text-muted); text-transform: uppercase;">PJ</div>
                                            <div style="font-size: 0.85rem; font-weight: 700; color: #fff;">${st.pj}</div>
                                        </div>
                                        <div style="background: rgba(0,0,0,0.3); padding: 4px; border-radius: 4px;">
                                            <div style="font-size: 0.6rem; color: var(--text-muted); text-transform: uppercase;">Goles</div>
                                            <div style="font-size: 0.85rem; font-weight: 700; color: #00ff88;">${st.goles}</div>
                                        </div>
                                        <div style="background: rgba(0,0,0,0.3); padding: 4px; border-radius: 4px;">
                                            <div style="font-size: 0.6rem; color: var(--text-muted); text-transform: uppercase;">Victorias</div>
                                            <div style="font-size: 0.85rem; font-weight: 700; color: #fbbf24;">${st.victorias}</div>
                                        </div>
                                    </div>
                                </div>
                            `;
                        });

                        popupContent += `</div>`;

                        try {
                            const geojsonFeature = JSON.parse(geojsonStr);
                            const teamLayer = L.geoJSON(geojsonFeature, {
                                style: {
                                    color: '#3b82f6',
                                    weight: 3,
                                    opacity: 0.9,
                                    fillColor: color,
                                    fillOpacity: 0.3
                                },
                                pointToLayer: (f, l) => null, // Ocultar puntos
                                onEachFeature: (feature, layer) => {
                                    if (layer.bindPopup) {
                                        layer.bindPopup(popupContent, { className: 'premium-popup', closeButton: true, autoPan: false });
                                        layer.on('mouseover', function(e) { 
                                            this.setStyle({ fillOpacity: 0.6, weight: 4 });
                                        });
                                        layer.on('mouseout', function(e) { 
                                            this.setStyle({ fillOpacity: 0.3, weight: 3 });
                                        });
                                    }
                                }
                            }).addTo(this.map);

                            if (teamLayer.getLayers().length > 0) {
                                this.markers.push(teamLayer);
                            }
                        } catch(e) {
                            console.error('Error procesando Geometría de equipo grouped', e);
                        }
                    });
                }
            }
        }

        // Auto-zoom a las áreas con datos (Solo la primera vez)
        if (geoStatsList.length > 0 && !this.initialViewSet) {
            const allCoords = geoStatsList
                .map(s => munCoords[`${s.estado}|${s.municipio}`] || stateCoords[s.estado])
                .filter(c => c);

            if (allCoords.length === 1) {
                this.map.setView(allCoords[0], 9); 
                this.initialViewSet = true;
            } else if (allCoords.length > 1) {
                const bounds = L.latLngBounds(allCoords);
                this.map.fitBounds(bounds, { padding: [50, 50] });
                this.initialViewSet = true;
            }
        }
    }
}
