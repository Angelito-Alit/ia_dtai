import re
from typing import Dict, List, Optional, Tuple
import logging

logger = logging.getLogger(__name__)

class QueryGenerator:
    def __init__(self):
        self.query_patterns = {
            'estadisticas_generales': {
                'keywords': ['estadisticas', 'general', 'resumen', 'total', 'cuantos', 'cantidad'],
                'query': """
                SELECT 
                    'Alumnos Activos' as categoria,
                    COUNT(*) as total
                FROM alumnos 
                WHERE estado_alumno = 'activo'
                UNION ALL
                SELECT 
                    'Profesores Activos' as categoria,
                    COUNT(*) as total
                FROM profesores 
                WHERE activo = 1
                UNION ALL
                SELECT 
                    'Carreras Activas' as categoria,
                    COUNT(*) as total
                FROM carreras 
                WHERE activa = 1
                UNION ALL
                SELECT 
                    'Grupos Activos' as categoria,
                    COUNT(*) as total
                FROM grupos 
                WHERE activo = 1
                UNION ALL
                SELECT 
                    'Reportes Abiertos' as categoria,
                    COUNT(*) as total
                FROM reportes_riesgo 
                WHERE estado IN ('abierto', 'en_proceso')
                UNION ALL
                SELECT 
                    'Solicitudes Pendientes' as categoria,
                    COUNT(*) as total
                FROM solicitudes_ayuda 
                WHERE estado IN ('pendiente', 'en_atencion')
                """
            },
            
            'alumnos_riesgo': {
                'keywords': ['riesgo', 'problema', 'dificultad', 'critico', 'alto'],
                'query': """
                SELECT 
                    u.nombre,
                    u.apellido,
                    al.matricula,
                    car.nombre as carrera,
                    rr.nivel_riesgo,
                    rr.tipo_riesgo,
                    rr.descripcion,
                    rr.fecha_reporte,
                    rr.estado
                FROM reportes_riesgo rr
                JOIN alumnos al ON rr.alumno_id = al.id
                JOIN usuarios u ON al.usuario_id = u.id
                JOIN carreras car ON al.carrera_id = car.id
                WHERE rr.estado IN ('abierto', 'en_proceso')
                ORDER BY 
                    CASE rr.nivel_riesgo 
                        WHEN 'critico' THEN 1 
                        WHEN 'alto' THEN 2 
                        WHEN 'medio' THEN 3 
                        ELSE 4 
                    END,
                    rr.fecha_reporte DESC
                LIMIT 20
                """
            },
            
            'promedio_carreras': {
                'keywords': ['promedio', 'carrera', 'rendimiento'],
                'query': """
                SELECT 
                    c.nombre as carrera,
                    COUNT(al.id) as total_alumnos,
                    ROUND(AVG(al.promedio_general), 2) as promedio_carrera,
                    COUNT(CASE WHEN al.promedio_general < 7.0 THEN 1 END) as alumnos_riesgo,
                    ROUND(
                        COUNT(CASE WHEN al.promedio_general < 7.0 THEN 1 END) * 100.0 / COUNT(al.id), 
                        1
                    ) as porcentaje_riesgo
                FROM carreras c
                LEFT JOIN alumnos al ON c.id = al.carrera_id
                WHERE al.estado_alumno = 'activo' AND c.activa = 1
                GROUP BY c.id, c.nombre
                HAVING total_alumnos > 0
                ORDER BY promedio_carrera DESC
                """
            },
            
            'materias_reprobadas': {
                'keywords': ['reprobada', 'reprobadas', 'asignatura', 'materia', 'falla'],
                'query': """
                SELECT 
                    a.nombre as asignatura,
                    COUNT(c.id) as total_reprobados,
                    ROUND(
                        COUNT(c.id) * 100.0 / 
                        (SELECT COUNT(*) FROM calificaciones WHERE asignatura_id = a.id), 
                        1
                    ) as porcentaje_reprobacion
                FROM asignaturas a
                JOIN calificaciones c ON a.id = c.asignatura_id
                WHERE c.calificacion_final < 7.0 AND c.estatus = 'reprobado'
                GROUP BY a.id, a.nombre
                HAVING total_reprobados > 0
                ORDER BY total_reprobados DESC
                LIMIT 15
                """
            },
            
            'solicitudes_ayuda': {
                'keywords': ['solicitud', 'ayuda', 'pendiente', 'atencion'],
                'query': """
                SELECT 
                    sa.estado,
                    sa.tipo_problema,
                    sa.urgencia,
                    COUNT(*) as cantidad,
                    DATE(sa.fecha_solicitud) as fecha
                FROM solicitudes_ayuda sa
                WHERE sa.fecha_solicitud >= DATE_SUB(NOW(), INTERVAL 30 DAY)
                GROUP BY sa.estado, sa.tipo_problema, sa.urgencia, DATE(sa.fecha_solicitud)
                ORDER BY sa.fecha_solicitud DESC, cantidad DESC
                """
            },
            
            'calificaciones_alumno': {
                'keywords': ['calificacion', 'nota', 'matricula'],
                'query': """
                SELECT 
                    a.nombre as asignatura,
                    c.calificacion_final,
                    c.estatus,
                    c.parcial_1,
                    c.parcial_2,
                    c.parcial_3,
                    c.fecha_captura
                FROM calificaciones c
                JOIN asignaturas a ON c.asignatura_id = a.id
                JOIN alumnos al ON c.alumno_id = al.id
                WHERE al.matricula = %s
                ORDER BY a.nombre
                """
            },
            
            'horario_alumno': {
                'keywords': ['horario', 'clase', 'aula'],
                'query': """
                SELECT 
                    a.nombre as asignatura,
                    h.dia_semana,
                    h.hora_inicio,
                    h.hora_fin,
                    h.aula,
                    CONCAT(u.nombre, ' ', u.apellido) as profesor
                FROM horarios h
                JOIN grupos g ON h.grupo_id = g.id
                JOIN alumnos al ON g.id = al.grupo_id
                JOIN asignaturas a ON h.asignatura_id = a.id
                JOIN profesores p ON h.profesor_id = p.id
                JOIN usuarios u ON p.usuario_id = u.id
                WHERE al.matricula = %s AND g.activo = 1
                ORDER BY 
                    FIELD(h.dia_semana, 'Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado'),
                    h.hora_inicio
                """
            },
            
            'grupos': {
                'keywords': ['grupo', 'grupos'],
                'query': """
                SELECT 
                    g.nombre as grupo,
                    c.nombre as carrera,
                    g.cuatrimestre,
                    g.capacidad_maxima,
                    COUNT(al.id) as alumnos_inscritos,
                    CONCAT(u.nombre, ' ', u.apellido) as tutor,
                    g.ciclo_escolar,
                    g.activo
                FROM grupos g
                JOIN carreras c ON g.carrera_id = c.id
                LEFT JOIN alumnos al ON g.id = al.grupo_id
                LEFT JOIN profesores p ON g.tutor_id = p.id
                LEFT JOIN usuarios u ON p.usuario_id = u.id
                WHERE g.activo = 1
                GROUP BY g.id, g.nombre, c.nombre, g.cuatrimestre, g.capacidad_maxima, u.nombre, u.apellido, g.ciclo_escolar, g.activo
                ORDER BY c.nombre, g.cuatrimestre, g.nombre
                """
            }
        }
    
    def generate_query(self, message: str, intent: str, user_id: Optional[int] = None, role: str = 'alumno') -> Tuple[Optional[str], list]:
        message_lower = message.lower()
        
        matricula_match = re.search(r'\b\d{8,12}\b', message)
        
        if intent in ['calificaciones', 'calificacion'] or any(k in message_lower for k in ['calificacion', 'nota']):
            if matricula_match:
                return self.query_patterns['calificaciones_alumno']['query'], [matricula_match.group()]
            elif role == 'alumno' and user_id:
                query = """
                SELECT 
                    a.nombre as asignatura,
                    c.calificacion_final,
                    c.estatus,
                    c.parcial_1,
                    c.parcial_2,
                    c.parcial_3,
                    c.fecha_captura
                FROM calificaciones c
                JOIN asignaturas a ON c.asignatura_id = a.id
                JOIN alumnos al ON c.alumno_id = al.id
                WHERE al.usuario_id = %s
                ORDER BY a.nombre
                """
                return query, [user_id]
        
        if intent in ['horario', 'horarios'] or any(k in message_lower for k in ['horario', 'clase', 'aula']):
            if matricula_match:
                return self.query_patterns['horario_alumno']['query'], [matricula_match.group()]
            elif role == 'alumno' and user_id:
                query = """
                SELECT 
                    a.nombre as asignatura,
                    h.dia_semana,
                    h.hora_inicio,
                    h.hora_fin,
                    h.aula,
                    CONCAT(u.nombre, ' ', u.apellido) as profesor
                FROM horarios h
                JOIN grupos g ON h.grupo_id = g.id
                JOIN alumnos al ON g.id = al.grupo_id
                JOIN asignaturas a ON h.asignatura_id = a.id
                JOIN profesores p ON h.profesor_id = p.id
                JOIN usuarios u ON p.usuario_id = u.id
                WHERE al.usuario_id = %s AND g.activo = 1
                ORDER BY 
                    FIELD(h.dia_semana, 'Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado'),
                    h.hora_inicio
                """
                return query, [user_id]
        
        for pattern_name, pattern_data in self.query_patterns.items():
            if any(keyword in message_lower for keyword in pattern_data['keywords']):
                return pattern_data['query'], []
        
        return None, []
    
    def get_available_queries(self, role: str) -> list:
        base_queries = list(self.query_patterns.keys())
        
        if role == 'alumno':
            return [q for q in base_queries if q not in ['alumnos_riesgo']]
        elif role == 'profesor':
            return base_queries + ['mis_grupos', 'mis_alumnos']
        else:
            return base_queries