import pandas as pd
from src.vector_db.qdrant import get_qdrant_retriever
from src.llm_serving.ollama_llm import get_ollama_model
from src.graph.graph_funcs import get_compiled_graph, run_graph
from dotenv import load_dotenv

load_dotenv()

retriever = get_qdrant_retriever()
llm = get_ollama_model()
graph = get_compiled_graph(llm=llm, retriever=retriever)

data = {"question": [], "answer": [], "links": []}

questions = [
    "Как работают нейронные сети?",
    "Чем отличаются глубокие нейронные сети от обычных?",
    "Как обучить нейронную сеть?",
    "Какие существуют методы оптимизации в машинном обучении?",
    "Что такое регуляризация и зачем она нужна?",
    "Как работает метод обратного распространения ошибки?",
    "Какие есть методы кластеризации данных?",
    "Что такое k-means и как он работает?",
    "Как работает алгоритм ближайших соседей?",
    "Что такое решающие деревья?",
    "Как работает алгоритм Random Forest?",
    "Что такое градиентный бустинг?",
    "Какие библиотеки машинного обучения самые популярные?",
    "Какой язык программирования лучше всего подходит для Data Science?",
    "Что такое распределённые вычисления?",
    "Как работает Hadoop?",
    "Что такое Spark и чем он лучше Hadoop?",
    "Какие существуют инструменты для визуализации данных?",
    "Что такое Tableau и как им пользоваться?",
    "Как правильно интерпретировать данные?",
    "Какие методы статистического анализа данных существуют?",
    "Что такое A/B тестирование?",
    "Как оценить результаты эксперимента?",
    "Какие существуют подходы к проектированию пользовательских интерфейсов?",
    "Что такое UX-дизайн?",
    "Как провести пользовательское исследование?",
    "Какие существуют методы прототипирования?",
    "Как использовать аналитические данные для улучшения продукта?",
    "Что такое Agile и как он работает?",
    "Какие основные принципы Scrum?",
    "Чем отличается Kanban от Scrum?",
    "Как внедрить Agile в команду?",
    "Какие метрики помогают оценить эффективность команды?",
    "Что такое технический долг?",
    "Как снизить технический долг?",
    "Какие есть стратегии управления проектами?",
    "Что такое риск-менеджмент в IT?",
    "Какие существуют подходы к управлению требованиями?",
    "Как проводить code review?",
    "Что такое CI/CD pipeline?",
    "Как реализовать безопасный процесс деплоя?",
    "Какие существуют подходы к мониторингу приложений?",
    "Что такое логирование и как его настроить?",
    "Как работает централизованное логирование?",
    "Какие инструменты для мониторинга систем самые популярные?",
    "Как обеспечить отказоустойчивость системы?",
    "Какие существуют стратегии резервного копирования данных?",
    "Как настроить кластер баз данных?",
    "Что такое шардирование?",
    "Как реализовать репликацию данных?",
    "Какие существуют инструменты для анализа больших данных?",
    "Как построить потоковую обработку данных?",
    "Что такое Kafka и как она используется?",
    "Как работает Redis и зачем он нужен?",
    "Какие есть подходы к проектированию распределённых систем?",
    "Что такое CAP-теорема?",
    "Какие существуют подходы к оптимизации сетевых запросов?",
    "Как работает CDN?",
    "Какие бывают подходы к масштабированию веб-приложений?",
    "Что такое сервернаяless архитектура?",
    "Как использовать AWS Lambda?",
    "Какие преимущества предоставляет Kubernetes?",
    "Что такое Service Mesh?",
    "Как организовать работу с микросервисами?",
    "Какие существуют подходы к обеспечению безопасности микросервисов?",
    "Как построить систему мониторинга микросервисов?",
    "Что такое GraphQL и как он работает?",
    "Какие преимущества у gRPC по сравнению с REST?",
    "Как работает WebSocket?",
    "Какие есть подходы к проектированию высоконагруженных систем?",
    "Как построить архитектуру с высокой доступностью?",
    "Какие существуют способы оптимизации производительности фронтенда?",
    "Как работает механизм кэширования?",
    "Какие существуют подходы к разработке PWA?",
    "Что такое WebAssembly?",
    "Какие языки программирования поддерживают WebAssembly?",
    "Как использовать TypeScript для больших проектов?",
    "Какие преимущества предоставляет React по сравнению с Angular?",
    "Что такое виртуальный DOM?",
    "Как оптимизировать работу с DOM?"
]

for question in questions:
    try:
        processed_answer, docs = run_graph(graph=graph, query=question)
        links = [{"title": doc['title'], "url": doc['link']} for doc in docs]

        data["question"].append(question)
        data["answer"].append(processed_answer)
        data["links"].append(links)
    except Exception as e:
        print(f"Error processing question '{question}': {e}")
        data["question"].append(question)
        data["answer"].append("Error")
        data["links"].append([])

df = pd.DataFrame(data)

file_path = "question_responses.csv"
df.to_csv(file_path, index=False)
