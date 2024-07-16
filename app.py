from flask import Flask, render_template, request, jsonify, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta
import random
import pathlib
import textwrap
import os
from flask import Flask, render_template, request
import json

import google.generativeai as genai

# Configure API key
os.environ['GOOGLE_API_KEY'] = "AIzaSyD1Qrtk3Fa-XtdG9Xf5CSbffZo4hBYBK_g"  # Replace with your actual API key
genai.configure(api_key=os.environ['GOOGLE_API_KEY'])

# Load the model
model = genai.GenerativeModel('gemini-pro')

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///quiz.db'
db = SQLAlchemy(app)
class Question(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String(255), nullable=False)
    answer = db.Column(db.String(255), nullable=False)
    age_group = db.Column(db.String(10), nullable=False)

    def _repr_(self):
        return f'<Question {self.id}>'
    
class Student(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    age_group = db.Column(db.String(10), nullable=False)
    score = db.Column(db.Integer, default=0)

    def _repr_(self):
        return f'<Student {self.id}: {self.name}, Age: {self.age_group}, Score: {self.score}>'
    
with app.app_context():
    db.create_all()    
def init_db():
    with app.app_context():
        db.create_all()

        if not Question.query.first():
            # Questions for 2-5 years
            questions_2_5 = [
                {'text': 'How many fingers do you have?', 'answer': '10', 'age_group': '2-5'},
                {'text': 'What is the first letter of the alphabet?', 'answer': 'A', 'age_group': '2-5'},
                {'text': 'What does a cat say?', 'answer': 'Meow', 'age_group': '2-5'},
                {'text': 'How many fingers do you have on one hand?','answer':'5', 'age_group':'2-5'},
                {'text': 'With help of which sense organ you can see?','answer':'Eyes', 'age_group':'2-5'},
                {'text': 'Which letter comes after B?','answer':'C', 'age_group':'2-5'},
                {'text': 'What color is the sky during the day?','answer':'Blue', 'age_group':'2-5'},
                {'text': 'How many legs does a cat have?','answer':'4', 'age_group':'2-5'},
                {'text': 'What is the opposite of "big"','answer':'Small', 'age_group':'2-5'},
                {'text': 'What is the shape of a circle?','answer':'ROund', 'age_group':'2-5'},
                {'text': 'What is the color of grass?','answer':'green', 'age_group':'2-5'},
                {'text': 'How many eyes do you have?','answer':'2', 'age_group':'2-5'},
                {'text': 'How many wheels does a bicycle have?','answer':'2', 'age_group':'2-5'},
                {'text': 'Which animal says "quack, quack"?','answer':'', 'age_group':'2-5'},
                {'text': 'What do you use to clean your teeth?','answer':'Toothbrush', 'age_group':'2-5'},
                {'text': 'What is the opposite of "hot"?','answer':'Cold', 'age_group':'2-5'},
                {'text': 'Tell the name of meal you have in morning?','answer':'Breakfast', 'age_group':'2-5'},
                {'text': 'what is name of big,round, white element in sky at night','answer':'Moon', 'age_group':'2-5'},
                {'text': 'Twinkle,twinle little ___','answer':'Stars', 'age_group':'2-5'},
                {'text': 'Tell the name of meal you have in night?','answer':'Dinner', 'age_group':'2-5'}

            ]

            # Questions for 5-8 years
            questions_5_8 = [
                {'text': 'What is the capital of India?', 'answer': 'New Delhi', 'age_group': '5-8'},
                {'text': 'Who is known as the "Father of the Nation" in India?', 'answer': 'Mahatma Gandhi', 'age_group': '5-8'},
                {'text': 'What is the largest planet in our solar system?', 'answer': 'Jupiter', 'age_group': '5-8'},
                # Add more questions for 5-8 years
                {'text': 'What color is the sun?','answer':'Yellow','age_group':'5-8'},
                {'text': 'What do you use to brush your teeth?','answer':'toothbrush','age_group':'5-8'},
                {'text': 'what comes after 999','answer':'1000','age_group':'5-8'},
                {'text': 'primary gas that makes up earth atmosphere?','answer':'Nitrogen','age_group':'5-8'},
                {'text': 'Which is the longest river in the world?','answer':'Nile','age_group':'5-8'},
                {'text': 'What is the name of our galaxy?','answer':'Milky-way','age_group':'5-8'},
                {'text': 'How many continents are there on Earth?','answer':'7','age_group':'5-8'},
                {'text': 'Which is the tallest mountain in the world?','answer':'Mount Everest','age_group':'5-8'},
                {'text': 'Which animal is known as the "King of the Jungle"?','answer':'Lion','age_group':'5-8'},
                {'text': 'Where is the India Gate located?','answer':'New delhi','age_group':'5-8'},
                {'text': 'Who is the Prime Minister of India','answer':'Narendra Modi','age_group':'5-8'}

            ]

            # Questions for 8+ years
            questions_8 = [
                {'text': 'In which year did World War II end?', 'answer': '1945', 'age_group': '8+'},
                {'text': 'Who painted the Mona Lisa?', 'answer': 'Leonardo da Vinci', 'age_group': '8+'},
                {'text': 'What is the currency of US?', 'answer': 'Dollar', 'age_group': '8+'},
                # Add more questions for 8+ years
                {'text':'What is the capital city of France?','answer': 'Paris','age_group':'8+'},
                {'text':'What is the currency of Japan?','answer': 'Yen','age_group':'8+'},
                {'text':'Who was the first President of the India','answer': 'Rajendra Prasad','age_group':'8+'},
                {'text':'Which two elements make up water?','answer': 'hydrogen and oxygen','age_group':'8+'},
                {'text':'what protects us from harmful CFCs?','answer': 'Ozone','age_group':'8+'},
                {'text':'What is the capital city of China?','answer': 'Beijing','age_group':'8+'},
                {'text':'If a train travels at 60 km/h for 3 hours, how far does it travel?','answer': '180','age_group':'8+'},
                {'text':'If a triangle has angles measuring 45°, 45°, and 90°, what type of triangle is it?','answer': 'isosceles','age_group':'8+'},
                {'text':'How many continents are there in the world?','answer': '7','age_group':'8+'},
                {'text':'What is the result of 15*8?','answer': '120','age_group':'8+'},
                {'text':'If a rectangle has a length of 12 units and a width of 8 units, what is its area?','answer': '96','age_group':'8+'},
                {'text':'Which planet is known as the "Red Planet"? Answer this','answer': 'Mars','age_group':'8+'}
                
            ]

            # Add questions to the database
            for questions_set in [questions_2_5, questions_5_8, questions_8]:
                for question_data in questions_set:
                    question = Question(**question_data)
                    db.session.add(question)

            db.session.commit()

    
@app.route('/')
def home():
    return render_template('home.html')

@app.route('/assessment', methods=['GET', 'POST'])
def assessment():
    if request.method == 'POST':
        # Get form data
        problems = request.form['problems']
        strengths = request.form['strengths']
        weaknesses = request.form['weaknesses']
        interests = request.form['interests']

        # Construct prompt
        prompt = f"Given the following information about a specially abled child:\n" \
                 f"- Problems: {problems}\n" \
                 f"- Strengths: {strengths}\n" \
                 f"- Weaknesses: {weaknesses}\n" \
                 f"- Interests: {interests}\n" \
                 f"Please provide some daily tasks that would be beneficial for this child's development, also give each task separated by $ so that i can differentiate them and display them differently"

        try:
            # Generate response from the model
            response = model.generate_content(prompt)
            #, and a future plan
            #, exercises

            #Extract text content (handling potential multiple parts)
            #if response.parts:
            #    text = "\n".join([part.text.strip() for part in response.parts])
            #else:
            text = response.text
          #  tasks = text.split("$")  # Assuming 'text' holds the response text
          #  for task in tasks:
          #      print(task)
            lines = text.split("$")
            lines = [line.strip() for line in lines if line.strip()]

           # print(lines)
#
            
            
          
           # if response.parts:
           #     text = "\n".join([part.text.strip() for part in response.parts])
           # print(text)
           # data = json.loads(text)
            #data = json.loads(text)
            #print(data)
          #  child_development_plan = json.loads(text)
           # tasks = child_development_plan[0]
            #exercises = child_development_plan[1]
           # future_plan = child_development_plan[2]
            #print(tasks) 



            # Extract tasks, exercises, and future plans
           # tasks = data.get('Tasks', {})
           # exercises = data.get('Exercises', {})
           # future_plan = data.get('Future Plan', {})
           # print(tasks)


#
           #     # Parse text content into tasks, exercises, and future_plan
           #     tasks, exercises, future_plan = {}, {}, {}
           #     current_section = None
           #     for line in text.split('\n'):
           #         if line.startswith('<b>Tasks:</b>'):
           #             current_section = tasks
           #         elif line.startswith('<b>Exercises:</b>'):
           #             current_section = exercises
           #         elif line.startswith('<b>Future Plan:</b>'):
           #             current_section = future_plan
           #         elif line.startswith('<b>') and current_section is not None:
           #             parts = line.split('</b>')
           #             key = parts[0][3:].strip()
           #             value = parts[1][1:].strip()
           #             current_section[key] = value
#
                # Pass the structured data to the template for rendering
          #  return render_template('results.html', results=text)
            #else:
             #   return render_template('error.html', error_message="No response from the model.")
            

          #  return render_template('results.html', results={"tasks": tasks, "exercises": exercises, "future_plan": future_plan})
            total_tasks = len(lines)
            completed_tasks = request.form.getlist('completed_tasks')
            completed_percentage = (len(completed_tasks) / total_tasks) * 100 if total_tasks > 0 else 0

            return render_template('results.html', results=lines, completed_percentage=completed_percentage)
           # return render_template('results.html', results=lines)  # Display results in a template

        except Exception as e:
            return render_template('error.html', error_message=str(e))  # Handle errors gracefully
        

    else:
        return render_template('form.html')  # Show the form initially
    
@app.route('/quizop')
def quizop():
    return render_template('quizop.html')

@app.route('/quiz', methods=['GET', 'POST'])
def quiz_index():
    if request.method == 'POST':
        return redirect(url_for('enter_name'))
    return render_template('index.html')

@app.route('/enter_name', methods=['GET', 'POST'])
def enter_name():
    if request.method == 'POST':
        name = request.form.get('name')
        if name:
            age_group = request.form.get('age')
            if age_group:
                student = Student(name=name, age_group=age_group)
                db.session.add(student)
                db.session.commit()
                return redirect(url_for('quiz_by_age', name=name, age_group=age_group))

    return render_template('enter_name.html')
    
@app.route('/quiz/<name>/<age_group>', methods=['GET', 'POST'])
def quiz_by_age(name, age_group):
    if request.method == 'POST':
        questions = get_daily_questions(age_group)

        # Initialize score for the current quiz attempt
        quiz_score = 0

        for question in questions:
            user_answer = request.form.get(f'answer_{question.id}')
            correct_answer = get_correct_answer(question.id)

            # Check if the answer is correct and update the quiz score
            if user_answer.lower() == correct_answer.lower():
                quiz_score += 1

        # Update the student's total score after completing the quiz
        student = Student.query.filter_by(name=name, age_group=age_group).first()
        student.score += quiz_score
        print(f"Score updated for {student.name}: {student.score}")
        db.session.commit()

    questions = get_daily_questions(age_group)
    return render_template('quiz.html', questions=questions, name=name, age_group=age_group)

def get_daily_questions(age_group):
    questions = Question.query.filter_by(age_group=age_group).all()
    random.shuffle(questions)
    return random.sample(questions,min(5, len(questions)))

def get_correct_answer(question_id):
    return Question.query.get(question_id).answer 


if __name__ == '__main__':
    app.run(debug=True)




