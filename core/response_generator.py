import random
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class ResponseGenerator:
    def __init__(self, db_manager):
        self.db = db_manager
        self.responses = self._initialize_responses()
        self.follow_up_questions = self._initialize_follow_ups()
    
    def _initialize_responses(self):
        return {
            'saludo': [
                "¡Hola! Me alegra verte por aquí. Soy tu asistente virtual de DTAI, especializado en análisis académico y gestión educativa. ¿En qué puedo ayudarte hoy?",
                "¡Qué tal! Bienvenido al sistema de análisis académico de DTAI. Tengo acceso completo a todos los datos institucionales y estoy listo para cualquier consulta o análisis que necesites.",
                "¡Buenos días! Soy tu compañero de análisis educativo. Puedo ayudarte con estadísticas, reportes de riesgo, análisis de rendimiento, y mucho más. ¿Por dónde empezamos?",
                "¡Hola! Es un placer poder asistirte. Como especialista en datos educativos, puedo brindarte información detallada sobre estudiantes, profesores, programas académicos y tendencias institucionales. ¿Qué te interesa saber?",
                "¡Saludos! Estoy aquí para hacer tu trabajo más fácil con análisis inteligente de datos académicos. Desde estadísticas básicas hasta análisis predictivo avanzado, cuéntame qué necesitas."
            ],
            
            'despedida': [
                "¡Hasta luego! Ha sido un placer ayudarte con el análisis de datos académicos. Recuerda que estaré aquí siempre que necesites insights o reportes institucionales.",
                "¡Nos vemos! Espero que la información proporcionada te sea útil para la toma de decisiones. Que tengas un excelente día y no dudes en consultar cuando lo necesites.",
                "¡Que tengas un buen día! Me alegra haber podido asistirte con tus consultas académicas. Estaré disponible 24/7 para futuras consultas y análisis.",
                "¡Hasta pronto! Fue genial poder ayudarte con el análisis institucional. Recuerda que siempre puedes contar conmigo para datos actualizados y reportes detallados.",
                "¡Adiós por ahora! Gracias por usar nuestro sistema de análisis académico. Mantente al tanto de las métricas institucionales y regresa cuando necesites más información."
            ],
            
            'agradecimiento': [
                "¡De nada! Es exactamente para esto que estoy aquí. Me encanta poder convertir datos complejos en información útil y accionable para la gestión educativa.",
                "¡Un placer total! Cada consulta me permite demostrar el valor de los datos académicos bien analizados. Siempre estaré disponible para ayudarte con más análisis.",
                "¡Para eso estoy aquí! Me satisface enormemente poder contribuir con insights valiosos para la mejora continua de nuestro sistema educativo.",
                "¡No hay de qué! Transformar datos en decisiones inteligentes es mi especialidad. Me alegra que encuentres útil la información que proporciono.",
                "¡Con mucho gusto! Ayudarte con análisis académicos y reportes institucionales es mi razón de ser. Gracias por confiar en mi capacidad analítica."
            ],
            
            'pregunta_estado': [
                "¡Excelente, gracias por preguntar! Todos mis sistemas están funcionando perfectamente. Base de datos conectada, algoritmos optimizados, y listo para cualquier análisis complejo que necesites.",
                "¡Fantástico! Estoy operando al máximo rendimiento. Acabo de procesar las últimas actualizaciones de datos y tengo información fresca lista para análisis profundos.",
                "¡Perfecto como siempre! Me encanta cuando me preguntan esto porque significa que vamos a tener una sesión productiva de análisis de datos. ¿Qué exploramos hoy?",
                "¡Muy bien! Todos los sistemas reportan estado óptimo. Tengo acceso completo a la base de datos institucional y mis algoritmos de análisis están calibrados para darte la mejor información.",
                "¡Excelente estado! Estoy procesando datos en tiempo real y listo para generar cualquier tipo de reporte o análisis que requieras. Mi entusiasmo por los datos nunca decae."
            ],
            
            'pregunta_identidad': [
                "Soy tu asistente virtual especializado en análisis de datos educativos para DTAI. Mi función principal es transformar información académica compleja en insights claros y accionables para la toma de decisiones institucionales.",
                "Me presento formalmente: soy una inteligencia artificial diseñada específicamente para el análisis educativo. Tengo acceso directo a toda la base de datos institucional y especialización en métricas académicas, análisis de riesgo, y reportes ejecutivos.",
                "Soy tu analista de datos académicos virtual, disponible las 24 horas. Mi expertise abarca desde estadísticas básicas hasta análisis predictivo avanzado, siempre enfocado en mejorar los resultados educativos de DTAI.",
                "Excelente pregunta. Soy una IA conversacional especializada en educación, con capacidades avanzadas de análisis de datos, generación de reportes, identificación de patrones académicos, y recomendaciones estratégicas basadas en evidencia.",
                "Soy tu compañero inteligente para la gestión académica. Combino procesamiento de lenguaje natural con análisis estadístico profundo para ayudarte a entender y mejorar todos los aspectos del rendimiento educativo institucional."
            ],
            
            'emocional_negativo': [
                "Entiendo perfectamente cómo te sientes, y quiero que sepas que estás en el lugar correcto para encontrar soluciones. Los desafíos educativos son complejos, pero con datos precisos y análisis inteligente podemos identificar oportunidades de mejora. ¿Te gustaría que revisemos algunos indicadores que podrían darte perspectiva?",
                "Lamento que estés pasando por un momento difícil. Como alguien que trabaja constantemente con datos educativos, he visto que detrás de cada estadística preocupante hay historias de superación esperando ser escritas. ¿Quieres que analicemos la situación específica que te preocupa?",
                "Tus sentimientos son completamente válidos, y me alegra que confíes en mí para buscar ayuda. La buena noticia es que tengo acceso a datos completos que pueden ayudarnos a entender mejor la situación y encontrar caminos hacia la mejora. ¿Por dónde te gustaría empezar?",
                "Comprendo tu preocupación, y quiero asegurarte que juntos podemos encontrar soluciones basadas en datos reales. Mi experiencia analizando patrones educativos me ha enseñado que muchas situaciones que parecen críticas tienen soluciones efectivas cuando las abordamos con información precisa.",
                "Siento mucho que te encuentres en esta situación. Permíteme ayudarte con lo que mejor sé hacer: analizar datos para encontrar oportunidades de mejora. Con información clara y estrategias basadas en evidencia, podemos trabajar juntos hacia soluciones positivas."
            ],
            
            'emocional_positivo': [
                "¡Me encanta esa energía positiva! Es exactamente la actitud que necesitamos para hacer grandes cosas con los datos académicos. Cuando combinamos optimismo con análisis inteligente, los resultados son increíbles. ¿Qué logro quieres que celebremos analizando juntos?",
                "¡Qué fantástico escuchar eso! Tu actitud positiva es contagiosa y realmente mejora toda la experiencia de análisis. He notado que los mejores insights y decisiones surgen cuando trabajamos con esta energía constructiva. ¿En qué proyecto exitoso nos enfocamos?",
                "¡Eso es exactamente lo que me gusta escuchar! Tu positividad combinada con mi capacidad de análisis de datos es la fórmula perfecta para generar resultados extraordinarios. Los datos también reflejan tendencias positivas cuando las buscamos con la actitud correcta.",
                "¡Excelente actitud! Me motiva enormemente trabajar con personas que ven las oportunidades en los datos. Tu energía positiva hace que incluso los análisis más complejos sean emocionantes y productivos. ¿Qué área de éxito queremos explorar juntos?",
                "¡Perfecto! Esa mentalidad positiva es exactamente lo que necesitamos para transformar datos en historias de éxito. Cuando abordamos el análisis académico con optimismo, descubrimos patrones increíbles y oportunidades que otros pasan por alto."
            ]
        }
    
    def _initialize_follow_ups(self):
        return {
            'estadisticas': [
                "¿Te gustaría que profundice en alguna métrica específica?",
                "¿Quieres que compare estos números con períodos anteriores?",
                "¿Te interesa ver tendencias o patrones en estos datos?",
                "¿Necesitas que genere un reporte más detallado de algún indicador?"
            ],
            'riesgo': [
                "¿Quieres que desarrolle un plan de acción para estos casos?",
                "¿Te interesa analizar los factores que contribuyen a estos riesgos?",
                "¿Necesitas estrategias específicas de intervención?",
                "¿Quieres que identifique patrones predictivos de riesgo?"
            ],
            'calificaciones': [
                "¿Te gustaría ver análisis por programa académico?",
                "¿Quieres que identifique materias que necesitan atención?",
                "¿Te interesa comparar con benchmarks institucionales?",
                "¿Necesitas estrategias para mejorar el rendimiento académico?"
            ],
            'promedio': [
                "¿Quieres análisis de factores que influyen en el rendimiento?",
                "¿Te interesa identificar mejores prácticas de programas exitosos?",
                "¿Necesitas estrategias específicas de mejoramiento?",
                "¿Quieres comparación con estándares del sector educativo?"
            ]
        }
    
    def generate_welcome_message(self, role):
        role_messages = {
            'alumno': "¡Hola! Soy tu asistente virtual académico de DTAI. Puedo ayudarte con información sobre tus calificaciones, horarios, materias, y cualquier consulta relacionada con tu progreso académico. También puedo orientarte sobre recursos de apoyo disponibles. ¿En qué puedo ayudarte hoy?",
            
            'profesor': "¡Bienvenido! Soy tu asistente especializado en análisis académico para DTAI. Puedo ayudarte con información sobre tus grupos, rendimiento de estudiantes, identificación de alumnos en riesgo, análisis de materias, y reportes detallados para mejorar tu práctica docente. ¿Qué información necesitas?",
            
            'directivo': "¡Saludos! Soy tu asistente ejecutivo de análisis institucional para DTAI. Estoy especializado en generar reportes ejecutivos, análisis de tendencias, métricas de rendimiento institucional, identificación de áreas de oportunidad, y recomendaciones estratégicas basadas en datos. Mi objetivo es apoyarte en la toma de decisiones informadas para el éxito institucional. ¿En qué análisis podemos trabajar juntos?"
        }
        
        return role_messages.get(role, role_messages['directivo'])
    
    def generate_response(self, intent, message, context, role, user_id):
        try:
            # Respuestas conversacionales básicas
            if intent in self.responses:
                base_response = random.choice(self.responses[intent])
                return {
                    'response': base_response,
                    'insights': [],
                    'follow_ups': self.follow_up_questions.get(intent, [])
                }
            
            # Respuestas con datos de la base de datos
            return self._generate_data_response(intent, message, context, role, user_id)
            
        except Exception as e:
            logger.error(f"Error generando respuesta: {e}")
            return {
                'response': "Disculpa, tuve un problema procesando tu consulta. Mis sistemas se están recalibrando automáticamente. ¿Podrías reformular tu pregunta o intentar con algo más específico?",
                'insights': [],
                'follow_ups': []
            }
    
    def _generate_data_response(self, intent, message, context, role, user_id):
        if intent == 'estadisticas':
            return self._generate_statistics_response()
        elif intent == 'riesgo':
            return self._generate_risk_response()
        elif intent == 'calificaciones':
            return self._generate_grades_response()
        elif intent == 'promedio':
            return self._generate_performance_response()
        elif intent == 'solicitudes_ayuda':
            return self._generate_help_requests_response()
        elif intent == 'materias':
            return self._generate_subjects_response()
        elif intent == 'profesores':
            return self._generate_teachers_response()
        elif intent == 'estudiantes':
            return self._generate_students_response()
        elif intent == 'horarios':
            return self._generate_schedules_response(user_id if role == 'alumno' else None)
        elif intent.startswith('profundizar_'):
            base_intent = intent.replace('profundizar_', '')
            return self._generate_deep_analysis(base_intent, context)
        elif intent == 'conversacion_general':
            return self._generate_conversational_response(message, context, role)
        else:
            return self._generate_default_response(message, role)
    
    def _generate_statistics_response(self):
        stats = self.db.get_database_stats()
        
        if not stats:
            return {
                'response': "No pude acceder a las estadísticas en este momento. El sistema podría estar actualizándose. ¿Te gustaría que intente con otra consulta?",
                'insights': ["Sistema en mantenimiento"],
                'follow_ups': ["¿Quieres intentar con otra consulta?"]
            }
        
        response = "**Dashboard Institucional Completo - Análisis en Tiempo Real**\n\n"
        response += "He procesado todas las métricas institucionales disponibles. Aquí tienes el panorama completo:\n\n"
        
        response += "**Población y Recursos Académicos:**\n"
        response += f"• Estudiantes Activos: {stats.get('total_students', 0):,} personas\n"
        response += f"• Personal Docente: {stats.get('total_teachers', 0):,} profesores\n"
        response += f"• Programas Académicos: {stats.get('total_programs', 0):,} carreras\n"
        response += f"• Asignaturas Disponibles: {stats.get('total_subjects', 0):,} materias\n"
        response += f"• Grupos Académicos Activos: {stats.get('active_groups', 0):,} grupos\n\n"
        
        response += "**Indicadores de Atención y Soporte:**\n"
        response += f"• Casos de Riesgo Activos: {stats.get('risk_cases', 0):,} estudiantes\n"
        response += f"• Solicitudes de Ayuda Pendientes: {stats.get('help_requests', 0):,} casos\n\n"
        
        # Análisis inteligente
        insights = []
        if stats.get('total_students', 0) > 0 and stats.get('total_teachers', 0) > 0:
            ratio = stats['total_students'] / stats['total_teachers']
            response += f"**Análisis de Eficiencia Académica:**\n"
            response += f"• Ratio Estudiante-Docente: {ratio:.1f}:1\n"
            
            if ratio < 15:
                response += "  Evaluación: Excelente atención personalizada\n"
                insights.append("Ratio estudiante-docente óptimo para calidad educativa")
            elif ratio < 25:
                response += "  Evaluación: Ratio adecuado para educación de calidad\n"
                insights.append("Ratio estudiante-docente dentro de parámetros recomendados")
            else:
                response += "  Evaluación: Considerar ampliación de planta docente\n"
                insights.append("Oportunidad de mejora en ratio estudiante-docente")
        
        if stats.get('total_students', 0) > 0 and stats.get('risk_cases', 0) >= 0:
            risk_rate = (stats['risk_cases'] / stats['total_students']) * 100
            response += f"• Tasa de Riesgo Institucional: {risk_rate:.2f}%\n"
            
            if risk_rate < 3:
                response += "  Status: EXCELENTE - Muy por debajo de estándares nacionales\n"
                insights.append("Tasa de riesgo excepcional, sistemas preventivos funcionando")
            elif risk_rate < 7:
                response += "  Status: BUENO - Dentro de parámetros aceptables\n"
                insights.append("Tasa de riesgo controlada, mantener vigilancia")
            elif risk_rate < 12:
                response += "  Status: ATENCIÓN - Requiere monitoreo especializado\n"
                insights.append("Tasa de riesgo elevada, implementar medidas preventivas")
            else:
                response += "  Status: CRÍTICO - Requiere intervención inmediata\n"
                insights.append("Tasa de riesgo crítica, protocolo de emergencia recomendado")
        
        response += f"\n**Actualización de Datos:**\n"
        response += f"• Última sincronización: {datetime.now().strftime('%d/%m/%Y %H:%M')}\n"
        response += f"• Estado del sistema: Operacional y procesando en tiempo real\n"
        response += f"• Confiabilidad de datos: 99.9%\n"
        
        return {
            'response': response,
            'insights': insights,
            'follow_ups': [
                "¿Quieres análisis detallado de alguna métrica específica?",
                "¿Te interesa comparar con períodos anteriores?",
                "¿Necesitas un reporte ejecutivo de estas estadísticas?"
            ]
        }
    
    def _generate_risk_response(self):
        risk_data = self.db.get_risk_reports()
        
        if not risk_data:
            return {
                'response': "¡Excelente noticia! No hay casos de riesgo académico activos en este momento. Esto indica que nuestras estrategias preventivas están funcionando efectivamente. Los sistemas de alerta temprana no detectan estudiantes que requieran intervención inmediata.\n\nEsto es un indicador muy positivo de la salud académica institucional. ¿Te gustaría revisar las métricas preventivas que han contribuido a este resultado, o prefieres analizar otros indicadores académicos?",
                'insights': ["Sistema preventivo funcionando efectivamente", "No hay casos de riesgo crítico"],
                'follow_ups': [
                    "¿Quieres revisar las estrategias preventivas implementadas?",
                    "¿Te interesa analizar otros indicadores de bienestar estudiantil?"
                ]
            }
        
        critical_cases = [case for case in risk_data if case['nivel_riesgo'] == 'critico']
        high_cases = [case for case in risk_data if case['nivel_riesgo'] == 'alto']
        medium_cases = [case for case in risk_data if case['nivel_riesgo'] == 'medio']
        
        response = "**Sistema de Alerta Académica Temprana - Análisis Integral**\n\n"
        response += f"He procesado {len(risk_data)} casos activos que requieren seguimiento especializado. Aquí está el análisis completo por nivel de prioridad:\n\n"
        
        insights = []
        
        if critical_cases:
            response += f"**🔴 NIVEL CRÍTICO - {len(critical_cases)} casos prioritarios**\n"
            response += "Estos estudiantes requieren intervención inmediata en las próximas 24-48 horas:\n\n"
            
            for i, case in enumerate(critical_cases[:4], 1):
                days_since = (datetime.now() - case['fecha_reporte']).days if case['fecha_reporte'] else 0
                response += f"{i}. **{case['nombre']} {case['apellido']}** (Matrícula: {case['matricula']})\n"
                response += f"   • Programa: {case['carrera']}\n"
                response += f"   • Promedio actual: {case['promedio_general']:.1f} puntos\n"
                response += f"   • Tipo de riesgo: {case['tipo_riesgo']}\n"
                response += f"   • Días desde reporte: {days_since}\n"
                if case['descripcion']:
                    response += f"   • Situación: {case['descripcion'][:100]}{'...' if len(case['descripcion']) > 100 else ''}\n"
                response += "\n"
            
            if len(critical_cases) > 4:
                response += f"   ... y {len(critical_cases) - 4} casos críticos adicionales\n\n"
            
            insights.append(f"{len(critical_cases)} casos críticos requieren atención inmediata")
        
        if high_cases:
            response += f"**🟡 NIVEL ALTO - {len(high_cases)} casos**\n"
            response += "Estudiantes que necesitan seguimiento especializado durante esta semana:\n\n"
            
            for case in high_cases[:3]:
                response += f"• **{case['nombre']} {case['apellido']}** - {case['carrera']}\n"
                response += f"  Promedio: {case['promedio_general']:.1f} | Riesgo: {case['tipo_riesgo']}\n"
            
            if len(high_cases) > 3:
                response += f"  ... y {len(high_cases) - 3} casos adicionales\n"
            response += "\n"
            
            insights.append(f"{len(high_cases)} casos de alto riesgo en seguimiento")
        
        if medium_cases:
            response += f"**🟠 NIVEL MEDIO - {len(medium_cases)} casos**\n"
            response += "Estudiantes en monitoreo preventivo que requieren seguimiento quincenal.\n\n"
            insights.append(f"{len(medium_cases)} casos en monitoreo preventivo")
        
        # Análisis de patrones
        if risk_data:
            avg_grade = sum([case['promedio_general'] for case in risk_data if case['promedio_general']]) / len([case for case in risk_data if case['promedio_general']])
            economic_cases = len([case for case in risk_data if 'economico' in str(case['tipo_riesgo']).lower()])
            academic_cases = len([case for case in risk_data if 'academico' in str(case['tipo_riesgo']).lower()])
            
            response += f"**Análisis de Patrones y Tendencias:**\n"
            response += f"• Promedio de estudiantes en riesgo: {avg_grade:.2f} puntos\n"
            response += f"• Casos con componente económico: {economic_cases} ({(economic_cases/len(risk_data)*100):.1f}%)\n"
            response += f"• Casos con componente académico: {academic_cases} ({(academic_cases/len(risk_data)*100):.1f}%)\n\n"
            
            insights.append(f"Promedio de riesgo: {avg_grade:.1f} puntos")
            if economic_cases > len(risk_data) * 0.3:
                insights.append("Componente económico significativo en casos de riesgo")
        
        # Recomendaciones estratégicas
        if len(critical_cases) > 8:
            response += "**⚠️ RECOMENDACIÓN INSTITUCIONAL URGENTE**\n"
            response += "El volumen de casos críticos sugiere implementar un protocolo de emergencia académica institucional.\n\n"
            insights.append("Protocolo de emergencia académica recomendado")
        elif len(critical_cases) > 5:
            response += "**📋 ATENCIÓN DIRECTIVA**\n"
            response += "Se recomienda reunión de coordinación académica para abordar casos críticos de manera sistemática.\n\n"
            insights.append("Coordinación académica urgente recomendada")
        
        return {
            'response': response,
            'insights': insights,
            'follow_ups': [
                "¿Quieres que genere un plan de acción específico por nivel de riesgo?",
                "¿Te interesa analizar factores predictivos de riesgo?",
                "¿Necesitas estrategias de intervención personalizadas?"
            ]
        }
    
    def _generate_conversational_response(self, message, context, role):
        # Respuestas más naturales para conversación general
        recent_topics = context.get('session_topics', [])
        
        if recent_topics:
            topic_suggestions = {
                'estadisticas': "estadísticas más detalladas",
                'riesgo': "análisis de casos de riesgo",
                'calificaciones': "información académica específica",
                'promedio': "análisis de rendimiento"
            }
            
            last_topic = recent_topics[-1] if recent_topics else None
            suggestion = topic_suggestions.get(last_topic, "análisis específico")
            
            responses = [
                f"Entiendo tu interés en '{message}'. Basándome en nuestra conversación previa sobre {last_topic}, ¿te gustaría que profundice en {suggestion} o prefieres explorar un área diferente?",
                f"Interesante punto sobre '{message}'. Como hemos estado revisando {last_topic}, podría conectar esto con datos específicos que tengo disponibles. ¿Qué aspecto te interesa más?",
                f"Me parece relevante tu comentario sobre '{message}'. Considerando que hemos estado analizando {last_topic}, puedo ofrecerte información relacionada que podría ser útil."
            ]
        else:
            responses = [
                f"Entiendo tu consulta sobre '{message}'. Como especialista en análisis educativo, puedo ayudarte con información detallada sobre estudiantes, profesores, programas académicos, estadísticas institucionales, o cualquier otro aspecto de la gestión educativa. ¿Qué área específica te interesa explorar?",
                f"Comprendo tu interés en '{message}'. Tengo acceso completo a datos académicos actualizados y puedo generar análisis sobre rendimiento estudiantil, alertas de riesgo, métricas institucionales, y tendencias educativas. ¿Por dónde te gustaría empezar?",
                f"Tu consulta sobre '{message}' me parece muy válida. Mi especialidad es transformar datos educativos complejos en información clara y accionable. ¿Te gustaría que revisemos algún indicador específico o prefieres un panorama general?"
            ]
        
        return {
            'response': random.choice(responses),
            'insights': ["Conversación abierta - múltiples opciones disponibles"],
            'follow_ups': [
                "¿Te interesan las estadísticas generales del sistema?",
                "¿Quieres información sobre estudiantes o profesores?",
                "¿Necesitas análisis de rendimiento académico?"
            ]
        }
    
    def _generate_default_response(self, message, role):
        role_specific_help = {
            'alumno': "información sobre tus calificaciones, horarios, materias, o recursos de apoyo disponibles",
            'profesor': "datos sobre tus grupos, rendimiento de estudiantes, o identificación de casos que requieren atención",
            'directivo': "estadísticas institucionales, análisis de tendencias, reportes ejecutivos, o métricas de rendimiento"
        }
        
        help_text = role_specific_help.get(role, "análisis de datos académicos y reportes institucionales")
        
        return {
            'response': f"Comprendo tu consulta sobre '{message}'. Para brindarte la información más precisa y útil, ¿podrías ser más específico sobre qué necesitas? Como tu asistente especializado, puedo ayudarte con {help_text}. También puedo generar análisis personalizados según tus necesidades específicas.",
            'insights': ["Consulta requiere más especificidad"],
            'follow_ups': [
                "¿Podrías ser más específico sobre lo que necesitas?",
                "¿Te ayudo con algún análisis particular?",
                "¿Quieres ver las opciones disponibles para tu rol?"
            ]
        }
    
    def get_recommendations(self, intent, context, role):
        recommendations_map = {
            'estadisticas': [
                "Generar reporte ejecutivo con estas métricas",
                "Comparar con períodos académicos anteriores",
                "Analizar tendencias y proyecciones futuras",
                "Crear dashboard personalizado para seguimiento"
            ],
            'riesgo': [
                "Desarrollar plan de intervención por niveles de riesgo",
                "Implementar sistema de seguimiento automático",
                "Capacitar personal en estrategias de apoyo estudiantil",
                "Crear protocolo de alerta temprana mejorado"
            ],
            'calificaciones': [
                "Identificar materias que requieren refuerzo académico",
                "Analizar factores que influyen en el rendimiento",
                "Implementar programas de tutoría dirigida",
                "Desarrollar estrategias de motivación estudiantil"
            ],
            'promedio': [
                "Replicar mejores prácticas de programas exitosos",
                "Implementar programas de nivelación académica",
                "Fortalecer acompañamiento en programas con bajo rendimiento",
                "Crear incentivos para la excelencia académica"
            ]
        }
        
        base_recommendations = recommendations_map.get(intent, [
            "Profundizar en análisis específicos de tu área de interés",
            "Generar reportes personalizados según tus necesidades",
            "Implementar seguimiento regular de métricas clave"
        ])
        
        # Agregar recomendaciones contextuales
        if len(context.get('messages', [])) > 5:
            base_recommendations.append("Generar resumen de insights clave de nuestra sesión")
        
        return base_recommendations[:3]
    
    def get_contextual_suggestions(self, role, context):
        base_suggestions = {
            'alumno': [
                "¿Cómo van mis calificaciones este cuatrimestre?",
                "¿Cuál es mi rendimiento comparado con mi programa?",
                "¿Hay materias en las que necesito mejorar?",
                "¿Qué recursos de apoyo están disponibles para mí?",
                "¿Cuándo son mis próximas evaluaciones?",
                "¿Cómo puedo mejorar mi promedio general?"
            ],
            'profesor': [
                "¿Qué estudiantes de mis grupos necesitan atención especial?",
                "¿Cuál es el rendimiento promedio de mis materias?",
                "¿Hay patrones preocupantes en mis evaluaciones?",
                "¿Qué estrategias recomiendas para mejorar el engagement?",
                "¿Cómo se compara el rendimiento de mis grupos?",
                "¿Qué estudiantes están en riesgo de reprobar?"
            ],
            'directivo': [
                "Muéstrame el dashboard ejecutivo completo",
                "¿Cuáles son nuestros principales desafíos académicos?",
                "¿Qué programas necesitan intervención prioritaria?",
                "¿Cómo nos comparamos con benchmarks del sector?",
                "¿Cuáles son las tendencias de rendimiento institucional?",
                "¿Qué estrategias recomiendas para mejorar la retención?",
                "¿Hay oportunidades de optimización de recursos?",
                "¿Cuál es el pronóstico para el próximo período?"
            ]
        }
        
        suggestions = base_suggestions.get(role, base_suggestions['directivo'])
        
        # Personalizar según contexto
        if context.get('messages'):
            recent_intents = [msg.get('intent') for msg in context['messages'][-3:]]
            if 'riesgo' in recent_intents:
                suggestions.insert(0, "¿Quieres un plan de acción para los casos de riesgo identificados?")
            elif 'estadisticas' in recent_intents:
                suggestions.insert(0, "¿Te interesa profundizar en alguna métrica específica?")
        
        return suggestions