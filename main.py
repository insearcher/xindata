"""
Главный модуль приложения для анализа данных о фрилансерах
"""

import os
import pandas as pd
from dotenv import load_dotenv
from src.data_analysis import load_data
from src.pandas_agent import PandasAgentService

# Загрузка переменных окружения из .env файла
load_dotenv()

def main():
    """
    Основная функция приложения
    """
    print("Система анализа данных о фрилансерах")
    print("====================================")

    # Проверка наличия API ключа OpenAI
    if not os.getenv("OPENAI_API_KEY"):
        print("Ошибка: Переменная окружения OPENAI_API_KEY не установлена.")
        print("Пожалуйста, создайте файл .env в корне проекта и добавьте в него строку:")
        print("OPENAI_API_KEY=ваш_ключ_api")
        print("Вы можете получить API ключ на сайте https://platform.openai.com/account/api-keys")
        return

    # Путь к файлу с данными
    data_path = os.path.join("data", "freelancer_earnings_bd.csv")

    # Проверка существования файла
    if not os.path.exists(data_path):
        # Если полный файл отсутствует, используем тестовый
        test_data_path = os.path.join("data", "freelancer_earnings_bd_100.csv")
        if os.path.exists(test_data_path):
            print(f"Файл {data_path} не найден, используем тестовый файл {test_data_path}")
            data_path = test_data_path
        else:
            print(f"Ошибка: Файл с данными не найден по пути {data_path}")
            print("Пожалуйста, скачайте датасет по ссылке: https://www.kaggle.com/datasets/shohinurpervezshohan/freelancer-earnings-and-job-trends")
            print("и поместите его в папку data/")
            return

    # Загрузка данных
    try:
        df = load_data(data_path)
    except Exception as e:
        print(f"Ошибка при загрузке данных: {e}")
        return

    # Инициализация Pandas Agent
    print("\nИнициализация Pandas Agent...")
    try:
        agent_service = PandasAgentService(df, model_name="gpt-4o-mini")
        print("Pandas Agent инициализирован успешно.")
    except Exception as e:
        print(f"Ошибка инициализации Pandas Agent: {e}")
        return

    print("\nСистема готова. Вы можете задавать вопросы о данных фрилансеров.")
    print("Введите 'exit' или 'quit' для завершения сеанса.")
    print()

    # Пример вопросов
    example_questions = [
        "Насколько выше доход у фрилансеров, принимающих оплату в криптовалюте, по сравнению с другими способами оплаты?",
        "Как распределяется доход фрилансеров в зависимости от региона проживания?",
        "Какой процент фрилансеров, считающих себя экспертами, выполнил менее 100 проектов?",
        "Какая категория работы имеет самый высокий средний доход?",
        "Существует ли корреляция между рейтингом клиента и доходом фрилансера?"
    ]
    print("Примеры вопросов:")
    for i, q in enumerate(example_questions, 1):
        print(f"{i}. {q}")
    print()

    # Основной цикл взаимодействия
    while True:
        # Получаем ввод пользователя
        user_query = input("> ")

        # Проверяем, хочет ли пользователь выйти
        if user_query.lower() in ['exit', 'quit', 'выход']:
            print("Спасибо за использование системы анализа данных о фрилансерах. До свидания!")
            break

        # Обрабатываем запрос
        print("\nАнализирую ваш вопрос...")
        try:
            result = agent_service.process_query(user_query)

            if result.get("error"):
                print(f"Ошибка: {result['error']}")
                continue

            print("\nОтвет:")
            print(result["answer"])
            print()
        except Exception as e:
            print(f"Ошибка обработки запроса: {e}")

        print()

if __name__ == "__main__":
    main()
