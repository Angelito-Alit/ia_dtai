self.query_templates = {
            # Consultas generales
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
            
            # Análisis por año y periodo
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
            
            # Datos de carrera y asignatura
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
            
            # Profesores
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
            
            # Alumnos
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
            
            # Calificaciones
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
            
            # Horarios y grupos
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
            
            # Reportes de riesgo
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
            
            # Solicitudes y chat
            'requests_per_director': """
                SELECT CONCAT(u.nombre, ' ', u.apellido) as directivo, COUNT(*) as solicitudes_respondidas
                FROM solicitudes_ayuda sa
                JOIN usuarios u ON sa.directivo_asignado = u.id
                WHERE sa.estado IN ('atendida', 'resuelta')
                GROUP BY u.id, u.nombre, u.apellido
                ORDER BY solicitudes_respondidas DESC
            """,
            'students_most_chat_usage': """
                SELECT CONCAT(u.nombre, ' ', u.apellido) as alumno, al.matricula, COUNT(*) as veces_usado_chat
                FROM chat_mensajes cm
                JOIN solicitudes_ayuda sa ON cm.solicitud_id = sa.id
                JOIN alumnos al ON sa.alumno_id = al.id
                JOIN usuarios u ON al.usuario_id = u.id
                WHERE cm.remitente = 'alumno'
                GROUP BY al.id, u.nombre, u.apellido, al.matricula
                ORDER BY veces_usado_chat DESC
                LIMIT 10
            """,
            'in_person_requests': """
                SELECT COUNT(*) as solicitudes_presenciales
                FROM solicitudes_ayuda
                WHERE tipo_contacto_preferido = 'presencial'
            """,
            'average_response_time': """
                SELECT ROUND(AVG(TIMESTAMPDIFF(HOUR, sa.fecha_solicitud, 
                    (SELECT MIN(cm.fecha_mensaje) 
                     FROM chat_mensajes cm 
                     WHERE cm.solicitud_id = sa.id AND cm.remitente = 'directivo'))), 2) as promedio_horas_respuesta
                FROM solicitudes_ayuda sa
                WHERE sa.estado != 'pendiente'
            """,
            'most_common_problem': """
                SELECT sa.tipo_problema, COUNT(*) as veces_reportado
                FROM solicitudes_ayuda sa
                GROUP BY sa.tipo_problema
                ORDER BY veces_reportado DESC
                LIMIT 1
            """,
            
            # Noticias y foro
            'most_viewed_news': """
                SELECT n.titulo, n.vistas, CONCAT(u.nombre, ' ', u.apellido) as autor
                FROM noticias n
                JOIN usuarios u ON n.autor_id = u.id
                WHERE n.activa = 1
                ORDER BY n.vistas DESC
                LIMIT 10
            """,
            'posts_per_forum_category': """
                SELECT fc.nombre as categoria, COUNT(fp.id) as total_publicaciones
                FROM foro_categorias fc
                LEFT JOIN foro_posts fp ON fc.id = fp.categoria_id
                GROUP BY fc.id, fc.nombre
                ORDER BY total_publicaciones DESC
            """,
            'user_most_posts': """
                SELECT CONCAT(u.nombre, ' ', u.apellido) as usuario, COUNT(*) as total_posts
                FROM foro_posts fp
                JOIN usuarios u ON fp.usuario_id = u.id
                GROUP BY u.id, u.nombre, u.apellido
                ORDER BY total_posts DESC
                LIMIT 1
            """,
            'bookmark_usage': """
                SELECT COUNT(*) as total_bookmarks
                FROM foro_interacciones
                WHERE tipo_interaccion = 'bookmark'
            """,
            'most_liked_comments': """
                SELECT fc.contenido, COUNT(fi.id) as total_likes
                FROM foro_comentarios fc
                LEFT JOIN foro_interacciones fi ON fc.id = fi.comentario_id
                WHERE fi.tipo_interaccion = 'like'
                GROUP BY fc.id, fc.contenido
                ORDER BY total_likes DESC
                LIMIT 10
            """,
            
            # Encuestas
            'survey_most_responses': """
                SELECT e.titulo, COUNT(er.id) as total_respuestas
                FROM encuestas e
                LEFT JOIN encuestas_respuestas er ON e.id = er.encuesta_id
                GROUP BY e.id, e.titulo
                ORDER BY total_respuestas DESC
                LIMIT 1
            """,
            'students_no_survey_response': """
                SELECT COUNT(*) as alumnos_sin_respuesta
                FROM alumnos al
                WHERE al.estado_alumno = 'activo'
                AND NOT EXISTS (
                    SELECT 1 FROM encuestas_respuestas er
                    JOIN encuestas e ON er.encuesta_id = e.id
                    WHERE er.alumno_id = al.id AND e.obligatoria = 1
                )
            """,
            'most_selected_option_vulnerability': """
                SELECT er.respuesta, COUNT(*) as veces_seleccionada
                FROM encuestas_respuestas er
                JOIN encuestas e ON er.encuesta_id = e.id
                WHERE e.tipo = 'vulnerabilidad'
                GROUP BY er.respuesta
                ORDER BY veces_seleccionada DESC
                LIMIT 1
            """,
            'surveys_per_teacher': """
                SELECT CONCAT(u.nombre, ' ', u.apellido) as profesor, COUNT(*) as encuestas_creadas
                FROM encuestas e
                JOIN usuarios u ON e.creador_id = u.id
                JOIN profesores p ON u.id = p.usuario_id
                GROUP BY u.id, u.nombre, u.apellido
                ORDER BY encuestas_creadas DESC
            """,
            'survey_no_answers_frequency': """
                SELECT ep.pregunta, COUNT(*) as respuestas_no
                FROM encuestas_respuestas er
                JOIN encuestas_preguntas ep ON er.pregunta_id = ep.id
                JOIN encuestas e ON ep.encuesta_id = e.id
                WHERE e.titulo LIKE %s AND er.respuesta = 'No'
                GROUP BY ep.id, ep.pregunta
                ORDER BY respuestas_no DESC
            """,
            
            # Consultas existentes que ya tenías
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
            'alumnos_bajas': """
                SELECT u.nombre, u.apellido, al.matricula, al.estado_alumno, c.nombre as carrera
                FROM alumnos al
                JOIN usuarios u ON al.usuario_id = u.id
                JOIN carreras c ON al.carrera_id = c.id
                WHERE al.estado_alumno IN ('baja_temporal', 'baja_definitiva')
                ORDER BY al.estado_alumno, u.apellido
            """,
            'grupo_aula_alumno': """
                SELECT u.nombre, u.apellido, g.nombre as grupo, au.nombre as aula
                FROM alumnos al
                JOIN usuarios u ON al.usuario_id = u.id
                JOIN grupos g ON al.grupo_id = g.id
                LEFT JOIN aulas au ON g.aula_id = au.id
                WHERE CONCAT(u.nombre, ' ', u.apellido) LIKE %s
            """,
            'contacto_alumno': """
                SELECT u.nombre, u.apellido, u.email, u.telefono, al.matricula,
                       CONCAT(tutor.nombre, ' ', tutor.apellido) as tutor_academico
                FROM alumnos al
                JOIN usuarios u ON al.usuario_id = u.id
                LEFT JOIN usuarios tutor ON al.tutor_id = tutor.id
                WHERE CONCAT(u.nombre, ' ', u.apellido) LIKE %s
            """,
            'evolucion_promedio': """
                SELECT c.fecha_calificacion, a.nombre as asignatura, c.calificacion_final,
                       AVG(c.calificacion_final) OVER (ORDER BY c.fecha_calificacion) as promedio_acumulado
                FROM calificaciones c
                JOIN asignaturas a ON c.asignatura_id = a.id
                JOIN alumnos al ON c.alumno_id = al.id
                JOIN usuarios u ON al.usuario_id = u.id
                WHERE CONCAT(u.nombre, ' ', u.apellido) LIKE %s
                ORDER BY c.fecha_calificacion
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
            'solicitudes_ayuda_alumno': """
                SELECT sa.fecha_solicitud, sa.tipo_problema, sa.descripcion,
                       sa.nivel_urgencia, sa.estado
                FROM solicitudes_ayuda sa
                JOIN alumnos al ON sa.alumno_id = al.id
                JOIN usuarios u ON al.usuario_id = u.id
                WHERE CONCAT(u.nombre, ' ', u.apellido) LIKE %s
                ORDER BY sa.fecha_solicitud DESC
            """,
            'encuestas_alumno': """
                SELECT e.titulo, er.fecha_respuesta, er.respuesta
                FROM encuestas_respuestas er
                JOIN encuestas e ON er.encuesta_id = e.id
                JOIN alumnos al ON er.alumno_id = al.id
                JOIN usuarios u ON al.usuario_id = u.id
                WHERE CONCAT(u.nombre, ' ', u.apellido) LIKE %s
                ORDER BY er.fecha_respuesta DESC
            """,
            'participacion_foro_alumno': """
                SELECT fp.titulo, fp.contenido, fp.fecha_publicacion, fp.vistas
                FROM foro_posts fp
                JOIN usuarios u ON fp.usuario_id = u.id
                WHERE CONCAT(u.nombre, ' ', u.apellido) LIKE %s
                ORDER BY fp.fecha_publicacion DESC
            """,
            'interacciones_alumno': """
                SELECT fi.tipo_interaccion, fp.titulo as post_titulo, fi.fecha_interaccion
                FROM foro_interacciones fi
                JOIN foro_posts fp ON fi.post_id = fp.id
                JOIN usuarios u ON fi.usuario_id = u.id
                WHERE CONCAT(u.nombre, ' ', u.apellido) LIKE %s
                ORDER BY fi.fecha_interaccion DESC
            """,
            'asignaturas_profesor': """
                SELECT DISTINCT a.nombre as asignatura, a.horas_teoricas, a.horas_practicas
                FROM asignaturas a
                JOIN grupos g ON a.id = g.asignatura_id
                JOIN usuarios u ON g.profesor_id = u.id
                WHERE CONCAT(u.nombre, ' ', u.apellido) LIKE %s
                ORDER BY a.nombre
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
        }class AdvancedQueryGenerator:
    def __init__(self):
        self.query_templates = {
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
            'alumnos_bajas': """
                SELECT u.nombre, u.apellido, al.matricula, al.estado_alumno, c.nombre as carrera
                FROM alumnos al
                JOIN usuarios u ON al.usuario_id = u.id
                JOIN carreras c ON al.carrera_id = c.id
                WHERE al.estado_alumno IN ('baja_temporal', 'baja_definitiva')
                ORDER BY al.estado_alumno, u.apellido
            """,
            'grupo_aula_alumno': """
                SELECT u.nombre, u.apellido, g.nombre as grupo, au.nombre as aula
                FROM alumnos al
                JOIN usuarios u ON al.usuario_id = u.id
                JOIN grupos g ON al.grupo_id = g.id
                LEFT JOIN aulas au ON g.aula_id = au.id
                WHERE CONCAT(u.nombre, ' ', u.apellido) LIKE %s
            """,
            'contacto_alumno': """
                SELECT u.nombre, u.apellido, u.email, u.telefono, al.matricula,
                       CONCAT(tutor.nombre, ' ', tutor.apellido) as tutor_academico
                FROM alumnos al
                JOIN usuarios u ON al.usuario_id = u.id
                LEFT JOIN usuarios tutor ON al.tutor_id = tutor.id
                WHERE CONCAT(u.nombre, ' ', u.apellido) LIKE %s
            """,
            'evolucion_promedio': """
                SELECT c.fecha_calificacion, a.nombre as asignatura, c.calificacion_final,
                       AVG(c.calificacion_final) OVER (ORDER BY c.fecha_calificacion) as promedio_acumulado
                FROM calificaciones c
                JOIN asignaturas a ON c.asignatura_id = a.id
                JOIN alumnos al ON c.alumno_id = al.id
                JOIN usuarios u ON al.usuario_id = u.id
                WHERE CONCAT(u.nombre, ' ', u.apellido) LIKE %s
                ORDER BY c.fecha_calificacion
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
            'solicitudes_ayuda_alumno': """
                SELECT sa.fecha_solicitud, sa.tipo_problema, sa.descripcion,
                       sa.nivel_urgencia, sa.estado
                FROM solicitudes_ayuda sa
                JOIN alumnos al ON sa.alumno_id = al.id
                JOIN usuarios u ON al.usuario_id = u.id
                WHERE CONCAT(u.nombre, ' ', u.apellido) LIKE %s
                ORDER BY sa.fecha_solicitud DESC
            """,
            'encuestas_alumno': """
                SELECT e.titulo, er.fecha_respuesta, er.respuesta
                FROM encuestas_respuestas er
                JOIN encuestas e ON er.encuesta_id = e.id
                JOIN alumnos al ON er.alumno_id = al.id
                JOIN usuarios u ON al.usuario_id = u.id
                WHERE CONCAT(u.nombre, ' ', u.apellido) LIKE %s
                ORDER BY er.fecha_respuesta DESC
            """,
            'participacion_foro_alumno': """
                SELECT fp.titulo, fp.contenido, fp.fecha_publicacion, fp.vistas
                FROM foro_posts fp
                JOIN usuarios u ON fp.usuario_id = u.id
                WHERE CONCAT(u.nombre, ' ', u.apellido) LIKE %s
                ORDER BY fp.fecha_publicacion DESC
            """,
            'interacciones_alumno': """
                SELECT fi.tipo_interaccion, fp.titulo as post_titulo, fi.fecha_interaccion
                FROM foro_interacciones fi
                JOIN foro_posts fp ON fi.post_id = fp.id
                JOIN usuarios u ON fi.usuario_id = u.id
                WHERE CONCAT(u.nombre, ' ', u.apellido) LIKE %s
                ORDER BY fi.fecha_interaccion DESC
            """,
            'asignaturas_profesor': """
                SELECT DISTINCT a.nombre as asignatura, a.horas_teoricas, a.horas_practicas
                FROM asignaturas a
                JOIN grupos g ON a.id = g.asignatura_id
                JOIN usuarios u ON g.profesor_id = u.id
                WHERE CONCAT(u.nombre, ' ', u.apellido) LIKE %s
                ORDER BY a.nombre
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
            """,
            'alumnos_grupo_profesor': """
                SELECT u_al.nombre, u_al.apellido, al.matricula
                FROM alumnos al
                JOIN usuarios u_al ON al.usuario_id = u_al.id
                JOIN grupos g ON al.grupo_id = g.id
                JOIN usuarios u_prof ON g.profesor_id = u_prof.id
                WHERE CONCAT(u_prof.nombre, ' ', u_prof.apellido) LIKE %s
                AND g.nombre LIKE %s
                ORDER BY u_al.apellido, u_al.nombre
            """,
            'reportes_emitidos_profesor': """
                SELECT u_al.nombre, u_al.apellido, rr.nivel_riesgo, rr.tipo_riesgo,
                       rr.fecha_reporte, rr.descripcion
                FROM reportes_riesgo rr
                JOIN alumnos al ON rr.alumno_id = al.id
                JOIN usuarios u_al ON al.usuario_id = u_al.id
                JOIN usuarios u_prof ON rr.profesor_id = u_prof.id
                WHERE CONCAT(u_prof.nombre, ' ', u_prof.apellido) LIKE %s
                ORDER BY rr.fecha_reporte DESC
            """,
            'calificaciones_profesor': """
                SELECT u_al.nombre, u_al.apellido, a.nombre as asignatura,
                       c.calificacion_final, c.fecha_calificacion
                FROM calificaciones c
                JOIN alumnos al ON c.alumno_id = al.id
                JOIN usuarios u_al ON al.usuario_id = u_al.id
                JOIN asignaturas a ON c.asignatura_id = a.id
                JOIN usuarios u_prof ON c.profesor_id = u_prof.id
                WHERE CONCAT(u_prof.nombre, ' ', u_prof.apellido) LIKE %s
                ORDER BY c.fecha_calificacion DESC
            """,
            'experiencia_profesor': """
                SELECT u.nombre, u.apellido, p.anos_experiencia, p.especialidad,
                       p.grado_academico, p.institucion_procedencia
                FROM profesores p
                JOIN usuarios u ON p.usuario_id = u.id
                WHERE CONCAT(u.nombre, ' ', u.apellido) LIKE %s
            """,
            'tutor_academico': """
                SELECT u.nombre, u.apellido, COUNT(al.id) as alumnos_tutorados
                FROM usuarios u
                JOIN profesores p ON u.id = p.usuario_id
                LEFT JOIN alumnos al ON u.id = al.tutor_id
                WHERE CONCAT(u.nombre, ' ', u.apellido) LIKE %s
                GROUP BY u.id, u.nombre, u.apellido
            """,
            'noticias_directivo': """
                SELECT n.titulo, n.contenido, n.fecha_publicacion, n.activa, n.destacada
                FROM noticias n
                JOIN usuarios u ON n.autor_id = u.id
                WHERE CONCAT(u.nombre, ' ', u.apellido) LIKE %s
                ORDER BY n.fecha_publicacion DESC
            """,
            'categorias_foro_directivo': """
                SELECT fc.nombre as categoria, COUNT(fp.id) as total_posts
                FROM foro_categorias fc
                LEFT JOIN foro_posts fp ON fc.id = fp.categoria_id
                JOIN usuarios u ON fc.creador_id = u.id
                WHERE CONCAT(u.nombre, ' ', u.apellido) LIKE %s
                GROUP BY fc.id, fc.nombre
                ORDER BY total_posts DESC
            """,
            'solicitudes_directivo': """
                SELECT sa.fecha_solicitud, sa.tipo_problema, sa.nivel_urgencia,
                       sa.estado, u_al.nombre as alumno_nombre, u_al.apellido as alumno_apellido
                FROM solicitudes_ayuda sa
                JOIN alumnos al ON sa.alumno_id = al.id
                JOIN usuarios u_al ON al.usuario_id = u_al.id
                JOIN usuarios u_dir ON sa.directivo_asignado = u_dir.id
                WHERE CONCAT(u_dir.nombre, ' ', u_dir.apellido) LIKE %s
                ORDER BY sa.fecha_solicitud DESC
            """,
            'conversaciones_directivo': """
                SELECT cc.fecha_inicio, cc.tema, COUNT(cm.id) as total_mensajes
                FROM conversaciones_chatbot cc
                LEFT JOIN chatbot_mensajes cm ON cc.id = cm.conversacion_id
                JOIN usuarios u ON cc.usuario_id = u.id
                WHERE CONCAT(u.nombre, ' ', u.apellido) LIKE %s
                GROUP BY cc.id, cc.fecha_inicio, cc.tema
                ORDER BY cc.fecha_inicio DESC
            """,
            'asignaturas_carrera': """
                SELECT a.nombre as asignatura, a.cuatrimestre, a.horas_teoricas, a.horas_practicas
                FROM asignaturas a
                JOIN carreras c ON a.carrera_id = c.id
                WHERE c.nombre LIKE %s
                ORDER BY a.cuatrimestre, a.nombre
            """,
            'asignaturas_cuatrimestre_carrera': """
                SELECT a.nombre as asignatura, a.horas_teoricas, a.horas_practicas
                FROM asignaturas a
                JOIN carreras c ON a.carrera_id = c.id
                WHERE a.cuatrimestre = %s AND c.nombre LIKE %s
                ORDER BY a.nombre
            """,
            'asignaturas_complejidad': """
                SELECT a.nombre as asignatura, a.nivel_complejidad, c.nombre as carrera
                FROM asignaturas a
                JOIN carreras c ON a.carrera_id = c.id
                ORDER BY a.nivel_complejidad DESC, a.nombre
                LIMIT 20
            """,
            'carreras_activas': """
                SELECT nombre, descripcion, duracion_cuatrimestres, fecha_creacion
                FROM carreras
                WHERE activa = 1
                ORDER BY nombre
            """,
            'horas_asignatura': """
                SELECT nombre, horas_teoricas, horas_practicas, 
                       (horas_teoricas + horas_practicas) as total_horas
                FROM asignaturas
                WHERE nombre LIKE %s
            """,
            'grupos_activos': """
                SELECT g.nombre as grupo, a.nombre as asignatura, g.ciclo_escolar,
                       g.cuatrimestre, COUNT(al.id) as total_alumnos
                FROM grupos g
                JOIN asignaturas a ON g.asignatura_id = a.id
                LEFT JOIN alumnos al ON g.id = al.grupo_id
                WHERE g.activo = 1
                GROUP BY g.id, g.nombre, a.nombre
                ORDER BY g.nombre
            """,
            'tutor_grupo': """
                SELECT g.nombre as grupo, u.nombre, u.apellido
                FROM grupos g
                JOIN usuarios u ON g.tutor_id = u.id
                WHERE g.nombre LIKE %s
            """,
            'aula_grupo': """
                SELECT g.nombre as grupo, au.nombre as aula, au.capacidad
                FROM grupos g
                JOIN aulas au ON g.aula_id = au.id
                WHERE g.nombre LIKE %s
            """,
            'capacidad_grupo': """
                SELECT g.nombre as grupo, g.capacidad_maxima, COUNT(al.id) as alumnos_inscritos
                FROM grupos g
                LEFT JOIN alumnos al ON g.id = al.grupo_id
                WHERE g.nombre LIKE %s
                GROUP BY g.id, g.nombre, g.capacidad_maxima
            """,
            'horarios_grupo_dia': """
                SELECT h.hora_inicio, h.hora_fin, a.nombre as asignatura, au.nombre as aula
                FROM horarios h
                JOIN grupos g ON h.grupo_id = g.id
                JOIN asignaturas a ON g.asignatura_id = a.id
                LEFT JOIN aulas au ON g.aula_id = au.id
                WHERE g.nombre LIKE %s AND h.dia_semana = %s
                ORDER BY h.hora_inicio
            """,
            'grupos_asignatura': """
                SELECT g.nombre as grupo, u.nombre as profesor_nombre, u.apellido as profesor_apellido,
                       COUNT(al.id) as total_alumnos
                FROM grupos g
                JOIN asignaturas a ON g.asignatura_id = a.id
                JOIN usuarios u ON g.profesor_id = u.id
                LEFT JOIN alumnos al ON g.id = al.grupo_id
                WHERE a.nombre LIKE %s
                GROUP BY g.id, g.nombre, u.nombre, u.apellido
                ORDER BY g.nombre
            """,
            'alumnos_reprobados': """
                SELECT u.nombre, u.apellido, al.matricula, c.calificacion_final
                FROM calificaciones c
                JOIN alumnos al ON c.alumno_id = al.id
                JOIN usuarios u ON al.usuario_id = u.id
                JOIN asignaturas a ON c.asignatura_id = a.id
                WHERE a.nombre LIKE %s AND c.calificacion_final < 7.0
                ORDER BY c.calificacion_final, u.apellido
            """,
            'aprobados_ordinario_extraordinario': """
                SELECT c.tipo_evaluacion, COUNT(*) as total_alumnos,
                       AVG(c.calificacion_final) as promedio_calificacion
                FROM calificaciones c
                WHERE c.estatus = 'aprobado'
                GROUP BY c.tipo_evaluacion
            """,
            'calificacion_final_alumno_asignatura': """
                SELECT u.nombre, u.apellido, a.nombre as asignatura, c.calificacion_final,
                       c.parcial_1, c.parcial_2, c.parcial_3, c.estatus
                FROM calificaciones c
                JOIN alumnos al ON c.alumno_id = al.id
                JOIN usuarios u ON al.usuario_id = u.id
                JOIN asignaturas a ON c.asignatura_id = a.id
                WHERE CONCAT(u.nombre, ' ', u.apellido) LIKE %s AND a.nombre LIKE %s
            """,
            'materias_cursando': """
                SELECT a.nombre as asignatura, c.parcial_1, c.parcial_2, c.parcial_3
                FROM calificaciones c
                JOIN asignaturas a ON c.asignatura_id = a.id
                JOIN alumnos al ON c.alumno_id = al.id
                JOIN usuarios u ON al.usuario_id = u.id
                WHERE CONCAT(u.nombre, ' ', u.apellido) LIKE %s AND c.estatus = 'cursando'
                ORDER BY a.nombre
            """,
            'profesor_calificacion': """
                SELECT DISTINCT u_prof.nombre, u_prof.apellido, a.nombre as asignatura
                FROM calificaciones c
                JOIN asignaturas a ON c.asignatura_id = a.id
                JOIN usuarios u_prof ON c.profesor_id = u_prof.id
                JOIN alumnos al ON c.alumno_id = al.id
                JOIN usuarios u_al ON al.usuario_id = u_al.id
                WHERE CONCAT(u_al.nombre, ' ', u_al.apellido) LIKE %s
                ORDER BY u_prof.apellido, a.nombre
            """,
            'reportes_tipo_nivel': """
                SELECT rr.tipo_riesgo, rr.nivel_riesgo, COUNT(*) as total_reportes
                FROM reportes_riesgo rr
                GROUP BY rr.tipo_riesgo, rr.nivel_riesgo
                ORDER BY rr.nivel_riesgo, total_reportes DESC
            """,
            'reportes_abiertos': """
                SELECT u.nombre, u.apellido, al.matricula, rr.nivel_riesgo, rr.tipo_riesgo,
                       rr.fecha_reporte, rr.descripcion
                FROM reportes_riesgo rr
                JOIN alumnos al ON rr.alumno_id = al.id
                JOIN usuarios u ON al.usuario_id = u.id
                WHERE rr.estado IN ('abierto', 'en_proceso')
                ORDER BY rr.nivel_riesgo, rr.fecha_reporte
            """,
            'acciones_recomendadas': """
                SELECT rr.fecha_reporte, rr.tipo_riesgo, rr.nivel_riesgo,
                       rr.acciones_recomendadas, rr.estado
                FROM reportes_riesgo rr
                JOIN alumnos al ON rr.alumno_id = al.id
                JOIN usuarios u ON al.usuario_id = u.id
                WHERE CONCAT(u.nombre, ' ', u.apellido) LIKE %s
                ORDER BY rr.fecha_reporte DESC
            """,
            'profesores_mas_reportes': """
                SELECT u.nombre, u.apellido, COUNT(rr.id) as total_reportes_emitidos
                FROM reportes_riesgo rr
                JOIN usuarios u ON rr.profesor_id = u.id
                GROUP BY u.id, u.nombre, u.apellido
                ORDER BY total_reportes_emitidos DESC
                LIMIT 10
            """,
            'seguimiento_reporte': """
                SELECT rr.fecha_reporte, rr.descripcion, rr.acciones_recomendadas,
                       rr.estado, rr.fecha_seguimiento, rr.observaciones_seguimiento
                FROM reportes_riesgo rr
                WHERE rr.id = %s
            """,
            'tipos_problemas_alumnos': """
                SELECT sa.tipo_problema, COUNT(*) as total_solicitudes,
                       AVG(CASE sa.nivel_urgencia 
                           WHEN 'alta' THEN 3 
                           WHEN 'media' THEN 2 
                           WHEN 'baja' THEN 1 END) as urgencia_promedio
                FROM solicitudes_ayuda sa
                GROUP BY sa.tipo_problema
                ORDER BY total_solicitudes DESC
            """,
            'solicitudes_pendientes': """
                SELECT sa.fecha_solicitud, sa.tipo_problema, sa.nivel_urgencia,
                       u.nombre, u.apellido, al.matricula
                FROM solicitudes_ayuda sa
                JOIN alumnos al ON sa.alumno_id = al.id
                JOIN usuarios u ON al.usuario_id = u.id
                WHERE sa.estado IN ('pendiente', 'en_atencion')
                ORDER BY sa.nivel_urgencia DESC, sa.fecha_solicitud
            """,
            'urgencia_comun': """
                SELECT sa.nivel_urgencia, COUNT(*) as total_solicitudes,
                       ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM solicitudes_ayuda), 2) as porcentaje
                FROM solicitudes_ayuda sa
                GROUP BY sa.nivel_urgencia
                ORDER BY total_solicitudes DESC
            """,
            'solicitudes_atendidas_directivo': """
                SELECT sa.fecha_solicitud, sa.tipo_problema, sa.estado,
                       u_al.nombre as alumno_nombre, u_al.apellido as alumno_apellido
                FROM solicitudes_ayuda sa
                JOIN alumnos al ON sa.alumno_id = al.id
                JOIN usuarios u_al ON al.usuario_id = u_al.id
                JOIN usuarios u_dir ON sa.directivo_asignado = u_dir.id
                WHERE CONCAT(u_dir.nombre, ' ', u_dir.apellido) LIKE %s
                ORDER BY sa.fecha_solicitud DESC
            """,
            'contacto_preferido': """
                SELECT sa.tipo_contacto_preferido, COUNT(*) as total_preferencias,
                       ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM solicitudes_ayuda), 2) as porcentaje
                FROM solicitudes_ayuda sa
                GROUP BY sa.tipo_contacto_preferido
                ORDER BY total_preferencias DESC
            """,
            'mensajes_solicitud': """
                SELECT cm.fecha_mensaje, cm.remitente, cm.contenido
                FROM chat_mensajes cm
                WHERE cm.solicitud_id = %s
                ORDER BY cm.fecha_mensaje
            """,
            'mensajes_alumno_directivo': """
                SELECT cm.fecha_mensaje, cm.remitente, cm.contenido
                FROM chat_mensajes cm
                JOIN solicitudes_ayuda sa ON cm.solicitud_id = sa.id
                JOIN alumnos al ON sa.alumno_id = al.id
                JOIN usuarios u_al ON al.usuario_id = u_al.id
                JOIN usuarios u_dir ON sa.directivo_asignado = u_dir.id
                WHERE CONCAT(u_al.nombre, ' ', u_al.apellido) LIKE %s
                AND CONCAT(u_dir.nombre, ' ', u_dir.apellido) LIKE %s
                ORDER BY cm.fecha_mensaje DESC
            """,
            'ultimo_mensaje': """
                SELECT MAX(cm.fecha_mensaje) as ultima_fecha
                FROM chat_mensajes cm
                WHERE cm.solicitud_id = %s
            """,
            'noticias_activas': """
                SELECT n.titulo, n.contenido, n.fecha_publicacion, n.vistas,
                       u.nombre as autor_nombre, u.apellido as autor_apellido
                FROM noticias n
                JOIN usuarios u ON n.autor_id = u.id
                WHERE n.activa = 1
                ORDER BY n.destacada DESC, n.fecha_publicacion DESC
            """,
            'categoria_mas_noticias': """
                SELECT nc.nombre as categoria, COUNT(n.id) as total_noticias
                FROM noticias_categorias nc
                LEFT JOIN noticias n ON nc.id = n.categoria_id
                GROUP BY nc.id, nc.nombre
                ORDER BY total_noticias DESC
                LIMIT 1
            """,
            'vistas_noticia': """
                SELECT n.titulo, n.vistas, n.fecha_publicacion
                FROM noticias n
                WHERE n.titulo LIKE %s
            """,
            'autor_noticia': """
                SELECT u.nombre, u.apellido, n.fecha_publicacion
                FROM noticias n
                JOIN usuarios u ON n.autor_id = u.id
                WHERE n.titulo LIKE %s
            """,
            'categorias_foro': """
                SELECT fc.nombre as categoria, fc.descripcion, COUNT(fp.id) as total_publicaciones
                FROM foro_categorias fc
                LEFT JOIN foro_posts fp ON fc.id = fp.categoria_id
                GROUP BY fc.id, fc.nombre, fc.descripcion
                ORDER BY total_publicaciones DESC
            """,
            'posts_mas_vistos': """
                SELECT fp.titulo, fp.vistas, COUNT(fc.id) as total_comentarios
                FROM foro_posts fp
                LEFT JOIN foro_comentarios fc ON fp.id = fc.post_id
                GROUP BY fp.id, fp.titulo, fp.vistas
                ORDER BY fp.vistas DESC, total_comentarios DESC
                LIMIT 10
            """,
            'comentarios_usuario': """
                SELECT fc.contenido, fc.fecha_comentario, fp.titulo as post_titulo
                FROM foro_comentarios fc
                JOIN foro_posts fp ON fc.post_id = fp.id
                JOIN usuarios u ON fc.usuario_id = u.id
                WHERE CONCAT(u.nombre, ' ', u.apellido) LIKE %s
                ORDER BY fc.fecha_comentario DESC
            """,
            'publicaciones_cerradas': """
                SELECT fp.titulo, fp.fecha_publicacion, fp.cerrado, fp.fijado
                FROM foro_posts fp
                WHERE fp.cerrado = 1 OR fp.fijado = 1
                ORDER BY fp.fijado DESC, fp.fecha_publicacion DESC
            """,
            'reacciones_post': """
                SELECT u.nombre, u.apellido, fi.tipo_interaccion, fi.fecha_interaccion
                FROM foro_interacciones fi
                JOIN usuarios u ON fi.usuario_id = u.id
                WHERE fi.post_id = %s
                ORDER BY fi.fecha_interaccion DESC
            """,
            'encuestas_profesor': """
                SELECT e.titulo, e.descripcion, e.fecha_creacion, e.activa
                FROM encuestas e
                JOIN usuarios u ON e.creador_id = u.id
                WHERE CONCAT(u.nombre, ' ', u.apellido) LIKE %s
                ORDER BY e.fecha_creacion DESC
            """,
            'respuestas_encuesta': """
                SELECT COUNT(DISTINCT er.alumno_id) as total_respuestas
                FROM encuestas_respuestas er
                JOIN encuestas e ON er.encuesta_id = e.id
                WHERE e.titulo LIKE %s
            """,
            'respuestas_alumno_encuesta': """
                SELECT ep.pregunta, er.respuesta, er.fecha_respuesta
                FROM encuestas_respuestas er
                JOIN encuestas_preguntas ep ON er.pregunta_id = ep.id
                JOIN encuestas e ON ep.encuesta_id = e.id
                JOIN alumnos al ON er.alumno_id = al.id
                JOIN usuarios u ON al.usuario_id = u.id
                WHERE CONCAT(u.nombre, ' ', u.apellido) LIKE %s AND e.titulo LIKE %s
                ORDER BY ep.orden
            """,
            'preguntas_encuesta': """
                SELECT ep.pregunta, ep.tipo_pregunta, ep.opciones, ep.obligatoria
                FROM encuestas_preguntas ep
                JOIN encuestas e ON ep.encuesta_id = e.id
                WHERE e.titulo LIKE %s
                ORDER BY ep.orden
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
            elif field in ['numero_cuatrimestre', 'id_reporte', 'id_solicitud', 'id_post']:
                params.append(int(value))
            else:
                params.append(value)
        
        return params