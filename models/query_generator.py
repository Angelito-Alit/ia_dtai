import logging
import re
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class QueryGenerator:
    def __init__(self, db_connection):
        self.db = db_connection
        self.schema = {}
        self.query_templates = {}
        self._initialize_templates()
    
    def load_database_schema(self):
        try:
            tables = self.db.get_all_tables()
            for table in tables:
                table_name = table['TABLE_NAME']
                self.schema[table_name] = {
                    'comment': table['TABLE_COMMENT'],
                    'columns': self.db.get_table_schema(table_name),
                    'relationships': []
                }
            relationships = self.db.get_table_relationships()
            for rel in relationships:
                table_name = rel['TABLE_NAME']
                if table_name in self.schema:
                    self.schema[table_name]['relationships'].append(rel)
            
            logger.info(f"Esquema cargado: {len(self.schema)} tablas")
            
        except Exception as e:
            logger.error(f"Error cargando esquema: {e}")
    
    def _initialize_templates(self):
        self.query_templates = {
            'calificaciones_alumno': {
                'query': """
                SELECT 
                    a.nombre, a.codigo, c.parcial_1, c.parcial_2, c.parcial_3,
                    c.calificacion_final, c.estatus, c.observaciones,
                    car.nombre as carrera
                FROM calificaciones c
                JOIN asignaturas a ON c.asignatura_id = a.id
                JOIN alumnos al ON c.alumno_id = al.id
                JOIN carreras car ON al.carrera_id = car.id
                WHERE al.usuario_id = %s AND c.ciclo_escolar = %s
                ORDER BY a.cuatrimestre, a.nombre
                """,
                'params': ['user_id', 'current_cycle']
            },
            
            'alumnos_en_riesgo': {
                'query': """
                SELECT DISTINCT
                    u.nombre, u.apellido, al.matricula, al.promedio_general,
                    rr.tipo_riesgo, rr.nivel_riesgo, rr.descripcion,
                    car.nombre as carrera
                FROM reportes_riesgo rr
                JOIN alumnos al ON rr.alumno_id = al.id
                JOIN usuarios u ON al.usuario_id = u.id
                JOIN carreras car ON al.carrera_id = car.id
                WHERE rr.estado IN ('abierto', 'en_proceso')
                {role_filter}
                ORDER BY 
                    CASE rr.nivel_riesgo 
                        WHEN 'critico' THEN 1 
                        WHEN 'alto' THEN 2 
                        WHEN 'medio' THEN 3 
                        ELSE 4 
                    END,
                    al.promedio_general ASC
                """,
                'role_filters': {
                    'profesor': 'AND EXISTS (SELECT 1 FROM profesor_asignatura_grupo pag JOIN profesores p ON pag.profesor_id = p.id WHERE p.usuario_id = %s AND pag.grupo_id IN (SELECT grupo_id FROM alumnos_grupos WHERE alumno_id = al.id))',
                    'directivo': '',
                    'alumno': 'AND al.usuario_id = %s'
                }
            },
            
            'promedio_por_carrera': {
                'query': """
                SELECT 
                    c.nombre as carrera,
                    COUNT(DISTINCT al.id) as total_alumnos,
                    AVG(al.promedio_general) as promedio_carrera,
                    COUNT(CASE WHEN al.promedio_general < 7.0 THEN 1 END) as alumnos_riesgo,
                    ROUND((COUNT(CASE WHEN al.promedio_general < 7.0 THEN 1 END) * 100.0 / COUNT(DISTINCT al.id)), 2) as porcentaje_riesgo
                FROM carreras c
                JOIN alumnos al ON c.id = al.carrera_id
                WHERE al.estado_alumno = 'activo'
                GROUP BY c.id, c.nombre
                ORDER BY promedio_carrera DESC
                """
            },
            
            'materias_reprobadas': {
                'query': """
                SELECT 
                    a.nombre as materia,
                    a.codigo,
                    COUNT(*) as total_reprobados,
                    AVG(c.calificacion_final) as promedio_materia,
                    car.nombre as carrera
                FROM calificaciones c
                JOIN asignaturas a ON c.asignatura_id = a.id
                JOIN alumnos al ON c.alumno_id = al.id
                JOIN carreras car ON al.carrera_id = car.id
                WHERE c.estatus = 'reprobado' 
                    AND c.ciclo_escolar = %s
                GROUP BY a.id, a.nombre, a.codigo, car.nombre
                ORDER BY total_reprobados DESC, promedio_materia ASC
                LIMIT 10
                """,
                'params': ['current_cycle']
            },
            'grupos_profesor': {
                'query': """
                SELECT DISTINCT
                    g.codigo as grupo,
                    g.cuatrimestre,
                    g.periodo,
                    g.año,
                    car.nombre as carrera,
                    a.nombre as asignatura,
                    COUNT(ag.alumno_id) as total_alumnos
                FROM grupos g
                JOIN profesor_asignatura_grupo pag ON g.id = pag.grupo_id
                JOIN profesores p ON pag.profesor_id = p.id
                JOIN carreras car ON g.carrera_id = car.id
                JOIN asignaturas a ON pag.asignatura_id = a.id
                LEFT JOIN alumnos_grupos ag ON g.id = ag.grupo_id AND ag.activo = TRUE
                WHERE p.usuario_id = %s AND pag.activo = TRUE
                GROUP BY g.id, g.codigo, g.cuatrimestre, g.periodo, g.año, car.nombre, a.nombre
                ORDER BY g.año DESC, g.periodo, car.nombre
                """,
                'params': ['user_id']
            },
            
            'solicitudes_ayuda_pendientes': {
                'query': """
                SELECT 
                    sa.id,
                    u.nombre,
                    u.apellido,
                    al.matricula,
                    sa.tipo_problema,
                    sa.descripcion_problema,
                    sa.urgencia,
                    sa.fecha_solicitud,
                    car.nombre as carrera
                FROM solicitudes_ayuda sa
                JOIN alumnos al ON sa.alumno_id = al.id
                JOIN usuarios u ON al.usuario_id = u.id
                JOIN carreras car ON al.carrera_id = car.id
                WHERE sa.estado IN ('pendiente', 'en_atencion')
                ORDER BY 
                    CASE sa.urgencia 
                        WHEN 'alta' THEN 1 
                        WHEN 'media' THEN 2 
                        ELSE 3 
                    END,
                    sa.fecha_solicitud ASC
                LIMIT 20
                """
            },
            'estadisticas_generales': {
                'query': """
                SELECT 
                    'Total Alumnos' as concepto,
                    COUNT(*) as valor
                FROM alumnos
                WHERE estado_alumno = 'activo'
                UNION ALL
                SELECT 
                    'Alumnos en Riesgo' as concepto,
                    COUNT(*) as valor
                FROM alumnos
                WHERE promedio_general < 7.0 AND estado_alumno = 'activo'
                UNION ALL
                SELECT 
                    'Reportes Abiertos' as concepto,
                    COUNT(*) as valor
                FROM reportes_riesgo
                WHERE estado IN ('abierto', 'en_proceso')
                UNION ALL
                SELECT 
                    'Solicitudes Pendientes' as concepto,
                    COUNT(*) as valor
                FROM solicitudes_ayuda
                WHERE estado IN ('pendiente', 'en_atencion')
                """
            },
            
            'horarios_alumno': {
                'query': """
                SELECT 
                    h.dia_semana,
                    h.hora_inicio,
                    h.hora_fin,
                    a.nombre as materia,
                    h.aula,
                    h.tipo_clase,
                    CONCAT(u.nombre, ' ', u.apellido) as profesor
                FROM horarios h
                JOIN profesor_asignatura_grupo pag ON h.profesor_asignatura_grupo_id = pag.id
                JOIN asignaturas a ON pag.asignatura_id = a.id
                JOIN grupos g ON pag.grupo_id = g.id
                JOIN alumnos_grupos ag ON g.id = ag.grupo_id
                JOIN alumnos al ON ag.alumno_id = al.id
                JOIN profesores p ON pag.profesor_id = p.id
                JOIN usuarios u ON p.usuario_id = u.id
                WHERE al.usuario_id = %s AND ag.activo = TRUE AND h.activo = TRUE
                ORDER BY 
                    CASE h.dia_semana
                        WHEN 'lunes' THEN 1
                        WHEN 'martes' THEN 2
                        WHEN 'miercoles' THEN 3
                        WHEN 'jueves' THEN 4
                        WHEN 'viernes' THEN 5
                        WHEN 'sabado' THEN 6
                    END,
                    h.hora_inicio
                """,
                'params': ['user_id']
            }
        }
    
    def generate_query(self, intent, entities, user_role, user_id=None, context=None):
        try:
            current_cycle = self._get_current_cycle()
            query_info = self._map_intent_to_query(intent, entities, user_role, user_id, current_cycle)
            
            if not query_info:
                return {'query': None, 'params': None, 'description': 'No se pudo generar consulta'}
            processed_params = self._process_parameters(
                query_info.get('params', []), 
                entities, 
                user_id, 
                current_cycle
            )
            final_query = self._apply_role_filters(
                query_info['query'], 
                user_role, 
                user_id, 
                query_info.get('role_filters', {})
            )
            
            return {
                'query': final_query,
                'params': processed_params,
                'description': query_info.get('description', 'Consulta generada'),
                'template_used': intent
            }
            
        except Exception as e:
            logger.error(f"Error generando consulta: {e}")
            return {'query': None, 'params': None, 'description': f'Error: {e}'}
    
    def _map_intent_to_query(self, intent, entities, user_role, user_id, current_cycle):
        intent_mapping = {
            'ver_calificaciones': 'calificaciones_alumno',
            'consultar_notas': 'calificaciones_alumno',
            'mis_calificaciones': 'calificaciones_alumno',
            
            'alumnos_riesgo': 'alumnos_en_riesgo',
            'estudiantes_problema': 'alumnos_en_riesgo',
            'riesgo_academico': 'alumnos_en_riesgo',
            
            'promedio_carreras': 'promedio_por_carrera',
            'rendimiento_carrera': 'promedio_por_carrera',
            
            'materias_reprobadas': 'materias_reprobadas',
            'asignaturas_problema': 'materias_reprobadas',
            
            'mis_grupos': 'grupos_profesor',
            'grupos_asignados': 'grupos_profesor',
            
            'solicitudes_pendientes': 'solicitudes_ayuda_pendientes',
            'ayuda_pendiente': 'solicitudes_ayuda_pendientes',
            
            'estadisticas': 'estadisticas_generales',
            'resumen_sistema': 'estadisticas_generales',
            
            'mi_horario': 'horarios_alumno',
            'horario_clases': 'horarios_alumno'
        }
        template_key = intent_mapping.get(intent)
        if template_key and template_key in self.query_templates:
            return self.query_templates[template_key]
        return self._generate_dynamic_query(intent, entities, user_role)
    
    def _generate_dynamic_query(self, intent, entities, user_role):
        if any(word in intent.lower() for word in ['promedio', 'calificacion', 'nota']):
            if user_role == 'alumno':
                return self.query_templates['calificaciones_alumno']
            else:
                return self.query_templates['promedio_por_carrera']
        
        elif any(word in intent.lower() for word in ['riesgo', 'problema', 'ayuda']):
            return self.query_templates['alumnos_en_riesgo']
        
        elif any(word in intent.lower() for word in ['grupo', 'clase', 'materia']):
            if user_role == 'profesor':
                return self.query_templates['grupos_profesor']
            elif user_role == 'alumno':
                return self.query_templates['horarios_alumno']
        
        elif any(word in intent.lower() for word in ['estadistica', 'reporte', 'analisis']):
            return self.query_templates['estadisticas_generales']
        return {
            'query': """
            SELECT 'informacion_general' as tipo,
                   'Consulta no específica detectada' as mensaje,
                   %s as intent_detectado
            """,
            'params': [intent],
            'description': 'Consulta genérica'
        }
    
    def _process_parameters(self, param_names, entities, user_id, current_cycle):
        params = []
        
        for param_name in param_names:
            if param_name == 'user_id':
                params.append(user_id)
            elif param_name == 'current_cycle':
                params.append(current_cycle)
            elif param_name in entities:
                params.append(entities[param_name])
            else:
                params.append(None)
        
        return params
    
    def _apply_role_filters(self, query, user_role, user_id, role_filters):
        if '{role_filter}' not in query:
            return query
        
        filter_clause = role_filters.get(user_role, '')
        final_query = query.replace('{role_filter}', filter_clause)
        
        return final_query
    
    def _get_current_cycle(self):
        now = datetime.now()
        year = now.year
        month = now.month
        
        if month <= 4:  
            return f"{year-1}-{year}"
        elif month <= 8:  
            return f"{year}-{year}"
        else:  
            return f"{year}-{year+1}"
    
    def validate_query(self, query, params):
        if not query:
            return False
        dangerous_keywords = [
            'DROP', 'DELETE', 'INSERT', 'UPDATE', 'ALTER', 
            'CREATE', 'TRUNCATE', 'EXEC', 'EXECUTE'
        ]
        
        query_upper = query.upper()
        for keyword in dangerous_keywords:
            if keyword in query_upper:
                logger.warning(f"Consulta rechazada por contener: {keyword}")
                return False
        
        return True
    
    def get_query_explanation(self, template_key):
        explanations = {
            'calificaciones_alumno': 'Obtiene las calificaciones de un alumno específico',
            'alumnos_en_riesgo': 'Lista alumnos que tienen reportes de riesgo activos',
            'promedio_por_carrera': 'Calcula promedios y estadísticas por carrera',
            'materias_reprobadas': 'Muestra las materias con más reprobados',
            'grupos_profesor': 'Lista los grupos asignados a un profesor',
            'solicitudes_ayuda_pendientes': 'Muestra solicitudes de ayuda sin resolver',
            'estadisticas_generales': 'Proporciona estadísticas generales del sistema',
            'horarios_alumno': 'Muestra el horario de clases de un alumno'
        }
        
        return explanations.get(template_key, 'Consulta personalizada')