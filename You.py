
# Arquivo: You.py
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import subprocess
import logging
import re
import shutil
import threading
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import shlex
import time
import ttkbootstrap as ttk
from plyer import notification

SIGNATURE = "DevFerreiraG"
LOG_FILE = "yt_downloader.log"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler(LOG_FILE, encoding="utf-8"), logging.StreamHandler(sys.stdout)]
)

YOUTUBE_URL_REGEX = re.compile(
    r'^(https?://)?((www|m)\.)?((youtube\.com/watch\?v=)|(youtu\.be/))([a-zA-Z0-9_-]{11})'
)

def install_dependencies():
    required_packages = ["yt-dlp", "ttkbootstrap", "plyer"]
    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            subprocess.run([sys.executable, "-m", "pip", "install", "--upgrade", package], check=True)

def install_ffmpeg():
    try:
        subprocess.run(["ffmpeg", "-version"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
    except FileNotFoundError:
        messagebox.showinfo("Instalando FFmpeg", "FFmpeg não encontrado. Instalando automaticamente...")
        subprocess.run([sys.executable, "-m", "pip", "install", "imageio[ffmpeg]"], check=True)

def get_yt_dlp_path():
    paths = [shutil.which("yt-dlp"),
             os.path.expanduser("~") + r"\AppData\Roaming\Python\Python313t\Scripts\yt-dlp.exe",
             os.path.expanduser("~") + r"\AppData\Roaming\Python\Python313\Scripts\yt-dlp.exe",
             os.path.expanduser("~") + r"\AppData\Local\Programs\Python\Python313\Scripts\yt-dlp.exe"]
    return next((path for path in paths if path and os.path.exists(path)), None)

def check_yt_dlp():
    yt_dlp_path = get_yt_dlp_path()
    if not yt_dlp_path:
        subprocess.run([sys.executable, "-m", "pip", "install", "--upgrade", "yt-dlp"], check=True)
        yt_dlp_path = get_yt_dlp_path()
    if not yt_dlp_path:
        messagebox.showerror("Erro", "yt-dlp não pôde ser instalado.")
        sys.exit(1)
    return yt_dlp_path

def fix_scripts_paths():
    scripts_dir = os.path.expanduser("~") + r"\AppData\Roaming\Python\Python313t\Scripts"
    if scripts_dir not in os.environ["PATH"]:
        os.environ["PATH"] += os.pathsep + scripts_dir
        messagebox.showinfo("Atualizando PATH", f"Adicionando {scripts_dir} ao PATH. Reinicie a aplicação para aplicar as mudanças.")

install_dependencies()
install_ffmpeg()
fix_scripts_paths()  # Corrige o PATH dos scripts
YT_DLP_PATH = check_yt_dlp()


class YouTubeDownloaderApp:
    def __init__(self, root: ttk.Window):
        self.root = root
        self.root.title("YouTube Downloader Pro")
        self.root.geometry("750x700")
        self.root.resizable(False, False)
        self.root.configure(background="#121212")

        self.default_output_directory = os.path.join(os.path.expanduser("~"), "Downloads", "YouTube")
        os.makedirs(self.default_output_directory, exist_ok=True)
        self.output_directory = self.default_output_directory

        self.download_active = False
        self.download_cancelled = False
        self.animation_index = 0
        self.animation_states = ["Baixando.", "Baixando..", "Baixando..."]
        self.current_process = None

        self.create_widgets()
        self.setup_bindings()

        logging.info("Aplicativo premium inicializado com sucesso! Pronto para revolucionar downloads.")

    def create_widgets(self):
        main_frame = ttk.Frame(self.root, padding=20, bootstyle="dark")
        main_frame.pack(fill="both", expand=True)

        ttk.Label(main_frame, text="YouTube Downloader Pro", font=("Arial", 20, "bold"), bootstyle="primary").pack(pady=10)

        self.url_entry = self.create_labeled_entry(main_frame, "URL do Vídeo:", 60)
        self.create_directory_controls(main_frame)
        self.create_download_options(main_frame)

        # Botões de controle do download
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(pady=15)
        self.download_button = ttk.Button(button_frame, text="INICIAR DOWNLOAD", bootstyle="success", command=self.start_download)
        self.download_button.pack(side="left", padx=5)
        self.cancel_button = ttk.Button(button_frame, text="CANCELAR DOWNLOAD", bootstyle="danger", command=self.cancel_download, state="disabled")
        self.cancel_button.pack(side="left", padx=5)

        self.progress_bar = ttk.Progressbar(main_frame, mode="determinate", maximum=100)
        self.progress_bar.pack(fill="x", padx=5, pady=10)
        self.progress_label = ttk.Label(main_frame, text="0%", font=("Arial", 12), bootstyle="info")
        self.progress_label.pack(pady=5)

        self.status_label = ttk.Label(main_frame, text="Pronto para baixar!", font=("Arial", 12), bootstyle="warning")
        self.status_label.pack(pady=10)

        ttk.Label(main_frame, text=f"Powered by {SIGNATURE}", font=("Arial", 10), bootstyle="secondary").pack(side="bottom", pady=5)

    def create_download_options(self, parent):
        option_frame = ttk.Frame(parent)
        option_frame.pack(fill="x", pady=10)
        ttk.Label(option_frame, text="Formato:", bootstyle="info").pack(side="left", padx=5)
        self.format_option = ttk.Combobox(option_frame, values=["Vídeo (somente vídeo)", "Áudio (apenas áudio)", "Vídeo e Áudio"], state="readonly")
        self.format_option.current(0)
        self.format_option.pack(side="left", padx=5)

    def setup_bindings(self):
        self.root.bind("<Return>", lambda event: self.start_download())

    def create_labeled_entry(self, parent, label_text, width):
        frame = ttk.Frame(parent)
        frame.pack(fill="x", pady=10)
        ttk.Label(frame, text=label_text, bootstyle="info").pack(side="left", padx=5)
        entry = ttk.Entry(frame, width=width, bootstyle="dark")
        entry.pack(side="left", padx=5, fill="x", expand=True)
        return entry

    def create_directory_controls(self, parent):
        frame = ttk.Frame(parent)
        frame.pack(fill="x", pady=10)
        ttk.Button(frame, text="Selecionar Pasta", bootstyle="secondary", command=self.select_folder).pack(side="left", padx=5, pady=5)
        ttk.Button(frame, text="Abrir Pasta", bootstyle="info", command=self.open_folder).pack(side="left", padx=5, pady=5)

    def select_folder(self):
        folder = filedialog.askdirectory(initialdir=self.default_output_directory, title="Selecione a Pasta de Download")
        if folder:
            self.output_directory = folder

    def open_folder(self):
        os.startfile(self.output_directory)

    def start_download(self):
        url = self.url_entry.get().strip()
        if not YOUTUBE_URL_REGEX.fullmatch(url):
            messagebox.showerror("Erro", "URL inválida!")
            return

        self.download_button.config(state="disabled")
        self.cancel_button.config(state="enabled")
        self.progress_bar["value"] = 0
        self.progress_label.config(text="0%")
        self.update_status("Iniciando download...", "info")
        self.download_active = True
        self.download_cancelled = False
        self.animate_status()

        threading.Thread(target=self.download_video, args=(url,), daemon=True).start()

    def cancel_download(self):
        if self.current_process and self.current_process.poll() is None:
            self.current_process.terminate()
            self.download_cancelled = True
            self.update_status("Download cancelado!", "warning")
            logging.info("Download cancelado pelo usuário.")
        self.download_active = False
        self.download_button.config(state="normal")
        self.cancel_button.config(state="disabled")

    def animate_status(self):
        if self.download_active:
            self.status_label.config(text=self.animation_states[self.animation_index])
            self.animation_index = (self.animation_index + 1) % len(self.animation_states)
            self.root.after(500, self.animate_status)

    def update_progress(self, percentage):
        self.progress_bar["value"] = percentage
        self.progress_label.config(text=f"{int(percentage)}%")

    def update_status(self, text, color):
        self.status_label.config(text=text, bootstyle=color)

    def download_complete(self):
        messagebox.showinfo("Sucesso", "Download concluído!")
        notification.notify(
            title="Download Concluído",
            message="O vídeo foi baixado com sucesso!",
            app_name="YouTube Downloader Pro",
            timeout=5
        )
        logging.info("Download concluído com sucesso.")

    def download_video(self, url):
        try:
            format_selected = self.format_option.get()
            if "Áudio" in format_selected and "Vídeo" not in format_selected:
                # Baixar somente áudio
                command = [
                    YT_DLP_PATH,
                    "-f", "bestaudio",
                    "--extract-audio",
                    "--audio-format", "mp3",
                    "-o", os.path.join(self.output_directory, "%(title)s.%(ext)s"),
                    url
                ]
            elif "Vídeo e Áudio" in format_selected:
                # Baixar vídeo com áudio (melhor combinação)
                command = [
                    YT_DLP_PATH,
                    "-f", "best",
                    "-o", os.path.join(self.output_directory, "%(title)s.%(ext)s"),
                    url
                ]
            else:
                # Baixar somente vídeo
                command = [
                    YT_DLP_PATH,
                    "-f", "bestvideo",
                    "-o", os.path.join(self.output_directory, "%(title)s.%(ext)s"),
                    url
                ]

            self.current_process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            for line in iter(self.current_process.stdout.readline, ""):
                match = re.search(r"(\d{1,3})%", line)
                if match:
                    self.root.after(0, self.update_progress, int(match.group(1)))
            self.current_process.wait()

            if not self.download_cancelled:
                self.root.after(0, self.download_complete)
                self.update_status("Download concluído!", "success")
            else:
                self.update_status("Download cancelado!", "warning")

        except Exception as e:
            messagebox.showerror("Erro", str(e))
            logging.error("Erro no download: %s", e)

        self.download_active = False
        self.download_button.config(state="normal")
        self.cancel_button.config(state="disabled")


if __name__ == '__main__':
    root = ttk.Window(themename="cyborg")
    app = YouTubeDownloaderApp(root)
    root.mainloop()
