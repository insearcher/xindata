import io
import os
from contextlib import redirect_stdout, redirect_stderr

from dotenv import load_dotenv
from langchain.agents.agent_types import AgentType
from langchain_experimental.agents.agent_toolkits import create_pandas_dataframe_agent
from langchain_openai import ChatOpenAI

load_dotenv()


class PandasAgentService:
    def __init__(self, df, model_name="gpt-4o-mini", temperature=0.0, verbose=False):
        self.api_key = os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("Переменная окружения OPENAI_API_KEY не установлена")

        self.df = df
        self.verbose = verbose

        self.llm = ChatOpenAI(
            temperature=temperature,
            openai_api_key=self.api_key,
            model=model_name
        )

        agent_prefix = """
        Ты - аналитик данных, работающий с DataFrame, содержащим информацию о фрилансерах.
        Твоя задача - отвечать на вопросы о данных, основываясь на анализе DataFrame.

        ВАЖНЫЕ ПРАВИЛА:
        1. НЕ используй функции визуализации (plt.plot, plt.bar, plt.show и т.д.)
        2. Предоставляй ответы только в текстовом формате
        3. Если нужно показать распределение или агрегацию, используй текстовое форматирование (например, таблицы с помощью .to_string())
        4. Для денежных значений используй форматирование с символом $ и округлением до 2 знаков
        5. Давай краткие, но информативные ответы
        6. Для ответа на вопрос о распределении данных по категориям, используй группировку и агрегацию без визуализации
        7. Если вопрос не относится к данным или запрашивает информацию, которой нет в данных, четко укажи это
        8. При сложных запросах с множеством условий, перечисли все примененные фильтры в ответе
        9. Если запрос синтаксически некорректен, попытайся понять его суть, но укажи, как ты его интерпретировал
        10. Не модифицируй данные (не удаляй, не изменяй), а работай только с копиями или временными выборками

        Пример для вопроса о распределении дохода по регионам:
        ```python
        region_stats = df.groupby('Client_Region')['Earnings_USD'].agg(['mean', 'median', 'count']).reset_index()
        region_stats = region_stats.sort_values(by='mean', ascending=False)
        for _, row in region_stats.iterrows():
            print(f"{row['Client_Region']}: ${row['mean']:.2f} (медиана: ${row['median']:.2f}, кол-во: {row['count']})")
        ```
        """

        self.agent = create_pandas_dataframe_agent(
            self.llm,
            self.df,
            verbose=verbose,
            agent_type=AgentType.OPENAI_FUNCTIONS,
            allow_dangerous_code=True,
            prefix=agent_prefix
        )

    def process_query(self, query):
        result = {
            "query": query,
            "answer": None,
            "error": None
        }

        try:
            if not self.verbose:
                stdout_buffer = io.StringIO()
                stderr_buffer = io.StringIO()

                with redirect_stdout(stdout_buffer), redirect_stderr(stderr_buffer):
                    response = self.agent.invoke(query)
            else:
                response = self.agent.invoke(query)

            result["answer"] = response["output"]

            return result
        except Exception as e:
            result["error"] = f"Ошибка обработки запроса: {str(e)}"
            return result
