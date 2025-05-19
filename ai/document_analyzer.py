import os
import json
from PyPDF2 import PdfReader
from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from pydantic import BaseModel, Field
from typing import List, Dict, Any

class DocumentAnalysisResult(BaseModel):
    """Модель результата анализа документа"""
    schools: List[Dict[str, Any]] = Field(description="Список школ, найденных в документе")
    verification_score: float = Field(description="Вероятность соответствия (0-1)")

class DocumentAnalyzer:
    """Модуль для анализа документов"""
    
    def __init__(self):
        """Инициализация модуля"""
        self.llm = ChatOpenAI(
            model="gpt-4o", 
            base_url="https://api.aitunnel.ru/v1/",
            api_key="sk-aitunnel-6dnjLye1zgdGdnSfmM7kuFp3hiPi9qKI"
        )
        self.parser = JsonOutputParser(pydantic_object=DocumentAnalysisResult)
    
    def extract_text_from_pdf(self, pdf_path):
        """
        Извлечение текста из PDF документа
        
        Args:
            pdf_path (str): Путь к PDF документу
            
        Returns:
            str: Извлеченный текст
        """
        try:
            reader = PdfReader(pdf_path)
            text = ""
            for page in reader.pages:
                text += page.extract_text() + "\n"
            return text
        except Exception as e:
            print(f"Ошибка при извлечении текста из PDF: {str(e)}")
            return ""
    
    def analyze_document(self, document_path, teacher_data):
        """
        Анализ документа с помощью LLM
        
        Args:
            document_path (str): Путь к документу
            teacher_data (dict): Данные учителя
            
        Returns:
            float: Вероятность соответствия (0-1)
        """
        # Извлекаем текст из документа
        text = ""
        if document_path.lower().endswith('.pdf'):
            text = self.extract_text_from_pdf(document_path)
        else:
            # Для других типов документов можно добавить соответствующие обработчики
            with open(document_path, 'r', encoding='utf-8') as file:
                text = file.read()
        
        if not text:
            return 0.0
        
        # Формируем запрос к LLM
        prompt = PromptTemplate(
            template="""
            Проанализируй следующий документ и извлеки информацию о местах работы.
            
            Документ:
            {text}
            
            Учитель указал следующие места работы:
            {teacher_data}
            
            Извлеки из документа все места работы в формате JSON:
            - schools: список школ с полями name (название), start_year (год начала), end_year (год окончания), subjects (предметы)
            - verification_score: вероятность соответствия указанных учителем мест работы с найденными в документе (от 0 до 1)
            
            {format_instructions}
            """,
            input_variables=["text", "teacher_data"],
            partial_variables={"format_instructions": self.parser.get_format_instructions()}
        )
        
        # Вызываем LLM
        chain = prompt | self.llm | self.parser
        
        try:
            response = chain.invoke({
                "text": text[:10000],  # Ограничиваем размер текста
                "teacher_data": json.dumps(teacher_data, ensure_ascii=False)
            })
            
            if isinstance(response, dict):
                return response.get("verification_score", 0.0)
            
            return response.verification_score
            
        except Exception as e:
            print(f"Ошибка при анализе документа: {str(e)}")
            return 0.0
    
    def calculate_verification_score(self, analysis_result, teacher_data):
        """
        Расчет вероятности соответствия
        
        Args:
            analysis_result (dict): Результат анализа
            teacher_data (dict): Данные учителя
            
        Returns:
            float: Вероятность соответствия (0-1)
        """
        # Этот метод можно использовать для более сложной логики расчета вероятности
        # В текущей реализации вероятность возвращается напрямую из LLM
        return analysis_result.get("verification_score", 0.0)