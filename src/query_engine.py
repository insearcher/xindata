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
                "code": сгенерированный код,
                "result": результат выполнения,
                "answer": ответ на естественном языке,
                "error": сообщение об ошибке, если есть
            }
        """
        result = {
            "query": query,
            "code": None,
            "result": None,
            "answer": None,
            "error": None
        }
        
        try:
            # Генерируем код из запроса
            code = self.llm_service.generate_code(query, self.schema)
            result["code"] = code
            
            # Выполняем код
            output, error = self.execute_code_safely(code)
            if error:
                result["error"] = error
                return result
            
            result["result"] = output
            
            # Генерируем ответ на естественном языке
            answer = self.llm_service.generate_answer(query, output)
            result["answer"] = answer
            
            return result
        except Exception as e:
            result["error"] = f"Ошибка обработки запроса: {str(e)}"
            return result
