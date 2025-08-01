from database.query_executor import execute_query
from models.query_generator import *

def process_calificaciones(user_id):
    query = get_calificaciones_query()
    data = execute_query(query, [user_id])
    
    if not data:
        return "No encontré calificaciones registradas para ti. Es tu primer cuatrimestre? Si crees que es un error, puedes contactar a tu coordinador académico."
    
    response = "Aquí tienes tus calificaciones:\n\n"
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
        response += f"{status} {row['nombre']}: {grade}\n"
        
        if row['parcial_1'] or row['parcial_2'] or row['parcial_3']:
            parciales = []
            if row['parcial_1']: parciales.append(f"P1: {row['parcial_1']:.1f}")
            if row['parcial_2']: parciales.append(f"P2: {row['parcial_2']:.1f}")
            if row['parcial_3']: parciales.append(f"P3: {row['parcial_3']:.1f}")
            response += f"   {' | '.join(parciales)}\n"
        response += "\n"
    
    if materias_count > 0:
        promedio_actual = total_promedio / materias_count
        response += f"Tu promedio actual: {promedio_actual:.2f}\n\n"
        
        if promedio_actual >= 9.0:
            response += "Excelente trabajo! Sigues por muy buen camino."
        elif promedio_actual >= 8.0:
            response += "Muy bien! Tu rendimiento es bueno."
        elif promedio_actual >= 7.0:
            response += "Vas bien, pero hay espacio para mejorar."
        else:
            response += "Necesitas enfocarte más en tus estudios."
        
        if materias_riesgo > 0:
            response += f"\nTienes {materias_riesgo} materia(s) por debajo de 7.0"
    
    response += "\n\nTe gustaría ver estrategias para mejorar en alguna materia específica?"
    return response

def process_riesgo():
    query = get_riesgo_query()
    data = execute_query(query)
    
    if not data:
        return "Excelente noticia! No hay alumnos en situación de riesgo actualmente. El sistema educativo está funcionando bien."
    
    criticos = len([d for d in data if d['nivel_riesgo'] == 'critico'])
    response = f"Alumnos que necesitan atención ({len(data)} casos activos):\n\n"
    
    for row in data:
        emoji = "🔴" if row['nivel_riesgo'] == 'critico' else "🟡" if row['nivel_riesgo'] == 'alto' else "🟠"
        response += f"{emoji} {row['nombre']} {row['apellido']} ({row['matricula']})\n"
        response += f"   Carrera: {row['carrera']}\n"
        response += f"   Riesgo: {row['nivel_riesgo']} ({row['tipo_riesgo']})\n"
        if row['descripcion']:
            response += f"   {row['descripcion'][:80]}...\n"
        response += "\n"
    
    if criticos > 0:
        response += f"ATENCIÓN URGENTE: {criticos} estudiantes en riesgo crítico requieren intervención inmediata.\n\n"
        response += "Recomendaciones:\n"
        response += "• Contactar a padres/tutores hoy mismo\n"
        response += "• Programar citas individuales esta semana\n"
        response += "• Evaluar apoyos adicionales (económicos, psicológicos)\n"
    
    response += "\nTe gustaría que genere un plan de intervención detallado?"
    return response

def process_promedio():
    query = get_promedio_query()
    data = execute_query(query)
    
    if not data:
        return "No se encontraron datos de promedios por carrera."
    
    response = "Rendimiento por Carrera:\n\n"
    for row in data:
        porcentaje_riesgo = (row['alumnos_riesgo'] / row['total_alumnos'] * 100) if row['total_alumnos'] > 0 else 0
        emoji = "🟢" if porcentaje_riesgo < 10 else "🟡" if porcentaje_riesgo < 25 else "🔴"
        
        response += f"{emoji} {row['carrera']}\n"
        response += f"   Alumnos: {row['total_alumnos']}\n"
        response += f"   Promedio: {row['promedio_carrera']}\n"
        response += f"   En riesgo: {row['alumnos_riesgo']} ({porcentaje_riesgo:.1f}%)\n\n"
    
    response += "Te gustaría ver un análisis más detallado de alguna carrera específica?"
    return response

def process_estadisticas():
    queries = get_estadisticas_queries()
    response = "Estadísticas del Sistema:\n\n"
    
    for name, query in queries:
        result = execute_query(query)
        if result:
            response += f"• {name}: {result[0]['total']}\n"
    
    avg_query = get_promedio_sistema_query()
    avg_result = execute_query(avg_query)
    if avg_result and avg_result[0]['promedio_sistema']:
        response += f"• Promedio General del Sistema: {avg_result[0]['promedio_sistema']}\n"
    
    response += "\nTe gustaría un análisis más profundo de algún área específica?"
    return response