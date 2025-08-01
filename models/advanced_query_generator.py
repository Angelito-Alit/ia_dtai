class AdvancedQueryGenerator:
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