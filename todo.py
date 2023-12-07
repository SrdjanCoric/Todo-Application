from flask import Flask, session, flash, render_template, url_for, redirect, request

from uuid import uuid4

import os

from functools import wraps

from werkzeug.exceptions import NotFound

from utils import (
    error_for_list_name,
    find_list_by_id,
    error_for_todo,
    find_todo_by_id,
    remove_todo_by_id,
    mark_all_completed,
    todos_remaining,
    is_list_completed,
    sort_items,
    is_todo_completed,
)

app = Flask(__name__)

app.secret_key='secret1'

@app.before_request
def inititalize_session():
    if 'lists' not in session:
        session['lists'] = []

@app.context_processor
def list_utilities_processor():
    return dict(
                is_list_completed=is_list_completed
            )

def require_list(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        list_id = kwargs.get('list_id')
        lst = find_list_by_id(list_id, session['lists'])
        if not lst:
            raise NotFound(description="List not found")
        return f(lst=lst, *args, **kwargs)
    return decorated_function

def require_todo(f):
    @wraps(f)
    @require_list
    def decorated_function(lst, *args, **kwargs):
        todo_id = kwargs.get('todo_id')
        todo = find_todo_by_id(todo_id, lst['todos'])
        if not todo:
            raise NotFound(description="Todo not found")
        return f(lst=lst, todo=todo, *args, **kwargs)
    return decorated_function

@app.route("/")
def index():
    return redirect(url_for('get_lists'))

@app.route("/lists/new")
def add_list():
    return render_template('new_list.html')

@app.route("/lists")
def get_lists():
    lists = sort_items(session['lists'], is_list_completed)
    return render_template('lists.html', lists=lists, todos_remaining = todos_remaining)

@app.route("/lists", methods=["POST"])
def create_list():
    name = request.form["list_name"].strip()
    error = error_for_list_name(name, session['lists'])
    if error:
        flash(error, "error")
        return render_template('new_list.html', title=name)

    session['lists'].append({'id': str(uuid4()), 'name': name, 'todos': []})
    flash("The list has been created.", "success")
    session.modified = True
    return redirect(url_for('get_lists'))

@app.route("/lists/<list_id>")
@require_list
def show_list(lst, list_id):
    todos = sort_items(lst['todos'], is_todo_completed)
    return render_template('list.html', lst=lst, todos=todos)

@app.route("/lists/<list_id>/todos", methods=["POST"])
@require_list
def create_todo(lst, list_id):
    todo_name = request.form["todo"].strip()
    error = error_for_todo(todo_name)
    if error:
        flash(error, "error")
        return render_template('list.html', lst=lst, todo_name=todo_name)
    lst['todos'].append({'id': str(uuid4()), 'name': todo_name, 'completed': False})
    flash("The todo was added.", "success")
    session.modified = True
    return redirect(url_for('show_list', list_id=list_id))

@app.route("/lists/<list_id>/todos/<todo_id>/toggle", methods=["POST"])
@require_todo
def update_todo_status(lst, todo, list_id, todo_id):
    is_completed = request.form['completed'] == 'True'
    todo['completed'] = is_completed

    flash("The todo has been updated.", "success")
    session.modified = True
    return redirect(url_for('show_list', list_id=list_id))

@app.route("/lists/<list_id>/todos/<todo_id>/delete", methods=["POST"])
@require_todo
def delete_todo(lst, todo, list_id, todo_id):
    remove_todo_by_id(todo_id, lst)

    flash("The todo has been deleted.", "success")
    session.modified = True
    return redirect(url_for('show_list', list_id=list_id))

@app.route("/lists/<list_id>/complete_all", methods=["POST"])
@require_list
def mark_all_todos_completed(list_id, lst):
    mark_all_completed(lst)

    flash("All todos have been updated.", "success")
    session.modified = True
    return redirect(url_for('show_list', list_id=list_id))

@app.route("/lists/<list_id>/edit")
@require_list
def edit_list(lst, list_id):
    return render_template('edit_list.html', lst=lst)

@app.route("/lists/<list_id>/delete", methods=["POST"])
@require_list
def delete_list(lst, list_id):
    session['lists'] = [l for l in session['lists'] if l['id'] != list_id]

    flash("The list has been deleted.", "success")
    session.modified = True
    return redirect(url_for('get_lists'))

@app.route("/lists/<list_id>", methods=["POST"])
@require_list
def update_list(lst, list_id):
    name = request.form["list_name"].strip()
    error = error_for_list_name(name, session['lists'])
    if error:
        flash(error, "error")
        return render_template('edit_list.html', lst=lst, name=name)
    lst['name'] = name
    flash("The list has been updated.", "success")
    session.modified = True
    return redirect(url_for('get_lists'))

if __name__ == "__main__":
    if os.environ.get('FLASK_ENV') == 'production':
        app.run(debug=False)
    else:
        app.run(debug=True, port=5003)