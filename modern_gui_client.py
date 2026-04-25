# Code: 2
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
import os
import tkinter as tk
from tkinter import filedialog, messagebox
import customtkinter as ctk
from datetime import datetime
from PIL import Image
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import serialization, hashes

# Appearance Settings
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

# 1. Encryption Engine (AES-GCM)
class SecureMessenger:
    def __init__(self):
        self.aesgcm = None

    def set_key(self, key: bytes):
        self.aesgcm = AESGCM(key)

    def encrypt(self, plaintext: str) -> bytes:
        nonce = os.urandom(12) 
        ct = self.aesgcm.encrypt(nonce, plaintext.encode('utf-8'), None)
        return nonce + ct 

    def decrypt(self, ciphertext: bytes) -> str:
        nonce = ciphertext[:12]
        ct = ciphertext[12:]
        plaintext = self.aesgcm.decrypt(nonce, ct, None)
        return plaintext.decode('utf-8')

# 2. Main GUI Application
class SentinelChatApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        self.username = self.get_user_name()
        self.other_username = "Other User"
        
        # Window Configuration
        self.title(f"Sentinel Messenger - {self.username} - Project: Encrypted Chat App - Group 3 | IMSIU")
        self.geometry("950x600")
        
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        # Variables
        self.messenger = SecureMessenger()
        self.aes_key_established = False
        self.client_socket = None
        self.total_data_bytes = 0 
        
        # RSA Key Generation
        self.private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
        self.public_key = self.private_key.public_key()
        self.pub_key_bytes = self.public_key.public_bytes(
            encoding=serialization.Encoding.PEM, format=serialization.PublicFormat.SubjectPublicKeyInfo
        )

        # Load Logo Image
        self.load_logo()
        
        self.setup_ui()
        self.connect_to_server()

    def get_user_name(self):
        dialog = ctk.CTkInputDialog(text="Enter your full name to join the secure chat:", title="Login")
        name = dialog.get_input()
        return name if name and name.strip() else f"User_{os.urandom(2).hex()}"

    def load_logo(self):
        """Load logo2.png and prepare it for the UI"""
        try:
            pil_image = Image.open("logo2.png")
            # Adjusted size to fit the sidebar top area
            self.logo_image = ctk.CTkImage(light_image=pil_image, dark_image=pil_image, size=(160, 90))
        except FileNotFoundError:
            self.logo_image = None
            print("Warning: logo2.png not found.")

    def setup_ui(self):
        # --- Side Panel ---
        self.sidebar = ctk.CTkFrame(self, width=280, corner_radius=0)
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        
        # 1. Logo Image at the very top (Red Mark Position)
        if hasattr(self, 'logo_image') and self.logo_image:
            self.logo_pic_label = ctk.CTkLabel(self.sidebar, image=self.logo_image, text="")
            self.logo_pic_label.pack(pady=(20, 0))

        # 2. Text Logo underneath the image
        self.logo_text_label = ctk.CTkLabel(self.sidebar, text="🔒 Sentinel Messenger", font=ctk.CTkFont(size=20, weight="bold"))
        self.logo_text_label.pack(pady=(15, 5), padx=20)
        
        self.group_tag = ctk.CTkLabel(self.sidebar, text="Project Team (Group 3 - IMSIU)", text_color="#1f6aa5", font=ctk.CTkFont(size=12, weight="bold"))
        self.group_tag.pack(pady=(0, 25))
        
        # Data Counter (Orange)
        self.counter_frame = ctk.CTkFrame(self.sidebar, fg_color="#2b2b2b", corner_radius=12)
        self.counter_frame.pack(pady=15, padx=20, fill="x")
        
        self.counter_title = ctk.CTkLabel(self.counter_frame, text="Network Traffic (Secure):", font=ctk.CTkFont(size=11))
        self.counter_title.pack(pady=(8, 2))
        
        self.counter_val = ctk.CTkLabel(self.counter_frame, text="0.00 KB", font=ctk.CTkFont(size=18, weight="bold"), text_color="#FF9500") 
        self.counter_val.pack(pady=(0, 8))

        # Security Status Labels
        self.status_box = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        self.status_box.pack(pady=10, padx=25, fill="x")
        
        self.rsa_status = ctk.CTkLabel(self.status_box, text="● RSA Encryption: Ready", text_color="#2CC985", font=ctk.CTkFont(size=12))
        self.rsa_status.pack(anchor="w")
        
        self.aes_status = ctk.CTkLabel(self.status_box, text="● AES-256 Key: Waiting...", text_color="#FF6C6C", font=ctk.CTkFont(size=12))
        self.aes_status.pack(anchor="w", pady=5)

        # Team Credits
        self.credits_frame = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        self.credits_frame.pack(side="bottom", pady=25, padx=25, fill="x")
        
        credits_text = (
            "Project Team (Group 3 - IMSIU):\n \n- Mojtaba Al-Jaafar\n \n- Anas Al-Hadyan\n \n- Abdullah Al-Qahtani\n \n- Muhammad Al-Hadyan"
        )
        self.team_label = ctk.CTkLabel(self.credits_frame, text=credits_text, font=ctk.CTkFont(size=11), justify="left", text_color="gray")
        self.team_label.pack(anchor="w")

        # --- MAIN CHAT AREA ---
        self.main_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.main_frame.grid(row=0, column=1, sticky="nsew", padx=20, pady=20)
        self.main_frame.grid_rowconfigure(0, weight=1)
        self.main_frame.grid_columnconfigure(0, weight=1)

        self.chat_display = ctk.CTkTextbox(self.main_frame, font=ctk.CTkFont(size=14))
        self.chat_display.grid(row=0, column=0, sticky="nsew", pady=(0, 15))
        self.chat_display.configure(state='disabled')
        
        self.chat_display.tag_config("me", justify="right", foreground="#3b8ed0")
        self.chat_display.tag_config("other", justify="left", foreground="#2CC985")
        self.chat_display.tag_config("system", justify="center", foreground="gray")

        # Input Frame
        self.input_area = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        self.input_area.grid(row=1, column=0, sticky="ew")
        self.input_area.grid_columnconfigure(0, weight=1)

        self.msg_entry = ctk.CTkEntry(self.input_area, placeholder_text="Write your encrypted message...", font=ctk.CTkFont(size=14))
        self.msg_entry.grid(row=0, column=0, sticky="ew", padx=(0, 15), ipady=7)
        self.msg_entry.bind("<Return>", self.send_message)

        self.send_btn = ctk.CTkButton(self.input_area, text="Send 🚀", width=100, command=self.send_message)
        self.send_btn.grid(row=0, column=1, ipady=7)

    # --- Logic Methods ---
    def update_data_counter(self, size_bytes):
        self.total_data_bytes += size_bytes
        kb_size = self.total_data_bytes / 1024
        self.counter_val.configure(text=f"{kb_size:.2f} KB")

    def insert_chat(self, text, tag):
        self.chat_display.configure(state='normal')
        self.chat_display.insert(tk.END, text + "\n\n", tag)
        self.chat_display.configure(state='disabled')
        self.chat_display.yview(tk.END)

    def connect_to_server(self):
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self.client_socket.connect(('127.0.0.1', 5555))
            self.insert_chat(f"[SYSTEM] Establishing secure tunnel...", "system")
            self.client_socket.sendall(b'PUBKEY:' + self.pub_key_bytes)
            threading.Thread(target=self.receive_messages, daemon=True).start()
        except:
            messagebox.showerror("Error", "Sentinel Network unreachable.")
            self.destroy()

    def receive_messages(self):
        while True:
            try:
                data = self.client_socket.recv(4096)
                if not data: break
                self.update_data_counter(len(data))

                if data.startswith(b'PUBKEY:'):
                    other_pub_key = serialization.load_pem_public_key(data[7:])
                    if not self.aes_key_established:
                        new_aes_key = AESGCM.generate_key(bit_length=256)
                        self.messenger.set_key(new_aes_key)
                        self.aes_key_established = True
                        enc_key = other_pub_key.encrypt(
                            new_aes_key, padding.OAEP(mgf=padding.MGF1(hashes.SHA256()), algorithm=hashes.SHA256(), label=None)
                        )
                        self.client_socket.sendall(b'AESKEY:' + enc_key)
                        self.aes_status.configure(text="● AES-256: Secured (E2EE)", text_color="#2CC985")
                        
                        enc_name = self.messenger.encrypt(f"NAME_SYNC:{self.username}")
                        self.client_socket.sendall(b'MSG:' + enc_name)

                elif data.startswith(b'AESKEY:'):
                    dec_key = self.private_key.decrypt(
                        data[7:], padding.OAEP(mgf=padding.MGF1(hashes.SHA256()), algorithm=hashes.SHA256(), label=None)
                    )
                    self.messenger.set_key(dec_key)
                    self.aes_key_established = True
                    self.aes_status.configure(text="● AES-256: Secured (E2EE)", text_color="#2CC985")
                    
                    enc_name = self.messenger.encrypt(f"NAME_SYNC:{self.username}")
                    self.client_socket.sendall(b'MSG:' + enc_name)

                elif data.startswith(b'MSG:'):
                    dec_msg = self.messenger.decrypt(data[4:])
                    
                    if dec_msg.startswith("NAME_SYNC:"):
                        self.other_username = dec_msg[10:]
                        self.insert_chat(f"[SYSTEM] Secure channel active with: {self.other_username}", "system")
                    else:
                        t = datetime.now().strftime("%H:%M")
                        self.insert_chat(f"{self.other_username} [{t}]:\n{dec_msg}", "other")
            except: break

    def send_message(self, event=None):
        msg = self.msg_entry.get().strip()
        if not msg or not self.aes_key_established: return
        
        t = datetime.now().strftime("%H:%M")
        self.insert_chat(f"You [{t}]:\n{msg}", "me")
        self.msg_entry.delete(0, tk.END)
        
        enc_msg = self.messenger.encrypt(msg)
        packet = b'MSG:' + enc_msg
        self.client_socket.sendall(packet)
        self.update_data_counter(len(packet))

if __name__ == "__main__":
    app = SentinelChatApp()
    app.mainloop()