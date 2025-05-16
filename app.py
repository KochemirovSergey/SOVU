from flask import Flask, render_template, request, jsonify
import pandas as pd
from llm_search_school import get_school_info
import traceback

app = Flask(__name__)

@app.route('/', methods=['GET'])
def index():
    # Читаем CSV файл
    df = pd.read_csv('cities.csv')
    # Создаем список городов с регионами
    cities_with_regions = df.apply(lambda row: f"{row['Город']} ({row['Регион']})", axis=1).tolist()
    return render_template('index.html', cities=cities_with_regions)

@app.route('/search', methods=['POST'])
def search():
    try:
        print("Получен POST запрос на /search")
        print("Content-Type:", request.headers.get('Content-Type'))
        print("Тело запроса:", request.get_data(as_text=True))
        
        if not request.is_json:
            print("Ошибка: Получены не JSON данные")
            return jsonify({'error': 'Неверный формат данных. Ожидается JSON.'}), 400
            
        data = request.get_json()
        print("Распарсенные JSON данные:", data)
        
        if not isinstance(data, dict):
            print("Ошибка: Данные не являются словарем")
            return jsonify({'error': 'Неверный формат данных'}), 400
            
        city = data.get('city')
        school_name = data.get('school')
        
        print(f"Извлеченные данные: город='{city}', школа='{school_name}'")
        
        if not city or not school_name:
            print("Отсутствуют обязательные параметры")
            return jsonify({'error': 'Пожалуйста, выберите город и введите название школы'})
        
        # Извлекаем название города из строки формата "Город (Регион)"
        city = city.split(' (')[0]
        print(f"Извлеченное название города: '{city}'")
        
        # Получаем информацию о школе
        print("Вызов get_school_info...")
        basic_info, detailed_info = get_school_info(city, school_name)
        print("get_school_info выполнен успешно")
        
        # Преобразуем объекты в словари
        result = {
            'basic': {
                'name': basic_info.name,
                'status': basic_info.status,
                'successor': basic_info.successor
            },
            'detailed': {
                'full_name': detailed_info.full_name,
                'address': detailed_info.address,
                'inn': detailed_info.inn,
                'director': detailed_info.director,
                'email': detailed_info.email
            }
        }
        
        print("Отправка результата:", result)
        return jsonify(result)
        
    except Exception as e:
        print("Произошла ошибка:", str(e))
        print("Traceback:", traceback.format_exc())
        return jsonify({'error': f'Произошла ошибка при поиске информации: {str(e)}'}), 500

if __name__ == '__main__':
    app.run(debug=True) 