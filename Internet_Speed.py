import tkinter as tk
from tkinter import ttk, messagebox
import math
import speedtest
from threading import Thread
import time

class SpeedTestApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Internet Speedometer")
        self.root.geometry("600x500")
        self.root.resizable(False, False)
        
        # Variables
        self.download_speed = 0
        self.upload_speed = 0
        self.max_download = 0
        self.max_upload = 0
        self.test_in_progress = False
        
        # Create UI
        self.create_widgets()
        
    def create_widgets(self):
        # Main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Download gauge
        self.download_canvas = tk.Canvas(main_frame, width=250, height=250, bg='white')
        self.download_canvas.grid(row=0, column=0, padx=10, pady=10)
        self.draw_gauge(self.download_canvas, "Download Speed (Mbps)")
        
        # Upload gauge
        self.upload_canvas = tk.Canvas(main_frame, width=250, height=250, bg='white')
        self.upload_canvas.grid(row=0, column=1, padx=10, pady=10)
        self.draw_gauge(self.upload_canvas, "Upload Speed (Mbps)")
        
        # Results frame
        results_frame = ttk.LabelFrame(main_frame, text="Test Results", padding="10")
        results_frame.grid(row=1, column=0, columnspan=2, pady=10, sticky="ew")
        
        # Download result
        ttk.Label(results_frame, text="Max Download Speed:").grid(row=0, column=0, sticky="e")
        self.download_result = ttk.Label(results_frame, text="0.00 Mbps", font=('Arial', 10, 'bold'))
        self.download_result.grid(row=0, column=1, sticky="w", padx=5)
        
        # Upload result
        ttk.Label(results_frame, text="Max Upload Speed:").grid(row=1, column=0, sticky="e")
        self.upload_result = ttk.Label(results_frame, text="0.00 Mbps", font=('Arial', 10, 'bold'))
        self.upload_result.grid(row=1, column=1, sticky="w", padx=5)
        
        # Test button
        self.test_button = ttk.Button(main_frame, text="Start Speed Test", command=self.start_test_thread)
        self.test_button.grid(row=2, column=0, columnspan=2, pady=10)
        
        # Status label
        self.status_label = ttk.Label(main_frame, text="Ready to test", foreground="blue")
        self.status_label.grid(row=3, column=0, columnspan=2)
        
    def draw_gauge(self, canvas, title):
        canvas.delete("all")
        width = canvas.winfo_width()
        height = canvas.winfo_height()
        center_x = width // 2
        center_y = height // 2
        radius = min(width, height) * 0.4
        
        # Draw outer circle
        canvas.create_oval(center_x - radius, center_y - radius, 
                          center_x + radius, center_y + radius, 
                          outline="black", width=2)
        
        # Draw title
        canvas.create_text(center_x, height - 20, text=title, font=('Arial', 10))
        
        # Draw scale marks (0-100 Mbps)
        for i in range(0, 101, 10):
            angle = math.radians(135 + (i * 2.7))
            inner_x = center_x + (radius - 10) * math.cos(angle)
            inner_y = center_y + (radius - 10) * math.sin(angle)
            outer_x = center_x + radius * math.cos(angle)
            outer_y = center_y + radius * math.sin(angle)
            
            canvas.create_line(inner_x, inner_y, outer_x, outer_y, width=2)
            
            # Add labels
            label_x = center_x + (radius - 25) * math.cos(angle)
            label_y = center_y + (radius - 25) * math.sin(angle)
            canvas.create_text(label_x, label_y, text=str(i), font=('Arial', 8))
        
        # Initial needle (pointing to 0)
        self.draw_needle(canvas, 0, "blue")
    
    def draw_needle(self, canvas, speed, color):
        # Limit speed to 100 for display purposes (adjust scale if you expect higher speeds)
        display_speed = min(speed, 100)
        
        # Calculate angle (135° to 405° range, but we'll use modulo)
        angle = math.radians(135 + (display_speed * 2.7))
        
        width = canvas.winfo_width()
        height = canvas.winfo_height()
        center_x = width // 2
        center_y = height // 2
        radius = min(width, height) * 0.4
        
        # Delete previous needle
        canvas.delete("needle")
        
        # Draw new needle
        end_x = center_x + (radius - 15) * math.cos(angle)
        end_y = center_y + (radius - 15) * math.sin(angle)
        canvas.create_line(center_x, center_y, end_x, end_y, 
                          width=3, fill=color, tags="needle")
        
        # Draw needle center
        canvas.create_oval(center_x - 5, center_y - 5, 
                          center_x + 5, center_y + 5, 
                          fill=color, outline="black", tags="needle")
        
        # Display current speed
        canvas.delete("speed_text")
        canvas.create_text(center_x, center_y + 30, 
                          text=f"{speed:.2f} Mbps", 
                          font=('Arial', 10, 'bold'), 
                          tags="speed_text")
    
    def start_test_thread(self):
        if not self.test_in_progress:
            self.test_in_progress = True
            self.test_button.config(state=tk.DISABLED)
            self.status_label.config(text="Testing...", foreground="orange")
            
            # Reset max values
            self.max_download = 0
            self.max_upload = 0
            self.download_result.config(text="0.00 Mbps")
            self.upload_result.config(text="0.00 Mbps")
            
            # Start test in a separate thread
            Thread(target=self.run_speed_test, daemon=True).start()
    
    def run_speed_test(self):
        try:
            st = speedtest.Speedtest()
            
            # Test download speed with progress updates
            self.status_label.config(text="Testing download speed...")
            st.get_best_server()
            
            # We'll simulate progress for the gauge (actual speedtest is one measurement)
            for i in range(0, 101, 5):
                if not self.test_in_progress:
                    break
                self.download_speed = i
                self.update_download_gauge()
                time.sleep(0.05)
            
            # Get actual download speed
            self.status_label.config(text="Measuring download speed...")
            download_speed = st.download() / 1_000_000  # Convert to Mbps
            self.download_speed = download_speed
            self.max_download = max(self.max_download, download_speed)
            self.update_download_gauge()
            self.download_result.config(text=f"{self.max_download:.2f} Mbps")
            
            # Test upload speed with progress updates
            self.status_label.config(text="Testing upload speed...")
            for i in range(0, 101, 5):
                if not self.test_in_progress:
                    break
                self.upload_speed = i
                self.update_upload_gauge()
                time.sleep(0.05)
            
            # Get actual upload speed
            self.status_label.config(text="Measuring upload speed...")
            upload_speed = st.upload() / 1_000_000  # Convert to Mbps
            self.upload_speed = upload_speed
            self.max_upload = max(self.max_upload, upload_speed)
            self.update_upload_gauge()
            self.upload_result.config(text=f"{self.max_upload:.2f} Mbps")
            
            self.status_label.config(text="Test completed!", foreground="green")
            
        except Exception as e:
            self.status_label.config(text=f"Error: {str(e)}", foreground="red")
            messagebox.showerror("Error", f"An error occurred during the speed test:\n{str(e)}")
        
        finally:
            self.test_in_progress = False
            self.test_button.config(state=tk.NORMAL)
    
    def update_download_gauge(self):
        self.draw_needle(self.download_canvas, self.download_speed, "blue")
        self.root.update()
    
    def update_upload_gauge(self):
        self.draw_needle(self.upload_canvas, self.upload_speed, "green")
        self.root.update()

if __name__ == "__main__":
    root = tk.Tk()
    app = SpeedTestApp(root)
    root.mainloop()