/**
 * Основной JavaScript файл для клиентской логики
 */

// Функция для инициализации всех компонентов
function initApp() {
    // Инициализация всплывающих подсказок
    initTooltips();
    
    // Инициализация форм
    initForms();
    
    // Инициализация динамических элементов
    initDynamicElements();
    
    console.log('Приложение инициализировано');
// Инициализация поиска школы для graduate/form.html
    
}

// Инициализация всплывающих подсказок Bootstrap
function initTooltips() {
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
}

// Инициализация форм
function initForms() {
    // Обработка форм с классом needs-validation
    const forms = document.querySelectorAll('.needs-validation');
    
    Array.from(forms).forEach(form => {
        form.addEventListener('submit', event => {
            if (!form.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();
            }
            
            form.classList.add('was-validated');
        }, false);
    });
    
    // Инициализация динамических форм
    initDynamicForms();
}

// Инициализация динамических форм
function initDynamicForms() {
    // Обработка динамических полей в формах
    const addFieldButtons = document.querySelectorAll('.add-field-button');
    
    Array.from(addFieldButtons).forEach(button => {
        button.addEventListener('click', event => {
            const targetId = button.getAttribute('data-target');
            const template = document.querySelector(`#${targetId}-template`);
            const container = document.querySelector(`#${targetId}-container`);
            
            if (template && container) {
                const clone = template.content.cloneNode(true);
                const index = container.children.length;
                
                // Обновляем индексы в клонированных элементах
                const inputs = clone.querySelectorAll('input, select, textarea');
                Array.from(inputs).forEach(input => {
                    const name = input.getAttribute('name');
                    if (name) {
                        input.setAttribute('name', name.replace('__index__', index));
                        input.setAttribute('id', name.replace('__index__', index));
                    }
                });
                
                // Добавляем кнопку удаления
                const removeButton = clone.querySelector('.remove-field-button');
                if (removeButton) {
                    removeButton.addEventListener('click', event => {
                        event.preventDefault();
                        const fieldGroup = event.target.closest('.field-group');
                        if (fieldGroup) {
                            fieldGroup.remove();
                        }
                    });
                }
                
                container.appendChild(clone);
            }
        });
    });
}

// Инициализация динамических элементов
function initDynamicElements() {
    // Обработка поиска школы
    const schoolSearchForm = document.querySelector('#school-search-form');
    if (schoolSearchForm) {
        schoolSearchForm.addEventListener('submit', async event => {
            event.preventDefault();
            
            const cityInput = schoolSearchForm.querySelector('[name="city"]');
            const schoolInput = schoolSearchForm.querySelector('[name="school_name"]');
            const resultsContainer = document.querySelector('#school-search-results');
            
            if (cityInput && schoolInput && resultsContainer) {
                try {
                    resultsContainer.innerHTML = '<div class="text-center"><div class="spinner-border" role="status"><span class="visually-hidden">Загрузка...</span></div></div>';
                    
                    const response = await fetch('/search', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                        },
                        body: JSON.stringify({
                            city: cityInput.value,
                            school: schoolInput.value
                        })
                    });
                    
                    const data = await response.json();
                    
                    if (data.error) {
                        resultsContainer.innerHTML = `<div class="alert alert-danger">${data.error}</div>`;
                    } else {
                        // Отображаем результаты поиска
                        displaySchoolSearchResults(data, resultsContainer);
                    }
                } catch (error) {
                    console.error('Ошибка при поиске школы:', error);
                    resultsContainer.innerHTML = '<div class="alert alert-danger">Произошла ошибка при поиске школы</div>';
                }
            }
        });
    }
}

// Отображение результатов поиска школы
function displaySchoolSearchResults(data, container) {
    const html = `
        <div class="card">
            <div class="card-header">Результаты поиска</div>
            <div class="card-body">
                <h5 class="card-title">${data.basic.name}</h5>
                <p class="card-text">Статус: ${data.basic.status}</p>
                <p class="card-text">Правопреемник: ${data.basic.successor || 'отсутствует'}</p>
                
                <h6 class="mt-3">Детальная информация:</h6>
                <ul class="list-group">
                    <li class="list-group-item">Полное название: ${data.detailed.full_name || '-'}</li>
                    <li class="list-group-item">Адрес: ${data.detailed.address || '-'}</li>
                    <li class="list-group-item">ИНН: ${data.detailed.inn || '-'}</li>
                    <li class="list-group-item">Директор: ${data.detailed.director || '-'}</li>
                    <li class="list-group-item">Почта: ${data.detailed.email || '-'}</li>
                </ul>
                
                <button type="button" class="btn btn-primary mt-3" id="select-school-button">Выбрать эту школу</button>
            </div>
        </div>
    `;
    
    container.innerHTML = html;
    
    // Обработка кнопки выбора школы
    const selectButton = container.querySelector('#select-school-button');
    if (selectButton) {
        selectButton.addEventListener('click', () => {
            // Заполняем скрытые поля формы данными о школе
            const schoolIdInput = document.querySelector('[name="school_id"]');
            const schoolNameInput = document.querySelector('[name="school_name_hidden"]');
            
            if (schoolIdInput && schoolNameInput) {
                schoolIdInput.value = data.basic.name;
                schoolNameInput.value = data.basic.name;
                
                // Отображаем форму с периодом обучения
                const periodForm = document.querySelector('#period-form');
                if (periodForm) {
                    periodForm.classList.remove('d-none');
                    periodForm.scrollIntoView({ behavior: 'smooth' });
                }
            }
        });
    }
}

// Запускаем инициализацию при загрузке страницы
document.addEventListener('DOMContentLoaded', initApp);