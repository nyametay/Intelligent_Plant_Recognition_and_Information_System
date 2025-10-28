from flask import Flask
import base64
from datetime import timedelta
from flask_sqlalchemy import SQLAlchemy


app = Flask(__name__, template_folder='./templates')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///data.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = '1567tay'
app.permanent_session_lifetime = timedelta(days=10)
app.secret_key = '1567tay'
UPLOAD_FOLDER = 'static/files'

# ✅ Allow larger image uploads (e.g., up to 50 MB)
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50 MB

db = SQLAlchemy(app)

# Plant.id API endpoint
PLANT_ID_API_URL = "https://plant.id/api/v3/identification"
url = "https://plant.id/api/v3/identification?details=common_names,url,description,taxonomy,rank,gbif_id,inaturalist_id,image,synonyms,edible_parts,watering&language=en"

# Replace with your Plant.id API token
PLANT_ID_API_KEY_OLD = "SMVUfdDn8bs2BPxl5m9JYXSnGFOVIaRzAY65DIm9NBTKNJfG7p"
PLANT_ID_API_KEY = "G0SyXknxTXJD0R8DyS5rVWlL9A05s8VrGFaXSGGEmHznnOho1u"

# Custom Jinja2 filter for base64 encoding
@app.template_filter('b64encode')
def b64encode_filter(data):
    """Encode binary data as base64 for safe HTML embedding."""
    if data is None:
        return ''
    return base64.b64encode(data).decode('utf-8')

from data import routes

