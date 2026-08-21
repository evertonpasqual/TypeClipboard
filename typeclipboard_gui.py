#!/usr/bin/env python3
"""
TypeClipboard - digita um texto/senha como se fosse o teclado.

Util para consoles onde Ctrl+C / Ctrl+V nao funciona (noVNC/SPICE do
Proxmox, iDRAC, iLO, VMware, IPMI, VMs em geral).

Autor: Everton Pasqualin
Licenca: MIT
"""

import os
import platform
import sys
import threading
import time
import tkinter as tk
from tkinter import messagebox, ttk

APP_NAME = "TypeClipboard"
VERSION = "1.0.0"

try:
    import pyautogui

    pyautogui.FAILSAFE = False
except Exception as exc:  # pragma: no cover
    pyautogui = None
    IMPORT_ERROR = exc
else:
    IMPORT_ERROR = None


class TypeClipboardApp:
    def __init__(self, root):
        self.root = root
        self.root.title(f"{APP_NAME} {VERSION}")
        self.root.geometry("460x300")
        self.root.resizable(False, False)

        self.running = False
        self.cancelled = False

        self.delay = tk.IntVar(value=5)
        self.press_enter = tk.BooleanVar(value=False)
        self.hide_window = tk.BooleanVar(value=False)
        self.show_text = tk.BooleanVar(value=False)

        self.build_ui()
        self.check_dependencies()

    # ------------------------------------------------------------------ UI
    def build_ui(self):
        frame = ttk.Frame(self.root, padding=18)
        frame.pack(fill="both", expand=True)

        ttk.Label(
            frame,
            text="Digite a senha/texto para enviar",
            font=("Helvetica", 15, "bold"),
        ).pack(pady=(0, 12))

        self.entry = ttk.Entry(frame, show="\u2022", width=42)
        self.entry.pack(pady=(0, 8))
        self.entry.focus()
        self.entry.bind("<Return>", lambda _e: self.start_typing())
        self.root.bind("<Escape>", lambda _e: self.cancel())

        options = ttk.Frame(frame)
        options.pack(fill="x", pady=(0, 10))

        ttk.Checkbutton(
            options, text="Mostrar texto", variable=self.show_text,
            command=self.toggle_show,
        ).grid(row=0, column=0, sticky="w", padx=(0, 14))

        ttk.Checkbutton(
            options, text="Enter no final", variable=self.press_enter,
        ).grid(row=0, column=1, sticky="w")

        ttk.Checkbutton(
            options, text="Esconder janela ao digitar", variable=self.hide_window,
        ).grid(row=1, column=0, columnspan=2, sticky="w", pady=(4, 0))

        delay_row = ttk.Frame(frame)
        delay_row.pack(fill="x", pady=(0, 10))
        ttk.Label(delay_row, text="Contagem regressiva:").pack(side="left")
        ttk.Spinbox(
            delay_row, from_=1, to=30, width=4, textvariable=self.delay,
        ).pack(side="left", padx=6)
        ttk.Label(delay_row, text="segundos").pack(side="left")

        self.status = ttk.Label(
            frame, text="Pronto para digitar", font=("Helvetica", 11)
        )
        self.status.pack(pady=(4, 8))

        self.button = ttk.Button(frame, text="COLAR", command=self.start_typing)
        self.button.pack()

    def toggle_show(self):
        self.entry.config(show="" if self.show_text.get() else "\u2022")

    def check_dependencies(self):
        if pyautogui is None:
            self.button.config(state="disabled")
            self.status.config(text="Erro: pyautogui nao instalado")
            messagebox.showerror(
                APP_NAME,
                "A biblioteca pyautogui nao foi encontrada.\n\n"
                f"Detalhe: {IMPORT_ERROR}\n\n"
                "Instale com:  pip3 install pyautogui",
            )

    # ------------------------------------------------------------- Digitacao
    def start_typing(self):
        if self.running or pyautogui is None:
            return

        text = self.entry.get()
        if not text:
            messagebox.showwarning(APP_NAME, "Digite uma senha ou texto.")
            return

        self.running = True
        self.cancelled = False
        self.button.config(state="disabled", text="Cancelar (Esc)")
        self.button.config(state="normal", command=self.cancel)
        self.entry.config(state="disabled")

        threading.Thread(target=self.run_process, args=(text,), daemon=True).start()

    def cancel(self):
        if self.running:
            self.cancelled = True
            self.update_status("Cancelando...")

    def run_process(self, text):
        for i in range(self.delay.get(), 0, -1):
            if self.cancelled:
                self.finish("Cancelado.")
                return
            self.update_status(f"Clique no campo de destino... {i}s")
            time.sleep(1)

        if self.cancelled:
            self.finish("Cancelado.")
            return

        if self.hide_window.get():
            self.root.after(0, self.root.withdraw)
            time.sleep(0.3)

        self.update_status("Digitando...")
        try:
            pyautogui.write(text, interval=0.02)
            if self.press_enter.get():
                pyautogui.press("enter")
            msg = "Concluido. Pode digitar novamente."
        except Exception as exc:
            msg = "Falha ao digitar (permissao de Acessibilidade?)"
            self.root.after(0, lambda: self.permission_error(exc))

        if self.hide_window.get():
            self.root.after(0, self.root.deiconify)

        self.finish(msg)

    def permission_error(self, exc):
        messagebox.showerror(
            APP_NAME,
            "Nao foi possivel simular o teclado.\n\n"
            "No macOS, va em Ajustes do Sistema > Privacidade e Seguranca > "
            "Acessibilidade e autorize o TypeClipboard (ou o Terminal, se estiver "
            "rodando pelo terminal).\n\n"
            f"Detalhe: {exc}",
        )

    def finish(self, message):
        self.update_status(message)
        self.root.after(0, self.reset_form)

    def update_status(self, message):
        self.root.after(0, lambda: self.status.config(text=message))

    def reset_form(self):
        self.entry.config(state="normal")
        self.entry.delete(0, tk.END)
        self.button.config(state="normal", text="COLAR", command=self.start_typing)
        self.entry.focus()
        self.running = False
        self.cancelled = False


def bring_to_front():
    """Traz a janela para frente sem usar AppKit (que conflita com o Tk)."""
    if platform.system() != "Darwin":
        return
    try:
        import subprocess

        subprocess.run(
            [
                "osascript",
                "-e",
                'tell application "System Events" to set frontmost of the first '
                'process whose unix id is {} to true'.format(os.getpid()),
            ],
            check=False,
            capture_output=True,
            timeout=3,
        )
    except Exception:
        pass


def main():
    root = tk.Tk()
    TypeClipboardApp(root)
    root.update_idletasks()
    root.lift()
    root.after(200, bring_to_front)
    root.mainloop()
    return 0


if __name__ == "__main__":
    sys.exit(main())
