# Retrieval Design

My design is based on the [Contextual Retrieval framework](https://www.anthropic.com/news/contextual-retrieval) put forward by Anthropic.

## Build

### Pre-processing

The application first extracts all documents into a normalized plain-text format. It currently supports plain text (`.txt`, `.md`, `.rst`) and `.pdf` file inputs. It has a 100% success rate converting the LabDocs dataset provided for this challenge. However, LabDocs/FDA/Microbiology/K181029.pdf appears to be an empty file.

Once the text is extracted, it is chunked into smaller pieces (approximately 500 words per chunk). I used the `chonkie.SentenceChunker` algorithm to chunk the documents. It tries to maintain sentence structures in the chunks. I used zero overlap between chunks because chunk context can be established with LLM-generated contextual embeddings. Context is added to each chunk based on its source file. This context comes in two forms:

1. Context derived from the file's path. This is added by expert opinion via the `app/config/chunk_annotation_patterns.yml` file.
2. Context added by an LLM intended to situate the chunk within the overall document. I limited the number of allowed characters in the LLM context to the range of 30 < x < 750.

The contextual embeddings were generated with the following query structure:
```
<document>
{whole_document}
</document>
Here is the chunk we want to situate within the whole document
<chunk>
{chunk_text}
</chunk>
Please give a short succinct context to situate this chunk within the overall document for the purposes of improving search retrieval of the chunk. Answer only with the succinct context and nothing else.
```

After chunking, there are 105,520 text blobs to search through.

There are approximately 50 million tokens in the text corpus after my pre-processing.

#### Challenges during pre-processing
1. Some input PDF files lacked the metadata that allows for fast `fitz`-based text extraction. I had to use an OCR-based imange-text extraction technique for those 73 files.
2. Chunk-context generation costs money and is slow. I used the low-cost Amazon Nova Lite to contextualize the chunks. It has a 300k token context window, which is well above the largest document+chunk size of ~90k tokens (LabDocs/FDA/Microbiology/K191288_REVIEW.pdf). However, the Amazon Nova Lite model's performance significantly degrades for large queries. Some of the documents in this dataset are 400k+ characters. I did an initial pass with Amazon Nova Lite, then found problematic examples and re-generated the context with the more powerful Amazon Nova Pro model. The larger, more expensive models generate much higher quality responses for normal and large queries and have higher behavioral stability.
3. I reviewed the contextual annotations and removed those with low quality (too long, too short, no content, junk tags). Then I re-ran those queries against the more powerful Amazon Nova Pro LLM. The total cost of generating the contextual annotations was approximately (TODO: calculate).

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

I retrieve 50 chunks with each algorithm and select the top 30 chunks based on the Rank Fusion score.

### Query and Retrieval
1. A user inputs a query (question or request)
2. Chunks are retrieved from the VDB via KNN L2 search with FAISS
3. Chunks are retrieved with the BM25 search
4. Use Reciprocal Rank Fusion and take the top 20 chunks.
5. Add the top 20 chunks to the user's input as context, and query the LLM to respond to the initial query.


