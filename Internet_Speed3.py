import tkinter as tk
from tkinter import ttk, messagebox
import speedtest
from threading import Thread
import time

class SpeedTestApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Network Speed Test")
        self.root.geometry("500x600")
        self.root.resizable(False, False)
        
        # Colors
        self.bg_color = "#FFFFFF"
        self.text_color = "#333333"
        self.accent_color = "#4285F4"
        self.download_color = "#34A853"
        self.upload_color = "#EA4335"
        self.ping_color = "#FBBC05"
        
        # Fonts
        self.title_font = ("Segoe UI", 16, "bold")
        self.label_font = ("Segoe UI", 12)
        self.speed_font = ("Segoe UI", 24, "bold")
        self.ping_font = ("Segoe UI", 14)
        
        # Variables
        self.download_speed = 0
        self.upload_speed = 0
        self.ping = 0
        self.test_in_progress = False
        
        # Create UI
        self.create_header()
        self.create_speed_test_area()
        self.create_results_area()
        self.create_footer()
        
    def create_header(self):
        header_frame = tk.Frame(self.root, bg=self.bg_color)
        header_frame.pack(fill=tk.X, padx=20, pady=10)
        
        tk.Label(header_frame, text="SPEEDTEST", font=self.title_font, 
                bg=self.bg_color, fg=self.accent_color).pack(side=tk.LEFT)
        
        # Menu buttons
        menu_frame = tk.Frame(header_frame, bg=self.bg_color)
        menu_frame.pack(side=tk.RIGHT)
        
        for text in ["English", "Apps", "Learn", "Data", "About"]:
            tk.Button(menu_frame, text=text, font=("Segoe UI", 10), 
                     borderwidth=0, bg=self.bg_color, fg=self.text_color,
                     activebackground=self.bg_color, activeforeground=self.accent_color).pack(side=tk.LEFT, padx=5)
    
    def create_speed_test_area(self):
        test_frame = tk.Frame(self.root, bg=self.bg_color)
        test_frame.pack(fill=tk.X, padx=40, pady=20)
        
        # Download test
        tk.Label(test_frame, text="DOWNLOAD", font=self.label_font, 
                bg=self.bg_color, fg=self.text_color).grid(row=0, column=0, sticky="w")
        
        self.download_label = tk.Label(test_frame, text="0 Mbps", font=self.speed_font,
                                      bg=self.bg_color, fg=self.download_color)
        self.download_label.grid(row=1, column=0, sticky="w", pady=(0, 20))
        
        # Upload test
        tk.Label(test_frame, text="UPLOAD", font=self.label_font, 
                bg=self.bg_color, fg=self.text_color).grid(row=2, column=0, sticky="w")
        
        self.upload_label = tk.Label(test_frame, text="0 Mbps", font=self.speed_font,
                                    bg=self.bg_color, fg=self.upload_color)
        self.upload_label.grid(row=3, column=0, sticky="w", pady=(0, 20))
        
        # Ping test
        ping_frame = tk.Frame(test_frame, bg=self.bg_color)
        ping_frame.grid(row=4, column=0, sticky="w")
        
        tk.Label(ping_frame, text="Ping", font=self.label_font, 
                bg=self.bg_color, fg=self.text_color).grid(row=0, column=0, sticky="w")
        
        self.ping_label = tk.Label(ping_frame, text="0 ms", font=self.ping_font,
                                  bg=self.bg_color, fg=self.ping_color)
        self.ping_label.grid(row=0, column=1, sticky="w", padx=10)
    
    def create_results_area(self):
        results_frame = tk.Frame(self.root, bg=self.bg_color)
        results_frame.pack(fill=tk.X, padx=40, pady=10)
        
        # Server info
        tk.Label(results_frame, text="Server:", font=self.label_font, 
                bg=self.bg_color, fg=self.text_color).grid(row=0, column=0, sticky="w")
        
        self.server_label = tk.Label(results_frame, text="Selecting best server...", 
                                   font=("Segoe UI", 10), bg=self.bg_color, fg=self.text_color)
        self.server_label.grid(row=0, column=1, sticky="w")
        
        # Test button
        self.test_button = tk.Button(self.root, text="START TEST", font=("Segoe UI", 12, "bold"),
                                   bg=self.accent_color, fg="white", borderwidth=0,
                                   command=self.start_test_thread, padx=30, pady=10)
        self.test_button.pack(pady=20)
    
    def create_footer(self):
        footer_frame = tk.Frame(self.root, bg="#F5F5F5")
        footer_frame.pack(fill=tk.X, side=tk.BOTTOM, pady=(20, 0))
        
        tk.Label(footer_frame, text="MetfonePNP - Linux", font=("Segoe UI", 10), 
                bg="#F5F5F5", fg="#666666").pack(side=tk.LEFT, padx=20, pady=10)
        
        tk.Label(footer_frame, text="Primem Pentix", font=("Segoe UI", 10), 
                bg="#F5F5F5", fg="#666666").pack(side=tk.RIGHT, padx=20, pady=10)
    
    def start_test_thread(self):
        if not self.test_in_progress:
            self.test_in_progress = True
            self.test_button.config(state=tk.DISABLED, text="TESTING...")
            
            # Reset values
            self.download_speed = 0
            self.upload_speed = 0
            self.ping = 0
            self.update_labels()
            
            # Start test in a separate thread
            Thread(target=self.run_speed_test, daemon=True).start()
    
    def run_speed_test(self):
        try:
            st = speedtest.Speedtest()
            
            # Get best server
            self.server_label.config(text="Finding best server...")
            server = st.get_best_server()
            self.server_label.config(text=f"{server['sponsor']} ({server['name']})")
            
            # Test ping
            self.ping = server['latency']
            self.ping_label.config(text=f"{self.ping:.2f} ms")
            
            # Test download speed
            self.download_speed = st.download() / 1_000_000  # Convert to Mbps
            self.download_label.config(text=f"{self.download_speed:.2f} Mbps")
            
            # Test upload speed
            self.upload_speed = st.upload() / 1_000_000  # Convert to Mbps
            self.upload_label.config(text=f"{self.upload_speed:.2f} Mbps")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to complete speed test:\n{str(e)}")
        
        finally:
            self.test_in_progress = False
            self.test_button.config(state=tk.NORMAL, text="START TEST")
    
    def update_labels(self):
        self.download_label.config(text=f"{self.download_speed:.2f} Mbps")
        self.upload_label.config(text=f"{self.upload_speed:.2f} Mbps")
        self.ping_label.config(text=f"{self.ping:.2f} ms")

if __name__ == "__main__":
    root = tk.Tk()
    app = SpeedTestApp(root)
    root.mainloop()