import logging
import os
from datetime import datetime

def setup_logging():
    """Configurar el sistema de logging"""
    log_level = os.environ.get('LOG_LEVEL', 'INFO').upper()
    
    logging.basicConfig(
        level=getattr(logging, log_level, logging.INFO),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler('dtai_assistant.log') if os.path.exists('.') else logging.NullHandler()
        ]
    )
    
    # Configurar loggers específicos
    logging.getLogger('mysql.connector').setLevel(logging.WARNING)
    logging.getLogger('werkzeug').setLevel(logging.WARNING)

def format_number(number):
    """Formatear números para mejor legibilidad"""
    if number is None:
        return "N/A"
    
    if isinstance(number, float):
        if number.is_integer():
            return f"{int(number):,}"
        else:
            return f"{number:,.2f}"
    
    return f"{number:,}"

def format_percentage(value, total):
    """Calcular y formatear porcentajes"""
    if total == 0:
        return "0.0%"
    
    percentage = (value / total) * 100
    return f"{percentage:.1f}%"

def get_status_emoji(status_type, value, thresholds=None):
    """Obtener emoji basado en estado y umbrales"""
    if not thresholds:
        thresholds = {
            'excellent': 90,
            'good': 70,
            'warning': 50,
            'critical': 30
        }
    
    if status_type == 'percentage':
        if value >= thresholds['excellent']:
            return "🟢"
        elif value >= thresholds['good']:
            return "🔵"
        elif value >= thresholds['warning']:
            return "🟡"
        else:
            return "🔴"
    
    elif status_type == 'risk':
        if value < 3:
            return "🟢"
        elif value < 7:
            return "🟡"
        elif value < 12:
            return "🟠"
        else:
            return "🔴"
    
    return "⚪"

def calculate_academic_status(average):
    """Determinar estatus académico basado en promedio"""
    if average >= 9.0:
        return {
            'status': 'EXCELENCIA',
            'description': 'Rendimiento excepcional',
            'color': 'green',
            'emoji': '🏆'
        }
    elif average >= 8.0:
        return {
            'status': 'SOBRESALIENTE',
            'description': 'Muy buen rendimiento',
            'color': 'blue',
            'emoji': '⭐'
        }
    elif average >= 7.0:
        return {
            'status': 'SATISFACTORIO',
            'description': 'Rendimiento aceptable',
            'color': 'yellow',
            'emoji': '✅'
        }
    elif average >= 6.0:
        return {
            'status': 'REQUIERE MEJORA',
            'description': 'Necesita atención',
            'color': 'orange',
            'emoji': '⚠️'
        }
    else:
        return {
            'status': 'CRÍTICO',
            'description': 'Requiere intervención inmediata',
            'color': 'red',
            'emoji': '🚨'
        }

def get_risk_level_info(level):
    """Obtener información detallada sobre niveles de riesgo"""
    risk_levels = {
        'critico': {
            'priority': 1,
            'response_time': '24-48 horas',
            'description': 'Requiere intervención inmediata',
            'actions': [
                'Contacto inmediato con estudiante y familia',
                'Evaluación psicológica si es necesario',
                'Plan de apoyo personalizado',
                'Seguimiento diario inicial'
            ],
            'emoji': '🔴',
            'color': 'red'
        },
        'alto': {
            'priority': 2,
            'response_time': '1 semana',
            'description': 'Necesita seguimiento especializado',
            'actions': [
                'Entrevista con el estudiante',
                'Contacto con familia',
                'Plan de apoyo académico',
                'Seguimiento semanal'
            ],
            'emoji': '🟡',
            'color': 'orange'
        },
        'medio': {
            'priority': 3,
            'response_time': '2 semanas',
            'description': 'Monitoreo preventivo',
            'actions': [
                'Conversación con el estudiante',
                'Revisión de progreso académico',
                'Seguimiento quincenal',
                'Recursos de apoyo disponibles'
            ],
            'emoji': '🟠',
            'color': 'yellow'
        },
        'bajo': {
            'priority': 4,
            'response_time': '1 mes',
            'description': 'Seguimiento de rutina',
            'actions': [
                'Monitoreo regular',
                'Check-in mensual',
                'Recursos preventivos'
            ],
            'emoji': '🟢',
            'color': 'green'
        }
    }
    
    return risk_levels.get(level.lower(), risk_levels['medio'])

def format_date_relative(date_obj):
    """Formatear fecha de manera relativa"""
    if not isinstance(date_obj, datetime):
        return "Fecha no disponible"
    
    now = datetime.now()
    diff = now - date_obj
    
    if diff.days == 0:
        if diff.seconds < 3600:
            minutes = diff.seconds // 60
            return f"hace {minutes} minuto{'s' if minutes != 1 else ''}"
        else:
            hours = diff.seconds // 3600
            return f"hace {hours} hora{'s' if hours != 1 else ''}"
    elif diff.days == 1:
        return "ayer"
    elif diff.days < 7:
        return f"hace {diff.days} días"
    elif diff.days < 30:
        weeks = diff.days // 7
        return f"hace {weeks} semana{'s' if weeks != 1 else ''}"
    else:
        return date_obj.strftime("%d/%m/%Y")

def generate_trend_indicator(current, previous):
    """Generar indicador de tendencia"""
    if previous == 0:
        return {
            'direction': 'neutral',
            'change': 0,
            'indicator': '➡️',
            'description': 'Sin datos previos para comparar'
        }
    
    change = ((current - previous) / previous) * 100
    
    if change > 5:
        return {
            'direction': 'up',
            'change': change,
            'indicator': '📈',
            'description': f'Incremento del {change:.1f}%'
        }
    elif change < -5:
        return {
            'direction': 'down',
            'change': abs(change),
            'indicator': '📉',
            'description': f'Disminución del {abs(change):.1f}%'
        }
    else:
        return {
            'direction': 'stable',
            'change': change,
            'indicator': '➡️',
            'description': 'Estable'
        }

def clean_and_validate_data(data):
    """Limpiar y validar datos de entrada"""
    if not data:
        return []
    
    cleaned_data = []
    for item in data:
        if isinstance(item, dict):
            cleaned_item = {}
            for key, value in item.items():
                if value is not None:
                    if isinstance(value, str):
                        cleaned_item[key] = value.strip()
                    else:
                        cleaned_item[key] = value
                else:
                    cleaned_item[key] = "N/A"
            cleaned_data.append(cleaned_item)
    
    return cleaned_data

def calculate_distribution_stats(values):
    """Calcular estadísticas de distribución"""
    if not values:
        return None
    
    values = [v for v in values if v is not None and isinstance(v, (int, float))]
    
    if not values:
        return None
    
    sorted_values = sorted(values)
    n = len(sorted_values)
    
    return {
        'count': n,
        'min': min(sorted_values),
        'max': max(sorted_values),
        'mean': sum(sorted_values) / n,
        'median': sorted_values[n//2] if n % 2 == 1 else (sorted_values[n//2-1] + sorted_values[n//2]) / 2,
        'range': max(sorted_values) - min(sorted_values),
        'q1': sorted_values[n//4] if n > 3 else sorted_values[0],
        'q3': sorted_values[3*n//4] if n > 3 else sorted_values[-1]
    }

def generate_insights_from_data(data, data_type='general'):
    """Generar insights automáticos de los datos"""
    insights = []
    
    if not data:
        return ["No hay datos suficientes para generar insights"]
    
    if data_type == 'grades':
        averages = [item.get('promedio_general', 0) for item in data if item.get('promedio_general')]
        if averages:
            stats = calculate_distribution_stats(averages)
            if stats:
                if stats['mean'] > 8.5:
                    insights.append("Rendimiento académico excepcional en el sistema")
                elif stats['mean'] < 7.0:
                    insights.append("Oportunidad de mejora en el rendimiento general")
                
                if stats['range'] > 3.0:
                    insights.append("Alta variabilidad en el rendimiento estudiantil")
    
    elif data_type == 'risk':
        critical_count = len([item for item in data if item.get('nivel_riesgo') == 'critico'])
        if critical_count > len(data) * 0.3:
            insights.append("Proporción elevada de casos críticos requiere atención")
        elif critical_count == 0:
            insights.append("Excelente gestión preventiva - sin casos críticos")
    
    elif data_type == 'programs':
        if len(data) > 5:
            top_performer = max(data, key=lambda x: x.get('promedio_carrera', 0))
            insights.append(f"Programa líder: {top_performer.get('carrera', 'N/A')}")
    
    return insights if insights else ["Datos procesados correctamente"]

def format_response_with_structure(title, data, insights=None, recommendations=None):
    """Formatear respuesta con estructura consistente"""
    response = f"**{title}**\n\n"
    
    if isinstance(data, str):
        response += data
    elif isinstance(data, list) and data:
        for item in data:
            if isinstance(item, str):
                response += f"• {item}\n"
            elif isinstance(item, dict):
                response += format_dict_item(item)
    
    if insights:
        response += "\n**Insights Clave:**\n"
        for insight in insights:
            response += f"• {insight}\n"
    
    if recommendations:
        response += "\n**Recomendaciones:**\n"
        for rec in recommendations:
            response += f"• {rec}\n"
    
    return response

def format_dict_item(item):
    """Formatear item de diccionario para respuesta"""
    formatted = ""
    
    # Campos principales
    if 'nombre' in item and 'apellido' in item:
        formatted += f"**{item['nombre']} {item['apellido']}**"
        if 'matricula' in item:
            formatted += f" ({item['matricula']})"
        formatted += "\n"
    elif 'nombre' in item:
        formatted += f"**{item['nombre']}**\n"
    
    # Información adicional
    for key, value in item.items():
        if key not in ['nombre', 'apellido', 'matricula'] and value is not None:
            formatted += f"  {key.replace('_', ' ').title()}: {value}\n"
    
    formatted += "\n"
    return formatted

def validate_user_input(user_input, input_type='general'):
    """Validar entrada del usuario"""
    if not user_input or not isinstance(user_input, str):
        return False, "Entrada inválida"
    
    user_input = user_input.strip()
    
    if len(user_input) < 1:
        return False, "Entrada vacía"
    
    if len(user_input) > 1000:
        return False, "Entrada demasiado larga"
    
    # Validaciones específicas por tipo
    if input_type == 'academic_query':
        forbidden_patterns = ['DROP', 'DELETE', 'INSERT', 'UPDATE', 'ALTER']
        if any(pattern in user_input.upper() for pattern in forbidden_patterns):
            return False, "Contenido no permitido detectado"
    
    return True, "Entrada válida"

def get_system_status():
    """Obtener estado del sistema"""
    return {
        'timestamp': datetime.now().isoformat(),
        'status': 'operational',
        'version': '5.0.0',
        'components': {
            'database': 'connected',
            'ai_engine': 'active',
            'context_manager': 'operational',
            'response_generator': 'active'
        },
        'uptime': 'continuous',
        'last_maintenance': 'automated'
    }