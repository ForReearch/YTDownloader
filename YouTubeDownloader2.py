import os
import yt_dlp
import tkinter as tk
from tkinter import messagebox, scrolledtext, font
import threading
import shutil

# Define the download folder
DOWNLOAD_FOLDER = "Video Downloaded"
os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)


# Check if ffmpeg is installed
def is_ffmpeg_installed():
    return shutil.which("ffmpeg") is not None


# Load Khmer font dynamically if not installed
def load_khmer_font():
    font_path = os.path.join(os.path.dirname(__file__), "KhmerOS_siemreap.ttf")
    if os.path.exists(font_path):
        try:
            font.Font(family="Khmer OS Siemreap Custom", size=12, weight="bold", file=font_path)
            font.Font(family="Khmer OS Siemreap Custom", size=10, file=font_path)
            return "Khmer OS Siemreap Custom"
        except Exception as e:
            print(f"Warning: Could not load KhmerOS_siemreap.ttf: {e}")
            return "Khmer OS Siemreap"  # Try system-installed font
    return "Khmer OS Siemreap"  # Fallback to system-installed font


# Common yt-dlp options
YDL_OPTS = {
    'outtmpl': os.path.join(DOWNLOAD_FOLDER, '%(uploader)s/%(title)s.%(ext)s'),
    'format': 'bestvideo+bestaudio/best' if is_ffmpeg_installed() else 'best',
    'merge_output_format': 'mp4',
    'noplaylist': True,
}

# Options for channel/playlist download
YDL_OPTS_CHANNEL = {
    'outtmpl': os.path.join(DOWNLOAD_FOLDER, '%(uploader)s/%(title)s.%(ext)s'),
    'format': 'bestvideo+bestaudio/best' if is_ffmpeg_installed() else 'best',
    'merge_output_format': 'mp4',
    'noplaylist': False,
    'ignoreerrors': True,
}


class YouTubeDownloaderGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Frog Downloader ")
        self.root.geometry("600x600")
        self.root.configure(bg='#E0F7E0')

        # Set window icon
        try:
            self.root.iconphoto(True, tk.PhotoImage(file="youtube.png"))
        except Exception as e:
            print(f"Warning: Could not load icon 'youtube.png': {e}")

        # Main frame
        self.main_frame = tk.Frame(self.root, padx=10, pady=10, bg='#E0F7E0')
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        # Khmer-style font for labels
        khmer_font = load_khmer_font()
        label_font = (khmer_font, 12, "bold") if khmer_font else ("Arial", 12, "bold")
        secondary_font = (khmer_font, 10) if khmer_font else ("Arial", 10)

        # Single video download section
        tk.Label(self.main_frame, text="Download Single Video or Short", font=label_font, bg='#E0F7E0').pack(anchor="w")
        tk.Label(self.main_frame, text="Enter YouTube URL:", font=secondary_font, bg='#E0F7E0').pack(anchor="w")
        self.single_url_entry = tk.Entry(self.main_frame, width=60)
        self.single_url_entry.pack(pady=5)
        tk.Button(self.main_frame, text="Download Single Video", command=self.download_single, bg='#D0E7D0').pack(
            pady=5)

        # Multiple videos download section
        tk.Label(self.main_frame, text="Download Multiple Videos", font=label_font, bg='#E0F7E0').pack(anchor="w",
                                                                                                       pady=10)
        tk.Label(self.main_frame, text="Enter YouTube URLs (one per line):", font=secondary_font, bg='#E0F7E0').pack(
            anchor="w")
        self.multi_url_text = scrolledtext.ScrolledText(self.main_frame, width=60, height=5)
        self.multi_url_text.pack(pady=5)
        tk.Button(self.main_frame, text="Download Multiple Videos", command=self.download_multiple, bg='#D0E7D0').pack(
            pady=5)

        # Channel/playlist download section
        tk.Label(self.main_frame, text="Download Entire Channel or Playlist", font=label_font, bg='#E0F7E0').pack(
            anchor="w", pady=10)
        tk.Label(self.main_frame,
                 text="Enter Channel/Playlist URL (e.g., https://www.youtube.com/c/YourChannel/videos):",
                 font=secondary_font, bg='#E0F7E0').pack(anchor="w")
        self.channel_url_entry = tk.Entry(self.main_frame, width=60)
        self.channel_url_entry.pack(pady=5)
        tk.Button(self.main_frame, text="Download Channel/Playlist", command=self.download_channel, bg='#D0E7D0').pack(
            pady=5)

        # Status display
        tk.Label(self.main_frame, text="Status:", font=label_font, bg='#E0F7E0').pack(anchor="w", pady=10)
        self.status_text = scrolledtext.ScrolledText(self.main_frame, width=60, height=10, state='disabled')
        self.status_text.pack(pady=5)

        # Exit button
        tk.Button(self.main_frame, text="Exit", command=self.root.quit, bg='#D0E7D0').pack(pady=5)

        # Note about ffmpeg
        ffmpeg_status = "ffmpeg detected. Using best quality." if is_ffmpeg_installed() else "ffmpeg not detected. Using single stream (lower quality). Install ffmpeg for best quality."
        self.log_status(f"Info: {ffmpeg_status}")

    def log_status(self, message):
        self.status_text.config(state='normal')
        self.status_text.insert(tk.END, f"{message}\n")
        self.status_text.see(tk.END)
        self.status_text.config(state='disabled')

    def download_single(self):
        url = self.single_url_entry.get().strip()
        if not url:
            messagebox.showerror("Error", "Please enter a URL.")
            return
        threading.Thread(target=self.download_single_thread, args=(url,), daemon=True).start()

    def download_single_thread(self, url):
        self.log_status(f"Downloading: {url}")
        with yt_dlp.YoutubeDL(YDL_OPTS) as ydl:
            try:
                ydl.download([url])
                self.log_status(f"✅ Download complete ➜ Saved in '{DOWNLOAD_FOLDER}'")
            except Exception as e:
                self.log_status(f"❌ Error: {e}")
                messagebox.showerror("Error", f"Failed to download {url}: {e}")

    def download_multiple(self):
        urls = self.multi_url_text.get("1.0", tk.END).strip().splitlines()
        urls = [url.strip() for url in urls if url.strip()]
        if not urls:
            messagebox.showerror("Error", "Please enter at least one URL.")
            return
        threading.Thread(target=self.download_multiple_thread, args=(urls,), daemon=True).start()

    def download_multiple_thread(self, urls):
        self.log_status("Starting multiple downloads...")
        with yt_dlp.YoutubeDL(YDL_OPTS) as ydl:
            for url in urls:
                try:
                    self.log_status(f"Downloading: {url}")
                    ydl.download([url])
                    self.log_status(f"✅ Downloaded: {url}")
                except Exception as e:
                    self.log_status(f"❌ Failed to download {url}: {e}")
        self.log_status(f"✅ All downloads finished ➜ Saved in '{DOWNLOAD_FOLDER}'")

    def download_channel(self):
        url = self.channel_url_entry.get().strip()
        if not url:
            messagebox.showerror("Error", "Please enter a channel or playlist URL.")
            return
        threading.Thread(target=self.download_channel_thread, args=(url,), daemon=True).start()

    def download_channel_thread(self, url):
        self.log_status(f"Starting channel/playlist download: {url}")
        with yt_dlp.YoutubeDL(YDL_OPTS_CHANNEL) as ydl:
            try:
                ydl.download([url])
                self.log_status(f"✅ Channel/playlist download complete ➜ Saved in '{DOWNLOAD_FOLDER}'")
            except Exception as e:
                self.log_status(f"❌ Error downloading channel/playlist: {e}")
                messagebox.showerror("Error", f"Failed to download channel/playlist: {e}")


if __name__ == "__main__":
    root = tk.Tk()
    app = YouTubeDownloaderGUI(root)
    root.mainloop()