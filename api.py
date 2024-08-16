from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from bs4 import BeautifulSoup
import urllib.parse
import requests
import wikipediaapi
import base64
import os

app = Flask(__name__)

# Configuration
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'postgresql://nyameget:77Gsoy3wKIUf96VTGcp8rbdjlPsKeFqx@dpg-cq1ed02j1k6c73bstmig-a.oregon-postgres.render.com/final_project_t2zo')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Define your database model

class User(db.Model):
    __tablename__ = 'users'
    username = db.Column(db.String(50), primary_key=True, unique=True, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(255), unique=True, nullable=False)  # Store plain text password
    images = db.relationship('Plant', backref='user', lazy=True)

class Plant(db.Model):
    __tablename__ = 'plants'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    filename = db.Column(db.String(255), nullable=False)
    image_data = db.Column(db.LargeBinary, nullable=False)
    plant_info = db.Column(db.JSON, nullable=False)
    plant_uses = db.Column(db.JSON, nullable=False)
    username = db.Column(db.String(50), db.ForeignKey('users.username'), nullable=False)

class Comment(db.Model):
    __tablename__ = 'comments'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    comment = db.Column(db.Text, nullable=False)
    rate = db.Column(db.Integer, nullable=False)
    username = db.Column(db.String(50), db.ForeignKey('users.username'), nullable=False)

def search_pfaf_by_name(name):
  search_url = f"https://pfaf.org/user/DatabaseSearhResult.aspx?CName=%{urllib.parse.quote(name)}%"
  response = requests.get(search_url)
  soup = BeautifulSoup(response.text, 'html.parser')
  return soup.find('table', id='ContentPlaceHolder1_gvresults')

### This finds the exact page url and the latin name of the plant 
def find_plant_page_by_name(common_name, botanical_name):
  result_table = search_pfaf_by_name(common_name)
  botanical_name = botanical_name.split(' ')[0]
  if not result_table and len(common_name.split()) > 1:
    parts = common_name.split()
    result_table_a = search_pfaf_by_name(parts[0])
    result_table_b = search_pfaf_by_name(parts[1])
  else:
    result_table_b = result_table_a = result_table
  ### This checks the table for the reult that best describes the searched plant
  def check_table(result_table):
    if not result_table:
      return None, None
    rows = result_table.find_all('tr')[1:]  # Skip the header row
    for row in rows:
      columns = row.find_all('td')
      if len(columns) < 2:
        continue
      latin_name = columns[0].get_text().strip()
      common_name_ = columns[1].get_text().strip()
      if botanical_name.lower() in latin_name.lower() or common_name.lower() in common_name_.lower():
        return latin_name, f"https://pfaf.org/user/Plant.aspx?LatinName={urllib.parse.quote(latin_name)}"
    return None, None

  latin_name, plant_page_url = check_table(result_table_a)
  if not plant_page_url:
    latin_name, plant_page_url = check_table(result_table_b)

  return latin_name, plant_page_url

def scrape_medical_uses(soup):
  # Find the section containing Edible Uses
  medicinal_uses_section = soup.find('h2', string='Medicinal Uses')
  
  if not medicinal_uses_section:
    print("Medicinal Uses section not found on the page")
    return None
  
  # Find the parent div with class 'boots3' containing Edible Uses content
  boots2_div = medicinal_uses_section.find_next('div', class_='boots2')
  
  if not boots2_div:
    print("Unable to locate the 'boots3' class for Medicnal Uses")
    return None
  
  # Initialize content to collect text
  medicinal_uses = []
  
  # Extract the content within the 'boots3' class
  next_element = boots2_div.find_next()
  
  while next_element:
    # Check if we've reached the end marker (small tag with text-muted class)
    if next_element.name == 'small' and 'text-muted' in next_element.get('class', []):
      break
    
    # Remove <br> tags
    for br_tag in next_element.find_all('br'):
      br_tag.replace_with('\n')  # Replace <br> with newline
    
    # Remove <i> tags and their content
    for i_tag in next_element.find_all('i'):
      i_tag.decompose()  # Completely remove <i> tags and their content
    # Check for "Edible Part" text followed by <a> tags
    if len(next_element.find_all('a')) == 0:
      medicinal_uses.append(next_element.get_text(strip=True))
    else:
      medicinal_uses.append(next_element.find_all(string=True)[-2]) 
    next_element = next_element.find_next_sibling()
  
  return medicinal_uses 

def scrape_edible_uses(soup):
  # Find the section containing Edible Uses
  edible_uses_section = soup.find('h2', string='Edible Uses')
  
  if not edible_uses_section:
    print("Edible Uses section not found on the page")
    return None
  
  # Find the parent div with class 'boots3' containing Edible Uses content
  boots3_div = edible_uses_section.find_next('div', class_='boots3')
  
  if not boots3_div:
    print("Unable to locate the 'boots3' class for Edible Uses")
    return None
  
  # Initialize content to collect text
  edible_parts = []
  edible_uses = []
  
  # Extract the content within the 'boots3' class
  next_element = boots3_div.find_next()
  
  while next_element:
    # Check if we've reached the end marker (small tag with text-muted class)
    if next_element.name == 'small' and 'text-muted' in next_element.get('class', []):
      break
    
    # Remove <br> tags
    for br_tag in next_element.find_all('br'):
      br_tag.replace_with('\n')  # Replace <br> with newline
    
    # Remove <i> tags and their content
    for i_tag in next_element.find_all('i'):
      i_tag.decompose()  # Completely remove <i> tags and their content
    # Check for "Edible Part" text followed by <a> tags
    if "Edible Part" in next_element.get_text():
      edible_part_tags = next_element.find_all('a')
      for tag in edible_part_tags:
        edible_parts.append(tag.get_text(separator='\n', strip=True))

    # Check for "Edible Use"
    if 'Edible Uses' in next_element.get_text():
      edible_uses.append(next_element.find_all(string=True)[-2]) 
    else:
      edible_uses.append(next_element.get_text(strip=True))
    next_element = next_element.find_next_sibling()
  
  return edible_parts, edible_uses 

def scrape_other_uses(soup):
    # Find the section containing Edible Uses
    other_uses_section = soup.find('h2', string='Other Uses')
    
    if not other_uses_section:
      print("Other Uses section not found on the page")
      return None
    
    # Find the parent div with class 'boots3' containing Edible Uses content
    boots4_div = other_uses_section.find_next('div', class_='boots4')
    
    if not boots4_div:
      print("Unable to locate the 'boots4' class for Other Uses")
      return None
    
    # Initialize content to collect text
    other_uses = []
    
    # Extract the content within the 'boots3' class
    next_element = boots4_div.find_next()
    
    while next_element and next_element.name != 'h3':
      if len(next_element.find_all('a')) == 0:
        text = next_element.get_text().strip()
        if text:  # Check if text is not empty
          other_uses.append(text)
      else:
        strings = next_element.find_all(string=True)
        if 'Special Uses' in strings:
          special_index = strings.index('Special Uses')
          if special_index > 0:
            other_uses.append(strings[special_index - 1].strip())
        else:
          if strings[-1].strip():  # Check if last string is not empty
            other_uses.append(strings[-1].strip())

      next_element = next_element.find_next_sibling()

    return other_uses 

### This gets the plant uses by checking pfaf
def get_plant_uses_pfaf(common_name, botanical_name):
  latin_name, plant_page_url = find_plant_page_by_name(common_name, botanical_name)
  if not plant_page_url:
    return None
  response = requests.get(plant_page_url)
  soup = BeautifulSoup(response.text, 'html.parser')
  medicinal_uses = scrape_medical_uses(soup)
  edible_parts, edible_uses = scrape_edible_uses(soup)
  other_uses = scrape_other_uses(soup)

  uses = {
      'Other Uses': other_uses,
      'Edible Parts': edible_parts,
      'Edible Uses': edible_uses,
      'Medicinal Uses': medicinal_uses   
  }

  return uses

### This gets the plant uses by checking wikipedia
def get_plant_use_wikipedia(plant_name):
  plant_name = plant_name.replace(' ', '_')
  wiki = wikipediaapi.Wikipedia('Nyameget (NYAMEGET@GMAIL.COM)', 'en', extract_format=wikipediaapi.ExtractFormat.HTML)
  page = wiki.page(plant_name)
  uses_section = page.section_by_title('Uses')
  
  if uses_section is None:
    return {None, None}
  if len(uses_section.sections) == 1:
    soup = BeautifulSoup(uses_section.text, "html.parser")
    paragraphs = soup.find_all('p')
    
    if len(paragraphs) > 1:
      return {paragraphs[0].text[:-2], paragraphs[1].text[:-2]}
    elif len(paragraphs) == 1:
      return {paragraphs[0].text[:-2], None}
    else:
      return {None, None}
  elif len(uses_section.sections) > 1:
    if len(BeautifulSoup(uses_section.text, "html.parser").find_all('p')) == 0:
      uses_section = uses_section.sections[0]
    soup = BeautifulSoup(uses_section.text, "html.parser")
    paragraphs = soup.find_all('p')
    
    if len(paragraphs) > 1:
      return {paragraphs[0].text[:-2], paragraphs[1].text[:-2]}
    elif len(paragraphs) == 1:
      return {paragraphs[0].text[:-2], None}
    else:
      return {None, None}

# Create a new user
@app.route('/users/create', methods=['POST'])
def create_user():
    data = request.get_json()
    if db.session.query(db.exists().where(User.username == data['username'])).scalar():
        return jsonify({'message': 'Username taken'}), 409
    new_user = User(username=data['username'], name=data['name'], email=data['email'], password=data['password'])
    db.session.add(new_user)
    db.session.commit()
    return jsonify({'message': 'User created successfully'}), 201

# Get all users
@app.route('/users/all', methods=['GET'])
def get_users():
    users = User.query.all()
    if users:
        return jsonify([{'username': user.username, 'name': user.name, 'email': user.email, 'password': user.password} for user in users])
    return jsonify({'message': 'No user found'}), 404

# Get a user by username
@app.route('/users/<string:username>', methods=['GET'])
def get_user(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        return jsonify({'message': 'User not found'}), 404
    return jsonify({'username': user.username, 'name': user.name, 'email': user.email, 'password': user.password})

# Update email
@app.route('/users/email/<string:username>', methods=['PUT'])
def update_email(username):
    data = request.get_json()
    user = User.query.filter_by(username=username).first()
    if user is None:
        return jsonify({'message': 'User not found'}), 404
    user.email = data['email']
    db.session.commit()
    return jsonify({'message': 'Email updated successfully'}), 200

# Update password
@app.route('/users/password/<string:username>', methods=['PUT'])
def update_password(username):
    data = request.get_json()
    user = User.query.filter_by(username=username).first()
    if user is None:
        return jsonify({'message': 'User not found'}), 404
    user.password = data['password']
    db.session.commit()
    return jsonify({'message': 'Password updated successfully'}), 200

# Check if password is taken
@app.route('/users/password/count/<string:password>', methods=['GET'])
def password_count(password):
    password_count = db.session.query(User).filter_by(password=password).count()
    if password_count == 0:
        return jsonify({'message': 'Password not taken'}), 200
    return jsonify({'message': 'Password is taken'}), 409

# Check if email is taken
@app.route('/users/email/count/<string:email>', methods=['GET'])
def email_count(email):
    email_count = db.session.query(User).filter_by(email=email).count()
    if email_count == 0:
        return jsonify({'message': 'Email not taken'}), 200
    return jsonify({'message': 'Email is taken'}), 409

# Check if username is taken
@app.route('/users/username/count/<string:username>', methods=['GET'])
def username_count(username):
    username_count = db.session.query(User).filter_by(username=username).count()
    if username_count == 0:
        return jsonify({'message': 'Username not taken'}), 200
    return jsonify({'message': 'Username is taken'}), 409

# Delete a user
@app.route('/users/delete/<string:username>', methods=['DELETE'])
def delete_user(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        return jsonify({'message': 'User not found'}), 404
    db.session.delete(user)
    db.session.commit()
    return jsonify({'message': 'User deleted successfully'}), 200

######################################################################################################################
# PLANTS
# Create a new plant
@app.route('/plants/create', methods=['POST'])
def create_plant():
    data = request.get_json()
    # saves new plant
    new_plant = Plant(filename=data['filename'], image_data=data['image_data'], plant_info=data['plant_info'],  plant_uses=data['plant_uses'] ,username=data['username'])
    db.session.add(new_plant)
    db.session.commit()
    return jsonify({'message': 'Plant created successfully'}), 201

# Get all plants
@app.route('/plants/all', methods=['GET'])
def get_plants():
    plants = Plant.query.all()
    if plants:
        return jsonify([{'id': plant.id, 'filename': plant.filename, 'image_data': base64.b64encode(plant.image_data).decode('utf-8'), 'plant_info': plant.plant_info, 'plant_uses':plant.plant_uses ,'username': plant.username} for plant in plants])
    return jsonify({'message': 'No plant found'}), 404

# Get a plant by id
@app.route('/plants/<int:id>', methods=['GET'])
def get_plant(id):
    plant = Plant.query.get(id)
    if plant is None:
        return jsonify({'message': 'Plant not found'}), 404
    return jsonify({'id': plant.id, 'filename': plant.filename, 'image_data': base64.b64encode(plant.image_data).decode('utf-8'), 'plant_info': plant.plant_info, 'plant_uses':plant.plant_uses, 'username': plant.username})
  

# Check if a plant has been uploaded before
@app.route('/plants/count/<string:username>', methods=['GET'])
def plant_count(username):
    plant_count = db.session.query(Plant).filter_by(username=username).count()
    if plant_count == 0:
        return jsonify({'message': 'No plant saved'}), 404
    return jsonify({'plant_count': plant_count}), 200

# This gets the plant uses by checking pfaf if no result is returned then checks wikipedia
@app.route('/plants/uses/<string:common_name>/<string:botanical_name>', methods=['GET'])
def plant_uses(common_name, botanical_name):
    if "-" in common_name:
        common_name = common_name.replace('-', ' ')
    if '-' in botanical_name:
        botanical_name = botanical_name.replace('-', ' ')
    uses = get_plant_uses_pfaf(common_name, botanical_name)
    if uses:
        return jsonify({'plant_uses': uses, 'type': 'dict'}), 200
    else:
        wikipedia_info = get_plant_use_wikipedia(common_name)
        return jsonify({'plant_uses': wikipedia_info, 'type': 'set'})


# Delete a plant
@app.route('/plants/delete/<int:id>', methods=['DELETE'])
def delete_plant(id):
    plant = Plant.query.get(id)
    if plant is None:
        return jsonify({'message': 'Plant not found'}), 404
    db.session.delete(plant)
    db.session.commit()
    return jsonify({'message': 'Plant deleted successfully'}), 200

######################################################################################################################
# COMMENTS
# Create a new comment
@app.route('/comment/create', methods=['POST'])
def create_comment():
    data = request.get_json()
    # saves new plant
    new_comment = Comment(comment=data['comment'], rate=data['rate'], username=data['username'])
    db.session.add(new_comment)
    db.session.commit()
    return jsonify({'message': 'Comment created successfully'}), 201

# Get all comments
@app.route('/comment/all', methods=['GET'])
def get_comment():
    comments = Comment.query.all()
    if comments:
        return jsonify([{'id': comment.id, 'comment': comment.comment, 'rate': comment.rate ,'username': comment.username} for comment in comments])
    return jsonify({'message': 'No comment found'}), 404

if __name__ == '__main__':
    app.run(debug=True)
