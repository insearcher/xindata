"""
Модуль для взаимодействия с языковыми моделями
"""

import os
from typing import Optional
from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate
from dotenv import load_dotenv

# Загрузка переменных окружения для API ключей
load_dotenv()

class LLMService:
    """Сервис для взаимодействия с языковыми моделями."""

    def __init__(self, model_name="gpt-3.5-turbo"):
        """
        Инициализация LLM сервиса.

        Args:
            model_name (str): Название модели для использования
        """
        self.api_key = os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("Переменная окружения OPENAI_API_KEY не установлена")

         self.llm = ChatOpenAI(
            temperature=0,  # Для детерминированных ответов
            openai_api_key=self.api_key,
            model=model_name
        )

        # Настройка шаблонов запросов
        self.code_prompt_template = """Ты - ассистент по анализу данных, который помогает анализировать DataFrame в pandas.

DataFrame df содержит следующие колонки:
{schema}

Твоя задача - преобразовать вопрос пользователя в Python код, использующий DataFrame df для получения ответа.
Возвращай ТОЛЬКО исполняемый Python-код. Без объяснений, маркировки и всего, что не является корректным Python-кодом.
Твой ответ должен быть ТОЛЬКО Python-кодом для выполнения.

ПРИМЕРЫ ВОПРОСОВ И КОДА:
Вопрос: Насколько выше доход у фрилансеров, принимающих оплату в криптовалюте, по сравнению с другими способами оплаты?
Код:
crypto_earnings = df[df['Payment_Method'] == 'Crypto']['Earnings_USD'].mean()
other_earnings = df[df['Payment_Method'] != 'Crypto']['Earnings_USD'].mean()
difference = crypto_earnings - other_earnings
percentage = (difference / other_earnings) * 100
print(f"Средний доход фрилансеров, принимающих оплату в криптовалюте: ${crypto_earnings:.2f}")
print(f"Средний доход фрилансеров, использующих другие способы оплаты: ${other_earnings:.2f}")
print(f"Разница: ${difference:.2f} ({percentage:.2f}%)")

Вопрос: Как распределяется доход фрилансеров в зависимости от региона проживания?
Код:
region_earnings = df.groupby('Client_Region')['Earnings_USD'].agg(['mean', 'median', 'count']).reset_index()
region_earnings = region_earnings.sort_values(by='mean', ascending=False)
for _, row in region_earnings.iterrows():
    print(f"{{row['Client_Region']}}: ${row['mean']:.2f} (медиана: ${row['median']:.2f}, кол-во: {{row['count']}})")

Вопрос: Какой процент фрилансеров, считающих себя экспертами, выполнил менее 100 проектов?
Код:
experts = df[df['Experience_Level'] == 'Expert']
experts_less_than_100 = experts[experts['Job_Completed'] < 100]
percentage = (len(experts_less_than_100) / len(experts)) * 100
print(f"Всего экспертов: {len(experts)}")
print(f"Экспертов с менее чем 100 проектами: {len(experts_less_than_100)}")
print(f"Процент: {percentage:.2f}%")

Вопрос пользователя: {question}

Python код:"""

        self.answer_prompt_template = """Ты - полезный ассистент по анализу данных.

Пользователь спросил: "{question}"

Анализ данных дал следующий результат:
```
{result}
```

На основе этого результата предоставь четкий, лаконичный и информативный ответ на вопрос пользователя.
Форматируй денежные значения с символом $ и округляй до 2 десятичных знаков, где это уместно.
Включи ключевые метрики и выводы из данных.

Твой ответ:"""

    def generate_code(self, question: str, schema: str) -> str:
        """
        Генерирует Python-код для ответа на вопрос пользователя.

        Args:
            question (str): Вопрос пользователя
            schema (str): Информация о схеме данных

        Returns:
            str: Сгенерированный Python-код
        """
        prompt = self.code_prompt_template.format(
            schema=schema,
            question=question
        )

        response = self.llm.invoke(prompt)
        return response.content.strip()

    def generate_answer(self, question: str, result: str) -> str:
        """
        Генерирует ответ на естественном языке на основе результата выполнения кода.

        Args:
            question (str): Исходный вопрос пользователя
            result (str): Результат выполнения кода

        Returns:
            str: Ответ на естественном языке
        """
        prompt = self.answer_prompt_template.format(
            question=question,
            result=result
        )

        response = self.llm.invoke(prompt)
        return response.content.strip()
