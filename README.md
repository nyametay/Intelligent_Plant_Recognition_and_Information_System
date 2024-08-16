Intelligent Plant Identification and Information System

Welcome to the Intelligent Plant Identification and Information System repository! This project leverages an external API to identify plant species from images and provide detailed information about them. The system is built using Flask for the backend.

Table of Contents
1. Introduction
2. Features
3. Installation
4. Usage
5. Project Structure
6. Contact

Introduction

This project aims to create a web application that can identify plant species from uploaded images and provide comprehensive information about them using an external API. The system offers a user-friendly interface and a robust backend to handle image processing and API interactions.

Features
1. Plant Identification: Recognizes plant species from images using an external API.
2. Information Retrieval: Provides detailed information about the identified plant species.
3. User-Friendly Interface: A simple and intuitive web interface for easy interaction.
4. Scalable Architecture: Designed to handle multiple requests and large datasets.

Installation

Follow these steps to set up the project on your local machine:

Prerequisites
1. Python 3.7+
2. Flask
3. HTML, CSS, and JavaScript knowledge
4. Virtual environment tools (optional but recommended)
5. API access (ensure you have access to the required external API)

Clone the Repository
1. git clone https://github.com/nyameget/plant_identification_system.git
2. cd plant_identification_system

Set Up the Virtual Environment
1. python3 -m venv venv
2. source venv/bin/activate  # On Windows use `venv\Scripts\activate`

Install the Dependencies
1. pip install -r requirements.txt

Usage

Running the Application
1. flask run
2. Navigate to http://127.0.0.1:5000/ in your web browser to use the application.

Uploading an Image
1. Click on the "Upload Image" button.
2. Select an image file from your computer.
3. The system will process the image, identify the plant species, and display detailed information about the plant.

Project Structure

gender-age-classification_system/

├── app/

│   ├── static/

│   │   ├── css/

│   │   │   └── styles.css

│   │   ├── js/

│   │   │   └── script.js

│   ├── templates/

│   │   └── index.html

│   ├── __init__.py

│   ├── routes.py

│   └── model.py

├── models/

│   └── gender_age_model.h5

├── tests/

│   └── test_app.py

├── .gitignore

├── README.md

├── requirements.txt

└── run.py

1. app/: Contains the Flask application files.
2. static/: Contains static files (CSS, JavaScript).
3. templates/: Contains HTML templates.
4. __init__.py: Initializes the Flask app.
5. routes.py: Contains the route definitions.
6. model.py: Contains the machine learning model loading and prediction logic.
7. models/: Contains the pre-trained machine learning models.
8. tests/: Contains test files.
9. .gitignore: Specifies files and directories to be ignored by Git.
10. README.md: This README file.
11. requirements.txt: Lists the Python dependencies.
12. run.py: The entry point to run the Flask application.

Contact

For any inquiries or feedback, please contact nyameget@gmail.com.

Thank you for visiting our repository! We hope you find this project useful and interesting.
