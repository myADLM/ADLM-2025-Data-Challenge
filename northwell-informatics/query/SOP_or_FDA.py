import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'modules'))
from llm import LLM
import json
import inspect

class SOP_FDA:
    def __init__(self, model="o3", debug=0):
        self.model = model
        self.debug = debug
        self.llm = LLM(model=model)

    def enhance_query_with_llm(self, question, model=None):
        """
        Use LLM to understand the question better before deciding which doc types to search
        
        Args:
            question: User's question
            
        Returns:
            Dictionary with enhanced query information
        """
        prompt_text = f"""
        You are a laboratory assistant analyzing a question about Laboratory Documents. There are several types of documents: Standard Operating Procedures (SOPs), FDA 501(k) Summary Documents,
        and FDA 510(k) SUBSTANTIAL EQUIVALENCE DETERMINATION DECISION SUMMARY Documents

        QUESTION TO ANALYZE: "{question}"
        
        Your task is to understand what the user is asking about using your general laboratory knowledge, 
        then identify the best search terms to find that information in the laboratory document data.
        In addition Rephrase this question to be more specific and searchable within laboratory test documentation, using your laboratory knowledge to expand abbreviations and clarify intent.
        You may use general knowledge to UNDERSTAND and re-word the question 
        (e.g., A1C = Hemoglobin A1C, QC means quality control)
        
        Return only the improved question, nothing else.
        
        Examples:
        - "What is the reference range for A1C?" → "What are the reference ranges and normal values for Hemoglobin A1C testing?
        - "How do I collect the specimen?" → "What are the specimen collection procedures and requirements?"
        - "What QC do I need?" → "What quality control procedures and requirements are specified?"
        - "Can i test for pregnancy?" -> "What are the Lab Tests I can order that will determine if i am pregnant?
        """
        llm = LLM(model=model or self.model)
        try:
            response = llm.invoke(prompt_text)
        except Exception as e:
            print(f'LLM invoke error in enhance_query_with_llm: {e}')
            return question  # Return original question as fallback
            
        if self.debug > 0:
            print(response)
        if self.debug > 2:
            print(prompt_text)
        return response

    def identify_relevant_document_types(self, primary_question, model=None):
        """
        Takes a question and determines the types of doucuments in the laboratory documents store that are most likely to be relevant to answering that question
        """
        prompt_text = f"""
        You are a clinical laboratory expert. You need to apply your expertise in evaluating a question and identifying the types of laboratory documents that are relevant
        in answering the question. You make a determination of relevance for each document type; the relevance is either yes or no.
        There are 3 laboratory document types:  Standard Operating Procedures (SOPs), FDA 501(k) Summary Documents, and FDA 510(k) SUBSTANTIAL EQUIVALENCE DETERMINATION DECISION SUMMARY Documents
        The Standard Operating Procedures (SOPs) are detailed documents that describe the procedures and protocols for performing laboratory tests.
        An FDA 510(k) is a submission to the FDA to market a new medical device, such as a laboratory test.
        The FDA 501(k) Summary Documents are shorter summaries of the test being submitted and a letter to the submitter about whether the FDA has cleared the test for marketing.
        The 510(k) SUBSTANTIAL EQUIVALENCE DETERMINATION DECISION SUMMARY Documents are detailed documents that describe the FDA's decision on whether the new test is substantially equivalent to an existing test.
        NOTE: some questions may be relevant to more than one document type. You can include all 3, none, or any combination of the document types in your determination
        ---------
        Primary question: {primary_question}
        ---------
        Examples:
        
        ---------
        Guidelines:
        1) Evaluate the potential relevance of each document type against the question
        2) Return 1 line per document type in the following format; enclose property name and value with double quotes and escape double quotes with "\\"
        "document_type":"value", "relevance":"value" 
        """
        
        llm = LLM(model=model or self.model)
        llm_response = llm(prompt_text)

        response = ' {"function":"' + inspect.stack()[0][3] + '","primary_question":"'+primary_question+'","document_types":['
        response_lines = []
        for line in llm_response.splitlines():
            if line.strip():  # Only add non-empty lines
                response_lines.append('{' + line + '}')
        
        if response_lines:
            response = response + ','.join(response_lines) + ']}'
        else:
            response = response + ']}'

        if self.debug > 0:
            print(llm_response)
        if self.debug > 2:
            print(prompt_text)
        try:
            jres = json.loads(response)
        except Exception as e:
            print(f'JSON parsing error in identify_relevant_documents: {e}')
            print('Response: '+response)
            jres = {"error": "Failed to parse JSON response", "raw_response": response}
        return jres

    def make_determination(self, question):
        """
        Main method to determine which document types are relevant to a question
        
        Args:
            question: The question to ask
            
        Returns:
            document types
        """
        import time
            
        current_time = time.time()
        start_time = current_time
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
            document_types = self.identify_relevant_document_types(enhanced_question)
        except Exception as e:
            print(f"Error in identify_relevant_document_types: {e}")
            return f"Error identifying relevant document types: {e}"

        current_time = time.time()
        print(f"Time after identifying relevant document types: {current_time} (Elapsed: {current_time - start_time:.2f}s)")

        return document_types

        
    
        