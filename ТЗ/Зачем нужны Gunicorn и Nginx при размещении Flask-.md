<img src="https://r2cdn.perplexity.ai/pplx-full-logo-primary-dark%402x.png" class="logo" width="120"/>

## Зачем нужны Gunicorn и Nginx при размещении Flask-приложения

### **Gunicorn**

- **Gunicorn** — это производительный сервер приложений WSGI для Python, который умеет обрабатывать множество одновременных запросов благодаря своей архитектуре с несколькими рабочими процессами (pre-fork worker model)[^1][^4].
- Flask имеет встроенный сервер (`app.run()`), но он предназначен только для разработки и не выдерживает высокой нагрузки, не обеспечивает безопасности и не поддерживает параллелизм на уровне, необходимом для production[^1][^4].
- Gunicorn принимает HTTP-запросы, преобразует их в формат, понятный Flask, вызывает ваш код и возвращает ответ[^4].
- Gunicorn может работать с несколькими процессами, что позволяет обрабатывать множество запросов одновременно и использовать ресурсы сервера эффективнее[^4].


### **Nginx**

- **Nginx** — это веб-сервер, который выступает в роли обратного прокси (reverse proxy) между интернетом и Gunicorn[^4][^6].
- Nginx принимает все входящие HTTP/HTTPS-запросы от клиентов и передаёт их на Gunicorn, а затем возвращает ответы обратно пользователям[^4][^6].
- Nginx умеет:
    - Обслуживать статические файлы (CSS, JS, изображения) быстрее и эффективнее, чем Gunicorn[^4].
    - Кэшировать статический контент.
    - Балансировать нагрузку между несколькими экземплярами Gunicorn (если приложение масштабируется)[^4].
    - Ограничивать скорость запросов, фильтровать нежелательный трафик и обеспечивать дополнительную безопасность[^4].
    - Работать с SSL-сертификатами для HTTPS, разгружая Gunicorn от этой задачи[^2][^4].


### **Схема взаимодействия**

1. **Клиент** отправляет запрос на сервер.
2. **Nginx** принимает запрос на 80/443 порту, обрабатывает статические файлы или проксирует запрос к Gunicorn.
3. **Gunicorn** запускает Flask-приложение, обрабатывает динамический запрос и возвращает результат через Nginx обратно клиенту[^4][^6].

---

## Детальная инструкция по этапу "Размещение приложения в продакшене"

### **1. Установка Gunicorn**

```bash
pip install gunicorn
```

Gunicorn устанавливается в ваше виртуальное окружение Python[^3][^5].

### **2. Запуск приложения через Gunicorn**

```bash
gunicorn --bind 0.0.0.0:8000 app:app
```

- `app:app` — это `имя_файла:имя_приложения`. Например, если ваш файл называется `app.py` и в нём есть `app = Flask(__name__)`, то используйте `app:app`[^1][^3].
- `--bind 0.0.0.0:8000` — Gunicorn слушает на всех интерфейсах порт 8000.


### **3. Демонизация Gunicorn (рекомендуется)**

Чтобы Gunicorn автоматически запускался при старте сервера и не останавливался при выходе из терминала, настройте systemd unit-файл:

```ini
# /etc/systemd/system/myflask.service
[Unit]
Description=Gunicorn instance to serve Flask app
After=network.target

[Service]
User=youruser
Group=www-data
WorkingDirectory=/path/to/your/app
Environment="PATH=/path/to/your/app/venv/bin"
ExecStart=/path/to/your/app/venv/bin/gunicorn --workers 3 --bind unix:/path/to/your/app/app.sock app:app

[Install]
WantedBy=multi-user.target
```

- Перезапустите systemd:

```bash
sudo systemctl start myflask
sudo systemctl enable myflask
```

Теперь Gunicorn будет работать в фоне и автоматически перезапускаться[^6].

### **4. Установка и настройка Nginx**

```bash
sudo apt install nginx
```

Создайте конфиг для вашего приложения:

```nginx
server {
    listen 80;
    server_name your_domain_or_ip;

    location / {
        proxy_pass http://unix:/path/to/your/app/app.sock;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

- `proxy_pass` может быть через сокет (`unix:/path/to/your/app/app.sock`) или через порт (`http://127.0.0.1:8000`), если Gunicorn слушает порт[^3][^7].
- Эти заголовки нужны для передачи реального IP клиента и корректной работы приложения[^6].

Активируйте конфиг и перезапустите Nginx:

```bash
sudo ln -s /etc/nginx/sites-available/myproject /etc/nginx/sites-enabled
sudo nginx -t
sudo systemctl restart nginx
```


### **5. Проверка работы**

- Откройте в браузере ваш домен или IP — приложение должно быть доступно через Nginx на 80 порту.

---

## **Вывод**

**Gunicorn** нужен для запуска Flask-приложения в production, обеспечивая параллелизм и стабильность, а **Nginx** — для приёма внешних запросов, обслуживания статики, безопасности и проксирования динамических запросов к Gunicorn[^2][^4][^6]. Такая архитектура — стандарт для продакшн-развёртывания Python-приложений.

<div style="text-align: center">⁂</div>

[^1]: https://dvmn.org/encyclopedia/web-server/deploy-wsgi-gunicorn-django-flask/

[^2]: https://help.sweb.ru/obsluzhivanie-prilozhenij-flask-s-pomosh6yu-nginx-i-gunicorn-v-ubuntu_1341.html

[^3]: https://www.digitalocean.com/community/tutorials/how-to-serve-flask-applications-with-gunicorn-and-nginx-on-ubuntu-20-04-ru

[^4]: https://flask.ivan-shamaev.ru/overview-python-flask-nginx-gunicorn-app-architecture/

[^5]: https://timeweb.cloud/tutorials/flask/obsluzhivanie-prilozhenij-flask-s-pomoshchyu-nginx-i-gunicorn-v-ubuntu

[^6]: https://dvmn.org/encyclopedia/web-server/deploy-django-nginx-gunicorn/

[^7]: https://www.8host.com/blog/obsluzhivanie-prilozhenij-flask-s-pomoshhyu-gunicorn-i-nginx-v-ubuntu-16-04/

[^8]: https://ru.stackoverflow.com/questions/897228/django-flask-почему-нельзя-без-nginx-в-production

[^9]: https://habr.com/ru/companies/skillbox/articles/764384/

[^10]: https://flask.ivan-shamaev.ru/setup-nginx-and-setting-for-flask-website/

[^11]: https://qna.habr.com/q/873177

[^12]: https://ya.ru/neurum/c/tehnologii/q/kakie_preimuschestva_ispolzovaniya_gunicorn_7874b646

[^13]: https://habr.com/ru/companies/megafon/articles/541826/

[^14]: https://www.digitalocean.com/community/tutorials/how-to-serve-flask-applications-with-gunicorn-and-nginx-on-ubuntu-18-04-ru

[^15]: https://qna.habr.com/q/1302492?from=questions_similar

[^16]: https://ru.stackoverflow.com/questions/590880/flask-nginx-gunicorn-vps-ubuntu-12-04-Домен-без-порта

[^17]: https://docs-python.ru/packages/veb-frejmvork-flask-python/flask-nginx-gunicorn-gevent/

