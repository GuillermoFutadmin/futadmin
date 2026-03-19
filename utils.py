from flask import request, jsonify

def paginate_query(query, renderer=None):
    """Universal helper for paginated SQLAlchemy queries."""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    
    items = pagination.items
    if renderer:
        items = [renderer(item) for item in items]
    else:
        items = [item.to_dict() for item in items]
        
    return jsonify({
        'items': items,
        'pagination': {
            'page': pagination.page,
            'per_page': pagination.per_page,
            'total_items': pagination.total,
            'total_pages': pagination.pages,
            'has_next': pagination.has_next,
            'has_prev': pagination.has_prev
        }
    })
