# SeqPaste v1.0

**SeqPaste** es una herramienta de productividad ligera diseñada para optimizar flujos de trabajo que requieren el copiado y pegado de múltiples fragmentos de texto de forma secuencial o selectiva. 

Desarrollada en Python utilizando **CustomTkinter**, esta aplicación permite capturar automáticamente el historial del portapapeles y pegarlo de manera fluida mediante atajos de teclado globales.

### Características Principales
* **Captura Inteligente:** Detecta automáticamente cada `Ctrl + C` y lo añade a una lista visual.
* **Pegado Secuencial (F8):** Pega el siguiente ítem de la lista en un bucle infinito, ideal para llenar formularios o bases de datos.
* **Interfaz Moderna:** Diseño oscuro (Fluent/Dark Mode) con tarjetas interactivas y efectos hover.
* **Auto-Scroll:** La lista se desplaza automáticamente para mantener siempre a la vista el ítem activo.
* **Acceso Rápido (F9):** Recupera la ventana instantáneamente si está oculta o minimizada.
* **Portable:** Ejecutable único sin necesidad de instalación.

### Tecnologías utilizadas
* **Python 3.x**
* **CustomTkinter:** Para la interfaz gráfica moderna.
* **Pynput:** Para el manejo de atajos de teclado globales (F8/F9).
* **Pyperclip & PyAutoGUI:** Para la gestión del portapapeles y la simulación de pegado.

---

## Requisitos e Instalación

Para ejecutar el código fuente desde Python, necesitas instalar las siguientes dependencias:

```bash
pip install customtkinter pyperclip pyautogui pynput pyinstaller
```

## Bibliotecas utilizadas:

* CustomTkinter
* Pyperclip
* PyAutoGUI
* Pynput

## Cómo generar el ejecutable (Versión Portable)

Si deseas compilar tu propio archivo .exe independiente, asegúrate de tener el archivo logo.ico en la carpeta raíz y ejecuta el siguiente comando en tu terminal:

```bash
python -m PyInstaller --noconsole --onefile --windowed --icon=logo.ico --add-data "logo.ico;." SeqPaste.py
```

*Desarrollado por Alejandro Álvarez con la asistencia técnica de Gemini (Google AI).*