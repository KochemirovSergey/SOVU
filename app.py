from flask import Flask, render_template, request
import pandas as pd

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():
    # Читаем CSV файл
    df = pd.read_csv('cities.csv')
    # Создаем список городов с регионами
    cities_with_regions = df.apply(lambda row: f"{row['Город']} ({row['Регион']})", axis=1).tolist()
    
    if request.method == 'POST':
        selected_city = request.form.get('city')
        school_name = request.form.get('school')
        return render_template('index.html', 
                             cities=cities_with_regions,
                             selected_city=selected_city,
                             school_name=school_name)
    
    return render_template('index.html', cities=cities_with_regions)

if __name__ == '__main__':
    app.run(debug=True) 