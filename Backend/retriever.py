import numpy as np
from embeddings import model

def retrieve_chunks(question,chunks,index,top_k=3):

    #question ->vector
    question_embedding=model.encode([question])

    #FAISS ko float 32 chaiye
    question_embedding = np.array(
        question_embedding
    ).astype("float32")

    #similar vectors search 
    distances,indices= index.search(
        question_embedding,
        top_k
    )

    #Relevent chunks
    results =[]

    for i in indices[0]:
        results.append(chunks[i])

    return results