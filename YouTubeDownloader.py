import os
import yt_dlp

# Define the download folder
DOWNLOAD_FOLDER = "Video Downloaded"
os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)

# Common yt-dlp options for best single stream (no ffmpeg required)
YDL_OPTS = {
    'outtmpl': os.path.join(DOWNLOAD_FOLDER, '%(title)s.%(ext)s'),
    'format': 'best',  # Selects the best pre-merged video+audio stream
    'merge_output_format': 'mp4',
    'noplaylist': True,
}

def download_single_video():
    url = input("\n📥 Enter YouTube video or Shorts URL: ")
    with yt_dlp.YoutubeDL(YDL_OPTS) as ydl:
        try:
            ydl.download([url])
            print(f"✅ Download complete ➜ Saved in '{DOWNLOAD_FOLDER}'\n")
        except Exception as e:
            print(f"❌ Error: {e}\n")

def download_multiple_videos():
    print("\n📥 Paste each YouTube URL. Type 'done' when finished.")
    urls = []
    while True:
        url = input("URL: ")
        if url.strip().lower() == 'done':
            break
        urls.append(url.strip())

    if not urls:
        print("⚠️ No URLs entered.\n")
        return

    with yt_dlp.YoutubeDL(YDL_OPTS) as ydl:
        for url in urls:
            try:
                ydl.download([url])
                print(f"✅ Downloaded: {url}")
            except Exception as e:
                print(f"❌ Failed to download {url}: {e}")
    print(f"✅ All downloads finished ➜ Saved in '{DOWNLOAD_FOLDER}'\n")

def download_profile_placeholder():
    print("\n🚧 Full profile/channel download:")
    print("To download an entire channel or playlist, uncomment the playlist option below.\n")
    print("Example (uncomment `YDL_OPTS['noplaylist'] = False`):")
    print("    YDL_OPTS['noplaylist'] = False")
    print("    ydl.download(['https://www.youtube.com/c/YourChannel/videos'])\n")
    print("Or just run:\n    yt-dlp -o 'Video Downloaded/%(title)s.%(ext)s' -f best '<channel_or_playlist_URL>'\n")

def main():
    while True:
        print("\n==== yt-dlp YouTube Downloader ====")
        print("1. Download Single Video or Short")
        print("2. Download Multiple Videos")
        print("3. Download The Whole Profile/Playlist (Instructions)")
        print("0. Exit")
        choice = input("Choose an option (0-3): ").strip()

        if choice == "1":
            download_single_video()
        elif choice == "2":
            download_multiple_videos()
        elif choice == "3":
            download_profile_placeholder()
        elif choice == "0":
            print("👋 Goodbye!")
            break
        else:
            print("❌ Invalid choice. Please try again.\n")

if __name__ == "__main__":
    main()