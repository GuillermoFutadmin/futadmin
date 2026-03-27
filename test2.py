import sys
import unittest.mock as mock
sys.modules['cloudinary'] = mock.MagicMock()
sys.modules['cloudinary.uploader'] = mock.MagicMock()
sys.modules['cloudinary.utils'] = mock.MagicMock()

from app import app
from models import Liga

try:
    with app.app_context():
        l = Liga.query.first()
        if l:
            d = l.to_dict()
            print("To dict finished successfully")
        else:
            print("No ligas found")
except Exception as e:
    import traceback
    traceback.print_exc()
