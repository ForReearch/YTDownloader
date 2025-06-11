import tkinter as tk
from tkinter import ttk
import speedtest
import threading
import math
import time

class SpeedometerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Frog TestSpeed")
        self.root.geometry("600x500")
        self.root.resizable(False, False)
        
        # Colors
        self.bg_color = "#2c3e50"
        self.needle_color = "#e74c3c"
        self.dial_color = "#34495e"
        self.text_color = "#ecf0f1"
        self.gauge_color = "#3498db"
        
        # Create main container
        self.main_frame = tk.Frame(root, bg=self.bg_color)
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Create speedometer canvas
        self.canvas = tk.Canvas(self.main_frame, width=400, height=400, bg=self.bg_color, highlightthickness=0)
        self.canvas.pack(pady=20)
        
        # Create controls frame
        self.controls_frame = tk.Frame(self.main_frame, bg=self.bg_color)
        self.controls_frame.pack(fill=tk.X, padx=20, pady=10)
        
        # Test button
        self.test_button = tk.Button(
            self.controls_frame, 
            text="Start Speed Test", 
            command=self.start_test,
            bg="#27ae60",
            fg="white",
            font=("Arial", 12),
            relief=tk.FLAT,
            padx=20,
            pady=5
        )
        self.test_button.pack(side=tk.LEFT)
        
        # Status label
        self.status_label = tk.Label(
            self.controls_frame,
            text="Ready to test",
            bg=self.bg_color,
            fg=self.text_color,
            font=("Arial", 10)
        )
        self.status_label.pack(side=tk.RIGHT, padx=10)
        
        # Results frame
        self.results_frame = tk.Frame(self.main_frame, bg=self.bg_color)
        self.results_frame.pack(fill=tk.X, padx=20, pady=10)
        
        # Download speed
        self.download_label = tk.Label(
            self.results_frame,
            text="Download: -- Mbps",
            bg=self.bg_color,
            fg=self.text_color,
            font=("Arial", 12, "bold")
        )
        self.download_label.pack(side=tk.LEFT, padx=10)
        
        # Upload speed
        self.upload_label = tk.Label(
            self.results_frame,
            text="Upload: -- Mbps",
            bg=self.bg_color,
            fg=self.text_color,
            font=("Arial", 12, "bold")
        )
        self.upload_label.pack(side=tk.LEFT, padx=10)
        
        # Ping
        self.ping_label = tk.Label(
            self.results_frame,
            text="Ping: -- ms",
            bg=self.bg_color,
            fg=self.text_color,
            font=("Arial", 12, "bold")
        )
        self.ping_label.pack(side=tk.LEFT, padx=10)
        
        # Initialize speedometer
        self.draw_speedometer()
        self.needle = None
        self.current_speed = 0
        
    def draw_speedometer(self):
        # Draw outer circle
        self.canvas.create_oval(50, 50, 350, 350, outline=self.dial_color, width=10, fill=self.dial_color)
        
        # Draw inner circle (gauge face)
        self.canvas.create_oval(100, 100, 300, 300, outline=self.gauge_color, width=2, fill=self.bg_color)
        
        # Draw speed markings
        for i in range(0, 220, 20):
            angle = math.radians(135 + (i * 0.9))
            start_x = 200 + 120 * math.cos(angle)
            start_y = 200 + 120 * math.sin(angle)
            end_x = 200 + 140 * math.cos(angle)
            end_y = 200 + 140 * math.sin(angle)
            self.canvas.create_line(start_x, start_y, end_x, end_y, fill=self.text_color, width=2)
            
            # Add numbers
            if i % 40 == 0:
                text_x = 200 + 100 * math.cos(angle)
                text_y = 200 + 100 * math.sin(angle)
                self.canvas.create_text(text_x, text_y, text=str(i), fill=self.text_color, font=("Arial", 10, "bold"))
        
        # Add labels
        self.canvas.create_text(200, 180, text="Mbps", fill=self.text_color, font=("Arial", 12, "bold"))
        self.canvas.create_text(200, 220, text="Internet Speed", fill=self.text_color, font=("Arial", 10))
        
    def update_needle(self, speed):
        # Limit speed to 200 for display purposes
        display_speed = min(speed, 200)
        
        # Calculate angle (135° to 315° range)
        angle = math.radians(135 + (display_speed * 0.9))
        
        # Calculate needle end point
        end_x = 200 + 90 * math.cos(angle)
        end_y = 200 + 90 * math.sin(angle)
        
        # Delete old needle if exists
        if self.needle:
            self.canvas.delete(self.needle)
        
        # Draw new needle
        self.needle = self.canvas.create_line(200, 200, end_x, end_y, fill=self.needle_color, width=3)
        
        # Draw needle center
        self.canvas.create_oval(195, 195, 205, 205, fill=self.needle_color, outline=self.needle_color)
        
    def animate_needle(self, target_speed):
        step = (target_speed - self.current_speed) / 20
        
        def animation_step():
            if abs(self.current_speed - target_speed) > 0.5:
                self.current_speed += step
                self.update_needle(self.current_speed)
                self.root.after(20, animation_step)
            else:
                self.current_speed = target_speed
                self.update_needle(self.current_speed)
        
        animation_step()
    
    def run_speed_test(self):
        self.test_button.config(state=tk.DISABLED, bg="#7f8c8d")
        self.status_label.config(text="Testing...")
        
        try:
            st = speedtest.Speedtest()
            st.get_best_server()
            
            # Test download speed with animation
            self.status_label.config(text="Testing Download Speed...")
            download_speed = st.download() / 1_000_000  # Convert to Mbps
            self.animate_needle(download_speed)
            self.download_label.config(text=f"Download: {download_speed:.2f} Mbps")
            
            # Test upload speed
            self.status_label.config(text="Testing Upload Speed...")
            upload_speed = st.upload() / 1_000_000  # Convert to Mbps
            self.upload_label.config(text=f"Upload: {upload_speed:.2f} Mbps")
            
            # Get ping
            ping = st.results.ping
            self.ping_label.config(text=f"Ping: {ping:.2f} ms")
            
            self.status_label.config(text="Test Complete")
            
        except Exception as e:
            self.status_label.config(text=f"Error: {str(e)}")
        finally:
            self.test_button.config(state=tk.NORMAL, bg="#27ae60")
    
    def start_test(self):
        # Run speed test in a separate thread to avoid freezing the GUI
        threading.Thread(target=self.run_speed_test, daemon=True).start()

if __name__ == "__main__":
    root = tk.Tk()
    app = SpeedometerApp(root)
    root.mainloop()