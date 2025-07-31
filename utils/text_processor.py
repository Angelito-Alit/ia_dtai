import re
import logging
from datetime import datetime, timedelta
import unicodedata

logger = logging.getLogger(__name__)

class TextProcessor:
    def __init__(self):
        self.patterns = {
            'matricula': r'\b\d{8,12}\b',
            'email': r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
            'telefono': r'\b(\+?\d{1,3}[-.\s]?)?\(?\d{2,4}\)?[-.\s]?\d{3,4}[-.\s]?\d{4}\b',
            'fecha': r'\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b',
            'numero': r'\b\d+\.?\d*\b',
            'codigo_materia': r'\b[A-Z]{2,4}[-]?\d{2,4}\b',
            'porcentaje': r'\b\d+\.?\d*%\b'
        }
        self.synonyms = {
            'calificaciones': ['notas', 'puntuaciones', 'evaluaciones', 'resultados', 'scores'],
            'alumnos': ['estudiantes', 'muchachos', 'chavos', 'personas', 'gente'],
            'profesores': ['maestros', 'docentes', 'profesoras', 'instructores'],
            'materias': ['asignaturas', 'clases', 'cursos', 'subjects'],
            'promedio': ['media', 'average', 'puntaje general'],
            'riesgo': ['peligro', 'problema', 'dificultad', 'conflicto'],
            'horario': ['calendario', 'schedule', 'programa'],
            'grupos': ['clases', 'secciones', 'cursos'],
            'carrera': ['licenciatura', 'ingeniería', 'programa', 'especialidad'],
            'cuatrimestre': ['período', 'semestre', 'trimestre', 'ciclo'],
            'reprobado': ['reprobados', 'fallidos', 'no aprobados', 'suspendidos']
        }
        self.negation_words = ['no', 'sin', 'nunca', 'jamás', 'nada', 'ninguno', 'ninguna', 'tampoco']
        self.stop_words = {
            'el', 'la', 'de', 'que', 'y', 'a', 'en', 'un', 'es', 'se', 'no', 'te', 'lo', 
            'le', 'da', 'su', 'por', 'son', 'con', 'para', 'al', 'del', 'los', 'las',
            'me', 'mi', 'tu', 'él', 'ella', 'esto', 'esta', 'ese', 'esa', 'como', 'pero',
            'si', 'o', 'cuando', 'donde', 'quien', 'cual', 'muy', 'mas', 'ya', 'puede',
            'ser', 'tener', 'hacer', 'estar', 'hay', 'haber', 'ver', 'ir', 'dar'
        }
    
    def process(self, text):
        if not text:
            return ""
        normalized = self._normalize_text(text)
        expanded = self._expand_synonyms(normalized)
        cleaned = self._clean_text(expanded)
        
        return cleaned
    
    def extract_entities(self, text):
        entities = {}
        for entity_type, pattern in self.patterns.items():
            matches = re.findall(pattern, text, re.IGNORECASE)
            if matches:
                entities[entity_type] = matches
        entities.update(self._extract_educational_entities(text))
        entities.update(self._extract_relative_dates(text))
        entities.update(self._extract_proper_names(text))
        
        return entities
    
    def _normalize_text(self, text):
        text = text.lower()
        text = unicodedata.normalize('NFD', text)
        text = ''.join(c for c in text if unicodedata.category(c) != 'Mn' or c in 'ñÑ')
        text = re.sub(r'\s+', ' ', text)
        text = re.sub(r'[^\w\s\.\?\!\,\-\%\@]', '', text)
        
        return text.strip()
    
    def _expand_synonyms(self, text):
        words = text.split()
        expanded_words = []
        
        for word in words:
            expanded = False
            for canonical, synonyms in self.synonyms.items():
                if word in synonyms:
                    expanded_words.append(canonical)
                    expanded = True
                    break
            
            if not expanded:
                expanded_words.append(word)
        
        return ' '.join(expanded_words)
    
    def _clean_text(self, text):
        words = text.split()
        important_words = []
        
        for word in words:
            if word not in self.stop_words or len(word) > 3:
                important_words.append(word)
        
        return ' '.join(important_words)
    
    def _extract_educational_entities(self, text):
        entities = {}
        carreras_patterns = {
            'sistemas': r'\b(sistemas|computacion|informatica|software)\b',
            'industrial': r'\b(industrial|manufactura|produccion)\b',
            'administracion': r'\b(administracion|negocios|empresas)\b',
            'mecatronica': r'\b(mecatronica|robotica|automatizacion)\b',
            'gastronomia': r'\b(gastronomia|culinaria|cocina)\b'
        }
        
        for carrera, pattern in carreras_patterns.items():
            if re.search(pattern, text, re.IGNORECASE):
                if 'carrera' not in entities:
                    entities['carrera'] = []
                entities['carrera'].append(carrera)
        periodos_patterns = {
            'ENE-ABR': r'\b(enero|febrero|marzo|abril|ene-abr|primer.*cuatrimestre)\b',
            'MAY-AGO': r'\b(mayo|junio|julio|agosto|may-ago|segundo.*cuatrimestre)\b',
            'SEP-DIC': r'\b(septiembre|octubre|noviembre|diciembre|sep-dic|tercer.*cuatrimestre)\b'
        }
        
        for periodo, pattern in periodos_patterns.items():
            if re.search(pattern, text, re.IGNORECASE):
                entities['periodo'] = periodo
                break
        cuatrimestre_match = re.search(r'\b(\d+)[°º]?\s*(cuatrimestre|semestre|año)\b', text, re.IGNORECASE)
        if cuatrimestre_match:
            entities['cuatrimestre'] = int(cuatrimestre_match.group(1))
        riesgo_patterns = {
            'academico': r'\b(academico|calificaciones|notas|estudio)\b',
            'asistencia': r'\b(asistencia|faltas|inasistencia|ausentismo)\b',
            'conducta': r'\b(conducta|comportamiento|disciplina)\b',
            'economico': r'\b(economico|dinero|beca|financiero)\b',
            'personal': r'\b(personal|familia|emocional|psicologico)\b'
        }
        
        for tipo_riesgo, pattern in riesgo_patterns.items():
            if re.search(pattern, text, re.IGNORECASE):
                if 'tipo_riesgo' not in entities:
                    entities['tipo_riesgo'] = []
                entities['tipo_riesgo'].append(tipo_riesgo)
        
        return entities
    
    def _extract_relative_dates(self, text):
        entities = {}
        relative_patterns = {
            'hoy': r'\b(hoy|ahora|actual|presente)\b',
            'ayer': r'\b(ayer|anterior)\b',
            'esta_semana': r'\b(esta.*semana|semana.*actual)\b',
            'este_mes': r'\b(este.*mes|mes.*actual)\b',
            'este_cuatrimestre': r'\b(este.*cuatrimestre|cuatrimestre.*actual)\b',
            'ultimo_mes': r'\b(ultimo.*mes|mes.*pasado)\b',
            'ultimo_cuatrimestre': r'\b(ultimo.*cuatrimestre|cuatrimestre.*pasado)\b'
        }
        
        for period, pattern in relative_patterns.items():
            if re.search(pattern, text, re.IGNORECASE):
                entities['fecha_relativa'] = period
                break
        
        return entities
    
    def _extract_proper_names(self, text):
        entities = {}
        name_pattern = r'\b[A-ZÁÉÍÓÚÑ][a-záéíóúñ]+(?:\s+[A-ZÁÉÍÓÚÑ][a-záéíóúñ]+)*\b'
        matches = re.findall(name_pattern, text)
        
        if matches:
            common_words = {'Sistemas', 'Industrial', 'Administracion', 'Universidad', 'Instituto'}
            names = [match for match in matches if match not in common_words and len(match.split()) <= 3]
            
            if names:
                entities['nombres'] = names
        
        return entities
    
    def detect_intent_keywords(self, text):
        intent_keywords = {
            'consulta': ['ver', 'mostrar', 'consultar', 'revisar', 'checar', 'buscar'],
            'analisis': ['analizar', 'analisis', 'reporte', 'estadisticas', 'resumen'],
            'comparacion': ['comparar', 'diferencia', 'mejor', 'peor', 'versus'],
            'filtro': ['filtrar', 'donde', 'que', 'con', 'sin', 'solo'],
            'temporal': ['cuando', 'fecha', 'periodo', 'tiempo', 'durante'],
            'cantidad': ['cuantos', 'cuantas', 'total', 'suma', 'contar'],
            'ayuda': ['ayuda', 'ayudar', 'problema', 'dificultad', 'soporte'],
            'recomendacion': ['recomienda', 'sugerir', 'consejo', 'que.*hacer']
        }
        
        detected_intents = []
        text_lower = text.lower()
        
        for intent, keywords in intent_keywords.items():
            for keyword in keywords:
                if re.search(r'\b' + keyword + r'\b', text_lower):
                    detected_intents.append(intent)
                    break
        
        return detected_intents
    
    def extract_question_type(self, text):
        question_patterns = {
            'que': r'\b(que|qué)\b',
            'como': r'\b(como|cómo)\b',
            'cuando': r'\b(cuando|cuándo)\b',
            'donde': r'\b(donde|dónde)\b',
            'quien': r'\b(quien|quién|quienes|quiénes)\b',
            'cuanto': r'\b(cuanto|cuánto|cuantos|cuántos|cuanta|cuánta|cuantas|cuántas)\b',
            'por_que': r'\b(por.*que|por.*qué|porque|porqué)\b',
            'cual': r'\b(cual|cuál|cuales|cuáles)\b'
        }
        
        for q_type, pattern in question_patterns.items():
            if re.search(pattern, text, re.IGNORECASE):
                return q_type
        
        return 'statement' 
    
    def has_negation(self, text):
        for neg_word in self.negation_words:
            if re.search(r'\b' + neg_word + r'\b', text, re.IGNORECASE):
                return True
        return False
    
    def extract_numbers_and_ranges(self, text):
        entities = {}
        range_pattern = r'\b(\d+(?:\.\d+)?)\s*(?:a|hasta|entre)\s*(\d+(?:\.\d+)?)\b'
        range_matches = re.findall(range_pattern, text, re.IGNORECASE)
        
        if range_matches:
            entities['rangos'] = [(float(start), float(end)) for start, end in range_matches]
        number_pattern = r'\b\d+(?:\.\d+)?\b'
        numbers = re.findall(number_pattern, text)
        
        if numbers:
            entities['numeros'] = [float(n) for n in numbers]
        
        return entities
    
    def clean_for_sql(self, text):
        dangerous_chars = ["'", '"', ';', '--', '/*', '*/', 'xp_', 'sp_']
        
        cleaned = text
        for char in dangerous_chars:
            cleaned = cleaned.replace(char, '')
        cleaned = cleaned[:500]
        
        return cleaned.strip()
    
    def tokenize(self, text):
        tokens = re.findall(r'\b\w+\b', text.lower())
        tokens = [token for token in tokens if len(token) > 2]
        
        return tokens
    
    def get_text_similarity(self, text1, text2):
        tokens1 = set(self.tokenize(text1))
        tokens2 = set(self.tokenize(text2))
        
        if not tokens1 or not tokens2:
            return 0.0
        
        intersection = tokens1.intersection(tokens2)
        union = tokens1.union(tokens2)
        
        return len(intersection) / len(union) if union else 0.0