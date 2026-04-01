# ALEJANDRO ÁLVAREZ 31/03/2026
# https://github.com/AlejandroAP98
# SEQPASTE v1.0
# Hecho con ayuda de IA (gemini)

import customtkinter as ctk
import pyperclip
import threading
import time
import pyautogui
from pynput import keyboard

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

class Tooltip:
    def __init__(self, widget, text):
        self.widget = widget
        self.text = text
        self.tip_window = None

    def toggle(self):
        if self.tip_window:
            self.hide_tip()
        else:
            self.show_tip()

    def show_tip(self):
        if self.tip_window or not self.text: return
        x = self.widget.winfo_rootx() + 25
        y = self.widget.winfo_rooty() + 25
        self.tip_window = tw = ctk.CTkToplevel(self.widget)
        tw.wm_overrideredirect(True)
        tw.wm_geometry(f"+{x}+{y}")
        tw.attributes("-topmost", True)
        tw.bind("<Button-1>", lambda e: self.hide_tip())
        label = ctk.CTkLabel(tw, text=self.text, justify="left", fg_color="#333333", 
                            text_color="white", corner_radius=6, padx=10, pady=8, 
                            font=("Segoe UI", 11))
        label.pack()

    def hide_tip(self):
        if self.tip_window:
            self.tip_window.destroy()
            self.tip_window = None

class SeqPaste(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        self.data_lock = threading.Lock()
        self.MAX_QUEUE_SIZE = 50 

        try:
            import os, sys
            base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
            icon_path = os.path.join(base_path, "logo.ico")
            self.iconbitmap(icon_path)
        except:
            pass

        self.title("SeqPaste")
        self.geometry("380x640")
        self.resizable(False, False)
        self.attributes('-topmost', True)
        
        self.queue = []
        self.current_index = 0
        self.last_copied = ""

        # UI Setup
        self.header_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.header_frame.pack(fill="x", padx=20, pady=(15, 0))
        self.font_ui = ctk.CTkFont(family="Segoe UI Variable Display", size=13)
        self.font_content = ctk.CTkFont(family="Consolas", size=12)
        self.label_titulo = ctk.CTkLabel(self.header_frame, text="LISTA EN BUCLE", font=(None, 18, "bold"), text_color="#3B8ED0")
        self.label_titulo.pack(side="left")
        
        self.btn_help = ctk.CTkLabel(self.header_frame, text="?", width=25, height=25,
                                    fg_color="#3B8ED0", corner_radius=12,
                                    font=(None, 12, "bold"), cursor="hand2")
        self.btn_help.pack(side="right")

        texto_ayuda = (
            "FUNCIONAMIENTO\n\n"
            "Ctrl+C: Agrega automáticamente (máx. 50).\n"
            "Tecla F8: Pega el ítem [SIGUIENTE].\n"
            "Clic en Tarjeta: Pega ese ítem específico.\n"
            "Tecla F9: Recupera la ventana.\n"
            "Limpiar todo: Reinicia la secuencia."
        )
        
        self.scroll_frame = ctk.CTkScrollableFrame(self, width=340, height=400, 
                                                 fg_color="#2B2B2B", 
                                                 label_text="Texto copiado")
        self.scroll_frame.pack(pady=4, padx=10, fill="both", expand=True)
        
        self.btn_clear = ctk.CTkButton(self, text="LIMPIAR TODO", fg_color="#C0392B", 
                                      hover_color="#E74C3C", command=self.clear_queue)
        self.btn_clear.pack(pady=10)
        
        self.info_label = ctk.CTkLabel(self, text='💡 F8: Pegar | F9: Mostrar 💡', font=("Segoe UI", 12), text_color="gray")
        self.info_label.pack(pady=2)

        self.tooltip = Tooltip(self.btn_help, texto_ayuda)
        self.btn_help.bind("<Button-1>", lambda e: [self.tooltip.toggle(), "break"][1])
        self.bind("<Button-1>", lambda e: self.tooltip.hide_tip(), add="+")
        self.scroll_frame.bind("<Button-1>", lambda e: self.tooltip.hide_tip(), add="+")

        threading.Thread(target=self.monitor_clipboard, daemon=True).start()
        threading.Thread(target=self.start_keyboard_listener, daemon=True).start()

    def update_display(self):
        with self.data_lock:
            queue_copy = list(self.queue)
            current_idx = self.current_index

        for widget in self.scroll_frame.winfo_children():
            widget.destroy()

        if not queue_copy:
            lbl = ctk.CTkLabel(self.scroll_frame, text="Haz CRTL + C en algún texto para empezar...", font=self.font_ui)
            lbl.pack(pady=20)
            return

        next_card_widget = None 

        for i, text in enumerate(queue_copy):
            is_next = (i == current_idx)
            bg_color = "#1A3A5A" if is_next else "#2B2B2B"
            hover_color = "#244A73" if is_next else "#383838" 
            border_color = "#3B8ED0" if is_next else "#404040"

            card = ctk.CTkFrame(self.scroll_frame, fg_color=bg_color, border_width=2 if is_next else 1,
                               border_color=border_color, corner_radius=8)
            card.pack(fill="x", pady=8, padx=5)

            if is_next: next_card_widget = card

            card.configure(cursor="hand2")
            lbl_idx = ctk.CTkLabel(card, text=f"ITEM {i+1}" + (" [SIGUIENTE]" if is_next else ""), 
                                  font=(None, 11, "bold"), 
                                  text_color="#3B8ED0" if is_next else "#808080", cursor="hand2") 
            lbl_idx.pack(anchor="w", padx=12, pady=(8, 2))

            resumen = text.replace('\n', ' ').strip()[:150]
            if len(text) > 150: resumen += "..."
            
            lbl_txt = ctk.CTkLabel(card, text=resumen, font=self.font_content,
                                  justify="left", wraplength=300, anchor="w", cursor="hand2") 
            lbl_txt.pack(anchor="w", padx=12, pady=(0, 12), fill="x")

            # Binds de eventos
            for w in [card, lbl_idx, lbl_txt]:
                w.bind("<Enter>", lambda e, c=card, h=hover_color: c.configure(fg_color=h))
                w.bind("<Leave>", lambda e, c=card, b=bg_color: c.configure(fg_color=b))
                w.bind("<Button-1>", lambda e, idx=i: self.on_card_click(idx))

        if next_card_widget:
            self.after(100, lambda: self.scroll_to_widget(next_card_widget))

    def scroll_to_widget(self, widget):
        self.update_idletasks()
        try:
            y_widget = widget.winfo_y()
            total_h = self.scroll_frame._parent_canvas.bbox("all")[3]
            if total_h > 0:
                self.scroll_frame._parent_canvas.yview_moveto(y_widget / total_h)
        except: pass

    def on_card_click(self, index):
        with self.data_lock:
            if index < len(self.queue):
                item = self.queue[index]
                self.current_index = (index + 1) % len(self.queue)
            else: return

        self.withdraw()
        time.sleep(0.2)
        pyperclip.copy(item)
        self.last_copied = item
        
        pyautogui.hotkey('ctrl', 'v')
        time.sleep(0.1) 
        
        self.after(400, self.deiconify)
        self.update_display()

    def monitor_clipboard(self):
        while True:
            try:
                current = pyperclip.paste()
                if current != self.last_copied and current.strip() != "":
                    with self.data_lock:
                        if not self.queue or current != self.queue[-1]:
                            self.last_copied = current
                            self.queue.append(current)

                            if len(self.queue) > self.MAX_QUEUE_SIZE:
                                self.queue.pop(0)
                                if self.current_index > 0:
                                    self.current_index -= 1
                                    
                            self.after(0, self.update_display)
            except: pass
            time.sleep(0.5)

    def paste_next_sequential(self):
        with self.data_lock:
            if not self.queue: return
            item = self.queue[self.current_index]
            self.current_index = (self.current_index + 1) % len(self.queue)
            
        pyperclip.copy(item)
        self.last_copied = item
        
        time.sleep(0.05) 
        pyautogui.hotkey('ctrl', 'v')
        
        self.after(0, self.update_display)

    def clear_queue(self):
        with self.data_lock:
            self.queue = []
            self.current_index = 0
        self.update_display()

    def start_keyboard_listener(self):
        def on_press(key):
            try:
                if key == keyboard.Key.f8:
                    threading.Thread(target=self.paste_next_sequential, daemon=True).start()
                elif key == keyboard.Key.f9:
                    self.after(0, self.deiconify)
            except: pass
        with keyboard.Listener(on_press=on_press) as listener:
            listener.join()

if __name__ == "__main__":
    app = SeqPaste()
    app.mainloop()