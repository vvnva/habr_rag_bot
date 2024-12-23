import yaml
from qdrant_client import QdrantClient
from langchain.embeddings import HuggingFaceEmbeddings
from langchain_qdrant import QdrantVectorStore

with open("config.yaml", "r") as file:
    config = yaml.safe_load(file)

def get_qdrant_retriever():
    client = QdrantClient(path=config['qdrant']['path_to_qdrant_collection'])
    embedder = HuggingFaceEmbeddings(model_name=config['qdrant']['embedder_model_name'])
    collection_name = config['qdrant']['collection_name']

    vector_store = QdrantVectorStore(
        client=client,
        collection_name=collection_name,
        embedding=embedder
    )
    return vector_store.as_retriever(search_type="similarity", search_kwargs={"k":5})