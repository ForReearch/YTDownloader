import os
import yt_dlp
import tkinter as tk
from tkinter import messagebox, scrolledtext, font, ttk, filedialog
import threading
import shutil
import sys
import subprocess
import platform

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
        self.root.geometry("700x650")
        self.theme = "light"
        self.set_theme()

        # Initialize download folder as None; prompt on first download
        self.download_folder = self.load_download_folder()

        # Set window icon
        try:
            icon_path = os.path.join(os.path.dirname(__file__), "frog-5.png")
            self.root.iconphoto(True, tk.PhotoImage(file=icon_path))
        except Exception as e:
            self.log_status(f"⚠️ Warning: Could not load icon 'frog-5.png': {e}")

        self.header_frame = tk.Frame(self.root, bg=self.colors['header'], pady=12)
        self.header_frame.pack(fill=tk.X)
        khmer_font = load_khmer_font()
        self.label_font = (khmer_font, 12, "bold")
        self.secondary_font = (khmer_font, 10)
        self.button_font = (khmer_font, 10)
        tk.Label(self.header_frame, text="Frog Downloader (YouTube, Instagram, Facebook) កំណែរទម្រង់ V 1.0", font=self.label_font, fg='white', bg=self.colors['header']).pack()

        container = tk.Frame(self.root, bg=self.colors['bg'])
        container.pack(fill="both", expand=True, padx=20, pady=20)
        self.scrollable_frame = ScrollableFrame(container, bg_color=self.colors['bg'])
        self.scrollable_frame.pack(fill="both", expand=True)
        self.main_frame = self.scrollable_frame.scrollable_frame
        self.main_frame.configure(bg=self.colors['bg'], padx=20, pady=20)

        style = ttk.Style()
        style.configure("TProgressbar", troughcolor=self.colors['bg'], background=self.colors['accent'], thickness=4)
        style.configure("TEntry", fieldbackground=self.colors['card'], padding=5)

        self.root.bind("<MouseWheel>", lambda e: self.scrollable_frame.canvas.yview_scroll(-1 * (e.delta // 120), "units"))
        self.root.bind("<Button-4>", lambda e: self.scrollable_frame.canvas.yview_scroll(-1, "units"))
        self.root.bind("<Button-5>", lambda e: self.scrollable_frame.canvas.yview_scroll(1, "units"))

        # Cookie input for Instagram/Facebook
        cookie_frame = tk.Frame(self.main_frame, bg=self.colors['card'], bd=1, relief=tk.SOLID, padx=15, pady=15)
        cookie_frame.pack(fill=tk.X, pady=8)
        tk.Label(cookie_frame, text="ឯកសារខូគី (សម្រាប់ Instagram/Facebook ឯកជន):", font=self.label_font, fg=self.colors['text'], bg=self.colors['card']).grid(row=0, column=0, columnspan=2, sticky="w")
        tk.Label(cookie_frame, text="បញ្ចូលផ្លូវទៅកាន់ឯកសារខូគី (ឧ. cookies.txt):", font=self.secondary_font, fg=self.colors['text2'], bg=self.colors['card']).grid(row=1, column=0, sticky="w", pady=5)
        self.cookie_entry = ttk.Entry(cookie_frame, width=50)
        self.cookie_entry.grid(row=2, column=0, padx=5, pady=5, sticky="ew")
        tk.Label(cookie_frame, text="ចំណាំ: នាំចេញខូគីពីកម្មវិធីរុករកសម្រាប់មាតិកាឯកជន។", font=self.secondary_font, fg=self.colors['text2'], bg=self.colors['card']).grid(row=3, column=0, columnspan=2, sticky="w")

        # Single video/post/reel
        single_frame = tk.Frame(self.main_frame, bg=self.colors['card'], bd=1, relief=tk.SOLID, padx=15, pady=15)
        single_frame.pack(fill=tk.X, pady=8)
        tk.Label(single_frame, text="ទាញយកវីឌីអូ/ប្រកាស/រៀលតែមួយ (YouTube/Instagram/Facebook)", font=self.label_font, fg=self.colors['text'], bg=self.colors['card']).grid(row=0, column=0, columnspan=2, sticky="w")
        tk.Label(single_frame, text="បញ្ចូល URL:", font=self.secondary_font, fg=self.colors['text2'], bg=self.colors['card']).grid(row=1, column=0, sticky="w", pady=5)
        self.single_url_entry = ttk.Entry(single_frame, width=50)
        self.single_url_entry.grid(row=2, column=0, padx=5, pady=5, sticky="ew")
        tk.Button(single_frame, text="ទាញយកមួយ", font=self.button_font, bg=self.colors['accent'], fg='white', activebackground=self.colors['accent_active'], relief="flat", command=self.download_single).grid(row=2, column=1, padx=5)

        # Multiple videos/posts/reels
        multi_frame = tk.Frame(self.main_frame, bg=self.colors['card'], bd=1, relief=tk.SOLID, padx=15, pady=15)
        multi_frame.pack(fill=tk.X, pady=8)
        tk.Label(multi_frame, text="ទាញយកវីឌីអូ/ប្រកាស/រៀលច្រើន", font=self.label_font, fg=self.colors['text'], bg=self.colors['card']).grid(row=0, column=0, columnspan=2, sticky="w")
        tk.Label(multi_frame, text="បញ្ចូល URLs (មួយក្នុងមួយបន្ទាត់):", font=self.secondary_font, fg=self.colors['text2'], bg=self.colors['card']).grid(row=1, column=0, sticky="w", pady=5)
        self.multi_url_text = scrolledtext.ScrolledText(multi_frame, width=50, height=5, font=self.secondary_font, bg=self.colors['card'], fg=self.colors['text'])
        self.multi_url_text.grid(row=2, column=0, padx=5, pady=5, sticky="ew")
        tk.Button(multi_frame, text="ទាញយកច្រើន", font=self.button_font, bg=self.colors['accent'], fg='white', activebackground=self.colors['accent_active'], relief="flat", command=self.download_multiple).grid(row=2, column=1, padx=5)

        # Channel/Playlist/Profile/Page
        channel_frame = tk.Frame(self.main_frame, bg=self.colors['card'], bd=1, relief=tk.SOLID, padx=15, pady=15)
        channel_frame.pack(fill=tk.X, pady=8)
        tk.Label(channel_frame, text="ទាញយកឆានែល/បញ្ជីចាក់/ប្រវត្តិរូប/ទំព័រ", font=self.label_font, fg=self.colors['text'], bg=self.colors['card']).grid(row=0, column=0, columnspan=2, sticky="w")
        tk.Label(channel_frame, text="បញ្ចូល URL ឆានែល/បញ្ជីចាក់/ប្រវត្តិរូប/ទំព័រ:", font=self.secondary_font, fg=self.colors['text2'], bg=self.colors['card']).grid(row=1, column=0, sticky="w", pady=5)
        self.channel_url_entry = ttk.Entry(channel_frame, width=50)
        self.channel_url_entry.grid(row=2, column=0, padx=5, pady=5, sticky="ew")
        tk.Button(channel_frame, text="ទាញយកឆានែល/បញ្ជីចាក់/ប្រវត្តិរូប/ទំព័រ", font=self.button_font, bg=self.colors['accent'], fg='white', activebackground=self.colors['accent_active'], relief="flat", command=self.download_channel).grid(row=2, column=1, padx=5)

        # Status frame
        status_frame = tk.Frame(self.main_frame, bg=self.colors['card'], bd=1, relief=tk.SOLID, padx=15, pady=15)
        status_frame.pack(fill=tk.X, pady=8)
        tk.Label(status_frame, text="ស្ថានភាព:", font=self.label_font, fg=self.colors['text'], bg=self.colors['card']).pack(anchor="w")
        self.status_text = scrolledtext.ScrolledText(status_frame, width=60, height=8, state='disabled', font=self.secondary_font, bg=self.colors['card'], fg=self.colors['text'])
        self.status_text.pack(pady=5, fill=tk.X)
        self.progress = ttk.Progressbar(status_frame, mode='indeterminate')
        self.progress.pack(fill=tk.X, pady=5)

        # Footer
        footer_frame = tk.Frame(self.root, bg=self.colors['bg'], pady=12)
        footer_frame.pack(fill=tk.X, side=tk.BOTTOM)
        tk.Button(footer_frame, text="ចាកចេញ", font=self.button_font, bg=self.colors['accent'], fg='white', activebackground=self.colors['accent_active'], relief="flat", command=self.root.quit).pack(side=tk.LEFT, padx=5)
        tk.Button(footer_frame, text="រក្សាទុក", font=self.button_font, bg=self.colors['accent'], fg='white', activebackground=self.colors['accent_active'], relief="flat", command=self.set_download_folder).pack(side=tk.LEFT, padx=5)
        tk.Button(footer_frame, text="បើក", font=self.button_font, bg=self.colors['accent'], fg='white', activebackground=self.colors['accent_active'], relief="flat", command=self.open_download_folder).pack(side=tk.LEFT, padx=5)
        self.theme_button = tk.Button(footer_frame, text="Dark Theme", font=self.button_font, bg=self.colors['accent'], fg='white', activebackground=self.colors['accent_active'], relief="flat", command=self.toggle_theme)
        self.theme_button.pack(side=tk.LEFT, padx=5)

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
        # Create a dialog window for folder selection
        dialog = tk.Toplevel(self.root)
        dialog.title("រក្សាទុកនៅកន្លែងណា?")
        dialog.geometry("400x200")
        dialog.transient(self.root)
        dialog.grab_set()
        dialog.configure(bg=self.colors['bg'])

        tk.Label(dialog, text="ជ្រើសរើសទីតាំងរក្សាទុកសម្រាប់ទាញយក", font=self.label_font, fg=self.colors['text'], bg=self.colors['bg']).pack(pady=10)
        folder_var = tk.StringVar()
        entry = ttk.Entry(dialog, textvariable=folder_var, width=40)
        entry.pack(pady=5, padx=10, fill=tk.X)

        def browse_folder():
            folder = filedialog.askdirectory(title="ជ្រើសរើសទីតាំងរក្សាទុក")
            if folder:
                folder_var.set(folder)

        tk.Button(dialog, text="រុករក", font=self.button_font, bg=self.colors['accent'], fg='white', activebackground=self.colors['accent_active'], command=browse_folder).pack(pady=5)
        
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

        tk.Button(dialog, text="រក្សាទុក", font=self.button_font, bg=self.colors['accent'], fg='white', activebackground=self.colors['accent_active'], command=confirm).pack(pady=10)
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
                elif system == "Darwin":  # macOS
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
                    widget.configure(bg=self.colors['card'], fg=self.colors['text'] if str(widget.cget("font")).startswith(str(self.label_font[0])) else self.colors['text2'])
                elif isinstance(widget, scrolledtext.ScrolledText):
                    widget.configure(bg=self.colors['card'], fg=self.colors['text'])
                elif isinstance(widget, tk.Button):
                    widget.configure(bg=self.colors['accent'], fg='white', activebackground=self.colors['accent_active'])
                elif isinstance(widget, ttk.Entry):
                    widget.configure(style="TEntry")
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

    def get_ydl_opts(self):
        opts = {
            'outtmpl': os.path.join(self.download_folder, '%(title)s.%(ext)s'),
            'format': 'bestvideo+bestaudio/best' if is_ffmpeg_installed() else 'best',
            'merge_output_format': 'mp4',
            'noplaylist': True,
            'ignoreerrors': True,
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
                self.log_status(f"✅ ទាញយកបានសម្រេច: {url} ➖ រក្សាទុកនៅ '{self.download_folder}'")
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
                self.log_status(f"✅ ទាញយកឆានែល/បញ្ជីចាក់/ប្រវត្តិរូប/ទំព័របានសម្រេច: {url} ➖ រក្សាទុកនៅ '{self.download_folder}'")
            except Exception as e:
                self.log_status(f"❌ បរាជ័យ: {e}")
            finally:
                self.root.after(0, self.progress.stop)

if __name__ == "__main__":
    root = tk.Tk()
    app = MediaDownloaderGUI(root)
    root.mainloop()