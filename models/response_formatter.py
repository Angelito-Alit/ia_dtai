import logging
from datetime import datetime
import pandas as pd

logger = logging.getLogger(__name__)

class ResponseFormatter:
    def __init__(self):
        self.response_templates = {
            'calificaciones_alumno': self._format_calificaciones,
            'alumnos_en_riesgo': self._format_alumnos_riesgo,
            'promedio_por_carrera': self._format_promedio_carrera,
            'materias_reprobadas': self._format_materias_reprobadas,
            'grupos_profesor': self._format_grupos_profesor,
            'solicitudes_ayuda_pendientes': self._format_solicitudes_ayuda,
            'estadisticas_generales': self._format_estadisticas,
            'horarios_alumno': self._format_horarios
        }
    
    def format_response(self, intent, data, query_info, user_role, original_message):
        try:
            if not data:
                return self._format_no_data_response(intent, original_message, user_role)
            template_key = query_info.get('template_used', intent)
            formatter = self.response_templates.get(template_key, self._format_generic_response)
            formatted = formatter(data, user_role, original_message)
            recommendations = self._generate_recommendations(template_key, data, user_role)
            formatted['recommendations'] = recommendations
            
            return formatted
            
        except Exception as e:
            logger.error(f"Error formateando respuesta: {e}")
            return {
                'text': "He encontrado información pero tuve problemas procesándola. ¿Puedes intentar reformular tu pregunta?",
                'recommendations': []
            }
    
    def _format_calificaciones(self, data, user_role, original_message):
        if not data:
            return {'text': "No encontré calificaciones registradas para este período."}
        total_materias = len(data)
        promedio_general = sum([row['calificacion_final'] for row in data if row['calificacion_final']]) / len([row for row in data if row['calificacion_final']])
        materias_aprobadas = len([row for row in data if row['estatus'] == 'aprobado'])
        materias_riesgo = len([row for row in data if row['calificacion_final'] and row['calificacion_final'] < 7.0])
        response = f"""📊 **Resumen de Calificaciones**
        
**Estadísticas Generales:**
• Total de materias: {total_materias}
• Promedio general: {promedio_general:.2f}
• Materias aprobadas: {materias_aprobadas}
• Materias en riesgo: {materias_riesgo}

**Detalle por Materia:**
"""
        
        for row in data:
            status_emoji = "✅" if row['estatus'] == 'aprobado' else "⚠️" if row['estatus'] == 'cursando' else "❌"
            final_grade = f"{row['calificacion_final']:.1f}" if row['calificacion_final'] else "Sin calificar"
            
            response += f"{status_emoji} **{row['nombre']}** ({row['codigo']})\n"
            response += f"   Calificación final: {final_grade} | Estado: {row['estatus']}\n"
            
            if row['observaciones']:
                response += f"   📝 {row['observaciones']}\n"
            response += "\n"
        
        return {'text': response}
    
    def _format_alumnos_riesgo(self, data, user_role, original_message):
        if not data:
            return {'text': "¡Excelente! No hay alumnos en situación de riesgo actualmente."}
        riesgo_critico = [row for row in data if row['nivel_riesgo'] == 'critico']
        riesgo_alto = [row for row in data if row['nivel_riesgo'] == 'alto']
        riesgo_medio = [row for row in data if row['nivel_riesgo'] == 'medio']
        
        response = f"🚨 **Alumnos en Situación de Riesgo** ({len(data)} total)\n\n"
        
        if riesgo_critico:
            response += f"🔴 **RIESGO CRÍTICO** ({len(riesgo_critico)} alumnos)\n"
            for row in riesgo_critico[:5]:  
                response += f"• **{row['nombre']} {row['apellido']}** ({row['matricula']})\n"
                response += f"  Carrera: {row['carrera']} | Promedio: {row['promedio_general']:.2f}\n"
                response += f"  Problema: {row['tipo_riesgo']} - {row['descripcion'][:100]}...\n\n"
        
        if riesgo_alto:
            response += f"🟡 **RIESGO ALTO** ({len(riesgo_alto)} alumnos)\n"
            for row in riesgo_alto[:3]:
                response += f"• **{row['nombre']} {row['apellido']}** ({row['matricula']})\n"
                response += f"  {row['tipo_riesgo']} | Promedio: {row['promedio_general']:.2f}\n\n"
        
        if riesgo_medio and len(riesgo_medio) > 0:
            response += f"🟠 **RIESGO MEDIO**: {len(riesgo_medio)} alumnos adicionales\n\n"
        
        return {'text': response}
    
    def _format_promedio_carrera(self, data, user_role, original_message):
        if not data:
            return {'text': "No se encontraron datos de carreras con alumnos activos."}
        
        response = "📈 **Análisis de Rendimiento por Carrera**\n\n"
        
        for row in data:
            porcentaje_riesgo = row['porcentaje_riesgo']
            status_emoji = "🟢" if porcentaje_riesgo < 10 else "🟡" if porcentaje_riesgo < 25 else "🔴"
            
            response += f"{status_emoji} **{row['carrera']}**\n"
            response += f"• Alumnos: {row['total_alumnos']}\n"
            response += f"• Promedio: {row['promedio_carrera']:.2f}\n"
            response += f"• En riesgo: {row['alumnos_riesgo']} ({porcentaje_riesgo}%)\n\n"
        
        return {'text': response}
    
    def _format_materias_reprobadas(self, data, user_role, original_message):
        if not data:
            return {'text': "No hay materias con índices significativos de reprobación este período."}
        
        response = "📉 **Materias con Mayor Índice de Reprobación**\n\n"
        
        for i, row in enumerate(data, 1):
            response += f"**{i}. {row['materia']}** ({row['codigo']})\n"
            response += f"   Carrera: {row['carrera']}\n"
            response += f"   Reprobados: {row['total_reprobados']} | Promedio: {row['promedio_materia']:.2f}\n\n"
        
        return {'text': response}
    
    def _format_grupos_profesor(self, data, user_role, original_message):
        if not data:
            return {'text': "No tienes grupos asignados actualmente."}
        carreras = {}
        for row in data:
            carrera = row['carrera']
            if carrera not in carreras:
                carreras[carrera] = []
            carreras[carrera].append(row)
        
        response = f"👨‍🏫 **Tus Grupos Asignados** ({len(data)} grupos)\n\n"
        
        for carrera, grupos in carreras.items():
            response += f"**{carrera}**\n"
            for grupo in grupos:
                response += f"• {grupo['grupo']} - {grupo['asignatura']}\n"
                response += f"  Cuatrimestre {grupo['cuatrimestre']} | {grupo['total_alumnos']} alumnos\n"
                response += f"  Período: {grupo['periodo']} {grupo['año']}\n\n"
        
        return {'text': response}
    
    def _format_solicitudes_ayuda(self, data, user_role, original_message):
        if not data:
            return {'text': "¡Perfecto! No hay solicitudes de ayuda pendientes."}
        alta_urgencia = [row for row in data if row['urgencia'] == 'alta']
        media_urgencia = [row for row in data if row['urgencia'] == 'media']
        baja_urgencia = [row for row in data if row['urgencia'] == 'baja']
        
        response = f"🆘 **Solicitudes de Ayuda Pendientes** ({len(data)} total)\n\n"
        
        if alta_urgencia:
            response += f"🔴 **URGENCIA ALTA** ({len(alta_urgencia)} solicitudes)\n"
            for row in alta_urgencia:
                days_waiting = (datetime.now() - row['fecha_solicitud']).days
                response += f"• **{row['nombre']} {row['apellido']}** ({row['matricula']})\n"
                response += f"  Problema: {row['tipo_problema']}\n"
                response += f"  Esperando: {days_waiting} días\n"
                response += f"   {row['descripcion_problema'][:80]}...\n\n"
        
        if media_urgencia:
            response += f" **URGENCIA MEDIA**: {len(media_urgencia)} solicitudes\n\n"
        
        if baja_urgencia:
            response += f" **URGENCIA BAJA**: {len(baja_urgencia)} solicitudes\n\n"
        
        return {'text': response}
    
    def _format_estadisticas(self, data, user_role, original_message):
        if not data:
            return {'text': "No se pudieron obtener las estadísticas del sistema."}
        
        response = " **Estadísticas del Sistema**\n\n"
        
        for row in data:
            concepto = row['concepto']
            valor = row['valor']
            
            response += f" **{concepto}**: {valor}\n"
        
        return {'text': response}
    
    def _format_horarios(self, data, user_role, original_message):
        if not data:
            return {'text': "No tienes horario registrado o no hay clases programadas."}
        dias = {}
        for row in data:
            dia = row['dia_semana']
            if dia not in dias:
                dias[dia] = []
            dias[dia].append(row)
        orden_dias = ['lunes', 'martes', 'miercoles', 'jueves', 'viernes', 'sabado']
        
        response = " **Tu Horario de Clases**\n\n"
        
        for dia in orden_dias:
            if dia in dias:
                response += f"**{dia.capitalize()}**\n"
                clases_dia = sorted(dias[dia], key=lambda x: x['hora_inicio'])
                
                for clase in clases_dia:
                    tipo_emoji = "" if clase['tipo_clase'] == 'teorica' else "" if clase['tipo_clase'] == 'laboratorio' else ""
                    response += f"{tipo_emoji} {clase['hora_inicio']} - {clase['hora_fin']} | **{clase['materia']}**\n"
                    response += f"    {clase['aula']} |  {clase['profesor']}\n"
                    response += f"   Tipo: {clase['tipo_clase']}\n\n"
        
        return {'text': response}
    
    def _format_generic_response(self, data, user_role, original_message):
        if isinstance(data, list) and len(data) > 0:
            response = f"He encontrado {len(data)} resultados para tu consulta:\n\n"
            for i, row in enumerate(data[:5], 1):
                response += f"**{i}.** "
                if isinstance(row, dict):
                    for key, value in list(row.items())[:3]:  
                        if value is not None:
                            response += f"{key}: {value} | "
                    response = response.rstrip(" | ") + "\n"
                else:
                    response += f"{row}\n"
            
            if len(data) > 5:
                response += f"\n... y {len(data) - 5} resultados más."
            
            return {'text': response}
        else:
            return {'text': "He procesado tu consulta pero no encontré resultados específicos."}
    
    def _format_no_data_response(self, intent, original_message, user_role):
        responses = {
            'calificaciones_alumno': "No encontré calificaciones registradas. Puede que aún no estén capturadas o no tengas materias asignadas este período.",
            'alumnos_en_riesgo': "¡Excelente noticia! No hay alumnos reportados en situación de riesgo actualmente.",
            'grupos_profesor': "No tienes grupos asignados en este momento o no se han configurado las asignaciones.",
            'horarios_alumno': "No encontré tu horario. Puede que aún no esté publicado o no tengas clases programadas."
        }
        
        default_response = f"No encontré información específica para tu consulta '{original_message}'. ¿Puedes proporcionar más detalles o reformular la pregunta?"
        
        return {
            'text': responses.get(intent, default_response),
            'recommendations': []
        }
    
    def _generate_recommendations(self, template_key, data, user_role):
        recommendations = []
        
        if template_key == 'alumnos_en_riesgo' and data:
            criticos = len([row for row in data if row['nivel_riesgo'] == 'critico'])
            if criticos > 0:
                recommendations.append(f"Prioriza la atención de {criticos} alumnos en riesgo crítico")
                recommendations.append("Considera programar sesiones de tutoría inmediatas")
            
            recommendations.append("Revisa los reportes individuales para planear intervenciones")
        
        elif template_key == 'promedio_por_carrera' and data:
            carreras_problema = [row for row in data if row['porcentaje_riesgo'] > 25]
            if carreras_problema:
                recommendations.append(f"Atención especial requerida en {len(carreras_problema)} carreras")
                recommendations.append("Implementar programas de nivelación académica")
        
        elif template_key == 'materias_reprobadas' and data:
            recommendations.append("Considera reforzar la enseñanza en estas materias")
            recommendations.append("Programa tutorías grupales para las materias más problemáticas")
        
        elif template_key == 'solicitudes_ayuda_pendientes' and data:
            urgentes = len([row for row in data if row['urgencia'] == 'alta'])
            if urgentes > 0:
                recommendations.append(f"Atender inmediatamente {urgentes} solicitudes urgentes")
                recommendations.append("Asignar responsables para cada solicitud pendiente")
        
        return recommendations