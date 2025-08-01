class IntentClassifier:
    def __init__(self):
        self.intent_patterns = {
            'saludo': ['hola', 'hello', 'hi', 'buenos dias', 'buenas tardes', 'buenas noches'],
            'agradecimiento': ['gracias', 'thank you', 'te lo agradezco'],
            'despedida': ['adios', 'bye', 'hasta luego', 'nos vemos'],
            'emocional_negativo': ['triste', 'deprimido', 'mal', 'terrible', 'horrible'],
            'emocional_positivo': ['feliz', 'contento', 'bien', 'genial', 'excelente'],
            'pregunta_estado': ['como estas', 'que tal', 'como estas', 'how are you'],
            'pregunta_identidad': ['quien eres', 'que eres', 'who are you', 'que puedes hacer'],
            'calificaciones': ['calificaciones', 'notas', 'puntuaciones', 'resultados'],
            'riesgo': ['riesgo', 'problema', 'dificultad', 'ayuda'],
            'promedio': ['promedio', 'carrera', 'rendimiento'],
            'estadisticas': ['estadisticas', 'resumen', 'general', 'numeros'],
            'afirmacion': ['si', 'claro', 'ok', 'esta bien'],
            'negacion': ['no', 'nada', 'mejor no']
        }
    
    def classify(self, message, context):
        msg = message.lower().strip()
        
        for intent, patterns in self.intent_patterns.items():
            if any(pattern in msg for pattern in patterns):
                return intent
        
        if context['last_intent'] and any(w in msg for w in ['mas', 'otro', 'tambien', 'ademas']):
            return f"mas_{context['last_intent']}"
        
        return 'conversacion_general'