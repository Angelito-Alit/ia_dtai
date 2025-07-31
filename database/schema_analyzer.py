import logging
from typing import Dict, List, Any, Optional
import json
from datetime import datetime

logger = logging.getLogger(__name__)

class SchemaAnalyzer:
    def __init__(self, db_connection):
        self.db = db_connection
        self.schema_cache = None
        self.last_analysis = None
        self.table_relationships = {}
        self.entity_mappings = {}
        
    def analyze_complete_schema(self) -> Dict[str, Any]:
        logger.info("Iniciando análisis completo del esquema")
        
        try:
            tables_info = self._get_tables_info()
            columns_info = self._get_columns_info()
            relationships = self._get_relationships()
            indexes = self._get_indexes_info()
            entity_analysis = self._analyze_entities(tables_info, columns_info)
            relationship_graph = self._build_relationship_graph(relationships)
            ai_mappings = self._generate_ai_mappings(tables_info, columns_info, relationships)
            
            schema_analysis = {
                'database_info': self._get_database_info(),
                'tables': tables_info,
                'columns': columns_info,
                'relationships': relationships,
                'indexes': indexes,
                'entity_analysis': entity_analysis,
                'relationship_graph': relationship_graph,
                'ai_mappings': ai_mappings,
                'analysis_timestamp': datetime.now().isoformat(),
                'schema_stats': self._calculate_schema_stats(tables_info, columns_info)
            }
            
            self.schema_cache = schema_analysis
            self.last_analysis = datetime.now()
            
            logger.info(f"Análisis completado: {len(tables_info)} tablas analizadas")
            return schema_analysis
            
        except Exception as e:
            logger.error(f"Error en análisis de esquema: {e}")
            raise
    
    def _get_database_info(self) -> Dict[str, Any]:
        queries = {
            'version': "SELECT VERSION() as mysql_version",
            'charset': "SELECT DEFAULT_CHARACTER_SET_NAME, DEFAULT_COLLATION_NAME FROM information_schema.SCHEMATA WHERE SCHEMA_NAME = DATABASE()",
            'size': """
                SELECT 
                    ROUND(SUM(data_length + index_length) / 1024 / 1024, 2) AS db_size_mb,
                    COUNT(*) as total_tables
                FROM information_schema.tables 
                WHERE table_schema = DATABASE()
            """
        }
        
        db_info = {}
        for key, query in queries.items():
            try:
                result = self.db.execute_query(query)
                db_info[key] = result[0] if result else None
            except Exception as e:
                logger.warning(f"Error obteniendo {key}: {e}")
                db_info[key] = None
        
        return db_info
    
    def _get_tables_info(self) -> Dict[str, Dict]:
        query = """
            SELECT 
                TABLE_NAME,
                TABLE_TYPE,
                ENGINE,
                TABLE_ROWS,
                DATA_LENGTH,
                INDEX_LENGTH,
                CREATE_TIME,
                UPDATE_TIME,
                TABLE_COMMENT
            FROM information_schema.TABLES
            WHERE TABLE_SCHEMA = DATABASE()
            ORDER BY TABLE_NAME
        """
        
        result = self.db.execute_query(query)
        tables_info = {}
        
        for table in result:
            table_name = table['TABLE_NAME']
            tables_info[table_name] = {
                'name': table_name,
                'type': table['TABLE_TYPE'],
                'engine': table['ENGINE'],
                'estimated_rows': table['TABLE_ROWS'] or 0,
                'data_size_bytes': table['DATA_LENGTH'] or 0,
                'index_size_bytes': table['INDEX_LENGTH'] or 0,
                'created': table['CREATE_TIME'],
                'updated': table['UPDATE_TIME'],
                'comment': table['TABLE_COMMENT'] or '',
                'entity_type': self._classify_entity_type(table_name),
                'business_context': self._get_business_context(table_name)
            }
        
        return tables_info
    
    def _get_columns_info(self) -> Dict[str, List[Dict]]:
        query = """
            SELECT 
                TABLE_NAME,
                COLUMN_NAME,
                ORDINAL_POSITION,
                COLUMN_DEFAULT,
                IS_NULLABLE,
                DATA_TYPE,
                CHARACTER_MAXIMUM_LENGTH,
                NUMERIC_PRECISION,
                NUMERIC_SCALE,
                COLUMN_TYPE,
                COLUMN_KEY,
                EXTRA,
                COLUMN_COMMENT
            FROM information_schema.COLUMNS
            WHERE TABLE_SCHEMA = DATABASE()
            ORDER BY TABLE_NAME, ORDINAL_POSITION
        """
        
        result = self.db.execute_query(query)
        columns_info = {}
        
        for column in result:
            table_name = column['TABLE_NAME']
            if table_name not in columns_info:
                columns_info[table_name] = []
            
            column_info = {
                'name': column['COLUMN_NAME'],
                'position': column['ORDINAL_POSITION'],
                'data_type': column['DATA_TYPE'],
                'column_type': column['COLUMN_TYPE'],
                'is_nullable': column['IS_NULLABLE'] == 'YES',
                'default_value': column['COLUMN_DEFAULT'],
                'max_length': column['CHARACTER_MAXIMUM_LENGTH'],
                'precision': column['NUMERIC_PRECISION'],
                'scale': column['NUMERIC_SCALE'],
                'key_type': column['COLUMN_KEY'],
                'extra': column['EXTRA'],
                'comment': column['COLUMN_COMMENT'] or '',
                'semantic_type': self._classify_semantic_type(column['COLUMN_NAME'], column['DATA_TYPE']),
                'ai_relevant': self._is_ai_relevant_column(column['COLUMN_NAME'], column['DATA_TYPE'])
            }
            
            columns_info[table_name].append(column_info)
        
        return columns_info
    
    def _get_relationships(self) -> List[Dict]:
        query = """
            SELECT 
                kcu.CONSTRAINT_NAME,
                kcu.TABLE_NAME as source_table,
                kcu.COLUMN_NAME as source_column,
                kcu.REFERENCED_TABLE_NAME as target_table,
                kcu.REFERENCED_COLUMN_NAME as target_column,
                rc.UPDATE_RULE,
                rc.DELETE_RULE
            FROM information_schema.KEY_COLUMN_USAGE kcu
            JOIN information_schema.REFERENTIAL_CONSTRAINTS rc 
                ON kcu.CONSTRAINT_NAME = rc.CONSTRAINT_NAME
            WHERE kcu.TABLE_SCHEMA = DATABASE()
                AND kcu.REFERENCED_TABLE_NAME IS NOT NULL
            ORDER BY kcu.TABLE_NAME, kcu.COLUMN_NAME
        """
        
        result = self.db.execute_query(query)
        relationships = []
        
        for rel in result:
            relationship = {
                'constraint_name': rel['CONSTRAINT_NAME'],
                'source_table': rel['source_table'],
                'source_column': rel['source_column'],
                'target_table': rel['target_table'],
                'target_column': rel['target_column'],
                'update_rule': rel['UPDATE_RULE'],
                'delete_rule': rel['DELETE_RULE'],
                'relationship_type': self._classify_relationship_type(rel),
                'business_meaning': self._get_relationship_meaning(rel)
            }
            relationships.append(relationship)
        
        return relationships
    
    def _get_indexes_info(self) -> Dict[str, List[Dict]]:
        query = """
            SELECT 
                TABLE_NAME,
                INDEX_NAME,
                COLUMN_NAME,
                SEQ_IN_INDEX,
                NON_UNIQUE,
                INDEX_TYPE,
                COMMENT
            FROM information_schema.STATISTICS
            WHERE TABLE_SCHEMA = DATABASE()
            ORDER BY TABLE_NAME, INDEX_NAME, SEQ_IN_INDEX
        """
        
        result = self.db.execute_query(query)
        indexes_info = {}
        
        for idx in result:
            table_name = idx['TABLE_NAME']
            if table_name not in indexes_info:
                indexes_info[table_name] = []
            existing_index = None
            for existing in indexes_info[table_name]:
                if existing['name'] == idx['INDEX_NAME']:
                    existing_index = existing
                    break
            
            if existing_index:
                existing_index['columns'].append({
                    'name': idx['COLUMN_NAME'],
                    'position': idx['SEQ_IN_INDEX']
                })
            else:
                index_info = {
                    'name': idx['INDEX_NAME'],
                    'type': idx['INDEX_TYPE'],
                    'is_unique': idx['NON_UNIQUE'] == 0,
                    'comment': idx['COMMENT'] or '',
                    'columns': [{
                        'name': idx['COLUMN_NAME'],
                        'position': idx['SEQ_IN_INDEX']
                    }]
                }
                indexes_info[table_name].append(index_info)
        
        return indexes_info
    
    def _analyze_entities(self, tables_info: Dict, columns_info: Dict) -> Dict[str, Any]:
        entities = {
            'core_entities': [],
            'lookup_tables': [],
            'junction_tables': [],
            'audit_tables': [],
            'entity_hierarchy': {},
            'business_processes': []
        }
        
        for table_name, table_info in tables_info.items():
            if self._is_core_entity(table_name, columns_info.get(table_name, [])):
                entities['core_entities'].append({
                    'table': table_name,
                    'business_name': self._get_business_name(table_name),
                    'primary_attributes': self._get_primary_attributes(columns_info.get(table_name, [])),
                    'estimated_importance': self._calculate_entity_importance(table_name, table_info)
                })
            
            elif self._is_lookup_table(table_name, columns_info.get(table_name, [])):
                entities['lookup_tables'].append({
                    'table': table_name,
                    'category': self._get_lookup_category(table_name),
                    'values_column': self._get_values_column(columns_info.get(table_name, []))
                })
            
            elif self._is_junction_table(table_name, columns_info.get(table_name, [])):
                entities['junction_tables'].append({
                    'table': table_name,
                    'connects': self._get_connected_entities(table_name, columns_info.get(table_name, []))
                })
        entities['business_processes'] = self._detect_business_processes(tables_info, columns_info)
        
        return entities
    
    def _build_relationship_graph(self, relationships: List[Dict]) -> Dict[str, Any]:
        graph = {
            'nodes': set(),
            'edges': [],
            'clusters': [],
            'critical_paths': []
        }
        for rel in relationships:
            graph['nodes'].add(rel['source_table'])
            graph['nodes'].add(rel['target_table'])
            
            graph['edges'].append({
                'from': rel['source_table'],
                'to': rel['target_table'],
                'type': rel['relationship_type'],
                'constraint': rel['constraint_name']
            })
        
        graph['nodes'] = list(graph['nodes'])
        graph['clusters'] = self._detect_table_clusters(graph['nodes'], graph['edges'])
        graph['critical_paths'] = self._find_critical_paths(graph['nodes'], graph['edges'])
        
        return graph
    
    def _generate_ai_mappings(self, tables_info: Dict, columns_info: Dict, relationships: List[Dict]) -> Dict[str, Any]:
        mappings = {
            'intent_to_tables': {},
            'entity_synonyms': {},
            'column_semantics': {},
            'common_queries': {},
            'business_rules': []
        }
        mappings['intent_to_tables'] = {
            'calificaciones': ['calificaciones', 'asignaturas', 'alumnos'],
            'alumnos_riesgo': ['reportes_riesgo', 'alumnos', 'usuarios'],
            'profesores': ['profesores', 'usuarios', 'profesor_asignatura_grupo'],
            'grupos': ['grupos', 'alumnos_grupos', 'carreras'],
            'estadisticas': ['alumnos', 'calificaciones', 'reportes_riesgo', 'carreras'],
            'horarios': ['horarios', 'profesor_asignatura_grupo', 'grupos'],
            'solicitudes': ['solicitudes_ayuda', 'alumnos', 'directivos'],
            'noticias': ['noticias', 'categorias_noticias', 'directivos'],
            'foro': ['foro_posts', 'foro_comentarios', 'categorias_foro']
        }
        mappings['entity_synonyms'] = {
            'estudiante': ['alumno', 'estudiante', 'muchacho', 'chavo'],
            'profesor': ['profesor', 'maestro', 'docente', 'instructor'],
            'materia': ['materia', 'asignatura', 'clase', 'curso'],
            'calificacion': ['calificacion', 'nota', 'puntuacion', 'resultado'],
            'grupo': ['grupo', 'clase', 'seccion'],
            'carrera': ['carrera', 'licenciatura', 'ingenieria', 'programa']
        }
        for table_name, columns in columns_info.items():
            for column in columns:
                col_name = column['name']
                if column['ai_relevant']:
                    mappings['column_semantics'][f"{table_name}.{col_name}"] = {
                        'semantic_type': column['semantic_type'],
                        'business_meaning': self._get_column_business_meaning(table_name, col_name),
                        'searchable': self._is_searchable_column(column),
                        'filterable': self._is_filterable_column(column),
                        'aggregatable': self._is_aggregatable_column(column)
                    }
        mappings['common_queries'] = self._generate_common_queries(tables_info, columns_info)
        mappings['business_rules'] = self._extract_business_rules(tables_info, columns_info)
        
        return mappings
    
    def _classify_entity_type(self, table_name: str) -> str:
        core_entities = ['usuarios', 'alumnos', 'profesores', 'directivos', 'asignaturas', 'carreras', 'grupos']
        lookup_tables = ['categorias_', 'tipos_', 'estados_', 'niveles_']
        junction_tables = ['_grupos', '_asignatura_', '_reportes']
        
        if table_name in core_entities:
            return 'core_entity'
        elif any(pattern in table_name for pattern in lookup_tables):
            return 'lookup_table'
        elif any(pattern in table_name for pattern in junction_tables):
            return 'junction_table'
        else:
            return 'transactional'
    
    def _classify_semantic_type(self, column_name: str, data_type: str) -> str:
        name_lower = column_name.lower()
        if 'id' in name_lower and ('int' in data_type or 'bigint' in data_type):
            return 'identifier'
        elif 'matricula' in name_lower or 'numero_empleado' in name_lower:
            return 'business_identifier'
        elif any(word in name_lower for word in ['nombre', 'apellido', 'titulo']):
            return 'name'
        elif any(word in name_lower for word in ['descripcion', 'comentario', 'observaciones']):
            return 'description'
        elif any(word in name_lower for word in ['correo', 'email']):
            return 'email'
        elif any(word in name_lower for word in ['telefono', 'celular']):
            return 'phone'
        elif 'direccion' in name_lower:
            return 'address'
        elif 'fecha' in name_lower or 'timestamp' in data_type:
            return 'date'
        elif 'hora' in name_lower and 'time' in data_type:
            return 'time'
        elif any(word in name_lower for word in ['calificacion', 'promedio', 'nota']):
            return 'grade'
        elif any(word in name_lower for word in ['porcentaje', 'indice']):
            return 'percentage'
        elif any(word in name_lower for word in ['estado', 'estatus', 'nivel', 'tipo']):
            return 'status'
        elif 'activo' in name_lower or 'boolean' in data_type:
            return 'flag'
        elif any(word in name_lower for word in ['precio', 'costo', 'monto']):
            return 'currency'
        
        return 'generic'
    
    def _is_ai_relevant_column(self, column_name: str, data_type: str) -> bool:
        name_lower = column_name.lower()
        important_patterns = [
            'nombre', 'apellido', 'matricula', 'calificacion', 'promedio',
            'estado', 'activo', 'fecha', 'tipo', 'nivel', 'descripcion',
            'observaciones', 'titulo', 'correo', 'telefono', 'carrera'
        ]
        exclude_patterns = [
            'created_at', 'updated_at', 'deleted_at', 'password',
            'token', 'hash', 'salt', 'session'
        ]
        
        if any(pattern in name_lower for pattern in exclude_patterns):
            return False
        
        return any(pattern in name_lower for pattern in important_patterns)
    
    def _get_business_context(self, table_name: str) -> str:
        contexts = {
            'usuarios': 'Gestión de identidad y acceso',
            'alumnos': 'Información académica de estudiantes',
            'profesores': 'Gestión de personal docente',
            'directivos': 'Administración institucional',
            'asignaturas': 'Catálogo académico',
            'carreras': 'Programas educativos',
            'grupos': 'Organización académica',
            'calificaciones': 'Evaluación académica',
            'reportes_riesgo': 'Sistema de alertas tempranas',
            'solicitudes_ayuda': 'Soporte estudiantil',
            'horarios': 'Programación académica',
            'noticias': 'Comunicación institucional',
            'foro_posts': 'Comunidad académica',
            'encuestas': 'Investigación y mejora'
        }
        
        return contexts.get(table_name, 'Datos operacionales')
    
    def _is_core_entity(self, table_name: str, columns: List[Dict]) -> bool:
        core_indicators = [
            len(columns) > 5, 
            any(col['name'] == 'id' and col['key_type'] == 'PRI' for col in columns),  
            table_name in ['usuarios', 'alumnos', 'profesores', 'asignaturas', 'grupos']
        ]
        
        return sum(core_indicators) >= 2
    
    def _is_lookup_table(self, table_name: str, columns: List[Dict]) -> bool:
        lookup_indicators = [
            'categoria' in table_name or 'tipo' in table_name,
            len(columns) <= 6, 
            any(col['name'] == 'nombre' for col in columns),  
            any(col['name'] == 'activo' for col in columns)   
        ]
        
        return sum(lookup_indicators) >= 2
    
    def _is_junction_table(self, table_name: str, columns: List[Dict]) -> bool:
        junction_indicators = [
            '_' in table_name and len(table_name.split('_')) >= 2,
            len([col for col in columns if col['name'].endswith('_id')]) >= 2,
            len(columns) <= 8 
        ]
        
        return sum(junction_indicators) >= 2
    
    def _calculate_entity_importance(self, table_name: str, table_info: Dict) -> float:
        importance = 0.0
        rows = table_info.get('estimated_rows', 0)
        if rows > 1000:
            importance += 0.3
        elif rows > 100:
            importance += 0.2
        elif rows > 10:
            importance += 0.1
        if table_name in ['usuarios', 'alumnos', 'profesores', 'calificaciones']:
            importance += 0.4
        if 'académica' in table_info.get('business_context', ''):
            importance += 0.3
        
        return min(importance, 1.0)
    
    def _detect_business_processes(self, tables_info: Dict, columns_info: Dict) -> List[Dict]:
        processes = [
            {
                'name': 'Gestión Académica',
                'tables': ['alumnos', 'asignaturas', 'calificaciones', 'grupos'],
                'description': 'Proceso de evaluación y seguimiento académico',
                'key_metrics': ['promedio_general', 'calificacion_final', 'estatus']
            },
            {
                'name': 'Sistema de Alertas',
                'tables': ['reportes_riesgo', 'seguimiento_reportes', 'alumnos'],
                'description': 'Detección y seguimiento de estudiantes en riesgo',
                'key_metrics': ['nivel_riesgo', 'tipo_riesgo', 'estado']
            },
            {
                'name': 'Soporte Estudiantil',
                'tables': ['solicitudes_ayuda', 'chat_ayuda', 'alumnos'],
                'description': 'Sistema de ayuda y soporte a estudiantes',
                'key_metrics': ['urgencia', 'estado', 'tipo_problema']
            },
            {
                'name': 'Gestión Docente',
                'tables': ['profesores', 'profesor_asignatura_grupo', 'horarios'],
                'description': 'Administración de personal docente y asignaciones',
                'key_metrics': ['activo', 'es_tutor', 'experiencia_años']
            }
        ]
        
        return processes
    
    def _generate_common_queries(self, tables_info: Dict, columns_info: Dict) -> Dict[str, str]:
        return {
            'total_alumnos_activos': "SELECT COUNT(*) FROM alumnos WHERE estado_alumno = 'activo'",
            'promedio_general_sistema': "SELECT AVG(promedio_general) FROM alumnos WHERE estado_alumno = 'activo'",
            'materias_por_carrera': "SELECT c.nombre, COUNT(a.id) as total_materias FROM carreras c LEFT JOIN asignaturas a ON c.id = a.carrera_id GROUP BY c.id",
            'alumnos_riesgo_critico': "SELECT COUNT(*) FROM reportes_riesgo WHERE nivel_riesgo = 'critico' AND estado IN ('abierto', 'en_proceso')",
            'solicitudes_pendientes': "SELECT COUNT(*) FROM solicitudes_ayuda WHERE estado IN ('pendiente', 'en_atencion')"
        }
    
    def _extract_business_rules(self, tables_info: Dict, columns_info: Dict) -> List[Dict]:
        rules = []
        for table_name, columns in columns_info.items():
            for column in columns:
                if 'CHECK' in column.get('extra', ''):
                    rules.append({
                        'type': 'data_constraint',
                        'table': table_name,
                        'column': column['name'],
                        'rule': f"Valor debe cumplir constraint en {column['name']}"
                    })
                
                if column['name'] == 'activo' and column['data_type'] == 'tinyint':
                    rules.append({
                        'type': 'soft_delete',
                        'table': table_name,
                        'rule': f"Tabla {table_name} usa borrado lógico con campo 'activo'"
                    })
        if 'calificaciones' in tables_info:
            rules.append({
                'type': 'business_logic',
                'table': 'calificaciones',
                'rule': 'Las calificaciones deben estar entre 0 y 10'
            })
        
        if 'reportes_riesgo' in tables_info:
            rules.append({
                'type': 'workflow',
                'table': 'reportes_riesgo',
                'rule': 'Los reportes de riesgo siguen un flujo: abierto → en_proceso → resuelto/cerrado'
            })
        
        return rules
    
    def get_schema_summary(self) -> Dict[str, Any]:
        if not self.schema_cache:
            self.analyze_complete_schema()
        
        return {
            'total_tables': len(self.schema_cache['tables']),
            'core_entities': [e['table'] for e in self.schema_cache['entity_analysis']['core_entities']],
            'main_relationships': len(self.schema_cache['relationships']),
            'business_processes': [p['name'] for p in self.schema_cache['entity_analysis']['business_processes']],
            'ai_mappings': self.schema_cache['ai_mappings'],
            'last_updated': self.last_analysis.isoformat() if self.last_analysis else None
        }
    
    def get_table_context(self, table_name: str) -> Dict[str, Any]:
        if not self.schema_cache:
            self.analyze_complete_schema()
        
        table_info = self.schema_cache['tables'].get(table_name, {})
        columns = self.schema_cache['columns'].get(table_name, [])
        related_tables = []
        for rel in self.schema_cache['relationships']:
            if rel['source_table'] == table_name:
                related_tables.append({
                    'table': rel['target_table'],
                    'type': 'references',
                    'via': rel['source_column']
                })
            elif rel['target_table'] == table_name:
                related_tables.append({
                    'table': rel['source_table'],
                    'type': 'referenced_by',
                    'via': rel['target_column']
                })
        
        return {
            'table_info': table_info,
            'columns': columns,
            'related_tables': related_tables,
            'ai_relevant_columns': [col for col in columns if col['ai_relevant']],
            'searchable_columns': [col for col in columns if self._is_searchable_column(col)],
            'business_context': table_info.get('business_context', ''),
            'common_queries': self._get_table_common_queries(table_name)
        }
    
    def _calculate_schema_stats(self, tables_info: Dict, columns_info: Dict) -> Dict[str, Any]:
        total_columns = sum(len(cols) for cols in columns_info.values())
        
        return {
            'total_tables': len(tables_info),
            'total_columns': total_columns,
            'avg_columns_per_table': round(total_columns / len(tables_info), 1),
            'estimated_total_rows': sum(t.get('estimated_rows', 0) for t in tables_info.values()),
            'total_size_mb': sum(
                (t.get('data_size_bytes', 0) + t.get('index_size_bytes', 0)) / 1024 / 1024 
                for t in tables_info.values()
            )
        }
    
    def _is_searchable_column(self, column: Dict) -> bool:
        searchable_types = ['name', 'description', 'email', 'business_identifier']
        return column['semantic_type'] in searchable_types
    
    def _is_filterable_column(self, column: Dict) -> bool:
        filterable_types = ['status', 'flag', 'date', 'grade', 'identifier']
        return column['semantic_type'] in filterable_types
    
    def _is_aggregatable_column(self, column: Dict) -> bool:
        aggregatable_types = ['grade', 'percentage', 'currency']
        return column['semantic_type'] in aggregatable_types
    
    def _get_column_business_meaning(self, table_name: str, column_name: str) -> str:
        meanings = {
            'calificaciones.calificacion_final': 'Calificación definitiva del alumno en la materia',
            'alumnos.promedio_general': 'Promedio ponderado de todas las materias',
            'reportes_riesgo.nivel_riesgo': 'Severidad del riesgo detectado',
            'usuarios.activo': 'Estado de actividad del usuario en el sistema',
            'solicitudes_ayuda.urgencia': 'Prioridad de atención de la solicitud'
        }
        
        key = f"{table_name}.{column_name}"
        return meanings.get(key, f"Campo {column_name} de la tabla {table_name}")
    
    def _get_table_common_queries(self, table_name: str) -> List[str]:
        common_queries = {
            'alumnos': [
                "SELECT COUNT(*) FROM alumnos WHERE estado_alumno = 'activo'",
                "SELECT AVG(promedio_general) FROM alumnos",
                "SELECT * FROM alumnos WHERE promedio_general < 7.0"
            ],
            'calificaciones': [
                "SELECT COUNT(*) FROM calificaciones WHERE estatus = 'reprobado'",
                "SELECT AVG(calificacion_final) FROM calificaciones",
                "SELECT asignatura_id, COUNT(*) FROM calificaciones GROUP BY asignatura_id"
            ],
            'reportes_riesgo': [
                "SELECT COUNT(*) FROM reportes_riesgo WHERE estado = 'abierto'",
                "SELECT nivel_riesgo, COUNT(*) FROM reportes_riesgo GROUP BY nivel_riesgo",
                "SELECT * FROM reportes_riesgo WHERE nivel_riesgo = 'critico'"
            ]
        }
        
        return common_queries.get(table_name, [])
    
    def validate_schema_for_ai(self) -> Dict[str, Any]:
        if not self.schema_cache:
            self.analyze_complete_schema()
        
        validation = {
            'is_valid': True,
            'warnings': [],
            'recommendations': [],
            'missing_elements': []
        }
        required_entities = ['usuarios', 'alumnos', 'profesores', 'asignaturas', 'calificaciones']
        for entity in required_entities:
            if entity not in self.schema_cache['tables']:
                validation['missing_elements'].append(f"Tabla requerida: {entity}")
                validation['is_valid'] = False
        important_columns = {
            'alumnos': ['promedio_general', 'estado_alumno'],
            'calificaciones': ['calificacion_final', 'estatus'],
            'usuarios': ['rol', 'activo']
        }
        
        for table, columns in important_columns.items():
            if table in self.schema_cache['columns']:
                table_columns = [col['name'] for col in self.schema_cache['columns'][table]]
                for col in columns:
                    if col not in table_columns:
                        validation['warnings'].append(f"Columna recomendada faltante: {table}.{col}")
        if len(self.schema_cache['relationships']) < 5:
            validation['recommendations'].append("Considerar agregar más relaciones entre tablas")
        
        if not any('fecha' in col['name'] for cols in self.schema_cache['columns'].values() for col in cols):
            validation['recommendations'].append("Agregar campos de fecha para análisis temporal")
        
        return validation