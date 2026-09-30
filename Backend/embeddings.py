from sentence_transformers import SentenceTransformer
model=SentenceTransformer("all-MiniLM-L6-v2")

def create_embeddings(chunks):
    embeddings=model.encode(chunks) #har chunk ko vector mai karta ha
    return embeddings