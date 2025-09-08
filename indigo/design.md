# Retrieval Design

My design is based on the [Contextual Retrieval framework](https://www.anthropic.com/news/contextual-retrieval) put forward by Anthropic.

## Build

### Pre-processing

The application first extracts all documents into a normalized plain-text format. It currently supports plain text (`.txt`, `.md`, `.rst`) and `.pdf` file inputs. It has a 100% success rate converting the LabDocs dataset provided for this challenge.

Once the text is extracted, it is chunked into smaller pieces (approximately 500 words per chunk). Context is added to each chunk based on its source file. This context comes in two forms:

1. Context derived from the file's path
2. Context added by an LLM intended to situate the chunk within the overall document


#### Vector Database
Once the chunks are prepared, I use the Quen3-Embedding-8B model to embed the chunks into a vector database.

#### BM25
To help with exact retrieval and other weaknesses of vector search, I also use classic BM25 search.

$$
score(q, D)=\sum_{t\in q}IDF(t)\frac{f(t,D)(k_{1}+1)}{f(t,D)+k_{1}(1-b+b\frac{|D|}{avgdl})}
$$

$k_{1}$ and $b$ are free parameters, set to the defaults.

### Query and Retrieval
1. A user inputs a query (question or request).
2. Chunks are retrieved from the VDB via KNN L2 search with FAISS
3. Chunks are retrieved with the BM25 search
4. Use Reciprocal Rank Fusion and take the top 20 chunks.
5. Add the top 20 chunks to the user's input as context, and query the LLM to respond to the initial query.


