from database.connection import DatabaseConnection
import logging

logger = logging.getLogger(__name__)

class SchemaAnalyzer:
    def __init__(self):
        self.db = DatabaseConnection()
    
    def get_table_schema(self, table_name):
        query = "DESCRIBE " + table_name
        return self.db.execute_query(query)
    
    def get_all_tables(self):
        query = "SHOW TABLES"
        result = self.db.execute_query(query)
        return [list(row.values())[0] for row in result] if result else []
    
    def analyze_relationships(self):
        query = """
        SELECT 
            TABLE_NAME,
            COLUMN_NAME,
            CONSTRAINT_NAME,
            REFERENCED_TABLE_NAME,
            REFERENCED_COLUMN_NAME
        FROM INFORMATION_SCHEMA.KEY_COLUMN_USAGE
        WHERE REFERENCED_TABLE_SCHEMA = DATABASE()
        AND REFERENCED_TABLE_NAME IS NOT NULL
        """
        return self.db.execute_query(query)
    
    def get_table_stats(self, table_name):
        count_query = f"SELECT COUNT(*) as total_rows FROM {table_name}"
        result = self.db.execute_single_query(count_query)
        return result['total_rows'] if result else 0
    
    def validate_table_access(self, table_name, role):
        allowed_tables = {
            'alumno': ['alumnos', 'calificaciones', 'asignaturas', 'usuarios'],
            'profesor': ['alumnos', 'calificaciones', 'asignaturas', 'grupos', 'reportes_riesgo', 'usuarios'],
            'directivo': ['alumnos', 'calificaciones', 'asignaturas', 'grupos', 'reportes_riesgo', 
                         'usuarios', 'carreras', 'solicitudes_ayuda']
        }
        
        return table_name in allowed_tables.get(role, [])
    
    def get_database_summary(self):
        tables = self.get_all_tables()
        summary = {
            'total_tables': len(tables),
            'tables': {},
            'relationships': len(self.analyze_relationships() or [])
        }
        
        for table in tables:
            summary['tables'][table] = {
                'columns': len(self.get_table_schema(table) or []),
                'rows': self.get_table_stats(table)
            }
        
        return summary