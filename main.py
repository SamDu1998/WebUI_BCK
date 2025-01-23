# -*- coding: utf-8 -*-
"""
定时下载远程数据库文件并保留最近7天备份，支持自定义URL和本地保存目录
"""

# 导入需要的模块
import requests
import os
import datetime
import time
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from tkinter import filedialog
import threading
import sys

# 定义下载间隔，单位为秒 (4小时 = 4 * 60 * 60 秒)
DOWNLOAD_INTERVAL = 4 * 60 * 60

# 定义备份保留天数
KEEP_DAYS = 7

# 用于存储用户输入的URL
remote_file_url = None

# 用于存储用户选择的本地保存目录
backup_dir = None

# 用于控制下载循环
stop_threads = False

# 函数：下载文件
def download_file(url, backup_dir):
    try:
        response = requests.get(url, stream=True)
        response.raise_for_status()  # 检查请求是否成功

        # 创建备份目录，如果不存在
        if not os.path.exists(backup_dir):
            os.makedirs(backup_dir)

        # 获取当前日期和时间
        now = datetime.datetime.now()
        timestamp = now.strftime("%Y%m%d_%H%M%S")

        # 构建新文件名
        local_filename = f"webui_bk_{timestamp}.db"
        local_filepath = os.path.join(backup_dir, local_filename)

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
def delete_old_files(backup_dir):
    cutoff_date = datetime.datetime.now() - datetime.timedelta(days=KEEP_DAYS)

    deleted_files = []

    if os.path.exists(backup_dir):
         for filename in os.listdir(backup_dir):
             if filename.startswith("webui_bk_") and filename.endswith(".db"):
                 file_path = os.path.join(backup_dir, filename)
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
    global remote_file_url, backup_dir, stop_threads

    while not stop_threads:
         # 确保URL和保存目录都已设置
        if not remote_file_url:
            log_text.insert(tk.END, f"{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - 请先输入远程文件地址\n")
            log_text.see(tk.END)
            time.sleep(10)
            continue
        if not backup_dir:
            log_text.insert(tk.END, f"{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - 请先选择本地保存目录\n")
            log_text.see(tk.END)
            time.sleep(10)
            continue

        # 下载文件
        status, message = download_file(remote_file_url,backup_dir)
        log_text.insert(tk.END, f"{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - 下载状态：{status}, 信息：{message}\n")
        log_text.see(tk.END)  # 滚动到文本框底部

        # 清理旧文件
        status, message = delete_old_files(backup_dir)
        log_text.insert(tk.END, f"{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - 清理旧文件状态：{status}, 信息：{message}\n")
        log_text.see(tk.END)

        time.sleep(DOWNLOAD_INTERVAL)

    # 当线程退出时，打印停止消息
    log_text.insert(tk.END, f"{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - 已停止\n")
    log_text.see(tk.END)



# 函数：启动下载和清理线程
def start_download():
    global remote_file_url, backup_dir
    global stop_threads

    if not remote_file_url:
        messagebox.showerror("错误", "请先输入远程文件地址!")
        return
    if not backup_dir:
        messagebox.showerror("错误", "请先选择本地保存目录!")
        return

    download_button.config(state=tk.DISABLED)  # 禁用启动按钮
    stop_button.config(state=tk.NORMAL)  # 启动停止按钮
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


# 函数：打开文件夹选择窗口
def choose_directory():
    global backup_dir, backup_dir_label
    directory = filedialog.askdirectory()
    if directory:
        backup_dir = directory
        backup_dir_label.config(text=backup_dir) # 更新标签文本
        messagebox.showinfo("提示", f"已选择保存目录: {backup_dir}")


# 函数：启动GUI
def start_gui():
    global log_text, download_button, stop_button, url_entry
    global backup_dir_label, window
    window = tk.Tk()
    window.title("远程文件定时下载器")
    window.geometry("600x500")  # 设置窗口大小
    window.protocol("WM_DELETE_WINDOW", on_closing) # 监听窗口关闭事件

    # 创建URL输入框和标签
    url_frame = ttk.Frame(window)
    url_frame.pack(pady=10)

    url_label = ttk.Label(url_frame, text="远程文件地址:")
    url_label.pack(side=tk.LEFT, padx=5)

    url_entry = ttk.Entry(url_frame, width=50)
    url_entry.pack(side=tk.LEFT, padx=5)

    save_url_button = ttk.Button(url_frame, text="保存地址", command=save_url)
    save_url_button.pack(side=tk.LEFT, padx=5)

    # 创建选择保存目录的按钮和标签
    dir_frame = ttk.Frame(window)
    dir_frame.pack(pady=10)

    dir_button = ttk.Button(dir_frame, text="选择保存目录", command=choose_directory)
    dir_button.pack(side=tk.LEFT, padx=5)

    backup_dir_label = ttk.Label(dir_frame, text="未选择目录")
    backup_dir_label.pack(side=tk.LEFT, padx=5)


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


# 函数：监听窗口关闭事件
def on_closing():
    global stop_threads
    stop_threads = True  # 设置停止标志
    window.after(100, window.destroy) #  使用window.after,在主线程中执行关闭窗口操作


if __name__ == "__main__":
    start_gui()