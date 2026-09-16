// Todo App client logic

async function fetchTodos() {
  const response = await fetch('/api/todos');
  if (!response.ok) {
    throw new Error(`Failed to fetch todos: ${response.statusText}`);
  }
  return response.json();
}

async function createTodo(title) {
  const response = await fetch('/api/todos', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({ title })
  });
  if (!response.ok) {
    throw new Error(`Failed to create todo: ${response.statusText}`);
  }
  return response.json();
}

async function updateTodo(id, updates) {
  const response = await fetch(`/api/todos/${id}`, {
    method: 'PATCH',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify(updates)
  });
  if (!response.ok) {
    throw new Error(`Failed to update todo: ${response.statusText}`);
  }
  return response.json();
}

async function deleteTodo(id) {
  const response = await fetch(`/api/todos/${id}`, {
    method: 'DELETE'
  });
  if (!response.ok) {
    throw new Error(`Failed to delete todo: ${response.statusText}`);
  }
}

function updateCount(todos) {
  const countElement = document.getElementById('todo-count');
  if (!countElement) return;
  const activeCount = todos.filter(t => !t.done).length;
  countElement.textContent = `${activeCount} items left`;
}

function renderTodos(todos) {
  const listElement = document.getElementById('todo-list');
  if (!listElement) return;

  listElement.innerHTML = '';

  todos.forEach(todo => {
    const li = document.createElement('li');
    li.setAttribute('data-testid', 'todo-item');
    li.setAttribute('data-id', String(todo.id));
    if (todo.done) {
      li.classList.add('done');
    }

    const checkbox = document.createElement('input');
    checkbox.type = 'checkbox';
    checkbox.setAttribute('data-testid', 'todo-toggle');
    checkbox.checked = Boolean(todo.done);
    checkbox.setAttribute('aria-label', `Mark "${todo.title}" as ${todo.done ? 'incomplete' : 'complete'}`);

    checkbox.addEventListener('change', async () => {
      try {
        await updateTodo(todo.id, { done: checkbox.checked });
        await reloadTodos();
      } catch (err) {
        console.error(err);
      }
    });

    const titleSpan = document.createElement('span');
    titleSpan.className = 'title';
    titleSpan.textContent = todo.title;

    const deleteBtn = document.createElement('button');
    deleteBtn.type = 'button';
    deleteBtn.className = 'destroy';
    deleteBtn.setAttribute('data-testid', 'todo-delete');
    deleteBtn.setAttribute('aria-label', `Delete "${todo.title}"`);
    deleteBtn.innerHTML = '&times;';

    deleteBtn.addEventListener('click', async () => {
      try {
        await deleteTodo(todo.id);
        await reloadTodos();
      } catch (err) {
        console.error(err);
      }
    });

    li.appendChild(checkbox);
    li.appendChild(titleSpan);
    li.appendChild(deleteBtn);

    listElement.appendChild(li);
  });

  updateCount(todos);
}

async function reloadTodos() {
  try {
    const todos = await fetchTodos();
    renderTodos(todos);
  } catch (err) {
    console.error(err);
  }
}

async function handleAddTodo() {
  const input = document.getElementById('todo-input');
  if (!input) return;
  const title = input.value.trim();
  if (!title) return;

  try {
    await createTodo(title);
    input.value = '';
    await reloadTodos();
  } catch (err) {
    console.error(err);
  }
}

document.addEventListener('DOMContentLoaded', () => {
  const form = document.getElementById('todo-form');
  const input = document.getElementById('todo-input');
  const addBtn = document.getElementById('todo-add');

  if (form) {
    form.addEventListener('submit', (e) => {
      e.preventDefault();
      handleAddTodo();
    });
  }

  if (addBtn) {
    addBtn.addEventListener('click', (e) => {
      e.preventDefault();
      handleAddTodo();
    });
  }

  if (input) {
    input.addEventListener('keydown', (e) => {
      if (e.key === 'Enter') {
        e.preventDefault();
        handleAddTodo();
      }
    });
  }

  reloadTodos();
});
