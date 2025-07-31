import re
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class IntentClassifier:
    def __init__(self):
        self.intent_patterns = self._initialize_patterns()
        self.contextual_patterns = self._initialize_contextual_patterns()
        self.role_specific_intents = self._initialize_role_patterns()
    
    def _initialize_patterns(self):
        return {
            'saludo': {
                'patterns': [
                    'hola', 'hello', 'hi', 'hey', 'buenos días', 'buenas tardes', 
                    'buenas noches', 'qué tal', 'como estas', 'saludos', 'buen día',
                    'que onda', 'wassup', 'muy buenos días', 'hola que tal', 'buenas',
                    'good morning', 'good afternoon', 'good evening', 'howdy',
                    'holi', 'holaa', 'hola como andas', 'que tal todo'
                ],
                'weight': 1.0
            },
            
            'despedida': {
                'patterns': [
                    'adiós', 'bye', 'hasta luego', 'nos vemos', 'chao', 'goodbye',
                    'hasta la vista', 'hasta pronto', 'me despido', 'que tengas buen día',
                    'hasta mañana', 'see you later', 'nos hablamos', 'cuídate',
                    'me voy', 'ya me retiro', 'nos vemos luego', 'que descanses',
                    'hasta otra', 'bye bye', 'see ya', 'take care'
                ],
                'weight': 1.0
            },
            
            'agradecimiento': {
                'patterns': [
                    'gracias', 'te agradezco', 'muchas gracias', 'thank you', 'thanks',
                    'mil gracias', 'te lo agradezco mucho', 'muy agradecido', 'agradezco',
                    'gracias por todo', 'muchas gracias por', 'te doy las gracias',
                    'está genial gracias', 'perfecto gracias', 'excelente gracias',
                    'grazie', 'merci', 'danke', 'arigato'
                ],
                'weight': 1.0
            },
            
            'pregunta_estado': {
                'patterns': [
                    'cómo estás', 'que tal estás', 'how are you', 'como te va',
                    'cómo te encuentras', 'que tal te va', 'como andas', 'cómo vas',
                    'todo bien contigo', 'como sigues', 'qué tal todo', 'how do you do',
                    'como te sientes', 'todo ok', 'como la llevas', 'que tal el día'
                ],
                'weight': 1.2
            },
            
            'pregunta_identidad': {
                'patterns': [
                    'quién eres', 'qué eres', 'who are you', 'qué puedes hacer',
                    'cuáles son tus funciones', 'para qué sirves', 'qué haces',
                    'cuál es tu propósito', 'de qué me puedes ayudar', 'qué tipo de asistente eres',
                    'cuéntame sobre ti', 'preséntate', 'dime quien eres', 'what can you do',
                    'como funcionas', 'que sabes hacer', 'en que me ayudas'
                ],
                'weight': 1.2
            },
            
            'estadisticas': {
                'patterns': [
                    'estadísticas', 'números', 'datos', 'resumen', 'panorama general',
                    'métricas', 'indicadores', 'dashboard', 'reporte general', 'cifras',
                    'analytics', 'información general', 'estado del sistema', 'overview',
                    'snapshot', 'estadísticas generales', 'datos generales', 'números generales',
                    'resumen ejecutivo', 'indicadores clave', 'métricas principales',
                    'dashboard ejecutivo', 'reporte institucional', 'datos institucionales'
                ],
                'weight': 1.1
            },
            
            'riesgo': {
                'patterns': [
                    'riesgo', 'problemas académicos', 'dificultades', 'estudiantes problema',
                    'alumnos difíciles', 'deserción', 'abandono escolar', 'estudiantes en peligro',
                    'alumnos vulnerables', 'casos críticos', 'alertas académicas', 'seguimiento especial',
                    'intervención', 'estudiantes que necesitan ayuda', 'problemas de rendimiento',
                    'alumnos en riesgo', 'reportes de riesgo', 'casos urgentes', 'alerta temprana',
                    'estudiantes críticos', 'situaciones problemáticas', 'casos preocupantes'
                ],
                'weight': 1.1
            },
            
            'calificaciones': {
                'patterns': [
                    'calificaciones', 'notas', 'puntuaciones', 'resultados', 'cómo van mis materias',
                    'cómo voy académicamente', 'mis notas', 'rendimiento académico', 'evaluaciones',
                    'exámenes', 'parciales', 'promedios', 'boleta', 'historial académico',
                    'como me fue', 'que tal mis calificaciones', 'revisar mis notas',
                    'ver calificaciones', 'consultar notas', 'mis resultados', 'grades',
                    'mis puntuaciones', 'evaluación académica', 'desempeño académico'
                ],
                'weight': 1.1
            },
            
            'promedio': {
                'patterns': [
                    'promedio', 'rendimiento', 'desempeño', 'cómo van las carreras', 'performance',
                    'estadísticas académicas', 'métricas de rendimiento', 'análisis comparativo',
                    'ranking académico', 'posición académica', 'nivel académico', 'índices académicos',
                    'promedio por carrera', 'rendimiento por programa', 'desempeño institucional',
                    'comparación académica', 'benchmarking académico', 'rendimiento comparativo'
                ],
                'weight': 1.1
            },
            
            'solicitudes_ayuda': {
                'patterns': [
                    'solicitudes de ayuda', 'ayuda pendiente', 'peticiones de apoyo', 'solicitudes pendientes',
                    'estudiantes pidiendo ayuda', 'casos de ayuda', 'apoyo estudiantil', 'asistencia pendiente',
                    'solicitudes sin resolver', 'ayudas por atender', 'peticiones urgentes',
                    'solicitudes de apoyo', 'casos de soporte', 'ayuda estudiantil', 'asistencia académica',
                    'apoyo institucional', 'servicios de ayuda', 'solicitudes de asistencia'
                ],
                'weight': 1.1
            },
            
            'materias': {
                'patterns': [
                    'materias', 'asignaturas', 'clases', 'cursos', 'subjects', 'disciplinas',
                    'módulos', 'seminarios', 'talleres', 'laboratorios', 'materias reprobadas',
                    'asignaturas pendientes', 'materias difíciles', 'clases complicadas',
                    'materias problemáticas', 'asignaturas críticas', 'cursos con problemas',
                    'subjects with issues', 'materias con alta reprobación', 'asignaturas complejas'
                ],
                'weight': 1.0
            },
            
            'profesores': {
                'patterns': [
                    'profesores', 'maestros', 'docentes', 'instructores', 'catedráticos',
                    'personal docente', 'facultad', 'staff académico', 'profesorado',
                    'mentores', 'tutores', 'coordinadores académicos', 'teachers', 'faculty',
                    'equipo docente', 'planta académica', 'cuerpo docente', 'profesores activos',
                    'docentes asignados', 'instructores disponibles', 'mentores académicos'
                ],
                'weight': 1.0
            },
            
            'estudiantes': {
                'patterns': [
                    'estudiantes', 'alumnos', 'muchachos', 'chavos', 'compañeros',
                    'población estudiantil', 'matrícula', 'cuerpo estudiantil',
                    'comunidad estudiantil', 'estudiantes activos', 'inscripciones',
                    'alumnado', 'students', 'learners', 'pupils', 'estudiantes matriculados',
                    'alumnos inscritos', 'estudiantes registrados', 'población académica'
                ],
                'weight': 1.0
            },
            
            'horarios': {
                'patterns': [
                    'horarios', 'calendario', 'schedule', 'programa', 'cronograma',
                    'horario de clases', 'agenda académica', 'distribución horaria',
                    'programación académica', 'itinerario', 'tiempos de clase',
                    'horarios de materias', 'calendario académico', 'schedule of classes',
                    'timetable', 'horarios escolares', 'programación de clases',
                    'distribución de horarios', 'calendario de clases', 'agenda de clases'
                ],
                'weight': 1.0
            },
            
            'analisis_avanzado': {
                'patterns': [
                    'análisis', 'reporte', 'tendencias', 'comparar', 'evaluar', 'investigar',
                    'profundizar', 'correlaciones', 'patrones', 'insights', 'business intelligence',
                    'data mining', 'análisis predictivo', 'forecasting', 'benchmarking',
                    'análisis profundo', 'estudio detallado', 'investigación académica',
                    'análisis estadístico', 'modelado predictivo', 'análisis de datos',
                    'deep analysis', 'advanced analytics', 'data analysis'
                ],
                'weight': 1.2
            },
            
            'recomendaciones': {
                'patterns': [
                    'recomendaciones', 'qué me sugieres', 'qué debo hacer', 'consejos', 'sugerencias',
                    'qué recomiendas', 'cuál es tu consejo', 'qué opinas', 'qué me aconsejas',
                    'dame tu opinión', 'qué harías tú', 'qué estrategia', 'cómo mejorar',
                    'suggestions', 'recommendations', 'advice', 'what should I do',
                    'tu recomendación', 'que me sugieres hacer', 'cual sería tu consejo',
                    'dame algunas ideas', 'qué me propones', 'cuáles son tus sugerencias'
                ],
                'weight': 1.1
            },
            
            'emocional_positivo': {
                'patterns': [
                    'me siento bien', 'estoy feliz', 'estoy contento', 'me siento genial',
                    'estoy emocionado', 'me siento fantástico', 'estoy motivado', 'me siento inspirado',
                    'estoy optimista', 'me siento satisfecho', 'estoy alegre', 'me siento excelente',
                    'todo va bien', 'estoy de buen humor', 'me siento positivo', 'estoy radiante',
                    'me siento increíble', 'estoy eufórico', 'me siento pleno'
                ],
                'weight': 0.9
            },
            
            'emocional_negativo': {
                'patterns': [
                    'me siento mal', 'estoy triste', 'tengo problemas', 'estoy preocupado',
                    'me siento abrumado', 'estoy frustrado', 'tengo dificultades', 'estoy confundido',
                    'me siento perdido', 'estoy desanimado', 'tengo miedo', 'estoy nervioso',
                    'me siento ansioso', 'estoy estresado', 'tengo dudas', 'me siento inseguro',
                    'estoy deprimido', 'me siento agobiado', 'estoy desesperado', 'tengo angustia',
                    'me siento terrible', 'estoy devastado', 'me siento horrible'
                ],
                'weight': 1.3
            }
        }
    
    def _initialize_contextual_patterns(self):
        return {
            'seguimiento': [
                'más detalles', 'profundiza', 'explícame más', 'y qué más', 'continúa',
                'sigue', 'dime más', 'cuéntame más', 'más información', 'amplía',
                'profundiza en', 'detalla más', 'explica mejor', 'más específico'
            ],
            'confirmacion': [
                'sí', 'claro', 'perfecto', 'ok', 'está bien', 'de acuerdo', 'correcto',
                'exacto', 'por supuesto', 'definitivamente', 'absolutamente', 'sin duda',
                'efectivamente', 'así es', 'tienes razón', 'estoy de acuerdo'
            ],
            'negacion': [
                'no', 'nada', 'mejor no', 'no gracias', 'paso', 'negativo',
                'para nada', 'de ninguna manera', 'jamás', 'nunca', 'no estoy de acuerdo',
                'no me interesa', 'no necesito', 'no quiero'
            ]
        }
    
    def _initialize_role_patterns(self):
        return {
            'alumno': [
                'saludo', 'despedida', 'agradecimiento', 'pregunta_estado', 'pregunta_identidad',
                'calificaciones', 'horarios', 'materias', 'solicitudes_ayuda', 'recomendaciones',
                'emocional_positivo', 'emocional_negativo'
            ],
            'profesor': [
                'saludo', 'despedida', 'agradecimiento', 'pregunta_estado', 'pregunta_identidad',
                'estudiantes', 'riesgo', 'materias', 'horarios', 'calificaciones', 'analisis_avanzado',
                'recomendaciones', 'estadisticas'
            ],
            'directivo': [
                'saludo', 'despedida', 'agradecimiento', 'pregunta_estado', 'pregunta_identidad',
                'estadisticas', 'riesgo', 'promedio', 'analisis_avanzado', 'recomendaciones',
                'estudiantes', 'profesores', 'materias', 'solicitudes_ayuda'
            ]
        }
    
    def classify_intent(self, message, context, role='directivo'):
        try:
            msg = message.lower().strip()
            recent_intents = [m.get('intent') for m in context.get('messages', [])[-3:]]
            
            # Verificar patrones contextuales primero
            if context.get('last_intent'):
                if any(pattern in msg for pattern in self.contextual_patterns['seguimiento']):
                    return f"profundizar_{context['last_intent']}"
                
                if any(pattern in msg for pattern in self.contextual_patterns['confirmacion']):
                    return 'confirmacion'
                
                if any(pattern in msg for pattern in self.contextual_patterns['negacion']):
                    return 'negacion'
            
            # Clasificar por patrones principales
            best_intent = None
            best_score = 0
            
            for intent, config in self.intent_patterns.items():
                # Verificar si la intención es apropiada para el rol
                if intent not in self.role_specific_intents.get(role, []):
                    continue
                
                score = 0
                patterns = config['patterns']
                weight = config['weight']
                
                for pattern in patterns:
                    if pattern in msg:
                        # Puntuación base por coincidencia
                        base_score = len(pattern) / len(msg)
                        
                        # Bonus por coincidencia exacta
                        if msg == pattern:
                            base_score *= 2
                        
                        # Bonus por coincidencia de palabra completa
                        if f' {pattern} ' in f' {msg} ':
                            base_score *= 1.5
                        
                        score += base_score
                
                # Aplicar peso de la intención
                score *= weight
                
                # Bonus por contexto reciente
                if intent in recent_intents:
                    score *= 1.2
                
                if score > best_score:
                    best_score = score
                    best_intent = intent
            
            # Verificar preguntas específicas
            question_starters = ['cuántos', 'cuántas', 'qué', 'cómo', 'dónde', 'cuándo', 'por qué', 'quién', 'cuál', 'cuáles']
            if any(msg.startswith(starter) for starter in question_starters):
                if best_score < 0.3:  # Solo si no encontramos una intención clara
                    return 'pregunta_especifica'
            
            # Clasificación por palabras clave específicas si no hay coincidencia clara
            if best_score < 0.2:
                keyword_mapping = {
                    'datos': 'estadisticas',
                    'números': 'estadisticas',
                    'información': 'estadisticas',
                    'reportar': 'analisis_avanzado',
                    'mostrar': 'estadisticas',
                    'ver': 'estadisticas',
                    'ayuda': 'solicitudes_ayuda',
                    'problema': 'riesgo',
                    'dificultad': 'riesgo',
                    'urgente': 'riesgo',
                    'crítico': 'riesgo',
                    'rendimiento': 'promedio',
                    'desempeño': 'promedio'
                }
                
                for keyword, intent in keyword_mapping.items():
                    if keyword in msg and intent in self.role_specific_intents.get(role, []):
                        return intent
            
            # Retornar la mejor intención encontrada o genérica
            if best_intent and best_score > 0.1:
                logger.info(f"Intención clasificada: {best_intent} (score: {best_score:.3f})")
                return best_intent
            
            return 'conversacion_general'
            
        except Exception as e:
            logger.error(f"Error clasificando intención: {e}")
            return 'conversacion_general'
    
    def get_intent_confidence(self, message, intent):
        """Calcula la confianza de una intención específica para un mensaje"""
        try:
            msg = message.lower().strip()
            if intent not in self.intent_patterns:
                return 0.0
            
            config = self.intent_patterns[intent]
            patterns = config['patterns']
            weight = config['weight']
            
            max_score = 0
            for pattern in patterns:
                if pattern in msg:
                    score = len(pattern) / len(msg)
                    if msg == pattern:
                        score *= 2
                    max_score = max(max_score, score)
            
            return min(max_score * weight, 1.0)
            
        except Exception as e:
            logger.error(f"Error calculando confianza: {e}")
            return 0.0
    
    def suggest_clarification(self, message, role):
        """Sugiere clarificaciones para mensajes ambiguos"""
        suggestions = []
        
        msg = message.lower()
        vague_terms = ['información', 'datos', 'cosas', 'todo', 'algo', 'eso']
        
        if any(term in msg for term in vague_terms):
            suggestions.append("¿Podrías ser más específico sobre qué tipo de información necesitas?")
        
        if len(message.split()) < 3:
            role_suggestions = {
                'alumno': "¿Te refieres a tus calificaciones, horarios, o algún problema específico?",
                'profesor': "¿Necesitas información sobre tus estudiantes, grupos, o análisis de rendimiento?",
                'directivo': "¿Buscas estadísticas institucionales, reportes de riesgo, o análisis comparativo?"
            }
            suggestions.append(role_suggestions.get(role, "¿Puedes especificar más tu consulta?"))
        
        return suggestions
    
    def get_related_intents(self, intent):
        """Obtiene intenciones relacionadas para sugerir"""
        related_mapping = {
            'calificaciones': ['promedio', 'materias', 'riesgo'],
            'riesgo': ['solicitudes_ayuda', 'estudiantes', 'recomendaciones'],
            'estadisticas': ['promedio', 'analisis_avanzado', 'estudiantes'],
            'promedio': ['calificaciones', 'materias', 'analisis_avanzado'],
            'materias': ['calificaciones', 'profesores', 'horarios'],
            'profesores': ['materias', 'estudiantes', 'horarios'],
            'estudiantes': ['calificaciones', 'riesgo', 'promedio'],
            'solicitudes_ayuda': ['riesgo', 'estudiantes', 'recomendaciones'],
            'horarios': ['materias', 'profesores', 'estudiantes']
        }
        
        return related_mapping.get(intent, [])