from flask import request, render_template, session
from data.models import get_plants, plants_saved_count, get_reviews
from data.plant_modules import _normalize_saved_plant_uses, _extract_disease_info, _extract_classification_core, _cap
from data.modules import *
from data.plant_modules import *
from data import db, app, PLANT_ID_API_KEY, url
import base64
import requests


@app.route('/', methods=['GET'])
def welcome():
    resp = logged_in(session)
    if resp:
        return resp
    return render_template('welcome.html')


@app.route('/signin', methods=['GET', 'POST'])
def signin():
    resp = logged_in(session)
    if resp:
        return resp
    try:
        if request.method == 'GET':
            return render_template('signin.html')

        # Gets User log in info
        username, password = get_login_details(request.form)
        user = User.query.filter_by(username=username).first()
        if not user:
            flash('User doesn\'t exist', 'danger')
            return redirect(url_for('signup'))
        # Checks if user is in the system
        if not user.check_password(password):
            # Wrong details
            flash('Wrong credentials', 'danger')
            return redirect(url_for('signin'))
        session['user'] = user.to_dict()
        flash('Login successful', 'danger')
        return redirect(url_for('home'))
    except Exception as e:
        # Error Occurred
        return exception_error(e, 'signin')


@app.route("/signup", methods=['GET', 'POST'])
def signup():
    resp = logged_in(session)
    if resp:
        return resp
    try:
        if request.method == 'GET':
            return render_template('signup.html')

        name, username, email, password = get_signup_details(request.form)
        if check_password(password) is None:
            flash('Weak Password', 'danger')
            return redirect(url_for('signup'))
        # Check if username is taken
        if len(User.query.filter_by(username=username).all()) != 0:
            flash('Account already exist', 'danger')
            return redirect(url_for('signin'))
        # Check if email is taken
        if len(User.query.filter_by(email=email).all()) != 0:
            flash('Email already exist', 'danger')
            return redirect(url_for('signin'))
        # Store user data and redirect to signin page
        add_user(name=name, username=username, email=email, password=password)
        flash('User created successfully', 'success')
        return redirect(url_for('signin'))
    except Exception as e:
        # User has no account and an error occurred during the signup process
        return exception_error(e, 'signup')


@app.route("/forgot", methods=['POST', 'GET'])
def forgot():
    resp = logged_in(session)
    if resp:
        return resp
    if request.method == 'GET':
        return render_template('forgot.html')

    try:
        name, username, email, new_password = get_signup_details(request.form)
        print(name, username, email, new_password)
        if check_password(new_password) is None:
            flash('Weak Password', 'danger')
            return redirect('forgot')
        user = User.query.filter_by(username=username).first()
        if user is None:
            flash('Account not found', 'danger')
            return redirect(url_for('signup'))
        if username != user.username or name != user.name or email != user.email:
            flash('Details Do Not Match', 'danger')
            return redirect(url_for('signup'))
        if user.check_password(new_password):
            flash('Used an old password', 'danger')
            return redirect(url_for('forgot'))
        user.password = new_password
        db.session.commit()
        flash('Password updated successfully', 'success')
        return redirect(url_for('signin'))
    except Exception as e:
        return exception_error(e, 'forgot')


@app.route("/home", methods=['GET'])
def home():
    resp = not_logged_in(session)
    if resp:
        return resp
    return render_template('home.html', data={'active_page': 'home'})


@app.route("/setting", methods=['GET', 'POST'])
def setting():
    resp = not_logged_in(session)
    if resp:
        return resp

    if request.method == 'GET':
        username = session['user']['username']
        user = User.query.filter_by(username=username).first()
        data_ = {
            'user': user,
            'active_page': 'setting',
        }
        return render_template('setting.html', data=data_)

    try:
        username = session['user']['username']
        rate, feedback = get_review_info(request.form)
        add_comment(feedback, rate, username)
        flash('Review submitted successfully', 'success')
        return redirect(url_for('setting'))
    except Exception as e:
        return exception_error(e, 'setting')


@app.route("/edit/profile", methods=['POST'])
def profile():
    resp = not_logged_in(session)
    if resp:
        return resp
    try:
        username = session['user']['username']
        file = request.files['profile_pic']

        if not file:
            flash("No image uploaded!", "danger")
            return redirect(url_for('setting'))

        user = User.query.filter_by(username=username).first()
        user.profile_pic_data = file.read()
        user.profile_pic_mimetype = file.mimetype
        db.session.commit()
        session['user'] = user.to_dict()
        flash("Profile image updated successfully!", "success")
        return redirect(url_for('setting'))
    except Exception as e:
        # An error occurred
        return exception_error(e, 'setting')


@app.route('/edit/password', methods=['POST'])
def edit_password():
    resp = not_logged_in(session)
    if resp:
        return resp
    try:
        current_password, new_password, confirm_password = get_passwords(request.form)
        username = session['user']['username']
        user = User.query.filter_by(username=username).first()
        if not user.check_password(current_password):
            flash('Current password incorrect', 'danger')
            return redirect(url_for('setting'))
        if new_password != confirm_password:
            flash('New password incorrect', 'danger')
            return redirect(url_for('setting'))
        user.password = new_password
        db.session.commit()
        session['user']['password'] = new_password
        flash('Password updated successfully', 'success')
        return redirect(url_for('setting'))
    except Exception as e:
        return exception_error(e, 'setting')


@app.route('/edit/email', methods=['POST'])
def edit_email():
    resp = not_logged_in(session)
    if resp:
        return resp
    try:
        current_password, new_email, old_email = get_emails(request.form)
        username = session['user']['username']
        user = User.query.filter_by(username=username).first()
        if user.email != old_email:
            flash('Current email incorrect', 'danger')
            return redirect(url_for('setting'))
        if new_email == old_email:
            flash('New email taken', 'danger')
            return redirect(url_for('setting'))
        if not user.check_password(current_password):
            flash('Current password incorrect', 'danger')
            return redirect(url_for('setting'))
        user.email = new_email
        db.session.commit()
        session['user']['email'] = new_email
        flash('Email updated successfully', 'success')
        return redirect(url_for('setting'))
    except Exception as e:
        return exception_error(e, 'setting')


@app.route('/delete/user', methods=['POST'])
def delete_user():
    try:
        username = session['user']['username']
        message = delete_user_(username)
        if message == 'success':
            flash('User\'s data has been successfully deleted', 'success')
            return redirect(url_for('logout'))
        flash('User not found', 'danger')
        return redirect(url_for('logout'))
    except Exception as e:
        return exception_error(e, 'setting')


@app.route("/review", methods=['GET'])
def review():
    try:
        reviews = get_reviews()
        return render_template('review.html', data={'reviews': reviews})
    except Exception as e:
        # An error occurred
        return exception_error(e, 'review')


@app.route("/about", methods={"GET"})
def about():
    resp = not_logged_in(session)
    if resp:
        return resp
    return render_template('about.html', data={"active_page": 'about'})


@app.route("/logout", methods=['GET'])
def logout():
    session.pop('user', None)
    return redirect(url_for('welcome'))


@app.route("/search", methods=['GET', 'POST'])
def search():
    resp = not_logged_in(session)
    if resp:
        return resp
    try:
        if request.method == 'GET':
            return render_template('search.html', data={'active_page': ''})

        plant_name = request.form['plant_name']
        search_url = f"https://plant.id/api/v3/kb/plants/name_search?q={plant_name}&thumbnails=true"
        print(search_url)
        headers = {
            'Api-Key': PLANT_ID_API_KEY,
            'Content-Type': 'application/json'
        }
        response = requests.get(search_url, headers=headers)
        if response.status_code == 200:
            with requests.Session() as session_:  # Optional: Reuse session for efficiency
                plant_details = build_plant_details_from_response(response, headers, session=session_)
            return render_template('search_result.html',
                                   data={'active-page': '', 'plant': plant_details})
    except Exception as e:
        return exception_error(e, 'search')


@app.route("/scan", methods=['GET'])
def scan():
    resp = not_logged_in(session)
    if resp:
        return resp
    return render_template('scan.html', data={'active_page':''})


@app.route('/upload', methods=['POST'])
def upload():
    try:
        if request.method == 'POST':
            # 1️⃣ Check for camera image (base64)
            captured_b64 = request.form.get('captured_image')
            file = request.files.get('image')

            if not captured_b64 and not file:
                flash('No image provided. Please upload or capture one.', 'danger')
                return redirect(url_for('scan'))

            if captured_b64:
                # Example: data:image/png;base64,iVBORw0...
                header, encoded = captured_b64.split(',', 1)
                image_bytes = base64.b64decode(encoded)
                filename = "captured_image.png"
            else:
                if not file.filename:
                    flash('File is empty.', 'danger')
                    return redirect(url_for('scan'))
                image_bytes = file.read()
                if not image_bytes:
                    flash('Uploaded file contained no data.', 'danger')
                    return redirect(url_for('scan'))
                filename = file.filename

            # 2️⃣ Encode for Plant.id API
            b64_image = base64.b64encode(image_bytes).decode('utf-8')
            base64_image_string = f"data:image/jpeg;base64,{b64_image}"

            payload = {
                "images": [base64_image_string],
                "similar_images": True,
                "health": "all",
            }

            headers = {
                'Api-Key': PLANT_ID_API_KEY,
                'Content-Type': 'application/json',
            }

            # 3️⃣ Send to Plant.id API
            resp = requests.post(url, headers=headers, json=payload, timeout=30)
            if resp.status_code not in (200, 201):
                print(f"Plant.id error {resp.status_code}: {resp.text}")
                flash('Plant identification failed. Please try again.', 'danger')
                return redirect(url_for('scan'))

            plant_info = resp.json()

            # 4️⃣ Parse result safely
            result = plant_info.get('result', {})
            is_plant = result.get('is_plant', {})
            if not is_plant.get('binary', False):
                flash('Image does not contain a plant.', 'danger')
                return redirect(url_for('scan'))

            classification = result.get('classification', {})
            suggestions = classification.get('suggestions', [])
            top_suggestion = suggestions[0] if suggestions else {}
            top_details = top_suggestion.get('details', {})
            common_names = top_details.get('common_names', [])
            botanical_name = top_suggestion.get('name')
            family = (top_details.get('taxonomy') or {}).get('family')

            if not common_names and len(suggestions) > 1:
                alt_suggest = suggestions[1]
                alt_details = alt_suggest.get('details', {})
                common_names = alt_details.get('common_names', [])

            if common_names:
                plant_uses, common_names = resolve_plant_uses(common_names, botanical_name, family)
            else:
                plant_uses, fam_cn = get_plant_uses_family(family, botanical_name)
                if plant_uses is not None:
                    common_names = [fam_cn] if fam_cn else []
                    top_details.setdefault('common_names', common_names)

            # 5️⃣ Save in DB
            new_plant = Plant(
                filename=filename,
                image_data=image_bytes,
                plant_info=plant_info,
                plant_uses=plant_uses,
                username=session['user']['username'],
            )
            db.session.add(new_plant)
            db.session.commit()

            flash('Image processed successfully.', 'success')
            return redirect(url_for('results', image_id=new_plant.id))

    except Exception as exc:
        print("Error processing plant scan:", exc)
        flash('An error occurred while processing the image. Please try again.', 'danger')
        return redirect(url_for('scan'))


@app.route('/results/<int:image_id>')
def results(image_id):
    try:
        image = Plant.query.get_or_404(image_id)

        # Normalize plant uses saved in DB
        plant_uses, plant_uses_type = _normalize_saved_plant_uses(image.plant_uses)

        # Plant.id payload as stored
        plant_info = image.plant_info or {}
        result = plant_info.get("result") or {}

        # Disease extraction
        disease_category, disease_description, disease_common_name, disease_name = _extract_disease_info(result)

        # Classification core
        plant_name, common_name, reversed_taxonomy, description, edible_parts, watering = _extract_classification_core(
            result)

        # Irrigation message
        irrigation_info = watering_message(watering) if watering else None

        # Encode original uploaded image
        image_base64 = base64.b64encode(image.image_data).decode("utf-8")
        image_url = f"data:image/jpeg;base64,{image_base64}"
        print(plant_uses)
        # After getting plant_uses
        if isinstance(plant_uses, dict):
            # Check if all lists are empty
            all_empty = all(len(v) == 0 for v in plant_uses.values())
            if all_empty:
                plant_uses = {
                    "None": f"https://www.google.com/search?q={plant_name}+plant+uses"
                }

        identification_results = {
            "name": plant_name,
            "common_name": common_name,
            "taxonomy": reversed_taxonomy,
            "description": description,
            "edible_part": edible_parts,
            "watering": irrigation_info,
            "disease_category": disease_category,
            "disease_description": disease_description,
            "disease_common_name": _cap(disease_common_name),
            "disease_name": _cap(disease_name),
            "plant_uses": plant_uses,
            "plant_uses_type": plant_uses_type,
        }

        return render_template(
            "result.html",
            data={"image_url": image_url, "results": identification_results},
        )
    except Exception as e:
        return exception_error(e, 'scan')


@app.route("/history", methods=['GET'])
def history():
    resp = not_logged_in(session)
    if resp:
        return resp
    try:
        if request.method == 'GET':
            username = session['user']['username']
            saved_plant_count = plants_saved_count(username)

            if saved_plant_count == 0:
                flash('No plant identified yet', 'info')
                return redirect(url_for('home'))

            saved_plants = get_plants(username)
            plant_details = []

            for plant in saved_plants:
                plant_info = plant.plant_info or {}
                result = plant_info.get('result')
                if not result:
                    continue  # Skip plants with no results

                classification = result.get('classification')
                suggestions = classification.get('suggestions') if classification else []

                if not suggestions:
                    continue  # Skip if there are no suggestions

                suggestion = suggestions[0]
                details = suggestion.get('details') or {}

                # Determine common name and plant name
                common_names = details.get('common_names') or []
                plant_name = suggestion.get('name')
                if common_names:
                    common_name = common_names[0]
                elif len(suggestions) > 1:
                    fallback_details = suggestions[1].get('details') or {}
                    common_name = (fallback_details.get('common_names') or [None])[0]
                    plant_name = suggestions[1].get('name', plant_name)
                else:
                    common_name = details.get('common_name', plant_name)

                # Taxonomy
                taxonomy = details.get('taxonomy', {})
                reversed_taxonomy = dict(reversed(list(taxonomy.items())))

                # Description with Wikipedia fallback
                description = (details.get('description') or {}).get('value')
                if not description:
                    if len(suggestions) > 1:
                        description = (suggestions[1].get('details', {}).get('description') or {}).get('value')
                    if not description:  # Fallback to Wikipedia
                        description = get_plant_description_wikipedia(common_name) or get_plant_description_wikipedia(
                            plant_name)
                description = truncate_words(description, 60)

                # Other details
                edible_parts = details.get('edible_parts')
                watering = details.get('watering')
                irrigation_info = watering_message(watering)

                # Build plant result
                identification_results = {
                    'name': plant_name,
                    'common_name': common_name,
                    'taxonomy': reversed_taxonomy,
                    'description': description,
                    'edible_part': edible_parts,
                    'watering': irrigation_info,
                    'plant_id': plant.id
                }

                # Encode image
                image_url = f"data:image/jpeg;base64,{base64.b64encode(plant.image_data).decode('utf-8')}"
                plant_details.append({
                    'image_url': image_url,
                    'plant_data': identification_results
                })

            return render_template('history.html',
                                   data={'plant_data': plant_details, 'active_page': 'history'})
    except Exception as e:
        return exception_error(e, 'history')

