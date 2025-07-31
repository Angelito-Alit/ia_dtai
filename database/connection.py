import mysql.connector
from mysql.connector import pooling
import os
import logging
from contextlib import contextmanager

logger = logging.getLogger(__name__)

class DatabaseConnection:
    def __init__(self):
        self.config = {
            'host': os.getenv('DB_HOST', 'bluebyte.space'),
            'user': os.getenv('DB_USER', 'bluebyte_angel'),
            'password': os.getenv('DB_PASSWORD', 'orbitalsoft'),
            'database': os.getenv('DB_NAME', 'bluebyte_dtai_web'),
            'port': int(os.getenv('DB_PORT', 3306)),
            'charset': 'utf8mb4',
            'use_unicode': True,
            'autocommit': True
        }
        
        self.pool_config = {
            'pool_name': 'ai_pool',
            'pool_size': 5,
            'pool_reset_session': True,
            **self.config
        }
        
        self._pool = None
        self._initialize_pool()
    
    def _initialize_pool(self):
        """Inicializar pool de conexiones"""
        try:
            self._pool = pooling.MySQLConnectionPool(**self.pool_config)
            logger.info("Pool de conexiones inicializado")
        except Exception as e:
            logger.error(f"Error inicializando pool: {e}")
            raise
    
    @contextmanager
    def get_connection(self):
        """Context manager para obtener conexión del pool"""
        connection = None
        try:
            connection = self._pool.get_connection()
            yield connection
        except Exception as e:
            logger.error(f"Error de conexión: {e}")
            raise
        finally:
            if connection and connection.is_connected():
                connection.close()
    
    def execute_query(self, query, params=None, fetch_all=True):
        """Ejecutar consulta SELECT"""
        try:
            with self.get_connection() as connection:
                cursor = connection.cursor(dictionary=True)
                cursor.execute(query, params)
                
                if fetch_all:
                    result = cursor.fetchall()
                else:
                    result = cursor.fetchone()
                
                cursor.close()
                return result
                
        except Exception as e:
            logger.error(f"Error ejecutando query: {e}")
            logger.error(f"Query: {query}")
            logger.error(f"Params: {params}")
            raise
    
    def execute_insert(self, query, params=None):
        """Ejecutar consulta INSERT"""
        try:
            with self.get_connection() as connection:
                cursor = connection.cursor()
                cursor.execute(query, params)
                connection.commit()
                
                last_id = cursor.lastrowid
                cursor.close()
                return last_id
                
        except Exception as e:
            logger.error(f"Error en INSERT: {e}")
            raise
    
    def execute_update(self, query, params=None):
        """Ejecutar consulta UPDATE"""
        try:
            with self.get_connection() as connection:
                cursor = connection.cursor()
                cursor.execute(query, params)
                connection.commit()
                
                affected_rows = cursor.rowcount
                cursor.close()
                return affected_rows
                
        except Exception as e:
            logger.error(f"Error en UPDATE: {e}")
            raise
    
    def get_table_schema(self, table_name):
        """Obtener esquema de una tabla"""
        query = """
        SELECT 
            COLUMN_NAME,
            DATA_TYPE,
            IS_NULLABLE,
            COLUMN_DEFAULT,
            COLUMN_COMMENT
        FROM INFORMATION_SCHEMA.COLUMNS
        WHERE TABLE_SCHEMA = %s AND TABLE_NAME = %s
        ORDER BY ORDINAL_POSITION
        """
        
        return self.execute_query(query, (self.config['database'], table_name))
    
    def get_all_tables(self):
        """Obtener lista de todas las tablas"""
        query = """
        SELECT TABLE_NAME, TABLE_COMMENT
        FROM INFORMATION_SCHEMA.TABLES
        WHERE TABLE_SCHEMA = %s
        ORDER BY TABLE_NAME
        """
        
        return self.execute_query(query, (self.config['database'],))
    
    def get_table_relationships(self):
        """Obtener relaciones entre tablas (foreign keys)"""
        query = """
        SELECT 
            kcu.TABLE_NAME,
            kcu.COLUMN_NAME,
            kcu.REFERENCED_TABLE_NAME,
            kcu.REFERENCED_COLUMN_NAME,
            rc.UPDATE_RULE,
            rc.DELETE_RULE
        FROM INFORMATION_SCHEMA.KEY_COLUMN_USAGE kcu
        JOIN INFORMATION_SCHEMA.REFERENTIAL_CONSTRAINTS rc 
            ON kcu.CONSTRAINT_NAME = rc.CONSTRAINT_NAME
        WHERE kcu.TABLE_SCHEMA = %s
            AND kcu.REFERENCED_TABLE_NAME IS NOT NULL
        ORDER BY kcu.TABLE_NAME, kcu.COLUMN_NAME
        """
        
        return self.execute_query(query, (self.config['database'],))
    
    def test_connection(self):
        """Probar conexión a la base de datos"""
        try:
            with self.get_connection() as connection:
                cursor = connection.cursor()
                cursor.execute("SELECT 1")
                result = cursor.fetchone()
                cursor.close()
                
                logger.info("Conexión a la base de datos exitosa")
                return True
                
        except Exception as e:
            logger.error(f"Error probando conexión: {e}")
            return False