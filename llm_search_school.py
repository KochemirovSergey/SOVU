import os
import json
from typing import Dict, Optional
from langchain_openai import ChatOpenAI
from langchain_community.tools.tavily_search import TavilySearchResults
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.prompts import PromptTemplate
from pydantic import BaseModel, Field
from rich.console import Console
from rich.table import Table

# Настройка переменных окружения для LangChain
os.environ["LANGCHAIN_TRACING_V2"] = "true"
os.environ["LANGCHAIN_ENDPOINT"] = "https://api.smith.langchain.com"
os.environ["LANGCHAIN_API_KEY"] = "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"
os.environ["LANGCHAIN_PROJECT"] = "pr-untimely-licorice-46"
os.environ["TAVILY_API_KEY"] = "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"

# Модель данных для базовой информации о школе
class SchoolBasicInfo(BaseModel):
    name: str = Field(default="", description="Название школы")
    status: str = Field(default="", description="Статус школы (строго 'ликвидирована' или 'действующая')")
    successor: str = Field(default="", description="Правопреемник (название организации или 'отсутствует')")

# Модель данных для детальной информации о школе
class SchoolDetailedInfo(BaseModel):
    full_name: str = Field(default="", description="Полное название школы")
    address: str = Field(default="", description="Полный адрес школы")
    inn: str = Field(default="", description="ИНН школы")
    director: str = Field(default="", description="ФИО директора")
    email: str = Field(default="", description="Официальная почта школы")

# Инициализация LLM и поискового API
llm = ChatOpenAI(
    model="gpt-4o", 
    base_url="https://api.aitunnel.ru/v1/",
    api_key="sk-aitunnel-6dnjLye1zgdGdnSfmM7kuFp3hiPi9qKI"
)

search = TavilySearchResults()
console = Console()

# Инициализация парсеров JSON
basic_parser = JsonOutputParser(pydantic_object=SchoolBasicInfo)
detailed_parser = JsonOutputParser(pydantic_object=SchoolDetailedInfo)

def get_user_input() -> tuple[str, str]:
    """Получение входных данных от пользователя"""
    city = input("Введите город: ").strip()
    school_name = input("Введите название школы: ").strip()
    return city, school_name

def search_school_info(city: str, school_name: str) -> list[Dict]:
    """Поиск информации о школе через Tavily API"""
    query = f"школа {school_name} {city} правопреемник инн"
    search_results = search.invoke(query)
    return search_results

def process_basic_info(results: list[Dict]) -> SchoolBasicInfo:
    """Обработка результатов поиска для получения базовой информации"""
    prompt = PromptTemplate(
        template="""Проанализируй следующие результаты поиска и извлеки базовую информацию о школе.
        Статус должен быть строго 'ликвидирована' или 'действующая'.
        Если школа ликвидирована, укажи правопреемника. Если действующая - укажи 'отсутствует'.
        
        Результаты поиска:
        {search_results}
        
        {format_instructions}
        """,
        input_variables=["search_results"],
        partial_variables={"format_instructions": basic_parser.get_format_instructions()}
    )
    
    chain = prompt | llm | basic_parser
    
    try:
        response = chain.invoke({"search_results": json.dumps(results, ensure_ascii=False, indent=2)})
        if isinstance(response, dict):
            return SchoolBasicInfo(**response)
        return response
    except Exception as e:
        console.print(f"[red]Ошибка при обработке базовой информации: {str(e)}[/red]")
        return SchoolBasicInfo()

def process_detailed_info(results: list[Dict]) -> SchoolDetailedInfo:
    """Обработка результатов поиска для получения детальной информации"""
    prompt = PromptTemplate(
        template="""Проанализируй следующие результаты поиска и извлеки детальную информацию о школе.
        Если какая-то информация не найдена, оставь поле пустым.
        
        Результаты поиска:
        {search_results}
        
        {format_instructions}
        """,
        input_variables=["search_results"],
        partial_variables={"format_instructions": detailed_parser.get_format_instructions()}
    )
    
    chain = prompt | llm | detailed_parser
    
    try:
        response = chain.invoke({"search_results": json.dumps(results, ensure_ascii=False, indent=2)})
        if isinstance(response, dict):
            return SchoolDetailedInfo(**response)
        return response
    except Exception as e:
        console.print(f"[red]Ошибка при обработке детальной информации: {str(e)}[/red]")
        return SchoolDetailedInfo()

def display_results(basic_info: SchoolBasicInfo, detailed_info: SchoolDetailedInfo):
    """Отображение результатов в виде двух таблиц"""
    # Таблица с базовой информацией
    basic_table = Table(title="Базовая информация о школе")
    basic_table.add_column("Параметр", style="cyan")
    basic_table.add_column("Значение", style="green")
    
    basic_table.add_row("Название", basic_info.name)
    basic_table.add_row("Статус", basic_info.status)
    basic_table.add_row("Правопреемник", basic_info.successor)
    
    console.print(basic_table)
    console.print("\n")
    
    # Таблица с детальной информацией
    detailed_table = Table(title="Детальная информация")
    detailed_table.add_column("Параметр", style="cyan")
    detailed_table.add_column("Значение", style="green")
    
    detailed_table.add_row("Полное название", detailed_info.full_name)
    detailed_table.add_row("Адрес", detailed_info.address)
    detailed_table.add_row("ИНН", detailed_info.inn)
    detailed_table.add_row("Директор", detailed_info.director)
    detailed_table.add_row("Почта", detailed_info.email)
    
    console.print(detailed_table)

def get_school_info(city: str, school_name: str) -> tuple[SchoolBasicInfo, SchoolDetailedInfo]:
    """
    Получение информации о школе по городу и названию.
    
    Args:
        city (str): Название города
        school_name (str): Название школы
        
    Returns:
        tuple[SchoolBasicInfo, SchoolDetailedInfo]: Кортеж с базовой и детальной информацией о школе
    """
    try:
        # Ищем базовую информацию
        search_results = search_school_info(city, school_name)
        basic_info = process_basic_info(search_results)
        
        # В зависимости от статуса школы
        if basic_info.status == "действующая":
            # Для действующей школы используем те же результаты поиска
            detailed_info = process_detailed_info(search_results)
        else:
            # Для ликвидированной школы ищем информацию о правопреемнике
            successor_results = search_school_info(city, basic_info.successor)
            detailed_info = process_detailed_info(successor_results)
            
        return basic_info, detailed_info
        
    except Exception as e:
        console.print(f"[red]Произошла ошибка: {str(e)}[/red]")
        return SchoolBasicInfo(), SchoolDetailedInfo()

def main():
    """Основная функция программы"""
    try:
        # Получаем входные данные
        city, school_name = get_user_input()
        
        # Получаем информацию о школе
        basic_info, detailed_info = get_school_info(city, school_name)
        
        # Отображаем результаты
        display_results(basic_info, detailed_info)
        
    except Exception as e:
        console.print(f"[red]Произошла ошибка: {str(e)}[/red]")

if __name__ == "__main__":
    main()




