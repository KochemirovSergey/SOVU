<img src="https://r2cdn.perplexity.ai/pplx-full-logo-primary-dark%402x.png" class="logo" width="120"/>

## Пошаговая инструкция по размещению Flask-проекта на VPS

**1. Подключение к серверу по SSH**

- Откройте терминал на вашем компьютере.
- Подключитесь к серверу командой:

```
ssh username@your_server_ip
```

Замените `username` на имя пользователя, а `your_server_ip` — на IP-адрес вашего VPS[^1][^2][^9].

**2. Обновление системы и установка Python**

- Обновите пакеты:

```
sudo apt update && sudo apt upgrade -y
```

- Проверьте наличие Python:

```
python3 -V
```

Если Python не установлен, установите его:

```
sudo apt install python3
```

- Установите модуль для виртуальных окружений:

```
sudo apt install python3-venv
```


**3. Создание структуры проекта и виртуального окружения**

- Создайте папку для проекта и перейдите в неё:

```
mkdir my_flask_project
cd my_flask_project
```

- Создайте виртуальное окружение:

```
python3 -m venv venv
```

- Активируйте виртуальное окружение:

```
source venv/bin/activate
```


**4. Установка Flask и зависимостей**

- Установите Flask:

```
pip install Flask
```

- Проверьте установку:

```
python -m flask --version
```

Если вы видите информацию о версиях Flask и Python — всё в порядке[^1][^2].

**5. Создание простого Flask-приложения**

- Создайте файл приложения, например `app.py`:

```python
from flask import Flask
app = Flask(__name__)

@app.route("/")
def hello():
    return "<h1>Hello, World!</h1>"

if __name__ == "__main__":
    app.run(host='0.0.0.0')
```

- Запустите приложение:

```
python3 app.py
```

- Перейдите в браузере по адресу `http://your_server_ip:5000` и убедитесь, что приложение работает[^2].

**6. Размещение приложения в продакшене (рекомендуется)**

Для постоянной и безопасной работы приложения используйте связку Gunicorn и Nginx:

- Установите Gunicorn:

```
pip install gunicorn
```

- Запустите приложение через Gunicorn:

```
gunicorn --bind 0.0.0.0:8000 app:app
```

Здесь `app:app` означает `имя_файла:имя_приложения` (без `.py`)[^17].
- Установите и настройте Nginx, чтобы он проксировал запросы на Gunicorn. Пример конфигурации для Nginx:

```
server {
    listen 80;
    server_name your_domain_or_ip;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

- Перезапустите Nginx:

```
sudo systemctl restart nginx
```

- Теперь ваше приложение будет доступно по вашему домену или IP-адресу на 80 порту[^17][^12][^13].


## Кратко

1. Подключитесь к VPS по SSH.
2. Установите Python и создайте виртуальное окружение.
3. Установите Flask.
4. Разместите код приложения.
5. Для продакшена используйте Gunicorn и настройте Nginx для проксирования запросов.

Такой подход обеспечит корректную и стабильную работу вашего Flask-проекта на VPS[^1][^2][^17].

<div style="text-align: center">⁂</div>

[^1]: https://help.reg.ru/support/servery-vps/oblachnyye-servery/ustanovka-programmnogo-obespecheniya/kak-ustanovit-flask-na-vps

[^2]: https://vpsup.ru/stati/ustanovka-flask-na-vps-c-ubuntu.html

[^3]: https://help.reg.ru/support/hosting/php-asp-net-i-skripty/kak-ustanovit-flask-na-hosting

[^4]: https://flask.ivan-shamaev.ru/python-flask-vps-tutorial/

[^5]: https://2domains.ru/support/hosting/ustanovka-flask-na-khosting

[^6]: https://flask.ivan-shamaev.ru/python-flask-initial-setting-vps-server/

[^7]: https://www.youtube.com/watch?v=A7R1IdkotoU

[^8]: https://beget.com/ru/kb/how-to/web-apps/video-ustanovka-flask-na-virtualnyj-hosting

[^9]: https://alexhost.com/ru/faq/kak-ustanovit-flask-na-hosting/

[^10]: https://kb.justhost.ru/article/1496

[^11]: https://help.sweb.ru/ustanovka-flask-na-virtual6nom-hostinge_1282.html

[^12]: https://flask.website/install/apache

[^13]: https://hww.ru/2020/06/publikacija-python-sajta-na-baze-flask-na-veb-servere-nginx/

[^14]: https://timeweb.cloud/tutorials/cloud/razvertyvanie-proekta-python-flask

[^15]: https://habr.com/ru/articles/833446/

[^16]: https://serverspace.ru/support/help/kak-napisat-web-prilozhenie-na-flask/

[^17]: https://devhops.ru/i/flask/deploy.php

[^18]: https://younglinux.info/flask/apache

