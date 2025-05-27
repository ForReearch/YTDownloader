# YTDownloader
YouTuberDownloader

===================

Frog Downloader
Frog Downloader is a user-friendly GUI application built with Python and tkinter to download YouTube videos, shorts, and entire channels or playlists. It features a Khmer-style interface with the "Khmer OS Siemreap" font, a light green theme, and a custom logo. The application uses yt_dlp to fetch videos in the highest quality available (up to 4K/8K with ffmpeg installed) and organizes downloads by channel.
Features

Download Single Video or Short: Enter a YouTube URL to download a single video or short.
Download Multiple Videos: Input multiple URLs (one per line) for batch downloading.
Download Entire Channel or Playlist: Fetch all videos from a channel or playlist URL.
Khmer Interface: Labels, buttons, and messages in Khmer script using the "Khmer OS Siemreap" font.
Custom Styling: Window titled "Frog Downloader," light green background (#E0F7E0), and youtube.png logo.
High-Quality Downloads: Uses bestvideo+bestaudio/best format (requires ffmpeg) or best as fallback.
Error Handling: Displays download progress and errors in a status box and pop-up messages.
Cross-Platform: Works on Windows, macOS, and Linux.

Requirements

Python: Version 3.6 or higher.
Dependencies:
yt_dlp: pip install -U yt-dlp
tkinter: Included with Python; for Linux, install with sudo apt install python3-tk
ffmpeg (optional, for best quality):
Windows: Download from gyan.dev, extract, add bin to PATH, verify with ffmpeg -version.
macOS: brew install ffmpeg
Linux: sudo apt install ffmpeg (Ubuntu/Debian) or sudo dnf install ffmpeg (Fedora)




Khmer Font: KhmerOS_siemreap.ttf (included or system-installed).
Logo: youtube.png (PNG image, preferably 32x32 or 64x64 pixels).

Installation

Clone or Download the Script:
Save YouTubeDownloaderGUI.py to a directory (e.g., E:\PythyonLanguage\PythonYouTube\).


Install Dependencies:pip install -U yt-dlp


For Linux, ensure tkinter:sudo apt install python3-tk


Install ffmpeg (optional) for high-quality downloads (see Requirements).


Prepare the Khmer Font:
Option 1: Place Font File:
Copy KhmerOS_siemreap.ttf to E:\PythyonLanguage\PythonYouTube\.
The script loads it dynamically as "Khmer OS Siemreap Custom."


Option 2: Install System-Wide (recommended):
Download KhmerOS_siemreap.ttf from KhmerOS.info.
Install:
Windows: Double-click the .ttf file, click “Install.”
macOS: Open with Font Book, click “Install Font.”
Linux:   mkdir -p ~/.fonts
   cp KhmerOS_siemreap.ttf ~/.fonts/
   fc-cache -fv




Verify with:from tkinter import font
print(font.families())  # Look for "KhmerOS_siemreap"






Prepare the Logo:
Place youtube.png in E:\PythyonLanguage\PythonYouTube\ or update the path in the script (line with self.root.iconphoto(True, tk.PhotoImage(file="youtube.png"))).



Usage

Run the Application:cd E:\PythyonLanguage\PythonYouTube
python YouTubeDownloaderGUI.py


Interface:
Title: "Frog Downloader" with youtube.png icon.
Background: Light green (#E0F7E0).
Text: Khmer script in "Khmer OS Siemreap" font for labels, buttons, and status.


Downloading Videos:
Single Video:
Enter a URL (e.g., https://www.youtube.com/shorts/XM1fh0khi5M).
Click “ទាញយកវីឌីអូតែមួយ” (Download Single Video).


Multiple Videos:
Enter URLs (one per line) in the text area.
Click “ទាញយកវីឌីអូច្រើន” (Download Multiple Videos).


Channel/Playlist:
Enter a channel or playlist URL (e.g., https://www.youtube.com/c/TED/videos).
Click “ទាញយកឆានែល/បញ្ជីចាក់” (Download Channel/Playlist).


Output: Videos save in Video Downloaded/<ChannelName>/<VideoTitle>.mp4.


Status and Errors:
Progress and errors appear in the status box (e.g., “កំពុងទាញយក: {url}”).
Pop-up messages for errors (e.g., “សូមបញ្ចូល URL។” for empty input).


Exit:
Click “ចាកចេញ” (Exit) to close.



Troubleshooting

Font Not Displaying:
Symptoms: Labels/buttons show default font (e.g., Arial) instead of Khmer style.
Fixes:
Ensure KhmerOS_siemreap.ttf is at E:\PythyonLanguage\PythonYouTube\.
Check console for Warning: Could not load KhmerOS_siemreap.ttf. If present:
Verify file isn’t corrupted (open in a font viewer).
Check permissions (right-click > Properties > Security).
Download a fresh copy from KhmerOS.info.


Install font system-wide (see Installation).
Test font:from tkinter import Tk, Label
from tkinter import font
root = Tk()
Label(root, text="សួស្តី", font=("Khmer OS Siemreap", 12)).pack()
root.mainloop()






Logo Not Showing:
Ensure youtube.png is in E:\PythyonLanguage\PythonYouTube\.
Check console for Warning: Could not load icon 'youtube.png'.
Use a valid PNG (32x32 or 64x64 pixels).


Download Issues:
Private Videos: Require YouTube Premium or login (not supported).
Geo-Restrictions: Use a VPN to bypass.
Rate Limits: Wait a few hours or change IP.
Corrupted Videos: Repair with tools like Wondershare Repairit.


ffmpeg Not Detected:
Install ffmpeg (see Requirements) for high-quality downloads.
Without ffmpeg, downloads use lower-quality single streams (up to 1080p).



Notes

Quality: With ffmpeg, downloads are in the highest resolution (e.g., 4K/8K) with best audio, merged into MP4. Without ffmpeg, the best pre-merged stream is used (typically up to 1080p).
Khmer Font: If “Khmer OS Siemreap” is unreadable for English text, try “Noto Sans Khmer” from Google Fonts and update font_path in load_khmer_font().
Large Channels: Downloading entire channels may take time and disk space. Ensure a stable internet connection (3 Mbps+ recommended).
License: For personal use. Respect YouTube’s terms of service when downloading content.

Contributing
Feel free to fork the project, add features (e.g., progress bar, resolution selection), or report issues. Submit pull requests or contact the developer for suggestions.
Acknowledgments

Built with yt_dlp for video downloading.
Uses Khmer OS Siemreap font for Khmer script.
Inspired by the need for a simple, culturally styled YouTube downloader.


