import customtkinter as ctk
from tkinter import filedialog, messagebox
import threading
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
from downloader import get_video_info, download_video
from history import load_history, save_entry, clear_history, build_entry

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

class App(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("YouTube Downloader")
        self.geometry("600x600")
        self.resizable(False, False)

        self.output_path = os.path.join(os.path.expanduser("~"), "Downloads")
        self.video_info = None

        self._build_ui()

    def _build_ui(self):
        # Título
        self.label_title = ctk.CTkLabel(self, text="YouTube Downloader", font=ctk.CTkFont(size=20, weight="bold"))
        self.label_title.pack(pady=(20, 10))

        # Pestañas
        self.tabview = ctk.CTkTabview(self)
        self.tabview.pack(padx=20, pady=10, fill="both", expand=True)

        self.tabview.add("Descargar")
        self.tabview.add("Historial")

        self._build_download_tab()
        self._build_history_tab()

    def _build_download_tab(self):
        tab = self.tabview.tab("Descargar")

        # Frame URL
        self.frame_url = ctk.CTkFrame(tab)
        self.frame_url.pack(padx=10, pady=10, fill="x")

        self.entry_url = ctk.CTkEntry(self.frame_url, placeholder_text="Pega aquí la URL de YouTube...", width=380)
        self.entry_url.pack(side="left", padx=(10, 5), pady=10)

        self.btn_search = ctk.CTkButton(self.frame_url, text="Buscar", width=80, command=self._on_search)
        self.btn_search.pack(side="left", padx=(5, 10), pady=10)

        # Frame info vídeo
        self.frame_info = ctk.CTkFrame(tab)
        self.frame_info.pack(padx=10, pady=10, fill="x")

        self.label_title_video = ctk.CTkLabel(self.frame_info, text="Título: -", anchor="w")
        self.label_title_video.pack(padx=10, pady=(10, 2), fill="x")

        self.label_duration = ctk.CTkLabel(self.frame_info, text="Duración: -", anchor="w")
        self.label_duration.pack(padx=10, pady=(2, 10), fill="x")

        # Frame opciones
        self.frame_options = ctk.CTkFrame(tab)
        self.frame_options.pack(padx=10, pady=10, fill="x")

        # Selector formato
        self.label_format = ctk.CTkLabel(self.frame_options, text="Formato:")
        self.label_format.grid(row=0, column=0, padx=10, pady=10, sticky="w")

        self.combo_format = ctk.CTkComboBox(self.frame_options, values=["mp4", "mp3"], width=100,
                                             command=self._on_format_change)
        self.combo_format.set("mp4")
        self.combo_format.grid(row=0, column=1, padx=10, pady=10, sticky="w")

        # Selector calidad
        self.label_quality = ctk.CTkLabel(self.frame_options, text="Calidad:")
        self.label_quality.grid(row=1, column=0, padx=10, pady=10, sticky="w")

        self.combo_quality = ctk.CTkComboBox(self.frame_options, values=["Busca un vídeo primero"], width=150)
        self.combo_quality.grid(row=1, column=1, padx=10, pady=10, sticky="w")

        # Selector carpeta
        self.label_folder = ctk.CTkLabel(self.frame_options, text="Carpeta:")
        self.label_folder.grid(row=2, column=0, padx=10, pady=10, sticky="w")

        self.entry_folder = ctk.CTkEntry(self.frame_options, width=320)
        self.entry_folder.insert(0, self.output_path)
        self.entry_folder.grid(row=2, column=1, padx=10, pady=10, sticky="w")

        self.btn_folder = ctk.CTkButton(self.frame_options, text="...", width=40, command=self._on_select_folder)
        self.btn_folder.grid(row=2, column=2, padx=10, pady=10)

        # Barra de progreso
        self.progress_bar = ctk.CTkProgressBar(tab, width=540)
        self.progress_bar.pack(padx=10, pady=(10, 2))
        self.progress_bar.set(0)

        self.label_progress = ctk.CTkLabel(tab, text="0%")
        self.label_progress.pack()

        # Botón descargar
        self.btn_download = ctk.CTkButton(tab, text="Descargar", width=200, height=40,
                                           font=ctk.CTkFont(size=14, weight="bold"),
                                           command=self._on_download)
        self.btn_download.pack(pady=15)

    def _build_history_tab(self):
        tab = self.tabview.tab("Historial")

        # Botón limpiar historial
        self.btn_clear = ctk.CTkButton(tab, text="Limpiar historial", width=160,
                                        fg_color="red", hover_color="#aa0000",
                                        command=self._on_clear_history)
        self.btn_clear.pack(padx=10, pady=(10, 5), anchor="e")

        # Frame scrollable para las entradas
        self.history_frame = ctk.CTkScrollableFrame(tab)
        self.history_frame.pack(padx=10, pady=5, fill="both", expand=True)

        self._refresh_history()

    def _refresh_history(self):
        # Limpiar frame
        for widget in self.history_frame.winfo_children():
            widget.destroy()

        history = load_history()

        if not history:
            ctk.CTkLabel(self.history_frame, text="No hay descargas registradas.", anchor="w").pack(padx=10, pady=20)
            return

        for entry in history:
            frame = ctk.CTkFrame(self.history_frame)
            frame.pack(padx=5, pady=5, fill="x")

            title = entry.get('title', '-')
            fmt = entry.get('format', '-')
            quality = entry.get('quality', '-')
            size = entry.get('size_mb', '-')
            elapsed = entry.get('elapsed_seconds', '-')
            date = entry.get('date', '-')
            path = entry.get('output_path', '-')

            ctk.CTkLabel(frame, text=f"🎬 {title}", anchor="w",
                         font=ctk.CTkFont(weight="bold"), wraplength=500).pack(padx=10, pady=(8, 2), fill="x")
            ctk.CTkLabel(frame, text=f"📅 {date}   •   {fmt}   •   {quality}   •   {size} MB   •   {elapsed}s",
                         anchor="w", text_color="gray").pack(padx=10, pady=(2, 2), fill="x")
            ctk.CTkLabel(frame, text=f"📁 {path}", anchor="w",
                         text_color="gray", wraplength=500).pack(padx=10, pady=(2, 8), fill="x")

    def _on_clear_history(self):
        if messagebox.askyesno("Confirmar", "¿Seguro que quieres borrar todo el historial?"):
            clear_history()
            self._refresh_history()

    def _on_format_change(self, value):
        if value == "mp3":
            self.combo_quality.configure(state="normal", values=["128kbps", "192kbps", "320kbps"])
            self.combo_quality.set("192kbps")
        else:
            self.combo_quality.configure(state="normal")
            if self.video_info:
                self.combo_quality.configure(values=self.video_info['formats'])
                self.combo_quality.set(self.video_info['formats'][0])
            else:
                self.combo_quality.configure(values=["Busca un vídeo primero"])
                self.combo_quality.set("Busca un vídeo primero")

    def _on_search(self):
        url = self.entry_url.get().strip()
        if not url:
            messagebox.showwarning("Aviso", "Por favor introduce una URL.")
            return

        self.btn_search.configure(state="disabled", text="Buscando...")
        self.label_title_video.configure(text="Título: -")
        self.label_duration.configure(text="Duración: -")

        def search_thread():
            try:
                info = get_video_info(url)
                self.video_info = info

                seconds = info['duration']
                minutes = seconds // 60
                secs = seconds % 60
                duration_str = f"{minutes}:{secs:02d}"

                self.after(0, lambda: self._update_info(info['title'], duration_str, info['formats']))
            except Exception as e:
                self.after(0, lambda: messagebox.showerror("Error", f"No se pudo obtener información del vídeo.\n{e}"))
            finally:
                self.after(0, lambda: self.btn_search.configure(state="normal", text="Buscar"))

        threading.Thread(target=search_thread, daemon=True).start()

    def _update_info(self, title, duration, formats):
        self.label_title_video.configure(text=f"Título: {title}")
        self.label_duration.configure(text=f"Duración: {duration}")
        if self.combo_format.get() == "mp4":
            self.combo_quality.configure(state="normal", values=formats)
            self.combo_quality.set(formats[0] if formats else "-")

    def _on_select_folder(self):
        folder = filedialog.askdirectory(initialdir=self.output_path)
        if folder:
            self.output_path = folder
            self.entry_folder.delete(0, "end")
            self.entry_folder.insert(0, folder)

    def _on_download(self):
        if not self.video_info:
            messagebox.showwarning("Aviso", "Primero busca un vídeo.")
            return

        url = self.entry_url.get().strip()
        quality = self.combo_quality.get()
        output_format = self.combo_format.get()
        output_path = self.entry_folder.get().strip()

        self.btn_download.configure(state="disabled", text="Descargando...")
        self.progress_bar.set(0)
        self.label_progress.configure(text="0%")

        def progress_callback(percentage):
            self.after(0, lambda: self.progress_bar.set(percentage / 100))
            self.after(0, lambda: self.label_progress.configure(text=f"{int(percentage)}%"))

        def download_thread():
            result = download_video(url, quality, output_format, output_path, progress_callback)
            if result:
                save_entry(build_entry(result))
                self.after(0, self._refresh_history)
                msg = (f"Descarga completada.\n\n"
                       f"Formato: {result['format'].upper()}\n"
                       f"Calidad: {result['quality']}\n"
                       f"Peso: {result['size_mb']} MB\n"
                       f"Tiempo: {result['elapsed_seconds']}s\n"
                       f"Carpeta: {result['output_path']}")
                self.after(0, lambda: messagebox.showinfo("Completado", msg))
            else:
                self.after(0, lambda: messagebox.showerror("Error", "No se pudo descargar el vídeo."))
            self.after(0, lambda: self.btn_download.configure(state="normal", text="Descargar"))

        threading.Thread(target=download_thread, daemon=True).start()

def main():
    app = App()
    app.mainloop()

if __name__ == "__main__":
    main()