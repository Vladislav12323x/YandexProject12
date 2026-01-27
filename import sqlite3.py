import tkinter as tk
from tkinter import messagebox
import pyautogui
import threading
import time

def run_macro():
    time.sleep(0.9)
    for i in range(500):
        pyautogui.press('space')
    


def start_macro_thread():
    thread = threading.Thread(target=run_macro)
    thread.daemon = True
    thread.start()

root = tk.Tk()
root.title("Макрос")
root.geometry("200x80")
root.resizable(False, False)

root.eval('tk::PlaceWindow . center')

# Кнопка запуска
btn = tk.Button(root, text="Запустить макрос", command=start_macro_thread, font=("Arial", 10))
btn.pack(expand=True)

# Запуск GUI
root.mainloop()