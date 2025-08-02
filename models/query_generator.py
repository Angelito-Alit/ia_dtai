import re
from typing import Dict, List, Optional, Tuple
import logging

logger = logging.getLogger(__name__)

class QueryGenerator:
    def __init__(self):
        self.directivo_queries = {
            'estadisticas_generales': {
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
                    'Reportes Críticos Abiertos' as categoria,
                    COUNT(*) as total
                FROM reportes_riesgo 
                WHERE estado IN ('abierto', 'en_proceso') AND nivel_riesgo = 'critico'
                UNION ALL
                SELECT 
                    'Solicitudes Urgentes' as categoria,
                    COUNT(*) as total
                FROM solicitudes_ayuda 
                WHERE estado IN ('pendiente', 'en_atencion') AND urgencia = 'alta'
                """
            },
            
            'alumnos_bajo_rendimiento': {
                'query': """
                SELECT 
                    al.matricula,
                    CONCAT(u.nombre, ' ', u.apellido) as nombre_completo,
                    car.nombre as carrera,
                    g.nombre as grupo,
                    al.promedio_general,
                    al.cuatrimestre_actual,
                    COUNT(c.id) as materias_reprobadas,
                    al.estado_alumno
                FROM alumnos al
                JOIN usuarios u ON al.usuario_id = u.id
                JOIN carreras car ON al.carrera_id = car.id
                LEFT JOIN grupos g ON al.grupo_id = g.id
                LEFT JOIN calificaciones c ON al.id = c.alumno_id AND c.estatus = 'reprobado'
                WHERE al.estado_alumno = 'activo' 
                AND (al.promedio_general < 7.0 OR al.promedio_general IS NULL)
                GROUP BY al.id, al.matricula, u.nombre, u.apellido, car.nombre, g.nombre, al.promedio_general, al.cuatrimestre_actual, al.estado_alumno
                ORDER BY al.promedio_general ASC, materias_reprobadas DESC
                LIMIT 20
                """
            },
            
            'alumnos_riesgo': {
                'query': """
                SELECT 
                    al.matricula,
                    CONCAT(u.nombre, ' ', u.apellido) as nombre_completo,
                    car.nombre as carrera,
                    g.nombre as grupo,
                    rr.nivel_riesgo,
                    rr.tipo_riesgo,
                    rr.descripcion,
                    rr.fecha_reporte,
                    rr.estado as estado_reporte,
                    al.promedio_general
                FROM reportes_riesgo rr
                JOIN alumnos al ON rr.alumno_id = al.id
                JOIN usuarios u ON al.usuario_id = u.id
                JOIN carreras car ON al.carrera_id = car.id
                LEFT JOIN grupos g ON al.grupo_id = g.id
                WHERE rr.estado IN ('abierto', 'en_proceso')
                ORDER BY 
                    CASE rr.nivel_riesgo 
                        WHEN 'critico' THEN 1 
                        WHEN 'alto' THEN 2 
                        WHEN 'medio' THEN 3 
                        ELSE 4 
                    END,
                    rr.fecha_reporte DESC
                LIMIT 25
                """
            },
            
            'ubicacion_grupos': {
                'query': """
                SELECT DISTINCT
                    g.nombre as grupo,
                    car.nombre as carrera,
                    g.cuatrimestre,
                    h.aula,
                    h.dia_semana,
                    h.hora_inicio,
                    h.hora_fin,
                    a.nombre as asignatura,
                    CONCAT(up.nombre, ' ', up.apellido) as profesor,
                    COUNT(al.id) as alumnos_inscritos
                FROM grupos g
                JOIN carreras car ON g.carrera_id = car.id
                LEFT JOIN horarios h ON g.id = h.grupo_id
                LEFT JOIN asignaturas a ON h.asignatura_id = a.id
                LEFT JOIN profesores p ON h.profesor_id = p.id
                LEFT JOIN usuarios up ON p.usuario_id = up.id
                LEFT JOIN alumnos al ON g.id = al.grupo_id AND al.estado_alumno = 'activo'
                WHERE g.activo = 1
                GROUP BY g.id, g.nombre, car.nombre, g.cuatrimestre, h.aula, h.dia_semana, h.hora_inicio, h.hora_fin, a.nombre, up.nombre, up.apellido
                ORDER BY car.nombre, g.cuatrimestre, g.nombre, h.dia_semana, h.hora_inicio
                """
            },
            
            'horarios_grupos': {
                'query': """
                SELECT 
                    g.nombre as grupo,
                    car.nombre as carrera,
                    h.dia_semana,
                    h.hora_inicio,
                    h.hora_fin,
                    h.aula,
                    a.nombre as asignatura,
                    CONCAT(up.nombre, ' ', up.apellido) as profesor,
                    COUNT(al.id) as alumnos_en_grupo
                FROM grupos g
                JOIN carreras car ON g.carrera_id = car.id
                JOIN horarios h ON g.id = h.grupo_id
                JOIN asignaturas a ON h.asignatura_id = a.id
                JOIN profesores p ON h.profesor_id = p.id
                JOIN usuarios up ON p.usuario_id = up.id
                LEFT JOIN alumnos al ON g.id = al.grupo_id AND al.estado_alumno = 'activo'
                WHERE g.activo = 1
                GROUP BY g.id, g.nombre, car.nombre, h.dia_semana, h.hora_inicio, h.hora_fin, h.aula, a.nombre, up.nombre, up.apellido
                ORDER BY 
                    FIELD(h.dia_semana, 'Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado'),
                    h.hora_inicio,
                    car.nombre,
                    g.nombre
                """
            },
            
            'grupos_detalle': {
                'query': """
                SELECT 
                    g.nombre as grupo,
                    car.nombre as carrera,
                    g.cuatrimestre,
                    g.capacidad_maxima,
                    COUNT(al.id) as alumnos_inscritos,
                    ROUND((COUNT(al.id) * 100.0 / g.capacidad_maxima), 1) as porcentaje_ocupacion,
                    CONCAT(ut.nombre, ' ', ut.apellido) as tutor,
                    g.ciclo_escolar,
                    AVG(al.promedio_general) as promedio_grupo
                FROM grupos g
                JOIN carreras car ON g.carrera_id = car.id
                LEFT JOIN alumnos al ON g.id = al.grupo_id AND al.estado_alumno = 'activo'
                LEFT JOIN profesores pt ON g.tutor_id = pt.id
                LEFT JOIN usuarios ut ON pt.usuario_id = ut.id
                WHERE g.activo = 1
                GROUP BY g.id, g.nombre, car.nombre, g.cuatrimestre, g.capacidad_maxima, ut.nombre, ut.apellido, g.ciclo_escolar
                ORDER BY car.nombre, g.cuatrimestre, g.nombre
                """
            },
            
            'carreras_rendimiento': {
                'query': """
                SELECT 
                    c.nombre as carrera,
                    COUNT(al.id) as total_alumnos,
                    ROUND(AVG(al.promedio_general), 2) as promedio_carrera,
                    COUNT(CASE WHEN al.promedio_general < 7.0 THEN 1 END) as alumnos_riesgo,
                    COUNT(CASE WHEN al.promedio_general >= 9.0 THEN 1 END) as alumnos_excelencia,
                    ROUND(COUNT(CASE WHEN al.promedio_general < 7.0 THEN 1 END) * 100.0 / COUNT(al.id), 1) as porcentaje_riesgo,
                    COUNT(DISTINCT g.id) as grupos_activos,
                    COUNT(DISTINCT rr.id) as reportes_riesgo_activos
                FROM carreras c
                LEFT JOIN alumnos al ON c.id = al.carrera_id AND al.estado_alumno = 'activo'
                LEFT JOIN grupos g ON c.id = g.carrera_id AND g.activo = 1
                LEFT JOIN reportes_riesgo rr ON al.id = rr.alumno_id AND rr.estado IN ('abierto', 'en_proceso')
                WHERE c.activa = 1
                GROUP BY c.id, c.nombre
                HAVING total_alumnos > 0
                ORDER BY promedio_carrera DESC, total_alumnos DESC
                """
            },
            
            'profesores_carga': {
                'query': """
                SELECT 
                    CONCAT(u.nombre, ' ', u.apellido) as profesor,
                    p.especialidad,
                    COUNT(DISTINCT h.grupo_id) as grupos_asignados,
                    COUNT(DISTINCT h.asignatura_id) as materias_diferentes,
                    COUNT(h.id) as total_clases_semanales,
                    GROUP_CONCAT(DISTINCT car.nombre SEPARATOR ', ') as carreras_imparte,
                    CASE 
                        WHEN p.es_tutor = 1 THEN 'Sí' 
                        ELSE 'No' 
                    END as es_tutor
                FROM profesores p
                JOIN usuarios u ON p.usuario_id = u.id
                LEFT JOIN horarios h ON p.id = h.profesor_id
                LEFT JOIN grupos g ON h.grupo_id = g.id AND g.activo = 1
                LEFT JOIN carreras car ON g.carrera_id = car.id
                WHERE p.activo = 1
                GROUP BY p.id, u.nombre, u.apellido, p.especialidad, p.es_tutor
                ORDER BY grupos_asignados DESC, total_clases_semanales DESC
                """
            },
            
            'materias_criticas': {
                'query': """
                SELECT 
                    a.nombre as asignatura,
                    COUNT(c.id) as total_calificaciones,
                    COUNT(CASE WHEN c.calificacion_final < 7.0 THEN 1 END) as reprobados,
                    ROUND(COUNT(CASE WHEN c.calificacion_final < 7.0 THEN 1 END) * 100.0 / COUNT(c.id), 1) as porcentaje_reprobacion,
                    ROUND(AVG(c.calificacion_final), 2) as promedio_asignatura,
                    COUNT(DISTINCT car.nombre) as carreras_que_la_imparten,
                    GROUP_CONCAT(DISTINCT car.nombre SEPARATOR ', ') as lista_carreras
                FROM asignaturas a
                JOIN calificaciones c ON a.id = c.asignatura_id
                JOIN alumnos al ON c.alumno_id = al.id
                JOIN carreras car ON al.carrera_id = car.id
                WHERE c.calificacion_final IS NOT NULL
                GROUP BY a.id, a.nombre
                HAVING total_calificaciones >= 5
                ORDER BY porcentaje_reprobacion DESC, total_calificaciones DESC
                LIMIT 15
                """
            },
            
            'solicitudes_urgentes': {
                'query': """
                SELECT 
                    sa.id as solicitud_id,
                    CONCAT(u.nombre, ' ', u.apellido) as alumno,
                    al.matricula,
                    car.nombre as carrera,
                    sa.tipo_problema,
                    sa.urgencia,
                    sa.descripcion,
                    sa.estado,
                    sa.fecha_solicitud,
                    DATEDIFF(NOW(), sa.fecha_solicitud) as dias_pendiente,
                    CONCAT(ud.nombre, ' ', ud.apellido) as asignado_a
                FROM solicitudes_ayuda sa
                JOIN alumnos al ON sa.alumno_id = al.id
                JOIN usuarios u ON al.usuario_id = u.id
                JOIN carreras car ON al.carrera_id = car.id
                LEFT JOIN usuarios ud ON sa.asignado_a = ud.id
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
            
            'capacidad_grupos': {
                'query': """
                SELECT 
                    g.nombre as grupo,
                    car.nombre as carrera,
                    g.capacidad_maxima,
                    COUNT(al.id) as alumnos_actuales,
                    ROUND((COUNT(al.id) * 100.0 / g.capacidad_maxima), 1) as porcentaje_ocupacion,
                    (g.capacidad_maxima - COUNT(al.id)) as espacios_disponibles,
                    CASE 
                        WHEN COUNT(al.id) >= g.capacidad_maxima THEN 'LLENO'
                        WHEN COUNT(al.id) >= (g.capacidad_maxima * 0.9) THEN 'CRÍTICO'
                        WHEN COUNT(al.id) >= (g.capacidad_maxima * 0.75) THEN 'ALTO'
                        ELSE 'NORMAL'
                    END as estado_capacidad
                FROM grupos g
                JOIN carreras car ON g.carrera_id = car.id
                LEFT JOIN alumnos al ON g.id = al.grupo_id AND al.estado_alumno = 'activo'
                WHERE g.activo = 1
                GROUP BY g.id, g.nombre, car.nombre, g.capacidad_maxima
                ORDER BY porcentaje_ocupacion DESC, car.nombre, g.nombre
                """
            },
            
            'matriculas_especificas': {
                'query': """
                SELECT 
                    al.matricula,
                    CONCAT(u.nombre, ' ', u.apellido) as nombre_completo,
                    car.nombre as carrera,
                    g.nombre as grupo,
                    al.cuatrimestre_actual,
                    al.promedio_general,
                    al.estado_alumno,
                    COUNT(c.id) as total_materias,
                    COUNT(CASE WHEN c.estatus = 'aprobado' THEN 1 END) as materias_aprobadas,
                    COUNT(CASE WHEN c.estatus = 'reprobado' THEN 1 END) as materias_reprobadas,
                    COUNT(CASE WHEN c.estatus = 'cursando' THEN 1 END) as materias_cursando,
                    COUNT(rr.id) as reportes_riesgo
                FROM alumnos al
                JOIN usuarios u ON al.usuario_id = u.id
                JOIN carreras car ON al.carrera_id = car.id
                LEFT JOIN grupos g ON al.grupo_id = g.id
                LEFT JOIN calificaciones c ON al.id = c.alumno_id
                LEFT JOIN reportes_riesgo rr ON al.id = rr.alumno_id AND rr.estado IN ('abierto', 'en_proceso')
                WHERE al.matricula = %s
                GROUP BY al.id, al.matricula, u.nombre, u.apellido, car.nombre, g.nombre, al.cuatrimestre_actual, al.promedio_general, al.estado_alumno
                """
            }
        }
    
    def generate_query(self, message: str, intent: str, user_id: Optional[int] = None, role: str = 'directivo') -> Tuple[Optional[str], list]:
        message_lower = message.lower()
        
        matricula_match = re.search(r'\b\d{8,12}\b', message)
        if matricula_match and intent == 'matriculas_especificas':
            return self.directivo_queries['matriculas_especificas']['query'], [matricula_match.group()]
        
        if intent in self.directivo_queries:
            return self.directivo_queries[intent]['query'], []
        
        keyword_mappings = {
            'cuantos alumnos': 'estadisticas_generales',
            'cuantos profesores': 'estadisticas_generales', 
            'donde esta el grupo': 'ubicacion_grupos',
            'que hora tiene': 'horarios_grupos',
            'peores calificaciones': 'alumnos_bajo_rendimiento',
            'bajo rendimiento': 'alumnos_bajo_rendimiento',
            'mas reprobadas': 'materias_criticas',
            'solicitudes urgentes': 'solicitudes_urgentes',
            'grupos llenos': 'capacidad_grupos',
            'carga profesor': 'profesores_carga',
            'rendimiento carrera': 'carreras_rendimiento'
        }
        
        for keyword, mapped_intent in keyword_mappings.items():
            if keyword in message_lower:
                if mapped_intent in self.directivo_queries:
                    return self.directivo_queries[mapped_intent]['query'], []
        
        return None, []
    
    def get_available_queries(self, role: str = 'directivo') -> list:
        return list(self.directivo_queries.keys())
    
    def get_query_description(self, intent: str) -> str:
        descriptions = {
            'estadisticas_generales': 'Estadísticas generales del sistema educativo',
            'alumnos_bajo_rendimiento': 'Alumnos con bajo rendimiento académico',
            'alumnos_riesgo': 'Alumnos en situación de riesgo académico',
            'ubicacion_grupos': 'Ubicación y aulas de los grupos',
            'horarios_grupos': 'Horarios detallados de todos los grupos',
            'grupos_detalle': 'Información detallada de grupos y ocupación',
            'carreras_rendimiento': 'Rendimiento académico por carrera',
            'profesores_carga': 'Carga académica de profesores',
            'materias_criticas': 'Materias con mayor índice de reprobación',
            'solicitudes_urgentes': 'Solicitudes de ayuda pendientes y urgentes',
            'capacidad_grupos': 'Capacidad y ocupación de grupos',
            'matriculas_especificas': 'Información detallada de matrícula específica'
        }
        return descriptions.get(intent, 'Consulta administrativa')