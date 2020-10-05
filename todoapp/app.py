# Import Flask, SQLAlchemy, and Flask-Migarate to allow Python access to script to the database with Object Relational Mapping
from flask import Flask, render_template, request, redirect, url_for, jsonify, abort
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
# Import the sys library
import sys

# Set the flask instance to an app variable for later use
app = Flask(__name__)
# Defind the SQLAlchemy database connection string syntax postgresql://username:password@URL:port/databasename
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:postgres@localhost:5432/todoapp'
# Flask debug mode for live reloading in development mode
# app.run(debug=True)

# Set a db instance to link the SQLAlchemy library to interact with the database
db = SQLAlchemy(app)

# Set a migrate instance to link Flask-Migrate library to interact with the app and db instance
migrate = Migrate(app, db)

# Set a todo class to inherit from db.Model, with attributes mapped to the tablename and columns
class Todo(db.Model):
    __tablename__ = 'todos'
    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.String(), nullable=False)
    completed = db.Column(db.Boolean, nullable=False, default=False)

    def __repr__(self):
        return f'<Todo {self.id} {self.description}>'

# Detect models and create tables for them (if they don't exist already)
# db.create_all()

@app.route('/')
def index():
    return render_template('index.html', data=Todo.query.order_by('id').all()
    )

@app.route('/todos/create', methods=['POST'])
def create_todo():
    error = False
    body = {}
    try:
        description = request.get_json()['description']
        todo = Todo(description=description)
        db.session.add(todo)
        db.session.commit()
        body['description'] = todo.description
    except:
        error = True
        db.session.rollback()
        print(sys.exc_info())
    finally:
        db.session.close()
    if error:
        abort (400)
    else:
        return jsonify (body)

@app.route('/todos/<todo_id>/set-completed', methods=['POST'])
def set_completed_todo(todo_id):
    try:
        completed = request.get_json()['completed']
        todo = Todo.query.get(todo_id)
        todo.completed = completed
        db.session.commit()
    except: 
        db.session.rollback()
    finally:
        db.session.close()
    return redirect(url_for('index'))

@app.route('/todos/<todo_id>', methods=['DELETE'])
def delete_todo(todo_id):
    try:
        Todo.query.filter_by(id=todo_id).delete()
        db.session.commit()
    except:
        db.session.rollback()
    finally:
        db.session.close()
    return jsonify({ 'success': True })

if __name__ == '__main__': 
 app.run()