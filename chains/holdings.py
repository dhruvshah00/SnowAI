from chains.base_text_to_sql_manager import BaseTextToSqlManager

class Holdings(BaseTextToSqlManager):
    def __init__(self, sql_schema_path="sql_schema/holdings.txt"):
        super().__init__(sql_schema_path)
    
    def get_chain(self):
        return self.build_chains()