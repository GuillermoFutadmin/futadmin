from flask import Blueprint, request, jsonify
from models import db, Cancha, PagoCancha, Partido
from sqlalchemy import func

pagos_cancha_bp = Blueprint('pagos_cancha', __name__)

@pagos_cancha_bp.route('/api/canchas/<int:cancha_id>/estado_cuenta', methods=['GET'])
def get_estado_cuenta(cancha_id):
    cancha = Cancha.query.get_or_404(cancha_id)
    
    # Calcular uso (solo para canchas Rentadas, si es Propia o Gratuita no hay "deuda")
    total_uso = 0.0
    desglose_uso = []
    
    if cancha.tipo == 'Rentada':
        # Partidos programados en esta cancha
        partidos = Partido.query.filter_by(cancha=cancha.nombre).all()
        for p in partidos:
            if cancha.unidad_cobro == 'Partido':
                costo = cancha.costo_renta
            else:
                # Simplificación temporal si es por Hora o Día
                costo = cancha.costo_renta
                
            total_uso += costo
            desglose_uso.append({
                "fecha": p.fecha.strftime('%Y-%m-%d') if p.fecha else "Sin fecha",
                "descripcion": f"Partido: {p.equipo_local.nombre if p.equipo_local else '?'} vs {p.equipo_visitante.nombre if p.equipo_visitante else '?'}",
                "monto": costo
            })
    
    # Calcular pagos realizados
    pagos = PagoCancha.query.filter_by(cancha_id=cancha_id).order_by(PagoCancha.fecha.desc()).all()
    total_pagado = sum(p.monto for p in pagos)
    
    saldo_pendiente = total_uso - total_pagado
    
    return jsonify({
        "cancha_id": cancha.id,
        "cancha_nombre": cancha.nombre,
        "tipo": cancha.tipo,
        "costo_renta": cancha.costo_renta,
        "unidad_cobro": cancha.unidad_cobro,
        "total_uso": total_uso,
        "total_pagado": total_pagado,
        "saldo_pendiente": saldo_pendiente,
        "pagos": [p.to_dict() for p in pagos],
        "desglose_uso": desglose_uso
    })

@pagos_cancha_bp.route('/api/pagos_cancha', methods=['GET'])
def get_all_pagos_canchas():
    pagos = PagoCancha.query.order_by(PagoCancha.fecha.desc()).all()
    return jsonify([p.to_dict() for p in pagos])

@pagos_cancha_bp.route('/api/pagos_cancha', methods=['POST'])
def add_pago_cancha():
    data = request.get_json()
    if not data or not data.get('cancha_id') or not data.get('monto'):
        return jsonify({"error": "cancha_id y monto requeridos"}), 400
        
    pago = PagoCancha(
        cancha_id=data['cancha_id'],
        monto=float(data['monto']),
        comprobante_url=data.get('comprobante_url'),
        notas=data.get('notas')
    )
    
    db.session.add(pago)
    db.session.commit()
    
    return jsonify(pago.to_dict()), 201

@pagos_cancha_bp.route('/api/pagos_cancha/<int:id>', methods=['DELETE'])
def delete_pago_cancha(id):
    pago = PagoCancha.query.get_or_404(id)
    db.session.delete(pago)
    db.session.commit()
    return jsonify({"message": "Pago eliminado exitosamente"})
