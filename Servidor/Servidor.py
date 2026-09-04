# -*- coding: utf-8 -*-
import threading
import socket
import mysql.connector as mysql
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


ORIGEN = "localhost"
USUARIO = "root"
CONTRASENA = "TU_CONTRASEÑA"
BASEDATOS = "juego_app"

CORREO_SERVIDOR = "tu_correo@gmail.com"
CONTRASENA_EMAIL = "TU_CONTRASEÑA_DE_APLICACION"

nicknames = {}
jugadas = {}
sockets = {}

lock = threading.Lock()
ronda_activa = False

def enviar(id_cliente, mensaje):
    try:
        if id_cliente in sockets:
            sockets[id_cliente].send((mensaje + "\n").encode("utf-8"))
    except Exception as e:
        print(f"Error enviando a {id_cliente}:", e)
        with lock:
            if id_cliente in sockets:
                sockets[id_cliente].close()
                del sockets[id_cliente]


def guardar_resultado(ganador, perdedor):
    try:
        BD = mysql.connect(host=ORIGEN, user=USUARIO, passwd=CONTRASENA, db=BASEDATOS)
        Cursor = BD.cursor()
        Cursor.callproc("registrar_resultado", [ganador, perdedor])
        BD.commit()
        BD.close()
    except Exception as e:
        print("Error BD:", e)

def obtener_resultados():
    try:
        BD = mysql.connect(host=ORIGEN, user=USUARIO, passwd=CONTRASENA, db=BASEDATOS)
        Cursor = BD.cursor()
        Cursor.execute("""
            SELECT nickname, victorias, derrotas, (victorias + derrotas)
            FROM jugadores
            ORDER BY victorias DESC
        """)
        data = Cursor.fetchall()
        BD.close()
        return data
    except:
        return []

def obtener_partidas():
    try:
        BD = mysql.connect(host=ORIGEN, user=USUARIO, passwd=CONTRASENA, db=BASEDATOS)
        Cursor = BD.cursor()
        Cursor.execute("""
            SELECT nickname_ganador, nickname_perdedor, fecha_hora
            FROM partidas
            ORDER BY fecha_hora DESC
        """)
        data = Cursor.fetchall()
        BD.close()
        return data
    except:
        return []


def enviar_correo(destino):
    try:
        filas = obtener_resultados()
        partidas = obtener_partidas()

        tabla1 = ""
        for f in filas:
            tabla1 += f"""
            <tr>
                <td>{str(f[0]).strip()}</td>
                <td>{f[1]}</td>
                <td>{f[2]}</td>
                <td>{f[3]}</td>
            </tr>
            """

        tabla2 = ""
        for p in partidas:
            tabla2 += f"""
            <tr>
                <td>{str(p[0]).strip()}</td>
                <td>{str(p[1]).strip()}</td>
                <td>{p[2]}</td>
            </tr>
            """

        cuerpo = f"""
        <html>
        <body>
        <h2>Resultados - Piedra Papel Tijera</h2>

        <h3>Ranking</h3>
        <table border="1">
        <tr>
            <th>Jugador</th><th>Victorias</th><th>Derrotas</th><th>Partidas</th>
        </tr>
        {tabla1}
        </table>

        <h3>Historial</h3>
        <table border="1">
        <tr>
            <th>Ganador</th><th>Perdedor</th><th>Fecha</th>
        </tr>
        {tabla2}
        </table>

        </body>
        </html>
        """

        msg = MIMEMultipart()
        msg['From'] = CORREO_SERVIDOR
        msg['To'] = destino
        msg['Subject'] = "Resultados PPT"
        msg.attach(MIMEText(cuerpo, 'html'))

        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(CORREO_SERVIDOR, CONTRASENA_EMAIL)
        server.sendmail(CORREO_SERVIDOR, destino, msg.as_string())
        server.quit()

        return True

    except Exception as e:
        print("Error correo:", e)
        return False


def determinar_ganador(j1, j2):
    if j1 == j2:
        return "empate"
    if (j1, j2) in [("piedra","tijera"),("tijera","papel"),("papel","piedra")]:
        return "cliente1"
    return "cliente2"

def procesar_jugadas_thread(j1, j2):
    global ronda_activa

    try:
        r = determinar_ganador(j1, j2)

        if r == "empate":
            enviar("cliente1", f"EMPATE|{j1}|{j2}")
            enviar("cliente2", f"EMPATE|{j1}|{j2}")

        elif r == "cliente1":
            enviar("cliente1", f"GANASTE|{j1}|{j2}")
            enviar("cliente2", f"PERDISTE|{j1}|{j2}")
            guardar_resultado(nicknames["cliente1"], nicknames["cliente2"])

        else:
            enviar("cliente1", f"PERDISTE|{j1}|{j2}")
            enviar("cliente2", f"GANASTE|{j1}|{j2}")
            guardar_resultado(nicknames["cliente2"], nicknames["cliente1"])

    except Exception as e:
        print("ERROR EN JUEGO:", e)

    finally:
        with lock:
            jugadas["cliente1"] = None
            jugadas["cliente2"] = None
            ronda_activa = True

def manejar_cliente(id_cliente, sock, addr):
    global ronda_activa
    print("Conectado:", id_cliente, addr)

    try:
        while True:
            msg = sock.recv(1024).decode("utf-8")
            if not msg:
                break

            partes = msg.strip().split("|")
            cmd = partes[0]

            if cmd == "JUGADA":
                with lock:
                    if not ronda_activa:
                        continue  # 🔥 NO DESCONECTA

                    jugadas[id_cliente] = partes[1].strip()

                    if (
                        jugadas.get("cliente1") is not None and
                        jugadas.get("cliente2") is not None
                    ):
                        j1 = jugadas["cliente1"]
                        j2 = jugadas["cliente2"]

                        ronda_activa = False

                        threading.Thread(
                            target=procesar_jugadas_thread,
                            args=(j1, j2),
                            daemon=True
                        ).start()

            elif cmd == "CORREO":
                destino = partes[1]
                exito = enviar_correo(destino)

                if exito:
                    enviar(id_cliente, "CORREO_OK")
                else:
                    enviar(id_cliente, "CORREO_ERROR")

            elif cmd == "cerrar":
                break

    except Exception as e:
        print("Error:", e)

    finally:
        print("Desconectado:", id_cliente)
        sock.close()

        with lock:
            sockets.pop(id_cliente, None)
            jugadas.pop(id_cliente, None)
            nicknames.pop(id_cliente, None)


if __name__ == "__main__":
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    server.bind(("0.0.0.0", 1234))
    server.listen(5)

    print("Servidor listo...")

    while True:
        sock, addr = server.accept()
        print("Nueva conexión:", addr)

        try:
            msg = sock.recv(1024).decode("utf-8")
            partes = msg.strip().split("|")

            # =========================
            # SOLO CORREO
            # =========================
            if partes[0] == "SOLO_CORREO":
                id_cliente = "correo_" + str(addr[1])

                with lock:
                    sockets[id_cliente] = sock

                sock.send(("LISTO_CORREO\n").encode("utf-8"))

                threading.Thread(
                    target=manejar_cliente,
                    args=(id_cliente, sock, addr),
                    daemon=True
                ).start()

            # =========================
            # JUGADORES
            # =========================
            elif partes[0] == "NICKNAME":

                with lock:
                    if "cliente1" not in sockets:
                        id_cliente = "cliente1"
                    elif "cliente2" not in sockets:
                        id_cliente = "cliente2"
                    else:
                        sock.send(("LLENO\n").encode("utf-8"))
                        sock.close()
                        continue

                    sockets[id_cliente] = sock
                    jugadas[id_cliente] = None  # 🔥 CORREGIDO
                    nicknames[id_cliente] = partes[1].strip()

                enviar(id_cliente, "NICKNAME_OK")

                if "cliente1" in sockets and "cliente2" in sockets:
                    enviar("cliente1", "INICIO|Ambos jugadores conectados")
                    enviar("cliente2", "INICIO|Ambos jugadores conectados")

                    with lock:
                        ronda_activa = True  # 🔥 ACTIVAR RONDA

                threading.Thread(
                    target=manejar_cliente,
                    args=(id_cliente, sock, addr),
                    daemon=True
                ).start()

        except:
            sock.close()