import os
import yaml
from langchain_ollama.llms import OllamaLLM

with open("config.yaml", "r") as file:
    config = yaml.safe_load(file)

ollama_host_env = os.getenv("OLLAMA_HOST")
if ollama_host_env:
    config['llm']['base_url'] = ollama_host_env

llm = OllamaLLM(
    model=config['llm']['ollama_model_name'],
    temperature=config['llm']['temperature'],
    base_url=config['llm']['base_url']
    )

def get_ollama_model():
    return llm