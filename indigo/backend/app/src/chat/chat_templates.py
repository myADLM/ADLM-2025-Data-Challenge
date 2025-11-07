import inspect

def system_instructions():
    return inspect.cleandoc("""
        You are a helpful AI agent working with a corpus of documents related to medical devices and clinical
        lab processes. You will receive a question from the user and a list of partial documents that may be
        related to the question. You should read the document chunks to reply to the question and include
        citations from the documents. Keep your reply short and concise, only using documents if they are
        relevant to the question. You may usemarkdown formatting in your reply.
    """)

def user_query(context_chunks: list[str], query: str):
    context = "\n\n".join(
        [
            f"Source file: {record['file_path']}\nChunk: {record['contextual_chunk']}"
            for record in sorted(context_chunks, key=lambda d: d["file_path"])
        ]
    )
    return inspect.cleandoc(f"""
    DOCUMENT CHUNKS:
    {context}
    
    USER QUERY:
    {query}
    """)
