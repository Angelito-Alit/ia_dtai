class FixedQueryGenerator:
    def __init__(self):
        self.query_templates = {
            'all_groups': """
                SELECT g.nombre as grupo, a.nombre as asignatura, g.cuatrimestre,
                       COUNT(al.id) as total_alumnos, g.capacidad_maxima,
                       CONCAT(u.nombre, ' ', u.apellido) as profesor
                FROM grupos g
                JOIN asignaturas a ON g.asignatura_id = a.id
                LEFT JOIN usuarios u ON g.profesor_id = u.id
                LEFT JOIN alumnos al ON g.id = al.grupo_id
                WHERE g.activo = 1
                GROUP BY g.id, g.nombre, a.nombre
                ORDER BY g.nombre
            """,
            'student_count': """
                SELECT COUNT(*) as total_alumnos
                FROM alumnos
                WHERE estado_alumno = 'activo'
            """,
            'active_teachers': """
                SELECT COUNT(*) as total_profesores
                FROM usuarios u
                JOIN profesores p ON u.id = p.usuario_id
                WHERE u.activo = 1
            """,
            'directors_by_level': """
                SELECT d.nivel_acceso, COUNT(*) as total_directivos
                FROM usuarios u
                JOIN directivos d ON u.id = d.usuario_id
                WHERE u.activo = 1
                GROUP BY d.nivel_acceso
                ORDER BY total_directivos DESC
            """,
            'users_by_role': """
                SELECT u.rol, COUNT(*) as total_usuarios
                FROM usuarios u
                WHERE u.activo = 1
                GROUP BY u.rol
                ORDER BY total_usuarios DESC
            """,
            'groups_by_career': """
                SELECT c.nombre as carrera, COUNT(g.id) as total_grupos
                FROM carreras c
                LEFT JOIN asignaturas a ON c.id = a.carrera_id
                LEFT JOIN grupos g ON a.id = g.asignatura_id
                WHERE c.activa = 1
                GROUP BY c.id, c.nombre
                ORDER BY total_grupos DESC
            """,
            'permanent_dropouts': """
                SELECT COUNT(*) as total_bajas_definitivas
                FROM alumnos
                WHERE estado_alumno = 'baja_definitiva'
            """,
            'tutor_ratio': """
                SELECT 
                    COUNT(CASE WHEN EXISTS(SELECT 1 FROM alumnos WHERE tutor_id = p.usuario_id) THEN 1 END) as tutores,
                    COUNT(*) as total_profesores,
                    ROUND(COUNT(CASE WHEN EXISTS(SELECT 1 FROM alumnos WHERE tutor_id = p.usuario_id) THEN 1 END) * 100.0 / COUNT(*), 2) as porcentaje_tutores
                FROM profesores p
                JOIN usuarios u ON p.usuario_id = u.id
                WHERE u.activo = 1
            """,
            'active_subjects': """
                SELECT COUNT(*) as total_asignaturas_activas
                FROM asignaturas
                WHERE activa = 1
            """,
            'open_reports_count': """
                SELECT COUNT(*) as reportes_abiertos
                FROM reportes_riesgo
                WHERE estado IN ('abierto', 'en_proceso')
            """,
            'pending_requests_count': """
                SELECT COUNT(*) as solicitudes_pendientes
                FROM solicitudes_ayuda
                WHERE estado = 'pendiente'
            """,
            'groups_by_year': """
                SELECT COUNT(*) as grupos_creados
                FROM grupos
                WHERE YEAR(fecha_creacion) = %s
            """,
            'students_by_period': """
                SELECT COUNT(*) as alumnos_inscritos
                FROM alumnos
                WHERE ciclo_ingreso = %s
            """,
            'requests_by_year': """
                SELECT COUNT(*) as solicitudes_año
                FROM solicitudes_ayuda
                WHERE YEAR(fecha_solicitud) = %s
            """,
            'grades_by_cycle': """
                SELECT COUNT(*) as calificaciones_registradas
                FROM calificaciones
                WHERE ciclo_escolar = %s
            """,
            'career_most_new_students': """
                SELECT c.nombre as carrera, COUNT(al.id) as alumnos_nuevos
                FROM carreras c
                JOIN alumnos al ON c.id = al.carrera_id
                WHERE al.ciclo_ingreso = %s
                GROUP BY c.id, c.nombre
                ORDER BY alumnos_nuevos DESC
                LIMIT 1
            """,
            'career_most_subjects': """
                SELECT c.nombre as carrera, COUNT(a.id) as total_asignaturas
                FROM carreras c
                LEFT JOIN asignaturas a ON c.id = a.carrera_id
                WHERE c.activa = 1
                GROUP BY c.id, c.nombre
                ORDER BY total_asignaturas DESC
                LIMIT 1
            """,
            'subject_most_practical_hours': """
                SELECT nombre as asignatura, horas_practicas
                FROM asignaturas
                WHERE activa = 1
                ORDER BY horas_practicas DESC
                LIMIT 1
            """,
            'highest_complexity_subjects': """
                SELECT a.nombre as asignatura, a.nivel_complejidad, c.nombre as carrera
                FROM asignaturas a
                JOIN carreras c ON a.carrera_id = c.id
                WHERE a.activa = 1
                ORDER BY a.nivel_complejidad DESC
                LIMIT 5
            """,
            'career_most_teachers': """
                SELECT c.nombre as carrera, COUNT(DISTINCT g.profesor_id) as total_profesores
                FROM carreras c
                JOIN asignaturas a ON c.id = a.carrera_id
                JOIN grupos g ON a.id = g.asignatura_id
                WHERE c.activa = 1 AND g.activo = 1
                GROUP BY c.id, c.nombre
                ORDER BY total_profesores DESC
                LIMIT 1
            """,
            'students_per_term_career': """
                SELECT al.cuatrimestre_actual, COUNT(*) as total_alumnos
                FROM alumnos al
                JOIN carreras c ON al.carrera_id = c.id
                WHERE c.nombre LIKE %s AND al.estado_alumno = 'activo'
                GROUP BY al.cuatrimestre_actual
                ORDER BY al.cuatrimestre_actual
            """,
            'teacher_most_subjects': """
                SELECT CONCAT(u.nombre, ' ', u.apellido) as profesor, COUNT(DISTINCT a.id) as total_asignaturas
                FROM usuarios u
                JOIN grupos g ON u.id = g.profesor_id
                JOIN asignaturas a ON g.asignatura_id = a.id
                WHERE u.activo = 1 AND g.activo = 1
                GROUP BY u.id, u.nombre, u.apellido
                ORDER BY total_asignaturas DESC
                LIMIT 1
            """,
            'teachers_multiple_groups': """
                SELECT CONCAT(u.nombre, ' ', u.apellido) as profesor, COUNT(g.id) as total_grupos
                FROM usuarios u
                JOIN grupos g ON u.id = g.profesor_id
                WHERE u.activo = 1 AND g.activo = 1
                GROUP BY u.id, u.nombre, u.apellido
                HAVING COUNT(g.id) > 1
                ORDER BY total_grupos DESC
            """,
            'inactive_teachers': """
                SELECT CONCAT(u.nombre, ' ', u.apellido) as profesor, u.fecha_ultimo_acceso
                FROM usuarios u
                JOIN profesores p ON u.id = p.usuario_id
                WHERE u.activo = 0
                ORDER BY u.apellido, u.nombre
            """,
            'teachers_per_career': """
                SELECT c.nombre as carrera, COUNT(DISTINCT g.profesor_id) as total_profesores
                FROM carreras c
                JOIN asignaturas a ON c.id = a.carrera_id
                JOIN grupos g ON a.id = g.asignatura_id
                WHERE c.activa = 1 AND g.activo = 1
                GROUP BY c.id, c.nombre
                ORDER BY total_profesores DESC
            """,
            'highest_gpa_student': """
                SELECT CONCAT(u.nombre, ' ', u.apellido) as alumno, al.matricula, al.promedio_general
                FROM alumnos al
                JOIN usuarios u ON al.usuario_id = u.id
                WHERE al.estado_alumno = 'activo' AND al.promedio_general IS NOT NULL
                ORDER BY al.promedio_general DESC
                LIMIT 1
            """,
            'low_gpa_students': """
                SELECT CONCAT(u.nombre, ' ', u.apellido) as alumno, al.matricula, al.promedio_general
                FROM alumnos al
                JOIN usuarios u ON al.usuario_id = u.id
                WHERE al.estado_alumno = 'activo' AND al.promedio_general < 6.0
                ORDER BY al.promedio_general
            """,
            'final_term_students': """
                SELECT COUNT(*) as alumnos_ultimo_cuatrimestre
                FROM alumnos al
                JOIN carreras c ON al.carrera_id = c.id
                WHERE al.estado_alumno = 'activo' 
                AND al.cuatrimestre_actual = c.duracion_cuatrimestres
            """,
            'students_with_group': """
                SELECT COUNT(*) as alumnos_con_grupo
                FROM alumnos
                WHERE estado_alumno = 'activo' AND grupo_id IS NOT NULL
            """,
            'students_multiple_reports': """
                SELECT COUNT(*) as alumnos_multiples_reportes
                FROM (
                    SELECT rr.alumno_id, COUNT(*) as total_reportes
                    FROM reportes_riesgo rr
                    GROUP BY rr.alumno_id
                    HAVING COUNT(*) > 1
                ) as subquery
            """,
            'passed_ordinary_cycle': """
                SELECT COUNT(*) as aprobados_ordinario
                FROM calificaciones c
                WHERE c.ciclo_escolar = %s 
                AND c.estatus = 'aprobado' 
                AND c.tipo_evaluacion = 'ordinario'
            """,
            'subjects_most_extraordinary': """
                SELECT a.nombre as asignatura, COUNT(*) as casos_extraordinarios
                FROM calificaciones c
                JOIN asignaturas a ON c.asignatura_id = a.id
                WHERE c.tipo_evaluacion = 'extraordinario'
                GROUP BY a.id, a.nombre
                ORDER BY casos_extraordinarios DESC
                LIMIT 10
            """,
            'average_per_subject': """
                SELECT a.nombre as asignatura, ROUND(AVG(c.calificacion_final), 2) as promedio_general
                FROM calificaciones c
                JOIN asignaturas a ON c.asignatura_id = a.id
                WHERE c.calificacion_final IS NOT NULL
                GROUP BY a.id, a.nombre
                ORDER BY promedio_general DESC
            """,
            'teacher_most_failing_grades': """
                SELECT CONCAT(u.nombre, ' ', u.apellido) as profesor, COUNT(*) as calificaciones_reprobatorias
                FROM calificaciones c
                JOIN usuarios u ON c.profesor_id = u.id
                WHERE c.calificacion_final < 7.0
                GROUP BY u.id, u.nombre, u.apellido
                ORDER BY calificaciones_reprobatorias DESC
                LIMIT 1
            """,
            'average_grade_per_group': """
                SELECT g.nombre as grupo, ROUND(AVG(c.calificacion_final), 2) as promedio_grupo
                FROM calificaciones c
                JOIN alumnos al ON c.alumno_id = al.id
                JOIN grupos g ON al.grupo_id = g.id
                WHERE c.calificacion_final IS NOT NULL
                GROUP BY g.id, g.nombre
                ORDER BY promedio_grupo DESC
            """,
            'most_used_classroom': """
                SELECT au.nombre as aula, COUNT(*) as veces_usada_semana
                FROM horarios h
                JOIN grupos g ON h.grupo_id = g.id
                JOIN aulas au ON g.aula_id = au.id
                WHERE g.activo = 1
                GROUP BY au.id, au.nombre
                ORDER BY veces_usada_semana DESC
                LIMIT 1
            """,
            'largest_group': """
                SELECT g.nombre as grupo, COUNT(al.id) as total_alumnos_inscritos
                FROM grupos g
                LEFT JOIN alumnos al ON g.id = al.grupo_id
                WHERE g.activo = 1
                GROUP BY g.id, g.nombre
                ORDER BY total_alumnos_inscritos DESC
                LIMIT 1
            """,
            'groups_capacity_over': """
                SELECT COUNT(*) as grupos_capacidad_mayor
                FROM grupos
                WHERE capacidad_maxima > %s AND activo = 1
            """,
            'groups_same_classroom_schedule': """
                SELECT au.nombre as aula, h.dia_semana, h.hora_inicio, h.hora_fin,
                       GROUP_CONCAT(g.nombre) as grupos_conflicto
                FROM horarios h
                JOIN grupos g ON h.grupo_id = g.id
                JOIN aulas au ON g.aula_id = au.id
                WHERE g.activo = 1
                GROUP BY au.id, h.dia_semana, h.hora_inicio, h.hora_fin
                HAVING COUNT(*) > 1
                ORDER BY au.nombre, h.dia_semana, h.hora_inicio
            """,
            'saturday_classes': """
                SELECT COUNT(*) as clases_sabados
                FROM horarios h
                JOIN grupos g ON h.grupo_id = g.id
                WHERE h.dia_semana = 'sabado' AND g.activo = 1
            """,
            'reports_by_type': """
                SELECT rr.tipo_riesgo, COUNT(*) as total_reportes
                FROM reportes_riesgo rr
                GROUP BY rr.tipo_riesgo
                ORDER BY total_reportes DESC
            """,
            'students_multiple_critical_reports': """
                SELECT CONCAT(u.nombre, ' ', u.apellido) as alumno, al.matricula, COUNT(*) as reportes_criticos
                FROM reportes_riesgo rr
                JOIN alumnos al ON rr.alumno_id = al.id
                JOIN usuarios u ON al.usuario_id = u.id
                WHERE rr.nivel_riesgo = 'critico'
                GROUP BY al.id, u.nombre, u.apellido, al.matricula
                HAVING COUNT(*) > 1
                ORDER BY reportes_criticos DESC
            """,
            'resolved_reports': """
                SELECT COUNT(*) as reportes_resueltos
                FROM reportes_riesgo
                WHERE estado = 'resuelto'
            """,
            'reports_no_follow_up': """
                SELECT COUNT(*) as reportes_sin_seguimiento
                FROM reportes_riesgo
                WHERE fecha_seguimiento IS NULL AND estado IN ('abierto', 'en_proceso')
            """,
            'teachers_over_5_reports': """
                SELECT CONCAT(u.nombre, ' ', u.apellido) as profesor, COUNT(*) as total_reportes
                FROM reportes_riesgo rr
                JOIN usuarios u ON rr.profesor_id = u.id
                GROUP BY u.id, u.nombre, u.apellido
                HAVING COUNT(*) > 5
                ORDER BY total_reportes DESC
            """,
            'promedio_alumno': """
                SELECT al.matricula, u.nombre, u.apellido, al.promedio_general
                FROM alumnos al
                JOIN usuarios u ON al.usuario_id = u.id
                WHERE CONCAT(u.nombre, ' ', u.apellido) LIKE %s
            """,
            'alumnos_cuatrimestre': """
                SELECT u.nombre, u.apellido, al.matricula, al.cuatrimestre_actual
                FROM alumnos al
                JOIN usuarios u ON al.usuario_id = u.id
                WHERE al.cuatrimestre_actual = %s AND al.estado_alumno = 'activo'
            """,
            'alumnos_por_carrera': """
                SELECT c.nombre as carrera, COUNT(al.id) as total_alumnos
                FROM carreras c
                LEFT JOIN alumnos al ON c.id = al.carrera_id AND al.estado_alumno = 'activo'
                GROUP BY c.id, c.nombre
                ORDER BY total_alumnos DESC
            """,
            'asignaturas_alumno': """
                SELECT a.nombre as asignatura, c.calificacion_final, c.estatus,
                       c.parcial_1, c.parcial_2, c.parcial_3
                FROM calificaciones c
                JOIN asignaturas a ON c.asignatura_id = a.id
                JOIN alumnos al ON c.alumno_id = al.id
                JOIN usuarios u ON al.usuario_id = u.id
                WHERE CONCAT(u.nombre, ' ', u.apellido) LIKE %s
                ORDER BY a.nombre
            """,
            'reportes_riesgo_alumno': """
                SELECT rr.fecha_reporte, rr.nivel_riesgo, rr.tipo_riesgo, rr.descripcion,
                       rr.acciones_recomendadas, rr.estado
                FROM reportes_riesgo rr
                JOIN alumnos al ON rr.alumno_id = al.id
                JOIN usuarios u ON al.usuario_id = u.id
                WHERE CONCAT(u.nombre, ' ', u.apellido) LIKE %s
                ORDER BY rr.fecha_reporte DESC
            """,
            'grupos_profesor': """
                SELECT g.nombre as grupo, a.nombre as asignatura, g.ciclo_escolar,
                       g.cuatrimestre, COUNT(al.id) as total_alumnos
                FROM grupos g
                JOIN asignaturas a ON g.asignatura_id = a.id
                JOIN usuarios u ON g.profesor_id = u.id
                LEFT JOIN alumnos al ON g.id = al.grupo_id
                WHERE CONCAT(u.nombre, ' ', u.apellido) LIKE %s
                GROUP BY g.id, g.nombre, a.nombre
                ORDER BY g.nombre
            """,
            'horarios_profesor': """
                SELECT h.dia_semana, h.hora_inicio, h.hora_fin, a.nombre as asignatura,
                       g.nombre as grupo, au.nombre as aula
                FROM horarios h
                JOIN grupos g ON h.grupo_id = g.id
                JOIN asignaturas a ON g.asignatura_id = a.id
                JOIN usuarios u ON g.profesor_id = u.id
                LEFT JOIN aulas au ON g.aula_id = au.id
                WHERE CONCAT(u.nombre, ' ', u.apellido) LIKE %s
                ORDER BY h.dia_semana, h.hora_inicio
            """
        }
    
    def generate_query(self, query_type, parameters):
        if query_type not in self.query_templates:
            return None, []
        
        template = self.query_templates[query_type]
        param_count = template.count('%s')
        
        if param_count != len(parameters):
            return None, []
        
        return template, parameters
    
    def format_parameters(self, extracted_data, missing_data):
        params = []
        
        for field, value in extracted_data.items():
            if 'nombre' in field:
                params.append(f'%{value}%')
            elif field in ['numero_cuatrimestre', 'numero_capacidad', 'año', 'id_reporte', 'id_solicitud', 'id_post']:
                try:
                    params.append(int(value))
                except:
                    params.append(value)
            else:
                params.append(value)
        
        return params