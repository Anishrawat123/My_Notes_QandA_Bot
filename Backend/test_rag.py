from pdf_reader import extract_text_from_pdf
from chunker import create_chunks
from embeddings import create_embeddings
from vector_db import create_vector_database
from retriever import retrieve_chunks
from generator import generate_answer

#1.PDF->TEXT
text=extract_text_from_pdf("documents\The Ultimate Python Handbook (1).pdf")

#2. TEXT->CHUNKS
chunks=create_chunks(text)

print("Total chunks:",len(chunks))

#3. Chunks->embeddings 
embeddings=create_embeddings(chunks)

print("Embedding shape:",embeddings.shape)

#4. Embeddings->FAISS
index=create_vector_database(embeddings)
print("Vectors stored:",index.ntotal)

#user question 
question = "what is list "

# Retrieve relevent chunks 
results=retrieve_chunks(
    question,
    chunks,
    index,
    top_k=3
)

#7.Generate answer 
answer=generate_answer(
    question,
    results
)

print("\nANSWER:")
print(answer)


#ALL above steps is rag pipelines 


