/**
 * Recurso de Geografía de México
 * Mapeo de Estados y sus Municipios principales.
 */
const MEXICO_GEO = {
    "Aguascalientes": ["Aguascalientes", "Asientos", "Calvillo", "Cosío", "Jesús María", "Pabellón de Arteaga", "Rincón de Romos", "San José de Gracia", "Tepezalá", "El Llano", "San Francisco de los Romo"],
    "Baja California": ["Ensenada", "Mexicali", "Tecate", "Tijuana", "Playas de Rosarito", "San Quintín", "San Felipe"],
    "Baja California Sur": ["Comondú", "Mulegé", "La Paz", "Los Cabos", "Loreto"],
    "Campeche": ["Campeche", "Calkiní", "Carmen", "Champotón", "Hecelchakán", "Hopelchén", "Palizada", "Tenabo", "Escárcega", "Calakmul", "Candelaria", "Seybaplaya", "Dzitbalché"],
    "Chiapas": ["Tuxtla Gutiérrez", "Tapachula", "San Cristóbal de las Casas", "Comitán de Domínguez", "Palenque", "Chiapa de Corzo"],
    "Chihuahua": ["Chihuahua", "Juárez", "Cuauhtémoc", "Delicias", "Hidalgo del Parral", "Nuevo Casas Grandes"],
    "Ciudad de México": ["Álvaro Obregón", "Azcapotzalco", "Benito Juárez", "Coyoacán", "Cuajimalpa de Morelos", "Cuauhtémoc", "Gustavo A. Madero", "Iztacalco", "Iztapalapa", "La Magdalena Contreras", "Miguel Hidalgo", "Milpa Alta", "Tláhuac", "Tlalpan", "Venustiano Carranza", "Xochimilco"],
    "Coahuila": ["Saltillo", "Torreón", "Monclova", "Piedras Negras", "Acuña", "Matamoros", "San Pedro"],
    "Colima": ["Colima", "Manzanillo", "Tecomán", "Villa de Álvarez", "Armería", "Comala"],
    "Durango": ["Durango", "Gómez Palacio", "Lerdo", "Pueblo Nuevo", "Santiago Papasquiaro"],
    "Estado de México": ["Toluca", "Ecatepec", "Nezahualcóyotl", "Naucalpan", "Tlalnepantla", "Chimalhuacán", "Cuautitlán Izcalli", "Huixquilucan"],
    "Guanajuato": ["Guanajuato", "León", "Irapuato", "Celaya", "Salamanca", "Silao", "San Miguel de Allende"],
    "Guerrero": ["Chilpancingo", "Acapulco", "Iguala", "Taxco", "Zihuatanejo", "Tlapa"],
    "Hidalgo": ["Pachuca", "Tulancingo", "Tula", "Ixmiquilpan", "Huejutla"],
    "Jalisco": ["Guadalajara", "Zapopan", "Tlaquepaque", "Tonalá", "Tlajomulco", "Puerto Vallarta", "Lagos de Moreno"],
    "Michoacán": ["Morelia", "Uruapan", "Zamora", "Lázaro Cárdenas", "Pátzcuaro", "Zitácuaro"],
    "Morelos": ["Cuernavaca", "Jiutepec", "Cuautla", "Temixco", "Yautepec"],
    "Nayarit": ["Tepic", "Bahía de Banderas", "Santiago Ixcuintla", "Compostela"],
    "Nuevo León": ["Monterrey", "Guadalupe", "San Nicolás de los Garza", "Apodaca", "Escobedo", "Santa Catarina", "San Pedro Garza García"],
    "Oaxaca": ["Oaxaca de Juárez", "San Juan Bautista Tuxtepec", "Salina Cruz", "Juchitán de Zaragoza"],
    "Puebla": ["Puebla", "Tehuacán", "San Martín Texmelucan", "Cholula", "Atlixco"],
    "Querétaro": ["Querétaro", "San Juan del Río", "El Marqués", "Corregidora"],
    "Quintana Roo": ["Cancún (Benito Juárez)", "Playa del Carmen (Solidaridad)", "Chetumal (Othón P. Blanco)", "Cozumel"],
    "San Luis Potosí": ["San Luis Potosí", "Soledad de Graciano Sánchez", "Ciudad Valles", "Matehuala"],
    "Sinaloa": ["Culiacán", "Mazatlán", "Los Mochis (Ahome)", "Guasave"],
    "Sonora": ["Hermosillo", "Ciudad Obregón (Cajeme)", "Nogales", "San Luis Río Colorado", "Navojoa", "Guaymas"],
    "Tabasco": ["Villahermosa (Centro)", "Cárdenas", "Comalcalco", "Huimanguillo"],
    "Tamaulipas": ["Ciudad Victoria", "Reynosa", "Matamoros", "Nuevo Laredo", "Tampico", "Madero", "Altamira"],
    "Tlaxcala": ["Tlaxcala", "Apizaco", "Huamantla", "Chiautempan"],
    "Veracruz": ["Xalapa", "Veracruz", "Coatzacoalcos", "Boca del Río", "Orizaba", "Córdoba", "Poza Rica"],
    "Yucatán": ["Mérida", "Progreso", "Tizimín", "Valladolid", "Kanasín"],
    "Zacatecas": ["Zacatecas", "Fresnillo", "Guadalupe", "Jerez", "Río Grande"]
};

if (typeof window !== 'undefined') {
    window.MEXICO_GEO = MEXICO_GEO;
}
