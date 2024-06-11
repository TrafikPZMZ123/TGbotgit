from ping3 import ping
import config
import telebot
import time
import threading
import os
import subprocess

bot = telebot.TeleBot(config.token)  # Создание бота с указанным токеном

is_running = False # отслеживания состояния

def check_ping(chat_id, ip_address): # Функция для проверки пинга по указанному IP-адресу
    time.sleep(3)
    global is_running
    is_running = True # Устанавливает флаг запуска проверки
    while is_running:  # Цикл проверки состояния пинга (пока флаг установлен в True)
        if ping(ip_address) is None:   # Проверка пинга по адресу
            bot.send_message(chat_id, f'Сервер {ip_address} Офлайн') # Отправка сообщения о статусе сервера
        else:
            bot.send_message(chat_id, f'Сервер {ip_address} Онлайн') # Отправка сообщения о статусе сервера

        time.sleep(2)
def trace_route(chat_id, ip_address):
    global is_running

    if is_running:
        bot.send_message(chat_id, "Трассировка уже запущена. Пожалуйста, дождитесь ее завершения.")
        return

    is_running = True  # Устанавливаем флаг, что трассировка запущена

    try:
        if config.operating_system == 'Windows':
            result = subprocess.run(['tracert', ip_address], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, encoding='cp866')
        elif config.operating_system == 'Linux':
            result = subprocess.run(['traceroute', ip_address], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

        trace_result = result.stdout
        bot.send_message(chat_id, f'Результат трассировки маршрута для {ip_address}:\n{trace_result}')  # Отправка результатов трассировки
    except Exception as e:
        bot.send_message(chat_id, f'An error occurred during traceroute: {e}')
    finally:
        is_running = False  # Устанавливаем флаг, что трассировка завершена

    time.sleep(1)  # Небольшая задержка перед возможным повторным запуском


@bot.message_handler(commands=['ping']) # Обработчик команды /ping для запуска проверки пинга
def start_ping(message):
    global is_running # Объявление глобальной переменной
    if not is_running:
        try:
            ip_address = message.text.split()[1]  # Получение IP-адреса из сообщения
            # ip_address = '192.168.0.9'
            threading.Thread(target=check_ping, args=(message.chat.id, ip_address)).start()  # Запуск проверки пинга в отдельном потоке
            bot.send_message(message.chat.id, f"Начата проверка пинга для {ip_address}")  # Отправка сообщения о начале проверки
        except IndexError:
            bot.send_message(message.chat.id, "Не указан IP-адрес для проверки")   # Отправка сообщения об ошибке
    else:
        bot.send_message(message.chat.id, "Проверка пинга уже запущена") # Отправка сообщения о том, что проверка уже запущена

@bot.message_handler(commands=['trace'])
def start_trace(message):
    global is_running
    if not is_running:
        try:
            ip_address = message.text.split()[1]
            threading.Thread(target=trace_route, args=(message.chat.id, ip_address)).start()
            bot.send_message(message.chat.id, f"Начата трассировка маршрута для {ip_address}, Ожидайте")
        except IndexError:
            bot.send_message(message.chat.id, "Не указан IP-адрес для трассировки")
    else:
        bot.send_message(message.chat.id, "Трассировка маршрута уже запущена")

@bot.message_handler(commands=['stop_ping']) # Обработчик команды /stop для остановки проверки пинга
def stop_ping(message):
    global is_running
    is_running = False  # Остановка проверки пинга
    bot.send_message(message.chat.id, "Остановка проверки пинга")

@bot.message_handler(commands=['stop_trace'])
def stop_trace(message):
    global is_running
    is_running = False
    bot.send_message(message.chat.id, "Остановка трассировки маршрута")

bot.polling() # Запуск постоянного опроса
