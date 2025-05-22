# Таблица соответствия файлов архитектуре с детализацией по элементам

| Путь к файлу | Статус | Краткое описание | Входящие элементы | Предназначение |
|--------------|--------|------------------|-------------------|---------------|
| app.py | 🟩 | Точка входа | Flask-приложение, регистрация blueprint'ов, инициализация расширений | Запуск и конфигурирование всего приложения |
| config.py | 🟩 | Конфиг | Класс Config, переменные окружения | Хранение конфигурации Flask, БД, секретов |
| requirements.txt | 🟩 | Зависимости | Список библиотек | Описание зависимостей для установки через pip |
| static/css/style.css | 🟥 | Стили | CSS-классы: .footer, .card, .form-group, .vote-item и др. | Оформление интерфейса, стилизация страниц и компонентов |
| static/js/main.js | 🟥 | JS-логика | Функции: initApp, initTooltips, initForms, displaySchoolSearchResults; обработчики событий | Динамика интерфейса, обработка форм, поиск школы, работа с динамическими полями |
| static/img/ | 🟦 | Изображения | — | Каталог для хранения изображений (не реализован) |
| static/qr/ | 🟩 | QR-коды | — | Каталог для хранения сгенерированных QR-кодов |
| static/documents/ | 🟦 | Документы | — | Каталог для сгенерированных документов (не реализован) |
| templates/base.html | 🟥 | Базовый шаблон | Блоки Jinja2: title, content, extra_css, extra_js; navbar, footer | Базовый шаблон для всех страниц, структура и оформление |
| templates/index.html | 🟥 | Главная | Форма поиска, таблицы, JS-скрипт, блоки вывода результатов | Главная страница поиска школы, отображение информации |
| templates/admin/ | 🟩 | Шаблоны админки | — | Каталог шаблонов для административной панели |
| templates/admin/application_detail.html | 🟥 | Детали заявки | Блоки Jinja2, формы, кнопки | Страница с деталями заявки для админа |
| templates/admin/application_document.html | 🟥 | Документ заявки | Блоки Jinja2, формы, кнопки | Генерация/редактирование письма-запроса |
| templates/admin/applications.html | 🟥 | Список заявок | Таблица заявок, фильтр, кнопки | Список всех заявок в админке |
| templates/admin/graduate_detail.html | 🟥 | Детали выпускника | Блоки Jinja2, кнопки | Страница с деталями выпускника |
| templates/admin/graduate_edit.html | 🟥 | Редактирование выпускника | Форма редактирования, кнопки | Редактирование данных выпускника |
| templates/admin/graduate_link.html | 🟥 | Ссылка выпускника | Ссылка, кнопка копирования | Отображение уникальной ссылки выпускника |
| templates/admin/graduates.html | 🟥 | Список выпускников | Таблица выпускников, кнопки | Список всех выпускников |
| templates/admin/index.html | 🟥 | Главная админки | Навигация, карточки, кнопки | Главная страница административной панели |
| templates/auth/ | 🟩 | Шаблоны auth | — | Каталог шаблонов для аутентификации |
| templates/auth/login.html | 🟥 | Вход | Flask-WTF форма, поля username, password, кнопка submit | Страница входа администратора |
| templates/auth/profile.html | 🟥 | Профиль | Вывод username, email, роль, кнопка возврата | Страница профиля пользователя |
| templates/auth/register.html | 🟥 | Регистрация | Flask-WTF форма, поля username, email, password, submit | Регистрация нового администратора |
| templates/404.html | 🟥 | 404 | Сообщение об ошибке, кнопка возврата | Страница ошибки 404 |
| templates/500.html | 🟥 | 500 | Сообщение об ошибке, кнопка возврата | Страница ошибки 500 |
| models/__init__.py | 🟩 | Инициализация | Импорт моделей | Настройка пакета models |
| models/graduate.py | 🟩 | Модель выпускника | Классы: Graduate, GraduateSchool, Vote | Описание моделей выпускника, связей, голосования |
| models/school.py | 🟩 | Модель школы | Классы: School, TeacherSchool | Описание моделей школы и связей с учителями |
| models/teacher.py | 🟩 | Модель учителя | Классы: Teacher, TeacherSchool | Описание модели учителя и связей со школами |
| models/application.py | 🟩 | Модель заявки | Класс: Application, методы, связи | Описание модели заявки, связи с выпускником и школой |
| models/user.py | 🟥 | Модель пользователя | Класс: User | Модель пользователя для аутентификации админа |
| controllers/__init__.py | 🟩 | Инициализация | Импорт контроллеров | Настройка пакета controllers |
| controllers/admin_controller.py | 🟩 | Контроллер админки | Маршруты Flask, функции: index, graduates, applications и др. | CRUD для выпускников, заявок, школ, учителей, генерация ссылок и документов |
| controllers/graduate_controller.py | 🟩 | Контроллер выпускника | Маршруты Flask, функции: form, vote | Форма для выпускника, создание заявки, голосование |
| controllers/school_controller.py | 🟩 | Контроллер школы | Маршруты Flask, функции: form, update | Форма для школы, обновление данных, просмотр учителей |
| controllers/teacher_controller.py | 🟩 | Контроллер учителя | Маршруты Flask, функции: form, document | Форма для учителя, загрузка документов, верификация |
| controllers/auth_controller.py | 🟥 | Контроллер auth | Маршруты Flask, функции: login, logout, register, profile | Аутентификация и регистрация администратора |
| services/__init__.py | 🟩 | Инициализация | Импорт сервисов | Настройка пакета services |
| services/link_service.py | 🟩 | Сервис ссылок | Класс: LinkService, методы генерации токенов, ссылок, QR | Генерация токенов, ссылок, QR-кодов для разных ролей |
| services/qr_service.py | 🟩 | Сервис QR | Класс: QRService, методы генерации и сохранения QR | Генерация и сохранение QR-кодов для ссылок |
| services/document_service.py | 🟩 | Сервис документов | Класс: DocumentService, методы генерации писем, сохранения | Генерация писем-запросов, сохранение документов |
| services/voting_service.py | 🟩 | Сервис голосования | Класс: VotingService, методы голосования, подсчёта голосов | Логика голосования, подсчёт голосов, топ учителей |
| ai/__init__.py | 🟩 | Инициализация | Импорт модулей ИИ | Настройка пакета ai |
| ai/document_analyzer.py | 🟩 | Анализ документов | Класс: DocumentAnalyzer, методы: extract_text_from_pdf, analyze_document, calculate_verification_score | Анализ документов: извлечение текста из PDF, вызов LLM, парсинг результата, расчет вероятности |
| ai/llm_search_school.py | 🟩 | Поиск школы (ИИ) | Классы: SchoolBasicInfo, SchoolDetailedInfo; функции: get_school_info, process_basic_info, process_detailed_info | Поиск и анализ информации о школах через Tavily API и LLM |
| forms/__init__.py | 🟩 | Инициализация | Импорт форм | Настройка пакета forms |
| forms/admin_forms.py | 🟩 | Формы админки | Классы: GraduateForm, ApplicationFilterForm, ApplicationStatusForm, ApplicationForm | Flask-WTF формы для работы с выпускниками и заявками |
| forms/auth_forms.py | 🟩 | Формы auth | Классы: LoginForm, RegisterForm, методы-валидаторы | Flask-WTF формы для аутентификации, проверки уникальности |
| utils/__init__.py | 🟩 | Инициализация | Импорт утилит | Настройка пакета utils |
| utils/auth.py | 🟩 | Декораторы, токены | Функции: admin_required, token_required, validate_token, generate_password_hash, check_password_hash | Декораторы для проверки прав, работа с токенами и паролями |
| utils/helpers.py | 🟩 | Хелперы | Функции: format_date, format_datetime, get_current_year, load_cities_from_csv, save_to_json, load_from_json, ensure_dir, get_file_extension, is_allowed_file | Форматирование дат, работа с файлами, загрузка/сохранение JSON и CSV, проверка директорий, расширений файлов |
| utils/validators.py | 🟩 | Валидаторы | Функции: validate_email, validate_inn, validate_year, validate_grade, validate_period, validate_full_name | Валидация email, ИНН, года, класса, периода обучения, ФИО |
| extensions.py | 🟥 | Инициализация расширений | Переменные: db, login_manager, csrf, admin; классы: SecureModelView, SecureAdminIndexView | Инициализация расширений Flask, настройка Flask-Admin с ограничением доступа |
| llm_search_school.py | 🟥 | Поиск школы (CLI) | Классы: SchoolBasicInfo, SchoolDetailedInfo; функции: get_school_info, process_basic_info, process_detailed_info, main | CLI-утилита для поиска и анализа информации о школах через Tavily API и LLM |
| .gitignore | 🟩 | Git ignore | Список игнорируемых файлов и папок | Исключение файлов и папок из git-репозитория |
| .cursorrules | 🟩 | VSCode | — | Служебный файл редактора |
| instance/app.db | 🟩 | БД | — | Файл базы данных SQLite |
| project_overview.md | 🟥 | Описание проекта | Markdown-разметка | Описание состояния и структуры проекта |
| file_structure_colored.md | 🟥 | Сравнение структур | Markdown-разметка | Сравнение архитектурной и реальной структуры проекта |
| tz.md | 🟥 | ТЗ | Markdown-разметка | Техническое задание проекта |
| architecture.md | 🟥 | Архитектура | Markdown-разметка | Архитектурное описание проекта |