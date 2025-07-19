from flask import request, jsonify, render_template, redirect, url_for, flash, session
from data.models import User, Plant
from data.models import get_plants, plants_saved_count, get_reviews
from data.scrapping import watering_message, truncate_words, get_plant_uses_family, get_plant_description_wikipedia
from data.modules import check_password, logged_in, not_logged_in, get_login_details, exception_error, \
    get_signup_details, add_user, get_passwords, get_emails, \
    get_profile_data, delete_user, add_comment, get_review_info
from data.plant_modules import build_plant_details_from_response, resolve_plant_uses, _normalize_saved_plant_uses, \
    _extract_disease_info, _extract_classification_core, _cap
from data import db, app, PLANT_ID_API_KEY, url
import base64
import requests


@app.route('/', methods=['GET'])
def welcome():
    logged_in(session)
    theme = session.get('theme', 'light')
    return render_template('welcome.html', data={'theme': theme})


@app.route('/signin', methods=['GET', 'POST'])
def signin():
    logged_in(session)
    try:
        if request.method == 'GET':
            theme = session.get('theme', 'light')
            return render_template('signin.html', data={'theme': theme})

        # Gets User log in info
        username, password = get_login_details(request.form)
        user = User.query.filter_by(username=username).first()
        # Checks if user is in the system
        if user and user.check_password(password):
            session['user'] = user
            flash('Login successful', 'success')
            return redirect(url_for('home'))
        # Wrong details
        flash('Wrong credentials', 'warning')
        return redirect(url_for('signin'))
    except Exception as e:
        # Error Occurred
        exception_error(e, 'signin')


@app.route("/signup", methods=['GET', 'POST'])
def signup():
    logged_in(session)
    try:
        if request.method == 'GET':
            theme = session.get('theme', 'light')
            return render_template('signup.html', data={'theme': theme})

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
        add_user(name=name, username=username, email=email, password=password, )
        flash('User created successfully', 'success')
        return redirect(url_for('signin'))
    except Exception as e:
        # User has no account and an error occurred during the signup process
        exception_error(e, 'signup')


@app.route("/home", methods=['GET'])
def home():
    not_logged_in(session)
    theme = session.get('theme', 'light')
    return render_template('home.html', data={'active_page': 'home', 'theme': theme})


@app.route("/profile", methods=['GET'])
def profile():
    not_logged_in(session)
    try:
        username = session['user'].username
        userInfo = get_profile_data(username=username)
        theme = session.get('theme', 'light')
        return render_template('profile.html', data={'user': userInfo, 'active_page': 'profile', 'theme': theme})
    except Exception as e:
        # An error occurred
        exception_error(e, 'profile')


@app.route("/setting", methods=['GET', 'POST'])
def setting():
    not_logged_in(session)
    try:
        if request.method == 'GET':
            theme = session.get('theme', 'light')
            username = session['user'].username
            email = session['user'].email
            return render_template('setting.html', data={'active_page': 'setting', 'theme': theme, 'email': email,
                                                         'username': username})

        # Handle form submission here
        username = session['user'].username
        if 'theme' in request.form:
            theme = str(request.form['theme']).strip()
            session['theme'] = theme
            return redirect(url_for('home'))
        if 'decision' in request.form:
            decision = str(request.form['decision']).strip()
            if decision == 'yes':
                if delete_user(username) == 'success':
                    flash('User\'s data has been successfully deleted', 'success')
                    return redirect(url_for('logout'))
                flash('User not found', 'danger')
                return redirect(url_for('logout'))
            elif 'rate' in request.form:
                rate, feedback = get_review_info(request.form)
                add_comment(feedback, rate, username)
                flash('Review submitted successfully', 'success')
                return redirect(url_for('home'))
    except Exception as e:
        exception_error(e, 'setting')


@app.route("/search", methods=['GET', 'POST'])
def search():
    not_logged_in(session)
    try:
        if request.method == 'GET':
            theme = session.get('theme', 'light')
            return render_template('search.html', data={'theme': theme, 'active_page': ''})

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
            theme = session.get('theme', 'light')
            return render_template('search_result.html',
                                   data={'active-page': '', 'plant': plant_details, 'theme': theme})
    except Exception as e:
        exception_error(e, 'search')


@app.route("/about", methods={"GET"})
def about():
    not_logged_in(session)
    theme = session.get('theme', 'light')
    return render_template('about.html', data={"active_page": 'about', 'theme': theme})


@app.route("/edit", methods=['GET', 'POST'])
def edit():
    not_logged_in(session)
    try:
        if request.method == 'GET':
            theme = session.get('theme', 'light')
            return render_template('editinfo.html', data={'active_page': '', 'theme': theme})

        choice = str(request.form['choice'])
        user = session['user']
        if choice == 'password':
            oldPassword, newPassword, passwordConfirmation = get_passwords(request.form)
            if newPassword != passwordConfirmation:
                flash('Password Mismatch', 'danger')
                return redirect(url_for('edit'))
            if check_password(newPassword) is None:
                flash('Weak Password', 'danger')
                return redirect(url_for('edit'))
            if user.check_password(oldPassword) and newPassword != oldPassword:
                user.password = newPassword
                db.session.commit()
                # Updated successfully
                session['user'] = user
                flash('Password successfully updated', 'success')
                return redirect(url_for('home'))
            # Password does not match
            flash('Password mismatch', 'danger')
            return redirect(url_for('edit'))
        elif choice == 'email':
            password, oldEmail, newEmail = get_emails(request.form)
            if not user.check_password(password):
                flash('Wrong Credentials', 'danger')
                return redirect(url_for('edit'))
            if len(User.query.filter_by(email=newEmail).all()) != 0:
                flash('New Email Already Taken', 'danger')
                return redirect(url_for('edit'))
            user.email = newEmail
            db.session.commit()
            session['user'] = user
            # Updated successfully
            flash('Email has been successfully updated', 'success')
            return redirect(url_for('home'))
    except Exception as e:
        exception_error(e, 'edit')


@app.route("/scan", methods=['GET'])
def scan():
    not_logged_in(session)
    theme = session.get('theme', 'light')
    return render_template('scan.html', data={'active_page': '', 'theme': theme})


@app.route('/upload', methods=['POST'])
def upload():
    if request.method == 'POST':
        file = request.files.get('image')
        if file is None:
            flash('There is no file part.', 'warning')
            return redirect(url_for('scan'))

        if not file.filename:  # empty filename
            flash('File is empty.', 'warning')
            return redirect(url_for('scan'))

        try:
            # Read raw bytes (store for DB) & base64 encode (for Plant.id)
            image_bytes = file.read()
            if not image_bytes:
                flash('Uploaded file contained no data.', 'warning')
                return redirect(url_for('scan'))

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

            # Identify via Plant.id
            resp = requests.post(url, headers=headers, json=payload, timeout=30)

            if resp.status_code not in (200, 201):
                print("Plant.id error %s: %s", resp.status_code, resp.text)
                flash('Plant identification failed. Please try again.', 'danger')
                return redirect(url_for('scan'))

            plant_info = resp.json()
            print(plant_info)  # debug

            # --- Parse response safely ---
            result = plant_info.get('result') or {}
            is_plant = result.get('is_plant') or {}
            plant_binary = is_plant.get('binary', False)

            if not plant_binary:
                flash('Image does not contain a plant.', 'warning')
                return redirect(url_for('scan'))

            classification = result.get('classification') or {}
            suggestions = classification.get('suggestions') or []
            top_suggestion = suggestions[0] if suggestions else {}

            # Pull details from top suggestion
            top_details = top_suggestion.get('details') or {}
            common_names = top_details.get('common_names') or []
            botanical_name = top_suggestion.get('name')
            family = (top_details.get('taxonomy') or {}).get('family')

            # Fallback: try 2nd suggestion if no common names
            if not common_names and len(suggestions) > 1:
                alt_suggest = suggestions[1]
                alt_details = alt_suggest.get('details') or {}
                common_names = alt_details.get('common_names') or []
                # preserve botanical/family from top suggestion (confidence highest)

            # Resolve plant uses
            plant_uses = None
            if common_names:
                plant_uses, common_names = resolve_plant_uses(common_names, botanical_name, family)
            else:
                # Last resort: try family-level lookup
                plant_uses, fam_cn = get_plant_uses_family(family, botanical_name)
                if plant_uses is not None:
                    common_names = [fam_cn] if fam_cn else []
                    # mutate original structure so downstream UI sees a common name
                    top_details.setdefault('common_names', common_names)

            # (Optional) store probability in DB if you want it
            # plant_probability = is_plant.get('probability')

            # --- Persist ---
            new_plant = Plant(
                filename=file.filename,
                image_data=image_bytes,
                plant_info=plant_info,  # raw API payload
                plant_uses=plant_uses,
                username=session['username'],
            )
            db.session.add(new_plant)
            db.session.commit()
            print("Plant %s saved (id=%s)", file.filename, new_plant.id)

            flash('Image saved successfully.', 'success')
            return redirect(url_for('results', image_id=new_plant.id))
        except Exception as exc:
            print("Error processing plant scan: %s", exc)
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

        theme = session.get("theme", "light")
        return render_template(
            "result.html",
            data={"image_url": image_url, "results": identification_results, "theme": theme},
        )
    except Exception as e:
        exception_error(e, 'scan')


@app.route("/history", methods=['GET'])
def history():
    not_logged_in(session)
    try:
        if request.method == 'GET':
            username = session['user'].username
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

                theme = session.get('theme', 'light')
                return render_template('history.html',
                                       data={'plant_data': plant_details, 'active_page': 'history', 'theme': theme})
    except Exception as e:
        exception_error(e, 'history')


@app.route("/review", methods=['GET'])
def review():
    try:
        reviews = get_reviews()
        theme = session.get('theme', 'light')
        return render_template('review.html', data={'reviews': reviews, 'theme': theme})
    except Exception as e:
        # An error occurred
        exception_error(e, 'review')


@app.route("/forgot", methods=['POST', 'GET'])
def forgot():
    logged_in(session)
    if request.method == 'GET':
        theme = session.get('theme', 'light')
        return render_template('forgot.html', data={'theme': theme})

    try:
        name, username, email, new_password = get_signup_details(request.form)
        if check_password(new_password) is None:
            flash('Weak Password', 'danger')
            return redirect('forgot')

        user = User.query.filter_by(username=username).first()
        if user is None:
            flash('Account not found', 'danger')
            return redirect(url_for('signup'))
        if username == user.username and name == user.name and email == user.email:
            if new_password == user.password:
                flash('Used an old password', 'info')
                return redirect(url_for('forgot'))
            user.password = new_password
            db.session.commit()
            flash('Password updated successfully', 'success')
            return redirect(url_for('signin'))
    except Exception as e:
        exception_error(e, 'forgot')


@app.route("/logout", methods=['GET'])
def logout():
    session.pop('user', None)
    return redirect(url_for('welcome'))
