import logging
from datetime import datetime
from collections import defaultdict

logger = logging.getLogger(__name__)

class ContextManager:
    def __init__(self):
        self.contexts = {}
        self.session_analytics = defaultdict(int)
    
    def get_context(self, user_id):
        if user_id not in self.contexts:
            self.contexts[user_id] = {
                'messages': [],
                'last_intent': None,
                'session_topics': [],
                'user_preferences': {},
                'conversation_depth': 0,
                'session_start': datetime.now(),
                'last_activity': datetime.now(),
                'sentiment_history': [],
                'engagement_level': 'initial'
            }
        return self.contexts[user_id]
    
    def update_context(self, user_id, message, intent, response):
        context = self.get_context(user_id)
        
        sentiment = self.analyze_sentiment(message)
        
        context['messages'].append({
            'user_message': message,
            'bot_response': response[:200],
            'intent': intent,
            'timestamp': datetime.now(),
            'sentiment': sentiment,
            'response_length': len(response)
        })
        
        context['last_intent'] = intent
        context['session_topics'].append(intent)
        context['conversation_depth'] += 1
        context['last_activity'] = datetime.now()
        context['sentiment_history'].append(sentiment)
        context['engagement_level'] = self._calculate_engagement(context)
        
        # Mantener solo los últimos 20 mensajes
        if len(context['messages']) > 20:
            context['messages'] = context['messages'][-20:]
        
        # Mantener solo los últimos 30 sentimientos
        if len(context['sentiment_history']) > 30:
            context['sentiment_history'] = context['sentiment_history'][-30:]
        
        # Actualizar analytics del sistema
        self.session_analytics['total_messages'] += 1
        self.session_analytics[f'intent_{intent}'] += 1
        
        logger.info(f"Contexto actualizado para usuario {user_id}: {intent}")
    
    def analyze_sentiment(self, message):
        positive_indicators = [
            'excelente', 'genial', 'fantástico', 'perfecto', 'bueno', 'bien', 'gracias',
            'me gusta', 'increíble', 'maravilloso', 'estupendo', 'satisfecho', 'feliz',
            'contento', 'alegre', 'optimista', 'positivo', 'emocionado', 'entusiasmado',
            'motivado', 'inspirado', 'agradecido', 'encantado', 'exitoso', 'logrado'
        ]
        
        negative_indicators = [
            'mal', 'terrible', 'horrible', 'problema', 'dificultad', 'preocupado',
            'frustrado', 'molesto', 'enojado', 'triste', 'deprimido', 'confundido',
            'perdido', 'abrumado', 'estresado', 'ansioso', 'nervioso', 'inseguro',
            'desanimado', 'desesperado', 'angustiado', 'devastado', 'decepcionado'
        ]
        
        neutral_indicators = [
            'información', 'datos', 'estadísticas', 'reporte', 'análisis', 'consulta',
            'pregunta', 'duda', 'necesito', 'quiero', 'busco', 'solicito', 'requiero'
        ]
        
        message_lower = message.lower()
        
        positive_count = sum(1 for word in positive_indicators if word in message_lower)
        negative_count = sum(1 for word in negative_indicators if word in message_lower)
        neutral_count = sum(1 for word in neutral_indicators if word in message_lower)
        
        # Sistema de puntuación ponderada
        positive_score = positive_count * 1.2
        negative_score = negative_count * 1.5  # Dar más peso a sentimientos negativos
        neutral_score = neutral_count * 0.8
        
        if negative_score > positive_score and negative_score > neutral_score:
            return 'negative'
        elif positive_score > negative_score and positive_score > neutral_score:
            return 'positive'
        else:
            return 'neutral'
    
    def _calculate_engagement(self, context):
        depth = context['conversation_depth']
        topic_variety = len(set(context['session_topics']))
        recent_activity = (datetime.now() - context['last_activity']).seconds < 300  # 5 minutos
        
        # Calcular puntuación de engagement
        engagement_score = 0
        
        if depth > 15:
            engagement_score += 4
        elif depth > 8:
            engagement_score += 3
        elif depth > 3:
            engagement_score += 2
        else:
            engagement_score += 1
        
        if topic_variety > 6:
            engagement_score += 3
        elif topic_variety > 3:
            engagement_score += 2
        elif topic_variety > 1:
            engagement_score += 1
        
        if recent_activity:
            engagement_score += 1
        
        # Considerar sentimiento general
        if len(context['sentiment_history']) > 2:
            recent_sentiments = context['sentiment_history'][-3:]
            if recent_sentiments.count('positive') > recent_sentiments.count('negative'):
                engagement_score += 1
        
        # Clasificar nivel de engagement
        if engagement_score >= 8:
            return 'highly_engaged'
        elif engagement_score >= 6:
            return 'actively_engaged'
        elif engagement_score >= 4:
            return 'moderately_engaged'
        elif engagement_score >= 2:
            return 'exploratory'
        else:
            return 'initial'
    
    def get_conversation_mood(self, user_id):
        context = self.get_context(user_id)
        
        if not context['sentiment_history']:
            return 'neutral'
        
        recent_sentiments = context['sentiment_history'][-5:]  # Últimos 5 sentimientos
        
        positive_count = recent_sentiments.count('positive')
        negative_count = recent_sentiments.count('negative')
        neutral_count = recent_sentiments.count('neutral')
        
        total = len(recent_sentiments)
        
        if positive_count > total * 0.6:
            return 'predominantly_positive'
        elif negative_count > total * 0.4:
            return 'needs_support'
        elif positive_count > negative_count:
            return 'positive_leaning'
        elif negative_count > positive_count:
            return 'concerning_trend'
        else:
            return 'balanced'
    
    def get_conversation_insights(self, user_id):
        context = self.get_context(user_id)
        insights = []
        
        # Análisis de profundidad
        depth = context['conversation_depth']
        if depth > 20:
            insights.append("Usuario muy comprometido - conversación extremadamente profunda")
        elif depth > 10:
            insights.append("Alta participación - usuario activamente involucrado")
        elif depth > 5:
            insights.append("Engagement moderado - conversación productiva")
        
        # Análisis de diversidad temática
        unique_topics = len(set(context['session_topics']))
        if unique_topics > 7:
            insights.append("Conversación muy diversa - múltiples áreas exploradas")
        elif unique_topics > 4:
            insights.append("Buena variedad temática - intereses amplios")
        elif unique_topics > 2:
            insights.append("Enfoque temático específico")
        
        # Análisis de tendencia emocional
        mood = self.get_conversation_mood(user_id)
        mood_insights = {
            'predominantly_positive': "Tendencia emocional muy positiva - usuario satisfecho",
            'positive_leaning': "Tendencia emocional positiva - experiencia favorable",
            'needs_support': "Usuario requiere apoyo adicional - atención empática",
            'concerning_trend': "Tendencia preocupante - considerar escalamiento",
            'balanced': "Estado emocional equilibrado - interacción profesional"
        }
        
        if mood in mood_insights:
            insights.append(mood_insights[mood])
        
        # Análisis de patrones de interacción
        if len(context['messages']) > 3:
            avg_response_length = sum(msg['response_length'] for msg in context['messages']) / len(context['messages'])
            if avg_response_length > 1000:
                insights.append("Respuestas detalladas proporcionadas - análisis profundo")
            elif avg_response_length > 500:
                insights.append("Información completa compartida - buena profundidad")
        
        # Análisis de continuidad
        session_duration = (datetime.now() - context['session_start']).seconds / 60  # en minutos
        if session_duration > 30:
            insights.append("Sesión extendida - alto nivel de compromiso")
        elif session_duration > 15:
            insights.append("Sesión productiva - tiempo suficiente para análisis")
        
        return insights
    
    def get_session_summary(self, user_id):
        context = self.get_context(user_id)
        
        if context['conversation_depth'] < 2:
            return "Sesión inicial - fase de exploración"
        
        # Analizar temas principales
        topic_counts = {}
        for topic in context['session_topics']:
            topic_counts[topic] = topic_counts.get(topic, 0) + 1
        
        main_topics = sorted(topic_counts.items(), key=lambda x: x[1], reverse=True)[:3]
        topic_names = [topic[0] for topic in main_topics]
        
        # Generar resumen basado en patrones
        if len(topic_names) == 1:
            return f"Sesión especializada - enfoque profundo en {topic_names[0]}"
        elif 'estadisticas' in topic_names and 'riesgo' in topic_names:
            return "Sesión de análisis institucional - revisión integral de métricas y alertas"
        elif 'analisis_avanzado' in topic_names:
            return "Sesión de consultoría avanzada - análisis técnico especializado"
        elif len(set(topic_names)) >= 3:
            return "Sesión exploratoria amplia - múltiples áreas de interés"
        else:
            return f"Sesión enfocada - trabajo colaborativo en {' y '.join(topic_names)}"
    
    def get_full_context_analysis(self, user_id):
        context = self.get_context(user_id)
        
        return {
            'conversation_metrics': {
                'total_messages': len(context['messages']),
                'conversation_depth': context['conversation_depth'],
                'session_duration_minutes': (datetime.now() - context['session_start']).seconds / 60,
                'last_activity': context['last_activity'].isoformat(),
                'engagement_level': context['engagement_level']
            },
            'topic_analysis': {
                'topics_explored': len(set(context['session_topics'])),
                'topic_distribution': {topic: context['session_topics'].count(topic) 
                                    for topic in set(context['session_topics'])},
                'last_intent': context['last_intent'],
                'session_summary': self.get_session_summary(user_id)
            },
            'emotional_analysis': {
                'current_mood': self.get_conversation_mood(user_id),
                'sentiment_distribution': {
                    'positive': context['sentiment_history'].count('positive'),
                    'negative': context['sentiment_history'].count('negative'),
                    'neutral': context['sentiment_history'].count('neutral')
                },
                'mood_trend': self._get_mood_trend(context)
            },
            'insights': self.get_conversation_insights(user_id),
            'recent_messages': context['messages'][-5:] if context['messages'] else []
        }
    
    def _get_mood_trend(self, context):
        if len(context['sentiment_history']) < 4:
            return 'insufficient_data'
        
        recent = context['sentiment_history'][-3:]
        earlier = context['sentiment_history'][-6:-3] if len(context['sentiment_history']) >= 6 else []
        
        if not earlier:
            return 'stable'
        
        recent_positive = recent.count('positive') / len(recent)
        earlier_positive = earlier.count('positive') / len(earlier)
        
        if recent_positive > earlier_positive + 0.2:
            return 'improving'
        elif recent_positive < earlier_positive - 0.2:
            return 'declining'
        else:
            return 'stable'
    
    def clear_context(self, user_id):
        if user_id in self.contexts:
            del self.contexts[user_id]
            logger.info(f"Contexto limpiado para usuario {user_id}")
            return True
        return False
    
    def get_system_analytics(self):
        total_users = len(self.contexts)
        active_users = len([
            user_id for user_id, context in self.contexts.items()
            if (datetime.now() - context['last_activity']).seconds < 1800  # 30 minutos
        ])
        
        total_messages = sum(len(context['messages']) for context in self.contexts.values())
        
        # Análisis de engagement
        engagement_distribution = {}
        for context in self.contexts.values():
            level = context['engagement_level']
            engagement_distribution[level] = engagement_distribution.get(level, 0) + 1
        
        # Análisis de temas populares
        all_topics = []
        for context in self.contexts.values():
            all_topics.extend(context['session_topics'])
        
        topic_popularity = {}
        for topic in set(all_topics):
            topic_popularity[topic] = all_topics.count(topic)
        
        # Top 5 temas más consultados
        popular_topics = sorted(topic_popularity.items(), key=lambda x: x[1], reverse=True)[:5]
        
        return {
            'user_metrics': {
                'total_users': total_users,
                'active_users': active_users,
                'total_conversations': total_messages,
                'avg_messages_per_user': total_messages / total_users if total_users > 0 else 0
            },
            'engagement_analysis': engagement_distribution,
            'topic_trends': {
                'popular_topics': popular_topics,
                'topic_diversity': len(set(all_topics)),
                'total_topic_interactions': len(all_topics)
            },
            'system_health': {
                'active_sessions': active_users,
                'memory_usage': f"{len(self.contexts)} contexts stored",
                'last_updated': datetime.now().isoformat()
            }
        }