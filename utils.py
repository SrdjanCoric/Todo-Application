def error_for_list_name(name, lists):
    if any(lst['name'] == name for lst in lists):
        return "The list name must be unique."
    elif not 1 <= len(name) <= 100:
        return "The list name must be between 1 and 100 characters"
    return None

def find_list_by_id(list_id, lists):
    return next((lst for lst in lists if lst['id'] == list_id), None)

def error_for_todo(name):
    if not 1 <= len(name) <= 100:
        return "Todo name must be between 1 and 100 characters"

    return None

def find_todo_by_id(todo_id, todos):
    return next((todo for todo in todos if todo['id'] == todo_id), None)

def remove_todo_by_id(todo_id, lst):
    lst['todos'] = [todo for todo in lst['todos'] if todo['id'] != todo_id]
    return None

def mark_all_completed(lst):
    for todo in lst['todos']:
        todo['completed'] = True
    return None

def todos_remaining(lst):
    return sum(1 for todo in lst['todos'] if not todo['completed'])

def is_list_completed(lst):
    return len(lst['todos']) > 0 and todos_remaining(lst) == 0

def is_todo_completed(todo):
    return todo['completed']

def sort_items(items, is_completed):
    sorted_items = sorted(items, key=lambda i: i['name'].lower())
    incomplete_items = [item for item in sorted_items if not is_completed(item)]
    complete_items = [item for item in sorted_items if is_completed(item)]

    return incomplete_items + complete_items