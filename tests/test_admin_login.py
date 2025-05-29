import pytest
from playwright.sync_api import sync_playwright

def test_admin_login():
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

        # 1. Открываем главную страницу
        print("[INFO] Открываем главную страницу http://127.0.0.1:5000/")
        page.goto("http://127.0.0.1:5000/")
        screenshot1 = os.path.join(screenshots_dir, "01_main.png")
        page.screenshot(path=screenshot1)
        print(f"[SUCCESS] Главная страница открыта. Скриншот: {screenshot1}")

        # 2. Кликаем по ссылке 'Вход'
        print("[INFO] Кликаем по ссылке 'Вход'")
        page.click('a.nav-link[href="/auth/login"]')
        screenshot2 = os.path.join(screenshots_dir, "02_login_page.png")
        page.screenshot(path=screenshot2)
        print(f"[SUCCESS] Перешли на страницу: {page.url}. Скриншот: {screenshot2}")

        # 3. Проверяем, что находимся на странице логина
        print("[INFO] Проверяем, что находимся на странице логина")
        assert page.url == "http://127.0.0.1:5000/auth/login", f"Ожидался url /auth/login, получен {page.url}"
        print("[SUCCESS] URL страницы логина корректен.")

        # 4. Заполняем логин и пароль
        print("[INFO] Заполняем логин и пароль")
        page.fill('input[name="username"]', "admin")
        page.fill('input[name="password"]', "admin123")
        screenshot3 = os.path.join(screenshots_dir, "03_filled_login.png")
        page.screenshot(path=screenshot3)
        print(f"[SUCCESS] Логин и пароль заполнены. Скриншот: {screenshot3}")

        # 5. Нажимаем на кнопку 'Войти'
        print("[INFO] Нажимаем на кнопку 'Войти'")
        page.click('button[type="submit"], input[type="submit"]')
        print("[SUCCESS] Кнопка 'Войти' нажата.")

        # 6. Ожидаем загрузку страницы после авторизации
        print("[INFO] Ожидаем загрузку страницы после авторизации")
        page.wait_for_load_state("networkidle")
        screenshot4 = os.path.join(screenshots_dir, "04_after_login.png")
        page.screenshot(path=screenshot4)
        print(f"[SUCCESS] После авторизации. Скриншот: {screenshot4}")

        # 7. Проверяем успешную авторизацию
        print("[INFO] Проверяем успешную авторизацию (наличие 'админ', 'вышли' или /admin в url)")
        content = page.content().lower()
        assert "админ" in content or "вышли" in content or "/admin" in page.url, "Авторизация не удалась"
        print("[SUCCESS] Авторизация успешна.")

        print("\n[INFO] Логи консоли браузера:")
        for log in browser_logs:
            print(log)

        browser.close()