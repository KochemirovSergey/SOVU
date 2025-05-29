import pytest
from playwright.sync_api import sync_playwright

def test_add_graduate():
    import sys
    import time
    import os

    screenshots_dir = "tests/screenshots"
    os.makedirs(screenshots_dir, exist_ok=True)

    test_full_name = f"Тестовый Выпускник {int(time.time())}"

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        # Список для сбора сообщений консоли браузера
        browser_logs = []

        def log_console(msg):
            print(f"[Browser Console][{msg.type.upper()}] {msg.text}")
            browser_logs.append(f"{msg.type.upper()}: {msg.text}")

        page.on("console", log_console)

        # 1. Открываем главную страницу
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

        # 2. Переходим на страницу выпускников
        print("[INFO] Переходим на страницу /admin_panel/graduates")
        page.goto("http://127.0.0.1:5000/admin_panel/graduates")
        screenshot1 = os.path.join(screenshots_dir, "01_graduates_page.png")
        page.screenshot(path=screenshot1)
        print(f"[SUCCESS] Страница выпускников открыта. Скриншот: {screenshot1}")

        # 3. Заполняем форму добавления выпускника
        print(f"[INFO] Заполняем форму: ФИО = '{test_full_name}'")
        page.fill('input[name=\"full_name\"]', test_full_name)
        screenshot2 = os.path.join(screenshots_dir, "02_filled_form.png")
        page.screenshot(path=screenshot2)
        print(f"[SUCCESS] Форма заполнена. Скриншот: {screenshot2}")

        # 4. Нажимаем кнопку "Сохранить"
        print("[INFO] Нажимаем кнопку 'Сохранить'")
        page.click('button[type=\"submit\"], input[type=\"submit\"]')
        page.wait_for_load_state("networkidle")
        screenshot3 = os.path.join(screenshots_dir, "03_after_add.png")
        page.screenshot(path=screenshot3)
        print(f"[SUCCESS] После добавления выпускника. Скриншот: {screenshot3}")

        # 5. Проверяем, что выпускник появился в таблице
        print(f"[INFO] Проверяем наличие выпускника '{test_full_name}' в таблице")
        table_content = page.content()
        assert test_full_name in table_content, f"Выпускник '{test_full_name}' не найден в таблице!"
        print(f"[SUCCESS] Выпускник '{test_full_name}' успешно добавлен.")

        print("\n[INFO] Логи консоли браузера:")
        for log in browser_logs:
            print(log)

        browser.close()