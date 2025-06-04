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
### [23.05.2025] Подтверждение связки (is_confirmed) не работало через форму школы

**Причина:**  
POST-запрос с параметрами id, link_type, csrf_token отправлялся на /school_panel/<token>, но в коде ожидался параметр link_id, из-за чего обработка подтверждения не выполнялась. В консоли не появлялись print-логи, связанные с подтверждением.

**Как проявлялось:**  
- На странице: статус подтверждения не менялся.
- В консоли: отсутствовали ожидаемые print-логи из confirm_link или form(token).

**Решение:**  
В функцию form(token) в [`controllers/school_controller.py`](controllers/school_controller.py:16) добавлена поддержка обоих вариантов параметра идентификатора связки: link_id и id. Теперь при отправке формы с любым из этих параметров выполняется обработка подтверждения связки с подробными print-логами на каждом этапе (выводятся оба значения, найденный объект, новое значение is_confirmed, коммит). Это устраняет проблему несовпадения имени поля и позволяет корректно менять статус подтверждения.
## [04.06.2025] Ошибка рекурсивного поиска правопреемника школы

**Причина:**  
В рекурсивной функции поиска школ (`extract_school_chain`) при статусе "ликвидирована" рекурсия запускалась корректно, но для правопреемника (`successor_name`) с общим названием (например, "Муниципальное Общеобразовательное Учреждение") LLM не могла извлечь корректные данные — результатом был объект School с пустыми полями.

**Как проявлялась:**  
- В консоли:  
  - [DEBUG] Рекурсия: status=ликвидирована, next_name=Муниципальное Общеобразовательное Учреждение, next_inn=None, seen_inns={'5027093361'}
  - [DEBUG] search_school_info results for Муниципальное Общеобразовательное Учреждение (ИНН=None): [...]
  - [DEBUG] school object: name='' ... status='' ...
- На странице:  
  - Вторая школа (правопреемник) отображалась с пустыми полями, несмотря на то, что рекурсия запускалась.

**Решение:**  
- Добавлено подробное логирование на всех этапах рекурсии и поиска.
- Установлено, что проблема возникает из-за слишком общего successor_name, по которому невозможно однозначно найти школу.
- Для повышения качества поиска рекомендуется:
  - Пробовать искать по ИНН, если он появляется на следующем этапе.
  - Добавлять обработку случая, когда результат пустой, и информировать пользователя о невозможности найти правопреемника по слишком общему названию.

## [04.06.2025] Ошибки после синхронизации моделей LLM и БД

**Причина:**
После удаления полей `is_application` и отношений из модели School возникли множественные ошибки:
1. SQLAlchemy не могла найти свойство 'graduate_schools' в модели School
2. TypeError в GraduateSchoolForm.validate() - неожиданный аргумент 'extra_validators'
3. Blueprint конфликт имен в Flask-Admin
4. Отсутствие полей годов обучения в форме поиска школы

**Как проявлялись:**
- В консоли:
  - `sqlalchemy.exc.InvalidRequestError: Mapper 'Mapper[School(school)]' has no property 'graduate_schools'`
  - `TypeError: GraduateSchoolForm.validate() got an unexpected keyword argument 'extra_validators'`
  - `ValueError: The name 'graduate' is already registered for a different blueprint`
- На странице:
  - Приложение не запускалось
  - Кнопка "Найти школу" не работала (форма не проходила валидацию)

**Решение:**
1. **Исправлены отношения в моделях:** Убраны `back_populates` для School в моделях Graduate, Teacher, Application
2. **Исправлена форма:** Добавлен параметр `extra_validators=None` в метод `validate()` класса GraduateSchoolForm
3. **Исправлен конфликт Blueprint:** Добавлен уникальный `endpoint='graduates_admin'` для Flask-Admin представления Graduate
4. **Дополнен шаблон:** Добавлены поля для ввода годов начала и окончания обучения в форму поиска школы
5. **Улучшен контроллер:** Добавлено логирование и обработка ошибок в функции поиска школы

**Результат:**
Модели данных LLM и БД полностью синхронизированы. Поиск школы работает без дополнительного маппинга. ID присваивается автоматически при сохранении в БД.