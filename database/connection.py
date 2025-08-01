import os
import logging
import mysql.connector

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
    
    def get_connection(self):
        try:
            connection = mysql.connector.connect(**self.config)
            logger.info("Conexion a BD exitosa")
            return connection
        except Exception as e:
            logger.error(f"Error BD: {e}")
            return None
    
    def execute_query(self, query, params=None):
        connection = self.get_connection()
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
    
    def execute_single_query(self, query, params=None):
        connection = self.get_connection()
        if not connection:
            return None
        
        try:
            cursor = connection.cursor(dictionary=True)
            cursor.execute(query, params or [])
            result = cursor.fetchone()
            cursor.close()
            connection.close()
            return result
        except Exception as e:
            logger.error(f"Error query single: {e}")
            if connection:
                connection.close()
            return None