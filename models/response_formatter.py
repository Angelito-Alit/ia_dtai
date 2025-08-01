import random
from typing import Dict, List, Any, Optional
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class ResponseFormatter:
    def __init__(self):
        self.conversational_responses = {
            'saludo': [
                "Hola! Soy tu asistente virtual académico. ¿En qué te puedo ayudar hoy?",
                "Buenos días! ¿Qué necesitas saber?",
                "Hola! Me alegra verte por aquí. ¿Qué consulta tienes?",
                "Hey! ¿Cómo van las cosas? ¿En qué te puedo asistir?"
            ],
            'despedida': [
                "Hasta luego! Que tengas un excelente día.",
                "Nos vemos! Que te vaya súper bien en tus estudios!",
                "Adiós! Recuerda que siempre puedes contar conmigo.",
                "Hasta pronto! Aquí estaré cuando me necesites."
            ],
            'agradecimiento': [
                "De nada! Para eso estoy aquí. ¿Necesitas algo más?",
                "Un placer ayudarte! Cualquier otra cosa que necesites, solo pregunta.",
                "Siempre es un gusto! ¿Hay algo más en lo que te pueda asistir?"
            ],
            'pregunta_estado': [
                "Muy bien, gracias por preguntar! Estoy aquí para ayudarte con tus consultas académicas.",
                "Excelente! Funcionando al 100% y listo para ayudarte. ¿Qué necesitas?",
                "Perfecto! Siempre contento de poder ayudar a estudiantes como tú."
            ],
            'pregunta_identidad': [
                "Soy tu asistente virtual académico. Puedo ayudarte con calificaciones, reportes de riesgo, estadísticas y más.",
                "Hola! Soy una IA especializada en educación. Mi trabajo es ayudarte con tus consultas académicas.",
                "Soy tu compañero digital para todo lo académico. Consulto la base de datos en tiempo real."
            ],
            'emocional_negativo': [
                "Lo siento que te sientas así. Los desafíos académicos son temporales y siempre hay oportunidades de mejorar.",
                "Entiendo que puede ser frustrante. Estoy aquí para apoyarte. ¿Hay algo específico que te preocupa?",
                "Sé que a veces puede ser abrumador. Recuerda que cada dificultad es una oportunidad de crecimiento."
            ],
            'emocional_positivo': [
                "Me alegra mucho escuchar eso! Sigue así! ¿Hay algo en lo que pueda ayudarte?",
                "Qué bueno! La actitud positiva es clave para el éxito académico.",
                "Excelente! Me encanta ver estudiantes motivados."
            ],
            'afirmacion': [
                "Perfecto! ¿En qué más te puedo ayudar?",
                "Genial! ¿Hay algo más que quieras saber?",
                "Excelente! ¿Qué más necesitas?"
            ],
            'negacion': [
                "Entiendo. Si cambias de opinión o necesitas algo más, aquí estaré.",
                "Sin problema. ¿Hay algo diferente en lo que te pueda ayudar?",
                "Está bien. Cualquier otra consulta que tengas, solo dímelo."
            ]
        }
    
    def format_response(self, intent: str, data: Optional[List[Dict[str, Any]]], message: str = "", role: str = "alumno") -> str:
        if intent in self.conversational_responses:
            return random.choice(self.conversational_responses[intent])
        
        if not data:
            return self._format_no_data_response(intent)
        
        if intent in ['estadisticas', 'estadisticas_generales']:
            return self._format_statistics(data)
        elif intent in ['riesgo', 'alumnos_riesgo']:
            return self._format_risk_students(data)
        elif intent in ['promedio', 'promedio_carreras']:
            return self._format_career_averages(data)
        elif intent in ['reprobadas', 'materias_reprobadas']:
            return self._format_failed_subjects(data)
        elif intent in ['solicitudes', 'solicitudes_ayuda']:
            return self._format_help_requests(data)
        elif intent in ['calificaciones', 'calificacion']:
            return self._format_grades(data)
        elif intent in ['horarios', 'horario']:
            return self._format_schedule(data)
        elif intent in ['grupos']:
            return self._format_groups(data)
        else:
            return self._format_generic_data(data, intent)
    
    def _format_statistics(self, data: List[Dict[str, Any]]) -> str:
        response = "Estadísticas Generales del Sistema:\n\n"
        
        for item in data:
            categoria = item.get('categoria', 'Sin categoría')
            total = item.get('total', 0)
            response += f"• {categoria}: {total}\n"
        
        response += "\n¿Te gustaría un análisis más detallado de algún área específica?"
        return response
    
    def _format_risk_students(self, data: List[Dict[str, Any]]) -> str:
        if not data:
            return "Excelente noticia! No hay alumnos en situación de riesgo actualmente."
        
        criticos = len([d for d in data if d.get('nivel_riesgo') == 'critico'])
        response = f"Alumnos que necesitan atención ({len(data)} casos activos):\n\n"
        
        for student in data:
            emoji = "🔴" if student.get('nivel_riesgo') == 'critico' else "🟡" if student.get('nivel_riesgo') == 'alto' else "🟠"
            nombre = f"{student.get('nombre', '')} {student.get('apellido', '')}"
            matricula = student.get('matricula', '')
            carrera = student.get('carrera', '')
            nivel = student.get('nivel_riesgo', '')
            tipo = student.get('tipo_riesgo', '')
            
            response += f"{emoji} {nombre} ({matricula})\n"
            response += f"   Carrera: {carrera}\n"
            response += f"   Riesgo: {nivel} ({tipo})\n\n"
        
        if criticos > 0:
            response += f"ATENCIÓN URGENTE: {criticos} estudiantes en riesgo crítico requieren intervención inmediata.\n"
        
        return response
    
    def _format_career_averages(self, data: List[Dict[str, Any]]) -> str:
        response = "Rendimiento por Carrera:\n\n"
        
        for career in data:
            carrera = career.get('carrera', 'Sin nombre')
            total_alumnos = career.get('total_alumnos', 0)
            promedio = career.get('promedio_carrera', 0)
            alumnos_riesgo = career.get('alumnos_riesgo', 0)
            porcentaje_riesgo = career.get('porcentaje_riesgo', 0)
            
            emoji = "🟢" if porcentaje_riesgo < 10 else "🟡" if porcentaje_riesgo < 25 else "🔴"
            
            response += f"{emoji} {carrera}\n"
            response += f"   Alumnos: {total_alumnos}\n"
            response += f"   Promedio: {promedio}\n"
            response += f"   En riesgo: {alumnos_riesgo} ({porcentaje_riesgo}%)\n\n"
        
        response += "¿Te gustaría ver un análisis más detallado de alguna carrera específica?"
        return response
    
    def _format_failed_subjects(self, data: List[Dict[str, Any]]) -> str:
        response = "Materias con Mayor Índice de Reprobación:\n\n"
        
        for subject in data:
            asignatura = subject.get('asignatura', 'Sin nombre')
            total_reprobados = subject.get('total_reprobados', 0)
            porcentaje = subject.get('porcentaje_reprobacion', 0)
            
            response += f"• {asignatura}\n"
            response += f"   Reprobados: {total_reprobados} ({porcentaje}%)\n\n"
        
        response += "¿Te gustaría estrategias para mejorar el rendimiento en alguna materia?"
        return response
    
    def _format_help_requests(self, data: List[Dict[str, Any]]) -> str:
        response = "Estado de Solicitudes de Ayuda:\n\n"
        
        estados = {}
        tipos = {}
        
        for request in data:
            estado = request.get('estado', 'Sin estado')
            tipo = request.get('tipo_problema', 'Sin tipo')
            cantidad = request.get('cantidad', 0)
            
            if estado not in estados:
                estados[estado] = 0
            estados[estado] += cantidad
            
            if tipo not in tipos:
                tipos[tipo] = 0
            tipos[tipo] += cantidad
        
        response += "Por Estado:\n"
        for estado, cantidad in estados.items():
            response += f"• {estado}: {cantidad}\n"
        
        response += "\nPor Tipo de Problema:\n"
        for tipo, cantidad in tipos.items():
            response += f"• {tipo}: {cantidad}\n"
        
        return response
    
    def _format_grades(self, data: List[Dict[str, Any]]) -> str:
        if not data:
            return "No se encontraron calificaciones registradas."
        
        response = "Tus Calificaciones:\n\n"
        total_promedio = 0
        materias_count = 0
        materias_riesgo = 0
        
        for grade in data:
            asignatura = grade.get('asignatura', 'Sin nombre')
            calificacion_final = grade.get('calificacion_final')
            estatus = grade.get('estatus', 'Sin estatus')
            parcial_1 = grade.get('parcial_1')
            parcial_2 = grade.get('parcial_2')
            parcial_3 = grade.get('parcial_3')
            
            if calificacion_final:
                total_promedio += calificacion_final
                materias_count += 1
                if calificacion_final < 7.0:
                    materias_riesgo += 1
            
            status_emoji = "✅" if estatus == 'aprobado' else "📝" if estatus == 'cursando' else "❌"
            grade_text = f"{calificacion_final:.1f}" if calificacion_final else 'Sin calificar'
            
            response += f"{status_emoji} {asignatura}: {grade_text}\n"
            
            if parcial_1 or parcial_2 or parcial_3:
                parciales = []
                if parcial_1: parciales.append(f"P1: {parcial_1:.1f}")
                if parcial_2: parciales.append(f"P2: {parcial_2:.1f}")
                if parcial_3: parciales.append(f"P3: {parcial_3:.1f}")
                response += f"   📝 {' | '.join(parciales)}\n"
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
        
        return response
    
    def _format_schedule(self, data: List[Dict[str, Any]]) -> str:
        if not data:
            return "No se encontró horario registrado."
        
        response = "Tu Horario de Clases:\n\n"
        
        dias_orden = ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado']
        horario_por_dia = {}
        
        for clase in data:
            dia = clase.get('dia_semana', 'Sin día')
            if dia not in horario_por_dia:
                horario_por_dia[dia] = []
            horario_por_dia[dia].append(clase)
        
        for dia in dias_orden:
            if dia in horario_por_dia:
                response += f"{dia}:\n"
                clases_dia = sorted(horario_por_dia[dia], key=lambda x: x.get('hora_inicio', ''))
                
                for clase in clases_dia:
                    asignatura = clase.get('asignatura', 'Sin nombre')
                    hora_inicio = clase.get('hora_inicio', '')
                    hora_fin = clase.get('hora_fin', '')
                    aula = clase.get('aula', 'Sin aula')
                    profesor = clase.get('profesor', 'Sin profesor')
                    
                    response += f"  {hora_inicio}-{hora_fin} | {asignatura}\n"
                    response += f"  Aula: {aula} | Prof: {profesor}\n\n"
        
        return response
    
    def _format_groups(self, data: List[Dict[str, Any]]) -> str:
        if not data:
            return "No se encontraron grupos activos."
        
        response = "Grupos Activos en el Sistema:\n\n"
        
        for group in data:
            grupo = group.get('grupo', 'Sin nombre')
            carrera = group.get('carrera', 'Sin carrera')
            cuatrimestre = group.get('cuatrimestre', 'Sin cuatrimestre')
            capacidad = group.get('capacidad_maxima', 0)
            inscritos = group.get('alumnos_inscritos', 0)
            tutor = group.get('tutor', 'Sin tutor')
            ciclo = group.get('ciclo_escolar', 'Sin ciclo')
            
            ocupacion = (inscritos / capacidad * 100) if capacidad > 0 else 0
            emoji = "🔴" if ocupacion > 90 else "🟡" if ocupacion > 75 else "🟢"
            
            response += f"{emoji} {grupo} - {carrera}\n"
            response += f"   Cuatrimestre: {cuatrimestre} | Ciclo: {ciclo}\n"
            response += f"   Alumnos: {inscritos}/{capacidad} ({ocupacion:.1f}%)\n"
            response += f"   Tutor: {tutor}\n\n"
        
        return response
    
    def _format_generic_data(self, data: List[Dict[str, Any]], intent: str) -> str:
        response = f"Resultados para tu consulta ({intent}):\n\n"
        
        for i, item in enumerate(data[:10], 1):
            response += f"{i}. "
            for key, value in item.items():
                if value is not None:
                    response += f"{key}: {value} | "
            response = response.rstrip(" | ") + "\n"
        
        if len(data) > 10:
            response += f"\n... y {len(data) - 10} resultados más."
        
        return response
    
    def _format_no_data_response(self, intent: str) -> str:
        no_data_responses = {
            'calificaciones': "No se encontraron calificaciones registradas para ti.",
            'horarios': "No se encontró horario registrado.",
            'grupos': "No se encontraron grupos activos.",
            'estadisticas': "No se pudieron obtener las estadísticas en este momento.",
            'riesgo': "No hay alumnos en situación de riesgo actualmente.",
            'solicitudes': "No hay solicitudes de ayuda registradas."
        }
        
        return no_data_responses.get(intent, "No se encontraron datos para tu consulta.")
    
    def add_suggestions(self, response: str, intent: str, role: str) -> str:
        suggestions = {
            'calificaciones': "¿Te gustaría ver estrategias para mejorar en alguna materia?",
            'horarios': "¿Necesitas información sobre alguna clase específica?",
            'estadisticas': "¿Te gustaría un análisis más detallado de algún área?",
            'riesgo': "¿Te gustaría que genere un plan de intervención?",
            'grupos': "¿Quieres información específica de algún grupo?"
        }
        
        suggestion = suggestions.get(intent, "¿Hay algo más en lo que te pueda ayudar?")
        return f"{response}\n\n{suggestion}"