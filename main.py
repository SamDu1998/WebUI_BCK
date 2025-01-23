# -*- coding: utf-8 -*-
"""
定时下载远程数据库文件并保留最近7天备份
"""

# 导入需要的模块
import requests
import os
import datetime
import time
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import threading

# 定义远程文件URL
REMOTE_FILE_URL = "https://backup.dunetpanel.cyou/webui.db"

# 定义本地保存备份的目录
BACKUP_DIR = "C:\\Users\\djc19\\OneDrive\\Sync\\WEBUI_DB"

# 定义下载间隔，单位为秒 (4小时 = 4 * 60 * 60 秒)
DOWNLOAD_INTERVAL = 4 * 60 * 60

# 定义备份保留天数
KEEP_DAYS = 7

# 函数：下载文件
def download_file():
   try:
       response = requests.get(REMOTE_FILE_URL, stream=True)
       response.raise_for_status()  # 检查请求是否成功

       # 创建备份目录，如果不存在
       if not os.path.exists(BACKUP_DIR):
           os.makedirs(BACKUP_DIR)

       # 获取当前日期和时间
       now = datetime.datetime.now()
       timestamp = now.strftime("%Y%m%d_%H%M%S")

       # 构建新文件名
       local_filename = f"webui_bk_{timestamp}.db"
       local_filepath = os.path.join(BACKUP_DIR, local_filename)

       # 下载文件
       with open(local_filepath, 'wb') as f:
           for chunk in response.iter_content(chunk_size=8192):
               f.write(chunk)

       print(f"文件已下载：{local_filepath}")
       return True, f"文件已下载：{local_filepath}"

   except requests.exceptions.RequestException as e:
       print(f"下载失败：{e}")
       return False, f"下载失败：{e}"






# 函数：删除旧文件
def delete_old_files():
   cutoff_date = datetime.datetime.now() - datetime.timedelta(days=KEEP_DAYS)

   deleted_files = []

   if os.path.exists(BACKUP_DIR):
        for filename in os.listdir(BACKUP_DIR):
            if filename.startswith("webui_bk_") and filename.endswith(".db"):
                file_path = os.path.join(BACKUP_DIR, filename)
                try:
                    file_date_str = filename[9:17] # 提取日期部分  webui_bk_20240126_183010
                    file_time_str = filename[18:24] # 提取时间部分
                    file_datetime_str = f"{file_date_str}{file_time_str}"
                    file_datetime = datetime.datetime.strptime(file_datetime_str,"%Y%m%d%H%M%S")

                    if file_datetime < cutoff_date:
                        os.remove(file_path)
                        deleted_files.append(filename)
                except (ValueError, OSError) as e:
                    print(f"删除文件出错: {filename}, 错误信息：{e}")

   if deleted_files:
       print(f"删除旧文件：{', '.join(deleted_files)}")
       return True, f"删除旧文件：{', '.join(deleted_files)}"
   else:
       print("没有旧文件被删除")
       return False, "没有旧文件被删除"



# 函数：主循环，定时下载文件和清理旧文件
def main_loop():
   while True:
       # 下载文件
       status, message = download_file()
       log_text.insert(tk.END, f"{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - 下载状态：{status}, 信息：{message}\n")
       log_text.see(tk.END)  # 滚动到文本框底部

       # 清理旧文件
       status, message = delete_old_files()
       log_text.insert(tk.END, f"{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - 清理旧文件状态：{status}, 信息：{message}\n")
       log_text.see(tk.END)

       time.sleep(DOWNLOAD_INTERVAL)

#  函数：启动下载和清理线程
def start_download():
   download_button.config(state=tk.DISABLED)  # 禁用启动按钮
   stop_button.config(state=tk.NORMAL) # 启动停止按钮
   global stop_threads
   stop_threads = False
   download_thread = threading.Thread(target=main_loop,daemon=True)
   download_thread.start()

#  函数：停止下载和清理线程
def stop_download():
   global stop_threads
   stop_threads = True
   download_button.config(state=tk.NORMAL)  # 启用启动按钮
   stop_button.config(state=tk.DISABLED) # 停止停止按钮



#  函数：启动GUI
def start_gui():
   global log_text,download_button,stop_button
   window = tk.Tk()
   window.title("OpenWEBUI DataBase Backup")
   window.geometry("600x400")  # 设置窗口大小


   # 创建启动和停止按钮
   button_frame = ttk.Frame(window)
   button_frame.pack(pady=10)

   download_button = ttk.Button(button_frame, text="启动下载", command=start_download)
   download_button.pack(side=tk.LEFT, padx=10)

   stop_button = ttk.Button(button_frame, text="停止下载", command=stop_download,state=tk.DISABLED)
   stop_button.pack(side=tk.LEFT, padx=10)

   # 创建日志文本框
   log_text = tk.Text(window, height=15)  # 设置高度为15行
   log_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)



   window.mainloop()


if __name__ == "__main__":
   start_gui()