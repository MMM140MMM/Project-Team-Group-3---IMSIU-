# Sentinel Messenger - Secure E2EE Chat Application

This project provides a secure environment for messaging using advanced encryption algorithms. It ensures total privacy through a zero-trust architecture where even the routing server cannot read the messages.

## 🛠 Technical Features

* **Strong Encryption (E2EE):** Implements **RSA** (2048-bit) for secure key exchange and **AES-256 (GCM)** for fast, real-time message encryption.
* **Blind Server Architecture:** The server routes traffic but cannot decrypt the payloads, ensuring true zero-trust communication.
* **Graphical User Interface (GUI):** A modern, dark-themed interface built using **CustomTkinter**.
* **Python Powered:** Developed entirely in Python, following cybersecurity best practices.

## 📦 Prerequisites & Installation

To run this project successfully, all files and libraries must be set up correctly before execution.

1. **Download the Repository:** Ensure that all Python scripts and image files (`logo.png`, `logo2.png`) are downloaded and placed in the **exact same folder**. Do not change the file names, as the GUI depends on them.
2. **Open in an IDE:** Open the entire **Folder/Directory** (not just the individual files) in a code editor like Visual Studio Code.
3. **Install Dependencies:** Run the following command in the terminal to install all required libraries:
   ```bash
   pip install customtkinter cryptography pillow
pip install pycryptodome requests
