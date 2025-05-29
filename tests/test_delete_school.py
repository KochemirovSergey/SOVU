import pytest
from playwright.sync_api import sync_playwright

def test_delete_school():
    import sys
    import time
    import os

    screenshots_dir = "tests/screenshots"
    os.makedirs(screenshots_dir, exist_ok=True)

    test_name = "test_delete_school"
    city_name = "Салават"
    school_name = "Гимназия № 2"

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
        screenshot0 = os.path.join(screenshots_dir, f"{test_name}_00_main.png")
        page.screenshot(path=screenshot0)
        print(f"[SUCCESS] Главная страница открыта. Скриншот: {screenshot0}")

        # Проверяем, залогинены ли мы (ищем ссылку на /auth/login)
        if page.query_selector('a.nav-link[href="/auth/login"]'):
            print("[INFO] Необходима авторизация, выполняем логин")
            page.click('a.nav-link[href="/auth/login"]')
            page.wait_for_url("**/auth/login")
            print("[INFO] Заполняем логин и пароль")
            page.fill('input[name="username"]', "admin")
            page.fill('input[name="password"]', "admin123")
            page.click('button[type="submit"], input[type="submit"]')
            page.wait_for_load_state("networkidle")
            print("[SUCCESS] Авторизация выполнена")
        else:
            print("[INFO] Уже авторизованы")

        # 2. Переходим на страницу школ
        print("[INFO] Переходим на страницу /admin_panel/schools")
        page.goto("http://127.0.0.1:5000/admin_panel/schools")
        screenshot1 = os.path.join(screenshots_dir, f"{test_name}_01_schools.png")
        page.screenshot(path=screenshot1)
        print(f"[SUCCESS] Страница школ открыта. Скриншот: {screenshot1}")

        # 3. Ищем школу с нужным городом и названием (по ячейкам)
        print(f"[INFO] Ищем школу: город = '{city_name}', название = '{school_name}'")
        found = False
        rows = page.query_selector_all("table tbody tr")
        for idx, row in enumerate(rows):
            cells = row.query_selector_all("td")
            cell_texts = [cell.inner_text().strip() for cell in cells]
            print(f"[DEBUG] Строка {idx}: {cell_texts}")
            # Проверяем, что в нужных ячейках есть нужные значения
            # Обычно: [номер, название, ..., город, ...]
            if len(cell_texts) >= 4:
                name_cell = cell_texts[1]
                city_cell = cell_texts[3]
                if school_name in name_cell and city_name in city_cell:
                    print(f"[SUCCESS] Найдена строка: {cell_texts}")
                    screenshot2 = os.path.join(screenshots_dir, f"{test_name}_02_found_row.png")
                    row.screenshot(path=screenshot2)
                    print(f"[INFO] Скриншот строки: {screenshot2}")
                    # 4. Нажимаем кнопку "Удалить"
                    delete_btn = row.query_selector('button.btn.btn-sm.btn-danger[type="submit"]')
                    if delete_btn:
                        print("[INFO] Нажимаем кнопку 'Удалить' для найденной школы")
                        # Обработка confirm-диалога, если есть
                        def handle_dialog(dialog):
                            print(f"[BROWSER DIALOG] {dialog.type}: {dialog.message}")
                            dialog.accept()
                        page.once("dialog", handle_dialog)
                        # Находим форму, в которой находится кнопка
                        form = delete_btn.evaluate_handle("btn => btn.closest('form')")
                        if form:
                            print("[DEBUG] Отправляем форму удаления через JS submit()")
                            form.evaluate("form => form.submit()")
                        else:
                            print("[WARN] Не удалось найти форму, кликаем по кнопке")
                            delete_btn.click()
                        page.wait_for_load_state("networkidle")
                        screenshot3 = os.path.join(screenshots_dir, f"{test_name}_03_after_delete.png")
                        page.screenshot(path=screenshot3)
                        print(f"[SUCCESS] После удаления. Скриншот: {screenshot3}")
                        found = True
                    else:
                        print("[ERROR] Кнопка 'Удалить' не найдена в строке!")
                    break

        if not found:
            print(f"[INFO] Школа '{school_name}' в городе '{city_name}' не найдена. Тест завершён.")
            screenshot4 = os.path.join(screenshots_dir, f"{test_name}_04_not_found.png")
            page.screenshot(path=screenshot4)
            print(f"[INFO] Скриншот: {screenshot4}")
            print("\n[INFO] Логи консоли браузера:")
            for log in browser_logs:
                print(log)
            browser.close()
            return

        # 5. Проверяем, что школа исчезла из таблицы
        print(f"[INFO] Проверяем, что школа '{school_name}' в городе '{city_name}' удалена из таблицы")
        page.reload()
        page.wait_for_load_state("networkidle")
        screenshot5 = os.path.join(screenshots_dir, f"{test_name}_05_check_deleted.png")
        page.screenshot(path=screenshot5)
        print(f"[INFO] Скриншот после обновления: {screenshot5}")
        table_content = page.content()
        assert (city_name not in table_content or school_name not in table_content), (
            f"Школа '{school_name}' в городе '{city_name}' всё ещё присутствует в таблице!"
        )
        print(f"[SUCCESS] Школа '{school_name}' в городе '{city_name}' успешно удалена.")

        print("\n[INFO] Логи консоли браузера:")
        for log in browser_logs:
            print(log)

        browser.close()