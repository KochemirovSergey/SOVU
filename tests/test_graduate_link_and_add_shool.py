import pytest
from playwright.sync_api import sync_playwright

def test_graduate_link():
    import sys
    import time
    import os

    screenshots_dir = "tests/screenshots"
    os.makedirs(screenshots_dir, exist_ok=True)

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        # Список для сбора сообщений консоли браузера
        browser_logs = []

        def log_console(msg):
            print(f"[Browser Console][{msg.type.upper()}] {msg.text}")
            browser_logs.append(f"{msg.type.upper()}: {msg.text}")

        page.on("console", log_console)

        # ЛОГИН
        print("[INFO] Открываем главную страницу http://127.0.0.1:5000/")
        page.goto("http://127.0.0.1:5000/")
        # Проверяем, залогинены ли мы (ищем ссылку на /auth/login)
        if page.query_selector('a.nav-link[href="/auth/login"]'):
            print("[INFO] Необходима авторизация, выполняем логин")
            page.click('a.nav-link[href="/auth/login"]')
            page.wait_for_url("**/auth/login")
            print("[INFO] Заполняем логин и пароль")
            page.fill('input[name="username"]', "admin")
            page.fill('input[name="password"]', "admin123")
            page.click('button[type=\"submit\"], input[type=\"submit\"]')
            page.wait_for_load_state("networkidle")
            print("[SUCCESS] Авторизация выполнена")
        else:
            print("[INFO] Уже авторизованы")

        def log_console(msg):
            print(f"[Browser Console][{msg.type.upper()}] {msg.text}")
            browser_logs.append(f"{msg.type.upper()}: {msg.text}")

        page.on("console", log_console)

        # 1. Открываем страницу выпускников
        print("[INFO] Открываем страницу http://127.0.0.1:5000/admin_panel/graduates")
        page.goto("http://127.0.0.1:5000/admin_panel/graduates")
        screenshot1 = os.path.join(screenshots_dir, "test_graduate_link_01_graduates.png")
        page.screenshot(path=screenshot1)
        print(f"[SUCCESS] Страница выпускников открыта. Скриншот: {screenshot1}")

        # 2. Явно ждем появления хотя бы одной строки таблицы выпускников
        print("[INFO] Ждем появления первого выпускника в таблице")
        try:
            page.wait_for_selector("table tr", timeout=5000)
        except Exception as e:
            print("[ERROR] Не удалось дождаться строки таблицы: ", e)
            print("[DEBUG] HTML страницы:\n", page.content())
            raise AssertionError("В таблице нет ни одного выпускника (wait_for_selector не сработал)!")

        # Ищем первую строку с <td> (данные, а не заголовок)
        first_row = page.query_selector("table tbody tr")
        if not first_row:
            print("[ERROR] Не удалось найти строку таблицы даже после ожидания!")
            print("[DEBUG] HTML страницы:\n", page.content())
        assert first_row, "В таблице нет ни одного выпускника!"

        print("[DEBUG] HTML первой строки таблицы:")
        print(first_row.inner_html())

        # 3. Нажимаем на кнопку 'Ссылка' в первой строке
        print("[INFO] Нажимаем на кнопку 'Ссылка' у первого выпускника")
        # Ищем <a> с текстом "Ссылка" или с иконкой bi-link
        link_button = first_row.query_selector('a:has-text("Ссылка")')
        if not link_button:
            # Пробуем по классу и иконке
            all_links = first_row.query_selector_all('a')
            print(f"[DEBUG] Найдено ссылок в строке: {len(all_links)}")
            for idx, a in enumerate(all_links):
                print(f"[DEBUG] Ссылка {idx}: {a.inner_html()}")
                if "bi-link" in a.inner_html():
                    link_button = a
                    break
        assert link_button, "Кнопка 'Ссылка' не найдена в первой строке!"
        link_button.click()
        page.wait_for_load_state("networkidle")
        screenshot2 = os.path.join(screenshots_dir, "test_graduate_link_02_link_page.png")
        page.screenshot(path=screenshot2)
        print(f"[SUCCESS] Открыта страница ссылки выпускника. Скриншот: {screenshot2}")

        # 4. Проверяем, что мы на странице /admin_panel/graduates/<id>/link
        assert "/admin_panel/graduates/" in page.url and page.url.endswith("/link"), f"Ожидался url /admin_panel/graduates/<id>/link, получен {page.url}"

        # 5. Нажимаем на кнопку 'Копировать'
        print("[INFO] Нажимаем на кнопку 'Копировать'")
        # Получаем значение ссылки из input
        link_input = page.query_selector('input#graduateLink')
        assert link_input, "Поле с ссылкой не найдено!"
        graduate_link = link_input.get_attribute("value")
        assert graduate_link, "Ссылка для выпускника пуста!"
        copy_button = page.query_selector('button:has-text("Копировать")')
        assert copy_button, "Кнопка 'Копировать' не найдена!"
        copy_button.click()
        screenshot3 = os.path.join(screenshots_dir, "test_graduate_link_03_copied.png")
        page.screenshot(path=screenshot3)
        print(f"[SUCCESS] Кнопка 'Копировать' нажата. Скриншот: {screenshot3}")

        # 6. Переходим по скопированной ссылке
        print(f"[INFO] Переходим по скопированной ссылке: {graduate_link}")
        page.goto(graduate_link)
        page.wait_for_load_state("networkidle")
        screenshot4 = os.path.join(screenshots_dir, "test_graduate_link_04_school_form.png")
        page.screenshot(path=screenshot4)
        print(f"[SUCCESS] Открыта страница по ссылке. Скриншот: {screenshot4}")

        # 7. Проверяем, что это страница заполнения школы (по url и заголовку)
        assert "graduate" in page.url or "school" in page.url, f"Ожидалась страница заполнения школы, получен url: {page.url}"
        content = page.content()
        assert "школ" in content.lower() or "форма" in content.lower(), "Не найдена форма заполнения школы на открытой странице!"

        # 8. Заполняем форму школы: город, школа, годы, классы
        print("[INFO] Заполняем форму школы: город, школа, годы, классы")
        page.fill('input#city', "Салават")
        page.fill('input#school_name', "Гимназия №2")
        page.select_option('select#start_year', "1987")
        page.select_option('select#end_year', "2013")
        screenshot5 = os.path.join(screenshots_dir, "test_graduate_link_05_school_form_filled.png")
        page.screenshot(path=screenshot5)
        print(f"[SUCCESS] Форма школы заполнена. Скриншот: {screenshot5}")

        # 9. Нажимаем на кнопку "Найти школу"
        print("[INFO] Нажимаем на кнопку 'Найти школу'")
        page.click('button#find_school_btn')
        # 10. Дожидаемся появления блока с найденной школой (school_info_block)
        try:
            page.wait_for_selector("#school_info_block", timeout=10000)
            print("[SUCCESS] Данные школы получены (появился блок school_info_block)")
        except Exception as e:
            print("[ERROR] Не удалось дождаться school_info_block: ", e)
            print("[DEBUG] HTML страницы:\n", page.content())
            raise AssertionError("Не появились данные школы (school_info_block) после поиска!")
        screenshot6 = os.path.join(screenshots_dir, "test_graduate_link_06_school_found.png")
        page.screenshot(path=screenshot6)
        print(f"[SUCCESS] Данные школы отображены. Скриншот: {screenshot6}")

        # 11. Нажимаем на кнопку "Подтвердить школу"
        print("[INFO] Нажимаем на кнопку 'Подтвердить школу'")
        confirm_btn = page.query_selector('button[type="submit"][name="action"][value="confirm"]')
        assert confirm_btn, "Кнопка 'Подтвердить школу' не найдена!"
        confirm_btn.click()
        # 12. Дожидаемся успешного добавления школы (появление в списке)
        try:
            page.wait_for_selector('.card.mt-4 ul li', timeout=10000)
            print("[SUCCESS] Школа добавлена и отображается в списке")
        except Exception as e:
            print("[ERROR] Не удалось дождаться появления школы в списке: ", e)
            print("[DEBUG] HTML страницы:\n", page.content())
            raise AssertionError("Школа не появилась в списке после подтверждения!")
        screenshot7 = os.path.join(screenshots_dir, "test_graduate_link_07_school_confirmed.png")
        page.screenshot(path=screenshot7)
        print(f"[SUCCESS] Школа подтверждена и отображается в списке. Скриншот: {screenshot7}")

        # Проверяем, что в списке есть нужная школа и период (расширенная проверка)
        card_html = page.inner_html('.card.mt-4')
        print("[DEBUG] HTML .card.mt-4:\n", card_html)
        # Проверка по <li> — каждая школа отдельным элементом
        try:
            from bs4 import BeautifulSoup
        except ImportError:
            print("[ERROR] Для проверки нужен пакет beautifulsoup4. Установите: pip install beautifulsoup4")
            raise
        soup = BeautifulSoup(card_html, "html.parser")
        li_list = soup.find_all("li")
        found_school = False
        found_period = False
        for idx, li in enumerate(li_list):
            li_text = li.get_text(separator=" ", strip=True).lower()
            print(f"[DEBUG] Школа {idx}: {li_text}")
            if "гимназия" in li_text and "2" in li_text:
                found_school = True
            if (
                "1987–2013" in li_text
                or "1987-2013" in li_text
                or "1987 — 2013" in li_text
            ):
                found_period = True
        if not found_school:
            print("[ERROR] Не найдено <li> с названием школы, содержащим 'гимназия' и '2'")
            for idx, li in enumerate(li_list):
                print(f"[DEBUG] <li> {idx}: {li.get_text(separator=' ', strip=True)}")
        assert found_school, "В списке нет добавленной школы с названием, содержащим 'Гимназия № 2'!"
        assert found_period, "В списке нет нужного периода обучения!"

        print("\n[INFO] Логи консоли браузера:")
        for log in browser_logs:
            print(log)

        # 13. Переходим на страницу заявок
        print("[INFO] Открываем страницу заявок http://127.0.0.1:5000/admin_panel/applications")
        page.goto("http://127.0.0.1:5000/admin_panel/applications")
        page.wait_for_load_state("networkidle")
        screenshot8 = os.path.join(screenshots_dir, "test_graduate_link_08_applications.png")
        page.screenshot(path=screenshot8)
        print(f"[SUCCESS] Страница заявок открыта. Скриншот: {screenshot8}")

        # 14. Проверяем, что для тестового выпускника создалась заявка
        print("[INFO] Проверяем наличие заявки для выпускника 'Тест для заявки' со статусом 'Создана'")
        try:
            page.wait_for_selector("table tr", timeout=5000)
        except Exception as e:
            print("[ERROR] Не удалось дождаться строк таблицы заявок: ", e)
            print("[DEBUG] HTML страницы заявок:\n", page.content())
            raise AssertionError("В таблице заявок нет ни одной строки (wait_for_selector не сработал)!")

        # Ищем строку с нужным выпускником и статусом
        rows = page.query_selector_all("table tbody tr")
        found = False
        for idx, row in enumerate(rows):
            row_html = row.inner_html()
            print(f"[DEBUG] Заявка {idx} HTML: {row_html}")
            if (
                "Тест" in row_html
                and ("Создана" in row_html or "bg-primary" in row_html)
            ):
                found = True
                print(f"[SUCCESS] Найдена заявка для 'Тест для заявки' со статусом 'Создана' (строка {idx})")
                break
        if not found:
            print("[ERROR] Не найдена заявка для 'Тест для заявки' со статусом 'Создана'!")
            print("[DEBUG] HTML таблицы заявок:\n", page.inner_html("table"))
        assert found, "В таблице заявок нет строки для 'Тест для заявки' со статусом 'Создана'!"

        # 15. Открываем страницу заявки через кнопку "Просмотр"
        print("[INFO] Открываем страницу заявки через кнопку 'Просмотр'")
        application_row = None
        for idx, row in enumerate(rows):
            row_html = row.inner_html()
            if (
                "Тест" in row_html
                and ("Создана" in row_html or "bg-primary" in row_html)
            ):
                application_row = row
                break
        assert application_row, "Не найдена строка заявки для открытия!"

        view_btn = application_row.query_selector('a.btn-info, a:has-text("Просмотр")')
        assert view_btn, "Кнопка 'Просмотр' не найдена в строке заявки!"
        view_btn.click()
        page.wait_for_load_state("networkidle")
        screenshot9 = os.path.join(screenshots_dir, "test_graduate_link_09_application_view.png")
        page.screenshot(path=screenshot9)
        print(f"[SUCCESS] Открыта страница заявки. Скриншот: {screenshot9}")

        # 16. Проверяем, что создалась ссылка для школы
        print("[INFO] Проверяем наличие ссылки для школы на странице заявки")
        # Пробуем найти input с value (ссылка) или <a>
        school_link = None
        link_input = page.query_selector('input[type="text"][value*="http"]')
        if link_input:
            school_link = link_input.get_attribute("value")
        else:
            link_a = page.query_selector('a[href*="http"]')
            if link_a:
                school_link = link_a.get_attribute("href")
        assert school_link, "Ссылка для школы не найдена на странице заявки!"
        print(f"[SUCCESS] Ссылка для школы найдена: {school_link}")
        screenshot10 = os.path.join(screenshots_dir, "test_graduate_link_10_school_link.png")
        page.screenshot(path=screenshot10)

        # 17. Переходим по скопированной ссылке школы
        print(f"[INFO] Переходим по ссылке школы: {school_link}")
        page.goto(school_link)
        page.wait_for_load_state("networkidle")
        screenshot11 = os.path.join(screenshots_dir, "test_graduate_link_11_school_page.png")
        page.screenshot(path=screenshot11)
        print(f"[SUCCESS] Открыта страница школы по ссылке. Скриншот: {screenshot11}")

        # 18. Проверяем, что на странице школы отображается выпускник "Тест для заявки"
        print("[INFO] Проверяем, что на странице школы отображается выпускник 'Тест для заявки'")
        school_page_content = page.content()
        assert "Тест" in school_page_content, "Выпускник 'Тест для заявки' не найден на странице школы!"
        # Проверяем период и школу (допускаем разные тире)
        assert (
            "1987–2013" in school_page_content
            or "1987-2013" in school_page_content
            or "1987 — 2013" in school_page_content
        ), "Период обучения '1987–2013' не найден на странице школы!"
        assert (
            "Гимназия № 2" in school_page_content
            or "Гимназия №2" in school_page_content
        ), "Название школы 'Гимназия № 2' не найдено на странице школы!"

        browser.close()