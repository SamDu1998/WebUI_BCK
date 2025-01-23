# -*- coding: utf-8 -*-
"""
定时下载远程数据库文件并保留最近7天备份，支持自定义URL
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

# 定义本地保存备份的目录
BACKUP_DIR = "C:\\Users\\djc19\\OneDrive\\Sync\\WEBUI_DB"

# 定义下载间隔，单位为秒 (4小时 = 4 * 60 * 60 秒)
DOWNLOAD_INTERVAL = 4 * 60 * 60

# 定义备份保留天数
KEEP_DAYS = 7

# 用于存储用户输入的URL
remote_file_url = None

# 函数：下载文件
def download_file(url):
   try:
       response = requests.get(url, stream=True)
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
       error_message = f"下载失败：{e}"
       print(error_message)
       return False, error_message
   except Exception as e:
       error_message = f"下载过程中发生未知错误：{e}"
       print(error_message)
       return False, error_message


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
                    error_message = f"删除文件出错: {filename}, 错误信息：{e}"
                    print(error_message)
                    log_text.insert(tk.END, f"{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - 删除旧文件出错：{error_message}\n")
                    log_text.see(tk.END)

   if deleted_files:
       print(f"删除旧文件：{', '.join(deleted_files)}")
       return True, f"删除旧文件：{', '.join(deleted_files)}"
   else:
       print("没有旧文件被删除")
       return False, "没有旧文件被删除"



# 函数：主循环，定时下载文件和清理旧文件
def main_loop():
   global remote_file_url

   while True:
       # 确保URL已经设置
       if not remote_file_url:
           log_text.insert(tk.END, f"{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - 请先输入远程文件地址\n")
           log_text.see(tk.END)
           time.sleep(10)  # 等待10秒再检查
           continue  # 跳过本次循环，等待URL设置

       # 下载文件
       status, message = download_file(remote_file_url)
       log_text.insert(tk.END, f"{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - 下载状态：{status}, 信息：{message}\n")
       log_text.see(tk.END)  # 滚动到文本框底部

       # 清理旧文件
       status, message = delete_old_files()
       log_text.insert(tk.END, f"{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - 清理旧文件状态：{status}, 信息：{message}\n")
       log_text.see(tk.END)

       time.sleep(DOWNLOAD_INTERVAL)



# 函数：启动下载和清理线程
def start_download():
   global remote_file_url
   if not remote_file_url:
       messagebox.showerror("错误", "请先输入远程文件地址!")
       return

   download_button.config(state=tk.DISABLED)  # 禁用启动按钮
   stop_button.config(state=tk.NORMAL)  # 启动停止按钮
   global stop_threads
   stop_threads = False
   download_thread = threading.Thread(target=main_loop, daemon=True)
   download_thread.start()


#  函数：停止下载和清理线程
def stop_download():
   global stop_threads
   stop_threads = True
   download_button.config(state=tk.NORMAL)  # 启用启动按钮
   stop_button.config(state=tk.DISABLED)  # 停止停止按钮


# 函数：保存用户输入的url
def save_url():
   global remote_file_url
   url = url_entry.get().strip()
   if not url.startswith("http"):
       messagebox.showerror("错误", "请输入正确的URL，以http开头")
       return
   remote_file_url = url
   messagebox.showinfo("提示", "远程文件地址已保存！")


# 函数：启动GUI
def start_gui():
   global log_text, download_button, stop_button, url_entry
   window = tk.Tk()
   window.title("远程文件定时下载器")
   window.geometry("600x450")  # 设置窗口大小

   # 创建URL输入框和标签
   url_frame = ttk.Frame(window)
   url_frame.pack(pady=10)

   url_label = ttk.Label(url_frame, text="远程文件地址:")
   url_label.pack(side=tk.LEFT, padx=5)

   url_entry = ttk.Entry(url_frame, width=50)
   url_entry.pack(side=tk.LEFT, padx=5)

   save_url_button = ttk.Button(url_frame, text="保存地址", command=save_url)
   save_url_button.pack(side=tk.LEFT, padx=5)

   # 创建启动和停止按钮
   button_frame = ttk.Frame(window)
   button_frame.pack(pady=10)

   download_button = ttk.Button(button_frame, text="启动下载", command=start_download)
   download_button.pack(side=tk.LEFT, padx=10)

   stop_button = ttk.Button(button_frame, text="停止下载", command=stop_download, state=tk.DISABLED)
   stop_button.pack(side=tk.LEFT, padx=10)

   # 创建日志文本框
   log_text = tk.Text(window, height=15)  # 设置高度为15行
   log_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

   window.mainloop()


if __name__ == "__main__":
   start_gui()