import customtkinter as ctk
from tkinter import messagebox

ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")

BACKGROUND = "#FFFDF8"

TEXT = "#334155"

TITLE = "#EC4899"

BORDER = "#7DD3FC"

BUTTON = "#F472B6"

BUTTON_HOVER = "#EC4899"

ENTRY_BG = "#FFFFFF"

TITLE_FONT = ("Helvetica", 34, "bold")

SUBTITLE_FONT = ("Helvetica", 18)

LABEL_FONT = ("Helvetica", 15, "bold")

ENTRY_FONT = ("Helvetica", 14)

BUTTON_FONT = ("Helvetica", 16, "bold")


class MainWindow:

    def __init__(self):
        self.root = ctk.CTk()
        self.root.title("Emisor")
        self.center_window(700, 700)
        self.root.configure(fg_color=BACKGROUND)
        self.data = None
        self.build()

    def center_window(self, width, height):
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        x = int((screen_width / 2) - (width / 2))
        y = int((screen_height / 2) - (height / 2))
        self.root.geometry(f"{width}x{height}+{x}+{y}")

    def build(self):
        container = ctk.CTkFrame(self.root,fg_color="transparent")
        container.pack(fill="both", expand=True, padx=35, pady=30)

        icon = ctk.CTkLabel(container,text="📨",font=("Helvetica", 42))
        icon.pack(pady=(0, 10))

        title = ctk.CTkLabel(container,text="EMISOR",text_color=TITLE,font=TITLE_FONT)
        title.pack()

        subtitle = ctk.CTkLabel(container,text="Laboratorio de Redes",text_color=TEXT,font=SUBTITLE_FONT)
        subtitle.pack(pady=(0, 30))

        self.create_label(container, "Mensaje")
        self.message = ctk.CTkTextbox(container,height=140,corner_radius=15,border_width=2,border_color=BORDER,fg_color=ENTRY_BG,text_color=TEXT,font=ENTRY_FONT)
        self.message.pack(fill="x", pady=(0, 20))

        self.create_label(container, "Algoritmo")
        self.algorithm = ctk.CTkComboBox(container,values=["CRC32"],state="readonly",corner_radius=12,border_width=2,border_color=BORDER,fg_color=ENTRY_BG,button_color=BORDER,button_hover_color="#38BDF8",dropdown_fg_color="white",text_color=TEXT,font=ENTRY_FONT)
        self.algorithm.set("CRC32")
        self.algorithm.pack(fill="x", pady=(0, 20))

        self.create_label(container, "Puerto")
        self.port = ctk.CTkEntry(container,corner_radius=12,border_width=2,border_color=BORDER,fg_color=ENTRY_BG,text_color=TEXT,font=ENTRY_FONT)
        self.port.insert(0, "5000")
        self.port.pack(fill="x", pady=(0, 20))

        self.create_label(container, "BER (Bit Error Rate)")
        self.ber = ctk.CTkEntry(container,corner_radius=12,border_width=2,border_color=BORDER,fg_color=ENTRY_BG,text_color=TEXT,font=ENTRY_FONT)
        self.ber.insert(0, "0.01")
        self.ber.pack(fill="x", pady=(0, 35))

        button = ctk.CTkButton(container,text="Enviar mensaje",command=self.send,height=80,corner_radius=25,fg_color=BUTTON,hover_color=BUTTON_HOVER,text_color="white",font=BUTTON_FONT)
        button.pack(ipadx=25)

    def create_label(self, parent, text):
        label = ctk.CTkLabel(parent,text=text,text_color=TEXT,font=LABEL_FONT)
        label.pack(anchor="w", pady=(0, 8))

    def send(self):
        message = self.message.get("1.0", "end").strip()

        if not message:
            messagebox.showerror(
                "Error",
                "Debe ingresar un mensaje."
            )
            return

        try:
            port = int(self.port.get())
            ber = float(self.ber.get())

        except ValueError:
            messagebox.showerror(
                "Error",
                "Puerto o BER inválidos."
            )
            return

        if not (0 <= ber <= 1):
            messagebox.showerror(
                "Error",
                "El BER debe estar entre 0 y 1."
            )
            return

        self.data = {
            "message": message,
            "algorithm": self.algorithm.get(),
            "port": port,
            "ber": ber
        }
        self.root.destroy()

    def run(self):
        self.root.mainloop()
        return self.data