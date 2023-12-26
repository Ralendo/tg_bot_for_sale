from src.config import Config

filling_name = """
- Хорошо, введи имя человека...
"""
next_name = """
- Отлично, напиши мне имя следующего человека, на которого был куплен билет...
"""
error_name = """
- Напиши мне тогда ещё раз :)
"""
final_fill = f"""
- Поздравляю, вот твой билет! Жду тебя на месте в {Config.time_arrive} {Config.date_arrive} :)
А билет у тебя на имя (имена):"""

ticket_fill = """
- Вот твой билет на имя (имена):
"""

fill_message = {
	'filling_name': filling_name,
	'next_name': next_name,
	'error_name': error_name,
	'final_fill': final_fill,
	'ticket_fill': ticket_fill
}