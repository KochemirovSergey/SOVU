# Журнал исправленных багов

---
---

## Ошибка: BuildError — Could not build url for endpoint 'school.form'

**Как проявлялась:**
- **В консоли:**  
  ```
  werkzeug.routing.exceptions.BuildError: Could not build url for endpoint 'school.form' with values ['token']. Did you mean 'school_panel.form' instead?
  ```
- **На странице:**  
  500 Internal Server Error при открытии `/admin_panel/applications/1`.

**Причина:**  
В шаблоне `templates/admin/application_detail.html` использовались устаревшие endpoint'ы `school.form` и `teacher.form`, которых не существует. Актуальные endpoint'ы: `school_panel.form` и `teacher_panel.form` (по именам blueprint'ов).

**Решение:**  
Заменить в шаблоне:
```jinja2
url_for('school.form', ...) → url_for('school_panel.form', ...)
url_for('teacher.form', ...) → url_for('teacher_panel.form', ...)
```

## Ошибка: NameError: name 'GraduateSchool' is not defined при добавлении школы

**Как проявлялась:**
- **В консоли:**  
  ```
  NameError: name 'GraduateSchool' is not defined
  Traceback (most recent call last):
    File ".../controllers/graduate_controller.py", line 48, in form
      gs = GraduateSchool(
           ^^^^^^^^^^^^^^^
  ```
- **На странице:**  
  500 Internal Server Error при попытке добавить школу.

**Причина:**  
В файле `controllers/graduate_controller.py` не был импортирован класс `GraduateSchool` из `models/graduate.py`.

**Решение:**  
Добавить строку импорта:
```python
from models.graduate import GraduateSchool
```
в начало файла `controllers/graduate_controller.py` рядом с импортами других моделей.

---
## Ошибка: 400 Bad Request при отправке формы регистрации учителя

**Как проявлялась:**
- На странице: стандартная ошибка 400 (Bad Request), без flash-сообщения.
- В консоли сервера: "The CSRF token is missing."

**Причина:**
- В POST-запросе отсутствовал CSRF-токен.

**Решение:**
- Убедиться, что в шаблоне формы есть `{{ csrf_token() }}`.
- Проверить, что Flask-WTF инициализирован, SECRET_KEY не меняется, cookies включены.
- Для JS/AJAX — явно передавать CSRF-токен.
### [22.05.2025] Ошибка BuildError при регистрации учителя

**Симптомы:**
- После отправки данных на странице http://127.0.0.1:5000/teacher_panel/school/<school_token> появлялась ошибка:
- На странице: "BuildError: Could not build url for endpoint 'teacher_panel.self_register_success'. Did you mean 'teacher_panel.self_register' instead?"
- В консоли Flask: werkzeug.routing.exceptions.BuildError: Could not build url for endpoint 'teacher_panel.self_register_success'.

**Причина:**
- В файле controllers/teacher_controller.py дважды объявлялся Blueprint teacher_bp. Первый маршрут self_register_success регистрировался на первом экземпляре Blueprint, который затем затирался вторым объявлением. В результате endpoint 'teacher_panel.self_register_success' не попадал в итоговый Blueprint, и Flask не мог его найти.

**Решение:**
- Удалено дублирующее объявление Blueprint. Все маршруты, включая self_register_success, теперь регистрируются на одном экземпляре Blueprint.

**Как проявлялось в интерфейсе:**
- После отправки формы происходил редирект, который завершался ошибкой 500 и сообщением о невозможности построить url для endpoint 'teacher_panel.self_register_success'.

**Как проявлялось в консоли:**
- werkzeug.routing.exceptions.BuildError: Could not build url for endpoint 'teacher_panel.self_register_success'. Did you mean 'teacher_panel.self_register' instead?