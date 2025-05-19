import qrcode
import os
from flask import current_app

class QRService:
    """Сервис для генерации QR-кодов"""
    
    def generate_qr_code(self, data, filename=None):
        """
        Генерация QR-кода
        
        Args:
            data (str): Данные для QR-кода (обычно URL)
            filename (str, optional): Имя файла для сохранения QR-кода
            
        Returns:
            str: Путь к сгенерированному QR-коду
        """
        if not filename:
            # Генерируем уникальное имя файла
            import secrets
            import string
            alphabet = string.ascii_letters + string.digits
            random_suffix = ''.join(secrets.choice(alphabet) for _ in range(8))
            filename = f"qr_{random_suffix}"
            
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(data)
        qr.make(fit=True)
        
        img = qr.make_image(fill_color="black", back_color="white")
        file_path = os.path.join(current_app.config['QR_FOLDER'], f"{filename}.png")
        img.save(file_path)
        
        return file_path
    
    def generate_graduate_qr(self, graduate_id):
        """
        Генерация QR-кода для выпускника
        
        Args:
            graduate_id (int): ID выпускника
            
        Returns:
            str: Путь к сгенерированному QR-коду
        """
        from services.link_service import LinkService
        
        link_service = LinkService()
        url = link_service.generate_graduate_link(graduate_id)
        
        if not url:
            return None
            
        return self.generate_qr_code(url, f"graduate_{graduate_id}")
    
    def generate_school_qr(self, application_id):
        """
        Генерация QR-кода для школы
        
        Args:
            application_id (int): ID заявки
            
        Returns:
            str: Путь к сгенерированному QR-коду
        """
        from services.link_service import LinkService
        
        link_service = LinkService()
        url = link_service.generate_school_link(application_id)
        
        if not url:
            return None
            
        return self.generate_qr_code(url, f"school_{application_id}")
    
    def generate_teacher_qr(self, application_id):
        """
        Генерация QR-кода для учителей
        
        Args:
            application_id (int): ID заявки
            
        Returns:
            str: Путь к сгенерированному QR-коду
        """
        from services.link_service import LinkService
        
        link_service = LinkService()
        url = link_service.generate_teacher_link(application_id)
        
        if not url:
            return None
            
        return self.generate_qr_code(url, f"teacher_{application_id}")