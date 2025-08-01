class ResponseFormatter:
    def __init__(self):
        pass
    
    def format_calificaciones(self, data):
        response = "**Aqui tienes tus calificaciones:**\n\n"
        total_promedio = 0
        materias_count = 0
        materias_riesgo = 0
        
        for row in data:
            if row['calificacion_final']:
                total_promedio += row['calificacion_final']
                materias_count += 1
                if row['calificacion_final'] < 7.0:
                    materias_riesgo += 1
            
            status = "✅" if row['estatus'] == 'aprobado' else "📝" if row['estatus'] == 'cursando' else "❌"
            grade = f"{row['calificacion_final']:.1f}" if row['calificacion_final'] else 'Sin calificar'
            response += f"{status} **{row['nombre']}**: {grade}\n"
            
            if row['parcial_1'] or row['parcial_2'] or row['parcial_3']:
                parciales = []
                if row['parcial_1']: parciales.append(f"P1: {row['parcial_1']:.1f}")
                if row['parcial_2']: parciales.append(f"P2: {row['parcial_2']:.1f}")
                if row['parcial_3']: parciales.append(f"P3: {row['parcial_3']:.1f}")
                response += f"   {' | '.join(parciales)}\n"
            response += "\n"
        
        if materias_count > 0:
            promedio_actual = total_promedio / materias_count
            response += f"**Tu promedio actual**: {promedio_actual:.2f}\n\n"
            
            if promedio_actual >= 9.0:
                response += "Excelente trabajo! Sigues por muy buen camino."
            elif promedio_actual >= 8.0:
                response += "Muy bien! Tu rendimiento es bueno."
            elif promedio_actual >= 7.0:
                response += "Vas bien, pero hay espacio para mejorar."
            else:
                response += "Necesitas enfocarte mas en tus estudios."
            
            if materias_riesgo > 0:
                response += f"\nTienes {materias_riesgo} materia(s) por debajo de 7.0"
        
        response += "\n\nTe gustaria ver estrategias para mejorar en alguna materia especifica?"
        return response
    
    def format_riesgo(self, data):
        criticos = len([d for d in data if d['nivel_riesgo'] == 'critico'])
        response = f"**Alumnos que necesitan atencion** ({len(data)} casos activos):\n\n"
        
        for row in data:
            emoji = "🔴" if row['nivel_riesgo'] == 'critico' else "🟡" if row['nivel_riesgo'] == 'alto' else "🟠"
            response += f"{emoji} **{row['nombre']} {row['apellido']}** ({row['matricula']})\n"
            response += f"   Carrera: {row['carrera']}\n"
            response += f"   Riesgo: {row['nivel_riesgo']} ({row['tipo_riesgo']})\n"
            if row['descripcion']:
                response += f"   {row['descripcion'][:80]}...\n"
            response += "\n"
        
        if criticos > 0:
            response += f"**ATENCION URGENTE**: {criticos} estudiantes en riesgo critico requieren intervencion inmediata.\n\n"
            response += "**Recomendaciones**:\n"
            response += "• Contactar a padres/tutores hoy mismo\n"
            response += "• Programar citas individuales esta semana\n"
            response += "• Evaluar apoyos adicionales (economicos, psicologicos)\n"
        
        response += "\nTe gustaria que genere un plan de intervencion detallado?"
        return response
    
    def format_promedio(self, data):
        response = "**Rendimiento por Carrera:**\n\n"
        for row in data:
            porcentaje_riesgo = (row['alumnos_riesgo'] / row['total_alumnos'] * 100) if row['total_alumnos'] > 0 else 0
            emoji = "🟢" if porcentaje_riesgo < 10 else "🟡" if porcentaje_riesgo < 25 else "🔴"
            
            response += f"{emoji} **{row['carrera']}**\n"
            response += f"   Alumnos: {row['total_alumnos']}\n"
            response += f"   Promedio: {row['promedio_carrera']}\n"
            response += f"   En riesgo: {row['alumnos_riesgo']} ({porcentaje_riesgo:.1f}%)\n\n"
        
        response += "Te gustaria ver un analisis mas detallado de alguna carrera especifica?"
        return response
    
    def format_estadisticas(self, queries, db):
        response = "**Estadisticas del Sistema:**\n\n"
        
        for name, query in queries:
            result = db.execute_query(query)
            if result:
                response += f"• **{name}**: {result[0]['total']}\n"
        
        avg_query = "SELECT ROUND(AVG(promedio_general), 2) as promedio_sistema FROM alumnos WHERE estado_alumno = 'activo' AND promedio_general > 0"
        avg_result = db.execute_query(avg_query)
        if avg_result and avg_result[0]['promedio_sistema']:
            response += f"• **Promedio General del Sistema**: {avg_result[0]['promedio_sistema']}\n"
        
        response += "\nTe gustaria un analisis mas profundo de alguna area especifica?"
        return response
    
    def format_error_response(self, error_type):
        error_messages = {
            'no_data': "No se encontraron datos para tu consulta.",
            'permission_denied': "No tienes permisos para acceder a esta informacion.",
            'database_error': "Hubo un problema conectando con la base de datos.",
            'invalid_query': "La consulta no es valida.",
            'general_error': "Ocurrio un error inesperado."
        }
        
        return error_messages.get(error_type, error_messages['general_error'])
    
    def format_success_message(self, action):
        success_messages = {
            'data_retrieved': "Informacion obtenida exitosamente.",
            'query_executed': "Consulta ejecutada correctamente.",
            'context_updated': "Contexto actualizado.",
            'user_identified': "Usuario identificado correctamente."
        }
        
        return success_messages.get(action, "Operacion completada exitosamente.")