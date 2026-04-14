import os
import uuid
from PIL import Image
from flask import request, jsonify, current_app
from werkzeug.utils import secure_filename
import cloudinary
import cloudinary.uploader
import cloudinary.api

def paginate_query(query, renderer=None):
    """Universal helper for paginated SQLAlchemy queries."""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    
    items = pagination.items
    processed_items = []
    for item in items:
        try:
            if renderer:
                processed_items.append(renderer(item))
            else:
                processed_items.append(item.to_dict())
        except Exception as e:
            import traceback
            print(f"Error serializing item {getattr(item, 'id', '?')}: {e}")
            processed_items.append({
                "id": getattr(item, 'id', None),
                "error": "Serialization failed",
                "details": str(e)
            })
            
    return jsonify({
        'items': processed_items,
        'pagination': {
            'page': pagination.page,
            'per_page': pagination.per_page,
            'total_items': pagination.total,
            'total_pages': pagination.pages,
            'has_next': pagination.has_next,
            'has_prev': pagination.has_prev
        }
    })

def handle_image_upload(file, folder=None):
    """
    Procesa, comprime y guarda una imagen.
    Retorna la URL relativa si tiene éxito, o None si falla.
    """
    if not file or file.filename == '':
        return None, "Archivo no válido"

    if not folder:
        folder = current_app.config.get('UPLOAD_FOLDER')
    
    if not folder:
        # Fallback de emergencia a ruta absoluta estándar en Railway
        folder = "/app/static/uploads"
    
    os.makedirs(folder, exist_ok=True)

    try:
        # Verificar si Cloudinary está configurado
        cloudinary_url = os.environ.get('CLOUDINARY_URL') or current_app.config.get('CLOUDINARY_URL')
        if cloudinary_url:
            # Subir directo a Cloudinary sin guardar localmente
            upload_result = cloudinary.uploader.upload(
                file,
                folder="futadmin_uploads",
                resource_type="image",
                transformation=[
                    {'width': 800, 'height': 800, 'crop': 'limit'},
                    {'quality': 'auto:good'},
                    {'fetch_format': 'auto'}
                ]
            )
            # Retornamos la URL segura de Cloudinary (https://...)
            return upload_result.get('secure_url'), None
    except Exception as e:
        print(f"Error subiendo a Cloudinary: {e}, intentando fallback local...")

    try:
        # ---------------- FALLBACK LOCAL (RAILWAY EPÍMERO) ----------------
        file.seek(0)
        img = Image.open(file)
        if img.mode in ("RGBA", "P"):
            img = img.convert("RGB")
        max_size = (800, 800)
        img.thumbnail(max_size, Image.Resampling.LANCZOS)
        unique_name = f"{uuid.uuid4().hex}.jpg"
        save_path = os.path.join(folder, unique_name)
        img.save(save_path, "JPEG", optimize=True, quality=70)
        return f"/static/uploads/{unique_name}", None
    except Exception as e:
        print(f"Error procesando imagen: {e}")
        # Intento de fallback: guardar archivo original si Pillow falla
        try:
            filename = secure_filename(f"{uuid.uuid4().hex}_{file.filename}")
            file.seek(0)
            file.save(os.path.join(folder, filename))
            return f"/static/uploads/{filename}", None
        except Exception as e2:
            return None, str(e2)
