from langchain.prompts import ChatPromptTemplate

class TextToSqlPrompts:
    
    sql_query_template = """"Given an input question and chat history between Human and Assistant, first create a syntactically correct snowflake sql query to run, then look at the results of the query and return the answer. 
        Provide maximum weightage to input question and use chat history to understand the background context.
        You can order the results by a relevant column to return the most interesting examples in the database.

        Do not select all columns return only the relevant and requested columns.
        
        Pay attention to use only the column names that you can see in the schema description.
        
        For any agrregation prefer using group by clauses. You can also use nested queries when required and do not forget to qualify column names in select.
        Select only non-null values while running top N queries.
        Only use the tables listed below.
        {schema}

        Question: {question}
        Chat History: {chat_history}
        
        Return only the sql query as text without any markdown.
        Use the following format:
        <SQLQuery>
        """        
    sql_query_prompt = ChatPromptTemplate.from_template(sql_query_template)


    response_template = """Given an input question and chat history, synthesize a response from the query results. 
    Generate a response in tabular format with user friendly column names. 
    Format number as comma seperator values upto 2 decimals.
    Format Percentage columns by appending (%) sign to values.
    If requested then include markdown of sql query in response.

    In case the SQL Response is empty then let user know that there no matching results for the input question.

    Question: {question}
    Chat History: {chat_history}
    SQL Query: {query}
    SQL Response: {response}"""    
    response_prompt = ChatPromptTemplate.from_template(response_template)
    

    error_template = """Below conversation ran into an error either while preparing the query or executing the query.

    Provide a brief message regarding the error. Include markdown of sql query in the response.
    
    Conversation: {chat_history}
    SQL Query: {query}
    Response:"""
    error_prompt = ChatPromptTemplate.from_template(error_template)

    
    classification_template = """Given the user question below, classify it as either being about `TextToSql` or `SchemaDetails`.
    Do not respond with more than one word.

    `TextToSql` - If user is asking for data that can be provided by converting the input question to sql query and then running the query on the database.
    `SchemaDetails` - If user is asking about the schema details or general help on how to build the right prompt to pull the data

    Question: {question}

    Classification:"""
    classification_prompt = ChatPromptTemplate.from_template(classification_template)


    schema_details_template = """Help user answer the below question based on the schema mentioned below.
    Your job is either share the details based on the schema OR help user write a concise just text prompt that helps user effectively pull the required data.

    Ensure the responses is always grounded in the schema and never return a sql statement. 

    Question: {question}
    
    Schema: {schema}

    Response:"""
    schema_details_prompt = ChatPromptTemplate.from_template(schema_details_template)

