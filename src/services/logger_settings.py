import logging
from datetime import datetime, timedelta, timezone

# Установка часового пояса (kaliningrad)
kld_tz = timezone(timedelta(hours=2), name='KLD')

# Создание объекта datetime в нужном часовом поясе
now = datetime.now(tz=kld_tz)
file_name = f'src/logs/{now.strftime("%d_%m_%Y_time_%H_%M_%S")}.log'


class KaliningradFormatter(logging.Formatter):
    def formatTime(self, record, datefmt=None):
        dt = datetime.fromtimestamp(record.created, tz=timezone(timedelta(hours=2)))  # Калининградское время
        return dt.strftime('%d-%m-%Y %H:%M:%S %Z')


logger_config = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'kaliningrad_format': {
            '()': KaliningradFormatter,
            'format': '{asctime} - {levelname} - {message}',
            'style': '{',
        }
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'level': 'DEBUG',
            'formatter': 'kaliningrad_format'
        },
        'file': {
            'class': 'logging.FileHandler',
            'level': 'DEBUG',
            'formatter': 'kaliningrad_format',
            'filename': file_name,
            'mode': "w"
        }
    },
    'loggers': {
        'tg_bot': {
            'level': 'DEBUG',
            'handlers': ['console', 'file']
        },
        'sqlalchemy': {
            'level': 'ERROR',
            'handlers': ['console', 'file']
        }
    }
}
