import tkinter as tk
from tkinter import ttk, messagebox
import threading
import time
import sys
import os

class LockScreenAlarm:
    def __init__(self, root):
        self.root = root
        self.root.title("定时活动锁屏闹铃")
        self.root.geometry("400x300")
        self.root.resizable(False, False)
        
        # 设置图标（如果有的话）
        try:
            self.root.iconbitmap("alarm_icon.ico")
        except:
            pass
        
        # 变量初始化
        self.is_timing = False
        self.is_locked = False
        self.timer_thread = None
        self.lock_thread = None
        self.stop_event = threading.Event()
        
        self.setup_ui()
        
    def setup_ui(self):
        # 主标题
        title_label = tk.Label(self.root, text="定时活动锁屏闹铃", 
                              font=("Arial", 16, "bold"))
        title_label.pack(pady=10)
        
        # 定时设置框架
        timer_frame = ttk.LabelFrame(self.root, text="定时设置", padding=10)
        timer_frame.pack(pady=10, padx=20, fill="x")
        
        # 时间输入
        time_label = tk.Label(timer_frame, text="定时时间（分钟）:")
        time_label.grid(row=0, column=0, sticky="w", padx=5, pady=5)
        
        self.time_entry = ttk.Entry(timer_frame, width=10)
        self.time_entry.grid(row=0, column=1, padx=5, pady=5)
        self.time_entry.insert(0, "30")
        
        # 状态显示
        self.status_label = tk.Label(timer_frame, text="状态: 未启动", 
                                   fg="red", font=("Arial", 10))
        self.status_label.grid(row=1, column=0, columnspan=2, pady=5, sticky="w")
        
        self.time_remaining_label = tk.Label(timer_frame, text="剩余时间: --", 
                                           font=("Arial", 10))
        self.time_remaining_label.grid(row=2, column=0, columnspan=2, pady=2, sticky="w")
        
        # 按钮框架
        button_frame = ttk.Frame(self.root)
        button_frame.pack(pady=20)
        
        self.start_button = ttk.Button(button_frame, text="开始定时", 
                                      command=self.start_timer)
        self.start_button.pack(side="left", padx=10)
        
        self.stop_button = ttk.Button(button_frame, text="停止定时", 
                                     command=self.stop_timer, state="disabled")
        self.stop_button.pack(side="left", padx=10)
        
        # 说明文本
        info_text = """使用说明:
1. 输入定时时间（分钟）
2. 点击"开始定时"
3. 时间到达后会自动锁屏5分钟
4. 锁屏期间可点击解锁按钮提前解除
5. 锁屏解除后会自动重新开始定时
6. 点击"停止定时"可彻底关闭功能"""
        
        info_label = tk.Label(self.root, text=info_text, justify="left",
                            font=("Arial", 9), fg="gray")
        info_label.pack(pady=10)
        
    def start_timer(self):
        try:
            minutes = int(self.time_entry.get())
            if minutes <= 0:
                messagebox.showerror("错误", "请输入有效的正数分钟")
                return
        except ValueError:
            messagebox.showerror("错误", "请输入有效的数字")
            return
            
        self.is_timing = True
        self.stop_event.clear()
        
        # 更新UI状态
        self.start_button.config(state="disabled")
        self.stop_button.config(state="normal")
        self.status_label.config(text="状态: 定时中", fg="green")
        
        # 启动定时线程
        self.timer_thread = threading.Thread(target=self.timer_countdown, args=(minutes,))
        self.timer_thread.daemon = True
        self.timer_thread.start()
        
    def stop_timer(self):
        self.is_timing = False
        self.stop_event.set()
        
        # 更新UI状态
        self.start_button.config(state="normal")
        self.stop_button.config(state="disabled")
        self.status_label.config(text="状态: 未启动", fg="red")
        self.time_remaining_label.config(text="剩余时间: --")
        
        # 如果正在锁屏，关闭锁屏窗口
        if self.is_locked and hasattr(self, 'lock_window'):
            try:
                self.lock_window.destroy()
            except:
                pass
            self.is_locked = False
    
    def timer_countdown(self, minutes):
        total_seconds = minutes * 60
        
        for remaining in range(total_seconds, 0, -1):
            if self.stop_event.is_set():
                return
                
            # 更新剩余时间显示
            mins = remaining // 60
            secs = remaining % 60
            self.root.after(0, self.update_time_display, mins, secs)
            
            time.sleep(1)
        
        # 时间到达，启动锁屏
        if self.is_timing and not self.stop_event.is_set():
            self.root.after(0, self.show_lock_screen)
    
    def update_time_display(self, minutes, seconds):
        self.time_remaining_label.config(text=f"剩余时间: {minutes:02d}:{seconds:02d}")
    
    def show_lock_screen(self):
        self.is_locked = True
        
        # 创建全屏锁屏窗口
        self.lock_window = tk.Toplevel(self.root)
        self.lock_window.title("活动提醒")
        self.lock_window.attributes('-fullscreen', True)
        self.lock_window.attributes('-topmost', True)
        self.lock_window.configure(bg='black')
        
        # 锁屏内容
        lock_frame = tk.Frame(self.lock_window, bg='black')
        lock_frame.place(relx=0.5, rely=0.5, anchor='center')
        
        message_label = tk.Label(lock_frame, text="活动时间到！请休息5分钟", 
                               font=("Arial", 24), fg="white", bg="black")
        message_label.pack(pady=20)
        
        countdown_label = tk.Label(lock_frame, text="5:00", 
                                 font=("Arial", 48, "bold"), fg="yellow", bg="black")
        countdown_label.pack(pady=10)
        
        unlock_button = ttk.Button(lock_frame, text="解锁", 
                                 command=self.unlock_screen)
        unlock_button.pack(pady=20)
        
        # 启动锁屏倒计时
        self.lock_thread = threading.Thread(target=self.lock_countdown, 
                                          args=(countdown_label,))
        self.lock_thread.daemon = True
        self.lock_thread.start()
    
    def lock_countdown(self, countdown_label):
        total_seconds = 5 * 60  # 5分钟
        
        for remaining in range(total_seconds, 0, -1):
            if not self.is_locked or self.stop_event.is_set():
                return
                
            mins = remaining // 60
            secs = remaining % 60
            self.root.after(0, lambda: countdown_label.config(text=f"{mins}:{secs:02d}"))
            time.sleep(1)
        
        # 锁屏时间结束，自动解锁
        if self.is_locked:
            self.root.after(0, self.unlock_screen)
    
    def unlock_screen(self):
        self.is_locked = False
        
        # 关闭锁屏窗口
        if hasattr(self, 'lock_window'):
            try:
                self.lock_window.destroy()
            except:
                pass
        
        # 如果定时功能还在运行，重新开始定时
        if self.is_timing and not self.stop_event.is_set():
            self.root.after(0, self.restart_timer)
    
    def restart_timer(self):
        # 重新开始定时
        try:
            minutes = int(self.time_entry.get())
            self.timer_thread = threading.Thread(target=self.timer_countdown, args=(minutes,))
            self.timer_thread.daemon = True
            self.timer_thread.start()
        except:
            self.stop_timer()

def main():
    root = tk.Tk()
    app = LockScreenAlarm(root)
    root.mainloop()

if __name__ == "__main__":
    main()
