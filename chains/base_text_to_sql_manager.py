import os
from utils import get_db, get_llm_azure
import time
from langchain.schema.runnable import RunnableLambda, RunnableMap
from langchain.schema.output_parser import StrOutputParser
from operator import itemgetter

from chains.text_to_sql_prompts import TextToSqlPrompts

class BaseTextToSqlManager:
    def __init__(self, sql_schema_path, sql_query_prompt = TextToSqlPrompts.sql_query_prompt
                 , response_prompt = TextToSqlPrompts.response_prompt, error_prompt = TextToSqlPrompts.error_prompt
                 , classification_prompt = TextToSqlPrompts.classification_prompt, schema_details_prompt = TextToSqlPrompts.schema_details_prompt):
        self.db = get_db()
        self.model = get_llm_azure()
        self.sql_schema_path = sql_schema_path
        self.init_prompts(sql_query_prompt, response_prompt, error_prompt, classification_prompt, schema_details_prompt)

    def init_prompts(self, sql_query_prompt, response_prompt, error_prompt, classification_prompt, schema_details_prompt):
        """Initializes prompts for SQL query generation and response formatting."""
        
        self.sql_query_prompt = sql_query_prompt
        self.response_prompt = response_prompt
        self.error_prompt = error_prompt
        self.classification_prompt = classification_prompt 
        self.schema_details_prompt = schema_details_prompt

    
    def get_schema(self,_):
        """Reads and returns the SQL schema details from a file."""
        with open(self.sql_schema_path, 'r', encoding='utf-8') as file:
            schema_details = file.read()
        return schema_details

    def run_query(self, input):
        """Executes a SQL query with retries and error handling."""
        query = input['query']
        max_attempts = 2
        for attempt in range(1, max_attempts + 1):
            try:
                results = self.db.run(query)
                return results
            except Exception as e:
                if attempt == max_attempts:
                    raise
                time.sleep(5)

        
    
    def build_chains(self):
        """Builds and returns the chain of operations for managing admin holdings."""
        
        inputs = {
            "schema": RunnableLambda(self.get_schema),
            "question": itemgetter("question"),
            "chat_history": itemgetter("chat_history"),
        }

        topic_chain = (
            RunnableMap(inputs)
            | self.classification_prompt
            | self.model
            | StrOutputParser()
        )

        schema_chain = ({
                "schema": RunnableLambda(self.get_schema),
                "question": itemgetter("question"),
                "chat_history": itemgetter("chat_history"),
            }
            | self.schema_details_prompt
            | self.model
        )
        
        
        sql_response = (
            RunnableMap(inputs)
            | self.sql_query_prompt
            | self.model.bind(stop=["\nSQLQuery:"])
            | StrOutputParser()
        )

        sql_chain = (
            RunnableMap({
                "question": itemgetter("question"),
                "query": sql_response,
                "chat_history": itemgetter("chat_history"),
            }) 
            | {
                "schema": RunnableLambda(self.get_schema),
                "question": itemgetter("question"),
                "chat_history": itemgetter("chat_history"),
                "query": itemgetter("query"),
                "response": RunnableLambda(self.run_query)  
            }
            | self.response_prompt 
            | self.model
        )

        error_inspection_chain = (
            RunnableMap({
                "question": itemgetter("question"),
                "query": sql_response,
                "chat_history": itemgetter("chat_history"),
            }) 
            | {
                "question": itemgetter("question"),
                "chat_history": itemgetter("chat_history"),
                "query": itemgetter("query"),
            } 
            | self.error_prompt 
            | self.model
        )

        def route(info):
            if "TextToSql" in info["topic"]:
                return sql_chain.with_fallbacks(fallbacks=[error_inspection_chain])
            elif "SchemaDetails" in info["topic"]:
                return schema_chain
            else:
                return schema_chain

        

        full_chain = {"topic": topic_chain, "question": lambda x: x["question"], "chat_history": lambda x: x["chat_history"]} | RunnableLambda(route)

        return full_chain
    
    