import logging
import time
from datetime import datetime, timedelta
import pandas as pd
from typing import List, Dict, Any, Optional

logger = logging.getLogger(__name__)

class QueryExecutor:
    def __init__(self, db_connection):
        self.db = db_connection
        self.query_cache = {}
        self.cache_ttl = 300  
        self.execution_stats = {
            'total_queries': 0,
            'avg_execution_time': 0,
            'cache_hits': 0,
            'errors': 0
        }
    
    def execute_query(self, query: str, params: List = None, use_cache: bool = True) -> Dict[str, Any]:
        start_time = time.time()
        
        try:
            if not self._is_safe_query(query):
                raise ValueError("Consulta no segura detectada")
            
            cache_key = self._generate_cache_key(query, params)
            if use_cache and cache_key in self.query_cache:
                cached_result = self.query_cache[cache_key]
                if self._is_cache_valid(cached_result['timestamp']):
                    self.execution_stats['cache_hits'] += 1
                    logger.info(f"Cache hit para consulta: {query[:50]}...")
                    return {
                        'success': True,
                        'data': cached_result['data'],
                        'cached': True,
                        'execution_time': 0,
                        'row_count': len(cached_result['data']) if cached_result['data'] else 0
                    }
            logger.info(f"Ejecutando consulta: {query[:100]}...")
            result = self.db.execute_query(query, params)
            
            execution_time = time.time() - start_time
            self._update_stats(execution_time)
            if use_cache:
                self.query_cache[cache_key] = {
                    'data': result,
                    'timestamp': datetime.now()
                }
                self._cleanup_cache()
            processed_result = self._process_result(result)
            
            logger.info(f"Consulta ejecutada exitosamente en {execution_time:.2f}s - {len(result) if result else 0} filas")
            
            return {
                'success': True,
                'data': processed_result,
                'cached': False,
                'execution_time': execution_time,
                'row_count': len(result) if result else 0,
                'query_hash': cache_key
            }
            
        except Exception as e:
            execution_time = time.time() - start_time
            self.execution_stats['errors'] += 1
            
            logger.error(f"Error ejecutando consulta: {e}")
            logger.error(f"Query: {query}")
            logger.error(f"Params: {params}")
            
            return {
                'success': False,
                'error': str(e),
                'execution_time': execution_time,
                'row_count': 0
            }
    
    def execute_batch_queries(self, queries: List[Dict]) -> List[Dict]:
        results = []
        
        for i, query_info in enumerate(queries):
            logger.info(f"Ejecutando consulta {i+1}/{len(queries)}")
            
            result = self.execute_query(
                query_info['query'],
                query_info.get('params'),
                query_info.get('use_cache', True)
            )
            
            results.append({
                'query_index': i,
                'query_name': query_info.get('name', f'query_{i}'),
                **result
            })
        
        return results
    
    def _is_safe_query(self, query: str) -> bool:
        query_upper = query.upper().strip()
        if not query_upper.startswith('SELECT'):
            return False
        dangerous_keywords = [
            'DROP', 'DELETE', 'INSERT', 'UPDATE', 'ALTER', 'CREATE',
            'TRUNCATE', 'EXEC', 'EXECUTE', 'MERGE', 'CALL', 'REPLACE',
            'LOAD_FILE', 'INTO OUTFILE', 'INTO DUMPFILE'
        ]
        
        for keyword in dangerous_keywords:
            if keyword in query_upper:
                logger.warning(f"Consulta rechazada por contener: {keyword}")
                return False
        sql_injection_patterns = [
            '--', '/*', '*/', 'xp_', 'sp_', 'UNION SELECT',
            'OR 1=1', 'AND 1=1', "' OR '", '" OR "'
        ]
        
        for pattern in sql_injection_patterns:
            if pattern.upper() in query_upper:
                logger.warning(f"Posible inyección SQL detectada: {pattern}")
                return False
        
        return True
    
    def _generate_cache_key(self, query: str, params: List = None) -> str:
        import hashlib
        normalized_query = ' '.join(query.split())
        cache_string = normalized_query
        if params:
            cache_string += str(params)
        
        return hashlib.md5(cache_string.encode()).hexdigest()
    
    def _is_cache_valid(self, timestamp: datetime) -> bool:
        return (datetime.now() - timestamp).seconds < self.cache_ttl
    
    def _cleanup_cache(self):
        current_time = datetime.now()
        expired_keys = []
        
        for key, value in self.query_cache.items():
            if (current_time - value['timestamp']).seconds > self.cache_ttl:
                expired_keys.append(key)
        
        for key in expired_keys:
            del self.query_cache[key]
        if len(self.query_cache) > 100:
            sorted_cache = sorted(
                self.query_cache.items(),
                key=lambda x: x[1]['timestamp']
            )
            
            for key, _ in sorted_cache[:20]: 
                del self.query_cache[key]
    
    def _process_result(self, result: List[Dict]) -> List[Dict]:
        if not result:
            return []
        
        processed = []
        
        for row in result:
            processed_row = {}
            
            for key, value in row.items():
                if hasattr(value, 'decimal'):
                    processed_row[key] = float(value)
                elif isinstance(value, datetime):
                    processed_row[key] = value.isoformat()
                elif value is None and key in ['observaciones', 'descripcion', 'comentario']:
                    processed_row[key] = ''
                else:
                    processed_row[key] = value
            
            processed.append(processed_row)
        
        return processed
    
    def _update_stats(self, execution_time: float):
        self.execution_stats['total_queries'] += 1
        total_time = (self.execution_stats['avg_execution_time'] * 
                     (self.execution_stats['total_queries'] - 1) + execution_time)
        self.execution_stats['avg_execution_time'] = total_time / self.execution_stats['total_queries']
    
    def get_stats(self) -> Dict[str, Any]:
        cache_hit_rate = 0
        if self.execution_stats['total_queries'] > 0:
            cache_hit_rate = (self.execution_stats['cache_hits'] / 
                            self.execution_stats['total_queries']) * 100
        
        return {
            **self.execution_stats,
            'cache_hit_rate': round(cache_hit_rate, 2),
            'cache_size': len(self.query_cache),
            'cache_ttl_minutes': self.cache_ttl / 60
        }
    
    def clear_cache(self):
        self.query_cache.clear()
        logger.info("Cache limpiado")
    
    def execute_analytical_query(self, query: str, params: List = None) -> Dict[str, Any]:
        result = self.execute_query(query, params)
        
        if not result['success'] or not result['data']:
            return result
        try:
            df = pd.DataFrame(result['data'])
            analysis = {
                'row_count': len(df),
                'column_count': len(df.columns),
                'columns': list(df.columns),
                'data_types': df.dtypes.to_dict(),
                'summary_stats': {}
            }
            numeric_columns = df.select_dtypes(include=['number']).columns
            for col in numeric_columns:
                analysis['summary_stats'][col] = {
                    'mean': float(df[col].mean()) if not df[col].empty else 0,
                    'median': float(df[col].median()) if not df[col].empty else 0,
                    'min': float(df[col].min()) if not df[col].empty else 0,
                    'max': float(df[col].max()) if not df[col].empty else 0,
                    'std': float(df[col].std()) if not df[col].empty else 0
                }
            result['analysis'] = analysis
            
        except Exception as e:
            logger.warning(f"Error en análisis adicional: {e}")
            result['analysis'] = None
        
        return result
    
    def test_connection(self) -> Dict[str, Any]:
        test_query = "SELECT 1 as test_connection, NOW() as current_time"
        
        result = self.execute_query(test_query, use_cache=False)
        
        if result['success']:
            return {
                'connection_status': 'OK',
                'server_time': result['data'][0]['current_time'] if result['data'] else None,
                'response_time_ms': result['execution_time'] * 1000
            }
        else:
            return {
                'connection_status': 'ERROR',
                'error': result['error'],
                'response_time_ms': result['execution_time'] * 1000
            }
    
    def get_table_info(self, table_name: str) -> Dict[str, Any]:
        queries = {
            'schema': f"""
                SELECT 
                    COLUMN_NAME,
                    DATA_TYPE,
                    IS_NULLABLE,
                    COLUMN_DEFAULT,
                    CHARACTER_MAXIMUM_LENGTH,
                    NUMERIC_PRECISION,
                    COLUMN_COMMENT
                FROM INFORMATION_SCHEMA.COLUMNS
                WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = %s
                ORDER BY ORDINAL_POSITION
            """,
            'row_count': f"SELECT COUNT(*) as total_rows FROM {table_name}",
            'indexes': f"""
                SELECT 
                    INDEX_NAME,
                    COLUMN_NAME,
                    NON_UNIQUE
                FROM INFORMATION_SCHEMA.STATISTICS
                WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = %s
                ORDER BY INDEX_NAME, SEQ_IN_INDEX
            """
        }
        
        results = {}
        
        for query_name, query in queries.items():
            if query_name in ['schema', 'indexes']:
                result = self.execute_query(query, [table_name])
            else:
                result = self.execute_query(query)
            
            results[query_name] = result['data'] if result['success'] else None
        
        return results
    
    def optimize_query(self, query: str) -> Dict[str, Any]:
        explain_query = f"EXPLAIN {query}"
        explain_result = self.execute_query(explain_query, use_cache=False)
        
        suggestions = []
        
        if explain_result['success'] and explain_result['data']:
            for row in explain_result['data']:
                if row.get('type') == 'ALL':
                    suggestions.append("Considera agregar índices para evitar table scan completo")
                if row.get('key') is None:
                    suggestions.append(f"La tabla {row.get('table')} no está usando índices")
                if row.get('rows') and int(row.get('rows')) > 10000:
                    suggestions.append("La consulta examina muchas filas, considera agregar filtros")
        
        return {
            'explain_plan': explain_result['data'] if explain_result['success'] else None,
            'suggestions': suggestions,
            'query_analysis': {
                'has_where_clause': 'WHERE' in query.upper(),
                'has_joins': any(join in query.upper() for join in ['JOIN', 'INNER', 'LEFT', 'RIGHT']),
                'has_order_by': 'ORDER BY' in query.upper(),
                'has_group_by': 'GROUP BY' in query.upper(),
                'estimated_complexity': self._estimate_query_complexity(query)
            }
        }
    
    def _estimate_query_complexity(self, query: str) -> str:
        query_upper = query.upper()
        complexity_score = 0
        if 'JOIN' in query_upper:
            complexity_score += query_upper.count('JOIN') * 2
        
        if 'SUBQUERY' in query_upper or '(SELECT' in query_upper:
            complexity_score += 3
        
        if 'GROUP BY' in query_upper:
            complexity_score += 2
        
        if 'ORDER BY' in query_upper:
            complexity_score += 1
        
        if 'HAVING' in query_upper:
            complexity_score += 2
        if complexity_score <= 2:
            return 'BAJA'
        elif complexity_score <= 5:
            return 'MEDIA'
        else:
            return 'ALTA'