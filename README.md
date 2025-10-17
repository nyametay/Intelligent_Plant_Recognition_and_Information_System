# 🌿 Intelligent Plant Recognition System

An AI-powered web application that identifies plants, detects diseases, and provides detailed information such as scientific names, taxonomy, watering needs, and uses — all in one place.  
Built with **Flask**, **TensorFlow**, **BeautifulSoup**, and **Tailwind CSS**.

This system bridges the gap between **botany** and **artificial intelligence**, providing an interactive and educational way to explore the plant world.  
Whether you’re a **botanist**, **gardener**, **student**, or **AI enthusiast**, this platform helps you recognize plants, learn about their characteristics, and understand how to care for them.  

The app uses a **deep learning model** to analyze plant images and detect diseases, while an intelligent **data retrieval module** scrapes verified online sources (like PFAF and Wikipedia) to deliver accurate, organized, and human-readable information about each identified plant.

---

## 🧭 Key Highlights

- 🌱 **AI-Powered Plant Recognition** — Upload or capture any plant photo and get its exact species prediction.
- 🔍 **Disease Detection** — Detect common diseases (leaf spots, blight, rot, etc.) with severity categorization.
- 📚 **Comprehensive Plant Info** — Includes taxonomy, scientific name, description, and watering guide.
- 🧪 **Use Case Insights** — Displays medicinal, edible, ornamental, and industrial uses.
- 🌤️ **Beautiful & Responsive UI** — Designed with Tailwind CSS and dark mode support.
- 🔗 **Smart Fallback System** — Auto-generates a Google search link when specific data isn’t found.
- ⚡ **Fast & Lightweight** — Optimized for both desktop and mobile users.
- 🔒 **Environment-Friendly Config** — Secure `.env` API key management for integrations.

---

## 🧠 Tech Stack

| Category | Tools |
|-----------|--------|
| **Frontend** | HTML5, Jinja2, Tailwind CSS, JavaScript |
| **Backend** | Flask (Python) |
| **AI/ML** | TensorFlow / Keras (CNN for classification) |
| **Web Scraping** | BeautifulSoup4, Requests |
| **Database** | SQLite / SQLAlchemy (for persistent data) |
| **API Integration** | Google Custom Search API |
| **Media Processing** | OpenCV |
| **Environment Management** | Python-Dotenv |
| **Deployment** | Render / Railway / Heroku |

---

## 🧩 Folder Structure

📁 intelligent-plant-recognition-system
│
├── app.py                        # Main Flask application entry point
├── requirements.txt               # Python dependencies
│
├── data/                          # Core backend logic and templates
│   ├── __init__.py                # Initializes the Flask app
│   ├── routes.py                  # Defines all application routes
│   ├── module.py                  # Handles model prediction logic
│   ├── plant_modules.py           # Processes plant and disease data
│   ├── models.py                  # SQLAlchemy models and database structure
│   ├── scraping.py                # Web scraping logic for plant data
│
│   ├── templates/                 # All HTML templates
│   │   ├── partials/              # Reusable components (base, navbar, footer)
│   │   │   ├── base.html
│   │   │   ├── navbar.html
│   │   │   └── footer.html
│   │   ├── pages/                 # Main app pages
│   │   │   ├── home.html
│   │   │   ├── result.html
│   │   │   ├── history.html
│   │   │   ├── search_by_text.html
│   │   │   ├── search_result.html
│   │   │   └── about.html
│
│   ├── static/                    # Static files (frontend assets)
│   │   ├── css/                   # Stylesheets
│   │   │   ├── style.css
│   │   │   ├── homeform.css
│   │   │   └── card.css
│   │   ├── scripts/               # JavaScript files
│   │   │   ├── preview.js
│   │   │   ├── darkmode.js
│   │   │   └── main.js
│   │   ├── images/                # Images and icons
│   │   │   ├── logo.png
│   │   │   └── icons/
│   │   └── uploads/               # Uploaded plant images
│
└── README.md

---

## 🚀 Installation & Setup

### 1️⃣ Clone the Repository
```bash
git clone https://github.com/yourusername/intelligent-plant-recognition-system.git
cd intelligent-plant-recognition-system
```

## 2️⃣ Create a Virtual Environment
```bash
python -m venv venv
source venv/bin/activate       # On Windows: venv\Scripts\activate
```

## 3️⃣ Install Dependencies
```bash
pip install -r requirements.txt
```

## 4️⃣ Add Environment Variables
Create a .env file in the root directory and add your credentials:
```ini
GOOGLE_API_KEY=your_google_api_key
GOOGLE_CSE_ID=your_custom_search_engine_id
```

## 5️⃣ Run the Application
```bash
python app.py
```

Visit:
```cpp
http://127.0.0.1:5000
```

## 🧩 How It Works
- The user uploads or captures an image of a plant.
- The TensorFlow CNN model predicts the plant species and detects any visible disease.
- The backend uses BeautifulSoup to scrape verified sources for additional plant details.
- Data is organized and rendered dynamically using Flask Jinja2 templates.
- If data is missing, the app generates a Google search link for further exploration.
- Each identified plant is stored in history for later reference.

## 🧪 Example Output (JSON)
```json
{
  "results": {
    "common_name": "Aloe Vera",
    "name": "Aloe barbadensis",
    "taxonomy": {
      "kingdom": "Plantae",
      "family": "Asphodelaceae",
      "genus": "Aloe"
    },
    "watering": "Moderate watering required, avoid overwatering.",
    "description": "Aloe vera is a succulent plant species known for its medicinal properties.",
    "disease_name": "Leaf Spot",
    "disease_category": "Mild",
    "disease_description": "Caused by fungal infection resulting in brown lesions.",
    "plant_uses": {
      "Medicinal Uses": ["Treats burns", "Improves skin health"],
      "Edible Uses": ["Used in drinks and smoothies"],
      "Other Uses": ["Cosmetic and skincare industry"]
    }
  }
}
```

## 📜 Requirements
```nginx
Flask
beautifulsoup4
requests
opencv-python
python-dotenv
sqlalchemy
gunicorn
```

## Install all dependencies:
```bash
pip install -r requirements.txt
```

## ☁️ Deployment (Render / Railway / Heroku)
- Push your code to GitHub.
- Add environment variables (GOOGLE_API_KEY, GOOGLE_CSE_ID) in the deployment dashboard.
- Use the following Procfile entry:

```makefile
web: gunicorn app:app
Deploy the project — it will automatically launch your Flask web app.
```

## 👨‍💻 Developer Info
Developer: Isaac Nyame Taylor
Year: 2025

## 📄 License
This project is licensed under the MIT License — free for personal and academic use with attribution.

## ⭐ Support
If you find this project useful, don’t forget to star ⭐ the repository on GitHub!
Your support helps improve the project and inspire new AI-driven innovations.

“🌾 Empowering environmental awareness through AI and intelligent automation.”
