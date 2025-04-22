"""
Модуль для работы с Pandas DataFrame через LangChain Agent
"""

import os
from langchain.agents.agent_types import AgentType
from langchain_experimental.agents.agent_toolkits import create_pandas_dataframe_agent
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv

# Загрузка переменных окружения
load_dotenv()

class PandasAgentService:
    """Сервис для анализа данных с использованием LangChain Pandas Agent."""
    
    def __init__(self, df, model_name="gpt-4o-mini", temperature=0.0):
        """
        Инициализация сервиса Pandas Agent.
        
        Args:
            df (pd.DataFrame): DataFrame с данными
            model_name (str): Название модели для использования
            temperature (float): Параметр temperature для модели
        """
        self.api_key = os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("Переменная окружения OPENAI_API_KEY не установлена")
        
        self.df = df
        
        # Инициализация LLM
        self.llm = ChatOpenAI(
            temperature=temperature,
            openai_api_key=self.api_key,
            model=model_name
        )
        
        # Создание Pandas Agent
        self.agent = create_pandas_dataframe_agent(
            self.llm,
            self.df,
            verbose=True,
            agent_type=AgentType.OPENAI_FUNCTIONS
        )
    
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
        
        try:
            # Обрабатываем запрос с помощью агента
            response = self.agent.invoke(query)
            
            # Получаем ответ
            result["answer"] = response
            
            return result
        except Exception as e:
            result["error"] = f"Ошибка обработки запроса: {str(e)}"
            return result
