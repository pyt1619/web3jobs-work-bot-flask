import subprocess
import os
import time

# Пути к скриптам
scripts = [
    "bot.py",
    "app.py",
    "parser.py"
]

# Директория, в которой находятся скрипты
script_directory = "/root/parser_bot_vakansy2"

# Лог-файлы для каждого скрипта
log_files = {script: os.path.join(script_directory, f"{script}.log") for script in scripts}

# Функция для запуска скрипта
def run_script(script):
    log_file = log_files[script]
    with open(log_file, 'a') as lf:
        process = subprocess.Popen(['python3', script], cwd=script_directory, stdout=lf, stderr=lf)
    return process

# Основной цикл для запуска и мониторинга скриптов
processes = {script: run_script(script) for script in scripts}

try:
    while True:
        for script, process in processes.items():
            if process.poll() is not None:  # Если процесс завершился
                print(f"{script} завершился. Перезапуск...")
                processes[script] = run_script(script)
        time.sleep(10)  # Проверка каждые 10 секунд
except KeyboardInterrupt:
    print("Остановка всех скриптов...")
    for process in processes.values():
        process.terminate()
 
