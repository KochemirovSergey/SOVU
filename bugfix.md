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