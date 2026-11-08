import ctypes
import ctypes.wintypes as wt
import ntpath
import os
import re
import time

import psutil
from dotenv import load_dotenv
from pypresence import Presence
from pypresence.exceptions import DiscordNotFound, InvalidID, PipeClosed

INTERVALO = 5  
PROCESO = "packettracer.exe"
RE_ARCHIVO = re.compile(r"^Cisco Packet Tracer - (.+?\.pk[taz])\b", re.IGNORECASE)

user32 = ctypes.windll.user32
EnumWindowsProc = ctypes.WINFUNCTYPE(wt.BOOL, wt.HWND, wt.LPARAM)


def titulos_de_ventana(pids):
    titulos = []

    def callback(hwnd, _):
        if not user32.IsWindowVisible(hwnd):
            return True
        pid = wt.DWORD()
        user32.GetWindowThreadProcessId(hwnd, ctypes.byref(pid))
        if pid.value in pids:
            largo = user32.GetWindowTextLengthW(hwnd)
            if largo:
                buf = ctypes.create_unicode_buffer(largo + 1)
                user32.GetWindowTextW(hwnd, buf, largo + 1)
                titulos.append(buf.value)
        return True

    user32.EnumWindows(EnumWindowsProc(callback), 0)
    return titulos


def estado_packet_tracer():
    procesos = [p for p in psutil.process_iter(["name", "create_time"])
                if (p.info["name"] or "").lower() == PROCESO]
    if not procesos:
        return None

    inicio = int(min(p.info["create_time"] for p in procesos))
    archivo = None
    for titulo in titulos_de_ventana({p.pid for p in procesos}):
        m = RE_ARCHIVO.search(titulo)
        if m:
            archivo = ntpath.basename(m.group(1))
            break
    return archivo, inicio


def conectar(client_id):
    while True:
        try:
            rpc = Presence(client_id)
            rpc.connect()
            print("Conectado a Discord.")
            return rpc
        except DiscordNotFound:
            print("Discord no esta abierto, reintento en 15 s...")
        except InvalidID:
            raise SystemExit("PT_CLIENT_ID inválido: revisa el Application ID en el .env")
        time.sleep(15)


def main():
    load_dotenv()
    client_id = os.getenv("PT_CLIENT_ID")
    if not client_id:
        raise SystemExit("Falta PT_CLIENT_ID en el .env (el Application ID de tu app de Discord)")

    rpc = conectar(client_id)
    ultimo = object()  # fuerza el primer update

    print("Checking Packet Tracer... (Ctrl+C para salir)")
    try:
        while True:
            estado = estado_packet_tracer()
            if estado != ultimo:
                try:
                    if estado is None:
                        rpc.clear()
                        print("Packet Tracer cerrado: actividad borrada.")
                    else:
                        archivo, inicio = estado
                        if archivo and archivo.lower().endswith(".pka"):
                            texto = "Resolviendo una actividad"
                        else:
                            texto = "Armando una topologia de red"
                        nombre = os.path.splitext(archivo)[0] if archivo else None
                        rpc.update(
                            details=nombre[:128] if nombre else "En la pantalla de inicio",
                            state=texto,
                            start=inicio,
                            large_image="packet_tracer",   # nombre del asset subido en el portal
                            large_text="Cisco Packet Tracer",
                        )
                        print(f"Actividad: {archivo or 'sin archivo abierto'}")
                    ultimo = estado
                except (PipeClosed, BrokenPipeError, ConnectionError):
                    print("Se perdio la conexion con dscord, reconectando...")
                    rpc = conectar(client_id)
                    ultimo = object()
            time.sleep(INTERVALO)
    except KeyboardInterrupt:
        pass
    finally:
        try:
            rpc.clear()
            rpc.close()
        except Exception:
            pass


if __name__ == "__main__":
    main()
