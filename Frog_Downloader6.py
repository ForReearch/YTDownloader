import os
import yt_dlp
import tkinter as tk
from tkinter import messagebox, scrolledtext, font, ttk, filedialog
import threading
import shutil
import sys
import subprocess
import platform
import customtkinter as ctk

CONFIG_FILE = "config.txt"

def is_ffmpeg_installed():
    result = shutil.which("ffmpeg") is not None
    print(f"ffmpeg detected: {result}")
    return result

def load_khmer_font():
    font_name = "Khmer OS Siemreap"
    available_fonts = font.families()
    if font_name in available_fonts:
        print(f"Successfully found font '{font_name}' in system fonts")
        return font_name
    else:
        print(f"Warning: Font '{font_name}' not found in system fonts. Available fonts: {available_fonts}")
        return "Khmer OS"  # Fallback to another Khmer font or default

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

class MediaDownloaderGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Frog Downloader v1.0")
        self.root.geometry("800x800")
        self.theme = "light"
        ctk.set_appearance_mode("light")
        self.set_theme()

        self.download_folder = self.load_download_folder()

        # Set window icon with improved error handling
        try:
            icon_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "frog-5.png"))
            if os.path.exists(icon_path):
                icon = tk.PhotoImage(file=icon_path)
                self.root.iconphoto(True, icon)
                print(f"Successfully loaded icon: {icon_path}")
            else:
                self.log_status(f"⚠️ Warning: Icon file 'frog-5.png' not found at {icon_path}")
        except Exception as e:
            self.log_status(f"⚠️ Warning: Could not load icon 'frog-5.png': {e}")

        self.header_frame = tk.Frame(self.root, bg=self.colors['header'], pady=15)
        self.header_frame.pack(fill=tk.X)
        khmer_font = load_khmer_font()
        self.label_font = (khmer_font, 16, "bold")
        self.secondary_font = (khmer_font, 14)
        self.button_font = (khmer_font, 14)
        tk.Label(self.header_frame, text="Frog Downloader (YouTube, Instagram, Facebook) កំណែរទម្រង់ V 1.0", font=self.label_font, fg='white', bg=self.colors['header']).pack()

        container = tk.Frame(self.root, bg=self.colors['bg'])
        container.pack(fill="both", expand=True, padx=20, pady=20)
        self.scrollable_frame = ScrollableFrame(container, bg_color=self.colors['bg'])
        self.scrollable_frame.pack(fill="both", expand=True)
        self.main_frame = self.scrollable_frame.scrollable_frame
        self.main_frame.configure(bg=self.colors['bg'], padx=20, pady=20)

        self.button_style = {
            "fg_color": self.colors['accent'],
            "hover_color": self.colors['accent_active'],
            "text_color": "white",
            "text_color_disabled": "#606770",
            "font": self.button_font,
            "corner_radius": 0,  # Ensure sharp corners
            "border_width": 0,
            "height": 48,
            "width": 200
        }

        style = ttk.Style()
        style.theme_use('clam')
        style.configure("TProgressbar", troughcolor=self.colors['bg'], background=self.colors['accent'], thickness=6)
        style.configure("TEntry", fieldbackground=self.colors['card'], padding=6)

        self.root.bind("<MouseWheel>", lambda e: self.scrollable_frame.canvas.yview_scroll(-1 * (e.delta // 120), "units"))
        self.root.bind("<Button-4>", lambda e: self.scrollable_frame.canvas.yview_scroll(-1, "units"))
        self.root.bind("<Button-5>", lambda e: self.scrollable_frame.canvas.yview_scroll(1, "units"))

        # Cookie input
        cookie_frame = tk.Frame(self.main_frame, bg=self.colors['card'], bd=1, relief=tk.SOLID, padx=15, pady=15)
        cookie_frame.pack(fill=tk.X, pady=10)
        ctk.CTkLabel(cookie_frame, text="ឯកសារខូគី (សម្រាប់ Instagram/Facebook ឯកជន):", font=self.label_font, text_color=self.colors['text']).grid(row=0, column=0, columnspan=2, sticky="w")
        ctk.CTkLabel(cookie_frame, text="បញ្ចូលផ្លូវទៅកាន់ឯកសារខូគី (ឧ. cookies.txt):", font=self.secondary_font, text_color=self.colors['text2']).grid(row=1, column=0, sticky="w", pady=5)
        self.cookie_entry = ctk.CTkEntry(cookie_frame, width=450, fg_color=self.colors['card'], text_color=self.colors['text'], corner_radius=10, font=self.secondary_font)
        self.cookie_entry.grid(row=2, column=0, padx=5, pady=5, sticky="ew")
        ctk.CTkLabel(cookie_frame, text="ចំណាំ: នាំចេញខូគីពីកម្មវិធីរុករកសម្រាប់មាតិកាឯកជន។", font=self.secondary_font, text_color=self.colors['text2']).grid(row=3, column=0, columnspan=2, sticky="w")

        # Single video/post/reel
        single_frame = tk.Frame(self.main_frame, bg=self.colors['card'], bd=1, relief=tk.SOLID, padx=15, pady=15)
        single_frame.pack(fill=tk.X, pady=10)
        ctk.CTkLabel(single_frame, text="ទាញយកវីឌីអូ/ប្រកាស/រៀលតែមួយ (YouTube/Instagram/Facebook)", font=self.label_font, text_color=self.colors['text']).grid(row=0, column=0, columnspan=2, sticky="w")
        ctk.CTkLabel(single_frame, text="បញ្ចូល URL:", font=self.secondary_font, text_color=self.colors['text2']).grid(row=1, column=0, sticky="w", pady=5)
        self.single_url_entry = ctk.CTkEntry(single_frame, width=450, fg_color=self.colors['card'], text_color=self.colors['text'], corner_radius=10, font=self.secondary_font)
        self.single_url_entry.grid(row=2, column=0, padx=5, pady=5, sticky="ew")
        ctk.CTkButton(single_frame, text="ទាញយកមួយ", command=self.download_single, **self.button_style).grid(row=2, column=1, padx=5, pady=5)

        # Multiple videos/posts/reels
        multi_frame = tk.Frame(self.main_frame, bg=self.colors['card'], bd=1, relief=tk.SOLID, padx=15, pady=15)
        multi_frame.pack(fill=tk.X, pady=10)
        ctk.CTkLabel(multi_frame, text="ទាញយកវីឌីអូ/ប្រកាស/រៀលច្រើន", font=self.label_font, text_color=self.colors['text']).grid(row=0, column=0, columnspan=2, sticky="w")
        ctk.CTkLabel(multi_frame, text="បញ្ចូល URLs (មួយក្នុងមួយបន្ទាត់):", font=self.secondary_font, text_color=self.colors['text2']).grid(row=1, column=0, sticky="w", pady=5)
        self.multi_url_text = scrolledtext.ScrolledText(multi_frame, width=50, height=6, font=self.secondary_font, bg=self.colors['card'], fg=self.colors['text'])
        self.multi_url_text.grid(row=2, column=0, padx=5, pady=5, sticky="ew")
        ctk.CTkButton(multi_frame, text="ទាញយកច្រើន", command=self.download_multiple, **self.button_style).grid(row=2, column=1, padx=5, pady=5)

        # Channel/Playlist/Profile/Page
        channel_frame = tk.Frame(self.main_frame, bg=self.colors['card'], bd=1, relief=tk.SOLID, padx=15, pady=15)
        channel_frame.pack(fill=tk.X, pady=10)
        ctk.CTkLabel(channel_frame, text="ទាញយកឆានែល/បញ្ជីចាក់/ប្រវត្តិរូប/ទំព័រ", font=self.label_font, text_color=self.colors['text']).grid(row=0, column=0, columnspan=2, sticky="w")
        ctk.CTkLabel(channel_frame, text="បញ្ចូល URL ឆានែល/បញ្ជីចាក់/ប្រវត្តិរូប/ទំព័រ:", font=self.secondary_font, text_color=self.colors['text2']).grid(row=1, column=0, sticky="w", pady=5)
        self.channel_url_entry = ctk.CTkEntry(channel_frame, width=450, fg_color=self.colors['card'], text_color=self.colors['text'], corner_radius=10, font=self.secondary_font)
        self.channel_url_entry.grid(row=2, column=0, padx=5, pady=5, sticky="ew")
        ctk.CTkButton(channel_frame, text="ទាញយកឆានែល/បញ្ជីចាក់/ប្រវត្តិរូប/ទំព័រ", command=self.download_channel, **self.button_style).grid(row=2, column=1, padx=5, pady=5)

        # Status frame
        status_frame = tk.Frame(self.main_frame, bg=self.colors['card'], bd=1, relief=tk.SOLID, padx=15, pady=15)
        status_frame.pack(fill=tk.X, pady=10)
        ctk.CTkLabel(status_frame, text="ស្ថានភាព:", font=self.label_font, text_color=self.colors['text']).pack(anchor="w")
        self.status_text = scrolledtext.ScrolledText(status_frame, width=60, height=8, state='disabled', font=self.secondary_font, bg=self.colors['card'], fg=self.colors['text'])
        self.status_text.pack(pady=5, fill=tk.X)
        self.progress = ttk.Progressbar(status_frame, mode='indeterminate')
        self.progress.pack(fill=tk.X, pady=5)

        # Footer
        footer_frame = tk.Frame(self.root, bg=self.colors['bg'], pady=15)
        footer_frame.pack(fill=tk.X, side=tk.BOTTOM)
        ctk.CTkButton(footer_frame, text="ចាកចេញ", command=self.root.quit, **self.button_style).pack(side=tk.LEFT, padx=5, pady=5)
        ctk.CTkButton(footer_frame, text="រក្សាទុក", command=self.set_download_folder, **self.button_style).pack(side=tk.LEFT, padx=5, pady=5)
        ctk.CTkButton(footer_frame, text="បើក", command=self.open_download_folder, **self.button_style).pack(side=tk.LEFT, padx=5, pady=5)
        self.theme_button = ctk.CTkButton(footer_frame, text="Dark Theme", command=self.toggle_theme, **self.button_style)
        self.theme_button.pack(side=tk.LEFT, padx=5, pady=5)

        ffmpeg_status = "ffmpeg ត្រូវបានរកឃើញ។ ប្រើគុណភាពល្អបំផុត។" if is_ffmpeg_installed() else "ffmpeg មិនត្រូវបានរកឃើញ។ ប្រើស្ទ្រីមតែមួយ (គុណភាពទាបជាង)។ ដំឡើង ffmpeg សម្រាប់គុណភាពល្អបំផុត។"
        self.log_status(f"ព័ត៌មាន: {ffmpeg_status}")
        self.log_status("ចំណាំ: សម្រាប់ Instagram/Facebook មាតិកាឯកជន សូមបញ្ចូលឯកសារខូគី។ នាំចេញខូគីពីកម្មវិធីរុករក។")

    def load_download_folder(self):
        try:
            with open(CONFIG_FILE, 'r') as f:
                folder = f.read().strip()
                if folder and os.path.isdir(folder):
                    return folder
                else:
                    return None
        except Exception:
            return None

    def save_download_folder(self):
        try:
            with open(CONFIG_FILE, 'w') as f:
                f.write(self.download_folder)
        except Exception as e:
            self.log_status(f"⚠️ Warning: Could not save download folder to config: {e}")

    def set_download_folder(self):
        dialog = ctk.CTkToplevel(self.root)
        dialog.title("រក្សាទុកនៅកន្លែងណា?")
        dialog.geometry("500x300")
        dialog.transient(self.root)
        dialog.grab_set()
        dialog.configure(fg_color=self.colors['bg'])
        # Explicitly set font for dialog title (platform-specific handling)
        try:
            if platform.system() == "Windows":
                dialog.option_add("*Font", self.label_font)
            else:
                dialog.wm_title("រក្សាទុកនៅកន្លែងណា?")  # Re-set title to ensure font
        except Exception as e:
            self.log_status(f"⚠️ Warning: Could not set dialog title font: {e}")

        ctk.CTkLabel(dialog, text="ជ្រើសរើសទីតាំងរក្សាទុកសម្រាប់ទាញយក", font=self.label_font, text_color=self.colors['text']).pack(pady=15)
        folder_var = tk.StringVar()
        entry = ctk.CTkEntry(dialog, textvariable=folder_var, width=400, fg_color=self.colors['card'], text_color=self.colors['text'], corner_radius=10, font=self.secondary_font)
        entry.pack(pady=10, padx=10, fill=tk.X)

        def browse_folder():
            folder = filedialog.askdirectory(title="ជ្រើសរើសទីតាំងរក្សាទុក")
            if folder:
                folder_var.set(folder)

        ctk.CTkButton(dialog, text="រុករក", command=browse_folder, **self.button_style).pack(pady=10)
        
        def confirm():
            folder = folder_var.get().strip()
            if folder and os.path.isdir(folder):
                self.download_folder = folder
                os.makedirs(self.download_folder, exist_ok=True)
                self.save_download_folder()
                self.log_status(f"ទីតាំងរក្សាទុកបានផ្លាស់ប្តូរ: {self.download_folder}")
                dialog.destroy()
            else:
                messagebox.showerror("កំហុស", "សូមជ្រើសរើសទីតាំងត្រឹមត្រូវ។", parent=dialog)

        ctk.CTkButton(dialog, text="រក្សាទុក", command=confirm, **self.button_style).pack(pady=10)
        dialog.protocol("WM_DELETE_WINDOW", dialog.destroy)

    def prompt_for_download_folder(self):
        if self.download_folder and os.path.isdir(self.download_folder):
            return True
        self.set_download_folder()
        return self.download_folder and os.path.isdir(self.download_folder)

    def open_download_folder(self):
        if self.download_folder and os.path.isdir(self.download_folder):
            try:
                system = platform.system()
                if system == "Windows":
                    os.startfile(self.download_folder)
                elif system == "Darwin":
                    subprocess.run(["open", self.download_folder])
                elif system == "Linux":
                    subprocess.run(["xdg-open", self.download_folder])
                else:
                    self.log_status(f"❌ កំហុស: ប្រព័ន្ធប្រតិបត្តិការមិនគាំទ្រការបើកថត។")
                    return
                self.log_status(f"✅ បានបើកថត: {self.download_folder}")
            except Exception as e:
                self.log_status(f"❌ កំហុស: មិនអាចបើកថត '{self.download_folder}': {e}")
        else:
            self.log_status("❌ កំហុស: ទីតាំងរក្សាទុកមិនត្រឹមត្រូវ។ សូមកំណត់ទីតាំងជាមុន។")

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
            ctk.set_appearance_mode("light")
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
            ctk.set_appearance_mode("dark")
        self.root.configure(bg=self.colors['bg'])

    def toggle_theme(self):
        self.theme = "dark" if self.theme == "light" else "light"
        self.theme_button.configure(text="Light Theme" if self.theme == "dark" else "Dark Theme")
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
                if isinstance(widget, ctk.CTkLabel):
                    widget.configure(fg_color=self.colors['card'], text_color=self.colors['text'] if str(widget.cget("font")).startswith(str(self.label_font[0])) else self.colors['text2'])
                elif isinstance(widget, scrolledtext.ScrolledText):
                    widget.configure(bg=self.colors['card'], fg=self.colors['text'])
                elif isinstance(widget, ctk.CTkButton):
                    widget.configure(fg_color=self.colors['accent'], hover_color=self.colors['accent_active'], text_color="white", text_color_disabled="#606770", corner_radius=0)
                elif isinstance(widget, ctk.CTkEntry):
                    widget.configure(fg_color=self.colors['card'], text_color=self.colors['text'])
        footer_frame = self.root.winfo_children()[-1]
        footer_frame.configure(bg=self.colors['bg'])
        for widget in footer_frame.winfo_children():
            if isinstance(widget, ctk.CTkButton):
                widget.configure(fg_color=self.colors['accent'], hover_color=self.colors['accent_active'], text_color="white", text_color_disabled="#606770", corner_radius=0)
        dialog_frames = [w for w in self.root.winfo_children() if isinstance(w, ctk.CTkToplevel)]
        for dialog in dialog_frames:
            dialog.configure(fg_color=self.colors['bg'])
            for widget in dialog.winfo_children():
                if isinstance(widget, ctk.CTkLabel):
                    widget.configure(fg_color=self.colors['bg'], text_color=self.colors['text'])
                elif isinstance(widget, ctk.CTkEntry):
                    widget.configure(fg_color=self.colors['card'], text_color=self.colors['text'])
                elif isinstance(widget, ctk.CTkButton):
                    widget.configure(fg_color=self.colors['accent'], hover_color=self.colors['accent_active'], text_color="white", text_color_disabled="#606770", corner_radius=0)
        style = ttk.Style()
        style.configure("TProgressbar", troughcolor=self.colors['bg'], background=self.colors['accent'])

    def log_status(self, message):
        self.status_text.config(state='normal')
        self.status_text.insert(tk.END, f"{message}\n")
        self.status_text.see(tk.END)
        self.status_text.config(state='disabled')

    def get_ydl_opts(self):
        opts = {
            'outtmpl': os.path.join(self.download_folder, '%(title)s.%(ext)s'),
            'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best' if is_ffmpeg_installed() else 'best[ext=mp4]',
            'merge_output_format': 'mp4',
            'noplaylist': True,
            'ignoreerrors': True,
            'postprocessors': [{
                'key': 'FFmpegVideoRemuxer',
                'preferedformat': 'mp4'
            }],
            'http_headers': {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            },
            'retries': 10,
            'fragment_retries': 10,
            'extractor_retries': 10
        }
        cookie_file = self.cookie_entry.get().strip()
        if cookie_file and os.path.exists(cookie_file):
            opts['cookiefile'] = cookie_file
        return opts

    def download_single(self):
        url = self.single_url_entry.get().strip()
        if not url:
            self.log_status("❌ កំហុស: សូមបញ្ចូល URL។")
            return
        if not self.prompt_for_download_folder():
            self.log_status("❌ កំហុស: មិនបានជ្រើសរើសទីតាំងរក្សាទុក។")
            return
        self.progress.start()
        threading.Thread(target=self.download_single_thread, args=(url,), daemon=True).start()

    def download_single_thread(self, url):
        self.log_status(f"កំពុងទាញយក: {url}")
        with yt_dlp.YoutubeDL(self.get_ydl_opts()) as ydl:
            try:
                ydl.download([url])
                self.log_status(f"✅ ទាញយកបានសម្រេច: {url} ➖ លှာထားရာ '{self.download_folder}'")
            except Exception as e:
                self.log_status(f"❌ បរាជ័យ: {e}")
            finally:
                self.root.after(0, self.progress.stop)

    def download_multiple(self):
        urls = self.multi_url_text.get("1.0", tk.END).strip().splitlines()
        urls = [url.strip() for url in urls if url.strip()]
        if not urls:
            self.log_status("❌ Error: Please enter at least one URL.")
            return
        if not self.prompt_for_download_folder():
            self.log_status("❌ Error: No valid save location selected.")
            return
        self.progress.start()
        threading.Thread(target=self.download_multiple_thread, args=(urls,), daemon=True).start()

    def download_multiple_thread(self, urls):
        self.log_status("ចាប់ផ្តើមទាញយកច្រើន...")
        with yt_dlp.YoutubeDL(self.get_ydl_opts()) as ydl:
            for url in urls:
                try:
                    self.log_status(f"កំពុងទាញយក: {url}")
                    ydl.download([url])
                    self.log_status(f"✅ ទាញយកបានសម្រេច: {url}")
                except Exception as e:
                    self.log_status(f"❌ បរាជ័យ: {url}: {e}")
            self.log_status(f"✅ ទាញយកទាំងអស់បានបញ្ចប់ ➖ នៅ '{self.download_folder}'")
        self.root.after(0, self.progress.stop)

    def download_channel(self):
        url = self.channel_url_entry.get().strip()
        if not url:
            self.log_status("❌ កំហុស: សូមបញ្ចូល URL ឆានែល/បញ្ជីចាក់/ប្រវត្តិរូប/ទំព័រ។")
            return
        if not self.prompt_for_download_folder():
            self.log_status("❌ កំហុស: មិនបានជ្រើសរើសទីតាំងរក្សាទុក។")
            return
        self.progress.start()
        threading.Thread(target=self.download_channel_thread, args=(url,), daemon=True).start()

    def download_channel_thread(self, url):
        self.log_status(f"ចាប់ផ្តើមទាញយកឆានែល/បញ្ជីចាក់/ប្រវត្តិរូប/ទំព័រ: {url}")
        opts = self.get_ydl_opts()
        opts['noplaylist'] = False
        with yt_dlp.YoutubeDL(opts) as ydl:
            try:
                ydl.download([url])
                self.log_status(f"✅ ទាញយកឆានែល/បញ្ជីចាក់/ប្រវត្តិរូប/ទំព័របានសម្រេច: {url} ➖ លှာထားရာ '{self.download_folder}'")
            except Exception as e:
                self.log_status(f"❌ បរាជ័យ: {e}")
            finally:
                self.root.after(0, self.progress.stop)

if __name__ == "__main__":
    root = ctk.CTk()
    app = MediaDownloaderGUI(root)
    root.mainloop()