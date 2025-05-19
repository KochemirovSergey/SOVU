# Сравнение архитектурной и реальной структуры файлов (по папкам)

**Легенда:**
- 🟩 — соответствует архитектуре (папка или файл явно есть в архитектуре)
- 🟥 — есть в реальной структуре, но нет в архитектуре (файл внутри папки, если в архитектуре указана только папка)
- 🟦 — есть в архитектуре, но отсутствует в реальности

---

```
/
├── 🟩 app.py
├── 🟩 config.py
├── 🟩 requirements.txt
├── 🟩 static/
│   ├── 🟩 css/
│   │   ├── 🟥 style.css
│   ├── 🟩 js/
│   │   ├── 🟥 main.js
│   ├── 🟦 img/
│   ├── 🟩 qr/
│   ├── 🟦 documents/
├── 🟩 templates/
│   ├── 🟩 admin/
│   │   ├── 🟥 application_detail.html
│   │   ├── 🟥 application_document.html
│   │   ├── 🟥 applications.html
│   │   ├── 🟥 graduate_detail.html
│   │   ├── 🟥 graduate_edit.html
│   │   ├── 🟥 graduate_link.html
│   │   ├── 🟥 graduates.html
│   │   ├── 🟥 index.html
│   ├── 🟩 auth/
│   │   ├── 🟥 login.html
│   │   ├── 🟥 profile.html
│   │   ├── 🟥 register.html
│   ├── 🟥 404.html
│   ├── 🟥 500.html
│   ├── 🟥 base.html
│   ├── 🟥 index.html
├── 🟩 models/
│   ├── 🟩 __init__.py
│   ├── 🟩 graduate.py
│   ├── 🟩 school.py
│   ├── 🟩 teacher.py
│   ├── 🟩 application.py
│   ├── 🟥 user.py
├── 🟩 controllers/
│   ├── 🟩 __init__.py
│   ├── 🟩 admin_controller.py
│   ├── 🟩 graduate_controller.py
│   ├── 🟩 school_controller.py
│   ├── 🟩 teacher_controller.py
│   ├── 🟥 auth_controller.py
├── 🟩 services/
│   ├── 🟩 __init__.py
│   ├── 🟩 link_service.py
│   ├── 🟩 qr_service.py
│   ├── 🟩 document_service.py
│   ├── 🟩 voting_service.py
├── 🟩 ai/
│   ├── 🟩 __init__.py
│   ├── 🟩 document_analyzer.py
│   ├── 🟩 llm_search_school.py
├── 🟩 utils/
│   ├── 🟩 __init__.py
│   ├── 🟩 auth.py
│   ├── 🟩 validators.py
│   ├── 🟩 helpers.py
├── 🟥 extensions.py
├── 🟥 llm_search_school.py
├── 🟥 project_overview.md
├── 🟥 architecture.md
├── 🟥 tz.md
├── 🟩 .gitignore
├── 🟩 .cursorrules
├── 🟩 forms/
│   ├── 🟥 __init__.py
│   ├── 🟥 admin_forms.py
│   ├── 🟥 auth_forms.py
├── 🟩 instance/
│   ├── 🟥 app.db