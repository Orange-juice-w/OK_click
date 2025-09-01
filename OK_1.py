import threading
import tkinter as tk
from tkinter.scrolledtext import ScrolledText
import pyautogui
import pytesseract
import cv2
import numpy as np
from PIL import Image
import time

# 配置Tesseract路径 (Windows下安装Tesseract后需要改成实际路径)
pytesseract.pytesseract.tesseract_cmd = r"D:\Program Files\Tesseract-OCR\tesseract.exe"

running = True  # 控制循环标志

def log(message):
    def append_log():
        """在GUI窗口输出日志"""
        text_area.configure(state='normal')
        text_area.insert(tk.END, f"{time.strftime('%H:%M:%S')} - {message}\n")
        text_area.see(tk.END)
        text_area.configure(state='disabled')
        
    # 如果在主线程，直接执行；否则交给主线程
    text_area.after(0, append_log)

def find_and_click_ok():
    try:
    
        # 获取屏幕分辨率
        screen_width, screen_height = pyautogui.size()
    
        # 取屏幕中间区域 (宽高的中间 1/3 区域)
        left = screen_width // 3
        top = screen_height // 3
        width = screen_width // 3
        height = screen_height // 3
    
        # 截图
        screenshot = pyautogui.screenshot(region=(left, top, width, height))
        img = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
        
        # OCR识别
        text = pytesseract.image_to_string(Image.fromarray(img))
    
        # 检查是否有 "OK"
        if "OK" in text:
            # 查找OK的大致位置
            data = pytesseract.image_to_data(Image.fromarray(img), output_type=pytesseract.Output.DICT)
            for i, word in enumerate(data['text']):
                if word.strip().upper() == "OK":
                   # 文字框中心坐标（相对于整个屏幕）
                   x = left + data['left'][i] + data['width'][i] // 2
                   y = top + data['top'][i] + data['height'][i] // 2
                   pyautogui.click(x, y)
                   log(f"检测到 OK，已点击！位置: ({x},{y})")
                   return True
        return False
    except Exception as e:
        log(f"错误: {e}")
        return False

def worker():
    while running:
        found = find_and_click_ok()
        if not found:
            log("未检测到 OK，继续监控...")
        time.sleep(1)  # 每秒检测一次

def on_exit():
    global running
    running = False
    root.quit()

def on_esc(event):
    on_exit()

# 创建 GUI 窗口
root = tk.Tk()
root.title("OK Clicker Monitor")

# 日志显示区域
text_area = ScrolledText(root, width=60, height=20, state='disabled')
text_area.pack(padx=10, pady=10)

# 停止按钮
btn = tk.Button(root, text="停止程序", command=on_exit, bg="red", fg="white", width=20, height=2)
btn.pack(pady=10)

# 启动后台线程
threading.Thread(target=worker, daemon=True).start()

# 启动 GUI
log("程序启动，开始监控屏幕...")
root.mainloop()


