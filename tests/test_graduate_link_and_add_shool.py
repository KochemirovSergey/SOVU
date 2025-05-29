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
        page.fill('input#start_grade', "1")
        page.fill('input#end_grade', "11")
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
        # Проверка по подстроке "Гимназия № 2" (с пробелом), допускаем МБОУ/МОУ и любые кавычки
        assert (
            "Гимназия № 2" in card_html
            or "Гимназия №2" in card_html
            or "МОУ Гимназия № 2" in card_html
            or "МБОУ" in card_html and "Гимназия" in card_html
        ), "В списке нет добавленной школы с названием, содержащим 'Гимназия № 2'!"
        # Проверка периода (допускаем разные тире)
        assert (
            "1987–2013" in card_html
            or "1987-2013" in card_html
            or "1987 — 2013" in card_html
        ), "В списке нет нужного периода обучения!"
        # Проверка классов (допускаем разные тире)
        assert (
            "1–11 класс" in card_html
            or "1-11 класс" in card_html
            or "1 — 11 класс" in card_html
        ), "В списке нет нужных классов!"

        print("\n[INFO] Логи консоли браузера:")
        for log in browser_logs:
            print(log)

        browser.close()