from flask import Flask, render_template, request, redirect, flash, url_for, jsonify
import re
from flask import session
import db, Assistant
from datetime import date
app = Flask(__name__)
app.secret_key = "your_secret_key"


def verify_password(password):
    return (
        len(password) > 8 and
        re.search("[a-z]", password) and
        re.search("[A-Z]", password) and
        re.search("[0-9]", password) and
        re.search("[_@$]", password) and
        not re.search("\s", password)
    )

def validate_number(number):
    return bool(re.match(r'^\d{10}$', number))

def validate_mail(mail):
    return bool(re.match(r'^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$', mail))


@app.route('/')
def index():
    return render_template('home.html')


@app.route('/edu')
def edu():
    user = session.get('user')
    if not user:
        flash("Please log in first.")
        return redirect(url_for('index'))
    return render_template('edu.html', user=user)

@app.route('/ai')
def artificialIntelligence():
    return render_template('AI-basics.html')

@app.route('/sql')
def sql_now():
    return render_template('sql-course.html')

@app.route('/writing')
def writing():
    return render_template('technical-writing.html')

@app.route('/ask_course', methods=['POST'])
def ask_course():
    if 'user' not in session:
        return jsonify({'answer': 'Please log in to submit a query.'}), 401

    data = request.get_json()
    question = data.get('question', '')
    course = data.get('course', '').lower()

    # Set course title
    if course == 'ai':
        course_title = "Introduction to Artificial Intelligence"
    elif course == 'sql':
        course_title = "SQL for Beginners"
    else:
        course_title = "General Course"

    # Get answer
    answer = Assistant.get_answer(question, course_title)

    # Store in MongoDB
    user_email = session['user']
    query_entry = {"question": question, "answer": answer}

    db.user_data.update_one(
        {"email": user_email["email"]},
        {
            "$push": {
                f"qwery.{course}": {
                    "$each": [query_entry],
                    "$position": 0
                }
            }
        }
    )

    return jsonify({'answer': answer})

@app.route('/get_course_history', methods=['POST'])
def get_course_history():
    if 'user' not in session:
        return jsonify({"status": "error", "message": "User not logged in"}), 401

    data = request.get_json()
    course = data.get('course', '').lower()
    user_email = session['user']

    user_doc = db.user_data.find_one({"email": user_email["email"]})
    if not user_doc:
        return jsonify({"status": "error", "message": "User not found"}), 404

    history = user_doc.get("qwery", {}).get(course, [])

    return jsonify({"status": "success", "history": history})




@app.route('/enroll', methods=['POST'])
def enroll_course():
    if 'user' not in session:
        return jsonify({"status": "error", "message": "User not logged in"}), 401

    data = request.get_json()
    course_name = data.get('course')

    if not course_name:
        return jsonify({"status": "error", "message": "Course name missing"}), 400

    user_email = session['user']
    # Update enrollment and initialize query history for that course

    new_value = {"$unset": {}, "$set": {}}
    new_value["$set"][f"Enrol_course.{course_name}"] = True
    new_value["$set"][f"qwery.{course_name}"] = []

    db.user_data.update_one({"email": user_email['email']},new_value)

    return jsonify({"status": "success", "message": f"Enrolled in {course_name}!"})


@app.route('/register', methods=['POST'])
def register():
    name = request.form['name']
    email = request.form['email']
    password = request.form['password']
    confirm = request.form['confirm']
    number = request.form.get('number', '')

    user = db.users.find_one({"$and": [{"email": email}, {"password": password}]},
                             {"_id": False, "name": True})

    if not validate_mail(email):
        flash("Invalid email format.")
        return render_template("home.html", name=name, email=email, number=number, error_fields=["email"])
    elif not verify_password(password):
        flash("Password must contain 8+ characters, uppercase, lowercase, number, and special character.")
        return render_template("home.html", name=name, email=email, number=number, error_fields=["password", "confirm"])
    elif password != confirm:
        flash("Passwords do not match.")
        return render_template("home.html", name=name, email=email, number=number, error_fields=["confirm"])

    elif user:
        flash("Email already exists.")
        return render_template("home.html", name=name, email=email, number=number, error_fields=["email"])
    else:
        data = {"name": name, "email": email, "password": password, "number": number, "member since": date.today().strftime('%d-%m-%Y')}
        db.users.insert_one(data)
        db.user_data.insert_one({"email": email, "Enrol_course": {}})
        flash("Registration successful. Please login.")
        return redirect(url_for('index'))


@app.route('/login', methods=['POST'])
def login():
    email = request.form['email']
    password = request.form['password']

    user = db.users.find_one({"$and": [{"email": email}, {"password": password}]},
                                {"_id": False, "name": True, "email": True, "member since": True})
    if user:
        flash(f"Welcome, {user['name']}!")
        session['user'] = user
        return redirect(url_for('edu'))
    else:
        flash("Invalid email or password.")
        return redirect(url_for('index'))


if __name__ == '__main__':
    app.run(debug=True)
