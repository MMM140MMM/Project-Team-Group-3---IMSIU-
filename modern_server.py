# Code: 1
# GROUP MEMBERS: 3
# Project Idea:Simple Encrypted Chat App
# =====================================================================
# Students:                                     # Academic Number
# 1- Mojtaba Muhammad Al-Jaafar                 1- 446001613
# 2- Muhammad Mishal Al-Hadyan                  2- 446001758
# 3- Abdullah Sultan Al-Qahtani                 3- 446001579
# 4- Anas Abdulmohsen Al-Hadyan                 4- 446017319 
# =====================================================================

import socket
import threading
import tkinter as tk
from tkinter import messagebox
import customtkinter as ctk
from datetime import datetime
from PIL import Image

# Set appearance mode and color theme
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

class SentinelServerDashboard(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        self.title("Sentinel Server Dashboard - Project: Encrypted Chat App - Group 3 | IMSIU")
        self.geometry("750x650") # Increased height for the legend
        
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        # Server Variables
        self.HOST = '127.0.0.1'
        self.PORT = 5555
        self.clients = []
        self.server_socket = None
        self.is_running = False

        self.load_logo()
        self.setup_ui()

    def load_logo(self):
        try:
            pil_image = Image.open("logo.png")
            self.logo_image = ctk.CTkImage(light_image=pil_image, dark_image=pil_image, size=(150, 80))
        except FileNotFoundError:
            self.logo_image = None
            print("Warning: logo.png not found.")

    def setup_ui(self):
        # --- LEFT PANEL (Controls & Branding) ---
        self.sidebar = ctk.CTkFrame(self, width=220, corner_radius=0)
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        
        if self.logo_image:
            self.logo_label = ctk.CTkLabel(self.sidebar, image=self.logo_image, text="")
            self.logo_label.pack(pady=(25, 5))
        else:
            self.logo_label = ctk.CTkLabel(self.sidebar, text="🌐 Server ", font=ctk.CTkFont(size=20, weight="bold"))
            self.logo_label.pack(pady=(25, 5), padx=20)
            
        self.brand_title = ctk.CTkLabel(self.sidebar, text="Server \n Sentinel Messenger", font=ctk.CTkFont(size=14, weight="bold"))
        self.brand_title.pack(pady=(0, 20))
        
        # Connection Status
        self.status_label = ctk.CTkLabel(self.sidebar, text="Status: Offline", text_color="gray", font=ctk.CTkFont(weight="bold"))
        self.status_label.pack(pady=5)
        
        self.clients_label = ctk.CTkLabel(self.sidebar, text="Active Nodes: 0", font=ctk.CTkFont(weight="bold"))
        self.clients_label.pack(pady=5)

        # Server Controls
        self.start_btn = ctk.CTkButton(self.sidebar, text="Start Server", fg_color="#2CC985", hover_color="#209662", command=self.start_server_thread)
        self.start_btn.pack(pady=(20, 10), padx=20)
        
        self.stop_btn = ctk.CTkButton(self.sidebar, text="Stop Server", fg_color="#FF6C6C", hover_color="#C94F4F", command=self.stop_server, state="disabled")
        self.stop_btn.pack(pady=10, padx=20)

        # --- MONITOR LEGEND (New Addition) ---
        self.legend_frame = ctk.CTkFrame(self.sidebar, fg_color="#2b2b2b", corner_radius=10)
        self.legend_frame.pack(pady=(30, 10), padx=20, fill="x")
        
        self.legend_title = ctk.CTkLabel(self.legend_frame, text="Monitor Legend:", font=ctk.CTkFont(size=12, weight="bold"))
        self.legend_title.pack(pady=(5, 2), padx=10, anchor="w")

        # Color Key Labels
        ctk.CTkLabel(self.legend_frame, text="● System Status", text_color="#3b8ed0", font=ctk.CTkFont(size=11)).pack(padx=10, anchor="w")
        ctk.CTkLabel(self.legend_frame, text="● Nodes Activity", text_color="#FF9500", font=ctk.CTkFont(size=11)).pack(padx=10, anchor="w")
        ctk.CTkLabel(self.legend_frame, text="● Encrypted Traffic", text_color="#2CC985", font=ctk.CTkFont(size=11)).pack(padx=10, anchor="w")
        ctk.CTkLabel(self.legend_frame, text="● Error Alerts", text_color="#FF6C6C", font=ctk.CTkFont(size=11)).pack(pady=(0, 5), padx=10, anchor="w")

        # Credits
        self.credits_label = ctk.CTkLabel(self.sidebar, text="Project by Group 3 | IMSIU\nCybersecurity Diploma \n\n- Mojtaba Al-Jaafar\n- Anas Al-Hadyan\n- Abdullah Al-Qahtani\n- Muhammad Al-Hadyan", font=ctk.CTkFont(size=10), text_color="gray")
        self.credits_label.pack(side="bottom", pady=10)


        # --- RIGHT PANEL (Traffic Monitor) ---
        self.main_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.main_frame.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)
        self.main_frame.grid_rowconfigure(1, weight=1)
        self.main_frame.grid_columnconfigure(0, weight=1)

        self.monitor_label = ctk.CTkLabel(self.main_frame, text="Sentinel Monitor - Secure Traffic Log", font=ctk.CTkFont(size=16, weight="bold"))
        self.monitor_label.grid(row=0, column=0, sticky="w", pady=(0, 10))

        self.log_display = ctk.CTkTextbox(self.main_frame, font=ctk.CTkFont(family="Courier", size=11)) 
        self.log_display.grid(row=1, column=0, sticky="nsew")
        self.log_display.configure(state='disabled')
        
        # Color Tags Configuration
        self.log_display.tag_config("system", foreground="#3b8ed0")  # Blue
        self.log_display.tag_config("connect", foreground="#FF9500") # Orange
        self.log_display.tag_config("traffic", foreground="#2CC985") # Green
        self.log_display.tag_config("error", foreground="#FF6C6C")   # Red

    def log_event(self, text, tag="system"):
        time_now = datetime.now().strftime("%H:%M:%S")
        self.log_display.configure(state='normal')
        self.log_display.insert(tk.END, f"[{time_now}] {text}\n", tag)
        self.log_display.configure(state='disabled')
        self.log_display.yview(tk.END)

    def fake_decrypt_attempt(self):
        messagebox.showerror("Access Denied", "FATAL ERROR:\nCannot read traffic.\nE2EE Tunnel active.\nPrivate Key not stored on server.")

    # --- SERVER LOGIC ---
    def start_server_thread(self):
        if not self.is_running:
            threading.Thread(target=self.run_server, daemon=True).start()

    def run_server(self):
        self.is_running = True
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        
        try:
            self.server_socket.bind((self.HOST, self.PORT))
            self.server_socket.listen()
            
            self.after(0, lambda: self.start_btn.configure(state="disabled"))
            self.after(0, lambda: self.stop_btn.configure(state="normal"))
            self.after(0, lambda: self.status_label.configure(text=f"Listening on {self.PORT}", text_color="#2CC985"))
            self.after(0, self.log_event, "SYSTEM: Sentinel Server Started...", "system")
            
            while self.is_running:
                try:
                    client_socket, address = self.server_socket.accept()
                    self.clients.append(client_socket)
                    self.after(0, self.update_client_count)
                    self.after(0, self.log_event, f"Secure Node Connected: {address}", "connect")
                    
                    threading.Thread(target=self.handle_client, args=(client_socket, address), daemon=True).start()
                except OSError:
                    break
        except Exception as e:
            self.after(0, self.log_event, f"ERROR: {str(e)}", "error")
            self.stop_server()

    def broadcast(self, encrypted_message, sender_socket):
        for client in self.clients:
            if client != sender_socket:
                try:
                    client.sendall(encrypted_message)
                except:
                    self.remove_client(client)

    def handle_client(self, client_socket, address):
        while self.is_running:
            try:
                encrypted_message = client_socket.recv(1024)
                if encrypted_message:
                    hex_data = encrypted_message.hex()[:40] + "..."
                    self.after(0, self.log_event, f"Routing (E2EE): {hex_data}", "traffic")
                    self.broadcast(encrypted_message, client_socket)
                else:
                    break
            except:
                break
        self.remove_client(client_socket)
        self.after(0, self.log_event, f"Node Disconnected: {address}", "connect")

    def remove_client(self, client_socket):
        if client_socket in self.clients:
            self.clients.remove(client_socket)
            client_socket.close()
            self.after(0, self.update_client_count)

    def update_client_count(self):
        count = len(self.clients)
        self.clients_label.configure(text=f"Active Nodes: {count}")

    def stop_server(self):
        self.is_running = False
        if self.server_socket:
            self.server_socket.close()
        
        for client in self.clients:
            client.close()
        self.clients.clear()
        
        self.update_client_count()
        self.start_btn.configure(state="normal")
        self.stop_btn.configure(state="disabled")
        self.status_label.configure(text="Status: Offline", text_color="gray")
        self.after(0, self.log_event, "SYSTEM: Sentinel Server Stopped.", "system")

if __name__ == "__main__":
    app = SentinelServerDashboard()
    app.mainloop()