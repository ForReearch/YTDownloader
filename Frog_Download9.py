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
        return "Khmer OS"

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
        self.root.geometry("900x750")
        self.theme = "light"
        ctk.set_appearance_mode("light")
        self.set_theme()

        self.download_folder = self.load_download_folder()

        '''
        try:
            
            icon_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "frog-5.png"))
            if os.path.exists(icon_path):
                icon = tk.PhotoImage(file=icon_path)
                self.root.iconphoto(True, icon)
                print(f"Successfully loaded icon: {icon_path}")
            else:
                self.log_status(f"⚠️ Warning: Icon file 'frog-5.png' not found at {icon_path}")
        except Exception as e:
            self.log_status(f"⚠️ Warning: Could not load icon 'frog-5.png': {e}") '''
            
        try:
            script_dir = os.path.dirname(os.path.abspath(__file__))
            icon_path = os.path.join(script_dir, "frog-5.png")
            if os.path.exists(icon_path):
                # For customtkinter, use iconbitmap for Windows or fallback to PhotoImage
                if sys.platform.startswith('win'):
                    self.root.iconbitmap(icon_path)  # Use iconbitmap for PNG on Windows
                else:
                    icon = tk.PhotoImage(file=icon_path)
                    self.root.iconphoto(True, icon)  # Fallback for other platforms
                print(f"Successfully loaded icon: {icon_path}")
            else:
                self.log_status(f"⚠️ Warning: Icon file 'frog-5.png' not found at {icon_path}. Place it in: {script_dir}")
        except Exception as e:
            self.log_status(f"⚠️ Warning: Failed to load icon 'frog-5.png': {str(e)}")   
            
             
            

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
            "corner_radius": 8,
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

        # Platform selection
        platform_frame = tk.Frame(self.main_frame, bg=self.colors['card'], bd=1, relief=tk.SOLID, padx=15, pady=15)
        platform_frame.pack(fill=tk.X, pady=10)
        ctk.CTkLabel(platform_frame, text="Platform:", font=self.label_font, text_color=self.colors['text']).pack(side=tk.LEFT)
        self.platform_var = tk.StringVar(value='auto')
        platforms = [('Auto-detect', 'auto'), ('YouTube', 'youtube'), ('Instagram', 'instagram'), ('Facebook', 'facebook')]
        for text, mode in platforms:
            ctk.CTkRadioButton(platform_frame, text=text, variable=self.platform_var, value=mode, font=self.secondary_font, text_color=self.colors['text2']).pack(side=tk.LEFT, padx=5)

        # Cookie input
        cookie_frame = tk.Frame(self.main_frame, bg=self.colors['card'], bd=1, relief=tk.SOLID, padx=15, pady=15)
        cookie_frame.pack(fill=tk.X, pady=10)
        ctk.CTkLabel(cookie_frame, text="ឯកសារខូគី (សម្រាប់ Instagram/Facebook ឯកជន):", font=self.label_font, text_color=self.colors['text']).pack(anchor='w')
        self.cookie_entry = ctk.CTkEntry(cookie_frame, width=450, fg_color=self.colors['card'], text_color=self.colors['text'], corner_radius=10, font=self.secondary_font)
        self.cookie_entry.pack(fill=tk.X, pady=5)
        ctk.CTkButton(cookie_frame, text="Browse", command=self.browse_cookie_file, **self.button_style).pack(pady=5)

        # Single video/post/reel
        single_frame = tk.Frame(self.main_frame, bg=self.colors['card'], bd=1, relief=tk.SOLID, padx=15, pady=15)
        single_frame.pack(fill=tk.X, pady=10)
        ctk.CTkLabel(single_frame, text="ទាញយកវីឌីអូ/ប្រកាស/រៀលតែមួយ", font=self.label_font, text_color=self.colors['text']).pack(anchor='w')
        self.single_url_entry = ctk.CTkEntry(single_frame, width=450, fg_color=self.colors['card'], text_color=self.colors['text'], corner_radius=10, font=self.secondary_font)
        self.single_url_entry.pack(fill=tk.X, pady=5)

        # Multiple videos/posts/reels
        multi_frame = tk.Frame(self.main_frame, bg=self.colors['card'], bd=1, relief=tk.SOLID, padx=15, pady=15)
        multi_frame.pack(fill=tk.X, pady=10)
        ctk.CTkLabel(multi_frame, text="ទាញយកវីឌីអូ/ប្រកាស/រៀលច្រើន", font=self.label_font, text_color=self.colors['text']).pack(anchor='w')
        self.multi_url_text = scrolledtext.ScrolledText(multi_frame, width=50, height=6, font=self.secondary_font, bg=self.colors['card'], fg=self.colors['text'])
        self.multi_url_text.pack(fill=tk.X, pady=5)

        # Channel/Playlist/Profile/Page
        channel_frame = tk.Frame(self.main_frame, bg=self.colors['card'], bd=1, relief=tk.SOLID, padx=15, pady=15)
        channel_frame.pack(fill=tk.X, pady=10)
        ctk.CTkLabel(channel_frame, text="ទាញយកឆានែល/បញ្ជីចាក់/ប្រវត្តិរូប/ទំព័រ", font=self.label_font, text_color=self.colors['text']).pack(anchor='w')
        self.channel_url_entry = ctk.CTkEntry(channel_frame, width=450, fg_color=self.colors['card'], text_color=self.colors['text'], corner_radius=10, font=self.secondary_font)
        self.channel_url_entry.pack(fill=tk.X, pady=5)

        # Download type
        type_frame = tk.Frame(self.main_frame, bg=self.colors['card'], bd=1, relief=tk.SOLID, padx=15, pady=15)
        type_frame.pack(fill=tk.X, pady=10)
        ctk.CTkLabel(type_frame, text="Download Type:", font=self.label_font, text_color=self.colors['text']).pack(anchor='w')
        self.dl_type_var = tk.StringVar(value='video')
        ctk.CTkRadioButton(type_frame, text="Video", variable=self.dl_type_var, value='video', font=self.secondary_font, text_color=self.colors['text2']).pack(side=tk.LEFT, padx=5)
        ctk.CTkRadioButton(type_frame, text="Audio Only", variable=self.dl_type_var, value='audio', font=self.secondary_font, text_color=self.colors['text2']).pack(side=tk.LEFT, padx=5)

        # Save location
        location_frame = tk.Frame(self.main_frame, bg=self.colors['card'], bd=1, relief=tk.SOLID, padx=15, pady=15)
        location_frame.pack(fill=tk.X, pady=10)
        ctk.CTkLabel(location_frame, text="Save to:", font=self.secondary_font, text_color=self.colors['text']).pack(side=tk.LEFT)
        self.location_entry = ctk.CTkEntry(location_frame, width=450, fg_color=self.colors['card'], text_color=self.colors['text'], corner_radius=10, font=self.secondary_font)
        self.location_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        self.location_entry.insert(0, os.path.expanduser("~/Downloads"))
        ctk.CTkButton(location_frame, text="រក្សាទុក", command=self.browse_location, **self.button_style).pack(side=tk.LEFT)

        # Single Download Button
        btn_frame = tk.Frame(self.main_frame, bg=self.colors['card'], bd=1, relief=tk.SOLID, padx=15, pady=15)
        btn_frame.pack(fill=tk.X, pady=10)
        ctk.CTkButton(btn_frame, text="Download", command=self.download_all, fg_color='#4CAF50', hover_color='#45a049', text_color="white", font=self.button_font, corner_radius=8, height=48, width=200).pack(pady=5)

        # Status frame
        status_frame = tk.Frame(self.main_frame, bg=self.colors['card'], bd=1, relief=tk.SOLID, padx=15, pady=15)
        status_frame.pack(fill=tk.X, pady=10)
        ctk.CTkLabel(status_frame, text="ស្ថានភាព:", font=self.label_font, text_color=self.colors['text']).pack(anchor='w')
        self.status_text = scrolledtext.ScrolledText(status_frame, width=60, height=8, state='disabled', font=self.secondary_font, bg=self.colors['card'], fg=self.colors['text'])
        self.status_text.pack(pady=5, fill=tk.X)
        self.progress = ttk.Progressbar(status_frame, mode='determinate')
        self.progress.pack(fill=tk.X, pady=5)

        # Footer
        footer_frame = tk.Frame(self.root, bg=self.colors['bg'], pady=15)
        footer_frame.pack(fill=tk.X, side=tk.BOTTOM)
        ctk.CTkButton(footer_frame, text="ចាកចេញ", command=self.root.quit, **self.button_style).pack(side=tk.LEFT, padx=5, pady=5)
        ctk.CTkButton(footer_frame, text="បើក", command=self.open_download_folder, **self.button_style).pack(side=tk.LEFT, padx=5, pady=5)
        self.theme_button = ctk.CTkButton(footer_frame, text="Dark Theme", command=self.toggle_theme, **self.button_style)
        self.theme_button.pack(side=tk.LEFT, padx=5, pady=5)

        ffmpeg_status = "ffmpeg ត្រូវបានរកឃើញ។ ប្រើគុណភាពល្អបំផុត។" if is_ffmpeg_installed() else "ffmpeg មិនត្រូវបានរកឃើញ។ ប្រើស្ទ្រីមតែមួយ (គុណភាពទាបជាង)។ ដំឡើង ffmpeg សម្រាប់គុណភាពល្អបំផុត១"
        self.log_status(f"ព័ត៌មាន: {ffmpeg_status}")
        self.log_status("ចំណាំ: សម្រាប់ Instagram/Facebook មាតិកាឯកជន សូមបញ្ចូលឯកសារខូគី។ នាំចេញខូគីពីកម្មវិធីរុករក។")

    def browse_location(self):
        folder = filedialog.askdirectory()
        if folder:
            self.location_entry.delete(0, tk.END)
            self.location_entry.insert(0, folder)
            self.download_folder = folder
            os.makedirs(self.download_folder, exist_ok=True)
            self.save_download_folder()
            self.log_status(f"ទីតាំងរក្សាទុកបានផ្លាស់ប្តូរ: {self.download_folder}")

    def browse_cookie_file(self):
        file = filedialog.askopenfilename(title="Select cookies file", filetypes=[("Text files", "*.txt"), ("All files", "*.*")])
        if file:
            self.cookie_entry.delete(0, tk.END)
            self.cookie_entry.insert(0, file)

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

    def prompt_for_download_folder(self):
        if self.download_folder and os.path.isdir(self.download_folder):
            return True
        folder = filedialog.askdirectory(title="ជ្រើសរើសទីតាំងរក្សាទុក")
        if folder:
            self.download_folder = folder
            os.makedirs(self.download_folder, exist_ok=True)
            self.save_download_folder()
            self.log_status(f"ទីតាំងរក្សាទុកបានផ្លាស់ប្តូរ: {self.download_folder}")
            return True
        return False

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
                    widget.configure(fg_color=self.colors['accent'], hover_color=self.colors['accent_active'], text_color="white", text_color_disabled="#606770", corner_radius=8)
                elif isinstance(widget, ctk.CTkEntry):
                    widget.configure(fg_color=self.colors['card'], text_color=self.colors['text'])
                elif isinstance(widget, ctk.CTkRadioButton):
                    widget.configure(text_color=self.colors['text2'])
        footer_frame = self.root.winfo_children()[-1]
        footer_frame.configure(bg=self.colors['bg'])
        for widget in footer_frame.winfo_children():
            if isinstance(widget, ctk.CTkButton):
                widget.configure(fg_color=self.colors['accent'], hover_color=self.colors['accent_active'], text_color="white", text_color_disabled="#606770", corner_radius=8)
        dialog_frames = [w for w in self.root.winfo_children() if isinstance(w, ctk.CTkToplevel)]
        for dialog in dialog_frames:
            dialog.configure(fg_color=self.colors['bg'])
            for widget in dialog.winfo_children():
                if isinstance(widget, ctk.CTkLabel):
                    widget.configure(fg_color=self.colors['bg'], text_color=self.colors['text'])
                elif isinstance(widget, ctk.CTkEntry):
                    widget.configure(fg_color=self.colors['card'], text_color=self.colors['text'])
                elif isinstance(widget, ctk.CTkButton):
                    widget.configure(fg_color=self.colors['accent'], hover_color=self.colors['accent_active'], text_color="white", text_color_disabled="#606770", corner_radius=8)
        style = ttk.Style()
        style.configure("TProgressbar", troughcolor=self.colors['bg'], background=self.colors['accent'])

    def log_status(self, message):
        self.status_text.config(state='normal')
        self.status_text.insert(tk.END, f"{message}\n")
        self.status_text.see(tk.END)
        self.status_text.config(state='disabled')

    def get_ydl_opts(self, url):
        download_path = self.location_entry.get().strip() or self.download_folder or os.path.expanduser("~/Downloads")
        os.makedirs(download_path, exist_ok=True)

        platform = self.platform_var.get()
        if platform == 'auto':
            url_lower = url.lower()
            if 'youtube.com' in url_lower or 'youtu.be' in url_lower:
                platform = 'youtube'
            elif 'instagram.com' in url_lower:
                platform = 'instagram'
            elif 'facebook.com' in url_lower:
                platform = 'facebook'

        opts = {
            'outtmpl': os.path.join(download_path, '%(title)s.%(ext)s'),
            'progress_hooks': [self.progress_hook],
            'quiet': False,  # Enable verbose output for debugging
            'no_warnings': False,
            'ignoreerrors': True,  # Ignore errors to continue downloading
            'retries': 10,  # Retry on network errors
            'fragment_retries': 10,  # Retry on fragment download errors
            'extractor_retries': 10,  # Retry on extractor errors
            'http_headers': {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
                'DNT': '1',
                'Connection': 'keep-alive',
            }
        }

        if platform == 'youtube':
            opts['referer'] = 'https://www.youtube.com/'
            if self.dl_type_var.get() == 'audio':
                opts['format'] = 'bestaudio/best'
                if is_ffmpeg_installed():
                    opts['postprocessors'] = [{
                        'key': 'FFmpegExtractAudio',
                        'preferredcodec': 'mp3',
                        'preferredquality': '192',
                    }]
                else:
                    self.log_status("⚠️ Warning: ffmpeg not found. Audio will be downloaded as is.")
            else:
                opts['format'] = 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best' if is_ffmpeg_installed() else 'best[ext=mp4]'
                if is_ffmpeg_installed():
                    opts['postprocessors'] = [{
                        'key': 'FFmpegVideoRemuxer',
                        'preferedformat': 'mp4'
                    }]

        elif platform == 'instagram':
            opts['referer'] = 'https://www.instagram.com/'
            if self.dl_type_var.get() == 'audio':
                opts['format'] = 'bestaudio/best'
                if is_ffmpeg_installed():
                    opts['postprocessors'] = [{
                        'key': 'FFmpegExtractAudio',
                        'preferredcodec': 'mp3',
                        'preferredquality': '192',
                    }]
                else:
                    self.log_status("⚠️ Warning: ffmpeg not found. Audio will be downloaded as is.")
            else:
                opts['format'] = 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best' if is_ffmpeg_installed() else 'best[ext=mp4]'
                if is_ffmpeg_installed():
                    opts['postprocessors'] = [{
                        'key': 'FFmpegVideoRemuxer',
                        'preferedformat': 'mp4'
                    }]

        elif platform == 'facebook':
            opts['referer'] = 'https://www.facebook.com/'
            if self.dl_type_var.get() == 'audio':
                opts['format'] = 'bestaudio/best'
                if is_ffmpeg_installed():
                    opts['postprocessors'] = [{
                        'key': 'FFmpegExtractAudio',
                        'preferredcodec': 'mp3',
                        'preferredquality': '192',
                    }]
                else:
                    self.log_status("⚠️ Warning: ffmpeg not found. Audio will be downloaded as is.")
            else:
                opts['format'] = 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best' if is_ffmpeg_installed() else 'best[ext=mp4]'
                if is_ffmpeg_installed():
                    opts['postprocessors'] = [{
                        'key': 'FFmpegVideoRemuxer',
                        'preferedformat': 'mp4'
                    }]

        cookie_file = self.cookie_entry.get().strip()
        if cookie_file and os.path.exists(cookie_file):
            opts['cookiefile'] = cookie_file
            self.log_status(f"Using cookies from: {cookie_file}")

        # Handle playlists/channels
        if self.channel_url_entry.get().strip() == url:
            opts['noplaylist'] = False
        else:
            opts['noplaylist'] = True

        return opts

    def progress_hook(self, d):
        if d['status'] == 'downloading':
            total = d.get('total_bytes') or d.get('total_bytes_estimate', 0)
            if total:
                percent = (d['downloaded_bytes'] / total) * 100
                self.progress['value'] = percent
                self.root.update()
            else:
                self.progress['value'] = 50  # Fallback for indeterminate progress
        elif d['status'] == 'finished':
            self.log_status("✅ ទាញយកបានសម្រេច!")
            self.progress['value'] = 100
        elif d['status'] == 'error':
            self.log_status(f"❌ Error during download: {d.get('error', 'Unknown error')}")

    def download_all(self):
        single_url = self.single_url_entry.get().strip()
        multi_urls = self.multi_url_text.get("1.0", tk.END).strip().splitlines()
        multi_urls = [u.strip() for u in multi_urls if u.strip()]
        channel_url = self.channel_url_entry.get().strip()
        urls = []

        if single_url:
            urls.append(single_url)
        if multi_urls:
            urls.extend(multi_urls)
        if channel_url:
            urls.append(channel_url)

        if not urls:
            self.log_status("❌ កំហុស: សូមបញ្ចូល URL យ៉ាងហោចណាស់មួយ។")
            return
        if not self.prompt_for_download_folder():
            self.log_status("❌ កំហុស: មិនបានជ្រើសរើសទីតាំងរក្សាទុក។")
            return
        self.progress['value'] = 0
        self.progress['maximum'] = len(urls)
        threading.Thread(target=self._download, args=(urls, True), daemon=True).start()

    def _download(self, urls, is_multiple):
        try:
            for i, url in enumerate(urls, 1):
                opts = self.get_ydl_opts(url)
                with yt_dlp.YoutubeDL(opts) as ydl:
                    self.log_status(f"កំពុងទាញយក ({i}/{len(urls)}): {url}")
                    try:
                        ydl.download([url])
                        self.log_status(f"✅ ទាញយកបានសម្រេច: {url}")
                    except Exception as e:
                        self.log_status(f"❌ បរាជ័យ: {url}: {str(e)}")
                    if is_multiple:
                        self.progress['value'] = (i / len(urls)) * 100
                        self.root.update()
        except Exception as e:
            self.log_status(f"❌ បរាជ័យ: {str(e)}")
        finally:
            self.progress['value'] = 0

if __name__ == "__main__":
    root = ctk.CTk()
    app = MediaDownloaderGUI(root)
    root.mainloop()