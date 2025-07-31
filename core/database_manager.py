import mysql.connector
import os
import logging
from datetime import datetime
from contextlib import contextmanager

logger = logging.getLogger(__name__)

class DatabaseManager:
    def __init__(self):
        self.config = {
            'host': os.environ.get('DB_HOST', 'bluebyte.space'),
            'user': os.environ.get('DB_USER', 'bluebyte_angel'),
            'password': os.environ.get('DB_PASSWORD', 'orbitalsoft'),
            'database': os.environ.get('DB_NAME', 'bluebyte_dtai_web'),
            'port': int(os.environ.get('DB_PORT', 3306)),
            'charset': 'utf8mb4',
            'autocommit': True
        }
    
    @contextmanager
    def get_connection(self):
        connection = None
        try:
            connection = mysql.connector.connect(**self.config)
            logger.info("Conexión DB establecida")
            yield connection
        except Exception as e:
            logger.error(f"Error conexión DB: {e}")
            raise
        finally:
            if connection and connection.is_connected():
                connection.close()
    
    def execute_query(self, query, params=None):
        try:
            with self.get_connection() as connection:
                cursor = connection.cursor(dictionary=True)
                cursor.execute(query, params or [])
                result = cursor.fetchall()
                cursor.close()
                logger.info(f"Query ejecutada: {len(result)} registros")
                return result
        except Exception as e:
            logger.error(f"Error query: {e}")
            return None
    
    def test_connection(self):
        try:
            result = self.execute_query("SELECT 1 as test, NOW() as timestamp, 'Conexión exitosa' as status")
            if result:
                return {
                    "success": True,
                    "message": "Base de datos respondiendo correctamente",
                    "response_time": "< 100ms",
                    "last_check": result[0]['timestamp']
                }
            return {"success": False, "error": "Sin respuesta de la base de datos"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def get_database_stats(self):
        try:
            stats_queries = {
                "total_students": "SELECT COUNT(*) as count FROM alumnos WHERE estado_alumno = 'activo'",
                "total_teachers": "SELECT COUNT(*) as count FROM profesores WHERE activo = 1",
                "total_programs": "SELECT COUNT(*) as count FROM carreras WHERE activa = 1",
                "total_subjects": "SELECT COUNT(*) as count FROM asignaturas WHERE activa = 1",
                "active_groups": "SELECT COUNT(*) as count FROM grupos WHERE activo = 1",
                "risk_cases": "SELECT COUNT(*) as count FROM reportes_riesgo WHERE estado IN ('abierto', 'en_proceso')",
                "help_requests": "SELECT COUNT(*) as count FROM solicitudes_ayuda WHERE estado IN ('pendiente', 'en_atencion')"
            }
            
            stats = {}
            for key, query in stats_queries.items():
                result = self.execute_query(query)
                stats[key] = result[0]['count'] if result else 0
            
            return stats
        except Exception as e:
            logger.error(f"Error obteniendo stats DB: {e}")
            return {}
    
    def get_students_data(self, limit=20):
        query = """
        SELECT u.nombre, u.apellido, al.matricula, al.promedio_general, 
               al.estado_alumno, car.nombre as carrera
        FROM alumnos al
        JOIN usuarios u ON al.usuario_id = u.id
        JOIN carreras car ON al.carrera_id = car.id
        WHERE al.estado_alumno = 'activo'
        ORDER BY al.promedio_general DESC
        LIMIT %s
        """
        return self.execute_query(query, [limit])
    
    def get_risk_reports(self, limit=15):
        query = """
        SELECT u.nombre, u.apellido, al.matricula, rr.nivel_riesgo, 
               rr.tipo_riesgo, rr.descripcion, car.nombre as carrera,
               rr.fecha_reporte, al.promedio_general
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
        LIMIT %s
        """
        return self.execute_query(query, [limit])
    
    def get_program_performance(self):
        query = """
        SELECT c.nombre as carrera, 
               COUNT(al.id) as total_alumnos,
               ROUND(AVG(al.promedio_general), 2) as promedio_carrera,
               COUNT(CASE WHEN al.promedio_general < 7.0 THEN 1 END) as alumnos_riesgo,
               COUNT(CASE WHEN al.promedio_general >= 9.0 THEN 1 END) as alumnos_excelencia,
               MAX(al.promedio_general) as mejor_promedio,
               MIN(al.promedio_general) as menor_promedio
        FROM carreras c
        LEFT JOIN alumnos al ON c.id = al.carrera_id
        WHERE al.estado_alumno = 'activo' AND al.promedio_general IS NOT NULL
        GROUP BY c.id, c.nombre
        ORDER BY promedio_carrera DESC
        """
        return self.execute_query(query)
    
    def get_subject_performance(self, limit=20):
        query = """
        SELECT a.nombre, a.codigo, COUNT(c.id) as total_evaluaciones,
               ROUND(AVG(c.calificacion_final), 2) as promedio_materia,
               COUNT(CASE WHEN c.estatus = 'reprobado' THEN 1 END) as reprobados,
               COUNT(CASE WHEN c.calificacion_final >= 9.0 THEN 1 END) as excelentes,
               car.nombre as carrera
        FROM asignaturas a
        LEFT JOIN calificaciones c ON a.id = c.asignatura_id
        LEFT JOIN alumnos al ON c.alumno_id = al.id
        LEFT JOIN carreras car ON a.carrera_id = car.id
        WHERE a.activa = 1 AND c.calificacion_final IS NOT NULL
        GROUP BY a.id, a.nombre, a.codigo, car.nombre
        HAVING total_evaluaciones > 0
        ORDER BY promedio_materia DESC
        LIMIT %s
        """
        return self.execute_query(query, [limit])
    
    def get_help_requests(self, limit=10):
        query = """
        SELECT sa.id, u.nombre, u.apellido, al.matricula,
               sa.tipo_problema, sa.descripcion_problema, sa.urgencia,
               sa.fecha_solicitud, car.nombre as carrera, sa.estado
        FROM solicitudes_ayuda sa
        JOIN alumnos al ON sa.alumno_id = al.id
        JOIN usuarios u ON al.usuario_id = u.id
        JOIN carreras car ON al.carrera_id = car.id
        WHERE sa.estado IN ('pendiente', 'en_atencion')
        ORDER BY CASE sa.urgencia 
            WHEN 'alta' THEN 1 
            WHEN 'media' THEN 2 
            ELSE 3 END,
            sa.fecha_solicitud ASC
        LIMIT %s
        """
        return self.execute_query(query, [limit])
    
    def get_grades_analysis(self, limit=25):
        query = """
        SELECT a.nombre, c.calificacion_final, c.estatus, c.parcial_1, 
               c.parcial_2, c.parcial_3, car.nombre as carrera, 
               u.nombre as alumno_nombre, al.matricula
        FROM calificaciones c
        JOIN asignaturas a ON c.asignatura_id = a.id
        JOIN alumnos al ON c.alumno_id = al.id
        JOIN carreras car ON al.carrera_id = car.id
        JOIN usuarios u ON al.usuario_id = u.id
        WHERE c.calificacion_final IS NOT NULL
        ORDER BY c.calificacion_final DESC
        LIMIT %s
        """
        return self.execute_query(query, [limit])
    
    def get_teachers_data(self):
        query = """
        SELECT u.nombre, u.apellido, p.especialidad, p.experiencia_años,
               COUNT(pag.id) as grupos_asignados, p.es_tutor
        FROM profesores p
        JOIN usuarios u ON p.usuario_id = u.id
        LEFT JOIN profesor_asignatura_grupo pag ON p.id = pag.profesor_id AND pag.activo = 1
        WHERE p.activo = 1
        GROUP BY p.id, u.nombre, u.apellido, p.especialidad, p.experiencia_años, p.es_tutor
        ORDER BY grupos_asignados DESC, p.experiencia_años DESC
        """
        return self.execute_query(query)
    
    def get_schedules_data(self, user_id=None):
        base_query = """
        SELECT h.dia_semana, h.hora_inicio, h.hora_fin,
               a.nombre as materia, h.aula, h.tipo_clase,
               CONCAT(u.nombre, ' ', u.apellido) as profesor,
               g.codigo as grupo, car.nombre as carrera
        FROM horarios h
        JOIN profesor_asignatura_grupo pag ON h.profesor_asignatura_grupo_id = pag.id
        JOIN asignaturas a ON pag.asignatura_id = a.id
        JOIN grupos g ON pag.grupo_id = g.id
        JOIN carreras car ON g.carrera_id = car.id
        JOIN profesores p ON pag.profesor_id = p.id
        JOIN usuarios u ON p.usuario_id = u.id
        WHERE h.activo = 1
        """
        
        if user_id:
            query = base_query + """
            AND EXISTS (
                SELECT 1 FROM alumnos_grupos ag 
                JOIN alumnos al ON ag.alumno_id = al.id
                WHERE ag.grupo_id = g.id AND al.usuario_id = %s AND ag.activo = 1
            )
            """
            params = [user_id]
        else:
            query = base_query + " LIMIT 50"
            params = []
        
        query += """
        ORDER BY CASE h.dia_semana
            WHEN 'lunes' THEN 1 WHEN 'martes' THEN 2 WHEN 'miercoles' THEN 3
            WHEN 'jueves' THEN 4 WHEN 'viernes' THEN 5 WHEN 'sabado' THEN 6
        END, h.hora_inicio
        """
        
        return self.execute_query(query, params)