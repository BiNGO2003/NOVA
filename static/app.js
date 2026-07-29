const $ = (selector) => document.querySelector(selector);
const priorityNames = { high: 'Высокий', medium: 'Средний', low: 'Низкий' };
const priorityCycle = { high: 'medium', medium: 'low', low: 'high' };
let tasks = [], currentFilter = 'all', remaining = 25 * 60, selectedMinutes = 25, timerId, ticking = false;

const csrf = () => document.cookie.split('; ').find((item) => item.startsWith('csrftoken='))?.split('=')[1] || '';
async function api(url, method = 'GET', body) {
  const response = await fetch(url, { method, headers: { 'Content-Type': 'application/json', 'X-CSRFToken': csrf() }, body: body ? JSON.stringify(body) : undefined });
  const data = await response.json();
  if (!response.ok) throw new Error(data.error || 'Система не получила ответ.');
  return data;
}
function notify(text) { const message = $('#statusMessage'); message.textContent = text; message.hidden = false; }
function today() { return new Date().toISOString().slice(0, 10); }
function isOverdue(task) { return !task.completed && task.due_date && task.due_date < today(); }
function formatDeadline(task) {
  if (!task.due_date) return `${priorityNames[task.priority]} приоритет · без срока`;
  const date = new Date(`${task.due_date}T12:00:00`).toLocaleDateString('ru-RU', { day: 'numeric', month: 'short' });
  const time = task.due_time ? ` · ${task.due_time}` : '';
  return `${isOverdue(task) ? 'Просрочено' : task.due_date === today() ? 'Сегодня' : date}${time} · ${priorityNames[task.priority]}`;
}
function visibleTasks() {
  if (currentFilter === 'today') return tasks.filter((task) => !task.completed && task.due_date === today());
  if (currentFilter === 'overdue') return tasks.filter(isOverdue);
  if (currentFilter === 'done') return tasks.filter((task) => task.completed);
  return tasks;
}
function updateSummary() {
  const active = tasks.filter((task) => !task.completed), done = tasks.length - active.length;
  $('#activeCount').textContent = active.length;
  $('#todayCount').textContent = active.filter((task) => task.due_date === today()).length;
  $('#overdueCount').textContent = active.filter(isOverdue).length;
  $('#doneCount').textContent = done;
  $('#progressLabel').textContent = `${done} / ${tasks.length}`;
  $('#progressBar').style.width = tasks.length ? `${(done / tasks.length) * 100}%` : '0%';
  const urgent = active.filter((task) => task.priority === 'high').length;
  $('#briefing').textContent = !active.length ? 'Все задачи закрыты. Редкий порядок — не будем его тревожить без причины.' : urgent ? `Есть ${urgent} задач высокой важности. Сначала та, у которой ближе срок.` : `В работе ${active.length} задач. Укажите следующую — и NOVA не даст ей потеряться.`;
}
function renderPlanner() {
  const timeline = $('#dayTimeline');
  if (!timeline) return;
  const planned = tasks.filter((task) => task.due_date === today() && task.due_time).sort((a, b) => a.due_time.localeCompare(b.due_time));
  const unscheduled = tasks.filter((task) => task.due_date === today() && !task.due_time && !task.completed);
  const hours = Array.from({ length: 14 }, (_, index) => index + 7);
  $('#plannerDate').textContent = new Intl.DateTimeFormat('ru-RU', { day: 'numeric', month: 'long' }).format(new Date());
  timeline.innerHTML = hours.map((hour) => {
    const hourTasks = planned.filter((task) => Number(task.due_time.slice(0, 2)) === hour);
    const cards = hourTasks.map((task) => `<button class="planner-task ${task.completed ? 'done' : ''} priority-${task.priority}" data-id="${task.id}" title="Отметить выполненной"><time>${task.due_time}</time><span>${escapeHtml(task.title)}</span></button>`).join('');
    const time = `${String(hour).padStart(2, '0')}:00`;
    return `<div class="planner-slot"><button class="planner-hour" data-time="${time}" aria-label="Добавить задачу на ${time}">${time}</button><div class="planner-slot-content">${cards || '<span class="planner-empty">Свободно</span>'}</div></div>`;
  }).join('') + (unscheduled.length ? `<div class="planner-unscheduled"><strong>Без времени</strong>${unscheduled.map((task) => `<span>${escapeHtml(task.title)}</span>`).join('')}</div>` : '');
  document.querySelectorAll('.planner-hour').forEach((button) => button.onclick = () => { $('#dueDate').value = today(); $('#dueTime').value = button.dataset.time; $('#taskDialog').showModal(); $('#taskInput').focus(); });
  document.querySelectorAll('.planner-task').forEach((button) => button.onclick = async () => { const task = tasks.find((item) => item.id === Number(button.dataset.id)); if (!task) return; await api(`/api/tasks/${task.id}/`, 'POST', { completed: !task.completed }); await loadTasks(); });
}
function renderTasks() {
  const list = $('#taskList'); list.innerHTML = '';
  const visible = visibleTasks();
  visible.forEach((task) => {
    const item = $('#taskTemplate').content.firstElementChild.cloneNode(true);
    item.classList.toggle('done', task.completed); item.classList.toggle('overdue', isOverdue(task));
    item.querySelector('strong').textContent = task.title;
    item.querySelector('.task-meta').textContent = formatDeadline(task);
    const priority = item.querySelector('.priority-toggle'); priority.textContent = priorityNames[task.priority]; priority.classList.add(`priority-${task.priority}`);
    item.querySelector('.check').onclick = async () => { await api(`/api/tasks/${task.id}/`, 'POST', { completed: !task.completed }); await loadTasks(); };
    priority.onclick = async () => { await api(`/api/tasks/${task.id}/`, 'POST', { priority: priorityCycle[task.priority] }); await loadTasks(); };
    item.querySelector('.delete').onclick = async () => { await api(`/api/tasks/${task.id}/delete/`, 'POST'); notify('Задача удалена.'); await loadTasks(); };
    list.append(item);
  });
  $('#emptyTasks').hidden = visible.length !== 0;
  updateSummary();
  renderPlanner();
}
async function loadTasks() { tasks = (await api('/api/tasks/')).tasks; renderTasks(); }
async function loadNotes() { const notes = (await api('/api/notes/')).notes; $('#noteList').innerHTML = notes.map((note) => `<li><span>${escapeHtml(note.text)}</span><button class="note-delete" data-id="${note.id}" aria-label="Удалить заметку">×</button></li>`).join(''); document.querySelectorAll('.note-delete').forEach((button) => button.onclick = async () => { await api(`/api/notes/${button.dataset.id}/delete/`, 'POST'); notify('Заметка удалена.'); await loadNotes(); }); }
async function loadHabits() { const habits = (await api('/api/habits/')).habits; $('#habitList').innerHTML = habits.map((habit) => `<li><button class="habit-check ${habit.done_today ? 'done' : ''}" data-id="${habit.id}" aria-label="Отметить привычку">${habit.done_today ? '✓' : ''}</button><span>${escapeHtml(habit.name)}</span><small>${habit.streak} дн.</small><button class="habit-delete" data-id="${habit.id}" aria-label="Удалить привычку">×</button></li>`).join(''); document.querySelectorAll('.habit-check').forEach((button) => button.onclick = async () => { await api(`/api/habits/${button.dataset.id}/toggle/`, 'POST'); await loadHabits(); }); document.querySelectorAll('.habit-delete').forEach((button) => button.onclick = async () => { await api(`/api/habits/${button.dataset.id}/delete/`, 'POST'); await loadHabits(); }); }
async function loadMemories() { const memories = (await api('/api/memories/')).memories; $('#memoryList').innerHTML = memories.map((memory) => `<li><div><strong>${escapeHtml(memory.key)}</strong><span>${escapeHtml(memory.value)}</span></div><button class="memory-delete" data-id="${memory.id}" aria-label="Удалить из памяти">×</button></li>`).join(''); document.querySelectorAll('.memory-delete').forEach((button) => button.onclick = async () => { await api(`/api/memories/${button.dataset.id}/delete/`, 'POST'); notify('Запись удалена.'); await loadMemories(); }); }
function escapeHtml(text) { const div = document.createElement('div'); div.textContent = text; return div.innerHTML; }
function renderTimer() { $('#timerDisplay').textContent = `${String(Math.floor(remaining / 60)).padStart(2, '0')}:${String(remaining % 60).padStart(2, '0')}`; }
function setMinutes(value) { clearInterval(timerId); ticking = false; selectedMinutes = value; remaining = value * 60; $('#timerButton').textContent = 'Начать'; $('#focusTitle').textContent = value === 5 ? 'Короткий перерыв' : 'Глубокая работа'; document.querySelectorAll('.preset').forEach((button) => button.classList.toggle('active', +button.dataset.minutes === value)); renderTimer(); }
function toggleTimer() { ticking = !ticking; $('#timerButton').textContent = ticking ? 'Пауза' : 'Продолжить'; if (!ticking) return clearInterval(timerId); timerId = setInterval(() => { if (remaining) { remaining--; renderTimer(); } else { clearInterval(timerId); ticking = false; $('#timerButton').textContent = 'Новая сессия'; notify('Сессия завершена.'); } }, 1000); }
function greeting() { const hour = new Date().getHours(); $('#greeting').textContent = hour < 12 ? 'Доброе утро.' : hour < 18 ? 'Добрый день.' : 'Добрый вечер.'; $('#dateLabel').textContent = new Intl.DateTimeFormat('ru-RU', { weekday: 'long', day: 'numeric', month: 'long' }).format(new Date()); }

$('#openTask').onclick = () => $('#taskDialog').showModal(); $('#closeTask').onclick = () => $('#taskDialog').close(); $('#cancelTask').onclick = () => $('#taskDialog').close();
$('#taskForm').onsubmit = async (event) => { event.preventDefault(); const title = $('#taskInput').value.trim(); if (!title) return; try { await api('/api/tasks/create/', 'POST', { title, priority: $('#priorityInput').value, due_date: $('#dueDate').value, due_time: $('#dueTime').value }); $('#taskForm').reset(); $('#taskDialog').close(); notify('Задача добавлена.'); await loadTasks(); } catch (error) { notify(error.message); } };
$('#noteForm').onsubmit = async (event) => { event.preventDefault(); const text = $('#noteInput').value.trim(); if (!text) return; try { await api('/api/notes/create/', 'POST', { text }); $('#noteInput').value = ''; notify('Заметка сохранена.'); await loadNotes(); } catch (error) { notify(error.message); } };
$('#habitForm').onsubmit = async (event) => { event.preventDefault(); const name = $('#habitInput').value.trim(); if (!name) return; await api('/api/habits/create/', 'POST', { name }); $('#habitInput').value = ''; notify('Привычка добавлена.'); await loadHabits(); };
$('#memoryForm').onsubmit = async (event) => { event.preventDefault(); const key = $('#memoryKey').value.trim(), value = $('#memoryValue').value.trim(); if (!key || !value) return notify('Заполните тему и факт.'); await api('/api/memories/create/', 'POST', { key, value }); $('#memoryForm').reset(); notify('Запись сохранена.'); await loadMemories(); };
document.querySelectorAll('.filter').forEach((button) => button.onclick = () => { currentFilter = button.dataset.filter; document.querySelectorAll('.filter').forEach((item) => item.classList.toggle('active', item === button)); renderTasks(); });
$('#timerButton').onclick = toggleTimer; $('#resetTimer').onclick = () => setMinutes(selectedMinutes); document.querySelectorAll('.preset').forEach((button) => button.onclick = () => setMinutes(+button.dataset.minutes));
$('#themeButton').onclick = () => { document.body.classList.toggle('light'); localStorage.setItem('nova-theme', document.body.classList.contains('light') ? 'light' : 'dark'); }; if (localStorage.getItem('nova-theme') === 'light') document.body.classList.add('light');
greeting(); renderTimer(); Promise.all([loadTasks(), loadNotes(), loadHabits(), loadMemories()]).catch(() => notify('Не удалось получить данные. Проверьте, что сервер запущен.'));
