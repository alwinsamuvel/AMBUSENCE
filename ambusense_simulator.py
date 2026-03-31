import tkinter as tk
import math
import winsound
import threading
import time

class AmbuSenseApp:
    def __init__(self, root):
        self.root = root
        self.root.title("AmbuSense - Smart Ambulance Alert System Simulator")
        self.root.geometry("800x600")
        self.root.configure(bg="#2C3E50")
        
        # Scale for simulation: 100 pixels = 1 kilometer
        self.km_pixels = 150
        
        # State Initialization
        self.start_pos = [50, 50]
        self.ambulance_pos = list(self.start_pos)
        self.ambulance_target = [750, 500]
        self.user_pos = [400, 275] # roughly middle of path
        
        self.is_running = False
        self.siren_playing = False
        self.alert_triggered = False
        self.siren_thread = None

        self.setup_ui()
        
    def setup_ui(self):
        # Header Section
        header = tk.Label(self.root, text="🚑 AmbuSense: Proximity-Based Alert Simulator", 
                          font=("Segoe UI", 20, "bold"), bg="#2C3E50", fg="white")
        header.pack(pady=10)
        
        # Info Panel
        info_frame = tk.Frame(self.root, bg="#2C3E50")
        info_frame.pack(fill=tk.X, padx=30, pady=5)
        
        self.dist_label = tk.Label(info_frame, text="Distance to User: -- km", font=("Segoe UI", 14), bg="#2C3E50", fg="#F1C40F")
        self.dist_label.pack(side=tk.LEFT)
        
        self.status_label = tk.Label(info_frame, text="Status: Idle", font=("Segoe UI", 14, "bold"), bg="#2C3E50", fg="#BDC3C7")
        self.status_label.pack(side=tk.RIGHT)
        
        # Canvas for Map Visualization
        self.canvas = tk.Canvas(self.root, width=750, height=400, bg="#ECF0F1", highlightthickness=0, bd=0)
        self.canvas.pack(pady=15)
        
        self.draw_environment()
        
        # Control Button
        self.btn = tk.Button(self.root, text="Start Simulation", font=("Segoe UI", 14, "bold"), 
                             bg="#27ae60", fg="white", activebackground="#2ecc71", activeforeground="white",
                             command=self.toggle_simulation, relief=tk.FLAT, padx=20, pady=5, cursor="hand2")
        self.btn.pack()

    def draw_environment(self):
        # Draw the road (diagonal path)
        self.canvas.create_line(self.start_pos[0], self.start_pos[1], 
                                self.ambulance_target[0], self.ambulance_target[1], 
                                fill="#7F8C8D", width=25, capstyle=tk.ROUND)
        
        # Draw road dashed centerline
        self.canvas.create_line(self.start_pos[0], self.start_pos[1], 
                                self.ambulance_target[0], self.ambulance_target[1], 
                                fill="#ECF0F1", width=3, dash=(10, 10))
                                
        # Draw Hospital (Destination)
        hr = 20
        hx, hy = self.ambulance_target
        self.canvas.create_rectangle(hx-hr, hy-hr, hx+hr, hy+hr, fill="#2980B9", outline="#34495E", width=2)
        self.canvas.create_text(hx, hy, text="🏥", font=("Arial", 16))
        self.canvas.create_text(hx, hy+30, text="Hospital", font=("Segoe UI", 10, "bold"), fill="#2980B9")

        # Draw 1km Radius Zone
        rr = self.km_pixels
        self.radius_circle = self.canvas.create_oval(self.user_pos[0]-rr, self.user_pos[1]-rr,
                                                     self.user_pos[0]+rr, self.user_pos[1]+rr, 
                                                     outline="#E74C3C", width=2, dash=(8, 8))
        self.zone_text = self.canvas.create_text(self.user_pos[0], self.user_pos[1]-rr-15, 
                                                 text="1 KM Alert Zone", fill="#E74C3C", font=("Segoe UI", 10, "bold"))
                                                 
        # Draw User Vehicle (in the zone)
        ux, uy = self.user_pos
        ur = 12
        self.user_marker = self.canvas.create_oval(ux-ur, uy-ur, ux+ur, uy+ur, fill="#3498DB", outline="white", width=2)
        self.user_text = self.canvas.create_text(ux, uy, text="🚗", font=("Arial", 12))
        self.canvas.create_text(ux, uy+25, text="You", font=("Segoe UI", 10, "bold"), fill="#2980B9")

        # Draw Ambulance
        ax, ay = self.ambulance_pos
        self.ambu_text = self.canvas.create_text(ax, ay, text="🚑", font=("Arial", 20))
        self.ambu_label = self.canvas.create_text(ax, ay-25, text="Ambulance", font=("Segoe UI", 10, "bold"), fill="#C0392B")

    def beep_siren(self):
        """Play a dual-tone siren sound using Windows built-in winsound."""
        self.siren_playing = True
        while self.siren_playing and self.is_running:
            # High Tone
            if self.siren_playing: winsound.Beep(900, 400) 
            time.sleep(0.05)
            # Low Tone
            if self.siren_playing: winsound.Beep(700, 400)
            time.sleep(0.05)

    def trigger_alert(self):
        """Visual and audio alerts when ambulance enters the 1km radius."""
        self.alert_triggered = True
        self.status_label.config(text="CRITICAL: AMBULANCE WITHIN 1 KM! CLEAR THE ROAD!", fg="#E74C3C")
        self.canvas.itemconfig(self.radius_circle, outline="#C0392B", width=4, dash=(1,))
        self.canvas.itemconfig(self.zone_text, text="🚨 WARNING: EMERGENCY VEHICLE APPROACHING! 🚨", fill="#C0392B")
        
        # Start sound thread
        self.siren_thread = threading.Thread(target=self.beep_siren, daemon=True)
        self.siren_thread.start()

    def clear_alert(self, destination_reached=False):
        """Stop alerts when ambulance passes out of range or stops."""
        self.alert_triggered = False
        self.siren_playing = False
        
        if destination_reached:
            self.status_label.config(text="Status: Arrived at Hospital", fg="#27ae60")
        else:
            self.status_label.config(text="Status: EV Passed 1 KM - Normal Traffic", fg="#2ECC71")
            
        self.canvas.itemconfig(self.radius_circle, outline="#E74C3C", width=2, dash=(8, 8))
        self.canvas.itemconfig(self.zone_text, text="1 KM Alert Zone", fill="#E74C3C")

    def toggle_simulation(self):
        if not self.is_running:
            # Start Simulation
            self.ambulance_pos = list(self.start_pos)
            self.alert_triggered = False
            self.is_running = True
            
            self.btn.config(text="Stop / Reset Simulation", bg="#E74C3C", activebackground="#C0392B")
            self.status_label.config(text="Status: Dispatching Ambulance...", fg="#3498DB")
            self.move_ambulance()
        else:
            # Stop Simulation
            self.is_running = False
            self.siren_playing = False
            
            # Reset UI Elements
            self.btn.config(text="Start Simulation", bg="#27AE60", activebackground="#2ECC71")
            self.status_label.config(text="Status: Idle", fg="#BDC3C7")
            self.dist_label.config(text="Distance to User: -- km")
            
            self.ambulance_pos = list(self.start_pos)
            self.update_ambulance_ui()
            self.clear_alert()

    def update_ambulance_ui(self):
        ax, ay = self.ambulance_pos
        self.canvas.coords(self.ambu_text, ax, ay)
        self.canvas.coords(self.ambu_label, ax, ay-25)

    def move_ambulance(self):
        if not self.is_running:
            return
            
        # Target calculations
        target_x, target_y = self.ambulance_target
        current_x, current_y = self.ambulance_pos
        
        dx = target_x - current_x
        dy = target_y - current_y
        dist_to_target = math.hypot(dx, dy)
        
        if dist_to_target < 2:
            # Reached destination
            self.is_running = False
            self.clear_alert(destination_reached=True)
            self.btn.config(text="Start Simulation", bg="#27AE60", activebackground="#2ECC71")
            return
            
        # Move step (Speed)
        speed = 2.5
        self.ambulance_pos[0] += (dx / dist_to_target) * speed
        self.ambulance_pos[1] += (dy / dist_to_target) * speed
        
        self.update_ambulance_ui()
        
        # Calculate distance to user vehicle
        dist_to_user_px = math.hypot(self.user_pos[0] - self.ambulance_pos[0], 
                                     self.user_pos[1] - self.ambulance_pos[1])
                                     
        dist_km = dist_to_user_px / self.km_pixels
        self.dist_label.config(text=f"Distance to User: {dist_km:.2f} km")
        
        # Check Alert Logic
        if dist_km <= 1.0:
            if not self.alert_triggered:
                self.trigger_alert()
        else:
            if self.alert_triggered:
                self.clear_alert()
                
        # Loop animation (about 30 FPS)
        self.root.after(30, self.move_ambulance)
        
if __name__ == "__main__":
    root = tk.Tk()
    app = AmbuSenseApp(root)
    root.mainloop()
