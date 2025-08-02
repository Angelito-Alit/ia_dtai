import random
from typing import Dict, List, Any, Optional
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class ResponseFormatter:
    def __init__(self):
        self.conversational_responses = {
            'saludo': [
                "¡Buenos días! Soy su asistente virtual administrativo de DTAI. Puedo proporcionarle información sobre alumnos en riesgo, rendimiento por carreras, ubicación de grupos, cargas de profesores, materias críticas y estadísticas del sistema. ¿Qué información necesita para la toma de decisiones?",
                "¡Hola! Estoy aquí para apoyarle con información administrativa y académica del sistema DTAI. ¿En qué análisis le puedo asistir hoy?",
                "¡Saludos! Como directivo, tiene acceso completo a toda la información del sistema. ¿Qué datos necesita consultar?"
            ],
            'pregunta_identidad': [
                "Soy su asistente virtual administrativo especializado en el sistema educativo DTAI. Tengo acceso completo a la base de datos para proporcionarle información sobre: alumnos en riesgo, matrículas específicas, ubicación de grupos, horarios, cargas de profesores, materias problemáticas, solicitudes urgentes y estadísticas completas del sistema. ¿Qué información específica necesita?",
                "Soy una IA diseñada específicamente para directivos del sistema DTAI. Puedo generar reportes, identificar problemas, localizar estudiantes, analizar rendimiento y proporcionar cualquier dato que necesite para la gestión académica.",
                "Estoy especializada en brindar información administrativa completa del sistema DTAI. Desde localizar a un estudiante específico hasta generar análisis de rendimiento por carreras. ¿En qué le puedo ayudar?"
            ]
        }
    
    def format_response(self, intent: str, data: Optional[List[Dict[str, Any]]], message: str = "", role: str = "directivo") -> str:
        if intent in self.conversational_responses:
            return random.choice(self.conversational_responses[intent])
        
        if not data:
            return self._format_no_data_response(intent, message)
        
        formatters = {
            'estadisticas_generales': self._format_general_statistics,
            'alumnos_bajo_rendimiento': self._format_low_performance_students,
            'alumnos_riesgo': self._format_risk_students,
            'ubicacion_grupos': self._format_group_locations,
            'horarios_grupos': self._format_group_schedules,
            'grupos_detalle': self._format_group_details,
            'carreras_rendimiento': self._format_career_performance,
            'profesores_carga': self._format_teacher_workload,
            'materias_criticas': self._format_critical_subjects,
            'solicitudes_urgentes': self._format_urgent_requests,
            'capacidad_grupos': self._format_group_capacity,
            'matriculas_especificas': self._format_specific_student
        }
        
        formatter = formatters.get(intent, self._format_generic_administrative_data)
        return formatter(data, message)
    
    def _format_general_statistics(self, data: List[Dict[str, Any]], message: str) -> str:
        response = "📊 **ESTADÍSTICAS GENERALES DEL SISTEMA DTAI**\n\n"
        
        for item in data:
            categoria = item.get('categoria', 'Sin categoría')
            total = item.get('total', 0)
            
            if 'críticos' in categoria.lower() or 'urgentes' in categoria.lower():
                emoji = "🚨" if total > 0 else "✅"
            elif 'alumnos' in categoria.lower():
                emoji = "👨‍🎓"
            elif 'profesores' in categoria.lower():
                emoji = "👨‍🏫"
            elif 'carreras' in categoria.lower():
                emoji = "🎓"
            elif 'grupos' in categoria.lower():
                emoji = "👥"
            else:
                emoji = "📊"
            
            response += f"{emoji} **{categoria}**: {total}\n"
        
        critical_items = [item for item in data if item.get('total', 0) > 0 and ('críticos' in item.get('categoria', '').lower() or 'urgentes' in item.get('categoria', '').lower())]
        
        if critical_items:
            response += "\n🚨 **ATENCIÓN INMEDIATA REQUERIDA:**\n"
            for item in critical_items:
                response += f"• {item.get('categoria')}: {item.get('total')} casos\n"
        
        response += "\n💼 **Acciones Recomendadas:**\n"
        response += "• Revisar casos críticos inmediatamente\n"
        response += "• Programar reuniones de seguimiento\n"
        response += "• Evaluar recursos adicionales necesarios\n"
        
        return response
    
    def _format_low_performance_students(self, data: List[Dict[str, Any]], message: str) -> str:
        if not data:
            return "✅ **EXCELENTE NOTICIA:** Todos los alumnos mantienen rendimiento académico satisfactorio (≥7.0)."
        
        response = f"📉 **ALUMNOS CON BAJO RENDIMIENTO ACADÉMICO** ({len(data)} casos)\n\n"
        
        criticos = len([d for d in data if d.get('promedio_general') and d.get('promedio_general') < 6.0])
        muy_bajo = len([d for d in data if d.get('promedio_general') and 6.0 <= d.get('promedio_general') < 7.0])
        
        response += f"🔴 **CRÍTICO** (<6.0): {criticos} estudiantes\n"
        response += f"🟡 **BAJO** (6.0-6.9): {muy_bajo} estudiantes\n\n"
        
        response += "**📋 LISTADO DETALLADO:**\n\n"
        
        for i, student in enumerate(data[:15], 1):
            matricula = student.get('matricula', 'N/A')
            nombre = student.get('nombre_completo', 'Sin nombre')
            carrera = student.get('carrera', 'Sin carrera')
            grupo = student.get('grupo', 'Sin grupo')
            promedio = student.get('promedio_general')
            materias_reprobadas = student.get('materias_reprobadas', 0)
            
            if promedio and promedio < 6.0:
                emoji = "🔴"
                nivel = "CRÍTICO"
            elif promedio and promedio < 7.0:
                emoji = "🟡"
                nivel = "BAJO"
            else:
                emoji = "⚠️"
                nivel = "SIN PROMEDIO"
            
            promedio_text = f"{promedio:.2f}" if promedio else "N/A"
            
            response += f"{i}. {emoji} **{nombre}** (Mat: {matricula})\n"
            response += f"   📚 Carrera: {carrera} | Grupo: {grupo}\n"
            response += f"   📊 Promedio: {promedio_text} | Reprobadas: {materias_reprobadas}\n"
            response += f"   ⚠️ Estado: {nivel}\n\n"
        
        if len(data) > 15:
            response += f"... y {len(data) - 15} estudiantes más.\n\n"
        
        response += "🚨 **PLAN DE ACCIÓN INMEDIATO:**\n"
        response += "• Citar a estudiantes críticos esta semana\n"
        response += "• Contactar padres/tutores de casos críticos\n"
        response += "• Asignar tutorías académicas especializadas\n"
        response += "• Evaluar posibles bajas temporales\n"
        response += "• Revisar cargas académicas individuales\n"
        
        return response
    
    def _format_risk_students(self, data: List[Dict[str, Any]], message: str) -> str:
        if not data:
            return "✅ **SITUACIÓN CONTROLADA:** No hay reportes de riesgo activos en el sistema."
        
        criticos = len([d for d in data if d.get('nivel_riesgo') == 'critico'])
        altos = len([d for d in data if d.get('nivel_riesgo') == 'alto'])
        
        response = f"🚨 **REPORTES DE RIESGO ACTIVOS** ({len(data)} casos)\n\n"
        response += f"🔴 **CRÍTICO**: {criticos} casos (intervención inmediata)\n"
        response += f"🟡 **ALTO**: {altos} casos (seguimiento urgente)\n\n"
        
        response += "**📋 CASOS QUE REQUIEREN ATENCIÓN:**\n\n"
        
        for i, student in enumerate(data[:12], 1):
            matricula = student.get('matricula', 'N/A')
            nombre = student.get('nombre_completo', 'Sin nombre')
            carrera = student.get('carrera', 'Sin carrera')
            nivel = student.get('nivel_riesgo', 'N/A')
            tipo = student.get('tipo_riesgo', 'N/A')
            fecha = student.get('fecha_reporte', 'N/A')
            descripcion = student.get('descripcion', '')
            
            emoji = "🔴" if nivel == 'critico' else "🟡" if nivel == 'alto' else "🟠"
            
            response += f"{i}. {emoji} **{nombre}** (Mat: {matricula})\n"
            response += f"   📚 {carrera}\n"
            response += f"   ⚠️ Riesgo: {nivel.upper()} - {tipo}\n"
            response += f"   📅 Reportado: {fecha}\n"
            if descripcion:
                response += f"   📝 {descripcion[:80]}...\n"
            response += "\n"
        
        if criticos > 0:
            response += f"🚨 **PROTOCOLO DE EMERGENCIA ACTIVADO**\n"
            response += f"• {criticos} casos críticos requieren intervención HOY\n"
            response += "• Notificar a coordinadores académicos\n"
            response += "• Activar protocolo de contención\n"
            response += "• Evaluar recursos de apoyo psicosocial\n\n"
        
        return response
    
    def _format_group_locations(self, data: List[Dict[str, Any]], message: str) -> str:
        if not data:
            return "📍 No se encontraron ubicaciones de grupos en el sistema."
        
        response = "📍 **UBICACIONES Y DISTRIBUCIÓN DE GRUPOS**\n\n"
        
        aulas = {}
        for item in data:
            aula = item.get('aula', 'Sin aula')
            if aula not in aulas:
                aulas[aula] = []
            aulas[aula].append(item)
        
        for aula, grupos in aulas.items():
            response += f"🏫 **AULA {aula}:**\n"
            for grupo_info in grupos:
                grupo = grupo_info.get('grupo', 'Sin nombre')
                carrera = grupo_info.get('carrera', 'Sin carrera')
                dia = grupo_info.get('dia_semana', 'N/A')
                hora_inicio = grupo_info.get('hora_inicio', 'N/A')
                hora_fin = grupo_info.get('hora_fin', 'N/A')
                asignatura = grupo_info.get('asignatura', 'N/A')
                profesor = grupo_info.get('profesor', 'Sin profesor')
                alumnos = grupo_info.get('alumnos_inscritos', 0)
                
                response += f"   📚 {grupo} ({carrera})\n"
                response += f"   📅 {dia} {hora_inicio}-{hora_fin}\n"
                response += f"   📖 {asignatura}\n"
                response += f"   👨‍🏫 {profesor}\n"
                response += f"   👥 {alumnos} alumnos\n\n"
        
        response += "💡 **Para localizar un grupo específico, mencione el nombre del grupo en su consulta.**"
        return response
    
    def _format_group_schedules(self, data: List[Dict[str, Any]], message: str) -> str:
        if not data:
            return "📅 No se encontraron horarios de grupos configurados."
        
        response = "📅 **HORARIOS COMPLETOS DE GRUPOS**\n\n"
        
        dias_orden = ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado']
        
        for dia in dias_orden:
            clases_dia = [item for item in data if item.get('dia_semana') == dia]
            if clases_dia:
                response += f"📅 **{dia.upper()}:**\n"
                
                clases_ordenadas = sorted(clases_dia, key=lambda x: x.get('hora_inicio', ''))
                for clase in clases_ordenadas:
                    grupo = clase.get('grupo', 'Sin grupo')
                    carrera = clase.get('carrera', 'Sin carrera')
                    hora_inicio = clase.get('hora_inicio', 'N/A')
                    hora_fin = clase.get('hora_fin', 'N/A')
                    aula = clase.get('aula', 'N/A')
                    asignatura = clase.get('asignatura', 'N/A')
                    profesor = clase.get('profesor', 'Sin profesor')
                    alumnos = clase.get('alumnos_en_grupo', 0)
                    
                    response += f"   ⏰ {hora_inicio}-{hora_fin} | 🏫 Aula {aula}\n"
                    response += f"   📚 {grupo} ({carrera}) - {asignatura}\n"
                    response += f"   👨‍🏫 {profesor} | 👥 {alumnos} alumnos\n\n"
        
        return response
    
    def _format_group_details(self, data: List[Dict[str, Any]], message: str) -> str:
        if not data:
            return "👥 No se encontraron grupos activos en el sistema."
        
        response = f"👥 **DETALLES DE GRUPOS ACTIVOS** ({len(data)} grupos)\n\n"
        
        grupos_llenos = len([g for g in data if g.get('porcentaje_ocupacion', 0) >= 90])
        grupos_criticos = len([g for g in data if g.get('porcentaje_ocupacion', 0) >= 100])
        
        if grupos_criticos > 0:
            response += f"🚨 **ALERTA**: {grupos_criticos} grupos en capacidad máxima\n"
        if grupos_llenos > 0:
            response += f"⚠️ **ATENCIÓN**: {grupos_llenos} grupos cerca del límite\n\n"
        
        carreras_grupos = {}
        for grupo in data:
            carrera = grupo.get('carrera', 'Sin carrera')
            if carrera not in carreras_grupos:
                carreras_grupos[carrera] = []
            carreras_grupos[carrera].append(grupo)
        
        for carrera, grupos in carreras_grupos.items():
            response += f"🎓 **{carrera}:**\n"
            
            for grupo in grupos:
                nombre_grupo = grupo.get('grupo', 'Sin nombre')
                cuatrimestre = grupo.get('cuatrimestre', 'N/A')
                capacidad = grupo.get('capacidad_maxima', 0)
                inscritos = grupo.get('alumnos_inscritos', 0)
                ocupacion = grupo.get('porcentaje_ocupacion', 0)
                tutor = grupo.get('tutor', 'Sin tutor')
                promedio = grupo.get('promedio_grupo')
                
                if ocupacion >= 100:
                    emoji = "🔴"
                elif ocupacion >= 90:
                    emoji = "🟡"
                elif ocupacion >= 75:
                    emoji = "🟠"
                else:
                    emoji = "🟢"
                
                promedio_text = f" | Promedio: {promedio:.2f}" if promedio else ""
                
                response += f"   {emoji} **{nombre_grupo}** (Cuatri {cuatrimestre})\n"
                response += f"      👥 {inscritos}/{capacidad} ({ocupacion}%){promedio_text}\n"
                response += f"      👨‍🏫 Tutor: {tutor}\n\n"
        
        return response
    
    def _format_career_performance(self, data: List[Dict[str, Any]], message: str) -> str:
        if not data:
            return "🎓 No se encontraron datos de rendimiento por carreras."
        
        response = "🎓 **ANÁLISIS DE RENDIMIENTO POR CARRERA**\n\n"
        
        mejor_carrera = max(data, key=lambda x: x.get('promedio_carrera', 0))
        peor_carrera = min(data, key=lambda x: x.get('promedio_carrera', 0))
        
        response += f"🏆 **MEJOR RENDIMIENTO**: {mejor_carrera.get('carrera')} ({mejor_carrera.get('promedio_carrera')})\n"
        response += f"⚠️ **REQUIERE ATENCIÓN**: {peor_carrera.get('carrera')} ({peor_carrera.get('promedio_carrera')})\n\n"
        
        for i, carrera in enumerate(data, 1):
            nombre = carrera.get('carrera', 'Sin nombre')
            total_alumnos = carrera.get('total_alumnos', 0)
            promedio = carrera.get('promedio_carrera', 0)
            riesgo = carrera.get('alumnos_riesgo', 0)
            excelencia = carrera.get('alumnos_excelencia', 0)
            porcentaje_riesgo = carrera.get('porcentaje_riesgo', 0)
            grupos = carrera.get('grupos_activos', 0)
            reportes = carrera.get('reportes_riesgo_activos', 0)
            
            if porcentaje_riesgo < 10:
                emoji = "🟢"
                status = "EXCELENTE"
            elif porcentaje_riesgo < 25:
                emoji = "🟡"
                status = "BUENO"
            else:
                emoji = "🔴"
                status = "CRÍTICO"
            
            response += f"{i}. {emoji} **{nombre}** - {status}\n"
            response += f"   👥 Alumnos: {total_alumnos} | Grupos: {grupos}\n"
            response += f"   📊 Promedio: {promedio} | Excelencia: {excelencia}\n"
            response += f"   ⚠️ En riesgo: {riesgo} ({porcentaje_riesgo}%)\n"
            response += f"   📋 Reportes activos: {reportes}\n\n"
        
        return response
    
    def _format_teacher_workload(self, data: List[Dict[str, Any]], message: str) -> str:
        if not data:
            return "👨‍🏫 No se encontraron datos de carga académica de profesores."
        
        response = "👨‍🏫 **ANÁLISIS DE CARGA ACADÉMICA DE PROFESORES**\n\n"
        
        sobrecargados = [p for p in data if p.get('grupos_asignados', 0) > 3]
        tutores = [p for p in data if p.get('es_tutor') == 'Sí']
        
        if sobrecargados:
            response += f"⚠️ **PROFESORES SOBRECARGADOS**: {len(sobrecargados)} con >3 grupos\n"
        response += f"👨‍🏫 **PROFESORES TUTORES**: {len(tutores)}\n\n"
        
        for i, profesor in enumerate(data, 1):
            nombre = profesor.get('profesor', 'Sin nombre')
            especialidad = profesor.get('especialidad', 'Sin especialidad')
            grupos = profesor.get('grupos_asignados', 0)
            materias = profesor.get('materias_diferentes', 0)
            clases = profesor.get('total_clases_semanales', 0)
            carreras = profesor.get('carreras_imparte', 'N/A')
            es_tutor = profesor.get('es_tutor', 'No')
            
            if grupos > 4:
                emoji = "🔴"
                carga = "SOBRECARGADO"
            elif grupos > 2:
                emoji = "🟡"
                carga = "CARGA ALTA"
            else:
                emoji = "🟢"
                carga = "CARGA NORMAL"
            
            tutor_badge = " 🎯" if es_tutor == 'Sí' else ""
            
            response += f"{i}. {emoji} **{nombre}**{tutor_badge} - {carga}\n"
            response += f"   🎓 Especialidad: {especialidad}\n"
            response += f"   👥 Grupos: {grupos} | Materias: {materias} | Clases/sem: {clases}\n"
            response += f"   📚 Carreras: {carreras}\n\n"
        
        return response
    
    def _format_critical_subjects(self, data: List[Dict[str, Any]], message: str) -> str:
        if not data:
            return "📚 ¡Excelente! No se identificaron materias con problemas críticos de reprobación."
        
        response = "📚 **MATERIAS CON ÍNDICES CRÍTICOS DE REPROBACIÓN**\n\n"
        
        muy_criticas = len([m for m in data if m.get('porcentaje_reprobacion', 0) > 40])
        
        if muy_criticas > 0:
            response += f"🚨 **CRISIS ACADÉMICA**: {muy_criticas} materias con >40% reprobación\n\n"
        
        for i, materia in enumerate(data, 1):
            nombre = materia.get('asignatura', 'Sin nombre')
            total = materia.get('total_calificaciones', 0)
            reprobados = materia.get('reprobados', 0)
            porcentaje = materia.get('porcentaje_reprobacion', 0)
            promedio = materia.get('promedio_asignatura', 0)
            carreras = materia.get('carreras_que_la_imparten', 0)
            lista_carreras = materia.get('lista_carreras', 'N/A')
            
            if porcentaje > 40:
                emoji = "🚨"
                nivel = "CRISIS"
            elif porcentaje > 25:
                emoji = "🔴"
                nivel = "CRÍTICO"
            elif porcentaje > 15:
                emoji = "🟡"
                nivel = "ALTO"
            else:
                emoji = "🟠"
                nivel = "MODERADO"
            
            response += f"{i}. {emoji} **{nombre}** - {nivel}\n"
            response += f"   📊 Reprobación: {reprobados}/{total} ({porcentaje}%)\n"
            response += f"   📈 Promedio general: {promedio}\n"
            response += f"   🎓 Carreras ({carreras}): {lista_carreras}\n\n"
        
        response += "🔧 **ACCIONES CORRECTIVAS RECOMENDADAS:**\n"
        response += "• Revisar metodología de enseñanza\n"
        response += "• Capacitación docente especializada\n"
        response += "• Implementar tutorías grupales\n"
        response += "• Evaluar contenido curricular\n"
        response += "• Monitoreo semanal de avance\n"
        
        return response
    
    def _format_urgent_requests(self, data: List[Dict[str, Any]], message: str) -> str:
        if not data:
            return "📋 ✅ No hay solicitudes de ayuda urgentes pendientes."
        
        urgentes = len([s for s in data if s.get('urgencia') == 'alta'])
        antiguos = len([s for s in data if s.get('dias_pendiente', 0) > 7])
        
        response = f"📋 **SOLICITUDES DE AYUDA URGENTES** ({len(data)} casos)\n\n"
        response += f"🚨 **URGENCIA ALTA**: {urgentes} casos\n"
        response += f"⏰ **ANTIGUOS** (>7 días): {antiguos} casos\n\n"
        
        if antiguos > 0:
            response += "🚨 **ATENCIÓN**: Solicitudes con demora excesiva detectadas\n\n"
        
        for i, solicitud in enumerate(data[:10], 1):
            id_solicitud = solicitud.get('solicitud_id', 'N/A')
            alumno = solicitud.get('alumno', 'Sin nombre')
            matricula = solicitud.get('matricula', 'N/A')
            carrera = solicitud.get('carrera', 'Sin carrera')
            tipo = solicitud.get('tipo_problema', 'N/A')
            urgencia = solicitud.get('urgencia', 'N/A')
            estado = solicitud.get('estado', 'N/A')
            dias = solicitud.get('dias_pendiente', 0)
            asignado = solicitud.get('asignado_a', 'Sin asignar')
            
            if urgencia == 'alta' and dias > 3:
                emoji = "🚨"
            elif urgencia == 'alta':
                emoji = "🔴"
            elif dias > 7:
                emoji = "⏰"
            else:
                emoji = "🟡"
            
            response += f"{i}. {emoji} **Solicitud #{id_solicitud}** ({dias} días)\n"
            response += f"   👤 {alumno} (Mat: {matricula})\n"
            response += f"   📚 {carrera}\n"
            response += f"   🎯 Problema: {tipo} | Urgencia: {urgencia.upper()}\n"
            response += f"   📋 Estado: {estado} | Asignado: {asignado}\n\n"
        
        return response
    
    def _format_group_capacity(self, data: List[Dict[str, Any]], message: str) -> str:
        if not data:
            return "👥 No se encontraron datos de capacidad de grupos."
        
        llenos = len([g for g in data if g.get('estado_capacidad') == 'LLENO'])
        criticos = len([g for g in data if g.get('estado_capacidad') == 'CRÍTICO'])
        altos = len([g for g in data if g.get('estado_capacidad') == 'ALTO'])
        
        response = f"👥 **ANÁLISIS DE CAPACIDAD DE GRUPOS** ({len(data)} grupos)\n\n"
        response += f"🔴 **LLENOS** (100%): {llenos} grupos\n"
        response += f"🟡 **CRÍTICOS** (90-99%): {criticos} grupos\n"
        response += f"🟠 **ALTOS** (75-89%): {altos} grupos\n\n"
        
        if llenos > 0:
            response += "🚨 **ACCIÓN INMEDIATA**: Grupos en capacidad máxima requieren atención\n\n"
        
        for i, grupo in enumerate(data, 1):
            nombre = grupo.get('grupo', 'Sin nombre')
            carrera = grupo.get('carrera', 'Sin carrera')
            capacidad = grupo.get('capacidad_maxima', 0)
            actuales = grupo.get('alumnos_actuales', 0)
            ocupacion = grupo.get('porcentaje_ocupacion', 0)
            disponibles = grupo.get('espacios_disponibles', 0)
            estado = grupo.get('estado_capacidad', 'NORMAL')
            
            emoji_map = {
                'LLENO': '🔴',
                'CRÍTICO': '🟡',
                'ALTO': '🟠',
                'NORMAL': '🟢'
            }
            emoji = emoji_map.get(estado, '🟢')
            
            response += f"{i}. {emoji} **{nombre}** ({carrera}) - {estado}\n"
            response += f"   👥 Ocupación: {actuales}/{capacidad} ({ocupacion}%)\n"
            response += f"   💺 Espacios disponibles: {disponibles}\n\n"
        
        response += "💡 **RECOMENDACIONES:**\n"
        if llenos > 0:
            response += "• Considerar apertura de nuevos grupos\n"
        if criticos > 0:
            response += "• Monitorear inscripciones de grupos críticos\n"
        response += "• Evaluar redistribución de alumnos\n"
        response += "• Planificar capacidad para próximo período\n"
        
        return response
    
    def _format_specific_student(self, data: List[Dict[str, Any]], message: str) -> str:
        if not data:
            return "🔍 No se encontró información para la matrícula especificada."
        
        student = data[0]
        matricula = student.get('matricula', 'N/A')
        nombre = student.get('nombre_completo', 'Sin nombre')
        carrera = student.get('carrera', 'Sin carrera')
        grupo = student.get('grupo', 'Sin grupo')
        cuatrimestre = student.get('cuatrimestre_actual', 'N/A')
        promedio = student.get('promedio_general')
        estado = student.get('estado_alumno', 'N/A')
        total_materias = student.get('total_materias', 0)
        aprobadas = student.get('materias_aprobadas', 0)
        reprobadas = student.get('materias_reprobadas', 0)
        cursando = student.get('materias_cursando', 0)
        reportes = student.get('reportes_riesgo', 0)
        
        response = f"👤 **EXPEDIENTE ACADÉMICO COMPLETO**\n\n"
        
        response += f"📋 **DATOS GENERALES:**\n"
        response += f"• **Matrícula**: {matricula}\n"
        response += f"• **Nombre**: {nombre}\n"
        response += f"• **Carrera**: {carrera}\n"
        response += f"• **Grupo**: {grupo}\n"
        response += f"• **Cuatrimestre**: {cuatrimestre}\n"
        response += f"• **Estado**: {estado}\n\n"
        
        response += f"📊 **RENDIMIENTO ACADÉMICO:**\n"
        if promedio:
            if promedio >= 9.0:
                status_emoji = "🌟"
                status = "EXCELENTE"
            elif promedio >= 8.0:
                status_emoji = "✅"
                status = "BUENO"
            elif promedio >= 7.0:
                status_emoji = "⚠️"
                status = "REGULAR"
            else:
                status_emoji = "🚨"
                status = "CRÍTICO"
            
            response += f"• **Promedio General**: {promedio:.2f} {status_emoji} ({status})\n"
        else:
            response += f"• **Promedio General**: Sin datos\n"
        
        response += f"• **Total Materias**: {total_materias}\n"
        response += f"• **Aprobadas**: {aprobadas} ✅\n"
        response += f"• **Reprobadas**: {reprobadas} ❌\n"
        response += f"• **Cursando**: {cursando} 📚\n\n"
        
        if reportes > 0:
            response += f"🚨 **ALERTAS ACTIVAS:**\n"
            response += f"• **Reportes de Riesgo**: {reportes} casos activos\n"
            response += f"• **Requiere seguimiento inmediato**\n\n"
        else:
            response += f"✅ **Sin reportes de riesgo activos**\n\n"
        
        # Calcular eficiencia académica
        if total_materias > 0:
            eficiencia = (aprobadas / total_materias) * 100
            response += f"📈 **EFICIENCIA ACADÉMICA**: {eficiencia:.1f}%\n"
            
            if eficiencia >= 90:
                response += "🌟 Rendimiento excepcional\n"
            elif eficiencia >= 75:
                response += "✅ Rendimiento satisfactorio\n"
            elif eficiencia >= 60:
                response += "⚠️ Necesita mejorar\n"
            else:
                response += "🚨 Requiere intervención urgente\n"
        
        return response
    
    def _format_generic_administrative_data(self, data: List[Dict[str, Any]], intent: str, message: str) -> str:
        response = f"📊 **CONSULTA ADMINISTRATIVA** - {intent.replace('_', ' ').title()}\n\n"
        
        for i, item in enumerate(data[:15], 1):
            response += f"{i}. "
            for key, value in item.items():
                if value is not None:
                    key_formatted = key.replace('_', ' ').title()
                    response += f"**{key_formatted}**: {value} | "
            response = response.rstrip(" | ") + "\n\n"
        
        if len(data) > 15:
            response += f"... y {len(data) - 15} registros más.\n\n"
        
        response += "💡 ¿Necesita un análisis más específico o filtrado de esta información?"
        
        return response
    
    def _format_no_data_response(self, intent: str, message: str) -> str:
        responses = {
            'estadisticas_generales': "📊 No se pudieron obtener las estadísticas en este momento. Verifique la conexión con la base de datos.",
            'alumnos_bajo_rendimiento': "✅ Excelente noticia: No hay alumnos con bajo rendimiento académico en el sistema.",
            'alumnos_riesgo': "✅ Situación controlada: No hay reportes de riesgo activos actualmente.",
            'ubicacion_grupos': "📍 No se encontraron ubicaciones de grupos configuradas.",
            'horarios_grupos': "📅 No hay horarios de grupos disponibles en el sistema.",
            'grupos_detalle': "👥 No se encontraron grupos activos para mostrar.",
            'carreras_rendimiento': "🎓 No se encontraron datos de rendimiento por carreras.",
            'profesores_carga': "👨‍🏫 No se encontró información de carga académica de profesores.",
            'materias_criticas': "📚 ¡Excelente! No hay materias con problemas críticos identificados.",
            'solicitudes_urgentes': "📋 ✅ No hay solicitudes de ayuda urgentes pendientes.",
            'capacidad_grupos': "👥 No se encontraron datos de capacidad de grupos.",
            'matriculas_especificas': "🔍 No se encontró información para la matrícula especificada. Verifique que el número sea correcto."
        }
        
        specific = responses.get(intent)
        if specific:
            return f"{specific}\n\n¿Hay alguna otra consulta administrativa que necesite?"
        
        return f"No se encontraron datos para su consulta: '{message}'. Como directivo, puede consultar información sobre alumnos, grupos, profesores, carreras, ubicaciones, horarios y estadísticas del sistema. ¿Podría reformular su consulta?"
    
    def add_suggestions(self, response: str, intent: str, role: str) -> str:
        directivo_suggestions = {
            'estadisticas_generales': "💡 También puede consultar: 'alumnos en riesgo', 'materias más reprobadas', 'carga de profesores', o ubicación de grupos específicos.",
            'alumnos_bajo_rendimiento': "💡 Consultas relacionadas: 'reportes de riesgo activos', 'materias más problemáticas', o matrícula específica para más detalles.",
            'alumnos_riesgo': "💡 Acciones sugeridas: revisar 'materias críticas', 'capacidad de grupos', o generar plan de intervención personalizado.",
            'ubicacion_grupos': "💡 También disponible: 'horarios completos', 'capacidad de grupos', o consultar grupo específico por nombre.",
            'materias_criticas': "💡 Análisis complementario: 'profesores sobrecargados', 'rendimiento por carreras', o estrategias de mejora.",
            'solicitudes_urgentes': "💡 Gestión administrativa: 'alumnos en riesgo', 'casos críticos', o asignación de recursos."
        }
        
        suggestion = directivo_suggestions.get(intent, "💡 Como directivo, tiene acceso completo al sistema. Puede consultar cualquier información sobre alumnos, profesores, grupos, carreras o estadísticas.")
        return f"{response}\n\n{suggestion}"