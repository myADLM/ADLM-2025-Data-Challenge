import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'modules'))
from llm import LLM
from config import LLMConfig
import json
import inspect
import logging
import os
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor
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

class FDAQuery:
    def __init__(self, model=None, debug=0):
        # Get default model from config if not specified
        if model is None:
            config = LLMConfig.get_config(LLMConfig.DEFAULT_PROVIDER)
            model = config["default_model"]
        
        self.model = model
        self.debug = debug
        self.llm = LLM(model=model, max_tokens=10000)

        # Setup logging
        logs_dir = os.path.join(os.path.dirname(__file__), '../logs')
        os.makedirs(logs_dir, exist_ok=True)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        log_file = os.path.join(logs_dir, f'fda_query_{timestamp}.log')

        logging.basicConfig(
            filename=log_file,
            level=logging.DEBUG,
            format='%(asctime)s - %(levelname)s - %(message)s',
            encoding='utf-8'  # Handle Unicode characters properly
        )
        logging.info("Initialized FDAQuery instance")

    def log_function_call(self, func_name):
        logging.info(f"Function called: {func_name}")

    def enhance_query_with_llm(self, question, model=None):
        self.log_function_call("enhance_query_with_llm")
        """
        Use LLM to understand the question better and extract key search terms
        
        Args:
            question: User's question
            
        Returns:
            Dictionary with enhanced query information including exhaustive flag
        """
        prompt_text = f"""
        You are a laboratory assistant analyzing a question about FDA 510(k) documents.
        QUESTION TO ANALYZE: "{question}"

        Your task is to understand what the user is asking about using your general laboratory knowledge and FDA 510(k) summary knowledge, then identify the best search terms to find that information in the FDA 510(k) summary documents.

        CRITICAL INSTRUCTION: When the user mentions a CONCERN or PROBLEM (such as worrying about typos, duplicate steps, errors, discrepancies, or inconsistencies), you MUST convert that concern into a DIRECT QUESTION that asks the next LLM to specifically look for and identify those issues.

        Rephrase this question to be more specific and searchable within FDA 510(k) documentation, using your laboratory knowledge to expand abbreviations and clarify intent.
        Included in this, append to the question LIKELY FDA(s) to consider.
        You may use general laboratory knowledge to UNDERSTAND and re-word the question 
        (e.g., A1C = Hemoglobin A1C, QC means quality control)

        IMPORTANT: If the user expresses ANY concern about potential issues (typos, errors, duplicates, discrepancies), create a SEPARATE EXPLICIT QUESTION on the same line before 'LIKELY FDA(s)', asking to identify those specific issues. Don't just include the concern as context - make it an actionable question.

        EXHAUSTIVE ANALYSIS: Determine if this question requires a comprehensive search of ALL relevant documents or if a few top results would suffice:
        - Set to TRUE if the question uses words like: "all", "every", "list all", "show me all", "what are all", "comprehensive list", "complete list", "everything about", "all devices that", "all tests for", "all FDA clearances", "all 510(k) submissions"
        - Set to TRUE if the question is asking for a complete inventory, comprehensive comparison, or exhaustive listing
        - Set to FALSE if the question is asking about a specific device, procedure, or looking for general information where a few relevant examples would suffice

        Return your response in this exact format:
        ENHANCED_QUESTION: [your improved question here]
        EXHAUSTIVE: [true or false]
        
        Examples:
        - "I'd like all FDA documents around the TEG platform & assays" → "What are all FDA 510(k) submissions, clearances, and regulatory documentation related to Thromboelastography (TEG) platforms and associated assays, including device specifications, approved indications, and predicate devices? LIKELY DEVICE: TEG Thromboelastography Systems"
        - "Can the Da Vinci Surgical System be used on pediatric patients?" → "What specific pediatric use cases and safety data are included in the FDA 510(k) submissions for the Da Vinci Surgical System? LIKELY DEVICE: Da Vinci Surgical System"
        - "What are the side effects of the Medtronic MiniMed 670G?" → "List any reported adverse effects and post-market surveillance data related to the Medtronic MiniMed 670G as documented in FDA 510(k) records. LIKELY DEVICE: Medtronic MiniMed 670G"
        - "Are there similar devices to the Apple Watch Series 4 for health monitoring?" → "What predicate devices are listed in the 510(k) submissions that share functionality with the Apple Watch Series 4 for health monitoring purposes? LIKELY DEVICE: Apple Watch Series 4"
        - "who has cleared FDA for bacterial NGS?" → "Which companies and devices have received FDA clearance for bacterial Next-Generation Sequencing (NGS) testing, and what are the specific approved indications and sample types? LIKELY DEVICE: Bacterial NGS Systems"
        - "prostate ca prognosis tests FDA" → "Which prostate cancer prognosis tests have FDA clearance, and what are their specific claims for risk stratification and clinical decision-making? LIKELY DEVICE: Prostate Cancer Prognostic Tests"
        - "does my diabetes A1C sop match FDA requirements?" → "What are the FDA-approved specifications and requirements for Hemoglobin A1C testing devices and procedures? Are there any discrepancies between my current SOP and FDA-approved methodologies? LIKELY DEVICE: Hemoglobin A1C Analyzers"
        - "can you check if my HPV testing protocol is compliant?" → "What are the FDA-approved protocols and requirements for HPV testing systems? Does my current testing protocol comply with all FDA-mandated procedures and quality controls? LIKELY DEVICE: HPV Testing Systems"
        - "write me an sop for the Abbott ID NOW" → "Based on the FDA 510(k) clearance documentation for the Abbott ID NOW system, what are the specific procedural steps, quality control requirements, and operational specifications needed to create a comprehensive laboratory SOP? LIKELY DEVICE: Abbott ID NOW"
        - "what does AlloMap testing involve?" → "What are the specific methodologies, sample requirements, and analytical procedures for AlloMap Molecular Expression Testing as documented in FDA 510(k) submissions? LIKELY DEVICE: AlloMap Heart Molecular Expression Testing"
        - "do we need CLIA waiver for this test?" → "What are the FDA classification and CLIA complexity determinations for this specific testing device, and what regulatory requirements apply? LIKELY DEVICE: Point-of-Care Testing Systems"

        """
        llm = LLM(model=model or self.model)
        try:
            response = llm.invoke(prompt_text)
            # Sanitize the response to handle Unicode issues
            response = sanitize_unicode_text(response)
            
            # Parse the response to extract enhanced question and exhaustive flag
            enhanced_question = question  # fallback
            exhaustive = False  # default to false
            
            lines = response.strip().split('\n')
            for line in lines:
                if line.startswith('ENHANCED_QUESTION:'):
                    enhanced_question = line.replace('ENHANCED_QUESTION:', '').strip()
                elif line.startswith('EXHAUSTIVE:'):
                    exhaustive_str = line.replace('EXHAUSTIVE:', '').strip().lower()
                    exhaustive = exhaustive_str == 'true'
            
            return {
                'enhanced_question': enhanced_question,
                'exhaustive': exhaustive
            }
            
        except Exception as e:
            error_msg = f'LLM invoke error in enhance_query_with_llm: {e}'
            logging.error(error_msg)
            print(error_msg)
            return {
                'enhanced_question': question,  # Return original question as fallback
                'exhaustive': False
            }
            
        if self.debug > 0:
            print(response)
        if self.debug > 2:
            print(prompt_text)
        
    def make_llm_pretty(self, question, llm_response, model=None):
        self.log_function_call("make_llm_pretty")
        """
        Translate the llm response into nice english
        """
        prompt_text = f"""
        You are an eloquent, concise assistant working in FDA document analysis. 
        Translate structured LLM output into English understandable by staff.
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
        
        FORMATTING GUIDELINES:
        - Use clear paragraph breaks between sections (Q, A, Why, Refs)
        - Keep 510(k) numbers together (e.g., K221640, not K 2 2 1 6 4 0)
        - Keep page references together (e.g., pages 1-3, not pages 1- 3)
        - Use consistent formatting for regulatory numbers
        - Use bullet points or numbered lists when listing multiple items
        - Avoid unnecessary line breaks in the middle of words or numbers
        - Structure your response with clear sections separated by blank lines
        """
        
        llm = LLM(model=model or self.model)
        try:
            response = llm.invoke(prompt_text)
            # Sanitize the response to handle Unicode issues
            response = sanitize_unicode_text(response)
            
            # Post-process to fix common formatting issues
            response = self._clean_formatting(response)
            
        except Exception as e:
            error_msg = f'LLM invoke error in make_llm_pretty: {e}'
            logging.error(error_msg)
            print(error_msg)
            return f"Error formatting response: {e}"
            
        if self.debug > 0:
            print(response)
        if self.debug > 2:
            print(prompt_text)
        return response

    def _clean_formatting(self, text):
        """
        Clean up common formatting issues in FDA responses
        """
        import re
        
        # Remove or replace problematic Unicode characters that cause charmap issues
        # Replace common Unicode characters with ASCII equivalents
        unicode_replacements = {
            '\u2265': '>=',  # Greater than or equal to
            '\u2264': '<=',  # Less than or equal to
            '\u2260': '!=',  # Not equal to
            '\u00b1': '+/-', # Plus-minus
            '\u2248': '~=',  # Approximately equal
            '\u03bc': 'u',   # Greek letter mu (micro)
            '\u00b0': 'deg', # Degree symbol
            '\u2122': '(TM)', # Trademark
            '\u00ae': '(R)',  # Registered trademark
            '\u00a9': '(C)',  # Copyright
            '\u2013': '-',    # En dash
            '\u2014': '--',   # Em dash
            '\u2018': "'",    # Left single quote
            '\u2019': "'",    # Right single quote
            '\u201c': '"',    # Left double quote
            '\u201d': '"',    # Right double quote
            '\u2026': '...',  # Ellipsis
        }
        
        # Apply Unicode replacements
        for unicode_char, replacement in unicode_replacements.items():
            text = text.replace(unicode_char, replacement)
        
        # Remove any remaining problematic Unicode characters
        # Keep only ASCII and common extended ASCII characters
        text = ''.join(char if ord(char) < 256 else '-' for char in text)
        
        # Fix 510(k) numbers that got split with spaces or newlines
        # Match patterns like "K 2 2 1 6 4" or "K\n2\n2\n1\n6\n4" and convert to "K221640"
        text = re.sub(r'K\s*(\d)\s*(\d)\s*(\d)\s*(\d)\s*(\d)\s*(\d)', r'K\1\2\3\4\5\6', text)
        text = re.sub(r'K\s*(\d)\s*(\d)\s*(\d)\s*(\d)\s*(\d)', r'K\1\2\3\4\5', text)
        
        # Fix page references that got split
        text = re.sub(r'pages?\s*(\d+)\s*-\s*(\d+)', r'pages \1-\2', text)
        text = re.sub(r'page\s*(\d+)', r'page \1', text)
        
        # Fix other common splits in numbers (but preserve line breaks)
        text = re.sub(r'(\d)[ \t]+(\d)', r'\1\2', text)
        
        # Clean up excessive whitespace but preserve structure
        # Remove multiple spaces/tabs within lines but preserve line breaks
        text = re.sub(r'[ \t]+', ' ', text)
        
        # Normalize multiple consecutive newlines to double newlines (paragraph breaks)
        text = re.sub(r'\n\s*\n\s*\n+', '\n\n', text)
        
        # Remove trailing whitespace from lines
        text = re.sub(r'[ \t]+\n', '\n', text)
        
        # Fix bullet points that might have gotten mangled
        text = re.sub(r'•\s*', '• ', text)
        
        return text.strip()
        
    def synthesize_multiple_sources(self, primary_question, llm_response, model=None):
        self.log_function_call("synthesize_multiple_sources")
        """
        Synthesize information from multiple sources to answer a question
        """
        prompt_text = f"""
        You are a brilliant, inquisitive AI assistant who understands how to take structured information from multiple sources and synthesize the information to answer a question
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
            error_msg = f'LLM invoke error in synthesize_multiple_sources: {e}'
            logging.error(error_msg)
            print(error_msg)
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
            error_msg = f'JSON parsing error in synthesize_multiple_sources: {e}'
            logging.error(error_msg)
            print(error_msg)
            print('Response: '+response)
            jres = {"error": "Failed to parse JSON response", "raw_response": response}
        return jres

    def find_document_excerpts(self, primary_question, document, name, history="", relevance_threshold=0.1, model=None):
        self.log_function_call("find_document_excerpts")
        """
        Compare a question against a document and identify if the document addresses the question
        """
        prompt_text = f"""You are a laboratory assistant with access to Food and Drug Administration (FDA) 510(k) summary documents. 
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
        prompt_text += """
        CRITICAL: For the "excerpt" field:
        1. Replace any line breaks with spaces
        2. Escape any double quotes with backslashes
        3. Avoid truncating excerpts in the middle of words
        4. Keep all excerpts under 500 characters
        5. Verify your JSON is valid before returning
        """

        llm = LLM(model=model or self.model)
        try:
            logging.info(f"Starting LLM call for document: {name}")
            llm_response_text = llm.invoke(prompt_text)
            # Sanitize the response to handle Unicode issues
            llm_response_text = sanitize_unicode_text(llm_response_text)
            logging.info(f"Completed LLM call for document: {name}")
        except Exception as e:
            error_msg = f'LLM invoke error in find_document_excerpts for {name}: {e}'
            logging.error(error_msg)
            print(error_msg)
            return {"error": "Failed to invoke LLM in find_document_excerpts", "raw_error": str(e)}

        # response = ' {"function":"' + inspect.stack()[0][3] + '","primary_question":"'+primary_question+'","results":['
        # response_lines = []
        # for line in llm_response_text.splitlines():
        #     if line.strip():  # Only add non-empty lines
        #         response_lines.append('{' + line + '}')
        
        # if response_lines:
        #     response = response + ','.join(response_lines) + ']}'
        # else:
        #     response = response + ']}'

        # Improved response processing - handle malformed JSON better
        cleaned_lines = []
        for line in llm_response_text.splitlines():
            if line.strip():
                # Clean up common JSON formatting issues
                line = line.replace('\n', ' ')         # Replace newlines with spaces
                line = line.replace('\\', '\\\\')      # Escape backslashes first
                
                # Fix nested JSON structures
                line = line.replace('{{', '{')         # Remove nested braces
                line = line.replace('}}', '}')         # Remove nested braces
                line = line.replace('{[}', '')         # Remove invalid structures
                line = line.replace('{]}', '')         # Remove invalid structures
                
                # Handle quotes properly
                line = line.replace('"', '\\"')        # Escape all quotes
                line = line.replace('\\\\"', '\\"')    # Fix double-escaped quotes
                
                # Now we can safely add JSON structure around it
                if not line.startswith('{'):
                    line = '{' + line
                if not line.endswith('}'):
                    line = line + '}'
                
                cleaned_lines.append(line)

        response = ' {"function":"' + inspect.stack()[0][3] + '","primary_question":"'+primary_question+'","results":['
        
        if cleaned_lines:
            response = response + ','.join(cleaned_lines) + ']}'
        else:
            response = response + ']}'

        if self.debug > 0:
            print(llm_response_text)
        if self.debug > 2:
            print(prompt_text)
        try:
            jres = json.loads(response)
        except Exception as e:
            error_msg = f'JSON parsing error in find_document_excerpts: {e}'
            logging.error(error_msg)
            print(error_msg)
            print('Response: '+response)
            # jres = {"error": "Failed to parse JSON response", "raw_response": response}
            # Fallback approach - just use the raw text in a safe structure
            safe_response = {
                "function": "find_document_excerpts",
                "primary_question": primary_question,
                "results": [{
                    "question": primary_question,
                    "answer": "Error parsing LLM response, but original content might be helpful",
                    "document": name,
                    "excerpt": llm_response_text[:500] + ("..." if len(llm_response_text) > 500 else ""),
                    "relevance_level": "1"
                }]
            }
            return safe_response
        
        return jres

    def identify_relevant_documents(self, primary_question, choice, relevance_threshold=0.75, model=None):
        self.log_function_call("identify_relevant_documents")
        """
        Takes a natural language phrase and a list of documents, and returns the FDA 510(k) summary documents the phrase matches with a confidence level
        Processes documents in batches to avoid API limits
        """
        # Process documents in batches - smaller for OpenAI to reduce load
        try:
            from config import LLMConfig
            current_provider = LLMConfig.DEFAULT_PROVIDER
        except:
            current_provider = "northwell"
        
        # Use smaller batches for OpenAI to reduce rate limiting
        batch_size = 400 if current_provider == "openai" else 500
        all_relevant_docs = []
        
        if self.debug > 0:
            logging.info(f"Processing {len(choice)} documents in batches of {batch_size}")
            print(f"Processing {len(choice)} documents in batches of {batch_size}")
        
        total_batches = (len(choice) + batch_size - 1) // batch_size

        def process_batch(batch, batch_num):
            if self.debug > 0:
                print(f"Processing batch {batch_num}/{total_batches} ({len(batch)} documents)")

            batch_result = self._identify_relevant_documents_batch(primary_question, batch, relevance_threshold, model)

            if 'error' in batch_result:
                if self.debug > 0:
                    error_msg = f"Error in batch {batch_num}: {batch_result['error']}"
                    logging.error(error_msg)
                    print(error_msg)
                return []

            if 'documents' in batch_result and batch_result['documents']:
                if self.debug > 0:
                    info_msg = f"Batch {batch_num}: Found {len(batch_result['documents'])} relevant documents"
                    logging.info(info_msg)
                    print(info_msg)
                return batch_result['documents']
            return []

        # Check which provider we're using to decide on concurrency
        try:
            from config import LLMConfig
            current_provider = LLMConfig.DEFAULT_PROVIDER
            multithreading_enabled = LLMConfig.is_multithreading_enabled()
            sleep_time = LLMConfig.get_rate_limit_sleep()
        except:
            current_provider = "northwell"  # fallback
            multithreading_enabled = False
            sleep_time = 15
        
        if current_provider == "openai" and not multithreading_enabled:
            # Sequential processing for OpenAI to avoid rate limits
            if self.debug > 0:
                print(f"Using sequential processing for OpenAI provider (sleep: {sleep_time}s)")
            
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
                
                # Add configurable delay between requests for OpenAI
                import time
                time.sleep(sleep_time)
        else:
            # Parallel processing for Northwell and other providers, or OpenAI with multithreading enabled
            if self.debug > 0:
                if current_provider == "openai":
                    print("Using parallel processing for OpenAI provider (multithreading enabled)")
                else:
                    print("Using parallel processing for non-OpenAI provider")
                
            with ThreadPoolExecutor(max_workers=6) as executor:
                futures = []
                for i in range(0, len(choice), batch_size):
                    batch = choice[i:i + batch_size]
                    batch_num = i // batch_size + 1
                    futures.append(executor.submit(process_batch, batch, batch_num))

                for future in futures:
                    all_relevant_docs.extend(future.result())

        # Sort all results by relevance level and return
        if all_relevant_docs:
            all_relevant_docs.sort(key=lambda x: float(x.get('relevance_level', 0)), reverse=True)
            if self.debug > 0:
                info_msg = f"Total relevant documents found: {len(all_relevant_docs)}"
                logging.info(info_msg)
                print(info_msg)
            return {
                "function": "identify_relevant_documents",
                "primary_question": primary_question,
                "documents": all_relevant_docs,  # Return all relevant documents, no artificial limit
                "total_batches": total_batches,
                "total_documents_processed": len(choice),
                "total_relevant_found": len(all_relevant_docs)
            }
        else:
            if self.debug > 0:
                logging.info("No relevant documents found")
                print("No relevant documents found")
            return {
                "function": "identify_relevant_documents", 
                "primary_question": primary_question,
                "documents": [],
                "total_batches": total_batches,
                "total_documents_processed": len(choice)
            }
    
    def _identify_relevant_documents_batch(self, primary_question, choice_batch, relevance_threshold=0.1, model=None):
        self.log_function_call("_identify_relevant_documents_batch")
        """
        Process a single batch of documents for relevance identification
        """
        # Build document list string for this batch
        doc_list = ""
        for idx, name, desc in choice_batch:
            # Extract fda_folder from the JSON content if available
            try:
                json_obj = json.loads(desc)
                fda_folder = json_obj.get('fda_folder', 'Unknown')
            except:
                fda_folder = 'Unknown'

            # Sanitize Unicode characters that might cause encoding issues
            sanitized_name = sanitize_unicode_text(name, max_length=200)
            sanitized_desc = sanitize_unicode_text(desc, max_length=500)
            doc_list += f"doc_id {idx}; name {sanitized_name}; description {sanitized_desc}\n"

        prompt_text = f"""You are an FDA clinical laboratory regulatory expert with deep knowledge of FDA 510(k) submissions and related documentation. Your task is to assess a question and identify all FDA 510(k) documents that could be relevant in addressing the inquiry. Each document should be assigned a relevance level between 0 and 1, where 1 indicates 100% confidence in its relevance, and 0 indicates complete irrelevance. Report any document with a relevance level exceeding the relevance threshold.

        CRITICAL RELEVANCE GUIDELINES:
        - For SPECIFIC device-related questions (e.g., SynCardia TAH-t, Da Vinci Surgical System), only documents pertaining to that EXACT device should have high relevance (0.8-1.0).
        - General device categories or unrelated devices should have very low relevance (0.1-0.3) even if they fall within a similar category.
        - For example, if asked about the SynCardia TAH-t, a document on another cardiac assist device should be rated 0.1-0.2 in relevance, not 0.7+.
        - Assign high relevance only if the document explicitly pertains to the specified device, test type, or regulatory procedure mentioned.
        - Generic, procedural, or unrelated matches should have lower relevance unless they directly address the specific question.
        
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
            error_msg = f'LLM invoke error in _identify_relevant_documents_batch: {e}'
            logging.error(error_msg)
            print(error_msg)
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
            error_msg = f'JSON parsing error in _identify_relevant_documents_batch: {e}'
            logging.error(error_msg)
            print(error_msg)
            print('Response: '+response)
            jres = {"error": "Failed to parse JSON response", "raw_response": response}
        
        logging.info(jres)
        return jres
    
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
            response = sanitize_unicode_text(response)
        except Exception as e:
            error_msg = f'LLM invoke error in evaluate_answer_quality: {e}'
            logging.error(error_msg)
            print(error_msg)
            return f"Error evaluating answer quality: {e}"
        if self.debug > 0:
            print(response)
        if self.debug > 2:
            print(prompt_text)
        return response

    def ask_fda(self, question, fda_summary_docs, history=None, fda_docs_mds_path='../LabDocs/fda_extracted_mds/'):
        self.log_function_call("ask_fda")
        """
        Main method to ask a question about FDA 510(k)s summary documents and get a comprehensive answer
        
        Args:
            question: The question to ask
            fda_summary_docs: List of FDA summary documents [(idx, name, description), ...]
            history: List to track conversation history (optional)
            fda_docs_mds_path: Path to the extracted md files

        Returns:
            tuple: (answer_string, updated_history)
        """
        import time
        
        if history is None:
            history = []
            
        current_time = time.time()
        start_time = current_time
        logging.info(f"Starting FDA query: {question}")
        print(f"Starting time: {current_time}")
        
        try:
            enhancement_result = self.enhance_query_with_llm(question)
            enhanced_question = enhancement_result['enhanced_question']
            exhaustive = enhancement_result['exhaustive']
            logging.info(f"Enhanced question: {enhanced_question}")
            logging.info(f"Exhaustive search: {exhaustive}")
            print(f"Enhanced question: {enhanced_question}")
            print(f"Exhaustive search: {exhaustive}")
        except Exception as e:
            error_msg = f"Error in enhance_query_with_llm: {e}"
            logging.error(error_msg)
            print(error_msg)
            enhanced_question = question
            exhaustive = False

        current_time = time.time()
        print(f"Time after enhancing question: {current_time} (Elapsed: {current_time - start_time:.2f}s)")

        
        try:
            documents = self.identify_relevant_documents(enhanced_question, fda_summary_docs)
        except Exception as e:
            error_msg = f"Error in identify_relevant_documents: {e}"
            logging.error(error_msg)
            print(error_msg)
            return f"Error identifying relevant documents: {e}", history

        current_time = time.time()
        print(f"Time after identifying relevant documents: {current_time} (Elapsed: {current_time - start_time:.2f}s)")
            
        doc_excerpts = []
        
        # Check if we got a valid response with documents
        if 'error' in documents:
            error_msg = f"Error identifying relevant documents: {documents['error']}"
            logging.error(error_msg)
            return error_msg, history
        
        if 'documents' not in documents:
            error_msg = f"No documents key found in response. Response: {documents}"
            logging.error(error_msg)
            return error_msg, history
        
        # Check if no relevant documents were found
        if not documents['documents'] or len(documents['documents']) == 0:
            no_answer_response = (
                f"I'm sorry, but I couldn't find any relevant information in the available FDA documents "
                f"to answer your question: '{question}'. "
                f"The current FDA document database contains {len(fda_summary_docs)} document(s), but none appear to be "
                f"relevant to your query. You may want to:\n"
                f"1. Rephrase your question with different terminology\n"
                f"2. Check if there are additional FDA documents that should be loaded\n"
                f"3. Verify that your question relates to laboratory procedures covered by the FDA documents"
            )
            logging.info(f"No relevant documents found for question: {question}")
            history.append(no_answer_response)
            return no_answer_response, history
        
        # Limit to top 5 most relevant documents for performance (unless exhaustive search is needed)
        documents_to_process = documents['documents']
        total_relevant_docs = len(documents_to_process)
        
        # Validate document IDs before processing
        valid_documents = []
        for doc in documents_to_process:
            try:
                doc_id = int(doc['doc_id'])
                if 0 <= doc_id < len(fda_summary_docs):
                    valid_documents.append(doc)
                else:
                    if self.debug > 0:
                        logging.warning(f"Invalid doc_id {doc_id} found in document list, skipping. Valid range: 0-{len(fda_summary_docs)-1}")
            except (ValueError, KeyError) as e:
                if self.debug > 0:
                    logging.warning(f"Invalid document entry {doc}: {e}")
        
        documents_to_process = valid_documents
        if len(valid_documents) != total_relevant_docs:
            logging.info(f"Filtered out {total_relevant_docs - len(valid_documents)} invalid document references")
            total_relevant_docs = len(valid_documents)
        
        if not exhaustive and total_relevant_docs > 5:
            documents_to_process = documents_to_process[:5]  # They're already sorted by relevance in identify_relevant_documents
            logging.info(f"Performance optimization: Processing top 5 out of {total_relevant_docs} relevant documents (non-exhaustive search)")
            print(f"Performance optimization: Processing top 5 out of {total_relevant_docs} relevant documents (non-exhaustive search)")
        elif exhaustive:
            logging.info(f"Exhaustive search: Processing all {total_relevant_docs} relevant documents")
            print(f"Exhaustive search: Processing all {total_relevant_docs} relevant documents")
        else:
            logging.info(f"Processing all {total_relevant_docs} relevant documents")
            print(f"Processing all {total_relevant_docs} relevant documents")
        
        # Check if we have any valid documents to process after filtering
        if not documents_to_process:
            no_valid_docs_response = (
                f"I'm sorry, but while I found some potentially relevant documents for your question '{question}', "
                f"there were issues with the document references that prevented processing them. "
                f"This might be a temporary system issue. Please try rephrasing your question or try again later."
            )
            logging.warning(f"No valid documents to process after filtering for question: {question}")
            return no_valid_docs_response, history
        
        # print the contents of documents
        # if self.debug > 0:
        #     print(f"Identified {len(documents['documents'])} relevant documents:")
        #     for doc in documents['documents']:
        #         print(doc)
        try:
            def process_document(document):
                try:
                    doc_id = int(document['doc_id'])
                    if doc_id < 0 or doc_id >= len(fda_summary_docs):
                        if self.debug > 0:
                            logging.warning(f"Invalid doc_id {doc_id}, skipping document. Valid range: 0-{len(fda_summary_docs)-1}")
                        return None
                    fda_summary_idx, fda_summary_name, fda_summary_content = fda_summary_docs[doc_id]
                except (ValueError, IndexError, KeyError) as e:
                    if self.debug > 0:
                        logging.error(f"Error processing document {document}: {e}")
                    return None
                
                # get the fda_folder from the document
                fda_folder = None
                if 'fda_folder' in document:
                    fda_folder = document['fda_folder']
                else:
                    try:
                        json_content = json.loads(fda_summary_content)
                        fda_folder = json_content.get('fda_folder', None)
                    except Exception as json_error:
                        if self.debug > 0:
                            logging.error(f"Failed to parse JSON content: {json_error}")
                
                # If no fda_folder found, use the summary content directly
                if not fda_folder:
                    if self.debug > 0:
                        logging.info(f"No fda_folder found for {fda_summary_name}, using summary content directly")
                    doc_excerpt = self.find_document_excerpts(enhanced_question, fda_summary_content, fda_summary_name.replace('_es1.json', ''))
                    return json.dumps(doc_excerpt)

                # Convert .json filename to .md and remove _es1 suffix
                md_filename = fda_summary_name.replace('.json', '.md').replace('_es1', '')
                md_path = f'{fda_docs_mds_path}/{fda_folder}/{md_filename}'
                
                try:
                    with open(md_path, 'r', encoding='utf-8') as file:
                        fda_content = file.read()
                    if self.debug > 0:
                        logging.info(f"Successfully read MD file for {fda_summary_name}, content length: {len(fda_content)}")
                except UnicodeDecodeError:
                    # Fallback to different encodings if UTF-8 fails
                    try:
                        with open(md_path, 'r', encoding='latin-1') as file:
                            fda_content = file.read()
                        if self.debug > 0:
                            logging.info(f"Read MD file with latin-1 encoding for {fda_summary_name}")
                    except UnicodeDecodeError:
                        try:
                            with open(md_path, 'r', encoding='cp1252') as file:
                                fda_content = file.read()
                            if self.debug > 0:
                                logging.info(f"Read MD file with cp1252 encoding for {fda_summary_name}")
                        except UnicodeDecodeError as unicode_error:
                            if self.debug > 0:
                                logging.error(f"Unicode error reading MD file: {unicode_error}, using summary content instead")
                            fda_content = fda_summary_content
                except FileNotFoundError:
                    if self.debug > 0:
                        logging.warning(f"MD file not found at {md_path}, using summary content instead")
                    fda_content = fda_summary_content
                except Exception as file_error:
                    if self.debug > 0:
                        logging.error(f"Error reading MD file: {file_error}, using summary content instead")
                    fda_content = fda_summary_content

                # This LLM call will now run in parallel across different threads
                doc_excerpt = self.find_document_excerpts(enhanced_question, fda_content, fda_summary_name.replace('_es1.json', ''))
                return json.dumps(doc_excerpt)

            # Check configuration for multithreading
            try:
                from config import LLMConfig
                current_provider = LLMConfig.DEFAULT_PROVIDER
                multithreading_enabled = LLMConfig.is_multithreading_enabled()
                sleep_time = LLMConfig.get_rate_limit_sleep()
            except:
                current_provider = "northwell"
                multithreading_enabled = False
                sleep_time = 15
            
            if current_provider == "openai" and not multithreading_enabled:
                # Sequential processing for OpenAI to avoid rate limits
                if self.debug > 0:
                    print(f"Processing documents sequentially for OpenAI (sleep: {sleep_time}s)")
                
                for i, document in enumerate(documents_to_process):
                    doc_excerpt = process_document(document)
                    if doc_excerpt is not None:  # Only process non-None results
                        doc_excerpts.append(doc_excerpt)
                        history.append(doc_excerpt)
                    
                    # Add delay between document processing for OpenAI
                    if i < len(documents_to_process) - 1:  # Don't sleep after the last document
                        import time
                        time.sleep(sleep_time)
            else:
                # Use ThreadPoolExecutor to parallelize document processing
                if self.debug > 0:
                    if current_provider == "openai":
                        print("Processing documents in parallel for OpenAI (multithreading enabled)")
                    else:
                        print("Processing documents in parallel for non-OpenAI provider")
                
                with ThreadPoolExecutor(max_workers=6) as executor:
                    futures = [executor.submit(process_document, document) for document in documents_to_process]
                    for future in futures:
                        doc_excerpt = future.result()
                        if doc_excerpt is not None:  # Only process non-None results
                            doc_excerpts.append(doc_excerpt)
                            history.append(doc_excerpt)
        except Exception as e:
            error_msg = f"Error in find_document_excerpts: {e}"
            logging.error(error_msg)
            print(error_msg)
            if self.debug > 0:
                import traceback
                full_trace = f"Full traceback: {traceback.format_exc()}"
                logging.error(full_trace)
                print(full_trace)
            return f"Error processing documents: {e}", history

        current_time = time.time()
        print(f"Time after finding document excerpts: {current_time} (Elapsed: {current_time - start_time:.2f}s)")
        
        try:
            if len(documents_to_process) > 1:
                synthesized_results = self.synthesize_multiple_sources(enhanced_question, doc_excerpts)
                history.append(json.dumps(synthesized_results))
            else:
                synthesized_results = doc_excerpts
        except Exception as e:
            error_msg = f"Error in synthesize_multiple_sources: {e}"
            logging.error(error_msg)
            print(error_msg)
            synthesized_results = doc_excerpts

        current_time = time.time()
        print(f"Time after synthesizing sources: {current_time} (Elapsed: {current_time - start_time:.2f}s)")
        
        try:
            pretty_result = self.make_llm_pretty(enhanced_question, synthesized_results)
            history.append(pretty_result)
            current_time = time.time()
            print(f"Time after making llm pretty: {current_time} (Elapsed: {current_time - start_time:.2f}s)")

            # pass original Q and pretty result, have LLM judge if good answer. If not, say "we are not satisfied with the results, would you like to rephrase the question etc?"
            logging.info("Evaluating answer quality...")
            print("Evaluating answer quality...")

            evaluation = self.evaluate_answer_quality(enhanced_question, pretty_result)
            history.append(evaluation)

            current_time = time.time()
            print(f"Time after evaluating answer quality: {current_time} (Elapsed: {current_time - start_time:.2f}s)")

            #if the evaluation indicates poor quality, return a message instead of the answer
            if "not satisfied" in evaluation.lower():
                unsat_response = (
                    f"I'm sorry, but the information retrieved from the FDA summary documents does not adequately answer your question: '{question}'. "
                    f"You may want to:\n"
                    f"1. Rephrase your question with different terminology\n"
                    f"2. Check if there are additional FDA summary documents that should be loaded\n"
                    f"3. Verify that your question relates to laboratory procedures or devices covered by the FDA summary documents"
                )
                logging.info(f"Answer quality unsatisfactory for question: {question}")
                return unsat_response
            else:
                logging.info("Answer quality satisfactory, proceeding to format the answer.")
                print("Answer quality satisfactory, proceeding to format the answer.")

            end_time = time.time()
            total_time = end_time - start_time
            logging.info(f"ask_fda completed in {total_time:.2f} seconds")
            return pretty_result, history
        except Exception as e:
            error_msg = f"Error in make_llm_pretty: {e}"
            logging.error(error_msg)
            print(error_msg)
            return f"Error formatting final result: {e}", history