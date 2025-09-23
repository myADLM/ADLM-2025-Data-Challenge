# Retrieval Design

My design is based on the [Contextual Retrieval framework](https://www.anthropic.com/news/contextual-retrieval) put forward by Anthropic.

## Build

### Pre-processing

The application first extracts all documents into a normalized plain-text format. It currently supports plain text (`.txt`, `.md`, `.rst`) and `.pdf` file inputs. It has a 100% success rate converting the LabDocs dataset provided for this challenge. However, LabDocs/FDA/Microbiology/K181029.pdf appears to be an empty file.

73 files had to be converted to text via an OCR-based solution.

Once the text is extracted, it is chunked into smaller pieces (approximately 500 words per chunk). Context is added to each chunk based on its source file. This context comes in two forms:

1. Context derived from the file's path. This is added by expert opinion via the app/config/chunk_annotation_patterns.yml file.
2. Context added by an LLM intended to situate the chunk within the overall document

After chunking, there are 105,520 text blobs to search through.

There are approximately 50 million tokens in the text corpus after my pre-processing.

I am using the low-price Amazon Nova Liteto contextualize the chunks. It has a 300k token context window, which is well above the largest document+chunk size of ~90k tokens (LabDocs/FDA/Microbiology/K191288_REVIEW.pdf).

#### Vector Database
Once the chunks are prepared and annotated, I use the gpt-3.5-turbo model to embed the chunks into a vector database.

#### BM25
To help with exact retrieval and other weaknesses of vector search, I also use classic BM25 search. I am using the BM25Ok algorithm:

$$
score(q, D)=\sum_{t\in q}IDF(t)\frac{f(t,D)(k_{1}+1)}{f(t,D)+k_{1}(1-b+b\frac{|D|}{avgdl})}
$$

$k_{1}$ and $b$ are free parameters, set to the defaults.

I rewrote the Python rank_bm25 library in Rust and achieved 10x index construction speed and 240x search speed. Awesome!

#### Rank Fusion
I used [reciprocal rank fusion](https://cormack.uwaterloo.ca/cormacksigir09-rrf.pdf):

$$
RRF(d \in D) = (\frac{1}{60+r_{bm25}(d)})+(\frac{1}{60+r_{vector}(d)})
$$


### Query and Retrieval
1. A user inputs a query (question or request)
2. Chunks are retrieved from the VDB via KNN L2 search with FAISS
3. Chunks are retrieved with the BM25 search
4. Use Reciprocal Rank Fusion and take the top 20 chunks.
5. Add the top 20 chunks to the user's input as context, and query the LLM to respond to the initial query.


