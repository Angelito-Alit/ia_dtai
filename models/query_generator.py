class QueryGenerator:
    def __init__(self):
        self.base_queries = {
            'calificaciones': {
                'alumno': """
                    SELECT a.nombre, c.calificacion_final, c.estatus, c.parcial_1, c.parcial_2, c.parcial_3
                    FROM calificaciones c
                    JOIN asignaturas a ON c.asignatura_id = a.id
                    JOIN alumnos al ON c.alumno_id = al.id
                    WHERE al.usuario_id = %s
                    ORDER BY a.nombre
                    LIMIT 10
                """,
                'profesor': """
                    SELECT DISTINCT a.nombre, AVG(c.calificacion_final) as promedio_grupo,
                           COUNT(c.id) as total_alumnos,
                           COUNT(CASE WHEN c.calificacion_final < 7.0 THEN 1 END) as reprobados
                    FROM calificaciones c
                    JOIN asignaturas a ON c.asignatura_id = a.id
                    JOIN grupos g ON c.grupo_id = g.id
                    WHERE g.profesor_id = %s
                    GROUP BY a.id, a.nombre
                    ORDER BY promedio_grupo DESC
                    LIMIT 10
                """,
                'directivo': """
                    SELECT car.nombre as carrera, AVG(c.calificacion_final) as promedio_carrera,
                           COUNT(c.id) as total_calificaciones,
                           COUNT(CASE WHEN c.calificacion_final < 7.0 THEN 1 END) as reprobados
                    FROM calificaciones c
                    JOIN alumnos al ON c.alumno_id = al.id
                    JOIN carreras car ON al.carrera_id = car.id
                    GROUP BY car.id, car.nombre
                    ORDER BY promedio_carrera DESC
                    LIMIT 10
                """
            },
            'riesgo': {
                'profesor': """
                    SELECT u.nombre, u.apellido, al.matricula, rr.nivel_riesgo, rr.tipo_riesgo, rr.descripcion
                    FROM reportes_riesgo rr
                    JOIN alumnos al ON rr.alumno_id = al.id
                    JOIN usuarios u ON al.usuario_id = u.id
                    JOIN grupos g ON al.id = g.alumno_id
                    WHERE g.profesor_id = %s AND rr.estado IN ('abierto', 'en_proceso')
                    ORDER BY CASE rr.nivel_riesgo 
                        WHEN 'critico' THEN 1 
                        WHEN 'alto' THEN 2 
                        WHEN 'medio' THEN 3 
                        ELSE 4 END
                    LIMIT 10
                """,
                'directivo': """
                    SELECT u.nombre, u.apellido, al.matricula, rr.nivel_riesgo, rr.tipo_riesgo, rr.descripcion, car.nombre as carrera
                    FROM reportes_riesgo rr
                    JOIN alumnos al ON rr.alumno_id = al.id
                    JOIN usuarios u ON al.usuario_id = u.id
                    JOIN carreras car ON al.carrera_id = car.id
                    WHERE rr.estado IN ('abierto', 'en_proceso')
                    ORDER BY CASE rr.nivel_riesgo 
                        WHEN 'critico' THEN 1 
                        WHEN 'alto' THEN 2 
                        WHEN 'medio' THEN 3 
                        ELSE 4 END
                    LIMIT 10
                """
            },
            'estadisticas': {
                'directivo': [
                    ("Total Alumnos Activos", "SELECT COUNT(*) as total FROM alumnos WHERE estado_alumno = 'activo'"),
                    ("Total Carreras", "SELECT COUNT(*) as total FROM carreras WHERE activa = 1"),
                    ("Reportes Abiertos", "SELECT COUNT(*) as total FROM reportes_riesgo WHERE estado IN ('abierto', 'en_proceso')"),
                    ("Solicitudes Pendientes", "SELECT COUNT(*) as total FROM solicitudes_ayuda WHERE estado IN ('pendiente', 'en_atencion')")
                ],
                'profesor': [
                    ("Mis Grupos", "SELECT COUNT(DISTINCT grupo_id) as total FROM grupo_profesor WHERE profesor_id = %s"),
                    ("Mis Alumnos", "SELECT COUNT(DISTINCT al.id) as total FROM alumnos al JOIN grupos g ON al.id = g.alumno_id JOIN grupo_profesor gp ON g.id = gp.grupo_id WHERE gp.profesor_id = %s"),
                    ("Reportes Pendientes", "SELECT COUNT(*) as total FROM reportes_riesgo rr JOIN alumnos al ON rr.alumno_id = al.id JOIN grupos g ON al.id = g.alumno_id WHERE g.profesor_id = %s AND rr.estado = 'abierto'")
                ]
            }
        }
    
    def generate_query(self, intent, role, user_id=None):
        if intent not in self.base_queries:
            return None
        
        query_data = self.base_queries[intent]
        
        if role in query_data:
            return query_data[role]
        elif 'directivo' in query_data:
            return query_data['directivo']
        else:
            return list(query_data.values())[0] if query_data else None
    
    def build_dynamic_query(self, table, fields, conditions=None, order_by=None, limit=None):
        query = f"SELECT {', '.join(fields)} FROM {table}"
        
        if conditions:
            query += f" WHERE {' AND '.join(conditions)}"
        
        if order_by:
            query += f" ORDER BY {order_by}"
        
        if limit:
            query += f" LIMIT {limit}"
        
        return query
    
    def get_user_specific_query(self, base_query, user_id):
        if '%s' in base_query:
            return base_query, [user_id]
        return base_query, []
    
    def validate_query_permissions(self, intent, role):
        permissions = {
            'alumno': ['calificaciones'],
            'profesor': ['calificaciones', 'riesgo', 'estadisticas'],
            'directivo': ['calificaciones', 'riesgo', 'promedio', 'estadisticas']
        }
        
        return intent in permissions.get(role, [])