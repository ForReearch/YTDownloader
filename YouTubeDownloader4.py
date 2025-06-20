import os
import yt_dlp
import tkinter as tk
from tkinter import messagebox, scrolledtext, font, ttk
import threading
import shutil
import sys

DOWNLOAD_FOLDER = "Video Downloaded"
os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)

def is_ffmpeg_installed():
    result = shutil.which("ffmpeg") is not None
    print(f"ffmpeg detected: {result}")
    return result

def load_khmer_font():
    # Assume KhmerOS_siemreap.ttf is in the same directory as the script (matching shorter code's file name)
    font_path = os.path.join(os.path.dirname(__file__), "KhmerOS_siemreap.ttf")
    font_name = "Khmer OS Siemreap Custom"
    if os.path.exists(font_path):
        try:
            font.Font(family=font_name, size=12, weight="bold", file=font_path)
            font.Font(family=font_name, size=10, file=font_path)
            available_fonts = font.families()
            if font_name in available_fonts:
                print(f"Successfully loaded font '{font_name}' from {font_path}")
                return font_name
            else:
                print(f"Warning: Font loaded but not found in font families as '{font_name}'. Available fonts: {available_fonts}")
                return "Khmer OS Siemreap"  # Align fallback with shorter code
        except Exception as e:
            print(f"Error: Failed to load KhmerOS_siemreap.ttf: {e}. Falling back to Khmer OS Siemreap.")
            return "Khmer OS Siemreap"
    else:
        print(f"Error: Font file 'KhmerOS_siemreap.ttf' not found at {font_path}. Falling back to Khmer OS Siemreap.")
        return "Khmer OS Siemreap"

class ScrollableFrame(tk.Frame):
    def __init__(self, container, bg_color, *args, **kwargs):
        super().__init__(container, *args, **kwargs)
        self.canvas = tk.Canvas(self, borderwidth=0, background=bg_color, highlightthickness=0)
        self.scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = tk.Frame(self.canvas, background=bg_color)
        
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )
        
        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        
        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")

        self.bind_mouse_wheel()

    def bind_mouse_wheel(self):
        def scroll(event):
            if event.delta:
                delta = -1 * (event.delta // 120)
            elif event.num == 4:
                delta = -1
            elif event.num == 5:
                delta = 1
            else:
                return
            self.canvas.yview_scroll(delta, "units")

        self.canvas.bind("<MouseWheel>", scroll)
        self.canvas.bind("<Button-4>", scroll)
        self.canvas.bind("<Button-5>", scroll)

        self.scrollable_frame.bind("<MouseWheel>", scroll)
        self.scrollable_frame.bind("<Button-4>", scroll)
        self.scrollable_frame.bind("<Button-5>", scroll)

        for child in self.scrollable_frame.winfo_children():
            child.bind("<MouseWheel>", scroll)
            child.bind("<Button-4>", scroll)
            child.bind("<Button-5>", scroll)
            for grandchild in child.winfo_children():
                if not isinstance(grandchild, scrolledtext.ScrolledText):
                    grandchild.bind("<MouseWheel>", scroll)
                    grandchild.bind("<Button-4>", scroll)
                    grandchild.bind("<Button-5>", scroll)

class YouTubeDownloaderGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Frog Downloader")
        self.root.geometry("700x650")
        
        self.theme = "light"
        self.set_theme()

        try:
            self.root.iconphoto(True, tk.PhotoImage(file="youtube.png"))
        except Exception as e:
            print(f"Warning: Could not load icon 'youtube.png': {e}")

        self.header_frame = tk.Frame(self.root, bg=self.colors['header'], pady=12)
        self.header_frame.pack(fill=tk.X)
        tk.Label(self.header_frame, text="Frog Downloader", font=("Helvetica", 16, "bold"), fg='white', bg=self.colors['header']).pack()

        container = tk.Frame(self.root, bg=self.colors['bg'])
        container.pack(fill="both", expand=True, padx=20, pady=20)
        
        self.scrollable_frame = ScrollableFrame(container, bg_color=self.colors['bg'])
        self.scrollable_frame.pack(fill="both", expand=True)
        
        self.main_frame = self.scrollable_frame.scrollable_frame
        self.main_frame.configure(bg=self.colors['bg'], padx=20, pady=20)

        khmer_font = load_khmer_font()
        self.label_font = (khmer_font, 12, "bold")
        self.secondary_font = (khmer_font, 10)
        self.button_font = (khmer_font, 10)

        style = ttk.Style()
        style.configure("TProgressbar", 
                       troughcolor=self.colors['bg'], 
                       background=self.colors['accent'],
                       thickness=4)
        style.configure("TEntry", 
                       fieldbackground=self.colors['card'],
                       padding=5)

        self.root.bind("<MouseWheel>", lambda e: self.scrollable_frame.canvas.yview_scroll(-1 * (e.delta // 120), "units"))
        self.root.bind("<Button-4>", lambda e: self.scrollable_frame.canvas.yview_scroll(-1, "units"))
        self.root.bind("<Button-5>", lambda e: self.scrollable_frame.canvas.yview_scroll(1, "units"))

        single_frame = tk.Frame(self.main_frame, bg=self.colors['card'], bd=1, relief=tk.SOLID, padx=15, pady=15)
        single_frame.pack(fill=tk.X, pady=8)
        tk.Label(single_frame, text="ទាញយកវីឌីអូតែមួយ ឬវីឌីអូខ្លី", font=self.label_font, fg=self.colors['text'], bg=self.colors['card']).grid(row=0, column=0, columnspan=2, sticky="w")
        tk.Label(single_frame, text="បញ្ចូល URL យូធូប:", font=self.secondary_font, fg=self.colors['text2'], bg=self.colors['card']).grid(row=1, column=0, sticky="w", pady=5)
        self.single_url_entry = ttk.Entry(single_frame, width=50)
        self.single_url_entry.grid(row=2, column=0, padx=5, pady=5, sticky="ew")
        tk.Button(single_frame, text="ទាញយកវីឌីអូតែមួយ", font=self.button_font, bg=self.colors['accent'], fg='white', activebackground=self.colors['accent_active'], relief="flat", command=self.download_single).grid(row=2, column=1, padx=5)

        multi_frame = tk.Frame(self.main_frame, bg=self.colors['card'], bd=1, relief=tk.SOLID, padx=15, pady=15)
        multi_frame.pack(fill=tk.X, pady=8)
        tk.Label(multi_frame, text="ទាញយកវីឌីអូច្រើន", font=self.label_font, fg=self.colors['text'], bg=self.colors['card']).grid(row=0, column=0, columnspan=2, sticky="w")
        tk.Label(multi_frame, text="បញ្ចូល URL យូធូប (មួយក្នុងមួយបន្ទាត់):", font=self.secondary_font, fg=self.colors['text2'], bg=self.colors['card']).grid(row=1, column=0, sticky="w", pady=5)
        self.multi_url_text = scrolledtext.ScrolledText(multi_frame, width=50, height=5, font=self.secondary_font, bg=self.colors['card'], fg=self.colors['text'])
        self.multi_url_text.grid(row=2, column=0, padx=5, pady=5, sticky="ew")
        tk.Button(multi_frame, text="ទាញយកវីឌីអូច្រើន", font=self.button_font, bg=self.colors['accent'], fg='white', activebackground=self.colors['accent_active'], relief="flat", command=self.download_multiple).grid(row=2, column=1, padx=5)

        channel_frame = tk.Frame(self.main_frame, bg=self.colors['card'], bd=1, relief=tk.SOLID, padx=15, pady=15)
        channel_frame.pack(fill=tk.X, pady=8)
        tk.Label(channel_frame, text="ទាញយកឆានែល ឬ ផ្លេលីស ទាំងមូល", font=self.label_font, fg=self.colors['text'], bg=self.colors['card']).grid(row=0, column=0, columnspan=2, sticky="w")
        tk.Label(channel_frame, text="បញ្ចូល URL ឆានែល/បញ្ជីចាក់:", font=self.secondary_font, fg=self.colors['text2'], bg=self.colors['card']).grid(row=1, column=0, sticky="w", pady=5)
        self.channel_url_entry = ttk.Entry(channel_frame, width=50)
        self.channel_url_entry.grid(row=2, column=0, padx=5, pady=5, sticky="ew")
        tk.Button(channel_frame, text="ទាញយកឆានែល/បញ្ជីចាក់", font=self.button_font, bg=self.colors['accent'], fg='white', activebackground=self.colors['accent_active'], relief="flat", command=self.download_channel).grid(row=2, column=1, padx=5)

        status_frame = tk.Frame(self.main_frame, bg=self.colors['card'], bd=1, relief=tk.SOLID, padx=15, pady=15)
        status_frame.pack(fill=tk.X, pady=8)
        tk.Label(status_frame, text="ស្ថានភាព:", font=self.label_font, fg=self.colors['text'], bg=self.colors['card']).pack(anchor="w")
        self.status_text = scrolledtext.ScrolledText(status_frame, width=60, height=8, state='disabled', font=self.secondary_font, bg=self.colors['card'], fg=self.colors['text'])
        self.status_text.pack(pady=5, fill=tk.X)
        self.progress = ttk.Progressbar(status_frame, mode='indeterminate')
        self.progress.pack(fill=tk.X, pady=5)

        footer_frame = tk.Frame(self.root, bg=self.colors['bg'], pady=12)
        footer_frame.pack(fill=tk.X, side=tk.BOTTOM)
        tk.Button(footer_frame, text="ចាកចេញ", font=self.button_font, bg=self.colors['accent'], fg='white', activebackground=self.colors['accent_active'], relief="flat", command=self.root.quit).pack(side=tk.LEFT, padx=5)
        self.theme_button = tk.Button(footer_frame, text="Dark Theme", font=self.button_font, bg=self.colors['accent'], fg='white', activebackground=self.colors['accent_active'], relief="flat", command=self.toggle_theme)
        self.theme_button.pack(side=tk.LEFT, padx=5)

        ffmpeg_status = "ffmpeg ត្រូវបានរកឃើញ។ ប្រើគុណភាពល្អបំផុត។" if is_ffmpeg_installed() else "ffmpeg មិនត្រូវបានរកឃើញ។ ប្រើស្ទ្រីមតែមួយ (គុណភាពទាបជាង)។ ដំឡើង ffmpeg សម្រាប់គុណភាពល្អបំផុត។"
        self.log_status(f"ព័ត៌មាន: {ffmpeg_status}")

    def set_theme(self):
        if self.theme == "light":
            self.colors = {
                'bg': '#F0F2F5',
                'card': '#FFFFFF',
                'text': '#1C1E21',
                'text2': '#606770',
                'header': '#0866FF',
                'accent': '#0866FF',
                'accent_active': '#0057FF'
            }
        else:
            self.colors = {
                'bg': '#1C2526',
                'card': '#2C3435',
                'text': '#FFFFFF',
                'text2': '#B0B3B8',
                'header': '#0866FF',
                'accent': '#0866FF',
                'accent_active': '#0057FF'
            }
        self.root.configure(bg=self.colors['bg'])

    def toggle_theme(self):
        self.theme = "dark" if self.theme == "light" else "light"
        self.theme_button.config(text="Light Theme" if self.theme == "dark" else "Dark Theme")
        self.set_theme()
        self.update_gui_colors()

    def update_gui_colors(self):
        self.root.configure(bg=self.colors['bg'])
        self.header_frame.configure(bg=self.colors['header'])
        self.header_frame.winfo_children()[0].configure(bg=self.colors['header'], fg='white')
        self.scrollable_frame.configure(bg=self.colors['bg'])
        self.scrollable_frame.canvas.configure(bg=self.colors['bg'])
        self.main_frame.configure(bg=self.colors['bg'])
        
        for frame in self.main_frame.winfo_children():
            frame.configure(bg=self.colors['card'])
            for widget in frame.winfo_children():
                if isinstance(widget, tk.Label):
                    widget.configure(bg=self.colors['card'], fg=self.colors['text'] if widget.cget("font") == self.label_font else self.colors['text2'])
                elif isinstance(widget, scrolledtext.ScrolledText):
                    widget.configure(bg=self.colors['card'], fg=self.colors['text'])
                elif isinstance(widget, tk.Button):
                    widget.configure(bg=self.colors['accent'], fg='white', activebackground=self.colors['accent_active'])
        
        footer_frame = self.root.winfo_children()[-1]
        footer_frame.configure(bg=self.colors['bg'])
        for widget in footer_frame.winfo_children():
            widget.configure(bg=self.colors['accent'], fg='white', activebackground=self.colors['accent_active'])
        
        style = ttk.Style()
        style.configure("TProgressbar", troughcolor=self.colors['bg'], background=self.colors['accent'])
        style.configure("TEntry", fieldbackground=self.colors['card'])

    def log_status(self, message):
        self.status_text.config(state='normal')
        self.status_text.insert(tk.END, f"{message}\n")
        self.status_text.see(tk.END)
        self.status_text.config(state='disabled')

    def download_single(self):
        url = self.single_url_entry.get().strip()
        if not url:
            self.log_status("❌ កំហុស: សូមបញ្ចូល URL។")
            return
        self.progress.start()
        threading.Thread(target=self.download_single_thread, args=(url,), daemon=True).start()

    def download_single_thread(self, url):
        self.log_status(f"កំពុងទាញយក: {url}")
        with yt_dlp.YoutubeDL({
            'outtmpl': os.path.join(DOWNLOAD_FOLDER, '%(title)s.%(ext)s'),
            'format': 'bestvideo+bestaudio/best' if is_ffmpeg_installed() else 'best',
            'merge_output_format': 'mp4',
            'noplaylist': True,
        }) as ydl:
            try:
                ydl.download([url])
                self.log_status(f"✅ ទាញយកបានសម្រេច: {url} ➜ រក្សាទុកនៅ '{DOWNLOAD_FOLDER}'")
            except Exception as e:
                self.log_status(f"❌ បរាជ័យ: {url}: {e}")
            finally:
                self.root.after(0, self.progress.stop)

    def download_multiple(self):
        urls = self.multi_url_text.get("1.0", tk.END).strip().splitlines()
        urls = [url.strip() for url in urls if url.strip()]
        if not urls:
            self.log_status("❌ កំហុស: សូមបញ្ចូលយ៉ាងហោចណាស់ URL មួយ។")
            return
        self.progress.start()
        threading.Thread(target=self.download_multiple_thread, args=(urls,), daemon=True).start()

    def download_multiple_thread(self, urls):
        self.log_status("ចាប់ផ្តើមទាញយកច្រើន...")
        with yt_dlp.YoutubeDL({
            'outtmpl': os.path.join(DOWNLOAD_FOLDER, '%(title)s.%(ext)s'),
            'format': 'bestvideo+bestaudio/best' if is_ffmpeg_installed() else 'best',
            'merge_output_format': 'mp4',
            'noplaylist': True,
        }) as ydl:
            for url in urls:
                try:
                    self.log_status(f"កំពុងទាញយក: {url}")
                    ydl.download([url])
                    self.log_status(f"✅ ទាញយកបានសម្រេច: {url}")
                except Exception as e:
                    self.log_status(f"❌ បរាជ័យ: {url}: {e}")
            self.log_status(f"✅ ទាញយកទាំងអស់បានបញ្ចប់ ➜ រក្សាទុកនៅ '{DOWNLOAD_FOLDER}'")
        self.root.after(0, self.progress.stop)

    def download_channel(self):
        url = self.channel_url_entry.get().strip()
        if not url:
            self.log_status("❌ កំហុស: សូមបញ្ចូល URL ឆានែល ឬបញ្ជីចាក់។")
            return
        self.progress.start()
        threading.Thread(target=self.download_channel_thread, args=(url,), daemon=True).start()

    def download_channel_thread(self, url):
        self.log_status(f"ចាប់ផ្តើមទាញយកឆានែល/បញ្ជីចាក់: {url}")
        with yt_dlp.YoutubeDL({
            'outtmpl': os.path.join(DOWNLOAD_FOLDER, '%(title)s.%(ext)s'),
            'format': 'bestvideo+bestaudio/best' if is_ffmpeg_installed() else 'best',
            'merge_output_format': 'mp4',
            'noplaylist': False,
            'ignoreerrors': True,
        }) as ydl:
            try:
                ydl.download([url])
                self.log_status(f"✅ ទាញយកឆានែល/បញ្ជីចាក់បានសម្រេច: {url} ➜ លှာထုတ်ထားရန် '{DOWNLOAD_FOLDER}'")
            except Exception as e:
                self.log_status(f"❌ ရှာထုတ်မရပါ: {url}: {e}")
            finally:
                self.root.after(0, self.progress.stop)

if __name__ == "__main__":
    root = tk.Tk()
    app = YouTubeDownloaderGUI(root)
    root.mainloop()