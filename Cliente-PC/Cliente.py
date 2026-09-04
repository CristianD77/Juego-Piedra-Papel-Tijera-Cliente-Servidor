# -*- coding: utf-8 -*-

import socket
import threading
import tkinter as tk
from tkinter import messagebox

IP_Servidor = 'IP_DEL_SERVIDOR'
Puerto      = 1234

Nombre_Socket = None
Bandera       = False

# FUNCIONES DE CONEXION
def conectar():
    global Nombre_Socket, Bandera
    try:
        Nombre_Socket = socket.socket()
        Nombre_Socket.connect((IP_Servidor, Puerto))
        Bandera = True
        print("Conectado al servidor")
    except ConnectionRefusedError:
        Bandera = False
        messagebox.showerror("Error", "No se pudo conectar al servidor.\nVerifique que el servidor esté activo.")

def recibir_mensajes():
    '''Hilo que escucha mensajes del servidor constantemente'''
    while Bandera:
        try:
            bytes_a_recibir    = 1024
            mensaje_recibido   = Nombre_Socket.recv(bytes_a_recibir)
            texto              = mensaje_recibido.decode("utf-8")
            procesar_respuesta(texto)
        except:
            break

def enviar_mensaje(mensaje):
    global Bandera
    try:
        if Nombre_Socket is None or not Bandera:
            messagebox.showerror("Error", "No hay conexión con el servidor.")
            return
        paquete = mensaje.encode()
        Nombre_Socket.send(paquete)
    except OSError:
        Bandera = False
        messagebox.showerror("Error", "Se perdió la conexión con el servidor.")

# PROCESAR RESPUESTAS DEL SERVIDOR
def procesar_respuesta(texto):
    partes  = texto.split("|")
    comando = partes[0]

    if comando == "NICKNAME_OK":
        lbl_estado.config(text="Esperando al rival...")

    elif comando == "INICIO":
        lbl_estado.config(text="¡Rival conectado! Elige tu jugada")
        btn_piedra.config(state="normal")
        btn_papel.config(state="normal")
        btn_tijera.config(state="normal")

    elif comando == "GANASTE":
        jugada_propia  = partes[1]
        jugada_rival   = partes[2]
        lbl_resultado.config(
            text="¡GANASTE! Tú: {} | Rival: {}".format(jugada_propia, jugada_rival),
            fg="green")
        btn_piedra.config(state="disabled")
        btn_papel.config(state="disabled")
        btn_tijera.config(state="disabled")
        btn_jugar_nuevo.config(state="normal")

    elif comando == "PERDISTE":
        jugada_propia  = partes[1]
        jugada_rival   = partes[2]
        lbl_resultado.config(
            text="Perdiste. Tú: {} | Rival: {}".format(jugada_propia, jugada_rival),
            fg="red")
        btn_piedra.config(state="disabled")
        btn_papel.config(state="disabled")
        btn_tijera.config(state="disabled")
        btn_jugar_nuevo.config(state="normal")

    elif comando == "EMPATE":
        jugada_propia  = partes[1]
        jugada_rival   = partes[2]
        lbl_resultado.config(
            text="¡Empate! Tú: {} | Rival: {}".format(jugada_propia, jugada_rival),
            fg="orange")
        btn_piedra.config(state="disabled")
        btn_papel.config(state="disabled")
        btn_tijera.config(state="disabled")
        btn_jugar_nuevo.config(state="normal")

    elif comando == "CORREO_OK":
        messagebox.showinfo("Correo", "Resultados enviados exitosamente.")

    elif comando == "CORREO_ERROR":
        messagebox.showerror("Correo", "Error al enviar el correo. Intente nuevamente.")
    elif comando == "LISTO_CORREO":
        messagebox.showinfo("Conexión", "Conectado. Ingresa tu correo.")

# ACCIONES DE LA INTERFAZ
def accion_jugar():
    '''Pantalla de juego'''
    frame_menu.pack_forget()
    frame_juego.pack(pady=20)
    conectar()
    if Bandera:
        hilo = threading.Thread(target=recibir_mensajes, daemon=True)
        hilo.start()

def accion_consultar():
    frame_menu.pack_forget()
    frame_correo.pack(pady=20)
    conectar()
    if Bandera:
        hilo = threading.Thread(target=recibir_mensajes, daemon=True)
        hilo.start()
        # Avisar al servidor que este cliente es solo de consulta
        enviar_mensaje("SOLO_CORREO")

def accion_enviar_nickname():
    nick = entry_nickname.get().strip()
    if nick == "":
        messagebox.showwarning("Aviso", "Ingrese un nickname.")
        return
    lbl_estado.config(text="Conectando...")
    enviar_mensaje("NICKNAME|{}".format(nick))

def accion_jugada(jugada):
    btn_piedra.config(state="disabled")
    btn_papel.config(state="disabled")
    btn_tijera.config(state="disabled")
    lbl_resultado.config(text="Esperando jugada del rival...", fg="black")
    enviar_mensaje("JUGADA|{}".format(jugada))

def accion_jugar_nuevo():
    '''Reinicia la pantalla para jugar otra vez'''
    lbl_resultado.config(text="")
    lbl_estado.config(text="Elige tu jugada")
    btn_piedra.config(state="normal")
    btn_papel.config(state="normal")
    btn_tijera.config(state="normal")
    btn_jugar_nuevo.config(state="disabled")

def accion_enviar_correo():
    correo = entry_correo.get().strip()
    if correo == "":
        messagebox.showwarning("Aviso", "Ingrese un correo.")
        return
    enviar_mensaje("CORREO|{}".format(correo))

def accion_volver_menu():
    frame_juego.pack_forget()
    frame_correo.pack_forget()
    frame_menu.pack(pady=20)

def accion_salir():
    if Nombre_Socket:
        enviar_mensaje("cerrar")
        Nombre_Socket.close()
    ventana.destroy()

# INTERFAZ GRAFICA
ventana = tk.Tk()
ventana.title("Piedra Papel Tijera - Cliente PC")
ventana.geometry("420x420")
ventana.resizable(False, False)

#frame menu
frame_menu = tk.Frame(ventana)
frame_menu.pack(pady=20)

tk.Label(frame_menu, text="Piedra, Papel o Tijera",
         font=("Arial", 18, "bold")).pack(pady=20)

tk.Button(frame_menu, text="Jugar",
          font=("Arial", 13), width=20, bg="#6C63FF", fg="white",
          command=accion_jugar).pack(pady=8)

tk.Button(frame_menu, text="Consultar resultados",
          font=("Arial", 13), width=20, bg="#3B8BD4", fg="white",
          command=accion_consultar).pack(pady=8)

tk.Button(frame_menu, text="Salir",
          font=("Arial", 13), width=20, bg="#E24B4A", fg="white",
          command=accion_salir).pack(pady=8)


frame_juego = tk.Frame(ventana)

tk.Label(frame_juego, text="Ingresa tu nickname:",
         font=("Arial", 12)).pack(pady=5)

entry_nickname = tk.Entry(frame_juego, font=("Arial", 12), width=20)
entry_nickname.pack(pady=5)

tk.Button(frame_juego, text="Confirmar nickname",
          font=("Arial", 11), bg="#6C63FF", fg="white",
          command=accion_enviar_nickname).pack(pady=5)

lbl_estado = tk.Label(frame_juego, text="",
                      font=("Arial", 11), fg="gray")
lbl_estado.pack(pady=5)

frame_botones = tk.Frame(frame_juego)
frame_botones.pack(pady=10)

btn_piedra = tk.Button(frame_botones, text="Piedra",
                       font=("Arial", 12), width=9, state="disabled",
                       command=lambda: accion_jugada("piedra"))
btn_piedra.grid(row=0, column=0, padx=5)

btn_papel = tk.Button(frame_botones, text="Papel",
                      font=("Arial", 12), width=9, state="disabled",
                      command=lambda: accion_jugada("papel"))
btn_papel.grid(row=0, column=1, padx=5)

btn_tijera = tk.Button(frame_botones, text="Tijera",
                       font=("Arial", 12), width=9, state="disabled",
                       command=lambda: accion_jugada("tijera"))
btn_tijera.grid(row=0, column=2, padx=5)

lbl_resultado = tk.Label(frame_juego, text="",
                         font=("Arial", 12, "bold"))
lbl_resultado.pack(pady=10)

btn_jugar_nuevo = tk.Button(frame_juego, text="Jugar otra vez",
                            font=("Arial", 11), bg="#1D9E75", fg="white",
                            state="disabled", command=accion_jugar_nuevo)
btn_jugar_nuevo.pack(pady=5)

tk.Button(frame_juego, text="← Volver al menú",
          font=("Arial", 10), command=accion_volver_menu).pack(pady=5)

# --- FRAME CORREO ---
frame_correo = tk.Frame(ventana)

tk.Label(frame_correo, text="Consultar resultados",
         font=("Arial", 16, "bold")).pack(pady=15)

tk.Label(frame_correo, text="Ingresa tu correo electrónico:",
         font=("Arial", 12)).pack(pady=5)

entry_correo = tk.Entry(frame_correo, font=("Arial", 12), width=25)
entry_correo.pack(pady=5)

tk.Button(frame_correo, text="Enviar resultados",
          font=("Arial", 12), bg="#3B8BD4", fg="white",
          command=accion_enviar_correo).pack(pady=10)

tk.Button(frame_correo, text="← Volver al menú",
          font=("Arial", 10), command=accion_volver_menu).pack(pady=5)

# INICIAR VENTANA
ventana.mainloop()