from database.connection import DatabaseConnection
from database.schema_analyzer import SchemaAnalyzer
import logging
import re

logger = logging.getLogger(__name__)

class QueryExecutor:
    def __init__(self):
        self.db = DatabaseConnection()
        self.analyzer = SchemaAnalyzer()
        self.max_results = 1000
    
    def execute_safe_query(self, query, params=None, role='alumno'):
        if not self._validate_query_safety(query, role):
            logger.warning(f"Query rejected for security: {query}")
            return None
        
        try:
            result = self.db.execute_query(query, params)
            if result and len(result) > self.max_results:
                logger.warning(f"Query returned {len(result)} results, limiting to {self.max_results}")
                return result[:self.max_results]
            return result
        except Exception as e:
            logger.error(f"Query execution error: {e}")
            return None
    
    def _validate_query_safety(self, query, role):
        query_lower = query.lower().strip()
        
        dangerous_keywords = ['drop', 'delete', 'update', 'insert', 'alter', 'create', 'truncate']
        if any(keyword in query_lower for keyword in dangerous_keywords):
            return False
        
        if not query_lower.startswith('select'):
            return False
        
        table_pattern = r'from\s+(\w+)'
        tables = re.findall(table_pattern, query_lower)
        
        for table in tables:
            if not self.analyzer.validate_table_access(table, role):
                return False
        
        return True
    
    def build_parameterized_query(self, base_query, filters=None):
        if not filters:
            return base_query, []
        
        conditions = []
        params = []
        
        for field, value in filters.items():
            if isinstance(value, list):
                placeholders = ','.join(['%s'] * len(value))
                conditions.append(f"{field} IN ({placeholders})")
                params.extend(value)
            else:
                conditions.append(f"{field} = %s")
                params.append(value)
        
        if conditions:
            if 'WHERE' in base_query.upper():
                base_query += f" AND {' AND '.join(conditions)}"
            else:
                base_query += f" WHERE {' AND '.join(conditions)}"
        
        return base_query, params
    
    def execute_count_query(self, table, conditions=None, role='alumno'):
        if not self.analyzer.validate_table_access(table, role):
            return 0
        
        query = f"SELECT COUNT(*) as total FROM {table}"
        
        if conditions:
            query += f" WHERE {' AND '.join(conditions)}"
        
        result = self.db.execute_single_query(query)
        return result['total'] if result else 0
    
    def execute_aggregation_query(self, table, field, operation='AVG', conditions=None, role='alumno'):
        if not self.analyzer.validate_table_access(table, role):
            return None
        
        valid_operations = ['AVG', 'SUM', 'COUNT', 'MIN', 'MAX']
        if operation.upper() not in valid_operations:
            return None
        
        query = f"SELECT {operation.upper()}({field}) as result FROM {table}"
        
        if conditions:
            query += f" WHERE {' AND '.join(conditions)}"
        
        result = self.db.execute_single_query(query)
        return result['result'] if result else None