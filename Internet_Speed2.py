import tkinter as tk
from tkinter import ttk, messagebox
import math
import speedtest
from threading import Thread
import time
from tkinter import font as tkfont

class ProfessionalSpeedTestApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Network Speed Analyzer Pro")
        self.root.geometry("800x650")
        self.root.resizable(False, False)
        
        # Colors - defined before any usage
        self.bg_color = "#2E2E2E"
        self.gauge_bg = "#1E1E1E"
        self.text_color = "#FFFFFF"
        self.accent_color = "#4FC3F7"
        self.download_color = "#64B5F6"
        self.upload_color = "#81C784"
        self.error_color = "#E57373"
        
        # Fonts
        self.title_font = tkfont.Font(family="Segoe UI", size=14, weight="bold")
        self.gauge_font = tkfont.Font(family="Segoe UI", size=10)
        self.result_font = tkfont.Font(family="Segoe UI", size=12, weight="bold")
        
        # Configure style - after colors are defined
        self.style = ttk.Style()
        self.style.theme_use('clam')
        self.configure_styles()
        
        # Variables
        self.download_speed = 0
        self.upload_speed = 0
        self.max_download = 0
        self.max_upload = 0
        self.test_in_progress = False
        self.ping_result = 0
        
        # Configure root window
        self.root.configure(bg=self.bg_color)
        
        # Create UI
        self.create_widgets()
        
    def configure_styles(self):
        self.style.configure('TFrame', background=self.bg_color)
        self.style.configure('TLabel', background=self.bg_color, foreground=self.text_color)
        self.style.configure('TButton', background="#424242", foreground=self.text_color, 
                           borderwidth=1, font=('Segoe UI', 10))
        self.style.map('TButton', 
                      background=[('active', '#616161'), ('disabled', '#303030')],
                      foreground=[('disabled', '#757575')])
        self.style.configure('Title.TLabel', font=self.title_font, foreground=self.accent_color)
        self.style.configure('Result.TLabel', font=self.result_font, foreground=self.text_color)
        self.style.configure('Gauge.TFrame', background=self.gauge_bg, relief='flat')
        self.style.configure('HL.TSeparator', background="#616161")
        
    def create_widgets(self):
        # Header
        header_frame = ttk.Frame(self.root)
        header_frame.pack(fill=tk.X, padx=20, pady=(20, 10))
        
        ttk.Label(header_frame, text="NETWORK SPEED ANALYZER", style='Title.TLabel').pack(side=tk.LEFT)
        
        # Main content
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        # Gauges frame
        gauges_frame = ttk.Frame(main_frame, style='Gauge.TFrame')
        gauges_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 20))
        
        # Download gauge
        download_frame = ttk.Frame(gauges_frame)
        download_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        ttk.Label(download_frame, text="DOWNLOAD SPEED", style='Title.TLabel').pack()
        self.download_canvas = tk.Canvas(download_frame, width=300, height=300, 
                                        bg=self.gauge_bg, highlightthickness=0)
        self.download_canvas.pack(pady=(5, 10))
        self.draw_gauge(self.download_canvas, "Mbps", self.download_color)
        
        # Upload gauge
        upload_frame = ttk.Frame(gauges_frame)
        upload_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        ttk.Label(upload_frame, text="UPLOAD SPEED", style='Title.TLabel').pack()
        self.upload_canvas = tk.Canvas(upload_frame, width=300, height=300, 
                                      bg=self.gauge_bg, highlightthickness=0)
        self.upload_canvas.pack(pady=(5, 10))
        self.draw_gauge(self.upload_canvas, "Mbps", self.upload_color)
        
        # Separator
        ttk.Separator(main_frame, orient=tk.HORIZONTAL, style='HL.TSeparator').pack(fill=tk.X, pady=10)
        
        # Results frame
        results_frame = ttk.Frame(main_frame)
        results_frame.pack(fill=tk.X, pady=(0, 20))
        
        # Ping result
        ping_frame = ttk.Frame(results_frame)
        ping_frame.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=10)
        ttk.Label(ping_frame, text="LATENCY:", style='Title.TLabel').pack(anchor=tk.W)
        self.ping_label = ttk.Label(ping_frame, text="-- ms", style='Result.TLabel')
        self.ping_label.pack(anchor=tk.W)
        
        # Download result
        dl_frame = ttk.Frame(results_frame)
        dl_frame.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=10)
        ttk.Label(dl_frame, text="MAX DOWNLOAD:", style='Title.TLabel').pack(anchor=tk.W)
        self.download_result = ttk.Label(dl_frame, text="-- Mbps", style='Result.TLabel')
        self.download_result.pack(anchor=tk.W)
        
        # Upload result
        ul_frame = ttk.Frame(results_frame)
        ul_frame.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=10)
        ttk.Label(ul_frame, text="MAX UPLOAD:", style='Title.TLabel').pack(anchor=tk.W)
        self.upload_result = ttk.Label(ul_frame, text="-- Mbps", style='Result.TLabel')
        self.upload_result.pack(anchor=tk.W)
        
        # Controls frame
        controls_frame = ttk.Frame(main_frame)
        controls_frame.pack(fill=tk.X, pady=(10, 0))
        
        self.test_button = ttk.Button(controls_frame, text="START SPEED TEST", 
                                    command=self.start_test_thread)
        self.test_button.pack(pady=10, ipadx=20, ipady=5)
        
        # Status frame
        status_frame = ttk.Frame(main_frame)
        status_frame.pack(fill=tk.X)
        
        self.status_label = ttk.Label(status_frame, text="Ready to perform speed test", 
                                    style='Result.TLabel', foreground=self.accent_color)
        self.status_label.pack()
        
        # Footer
        footer_frame = ttk.Frame(self.root)
        footer_frame.pack(fill=tk.X, padx=20, pady=(0, 20))
        ttk.Label(footer_frame, text="© 2023 Network Speed Analyzer Pro", 
                style='TLabel', foreground="#757575").pack(side=tk.RIGHT)
    
    def draw_gauge(self, canvas, unit, color):
        canvas.delete("all")
        width = canvas.winfo_width()
        height = canvas.winfo_height()
        center_x = width // 2
        center_y = height // 2
        radius = min(width, height) * 0.4
        
        # Draw outer arc
        canvas.create_arc(center_x - radius, center_y - radius, 
                         center_x + radius, center_y + radius,
                         start=135, extent=270, outline="#424242", width=2, style=tk.ARC)
        
        # Draw scale marks (0-200 Mbps)
        for i in range(0, 201, 20):
            angle = math.radians(135 + (i * 1.35))  # Adjusted for 0-200 range
            inner_x = center_x + (radius - 15) * math.cos(angle)
            inner_y = center_y + (radius - 15) * math.sin(angle)
            outer_x = center_x + radius * math.cos(angle)
            outer_y = center_y + radius * math.sin(angle)
            
            canvas.create_line(inner_x, inner_y, outer_x, outer_y, width=2, fill="#616161")
            
            # Add labels
            label_x = center_x + (radius - 30) * math.cos(angle)
            label_y = center_y + (radius - 30) * math.sin(angle)
            canvas.create_text(label_x, label_y, text=str(i), font=self.gauge_font, fill=self.text_color)
        
        # Add unit label
        canvas.create_text(center_x, center_y + radius - 40, text=unit, 
                         font=self.gauge_font, fill=self.text_color)
        
        # Initial needle (pointing to 0)
        self.draw_needle(canvas, 0, color)
    
    def draw_needle(self, canvas, speed, color):
        # Limit speed to 200 for display purposes
        display_speed = min(speed, 200)
        
        # Calculate angle (135° to 405° range)
        angle = math.radians(135 + (display_speed * 1.35))  # Adjusted for 0-200 range
        
        width = canvas.winfo_width()
        height = canvas.winfo_height()
        center_x = width // 2
        center_y = height // 2
        radius = min(width, height) * 0.4
        
        # Delete previous needle
        canvas.delete("needle")
        
        # Draw new needle
        end_x = center_x + (radius - 20) * math.cos(angle)
        end_y = center_y + (radius - 20) * math.sin(angle)
        canvas.create_line(center_x, center_y, end_x, end_y, 
                         width=4, fill=color, tags="needle", arrow=tk.LAST, arrowshape=(12, 15, 5))
        
        # Draw needle center
        canvas.create_oval(center_x - 8, center_y - 8, 
                         center_x + 8, center_y + 8, 
                         fill=color, outline="#424242", width=2, tags="needle")
        
        # Display current speed
        canvas.delete("speed_text")
        canvas.create_text(center_x, center_y + 20, 
                         text=f"{speed:.1f}", 
                         font=('Segoe UI', 16, 'bold'), 
                         fill=self.text_color,
                         tags="speed_text")
    
    def start_test_thread(self):
        if not self.test_in_progress:
            self.test_in_progress = True
            self.test_button.config(state=tk.DISABLED)
            self.status_label.config(text="Initializing speed test...", foreground=self.accent_color)
            
            # Reset values
            self.max_download = 0
            self.max_upload = 0
            self.ping_result = 0
            self.download_result.config(text="-- Mbps")
            self.upload_result.config(text="-- Mbps")
            self.ping_label.config(text="-- ms")
            
            # Start test in a separate thread
            Thread(target=self.run_speed_test, daemon=True).start()
    
    def run_speed_test(self):
        try:
            st = speedtest.Speedtest()
            
            # Test ping first
            self.status_label.config(text="Measuring latency...")
            server = st.get_best_server()
            self.ping_result = server['latency']
            self.ping_label.config(text=f"{self.ping_result:.1f} ms")
            
            # Test download speed with progress updates
            self.status_label.config(text="Testing download speed...")
            
            # Simulate progress animation
            for i in range(0, 101, 2):
                if not self.test_in_progress:
                    break
                self.download_speed = i * 2  # Scale to 0-200 range
                self.update_download_gauge()
                time.sleep(0.03)
            
            # Get actual download speed
            self.status_label.config(text="Measuring download speed (this may take a while)...")
            download_speed = st.download() / 1_000_000  # Convert to Mbps
            self.download_speed = download_speed
            self.max_download = max(self.max_download, download_speed)
            self.update_download_gauge()
            self.download_result.config(text=f"{self.max_download:.2f} Mbps")
            
            # Test upload speed with progress updates
            self.status_label.config(text="Testing upload speed...")
            
            # Simulate progress animation
            for i in range(0, 101, 2):
                if not self.test_in_progress:
                    break
                self.upload_speed = i * 2  # Scale to 0-200 range
                self.update_upload_gauge()
                time.sleep(0.03)
            
            # Get actual upload speed
            self.status_label.config(text="Measuring upload speed (this may take a while)...")
            upload_speed = st.upload() / 1_000_000  # Convert to Mbps
            self.upload_speed = upload_speed
            self.max_upload = max(self.max_upload, upload_speed)
            self.update_upload_gauge()
            self.upload_result.config(text=f"{self.max_upload:.2f} Mbps")
            
            self.status_label.config(text="Speed test completed successfully!", foreground="#81C784")
            
        except Exception as e:
            self.status_label.config(text=f"Error: {str(e)}", foreground=self.error_color)
            messagebox.showerror("Test Error", f"An error occurred during the speed test:\n{str(e)}")
        
        finally:
            self.test_in_progress = False
            self.test_button.config(state=tk.NORMAL)
    
    def update_download_gauge(self):
        self.draw_needle(self.download_canvas, self.download_speed, self.download_color)
        self.root.update()
    
    def update_upload_gauge(self):
        self.draw_needle(self.upload_canvas, self.upload_speed, self.upload_color)
        self.root.update()

if __name__ == "__main__":
    root = tk.Tk()
    app = ProfessionalSpeedTestApp(root)
    root.mainloop()