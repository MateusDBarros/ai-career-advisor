from langchain_huggingface import HuggingFaceEmbeddings
from transformers import AutoTokenizer


model_path = "sentence-transformers/all-MiniLM-L6"
embbeding_model = HuggingFaceEmbeddings(
    model_name=model_path,
)
embedding_tokenizer = AutoTokenizer.from_pretrained(model_path)
