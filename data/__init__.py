from flask import Flask
from datetime import timedelta
from flask_sqlalchemy import SQLAlchemy


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://nyameget:xU9xKSe8zsSaeLqrUeotCAsdWNTzSwXX@dpg-cr938hq3esus73bfgb7g-a.oregon-postgres.render.com/dbname_skju'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = '1567tay'
app.permanent_session_lifetime = timedelta(days=10)
app.secret_key = '1567tay'
UPLOAD_FOLDER = 'static/files'

db = SQLAlchemy(app)

# Plant.id API endpoint
PLANT_ID_API_URL = "https://plant.id/api/v3/identification"
url = "https://plant.id/api/v3/identification?details=common_names,url,description,taxonomy,rank,gbif_id,inaturalist_id,image,synonyms,edible_parts,watering&language=en"

# Replace with your Plant.id API token
PLANT_ID_API_KEY_OLD = "SMVUfdDn8bs2BPxl5m9JYXSnGFOVIaRzAY65DIm9NBTKNJfG7p"
PLANT_ID_API_KEY = "G0SyXknxTXJD0R8DyS5rVWlL9A05s8VrGFaXSGGEmHznnOho1u"

from data import routes
