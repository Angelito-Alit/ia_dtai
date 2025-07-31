import logging
import re
from collections import defaultdict

logger = logging.getLogger(__name__)

class IntentClassifier:
    def __init__(self):
        self.intent_patterns = {}
        self.role_specific_intents = {}
        self._initialize_patterns()
    
    def initialize(self):
        logger.info("Clasificador de intenciones inicializado")
    
    def _initialize_patterns(self):
        self.intent_patterns = {
            'ver_calificaciones': [
                r'\b(ver|mostrar|consultar|revisar|checar)\b.*\b(calificaciones?|notas?|puntuaciones?|resultados?)\b',
                r'\b(mis|mi)\b.*\b(calificaciones?|notas?)\b',
                r'\b(como.*van|como.*estan)\b.*\b(calificaciones?|notas?)\b',
                r'\b(calificaciones?|notas?)\b.*\b(actuales?|del.*cuatrimestre)\b'
            ],
            
            'alumnos_riesgo': [
                r'\b(alumnos?|estudiantes?)\b.*\b(riesgo|problemas?|dificultades?)\b',
                r'\b(quien|quienes|que.*alumnos?)\b.*\b(riesgo|problema|dificultad)\b',
                r'\b(estudiantes?.*en.*riesgo|alumnos?.*con.*problemas?)\b',
                r'\b(riesgo.*academico|desercion|abandono)\b'
            ],
            
            'promedio_carreras': [
                r'\b(promedio|promedios?)\b.*\b(carrera|carreras?|licenciatura)\b',
                r'\b(rendimiento|desempeño)\b.*\b(carrera|carreras?)\b',
                r'\b(como.*van|estadisticas?)\b.*\b(carreras?|programas?)\b',
                r'\b(analisis?|reporte)\b.*\b(carreras?|academico)\b'
            ],
            
            'materias_reprobadas': [
                r'\b(materias?|asignaturas?)\b.*\b(reprobadas?|reprobados?|fallidas?)\b',
                r'\b(que.*materias?)\b.*\b(mas.*reprobados?|problemas?)\b',
                r'\b(asignaturas?.*con.*mas|materias?.*problematicas?)\b',
                r'\b(indice.*reprobacion|materias?.*dificiles?)\b'
            ],
            
            'mi_horario': [
                r'\b(mi|mis?)\b.*\b(horario|clases?|calendario)\b',
                r'\b(cuando|que.*hora)\b.*\b(clases?|materias?)\b',
                r'\b(horario.*de.*clases?|calendario.*academico)\b',
                r'\b(proximas?.*clases?|siguiente.*clase)\b'
            ],
            'mis_grupos': [
                r'\b(mis?|mi)\b.*\b(grupos?|clases?|materias?.*asignadas?)\b',
                r'\b(que.*grupos?)\b.*\b(tengo|doy|imparto)\b',
                r'\b(grupos?.*asignados?|clases?.*cargo)\b',
                r'\b(cuantos?.*grupos?|cuantas?.*clases?)\b'
            ],
            
            'solicitudes_pendientes': [
                r'\b(solicitudes?)\b.*\b(pendientes?|sin.*resolver)\b',
                r'\b(ayuda|ayudas?)\b.*\b(pendientes?|solicitud)\b',
                r'\b(que.*solicitudes?|cuantas?.*solicitudes?)\b',
                r'\b(estudiantes?.*pidiendo.*ayuda|alumnos?.*necesitan.*ayuda)\b'
            ],
            
            'reportes_riesgo': [
                r'\b(reportes?)\b.*\b(riesgo|pendientes?)\b',
                r'\b(que.*reportes?|cuantos?.*reportes?)\b',
                r'\b(seguimiento|revision)\b.*\b(reportes?|estudiantes?)\b'
            ],
            'estadisticas_generales': [
                r'\b(estadisticas?|resumen|panorama)\b.*\b(general|sistema|universidad)\b',
                r'\b(como.*esta|como.*van)\b.*\b(las.*cosas?|todo|general)\b',
                r'\b(dashboard|panel|indicadores?)\b',
                r'\b(numeros?.*generales?|cifras?.*generales?)\b'
            ],
            
            'analisis_desercion': [
                r'\b(desercion|abandono)\b.*\b(escolar|estudiantes?|alumnos?)\b',
                r'\b(cuantos?.*se.*van|indice.*desercion)\b',
                r'\b(estudiantes?.*que.*abandonan|alumnos?.*baja)\b'
            ],
            'buscar_alumno': [
                r'\b(buscar|encontrar|localizar)\b.*\b(alumno|estudiante)\b',
                r'\b(informacion.*de|datos.*de)\b.*\b(alumno|estudiante)\b',
                r'\b(alumno.*llamado|estudiante.*nombre)\b'
            ],
            
            'buscar_profesor': [
                r'\b(buscar|encontrar)\b.*\b(profesor|maestro|docente)\b',
                r'\b(informacion.*del.*profesor|datos.*profesor)\b',
                r'\b(profesor.*llamado|maestro.*nombre)\b'
            ],
            'solicitar_ayuda': [
                r'\b(necesito.*ayuda|requiero.*ayuda|pedir.*ayuda)\b',
                r'\b(tengo.*problema|problema.*con)\b',
                r'\b(no.*entiendo|no.*se.*como)\b',
                r'\b(ayudenme|ayudame|socorro)\b'
            ],
            
            'como_hacer': [
                r'\b(como.*hacer|como.*puedo)\b',
                r'\b(que.*debo.*hacer|que.*tengo.*que.*hacer)\b',
                r'\b(pasos.*para|proceso.*para)\b',
                r'\b(instrucciones|tutorial|guia)\b'
            ]
        }
        self.role_specific_intents = {
            'alumno': [
                'ver_calificaciones', 'mi_horario', 'solicitar_ayuda', 'como_hacer',
                'buscar_profesor', 'ver_noticias'
            ],
            'profesor': [
                'mis_grupos', 'alumnos_riesgo', 'reportes_riesgo', 'estadisticas_grupos',
                'buscar_alumno', 'crear_reporte'
            ],
            'directivo': [
                'estadisticas_generales', 'promedio_carreras', 'materias_reprobadas',
                'analisis_desercion', 'solicitudes_pendientes', 'reportes_sistema'
            ]
        }
    
    def classify(self, text, user_role='alumno'):
        try:
            text_lower = text.lower()
            intent_scores = {}
            
            for intent, patterns in self.intent_patterns.items():
                score = self._calculate_intent_score(text_lower, patterns)
                if intent in self.role_specific_intents.get(user_role, []):
                    score *= 1.5
                
                intent_scores[intent] = score
            best_intent = max(intent_scores.items(), key=lambda x: x[1])
            
            if best_intent[1] < 0.3:
                return self._classify_generic_intent(text_lower, user_role)
            
            logger.info(f"Intención clasificada: {best_intent[0]} (score: {best_intent[1]:.2f})")
            return best_intent[0]
            
        except Exception as e:
            logger.error(f"Error clasificando intención: {e}")
            return 'consulta_general'
    
    def _calculate_intent_score(self, text, patterns):
        max_score = 0
        
        for pattern in patterns:
            matches = len(re.findall(pattern, text, re.IGNORECASE))
            if matches > 0:
                pattern_score = matches * (len(pattern.split()) / 10)
                max_score = max(max_score, pattern_score)
        
        return max_score
    
    def _classify_generic_intent(self, text, user_role):
        generic_keywords = {
            'consulta': ['ver', 'mostrar', 'consultar', 'revisar', 'checar'],
            'analisis': ['analizar', 'reporte', 'estadisticas', 'resumen'],
            'busqueda': ['buscar', 'encontrar', 'localizar', 'ubicar'],
            'ayuda': ['ayuda', 'problema', 'dificultad', 'soporte'],
            'informacion': ['informacion', 'datos', 'detalles', 'info']
        }
        
        for intent_type, keywords in generic_keywords.items():
            for keyword in keywords:
                if keyword in text:
                    return self._map_generic_to_specific(intent_type, user_role)
        question_words = {
            'que': 'consulta_general',
            'como': 'como_hacer',
            'cuando': 'consulta_temporal',
            'donde': 'consulta_ubicacion',
            'quien': 'buscar_persona',
            'cuanto': 'consulta_cantidad'
        }
        
        for q_word, intent in question_words.items():
            if q_word in text:
                return intent
        default_intents = {
            'alumno': 'ver_calificaciones',
            'profesor': 'mis_grupos',
            'directivo': 'estadisticas_generales'
        }
        
        return default_intents.get(user_role, 'consulta_general')
    
    def _map_generic_to_specific(self, generic_intent, user_role):
        mapping = {
            'alumno': {
                'consulta': 'ver_calificaciones',
                'analisis': 'ver_calificaciones',
                'busqueda': 'buscar_profesor',
                'ayuda': 'solicitar_ayuda',
                'informacion': 'ver_calificaciones'
            },
            'profesor': {
                'consulta': 'mis_grupos',
                'analisis': 'alumnos_riesgo',
                'busqueda': 'buscar_alumno',
                'ayuda': 'reportes_riesgo',
                'informacion': 'mis_grupos'
            },
            'directivo': {
                'consulta': 'estadisticas_generales',
                'analisis': 'promedio_carreras',
                'busqueda': 'solicitudes_pendientes',
                'ayuda': 'solicitudes_pendientes',
                'informacion': 'estadisticas_generales'
            }
        }
        
        return mapping.get(user_role, {}).get(generic_intent, 'consulta_general')
    
    def get_intent_confidence(self, text, intent):
        if intent not in self.intent_patterns:
            return 0.0
        
        patterns = self.intent_patterns[intent]
        score = self._calculate_intent_score(text.lower(), patterns)
        confidence = min(score, 1.0)
        return confidence
    
    def suggest_clarification(self, text, user_role):
        suggestions = []
        vague_terms = ['cosas', 'todo', 'algo', 'eso', 'información']
        if any(term in text.lower() for term in vague_terms):
            suggestions.append("¿Puedes ser más específico sobre qué información necesitas?")
        if not any(domain in text.lower() for domain in ['calificaciones', 'alumnos', 'grupos', 'materias']):
            role_suggestions = {
                'alumno': "¿Te refieres a tus calificaciones, horario o información general?",
                'profesor': "¿Necesitas información sobre tus grupos, alumnos o reportes?",
                'directivo': "¿Buscas estadísticas, reportes o información administrativa?"
            }
            suggestions.append(role_suggestions.get(user_role, "¿Puedes especificar el tema?"))
        time_words = ['ahora', 'actual', 'reciente']
        if any(word in text.lower() for word in time_words):
            suggestions.append("¿Te refieres al cuatrimestre actual o un período específico?")
        
        return suggestions
    
    def get_related_intents(self, intent):
        related = {
            'ver_calificaciones': ['mi_horario', 'alumnos_riesgo'],
            'alumnos_riesgo': ['reportes_riesgo', 'solicitudes_pendientes'],
            'promedio_carreras': ['materias_reprobadas', 'estadisticas_generales'],
            'mis_grupos': ['alumnos_riesgo', 'reportes_riesgo'],
            'solicitudes_pendientes': ['alumnos_riesgo', 'reportes_riesgo']
        }
        
        return related.get(intent, [])
    
    def extract_intent_modifiers(self, text):
        modifiers = {}
        temporal_patterns = {
            'actual': r'\b(actual|este|presente|ahora)\b',
            'pasado': r'\b(pasado|anterior|ultimo|previa?)\b',
            'futuro': r'\b(proximo|siguiente|futuro)\b'
        }
        
        for modifier, pattern in temporal_patterns.items():
            if re.search(pattern, text, re.IGNORECASE):
                modifiers['temporal'] = modifier
                break
        quantity_patterns = {
            'todos': r'\b(todos?|todas?|completo|total)\b',
            'algunos': r'\b(algunos?|varias?|ciertos?)\b',
            'pocos': r'\b(pocos?|pocas?|limitados?)\b'
        }
        
        for modifier, pattern in quantity_patterns.items():
            if re.search(pattern, text, re.IGNORECASE):
                modifiers['cantidad'] = modifier
                break
        urgency_patterns = {
            'urgente': r'\b(urgente|inmediato|rapido|ya)\b',
            'normal': r'\b(cuando.*puedas?|sin.*prisa)\b'
        }
        
        for modifier, pattern in urgency_patterns.items():
            if re.search(pattern, text, re.IGNORECASE):
                modifiers['urgencia'] = modifier
                break
        
        return modifiers
    
    def is_question(self, text):
        if text.strip().endswith('?'):
            return True
        question_starters = [
            'qué', 'que', 'cómo', 'como', 'cuándo', 'cuando', 'dónde', 'donde',
            'quién', 'quien', 'cuál', 'cual', 'cuánto', 'cuanto', 'cuánta', 'cuanta',
            'cuántos', 'cuantos', 'cuántas', 'cuantas', 'por qué', 'por que',
            'para qué', 'para que'
        ]
        
        text_lower = text.lower().strip()
        for starter in question_starters:
            if text_lower.startswith(starter):
                return True
        
        return False
    
    def get_intent_examples(self, intent):
        examples = {
            'ver_calificaciones': [
                "¿Cuáles son mis calificaciones?",
                "Muéstrame mis notas del cuatrimestre",
                "¿Cómo van mis calificaciones?",
                "Revisar mis resultados académicos"
            ],
            'alumnos_riesgo': [
                "¿Qué alumnos están en riesgo?",
                "Muéstrame estudiantes con problemas",
                "¿Quiénes necesitan ayuda académica?",
                "Lista de alumnos en situación de riesgo"
            ],
            'promedio_carreras': [
                "¿Cuál es el promedio por carrera?",
                "Análisis de rendimiento por programa",
                "¿Cómo van las carreras académicamente?",
                "Estadísticas de promedios por licenciatura"
            ],
            'mis_grupos': [
                "¿Cuáles son mis grupos?",
                "Muéstrame las clases que imparto",
                "¿Qué materias tengo asignadas?",
                "Lista de mis grupos actuales"
            ]
        }
        
        return examples.get(intent, [])
    
    def get_all_intents_by_role(self, user_role):
        return self.role_specific_intents.get(user_role, [])