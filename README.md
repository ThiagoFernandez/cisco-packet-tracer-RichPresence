# cisco-packet-tracer-RichPresence

Muestra en tu actividad de Discord lo que estás haciendo en **Cisco Packet Tracer**: qué archivo
tenés abierto y hace cuánto que estás.

Packet Tracer no trae integración con Discord. Este script hace de puente:

1. Cada 5 segundos busca el proceso `PacketTracer.exe`.
2. Lee el título de su ventana para saber qué `.pkt` / `.pka` tenés abierto.
3. Se lo manda al Discord de tu PC por Rich Presence (IPC local, con
   [pypresence](https://github.com/qwertyquerty/pypresence)).

Cuando cerrás Packet Tracer, la actividad se borra sola.

## Qué se ve en Discord

| Situación                     | Detalle                          | Estado                         |
| ----------------------------- | -------------------------------- | ------------------------------ |
| Packet Tracer sin archivo     | En la pantalla de inicio         | Armando una topologia de red   |
| Un `.pkt` abierto             | nombre del archivo               | Armando una topologia de red   |
| Un `.pka` abierto (actividad) | nombre del archivo               | Resolviendo una actividad      |

Siempre como *Jugando a Cisco Packet Tracer* y con el tiempo transcurrido desde que lo abriste.

## Requisitos

* Windows (lee las ventanas con la API de Windows)
* Python 3.8+ (probado con 3.14)
* Discord de **escritorio** abierto (el de navegador no sirve)
* Probado con Cisco Packet Tracer 9.0

## Instalación

```bash
py -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

## Crear la aplicación de Discord

No hace falta bot ni token: solo una aplicación, cuyo nombre es lo que aparece en tu perfil.

1. En el [Discord Developer Portal](https://discord.com/developers/applications): **New
   Application** y ponele de nombre **Cisco Packet Tracer**.
2. En **General Information**, copiá el **Application ID**.
3. Copiá `.env.example` a `.env` y completalo:

   ```
   PT_CLIENT_ID=tu_application_id
   ```

4. Opcional: en **Rich Presence → Art Assets** subí un ícono (mínimo 512×512) con el nombre
   `packet_tracer`. Puede tardar unos minutos en aparecer.

En Discord tiene que estar activado **Ajustes → Privacidad de actividad → Compartir mi
actividad**.

## Uso

Desde PowerShell, en la carpeta del proyecto:

```bash
.\.venv\Scripts\python.exe main.py
```

Desde bash (Git Bash / MSYS2), con barras normales:

```bash
./.venv/Scripts/python.exe main.py
```

Se queda corriendo y avisa por consola cada cambio. **Ctrl+C** para salir: borra la actividad
antes de cerrarse.

Si Discord no está abierto, reintenta cada 15 segundos. Si lo cerrás con el script corriendo, se
reconecta solo cuando lo volvés a abrir.

### Que arranque con Windows (opcional)

Creá un acceso directo en la carpeta `shell:startup` (Win+R → `shell:startup`) que apunte a:

```
C:\ruta\al\proyecto\.venv\Scripts\pythonw.exe main.py
```

con *Iniciar en* = la carpeta del proyecto. `pythonw.exe` lo corre sin ventana de consola.

## Problemas comunes

| Síntoma                                               | Causa / solución                                                                                         |
| ----------------------------------------------------- | -------------------------------------------------------------------------------------------------------- |
| `Python was not found`                                | `python` es el atajo a la Microsoft Store. Usá `py` o el Python del `.venv`.                             |
| `running scripts is disabled` al activar el `.venv`   | PowerShell bloquea los `.ps1`. No hace falta activarlo: llamá a `.\.venv\Scripts\python.exe` directo.    |
| `Falta PT_CLIENT_ID en el .env`                       | El `.env` no está en la carpeta desde donde corrés el script, o se guardó como `.env.txt`.               |
| `PT_CLIENT_ID inválido`                               | El Application ID está mal copiado.                                                                      |
| Corre pero no aparece nada en Discord                 | Discord abierto en el navegador en vez de escritorio, o *Compartir mi actividad* desactivado.             |
| Aparece la actividad pero sin ícono                   | El asset no se llama `packet_tracer` o todavía no se propagó (esperá unos minutos).                      |
