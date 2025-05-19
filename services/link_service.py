import secrets
import string
from flask import current_app, url_for

class LinkService:
    """Сервис для генерации ссылок и токенов"""
    
    def generate_token(self, length=32):
        """
        Генерация уникального токена для ссылки
        
        Args:
            length (int): Длина токена
            
        Returns:
            str: Сгенерированный токен
        """
        alphabet = string.ascii_letters + string.digits
        return ''.join(secrets.choice(alphabet) for _ in range(length))
    
    def generate_graduate_link(self, graduate_id):
        """
        Генерация ссылки для выпускника
        
        Args:
            graduate_id (int): ID выпускника
            
        Returns:
            str: Ссылка для выпускника
        """
        from models.graduate import Graduate
        
        graduate = Graduate.query.get(graduate_id)
        if not graduate:
            return None
            
        if not graduate.link_token:
            graduate.link_token = self.generate_token()
            from models import db
            db.session.commit()
            
        return f"{current_app.config['BASE_URL']}{url_for('graduate_panel.form', token=graduate.link_token)}"
    
    def generate_school_link(self, application_id):
        """
        Генерация ссылки для школы
        
        Args:
            application_id (int): ID заявки
            
        Returns:
            str: Ссылка для школы
        """
        from models.application import Application
        
        application = Application.query.get(application_id)
        if not application:
            return None
            
        if not application.school_link_token:
            application.school_link_token = self.generate_token()
            from models import db
            db.session.commit()
            
        return f"{current_app.config['BASE_URL']}{url_for('school_panel.form', token=application.school_link_token)}"
    
    def generate_teacher_link(self, application_id):
        """
        Генерация ссылки для учителей
        
        Args:
            application_id (int): ID заявки
            
        Returns:
            str: Ссылка для учителей
        """
        from models.application import Application
        
        application = Application.query.get(application_id)
        if not application:
            return None
            
        if not application.teacher_link_token:
            application.teacher_link_token = self.generate_token()
            from models import db
            db.session.commit()
            
        return f"{current_app.config['BASE_URL']}{url_for('teacher_panel.form', token=application.teacher_link_token)}"
    
    def generate_qr_code(self, url, filename=None):
        """
        Генерация QR-кода для ссылки
        
        Args:
            url (str): URL для QR-кода
            filename (str, optional): Имя файла для сохранения QR-кода
            
        Returns:
            str: Путь к сгенерированному QR-коду
        """
        import qrcode
        import os
        
        if not filename:
            filename = f"qr_{self.generate_token(8)}"
            
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(url)
        qr.make(fit=True)
        
        img = qr.make_image(fill_color="black", back_color="white")
        file_path = os.path.join(current_app.config['QR_FOLDER'], f"{filename}.png")
        img.save(file_path)
        
        return file_path
    
    def generate_graduate_qr(self, graduate_id):
        """
        Генерация QR-кода для ссылки выпускника
        
        Args:
            graduate_id (int): ID выпускника
            
        Returns:
            str: Путь к сгенерированному QR-коду
        """
        link = self.generate_graduate_link(graduate_id)
        if not link:
            return None
            
        from models.graduate import Graduate
        graduate = Graduate.query.get(graduate_id)
        filename = f"graduate_{graduate_id}_{self.generate_token(4)}"
        
        return self.generate_qr_code(link, filename)
    
    def generate_school_qr(self, application_id):
        """
        Генерация QR-кода для ссылки школы
        
        Args:
            application_id (int): ID заявки
            
        Returns:
            str: Путь к сгенерированному QR-коду
        """
        link = self.generate_school_link(application_id)
        if not link:
            return None
            
        filename = f"school_{application_id}_{self.generate_token(4)}"
        
        return self.generate_qr_code(link, filename)
    
    def generate_teacher_qr(self, application_id):
        """
        Генерация QR-кода для ссылки учителей
        
        Args:
            application_id (int): ID заявки
            
        Returns:
            str: Путь к сгенерированному QR-коду
        """
        link = self.generate_teacher_link(application_id)
        if not link:
            return None
            
        filename = f"teacher_{application_id}_{self.generate_token(4)}"
        
        return self.generate_qr_code(link, filename)