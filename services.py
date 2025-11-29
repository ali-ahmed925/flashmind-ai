import os
import json
import PyPDF2
from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_text_splitters import RecursiveCharacterTextSplitter
import time

class PDFService:
    @staticmethod
    def extract_text(filepath):
        text = ""
        with open(filepath, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            for page in reader.pages:
                text += page.extract_text() + "\n"
        return text

class AIService:
    @staticmethod
    def generate_flashcards(text, difficulty, amount):
        # Chunk text if too large
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=6000,
            chunk_overlap=400,
            length_function=len,
        )
        chunks = text_splitter.split_text(text)
        
        # Use more chunks based on amount requested
        num_chunks = min(len(chunks), max(3, amount // 5))
        context_text = "\n".join(chunks[:num_chunks])
        
        llm = ChatOpenAI(temperature=0.7, model_name="gpt-3.5-turbo-16k")
        
        template = """
        You are an expert professor creating study materials. 
        
        CRITICAL INSTRUCTION: You MUST generate EXACTLY {amount} flashcards. Not more, not less. Count them carefully.
        
        Text to study:
        {text}
        
        Difficulty level: {difficulty}
        
        Generate a diverse mix of question types:
        1. "mcq" (Multiple Choice Question) - Provide exactly 4 options
        2. "qa" (Question & Answer) - Standard flashcard
        3. "true_false" (True/False) - Statement with boolean answer
        
        IMPORTANT: Return EXACTLY {amount} flashcards as a valid JSON array.
        
        Each object MUST have these fields:
        - "id": Unique string ID (e.g., "card_1", "card_2", etc.)
        - "type": "mcq", "qa", or "true_false"
        - "question": The question text
        - "options": Array of exactly 4 strings (ONLY for "mcq", use null for others)
        - "answer": The correct answer string (for mcq, use the exact option text; for true_false use "True" or "False")
        - "explanation": A detailed 2-3 sentence explanation of why the answer is correct
        - "difficulty": "{difficulty}"
        - "category": A short topic category (2-3 words)
        
        Return ONLY the JSON array. No markdown, no code blocks, no extra text.
        """
        
        prompt = PromptTemplate(
            input_variables=["amount", "difficulty", "text"],
            template=template
        )
        
        output_parser = StrOutputParser()
        chain = prompt | llm | output_parser
        
        response = chain.invoke({"amount": amount, "difficulty": difficulty, "text": context_text})
        
        try:
            # Clean up potential markdown code blocks if the LLM ignores instructions
            cleaned_response = response.strip()
            if cleaned_response.startswith("```json"):
                cleaned_response = cleaned_response[7:]
            if cleaned_response.startswith("```"):
                cleaned_response = cleaned_response[3:]
            if cleaned_response.endswith("```"):
                cleaned_response = cleaned_response[:-3]
                
            flashcards = json.loads(cleaned_response)
            
            # CRITICAL: Validate card count
            if len(flashcards) != amount:
                print(f"WARNING: Generated {len(flashcards)} cards instead of {amount}")
                # If we got fewer cards, try to pad or retry
                if len(flashcards) < amount:
                    raise Exception(f"Only generated {len(flashcards)} cards out of {amount} requested. Please try again.")
                # If we got more, truncate
                flashcards = flashcards[:amount]
            
            return flashcards
        except json.JSONDecodeError as e:
            # Fallback or retry logic could go here
            print("Failed to decode JSON:", response)
            raise Exception(f"Failed to generate valid JSON for flashcards: {str(e)}")

class StorageService:
    DATA_DIR = 'data'
    
    @staticmethod
    def save_session(filename, flashcards):
        session_id = filename.replace('.pdf', '')
        filepath = os.path.join(StorageService.DATA_DIR, f"{session_id}.json")
        with open(filepath, 'w') as f:
            json.dump(flashcards, f)
            
    @staticmethod
    def get_session(filename):
        session_id = filename.replace('.pdf', '')
        filepath = os.path.join(StorageService.DATA_DIR, f"{session_id}.json")
        if os.path.exists(filepath):
            with open(filepath, 'r') as f:
                return json.load(f)
        return []
