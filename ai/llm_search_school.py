import os
import json
from typing import List, Optional
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

# Новая модель данных для полной информации о школе
class School(BaseModel):
    name: str = Field(default="", description="Краткое название школы")
    full_name: str = Field(default="", description="Полное название школы")
    address: str = Field(default="", description="Полный адрес школы")
    inn: str = Field(default="", description="ИНН школы")
    director: str = Field(default="", description="ФИО директора")
    email: str = Field(default="", description="Официальная почта школы")
    phone: str = Field(default="", description="Официальный номер телефона школы")
    status: str = Field(default="", description="Статус школы (строго 'ликвидирована' или 'действующая')")
    city: str = Field(default="", description="Город школы")
    successor_name: Optional[str] = Field(default=None, description="Краткое название правоприемника (если ликвидирована)")
    successor_inn: Optional[str] = Field(default=None, description="ИНН правопреемника (если ликвидирована)")
    successor_address: Optional[str] = Field(default=None, description="Адрес правопреемника (если ликвидирована)")
    is_selected_by_graduate: bool = Field(default=False, description="Является школой из запроса. Выбрана выпускником. Главное чтобы совпадал номер.")

llm = ChatOpenAI(
    model="gpt-4o", 
    base_url="https://api.aitunnel.ru/v1/",
    api_key="sk-aitunnel-6dnjLye1zgdGdnSfmM7kuFp3hiPi9qKI"
)

search = TavilySearchResults()
console = Console()

school_parser = JsonOutputParser(pydantic_object=School)

def get_user_input() -> tuple[str, str, Optional[str]]:
    """Получение входных данных от пользователя"""
    city = input("Введите город: ").strip()
    school_name = input("Введите название школы: ").strip()
    inn = input("Введите ИНН (опционально): ").strip()
    return city, school_name, inn if inn else None

def search_school_info(city: str, school_name: str, inn: Optional[str] = None) -> list:
    """Поиск информации о школе через Tavily API"""
    query = f"{school_name} {city}"
    if inn:
        query += f" {inn}"
    query += " правопреемник, адрес"
    search_results = search.invoke(query)
    return search_results

def extract_school_info_from_llm(
    search_results: list,
    school_name: str,
    requested_school: dict = None,
    school_name_first: str = None,
    city: str = ""
) -> School:
    """
    Извлечение полной информации о школе через LLM.
    В prompt явно передаётся школа из запроса с пометкой "Школа из запроса".
    school_name — для совместимости с вызовом, может быть использован в будущем.
    """
    # Логирование для отладки
    print(f"[DEBUG] extract_school_info_from_llm args: search_results={type(search_results)}, school_name={school_name}, requested_school={requested_school}, school_name_first={school_name_first}")

    prompt = PromptTemplate(
        template="""
Школа из запроса(выбрана выпускником):
{school_name_first}

Искомая школа, по которой нужна информация:
{requested_school}


Проанализируй следующие результаты поиска и извлеки информацию о школе.
Заполни все поля строго по формату. Если информация отсутствует, оставь поле пустым.
Статус должен быть строго 'ликвидирована' или 'действующая'.
Если школа ликвидирована, обязательно попытайся извлечь сведения о правопреемнике (название, ИНН, адрес).

Результаты поиска:
{search_results}

{format_instructions}
""",
        input_variables=["search_results", "requested_school", "school_name_first"],
        partial_variables={"format_instructions": school_parser.get_format_instructions()}
    )
    chain = prompt | llm | school_parser
    try:
        response = chain.invoke({
            "search_results": json.dumps(search_results, ensure_ascii=False, indent=2),
            "requested_school": json.dumps(requested_school, ensure_ascii=False, indent=2) if requested_school else "",
            "school_name_first": school_name_first if school_name_first is not None else ""
        })
        if isinstance(response, dict):
            return School(**response)
        return response
    except Exception as e:
        console.print(f"[red]Ошибка при обработке информации о школе: {str(e)}[/red]")
        return School()

def extract_school_chain(city: str, school_name: str, school_name_first:str, inn: Optional[str] = None, seen_inns=None) -> List[School]:
    """
    Рекурсивно извлекает цепочку школ (от ликвидированной до действующей).
    seen_inns — защита от зацикливания по ИНН.
    """
    if seen_inns is None:
        seen_inns = set()
    print(f"[DEBUG] extract_school_chain: city={city}, school_name={school_name}, school_name_first={school_name_first}, inn={inn}, seen_inns={seen_inns}")
    search_results = search_school_info(city, school_name, inn)
    print(f"[DEBUG] search_school_info results for {school_name} (ИНН={inn}): {search_results}")
    requested_school = {
        "city": city,
        "school_name": school_name,
        "inn": inn or ""
    }
    school = extract_school_info_from_llm(search_results, school_name, requested_school, school_name_first)
    print(f"[DEBUG] school object: {school}")
    chain = [school]
    # Защита от зацикливания
    if school.inn and school.inn in seen_inns:
        print(f"[DEBUG] Зацикливание по ИНН: {school.inn}")
        return chain
    if school.inn:
        seen_inns.add(school.inn)
    # Если школа ликвидирована и есть сведения о правопреемнике — рекурсивно ищем дальше
    if (
        school.status.strip().lower() == "ликвидирована"
        and (school.successor_name or school.successor_inn)
    ):
        next_name = school.successor_name or ""
        next_inn = school.successor_inn or None
        print(f"[DEBUG] Рекурсия: status={school.status}, next_name={next_name}, next_inn={next_inn}, seen_inns={seen_inns}")
        # Для рекурсии используем тот же город, successor_name и successor_inn
        chain += extract_school_chain(city, next_name, school_name_first, next_inn, seen_inns)
    return chain

def display_school_chain(chain: List[School]):
    """Отображение цепочки школ в виде таблицы"""
    for idx, school in enumerate(chain, 1):
        table = Table(title=f"Школа {idx}")
        table.add_column("Параметр", style="cyan")
        table.add_column("Значение", style="green")
        table.add_row("Краткое название", school.name)
        table.add_row("Полное название", school.full_name)
        table.add_row("Адрес", school.address)
        table.add_row("ИНН", school.inn)
        table.add_row("Директор", school.director)
        table.add_row("Почта", school.email)
        table.add_row("Телефон", school.phone)
        table.add_row("Статус", school.status)
        table.add_row("Город", school.city)
        table.add_row("Правопреемник (название)", school.successor_name or "")
        table.add_row("Правопреемник (ИНН)", school.successor_inn or "")
        table.add_row("Правопреемник (адрес)", school.successor_address or "")
        table.add_row("Выбрана выпускником", str(school.is_selected_by_graduate))
        console.print(table)
        console.print("\n")

def main():
    """Основная функция программы"""
    try:
        city, school_name, inn = get_user_input()
        chain = extract_school_chain(city, school_name, school_name, inn)
        display_school_chain(chain)
    except Exception as e:
        console.print(f"[red]Произошла ошибка: {str(e)}[/red]")

if __name__ == "__main__":
    main()

