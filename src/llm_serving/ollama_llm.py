import yaml
from langchain_ollama.llms import OllamaLLM

with open("config.yaml", "r") as file:
    config = yaml.safe_load(file)

llm = OllamaLLM(
    model=config['llm']['ollama_model_name'],
    temperature=config['llm']['temperature'],
    base_url=config['llm']['base_url']
    )

def get_ollama_model():
    return llm