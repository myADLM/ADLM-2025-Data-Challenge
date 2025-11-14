import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'modules'))
from llm import LLM
from config import LLMConfig
import json
import inspect
from concurrent.futures import ThreadPoolExecutor
import logging
import os
from datetime import datetime
import unicodedata

def sanitize_unicode_text(text, max_length=None):
    """
    Sanitize text to handle Unicode characters that might cause encoding issues.
    Converts special Unicode characters to ASCII equivalents where possible.
    """
    if not isinstance(text, str):
        text = str(text)
    
    # Normalize Unicode characters and try to convert to ASCII
    try:
        # First normalize the Unicode (decompose combined characters)
        normalized = unicodedata.normalize('NFKD', text)
        # Try to encode to ASCII, replacing problematic characters
        ascii_text = normalized.encode('ascii', 'ignore').decode('ascii')
        
        # If we lost too much content, use a more conservative approach
        if len(ascii_text) < len(text) * 0.5:  # Lost more than 50% of characters
            # Keep common Unicode characters but replace problematic ones
            safe_text = text.replace('\u2206', 'Delta')  # ∆
            safe_text = safe_text.replace('\u03b2', 'beta')  # β
            safe_text = safe_text.replace('\u2264', '<=')  # ≤
            safe_text = safe_text.replace('\u2265', '>=')  # ≥
            safe_text = safe_text.replace('\u2192', '->')  # →
            safe_text = safe_text.replace('\u2190', '<-')  # ←
            safe_text = safe_text.replace('\u2010', '-')  # hyphen
            safe_text = safe_text.replace('\u2212', '-')  # minus
            safe_text = safe_text.replace('\u2248', '~=')  # ≈
            safe_text = safe_text.replace('\u03bc', 'mu')  # μ
            safe_text = safe_text.replace('\u00b1', '+/-')  # ±
            safe_text = safe_text.replace('\u2713', 'checkmark')  # ✓
            safe_text = safe_text.replace('\u2705', '[OK]')  # ✅
            safe_text = safe_text.replace('\u25e6', '•')  # ◦ white bullet
            safe_text = safe_text.replace('\u2022', '•')  # • bullet
            safe_text = safe_text.replace('\u2023', '>')  # ‣ triangular bullet
            safe_text = safe_text.replace('\u2043', '-')  # ⁃ hyphen bullet
            safe_text = safe_text.replace('\u204e', '*')  # ⁎ low asterisk
            safe_text = safe_text.replace('\u00b7', '·')  # · middle dot
            safe_text = safe_text.replace('\u2219', '*')  # ∙ bullet operator
            
            # Try ASCII encoding again
            try:
                ascii_text = safe_text.encode('ascii', 'ignore').decode('ascii')
            except (UnicodeEncodeError, UnicodeDecodeError):
                # More aggressive: strip all non-ASCII characters
                ascii_text = ''.join(char for char in safe_text if ord(char) < 128)
                
                # If still problematic, last resort
                if not ascii_text or len(ascii_text) < 10:
                    ascii_text = repr(text)[1:-1]  # Remove quotes from repr
        
        if max_length and len(ascii_text) > max_length:
            ascii_text = ascii_text[:max_length] + "..."
            
        return ascii_text
        
    except Exception as e:
        # Absolute fallback
        return repr(text)[1:-1]  # Remove quotes from repr

class SOPQuery:
    def __init__(self, model=None, debug=0):
        # Get default model from config if not specified
        if model is None:
            config = LLMConfig.get_config(LLMConfig.DEFAULT_PROVIDER)
            model = config["default_model"]
        
        self.model = model
        self.debug = debug
        self.llm = LLM(model=model)

        # Setup logging
        logs_dir = os.path.join(os.path.dirname(__file__), '../logs')
        os.makedirs(logs_dir, exist_ok=True)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        log_file = os.path.join(logs_dir, f'sop_query_{timestamp}.log')

        logging.basicConfig(
            filename=log_file,  # This writes to a file
            level=logging.DEBUG,
            format='%(asctime)s - %(levelname)s - %(message)s',
            encoding='utf-8'  # Handle Unicode characters properly
        )
        logging.info("Initialized SOPQuery instance")

    def log_function_call(self, func_name):
        logging.info(f"Function called: {func_name}")

    def enhance_query_with_llm(self, question, model=None):
        self.log_function_call("enhance_query_with_llm")
        """
        Use LLM to understand the question better and extract key search terms
        
        Args:
            question: User's question
            
        Returns:
            Dictionary with enhanced query information
        """
        prompt_text = f"""
        You are a laboratory assistant analyzing a question about Standard Operating Procedures (SOPs).
        QUESTION TO ANALYZE: "{question}"
        
        Your task is to understand what the user is asking about using your general laboratory knowledge, 
        then identify the best search terms to find that information in the SOP data.

        CRITICAL INSTRUCTION: When the user mentions a CONCERN or PROBLEM (such as worrying about typos, duplicate steps, errors, discrepancies, or inconsistencies), you MUST convert that concern into a DIRECT QUESTION that asks the next LLM to specifically look for and identify those issues.

        Rephrase the original question to be more specific and searchable within SOP documentation, using your laboratory knowledge to expand abbreviations and clarify intent.

        Included in this, append to the question LIKELY SOP to consider
        You may use general knowledge to UNDERSTAND and re-word the question 
        (e.g., A1C = Hemoglobin A1C, QC means quality control)

        IMPORTANT: If the user expresses ANY concern about potential issues (typos, errors, duplicates, discrepancies), create a SEPARATE EXPLICIT QUESTION on the same line before 'LIKELY SOP', asking to identify those specific issues. Don't just include the concern as context - make it an actionable question.

        Return only the improved question(s), nothing else.
        
        Examples:
        - "What is the reference range for A1C?" → "What are the reference ranges and normal values for Hemoglobin A1C testing? LIKELY SOP: Hemoglobin A1c"
        - "How do I collect the specimen?" → "What are the specimen collection procedures and requirements?"
        - "What QC do I need?" → "What quality control procedures and requirements are specified?"
        - "Can i test for pregnancy?" -> "What are the Lab Tests I can order that will determine if i am pregnant? LIKELY SOP: Quantitative hcg"
        - "I'm worried there are duplicate steps in the allergy test results for cockroach and peanut" -> "What are the procedures for performing and interpreting cockroach and peanut allergy tests? What, if any, are the possible duplicate steps in those procedures? LIKELY SOP: Cockroach IgE, Peanut IgE"
        """
        llm = LLM(model=model or self.model)
        try:
            response = llm.invoke(prompt_text)
            # Sanitize the response to handle Unicode issues
            sanitized_response = sanitize_unicode_text(response)
            return sanitized_response
        except Exception as e:
            print(f'LLM invoke error in enhance_query_with_llm: {e}')
            return question  # Return original question as fallback
            
        if self.debug > 0:
            print(sanitized_response)
        if self.debug > 2:
            print(prompt_text)
        
    def make_llm_pretty(self, question, llm_response, model=None):
        self.log_function_call("make_llm_pretty")
        """
        Translate the llm response into nice english
        """
        prompt_text = f"""
You are a eloquent, but concise AI assistant who works in the lab. 
Your expertise is translating structured output of an LLM into english that the lab staff can understand
 ---------
 ORIGINAL QUESTION
 {question}
 ---------
 LLM RESPONSE
 {llm_response}
 ---------
 Translate the response into English. To do so:
 1) Q: (Restate the original question)
 2) A: (Concisely state the answer)
 3) Why: (Add a short explanation)
 4) Refs: (List the documents and excerpts so they staff can understand the source)
"""
        
        llm = LLM(model=model or self.model)
        try:
            response = llm.invoke(prompt_text)
            # Sanitize the response to handle Unicode issues
            sanitized_response = sanitize_unicode_text(response)
            if self.debug > 0:
                print(sanitized_response)
            if self.debug > 2:
                print(prompt_text)
            return sanitized_response
        except Exception as e:
            print(f'LLM invoke error in make_llm_pretty: {e}')
            return f"Error formatting response: {e}"

    def synthesize_multiple_sources(self, primary_question, llm_response, model=None):
        self.log_function_call("synthesize_multiple_sources")
        """
        Synthesize information from multiple sources to answer a question
        """
        prompt_text = f"""
    You are a brilliant, inquisitive AI assistant who understands how to take structured information from multiple sources and synthesize 
    the information to answer a question
 ---------
 SOURCE INFORMATION
 {llm_response}
 ---------
 PRIMARY QUESTION: {primary_question}
 ---------
 Given the question and the source information, synthesize the information to answer the question clearly and concisely.
 Note that you are NOT to use your internal knowledge or outside references
 to answer the question - answers should be tracable to explicit excerpts within the source information.
 Given that the question may actually comprise multiple separate questions and answers. For each question, assess
 their relevance to the original question and
 rank over the relevance threshold, rank them from highest to lowest.
 The relevance level should be a number between 0 and 1, where 1 is 100% relevance.
 Only report options where the relevance level is greater than the relevance threshold.
 
 Guidelines:
 
 1) Answer the question against the source information
 2) For each question or derived question, assign a relevance to the primary question from 0 to 1
 3) Sort questions from highest to lowest
 4) Return 1 line per question in the following format; enclose property name and value with double quotes and escape double quotes with "\\"
  "question":"value", "answer":"value", "document": "value", "excerpt":"verbatim_passage_excerpt", "relevance_level":"value"
"""
        
        llm = LLM(model=model or self.model)
        try:
            llm_response_text = llm.invoke(prompt_text)
            # Sanitize the response to handle Unicode issues
            llm_response_text = sanitize_unicode_text(llm_response_text)
        except Exception as e:
            print(f'LLM invoke error in synthesize_multiple_sources: {e}')
            return {"error": "Failed to invoke LLM in synthesize_multiple_sources", "raw_error": str(e)}

        response = ' {"function":"' + inspect.stack()[0][3] + '","primary_question":"'+primary_question+'","results":['
        response_lines = []
        for line in llm_response_text.splitlines():
            if line.strip():  # Only add non-empty lines
                response_lines.append('{' + line + '}')
        
        if response_lines:
            response = response + ','.join(response_lines) + ']}'
        else:
            response = response + ']}'

        if self.debug > 0:
            print(llm_response_text)
        if self.debug > 2:
            print(prompt_text)
        try:
            jres = json.loads(response)
        except Exception as e:
            print(f'JSON parsing error in synthesize_multiple_sources: {e}')
            print('Response: '+response)
            jres = {"error": "Failed to parse JSON response", "raw_response": response}
        return jres

    def find_document_excerpts(self, primary_question, document, name, history="", relevance_threshold=0.1, model=None):
        self.log_function_call("find_document_excerpts")
        """
        Compare a question against a document and identify if the document addresses the question
        """
        prompt_text = f"""You are a laboratory assistant with access to Standard Operating Procedure (SOP) data. 
Assess questions against the reference in order to clearly answer the question.
 ---------
 DOCUMENT NAME
 {name}
 DOCUMENT
 {document}
 ---------
 QUESTION: {primary_question}
 ---------
 Given the document and the question, answer the question clearly and concisely.
 Some questions may require information from multiple documents, so extract any potentially relevant information
 Alternatively, the question may actually comprise multiple questions, enumerate the questions and answer each one
 Analogously, if there are important assumptions that make the interpretation unclear, identify
 these as unanswered question. Note that you are NOT to use your internal knowledge or outside references
 to answer the question - answers should be tracable to explicit excerpts within the document. Be generous with the excerpts to preserve context
 For each assumption or question, assess their relevance to the original question
 rank over the relevance threshold, rank them from highest to lowest.
 The relevance level should be a number between 0 and 1, where 1 is 100% relevance.
 Only report options where the relevance level is greater than the relevance threshold.
 
 Guidelines:
 
 1) Answer the question against the document
 2) For each question/assumption, assign a relevance to the question from 0 to 1
 3) Sort questions from highest to lowest
 4) Return 1 line per question in the following format; enclose property name and value with double quotes and escape double quotes with "\\"
  "question":"value", "answer":"value", "document": "value", "excerpt":"verbatim_passage_excerpt", "relevance_level":"value"
"""
        
        # Create a new LLM instance for each thread to ensure thread safety
        llm = LLM(model=model or self.model)
        try:
            logging.info(f"Starting LLM call for document: {name}")
            llm_response_text = llm.invoke(prompt_text)
            # Sanitize the response to handle Unicode issues
            llm_response_text = sanitize_unicode_text(llm_response_text)
            logging.info(f"Completed LLM call for document: {name}")
        except Exception as e:
            error_msg = f'LLM invoke error in find_document_excerpts for {name}: {e}'
            print(error_msg)
            logging.error(error_msg)
            return {"error": "Failed to invoke LLM in find_document_excerpts", "raw_error": str(e)}

        response = ' {"function":"' + inspect.stack()[0][3] + '","primary_question":"'+primary_question+'","results":['
        response_lines = []
        for line in llm_response_text.splitlines():
            if line.strip():  # Only add non-empty lines
                response_lines.append('{' + line + '}')
        
        if response_lines:
            response = response + ','.join(response_lines) + ']}'
        else:
            response = response + ']}'

        if self.debug > 0:
            print(llm_response_text)
        if self.debug > 2:
            print(prompt_text)
        try:
            jres = json.loads(response)
        except Exception as e:
            print(f'JSON parsing error in find_document_excerpts: {e}')
            print('Response: '+response)
            jres = {"error": "Failed to parse JSON response", "raw_response": response}
        return jres

    def identify_relevant_documents(self, primary_question, choice, relevance_threshold=0.75, model=None):
        self.log_function_call("identify_relevant_documents")
        """
        Takes a natural language phrase and a list of documents, and returns the sops the phrase matches with a confidence level
        Processes documents in batches to avoid API limits
        """
        # Process documents in batches - smaller for OpenAI to reduce load
        try:
            from config import LLMConfig
            current_provider = LLMConfig.DEFAULT_PROVIDER
        except:
            current_provider = "northwell"
        
        # Use smaller batches for OpenAI to reduce rate limiting
        batch_size = 400 if current_provider == "openai" else 400
        all_relevant_docs = []
        
        if self.debug > 0:
            print(f"Processing {len(choice)} documents in batches of {batch_size}")
        
        total_batches = (len(choice) + batch_size - 1) // batch_size

        def process_batch(batch, batch_num):
            if self.debug > 0:
                print(f"Processing batch {batch_num}/{total_batches} ({len(batch)} documents)")

            batch_result = self._identify_relevant_documents_batch(primary_question, batch, relevance_threshold, model)

            if 'error' in batch_result:
                error_msg = f"Error in batch {batch_num}: {batch_result['error']}"
                if 'raw_error' in batch_result:
                    error_msg += f" - {batch_result['raw_error']}"
                print(error_msg)
                logging.error(error_msg)
                return []

            if 'documents' in batch_result and batch_result['documents']:
                if self.debug > 0:
                    print(f"Batch {batch_num}: Found {len(batch_result['documents'])} relevant documents")
                return batch_result['documents']
            else:
                if self.debug > 0:
                    print(f"Batch {batch_num}: No documents found (result: {batch_result})")
            return []

        errors_encountered = []
        
        # Check which provider we're using to decide on concurrency
        try:
            from config import LLMConfig
            current_provider = LLMConfig.DEFAULT_PROVIDER
        except:
            current_provider = "northwell"  # fallback
        
        if current_provider == "openai":
            # Sequential processing for OpenAI to avoid rate limits
            if self.debug > 0:
                print("Using sequential processing for OpenAI provider")
            
            for i in range(0, len(choice), batch_size):
                batch = choice[i:i + batch_size]
                batch_num = i // batch_size + 1
                
                try:
                    result = process_batch(batch, batch_num)
                    if result:  # Only extend if we got actual results
                        all_relevant_docs.extend(result)
                    elif self.debug > 0:
                        print(f"Batch {batch_num} returned empty results")
                except Exception as e:
                    error_msg = f"Exception in batch {batch_num}: {e}"
                    print(error_msg)
                    logging.error(error_msg)
                    errors_encountered.append(error_msg)
                
                # Add a delay between requests for OpenAI
                import time
                time.sleep(15)
        else:
            # Parallel processing for Northwell and other providers
            if self.debug > 0:
                print("Using parallel processing for non-OpenAI provider")
                
            with ThreadPoolExecutor(max_workers=6) as executor:
                futures = []
                for i in range(0, len(choice), batch_size):
                    batch = choice[i:i + batch_size]
                    batch_num = i // batch_size + 1
                    futures.append(executor.submit(process_batch, batch, batch_num))

                for i, future in enumerate(futures):
                    try:
                        result = future.result()
                        if result:  # Only extend if we got actual results
                            all_relevant_docs.extend(result)
                        elif self.debug > 0:
                            print(f"Batch {i+1} returned empty results")
                    except Exception as e:
                        error_msg = f"Exception in batch {i+1}: {e}"
                        print(error_msg)
                        logging.error(error_msg)
                        errors_encountered.append(error_msg)

        # Sort all results by relevance level and return
        if all_relevant_docs:
            all_relevant_docs.sort(key=lambda x: float(x.get('relevance_level', 0)), reverse=True)
            if self.debug > 0:
                print(f"Total relevant documents found: {len(all_relevant_docs)}")
            return {
                "function": "identify_relevant_documents",
                "primary_question": primary_question,
                "documents": all_relevant_docs,  # Return all relevant documents, no artificial limit
                "total_batches": total_batches,
                "total_documents_processed": len(choice),
                "total_relevant_found": len(all_relevant_docs),
                "errors_encountered": errors_encountered
            }
        else:
            if self.debug > 0:
                print(f"No relevant documents found. Errors: {len(errors_encountered)}")
                if errors_encountered:
                    print("Errors encountered:", errors_encountered)
            return {
                "function": "identify_relevant_documents", 
                "primary_question": primary_question,
                "documents": [],
                "total_batches": total_batches,
                "total_documents_processed": len(choice),
                "errors_encountered": errors_encountered
            }
    
    def _identify_relevant_documents_batch(self, primary_question, choice_batch, relevance_threshold=0.1, model=None):
        self.log_function_call("_identify_relevant_documents_batch")
        """
        Process a single batch of documents for relevance identification
        """
        # Build document list string for this batch
        doc_list = ""
        for idx, name, desc in choice_batch:
            # Sanitize Unicode characters that might cause encoding issues
            sanitized_name = sanitize_unicode_text(name, max_length=200)
            sanitized_desc = sanitize_unicode_text(desc, max_length=500)
            doc_list += f"doc_id {idx}; name {sanitized_name}; description {sanitized_desc}\n"
        
        prompt_text = f"""You are a clinical laboratory expert who is very knowledgeable about clinical laboratory protocols. You need to apply
 your expertise in evaluating a question and identifying all the clinical laboratory SOPs that could be relevant
 in answering the question. You assign a relevance level to each document; the relevance level is a number
 between 0 and 1, where 1 is 100% confidence that the document is relevant, and 0 is 100% confidence that the
 document is irrelevant. Report any document that has a relevance level greater than the relevance threshold.
 
 CRITICAL RELEVANCE GUIDELINES:
 - For SPECIFIC allergen questions (e.g., cockroach, peanut, cat), only SOPs for that EXACT allergen should have high relevance (0.8-1.0)
 - General allergy tests or different allergens should have very low relevance (0.1-0.3) even if they are allergy-related
 - For example: if asking about cockroach allergy, a peanut IgE test should be 0.1-0.2 relevance, not 0.7+
 - Only give high relevance if the document specifically addresses the exact allergen, test type, or procedure mentioned
 - Generic or procedural matches should be lower relevance unless they directly apply to the specific question
 
 ---------
 Document list:
 {doc_list.strip()}
 ---------
 Primary question: {primary_question}
 ---------
 Relevance threshold: {relevance_threshold}
 ---------
 CRITICAL FORMATTING INSTRUCTIONS:
 - ONLY return the JSON lines as requested - NO explanatory text, headers, or conclusions
 - Do NOT include phrases like "Based on the primary question" or "The following documents have been evaluated"
 - Do NOT add explanatory paragraphs or summaries
 - If no documents meet the threshold, return nothing (empty response)
 
 Guidelines:
 1) Evaluate the potential relevance of each document against the question with strict specificity
 2) Be very conservative with relevance scores - only high scores for exact matches
 3) Identify the documents that have a relevance level greater than the relevance threshold
 4) Sort these documents from highest to lowest relevance level
 5) Return ONLY 1 line per relevant document in this exact format (no extra text):
  "doc_id":"value", "doc_name":"value", "relevance_level":"value"
"""
        
        llm = LLM(model=model or self.model)
        try:
            llm_response_text = llm.invoke(prompt_text)
            # Sanitize the response to handle Unicode issues
            llm_response_text = sanitize_unicode_text(llm_response_text)
            
            # Pre-process to fix common OpenAI formatting issues
            # Fix double braces that break JSON parsing
            llm_response_text = llm_response_text.replace('{{', '{').replace('}}', '}')
            
        except Exception as e:
            print(f'LLM invoke error in _identify_relevant_documents_batch: {e}')
            return {"error": "Failed to invoke LLM in batch processing", "raw_error": str(e)}

        # Escape quotes in primary_question to prevent JSON parsing issues
        escaped_question = primary_question.replace('"', '\\"')
        response = ' {"function":"' + inspect.stack()[0][3] + '","primary_question":"'+escaped_question+'","documents":['
        response_lines = []
        
        # Direct string extraction approach - more robust than JSON parsing
        import re
        
        # Find all instances of doc_id, doc_name, and relevance_level values
        doc_ids = re.findall(r'"doc_id":\s*"([^"]*)"', llm_response_text)
        doc_names = re.findall(r'"doc_name":\s*"([^"]*)"', llm_response_text)
        relevance_levels = re.findall(r'"relevance_level":\s*"([^"]*)"', llm_response_text)
        
        # Match them up (should be same length if properly formed)
        if doc_ids and doc_names and relevance_levels and len(doc_ids) == len(doc_names) == len(relevance_levels):
            for doc_id, doc_name, relevance_level in zip(doc_ids, doc_names, relevance_levels):
                # Create clean JSON object
                json_obj = f'{{"doc_id":"{doc_id}", "doc_name":"{doc_name}", "relevance_level":"{relevance_level}"}}'
                response_lines.append(json_obj)
        
        if response_lines:
            response = response + ','.join(response_lines) + ']}'
        else:
            response = response + ']}'

        if self.debug > 0:
            print(llm_response_text)
        if self.debug > 2:
            print(prompt_text)
        try:
            jres = json.loads(response)
        except Exception as e:
            print(f'JSON parsing error in _identify_relevant_documents_batch: {e}')
            print('Response: '+response)
            jres = {"error": "Failed to parse JSON response", "raw_response": response}

        try:
            logging.info(jres)
        except UnicodeEncodeError:
            logging.info(f"Batch result: {len(jres.get('documents', []))} documents found")
        return jres

    # function to pass original Q and synthesized results, have LLM judge if good answer. If not, say "we are not satisfied with the results, would you like to rephrase the question etc?"
    def evaluate_answer_quality(self, question, synthesized_results, model=None):
        self.log_function_call("evaluate_answer_quality")
        """
        Evaluate the quality of the synthesized answer against the original question
        """
        prompt_text = f"""You are a meticulous AI assistant who evaluates the quality of answers provided to questions.
        Your task is to assess whether the final results provided by a previous AI assistant adequately addresses the original question.
        Original User Question: {question}
        Final Results: {synthesized_results}
        Please evaluate the quality of the final results and if the answer is satisfactory based on the original question. Does the Answer given in number 2 of the Final Results actually answer the original question? If yes, return 'satisfactory'. If no, return 'not satisfactory'. After that, provide a brief explanation of your reasoning.
        """
        llm = LLM(model=model or self.model)
        try:
            response = llm.invoke(prompt_text)
            # Sanitize the response to handle Unicode issues
            sanitized_response = sanitize_unicode_text(response)
            if self.debug > 0:
                print(sanitized_response)
            if self.debug > 2:
                print(prompt_text)
            return sanitized_response
        except Exception as e:
            print(f'LLM invoke error in evaluate_answer_quality: {e}')
            return f"Error evaluating answer quality: {e}"

    def ask_sop(self, question, sops, history=None, sop_docs_path='../LabDocs/extracted_txts/'):
        self.log_function_call("ask_sop")
        """
        Main method to ask a question about SOPs and get a comprehensive answer
        
        Args:
            question: The question to ask
            sops: List of SOP documents [(idx, name, description), ...]
            history: List to track conversation history (optional)
            sop_docs_path: Path to the extracted text files
            
        Returns:
            tuple: (answer_string, updated_history)
        """
        import time
        start_time = time.time()

        if history is None:
            history = []
            
        current_time = start_time
        print(f"Starting time: {current_time}")
        
        try:
            enhanced_question = self.enhance_query_with_llm(question)
            print(f"Enhanced question: {enhanced_question}")
        except Exception as e:
            print(f"Error in enhance_query_with_llm: {e}")
            enhanced_question = question

        current_time = time.time()
        print(f"Time after enhancing question: {current_time} (Elapsed: {current_time - start_time:.2f}s)")

        
        try:
            documents = self.identify_relevant_documents(enhanced_question, sops)
        except Exception as e:
            print(f"Error in identify_relevant_documents: {e}")
            return f"Error identifying relevant documents: {e}", history

        current_time = time.time()
        print(f"Time after identifying relevant documents: {current_time} (Elapsed: {current_time - start_time:.2f}s)")
            
        doc_excerpts = []
        
        # Check if we got a valid response with documents
        if 'error' in documents:
            return f"Error identifying relevant documents: {documents['error']}", history
        
        if 'documents' not in documents:
            return f"No documents key found in response. Response: {documents}", history
        
        # Check if no relevant documents were found
        if not documents['documents'] or len(documents['documents']) == 0:
            # Check if this was due to API errors
            errors_encountered = documents.get('errors_encountered', [])
            if errors_encountered:
                error_response = (
                    f"I encountered errors while trying to analyze the SOPs for your question: '{question}'. "
                    f"API errors occurred:\n"
                )
                for i, error in enumerate(errors_encountered[:3]):  # Show first 3 errors
                    error_response += f"{i+1}. {error}\n"
                if len(errors_encountered) > 3:
                    error_response += f"... and {len(errors_encountered) - 3} more errors.\n"
                
                error_response += (
                    f"\nThis may be due to API rate limiting, authentication issues, or service unavailability. "
                    f"Please try again in a few moments, or contact your administrator if the problem persists."
                )
                history.append(error_response)
                return error_response, history
            else:
                no_answer_response = (
                    f"I'm sorry, but I couldn't find any relevant information in the available SOPs "
                    f"to answer your question: '{question}'. "
                    f"The current SOP database contains {len(sops)} document(s), but none appear to be "
                    f"relevant to your query. You may want to:\n"
                    f"1. Rephrase your question with different terminology\n"
                    f"2. Check if there are additional SOPs that should be loaded\n"
                    f"3. Verify that your question relates to laboratory procedures covered by the SOPs"
                )
                history.append(no_answer_response)
                return no_answer_response, history
        
        try:
            def process_document(document):
                sop = sops[int(document['doc_id'])]
                # Convert .json filename to .txt and remove _es1 suffix
                txt_filename = sop[1].replace('.json', '.txt').replace('_es1', '')
                txt_path = f'{sop_docs_path}{txt_filename}'

                try:
                    with open(txt_path, 'r', encoding='utf-8') as file:
                        sop_content = file.read()
                except UnicodeDecodeError:
                    # Fallback to different encodings if UTF-8 fails
                    try:
                        with open(txt_path, 'r', encoding='latin-1') as file:
                            sop_content = file.read()
                    except UnicodeDecodeError:
                        with open(txt_path, 'r', encoding='cp1252') as file:
                            sop_content = file.read()
                except FileNotFoundError:
                    print(f"Warning: Text file not found: {txt_path}")
                    return json.dumps({"error": f"Text file not found: {txt_filename}"})

                # Sanitize the document content to handle Unicode issues
                sanitized_content = sanitize_unicode_text(sop_content, max_length=None)
                
                # This LLM call will now run in parallel across different threads
                doc_excerpt = self.find_document_excerpts(enhanced_question, sanitized_content, sop[1][:-5])  # Remove .json extension
                
                # Safe JSON serialization with Unicode handling
                try:
                    return json.dumps(doc_excerpt, ensure_ascii=True)
                except (UnicodeEncodeError, TypeError) as e:
                    print(f"Unicode error in JSON serialization: {e}")
                    # Fallback: sanitize the entire result
                    sanitized_excerpt = {
                        "error": "Unicode encoding issue in document processing",
                        "document": sop[1][:-5],
                        "original_error": str(e)
                    }
                    return json.dumps(sanitized_excerpt, ensure_ascii=True)

            # Use more workers since we're now parallelizing the actual LLM calls
            with ThreadPoolExecutor(max_workers=6) as executor:
                futures = [executor.submit(process_document, document) for document in documents['documents']]
                for future in futures:
                    doc_excerpt = future.result()
                    doc_excerpts.append(doc_excerpt)
                    history.append(doc_excerpt)
        except Exception as e:
            print(f"Error in find_document_excerpts: {e}")
            return f"Error processing documents: {e}", history

        current_time = time.time()
        print(f"Time after finding document excerpts: {current_time} (Elapsed: {current_time - start_time:.2f}s)")
        
        try:
            if len(documents['documents']) > 1:
                synthesized_results = self.synthesize_multiple_sources(enhanced_question, doc_excerpts)
                history.append(json.dumps(synthesized_results))
            else:
                synthesized_results = doc_excerpts
        except Exception as e:
            print(f"Error in synthesize_multiple_sources: {e}")
            synthesized_results = doc_excerpts

        current_time = time.time()
        print(f"Time after synthesizing sources: {current_time} (Elapsed: {current_time - start_time:.2f}s)")
        
        try:
            pretty_result = self.make_llm_pretty(enhanced_question, synthesized_results)
            history.append(pretty_result)
            current_time = time.time()
            print(f"Time after making llm pretty: {current_time} (Elapsed: {current_time - start_time:.2f}s)")

            # pass original Q and pretty result, have LLM judge if good answer. If not, say "we are not satisfied with the results, would you like to rephrase the question etc?"
            print("Evaluating answer quality...")

            evaluation = self.evaluate_answer_quality(enhanced_question, pretty_result)
            history.append(evaluation)

            current_time = time.time()
            print(f"Time after evaluating answer quality: {current_time} (Elapsed: {current_time - start_time:.2f}s)")

            #if the evaluation indicates poor quality, return a message instead of the answer
            if "not satisfied" in evaluation.lower():
                unsat_response = (
                    f"I'm sorry, but the information retrieved from the SOPs does not adequately answer your question: '{question}'. "
                    f"You may want to:\n"
                    f"1. Rephrase your question with different terminology\n"
                    f"2. Check if there are additional SOPs that should be loaded\n"
                    f"3. Verify that your question relates to laboratory procedures covered by the SOPs"
                )
                return unsat_response
            else:
                print("Answer quality satisfactory, proceeding to format the answer.")
            #     print(f"Evaluation details: {evaluation}")
            
            end_time = time.time()
            total_time = end_time - start_time
            logging.info(f"ask_sop completed in {total_time:.2f} seconds")
            return pretty_result, history
        except Exception as e:
            print(f"Error in make_llm_pretty: {e}")
            return f"Error formatting final result: {e}", history