import os
import mysql.connector
import logging
from typing import Optional, Dict, Any, List

logger = logging.getLogger(__name__)

class DatabaseConnection:
    def __init__(self):
        self.config = {
            'host': os.environ.get('DB_HOST', 'bluebyte.space'),
            'user': os.environ.get('DB_USER', 'bluebyte_angel'),
            'password': os.environ.get('DB_PASSWORD', 'orbitalsoft'),
            'database': os.environ.get('DB_NAME', 'bluebyte_dtai_web'),
            'port': int(os.environ.get('DB_PORT', 3306)),
            'charset': 'utf8mb4',
            'autocommit': True
        }
        self._connection = None
    
    def connect(self) -> Optional[mysql.connector.MySQLConnection]:
        try:
            self._connection = mysql.connector.connect(**self.config)
            logger.info("Conexión a BD exitosa")
            return self._connection
        except Exception as e:
            logger.error(f"Error BD: {e}")
            return None
    
    def execute_query(self, query: str, params: Optional[list] = None) -> Optional[List[Dict[str, Any]]]:
        connection = self.connect()
        if not connection:
            return None
        
        try:
            cursor = connection.cursor(dictionary=True)
            cursor.execute(query, params or [])
            result = cursor.fetchall()
            cursor.close()
            connection.close()
            logger.info(f"Query ejecutada: {len(result)} filas")
            return result
        except Exception as e:
            logger.error(f"Error query: {e}")
            if connection:
                connection.close()
            return None
    
    def execute_single_query(self, query: str, params: Optional[list] = None) -> Optional[Dict[str, Any]]:
        result = self.execute_query(query, params)
        return result[0] if result else None
    
    def test_connection(self) -> bool:
        try:
            result = self.execute_query("SELECT 1 as test, NOW() as tiempo")
            return result is not None
        except:
            return False