import socket
import threading
import tkinter as tk
from tkinter import messagebox
import subprocess

server_socket = None
listening = False
current_port = None

def abrir_firewall(port):
    regla = f"PuertoTest_{port}"
    try:
        subprocess.run(
            ["netsh", "advfirewall", "firewall", "add", "rule",
             f"name={regla}", "dir=in", "action=allow", "protocol=TCP", f"localport={port}"],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True
        )
        print(f"✅ Regla de firewall creada: {regla}")
    except Exception as e:
        print("❌ Error al crear regla de firewall:", e)

def eliminar_firewall(port):
    regla = f"PuertoTest_{port}"
    try:
        subprocess.run(
            ["netsh", "advfirewall", "firewall", "delete", "rule", f"name={regla}"],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True
        )
        print(f"🧹 Regla de firewall eliminada: {regla}")
    except Exception as e:
        print("❌ Error al eliminar regla de firewall:", e)

def start_listening():
    global server_socket, listening, current_port
    try:
        port = int(port_entry.get())
        current_port = port

        # Crear regla de firewall
        abrir_firewall(port)

        # Iniciar servidor
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.bind(("", port))
        server_socket.listen(5)
        listening = True
        status_label.config(text=f"✅ Escuchando en puerto {port}")
        threading.Thread(target=accept_connections, daemon=True).start()
    except Exception as e:
        messagebox.showerror("Error", str(e))

def accept_connections():
    global listening
    while listening:
        try:
            client_socket, addr = server_socket.accept()
            mensaje = "✅ Hola, el puerto está abierto y operativo.\r\n"
            client_socket.send(mensaje.encode())
            client_socket.close()
        except:
            break

def stop_listening():
    global server_socket, listening, current_port
    listening = False
    if server_socket:
        server_socket.close()
        server_socket = None
    if current_port:
        if not keep_firewall_var.get():  # Si no está marcado, elimina regla
            eliminar_firewall(current_port)
        else:
            print(f"⚠️ Regla del puerto {current_port} conservada por el usuario.")
        current_port = None
    status_label.config(text="🛑 Detenido")

# --- Interfaz ---
root = tk.Tk()
root.title("Puerto Listener")
root.geometry("260x200")

tk.Label(root, text="Puerto:").pack(pady=5)
port_entry = tk.Entry(root, justify="center")
port_entry.pack()
port_entry.insert(0, "1438")

keep_firewall_var = tk.BooleanVar(value=False)
keep_check = tk.Checkbutton(root, text="Mantener regla de firewall al detener", variable=keep_firewall_var)
keep_check.pack(pady=5)

tk.Button(root, text="▶ Play", command=start_listening, width=10).pack(pady=5)
tk.Button(root, text="⏹ Stop", command=stop_listening, width=10).pack(pady=5)

status_label = tk.Label(root, text="🛑 Detenido")
status_label.pack(pady=5)

root.mainloop()

