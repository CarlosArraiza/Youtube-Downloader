import customtkinter as ctk
from tkinter import filedialog, messagebox
import threading
import os
import sys
import subprocess
import requests
from io import BytesIO
from PIL import Image

sys.path.insert(0, os.path.dirname(__file__))
from downloader import get_video_info, download_video, AUDIO_FORMATS, VIDEO_FORMATS, AUDIO_QUALITIES
from config import load_config, save_config, VIDEO_QUALITY_OPTIONS

THUMB_W, THUMB_H           = 160, 90
HIST_THUMB_W, HIST_THUMB_H = 96, 54

ALL_VIDEO_FORMATS = ["mp4", "mkv", "avi", "webm", "mov"]
ALL_AUDIO_FORMATS = ["mp3", "aac", "flac", "ogg", "wav", "m4a"]
ALL_FORMATS_COMBO = ["── Vídeo ──"] + ALL_VIDEO_FORMATS + ["── Audio ──"] + ALL_AUDIO_FORMATS

THEME_OPTIONS = ["dark", "light", "system"]
THEME_LABELS  = {"dark": "Oscuro", "light": "Claro", "system": "Sistema"}
THEME_REVERSE = {v: k for k, v in THEME_LABELS.items()}

YT_RED              = "#FF0000"
YT_RED_HOVER        = "#CC0000"
CTK_BLUE            = "#3B8ED0"
CTK_BLUE_HOVER      = "#36719F"
CTK_BLUE_DARK       = "#1F6AA5"
CTK_BLUE_DARK_HOVER = "#144870"

BTN_MAIN_FG      = (YT_RED, YT_RED)
BTN_MAIN_HOVER   = (YT_RED_HOVER, YT_RED_HOVER)
BTN_ACCENT_FG    = (YT_RED, CTK_BLUE_DARK)
BTN_ACCENT_HOVER = (YT_RED_HOVER, CTK_BLUE_DARK_HOVER)
BTN_CLEAR_FG     = (CTK_BLUE, YT_RED)
BTN_CLEAR_HOVER  = (CTK_BLUE_HOVER, YT_RED_HOVER)

GRAY_TEXT = ("gray40", "gray65")

# Fondo exacto de CTk en tema claro
LIGHT_BG = "#EBEBEB"


def _is_light_mode() -> bool:
    mode = ctk.get_appearance_mode().lower()
    if mode == "system":
        try:
            import darkdetect
            return not darkdetect.isDark()
        except Exception:
            return False
    return mode == "light"


def load_image_from_url(url: str, width: int, height: int):
    try:
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        img = Image.open(BytesIO(response.content)).convert("RGB")
        target_ratio = width / height
        orig_w, orig_h = img.size
        orig_ratio = orig_w / orig_h
        if orig_ratio > target_ratio:
            new_w = int(orig_h * target_ratio)
            left = (orig_w - new_w) // 2
            img = img.crop((left, 0, left + new_w, orig_h))
        elif orig_ratio < target_ratio:
            new_h = int(orig_w / target_ratio)
            top = (orig_h - new_h) // 2
            img = img.crop((0, top, orig_w, top + new_h))
        img = img.resize((width, height), Image.LANCZOS)
        return ctk.CTkImage(light_image=img, dark_image=img, size=(width, height))
    except Exception:
        return None


def open_file_location(file_path: str, fallback_folder: str):
    try:
        if file_path and os.path.exists(file_path):
            if sys.platform == "win32":
                subprocess.Popen(["explorer", "/select,", os.path.normpath(file_path)])
            elif sys.platform == "darwin":
                subprocess.Popen(["open", "-R", file_path])
            else:
                subprocess.Popen(["xdg-open", os.path.dirname(file_path)])
        elif fallback_folder and os.path.exists(fallback_folder):
            if sys.platform == "win32":
                subprocess.Popen(["explorer", os.path.normpath(fallback_folder)])
            elif sys.platform == "darwin":
                subprocess.Popen(["open", fallback_folder])
            else:
                subprocess.Popen(["xdg-open", fallback_folder])
        else:
            messagebox.showwarning("Aviso", "No se encontró el archivo ni la carpeta de destino.")
    except Exception as e:
        messagebox.showerror("Error", f"No se pudo abrir la ubicación.\n{e}")


def open_folder(folder: str):
    try:
        if sys.platform == "win32":
            subprocess.Popen(["explorer", os.path.normpath(folder)])
        elif sys.platform == "darwin":
            subprocess.Popen(["open", folder])
        else:
            subprocess.Popen(["xdg-open", folder])
    except Exception:
        pass


class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.config_data = load_config()

        ctk.set_appearance_mode(self.config_data['theme'])
        ctk.set_default_color_theme("blue")

        self.title("YouTube Downloader")
        self.geometry("680x720")
        self.resizable(False, False)

        self.output_path = self.config_data['default_output_path']
        self.video_info = None
        self._cancel_download = False
        self._spinner_running = False
        self._current_thumb = None
        self._active_tab = "Descargar"

        icon_path = os.path.join(os.path.dirname(__file__), '..', 'assets', 'icon.ico')
        if getattr(sys, 'frozen', False):
            icon_path = os.path.join(sys._MEIPASS, 'assets', 'icon.ico')
        if os.path.exists(icon_path):
            self.iconbitmap(icon_path)

        self._build_ui()

    # ------------------------------------------------------------------ #
    #  UI BUILD / REBUILD
    # ------------------------------------------------------------------ #

    def _build_ui(self):
        for widget in self.winfo_children():
            widget.destroy()

        self.label_main_title = ctk.CTkLabel(
            self, text="YouTube Downloader",
            font=ctk.CTkFont(size=20, weight="bold"))
        self.label_main_title.pack(pady=(20, 10))

        self.tabview = ctk.CTkTabview(self)
        self.tabview.pack(padx=20, pady=10, fill="both", expand=True)
        self.tabview.add("Descargar")
        self.tabview.add("Historial")
        self.tabview.add("Configuración")

        self._build_download_tab()
        self._build_history_tab()
        self._build_config_tab()

        self._apply_tab_colors()

        try:
            self.tabview.set(self._active_tab)
        except Exception:
            pass

    def _rebuild_ui(self):
        try:
            self._active_tab = self.tabview.get()
        except Exception:
            self._active_tab = "Configuración"
        self._build_ui()

    def _apply_tab_colors(self):
        seg = self.tabview._segmented_button
        if _is_light_mode():
            # Leer el color real del fondo del segmented para usarlo como "invisible"
            seg_bg = seg.cget("fg_color")
            if isinstance(seg_bg, (list, tuple)):
                seg_bg = seg_bg[0]
            seg.configure(
                selected_color=YT_RED,
                selected_hover_color=YT_RED_HOVER,
                unselected_color=seg_bg,
                unselected_hover_color=seg_bg,
            )
        else:
            self.tabview.configure(fg_color=("gray86", "gray17"))
            seg.configure(
                fg_color=("gray76", "gray29"),
                selected_color=CTK_BLUE_DARK,
                selected_hover_color=CTK_BLUE_DARK_HOVER,
                unselected_color=("gray76", "gray29"),
                unselected_hover_color=("gray70", "gray23"),
                text_color=("gray14", "gray84"),
                text_color_disabled=("gray14", "gray84"),
            )

    # ------------------------------------------------------------------ #
    #  PESTAÑA DESCARGAR
    # ------------------------------------------------------------------ #

    def _build_download_tab(self):
        tab = self.tabview.tab("Descargar")

        self.frame_url = ctk.CTkFrame(tab)
        self.frame_url.pack(padx=10, pady=10, fill="x")
        self.entry_url = ctk.CTkEntry(
            self.frame_url, placeholder_text="Pega aquí la URL de YouTube...", width=440)
        self.entry_url.pack(side="left", padx=(10, 5), pady=10)
        self.btn_search = ctk.CTkButton(
            self.frame_url, text="Buscar", width=90,
            fg_color=BTN_MAIN_FG, hover_color=BTN_MAIN_HOVER,
            command=self._on_search)
        self.btn_search.pack(side="left", padx=(5, 10), pady=10)

        self.frame_info = ctk.CTkFrame(tab)
        self.frame_info.pack(padx=10, pady=(0, 6), fill="x")
        self.frame_info.columnconfigure(1, weight=1)

        self.thumb_label = ctk.CTkLabel(
            self.frame_info, text="", width=THUMB_W, height=THUMB_H,
            fg_color="transparent", corner_radius=8)
        self.thumb_label.grid(row=0, column=0, rowspan=4, padx=(10, 14), pady=12, sticky="w")

        self.label_title_video = ctk.CTkLabel(
            self.frame_info, text="Título: -", anchor="w",
            wraplength=450, font=ctk.CTkFont(size=12, weight="bold"))
        self.label_title_video.grid(row=0, column=1, padx=(0, 10), pady=(12, 2), sticky="ew")

        self.label_uploader = ctk.CTkLabel(
            self.frame_info, text="Canal: -", anchor="w",
            text_color=GRAY_TEXT, font=ctk.CTkFont(size=12))
        self.label_uploader.grid(row=1, column=1, padx=(0, 10), pady=1, sticky="ew")

        self.label_duration = ctk.CTkLabel(
            self.frame_info, text="Duración: -", anchor="w",
            text_color=GRAY_TEXT, font=ctk.CTkFont(size=12))
        self.label_duration.grid(row=2, column=1, padx=(0, 10), pady=1, sticky="ew")

        self.label_qualities = ctk.CTkLabel(
            self.frame_info, text="Calidades: -", anchor="w",
            text_color=GRAY_TEXT, font=ctk.CTkFont(size=12), wraplength=450)
        self.label_qualities.grid(row=3, column=1, padx=(0, 10), pady=(1, 12), sticky="ew")

        self.label_spinner = ctk.CTkLabel(
            tab, text="", text_color=GRAY_TEXT, font=ctk.CTkFont(size=12))
        self.label_spinner.pack()

        self.frame_options = ctk.CTkFrame(tab)
        self.frame_options.pack(padx=10, pady=(0, 10), fill="x")

        ctk.CTkLabel(self.frame_options, text="Formato:").grid(
            row=0, column=0, padx=10, pady=10, sticky="w")
        self.combo_format = ctk.CTkComboBox(
            self.frame_options, values=ALL_FORMATS_COMBO, width=120,
            command=self._on_format_change)
        self.combo_format.set(self.config_data['default_format'])
        self.combo_format.grid(row=0, column=1, padx=10, pady=10, sticky="w")

        ctk.CTkLabel(self.frame_options, text="Calidad:").grid(
            row=1, column=0, padx=10, pady=10, sticky="w")
        self.combo_quality = ctk.CTkComboBox(
            self.frame_options, values=["Busca un vídeo primero"], width=150)
        if self._is_audio_format(self.config_data['default_format']):
            self.combo_quality.configure(values=AUDIO_QUALITIES)
            self.combo_quality.set(self.config_data['default_quality_audio'])
        self.combo_quality.grid(row=1, column=1, padx=10, pady=10, sticky="w")

        ctk.CTkLabel(self.frame_options, text="Carpeta:").grid(
            row=2, column=0, padx=10, pady=10, sticky="w")
        self.entry_folder = ctk.CTkEntry(self.frame_options, width=380)
        self.entry_folder.insert(0, self.output_path)
        self.entry_folder.grid(row=2, column=1, padx=10, pady=10, sticky="w")
        ctk.CTkButton(
            self.frame_options, text="...", width=40,
            fg_color=BTN_ACCENT_FG, hover_color=BTN_ACCENT_HOVER,
            command=self._on_select_folder).grid(row=2, column=2, padx=(4, 10), pady=10)

        self.progress_bar = ctk.CTkProgressBar(tab, width=620)
        self.progress_bar.pack(padx=10, pady=(10, 2))
        self.progress_bar.set(0)

        self.frame_status = ctk.CTkFrame(tab, fg_color="transparent")
        self.frame_status.pack(fill="x", padx=10)
        self.label_progress = ctk.CTkLabel(self.frame_status, text="0%")
        self.label_progress.pack(side="left", padx=10)
        self.label_speed = ctk.CTkLabel(self.frame_status, text="", text_color=GRAY_TEXT)
        self.label_speed.pack(side="right", padx=10)

        self.label_status = ctk.CTkLabel(tab, text="", text_color=GRAY_TEXT)
        self.label_status.pack()

        self.btn_download = ctk.CTkButton(
            tab, text="Descargar", width=200, height=40,
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color=BTN_MAIN_FG, hover_color=BTN_MAIN_HOVER,
            command=self._on_download)
        self.btn_download.pack(pady=10)

    # ------------------------------------------------------------------ #
    #  PESTAÑA HISTORIAL
    # ------------------------------------------------------------------ #

    def _build_history_tab(self):
        tab = self.tabview.tab("Historial")
        self.btn_clear = ctk.CTkButton(
            tab, text="Limpiar historial", width=160,
            fg_color=BTN_CLEAR_FG, hover_color=BTN_CLEAR_HOVER,
            command=self._on_clear_history)
        self.btn_clear.pack(padx=10, pady=(10, 5), anchor="e")

        self.history_frame = ctk.CTkScrollableFrame(tab)
        self.history_frame.pack(padx=10, pady=5, fill="both", expand=True)
        self._refresh_history()

    # ------------------------------------------------------------------ #
    #  PESTAÑA CONFIGURACIÓN
    # ------------------------------------------------------------------ #

    def _build_config_tab(self):
        tab = self.tabview.tab("Configuración")

        scroll = ctk.CTkScrollableFrame(tab, fg_color="transparent")
        scroll.pack(padx=10, pady=10, fill="both", expand=True)
        scroll.columnconfigure(1, weight=1)

        row = 0

        ctk.CTkLabel(scroll, text="Descargas",
                     font=ctk.CTkFont(size=14, weight="bold"), anchor="w").grid(
            row=row, column=0, columnspan=2, padx=10, pady=(10, 4), sticky="w")
        row += 1

        ctk.CTkLabel(scroll, text="Abrir carpeta al terminar la descarga:",
                     anchor="w").grid(row=row, column=0, padx=10, pady=8, sticky="w")
        self.switch_open_folder = ctk.CTkSwitch(scroll, text="")
        if self.config_data['open_folder_after_download']:
            self.switch_open_folder.select()
        self.switch_open_folder.grid(row=row, column=1, padx=10, pady=8, sticky="w")
        row += 1

        ctk.CTkLabel(scroll, text="Carpeta de descarga por defecto:",
                     anchor="w").grid(row=row, column=0, padx=10, pady=8, sticky="w")
        frame_folder = ctk.CTkFrame(scroll, fg_color="transparent")
        frame_folder.grid(row=row, column=1, padx=10, pady=8, sticky="ew")
        self.entry_default_folder = ctk.CTkEntry(frame_folder, width=300)
        self.entry_default_folder.insert(0, self.config_data['default_output_path'])
        self.entry_default_folder.pack(side="left", padx=(0, 6))
        ctk.CTkButton(
            frame_folder, text="...", width=40,
            fg_color=BTN_ACCENT_FG, hover_color=BTN_ACCENT_HOVER,
            command=self._on_browse_default_folder).pack(side="left")
        row += 1

        ctk.CTkFrame(scroll, height=1, fg_color=("gray70", "gray30")).grid(
            row=row, column=0, columnspan=2, padx=10, pady=8, sticky="ew")
        row += 1

        ctk.CTkLabel(scroll, text="Apariencia",
                     font=ctk.CTkFont(size=14, weight="bold"), anchor="w").grid(
            row=row, column=0, columnspan=2, padx=10, pady=(4, 4), sticky="w")
        row += 1

        ctk.CTkLabel(scroll, text="Tema:", anchor="w").grid(
            row=row, column=0, padx=10, pady=8, sticky="w")
        self.combo_theme = ctk.CTkComboBox(
            scroll,
            values=[THEME_LABELS[t] for t in THEME_OPTIONS],
            width=140,
            command=self._on_theme_change)
        self.combo_theme.set(THEME_LABELS.get(self.config_data['theme'], "Oscuro"))
        self.combo_theme.grid(row=row, column=1, padx=10, pady=8, sticky="w")
        row += 1

        ctk.CTkFrame(scroll, height=1, fg_color=("gray70", "gray30")).grid(
            row=row, column=0, columnspan=2, padx=10, pady=8, sticky="ew")
        row += 1

        ctk.CTkLabel(scroll, text="Formato y calidad por defecto",
                     font=ctk.CTkFont(size=14, weight="bold"), anchor="w").grid(
            row=row, column=0, columnspan=2, padx=10, pady=(4, 4), sticky="w")
        row += 1

        ctk.CTkLabel(scroll, text="Formato:", anchor="w").grid(
            row=row, column=0, padx=10, pady=8, sticky="w")
        self.combo_default_format = ctk.CTkComboBox(
            scroll, values=ALL_VIDEO_FORMATS + ALL_AUDIO_FORMATS, width=120)
        self.combo_default_format.set(self.config_data['default_format'])
        self.combo_default_format.grid(row=row, column=1, padx=10, pady=8, sticky="w")
        row += 1

        ctk.CTkLabel(scroll, text="Calidad de vídeo por defecto:", anchor="w").grid(
            row=row, column=0, padx=10, pady=8, sticky="w")
        self.combo_default_video_quality = ctk.CTkComboBox(
            scroll, values=VIDEO_QUALITY_OPTIONS, width=160)
        self.combo_default_video_quality.set(self.config_data['default_quality_video'])
        self.combo_default_video_quality.grid(row=row, column=1, padx=10, pady=8, sticky="w")
        row += 1

        ctk.CTkLabel(scroll, text="Calidad de audio por defecto:", anchor="w").grid(
            row=row, column=0, padx=10, pady=8, sticky="w")
        self.combo_default_audio_quality = ctk.CTkComboBox(
            scroll, values=AUDIO_QUALITIES, width=120)
        self.combo_default_audio_quality.set(self.config_data['default_quality_audio'])
        self.combo_default_audio_quality.grid(row=row, column=1, padx=10, pady=8, sticky="w")
        row += 1

        ctk.CTkFrame(scroll, height=1, fg_color=("gray70", "gray30")).grid(
            row=row, column=0, columnspan=2, padx=10, pady=8, sticky="ew")
        row += 1

        self.btn_save_config = ctk.CTkButton(
            scroll, text="Guardar configuración", width=220,
            fg_color=BTN_MAIN_FG, hover_color=BTN_MAIN_HOVER,
            command=self._on_save_config)
        self.btn_save_config.grid(row=row, column=0, columnspan=2, pady=16)

    # ------------------------------------------------------------------ #
    #  SPINNER
    # ------------------------------------------------------------------ #

    def _start_spinner(self):
        self._spinner_running = True
        self._spinner_step = 0
        self._animate_spinner()

    def _animate_spinner(self):
        if not self._spinner_running:
            self.label_spinner.configure(text="")
            return
        dots = "." * (self._spinner_step % 4)
        self.label_spinner.configure(text=f"Buscando{dots}")
        self._spinner_step += 1
        self.after(400, self._animate_spinner)

    def _stop_spinner(self):
        self._spinner_running = False

    # ------------------------------------------------------------------ #
    #  THUMBNAIL
    # ------------------------------------------------------------------ #

    def _load_thumbnail_async(self, url: str):
        def _fetch():
            img = load_image_from_url(url, THUMB_W, THUMB_H)
            if img:
                self._current_thumb = img
                self.after(0, lambda: self.thumb_label.configure(image=img, text=""))
        threading.Thread(target=_fetch, daemon=True).start()

    def _clear_thumbnail(self):
        self._current_thumb = None
        self.thumb_label.configure(image=None, text="")

    # ------------------------------------------------------------------ #
    #  HISTORIAL
    # ------------------------------------------------------------------ #

    def _refresh_history(self):
        for widget in self.history_frame.winfo_children():
            widget.destroy()
        from history import load_history
        history = load_history()
        if not history:
            ctk.CTkLabel(self.history_frame, text="No hay descargas registradas.",
                         anchor="w").pack(padx=10, pady=20)
            return
        for entry in history:
            self._build_history_card(entry)

    def _build_history_card(self, entry: dict):
        frame = ctk.CTkFrame(self.history_frame)
        frame.pack(padx=5, pady=5, fill="x")
        frame.columnconfigure(1, weight=1)

        title     = entry.get('title', '-')
        fmt       = entry.get('format', '-')
        quality   = entry.get('quality', '-')
        size      = entry.get('size_mb', '-')
        elapsed   = entry.get('elapsed_seconds', '-')
        date      = entry.get('date', '-')
        path      = entry.get('output_path', '-')
        file_path = entry.get('file_path')
        thumb_url = entry.get('thumbnail_url')

        thumb_lbl = ctk.CTkLabel(
            frame, text="", width=HIST_THUMB_W, height=HIST_THUMB_H,
            fg_color="transparent", corner_radius=6)
        thumb_lbl.grid(row=0, column=0, rowspan=3, padx=(10, 10), pady=10, sticky="ns")

        if thumb_url:
            def _fetch(url=thumb_url, lbl=thumb_lbl):
                img = load_image_from_url(url, HIST_THUMB_W, HIST_THUMB_H)
                if img:
                    self.after(0, lambda: lbl.configure(image=img, text=""))
            threading.Thread(target=_fetch, daemon=True).start()

        row_top = ctk.CTkFrame(frame, fg_color="transparent")
        row_top.grid(row=0, column=1, sticky="ew", padx=(0, 10), pady=(10, 2))
        row_top.columnconfigure(0, weight=1)

        ctk.CTkLabel(row_top, text=f"🎬 {title}",
                     font=ctk.CTkFont(weight="bold"), anchor="w",
                     wraplength=400).grid(row=0, column=0, sticky="ew")

        ctk.CTkButton(
            row_top, text="📂 Abrir", width=80, height=26,
            fg_color="transparent", border_width=1,
            text_color=("gray40", "gray70"),
            hover_color=("gray85", "gray25"),
            command=lambda fp=file_path, p=path: open_file_location(fp, p)
        ).grid(row=0, column=1, padx=(6, 0))

        ctk.CTkLabel(
            frame,
            text=f"📅 {date}   •   {fmt}   •   {quality}   •   {size} MB   •   {elapsed}s",
            anchor="w", text_color=GRAY_TEXT).grid(
            row=1, column=1, sticky="ew", padx=(0, 10), pady=(0, 2))

        ctk.CTkLabel(frame, text=f"📁 {path}", anchor="w",
                     text_color=GRAY_TEXT, wraplength=480).grid(
            row=2, column=1, sticky="ew", padx=(0, 10), pady=(0, 10))

    def _on_clear_history(self):
        from history import clear_history
        if messagebox.askyesno("Confirmar", "¿Seguro que quieres borrar todo el historial?"):
            clear_history()
            self._refresh_history()

    # ------------------------------------------------------------------ #
    #  CONFIGURACIÓN — handlers
    # ------------------------------------------------------------------ #

    def _on_browse_default_folder(self):
        folder = filedialog.askdirectory(
            initialdir=self.entry_default_folder.get() or os.path.expanduser("~"))
        if folder:
            self.entry_default_folder.delete(0, "end")
            self.entry_default_folder.insert(0, folder)

    def _on_theme_change(self, label):
        theme = THEME_REVERSE.get(label, "dark")
        self.config_data['theme'] = theme
        ctk.set_appearance_mode(theme)
        self.after(50, self._rebuild_ui)

    def _on_save_config(self):
        theme = THEME_REVERSE.get(self.combo_theme.get(), "dark")
        new_config = {
            'open_folder_after_download': self.switch_open_folder.get() == 1,
            'default_output_path': self.entry_default_folder.get().strip(),
            'theme': theme,
            'default_format': self.combo_default_format.get(),
            'default_quality_video': self.combo_default_video_quality.get(),
            'default_quality_audio': self.combo_default_audio_quality.get(),
        }
        save_config(new_config)
        self.config_data = new_config

        self.output_path = new_config['default_output_path']
        self.entry_folder.delete(0, "end")
        self.entry_folder.insert(0, self.output_path)
        self.combo_format.set(new_config['default_format'])
        self._on_format_change(new_config['default_format'])

        self.btn_save_config.configure(text="✓ Guardado")
        self.after(2000, lambda: self.btn_save_config.configure(text="Guardar configuración"))

    # ------------------------------------------------------------------ #
    #  FORMATO / CALIDAD
    # ------------------------------------------------------------------ #

    def _is_audio_format(self, fmt):
        return fmt.lower() in ALL_AUDIO_FORMATS

    def _on_format_change(self, value):
        if value.startswith("──"):
            self.combo_format.set("mp4")
            value = "mp4"
        if self._is_audio_format(value):
            self.combo_quality.configure(state="normal", values=AUDIO_QUALITIES)
            self.combo_quality.set(self.config_data.get('default_quality_audio', AUDIO_QUALITIES[0]))
        else:
            self.combo_quality.configure(state="normal")
            if self.video_info and self.video_info.get('formats'):
                formats = self.video_info['formats']
                default_vq = self.config_data.get('default_quality_video', 'Mejor disponible')
                self.combo_quality.configure(values=formats)
                if default_vq != 'Mejor disponible' and default_vq in formats:
                    self.combo_quality.set(default_vq)
                else:
                    self.combo_quality.set(formats[0])
            else:
                self.combo_quality.configure(values=["Busca un vídeo primero"])
                self.combo_quality.set("Busca un vídeo primero")

    # ------------------------------------------------------------------ #
    #  BUSCAR
    # ------------------------------------------------------------------ #

    def _on_search(self):
        url = self.entry_url.get().strip()
        if not url:
            messagebox.showwarning("Aviso", "Por favor introduce una URL.")
            return
        self.btn_search.configure(state="disabled", text="Buscando...")
        self._clear_thumbnail()
        self.label_title_video.configure(text="Título: -")
        self.label_uploader.configure(text="Canal: -")
        self.label_duration.configure(text="Duración: -")
        self.label_qualities.configure(text="Calidades: -")
        self._start_spinner()

        def search_thread():
            try:
                info = get_video_info(url)
                self.video_info = info
                minutes = info['duration'] // 60
                secs = info['duration'] % 60
                duration_str = f"{minutes}:{secs:02d}"
                qualities_str = "  •  ".join(info['formats']) if info['formats'] else "-"
                self.after(0, lambda: self._update_info(
                    info['title'], info.get('uploader', '-'),
                    duration_str, qualities_str, info['formats']))
                if info.get('thumbnail'):
                    self._load_thumbnail_async(info['thumbnail'])
            except Exception as e:
                self.after(0, lambda: messagebox.showerror(
                    "Error", f"No se pudo obtener información del vídeo.\n{e}"))
            finally:
                self.after(0, self._stop_spinner)
                self.after(0, lambda: self.btn_search.configure(state="normal", text="Buscar"))

        threading.Thread(target=search_thread, daemon=True).start()

    def _update_info(self, title, uploader, duration, qualities_str, formats):
        self.label_title_video.configure(text=f"Título: {title}")
        self.label_uploader.configure(text=f"Canal: {uploader}")
        self.label_duration.configure(text=f"Duración: {duration}")
        self.label_qualities.configure(text=f"Calidades: {qualities_str}")
        if not self._is_audio_format(self.combo_format.get()):
            default_vq = self.config_data.get('default_quality_video', 'Mejor disponible')
            self.combo_quality.configure(state="normal", values=formats)
            if default_vq != 'Mejor disponible' and default_vq in formats:
                self.combo_quality.set(default_vq)
            else:
                self.combo_quality.set(formats[0])

    # ------------------------------------------------------------------ #
    #  CARPETA
    # ------------------------------------------------------------------ #

    def _on_select_folder(self):
        folder = filedialog.askdirectory(initialdir=self.output_path)
        if folder:
            self.output_path = folder
            self.entry_folder.delete(0, "end")
            self.entry_folder.insert(0, folder)

    # ------------------------------------------------------------------ #
    #  DESCARGAR
    # ------------------------------------------------------------------ #

    def _on_cancel(self):
        self._cancel_download = True
        self.label_status.configure(text="Cancelando...")

    def _on_download(self):
        if not self.video_info:
            messagebox.showwarning("Aviso", "Primero busca un vídeo.")
            return
        url = self.entry_url.get().strip()
        quality = self.combo_quality.get()
        output_format = self.combo_format.get()
        output_path = self.entry_folder.get().strip()

        if output_format.startswith("──"):
            messagebox.showwarning("Aviso", "Selecciona un formato válido.")
            return

        self._cancel_download = False
        self.btn_download.configure(
            text="Cancelar", fg_color=("gray60", "gray35"),
            hover_color=("gray50", "gray25"), command=self._on_cancel)
        self.progress_bar.set(0)
        self.label_progress.configure(text="0%")
        self.label_speed.configure(text="")
        self.label_status.configure(text="Iniciando descarga...")

        def progress_callback(percentage, speed):
            if self._cancel_download:
                return
            self.after(0, lambda: self.progress_bar.set(percentage / 100))
            self.after(0, lambda: self.label_progress.configure(text=f"{int(percentage)}%"))
            if speed and speed > 0:
                speed_str = (f"{speed / (1024*1024):.1f} MB/s"
                             if speed >= 1024 * 1024
                             else f"{speed / 1024:.0f} KB/s")
                self.after(0, lambda: self.label_speed.configure(text=speed_str))
            if percentage == 100:
                self.after(0, lambda: self.label_status.configure(text="Procesando archivo..."))
                self.after(0, lambda: self.label_speed.configure(text=""))

        def download_thread():
            from history import save_entry, build_entry
            result = download_video(url, quality, output_format, output_path,
                                    progress_callback, lambda: self._cancel_download)
            if self._cancel_download:
                self.after(0, lambda: self.label_status.configure(text="✗ Descarga cancelada"))
                self.after(0, lambda: self.progress_bar.set(0))
                self.after(0, lambda: self.label_progress.configure(text="0%"))
            elif result:
                save_entry(build_entry(result))
                self.after(0, self._refresh_history)
                self.after(0, lambda: self.label_status.configure(text="✓ Descarga completada"))
                self.after(0, self._reset_form)
                if self.config_data.get('open_folder_after_download'):
                    self.after(500, lambda: open_folder(output_path))
                msg = (f"Descarga completada.\n\n"
                       f"Formato: {result['format'].upper()}\n"
                       f"Calidad: {result['quality']}\n"
                       f"Peso: {result['size_mb']} MB\n"
                       f"Tiempo: {result['elapsed_seconds']}s\n"
                       f"Carpeta: {result['output_path']}")
                self.after(0, lambda: messagebox.showinfo("Completado", msg))
            else:
                self.after(0, lambda: self.label_status.configure(text="✗ Error en la descarga"))
                self.after(0, lambda: messagebox.showerror("Error", "No se pudo descargar el vídeo."))
            self.after(0, lambda: self.btn_download.configure(
                text="Descargar", fg_color=BTN_MAIN_FG,
                hover_color=BTN_MAIN_HOVER, command=self._on_download))

        threading.Thread(target=download_thread, daemon=True).start()

    def _reset_form(self):
        self.entry_url.delete(0, "end")
        self.video_info = None
        self.label_title_video.configure(text="Título: -")
        self.label_uploader.configure(text="Canal: -")
        self.label_duration.configure(text="Duración: -")
        self.label_qualities.configure(text="Calidades: -")
        self._clear_thumbnail()
        self.combo_quality.configure(values=["Busca un vídeo primero"])
        self.combo_quality.set("Busca un vídeo primero")
        self.progress_bar.set(0)
        self.label_progress.configure(text="0%")


def main():
    app = App()
    app.mainloop()


if __name__ == "__main__":
    main()