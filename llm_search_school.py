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

# Модель данных для школы
class SchoolInfo(BaseModel):
    full_name: str = Field(default="не найдено", description="Полное название школы")
    address: str = Field(default="не найдено", description="Полный адрес школы")
    status: str = Field(default="не найдено", description="Статус школы (реорганизована/действующая)")
    inn: str = Field(default="не найдено", description="ИНН школы")
    director: str = Field(default="не найдено", description="ФИО директора")

# Инициализация LLM и поискового API
llm = ChatOpenAI(
    model="gpt-4o", 
    base_url="https://api.aitunnel.ru/v1/",
    api_key="sk-aitunnel-6dnjLye1zgdGdnSfmM7kuFp3hiPi9qKI"
)

search = TavilySearchResults()
console = Console()

# Инициализация парсера JSON
parser = JsonOutputParser(pydantic_object=SchoolInfo)

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

def process_search_results(results: list[Dict]) -> SchoolInfo:
    """Обработка результатов поиска с помощью LLM"""
    # Формируем промпт для LLM
    prompt = PromptTemplate(
        template="""Проанализируй следующие результаты поиска и извлеки информацию о школе.
        Если информация не найдена, используй значение "не найдено".
        
        Результаты поиска:
        {search_results}
        
        {format_instructions}
        """,
        input_variables=["search_results"],
        partial_variables={"format_instructions": parser.get_format_instructions()}
    )
    
    # Создаем цепочку обработки
    chain = prompt | llm | parser
    
    try:
        # Получаем и парсим результат
        response = chain.invoke({"search_results": json.dumps(results, ensure_ascii=False, indent=2)})
        if isinstance(response, dict):
            return SchoolInfo(**response)
        return response
    except Exception as e:
        console.print(f"[red]Ошибка при обработке ответа LLM: {str(e)}[/red]")
        return SchoolInfo()

def display_results(school_info: SchoolInfo):
    """Отображение результатов в виде таблицы"""
    table = Table(title="Информация о школе")
    
    table.add_column("Параметр", style="cyan")
    table.add_column("Значение", style="green")
    
    table.add_row("Название", school_info.full_name)
    table.add_row("Адрес", school_info.address)
    table.add_row("Статус", school_info.status)
    table.add_row("ИНН", school_info.inn)
    table.add_row("Директор", school_info.director)
    
    console.print(table)

def main():
    """Основная функция программы"""
    try:
        # Получаем входные данные
        city, school_name = get_user_input()
        
        # Ищем информацию
        console.print("[yellow]Поиск информации о школе...[/yellow]")
        search_results = search_school_info(city, school_name)
        
        # Обрабатываем результаты
        console.print("[yellow]Обработка результатов...[/yellow]")
        school_info = process_search_results(search_results)
        
        # Отображаем результаты
        display_results(school_info)
        
    except Exception as e:
        console.print(f"[red]Произошла ошибка: {str(e)}[/red]")

if __name__ == "__main__":
    main()




