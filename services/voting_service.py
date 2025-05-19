from sqlalchemy import func
from models import db
from models.graduate import Vote
from models.teacher import Teacher

class VotingService:
    """Сервис для голосования"""
    
    def vote_for_teacher(self, graduate_id, teacher_id):
        """
        Голосование выпускника за учителя
        
        Args:
            graduate_id (int): ID выпускника
            teacher_id (int): ID учителя
            
        Returns:
            bool: Результат операции
        """
        # Проверяем, голосовал ли уже выпускник за этого учителя
        existing_vote = Vote.query.filter_by(
            graduate_id=graduate_id,
            teacher_id=teacher_id
        ).first()
        
        if existing_vote:
            return False
            
        # Создаем новый голос
        vote = Vote(graduate_id=graduate_id, teacher_id=teacher_id)
        db.session.add(vote)
        db.session.commit()
        
        return True
    
    def vote_for_teachers(self, graduate_id, teacher_ids):
        """
        Голосование выпускника за нескольких учителей
        
        Args:
            graduate_id (int): ID выпускника
            teacher_ids (list): Список ID учителей
            
        Returns:
            int: Количество успешных голосов
        """
        success_count = 0
        
        for teacher_id in teacher_ids:
            if self.vote_for_teacher(graduate_id, teacher_id):
                success_count += 1
                
        return success_count
    
    def get_teacher_votes_count(self, teacher_id):
        """
        Получение количества голосов за учителя
        
        Args:
            teacher_id (int): ID учителя
            
        Returns:
            int: Количество голосов
        """
        return Vote.query.filter_by(teacher_id=teacher_id).count()
    
    def get_top_teachers(self, limit=10):
        """
        Получение топ учителей по количеству голосов
        
        Args:
            limit (int): Количество учителей в топе
            
        Returns:
            list: Список учителей с количеством голосов
        """
        result = db.session.query(
            Teacher,
            func.count(Vote.id).label('votes_count')
        ).join(
            Vote, Teacher.id == Vote.teacher_id
        ).group_by(
            Teacher.id
        ).order_by(
            func.count(Vote.id).desc()
        ).limit(limit).all()
        
        return result
    
    def get_graduate_votes(self, graduate_id):
        """
        Получение списка учителей, за которых проголосовал выпускник
        
        Args:
            graduate_id (int): ID выпускника
            
        Returns:
            list: Список учителей
        """
        votes = Vote.query.filter_by(graduate_id=graduate_id).all()
        teachers = [vote.teacher for vote in votes]
        
        return teachers