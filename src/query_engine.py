"""
Модуль для обработки естественно-языковых запросов к данным
"""

import io
import sys
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from contextlib import redirect_stdout, redirect_stderr
from .llm_service import LLMService
from .data_analysis import get_schema_for_prompt

class QueryEngine:
    """
    Движок для обработки естественно-языковых запросов к данным.
    """

    def __init__(self, df, model_name="gpt-3.5-turbo"):
        """
        Инициализация движка запросов.

        Args:
            df (pd.DataFrame): DataFrame с данными
            model_name (str): Название LLM модели для использования
        """
        self.df = df
        self.llm_service = LLMService(model_name)
        self.schema = get_schema_for_prompt(df)

    def execute_code_safely(self, code):
        """
        Безопасное выполнение сгенерированного Python-кода.

        Args:
            code (str): Python-код для выполнения

        Returns:
            tuple: (результат, сообщение об ошибке)
        """
        # Создаем буфер для перехвата stdout
        buffer = io.StringIO()
        error_buffer = io.StringIO()

        # Создаем локальное пространство имен с датафреймом
        local_vars = {"df": self.df, "pd": pd, "np": np, "plt": plt, "sns": sns}

        try:
            # Перенаправляем stdout и выполняем код
            with redirect_stdout(buffer), redirect_stderr(error_buffer):
                exec(code, local_vars)

            # Получаем вывод
            output = buffer.getvalue()
            return output, None
        except Exception as e:
            return None, f"Ошибка выполнения кода: {str(e)}\n{error_buffer.getvalue()}"

    def process_query(self, query):
        """
        Обработка естественно-языкового запроса о данных.

        Args:
            query (str): Вопрос пользователя

        Returns:
            dict: {
                "query": исходный запрос,
                "answer": ответ на запрос,
                "error": сообщение об ошибке, если есть
            }
        """
        result = {
            "query": query,
            "answer": None,
            "error": None
        }

        # Проверка на некорректные запросы или запросы не о данных
        if any(keyword in query.lower() for keyword in ['удалить', 'удали', 'изменить', 'модифицировать']):
            result["error"] = "Запрос содержит операции модификации данных, которые не поддерживаются системой."
            return result

        try:
            # Сначала пробуем обычный запрос
            if not self.verbose:
                stdout_buffer = io.StringIO()
                stderr_buffer = io.StringIO()

                with redirect_stdout(stdout_buffer), redirect_stderr(stderr_buffer):
                    # Обрабатываем запрос с помощью агента
                    response = self.agent.invoke(query)
            else:
                # Если режим подробного логгирования включен, выводим все в консоль
                response = self.agent.invoke(query)

            # Получаем ответ
            result["answer"] = response["output"]

            # Проверяем наличие индикаторов отсутствия данных в ответе
            if "отсутствует информация" in result["answer"].lower() or "нет данных" in result["answer"].lower():
                # Это нормальный случай, когда информации нет в данных
                pass

            return result
        except Exception as e:
            error_message = str(e)

            # Более дружественные сообщения об ошибках
            if "The agent had errors" in error_message:
                result["error"] = "Не удалось проанализировать данные для этого запроса. Попробуйте сформулировать вопрос иначе."
            elif "The agent exceeded" in error_message:
                result["error"] = "Запрос слишком сложный и превысил лимит попыток анализа. Попробуйте разбить его на более простые вопросы."
            else:
                result["error"] = f"Ошибка обработки запроса: {error_message}"

            return result
