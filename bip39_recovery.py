import tkinter as tk
from tkinter import ttk, messagebox
import os

# --- Konfiguration und Konstanten ---
WORDLIST_FILE = "english.txt"
VALID_INPUT_NUMBERS = {2**i for i in range(11)}  # Erzeugt {1, 2, 4, 8, ..., 1024}


class BIP39RecoveryApp:
    def __init__(self, root):
        """Initialisiert die Hauptanwendung."""
        self.root = root
        self.root.title("Offline BIP39 Mnemonic Recovery Tool")
        self.root.geometry("600x550")
        self.root.resizable(False, False)

        # Stile für die Widgets
        self.style = ttk.Style()
        self.style.configure("TButton", font=("Helvetica", 12), padding=10)
        self.style.configure("TLabel", font=("Helvetica", 12))
        self.style.configure("Header.TLabel", font=("Helvetica", 16, "bold"))
        self.style.configure(
            "Result.TLabel", font=("Courier", 12, "bold"), foreground="blue"
        )
        self.style.configure(
            "Warning.TLabel", font=("Helvetica", 10, "italic"), foreground="red"
        )

        self.wordlist = self.load_wordlist()
        if not self.wordlist:
            # Wenn die Wortliste nicht geladen werden konnte, wird die GUI nicht gestartet.
            self.root.destroy()
            return

        # Anwendungsstatusvariablen
        self.mnemonic_length = 0
        self.current_word_index = 0
        self.recovered_words = []
        self.current_word_sum = 0
        self.current_word_inputs = []

        self.create_welcome_frame()

    def load_wordlist(self):
        """Lädt die BIP39-Wortliste aus der Datei."""
        if not os.path.exists(WORDLIST_FILE):
            messagebox.showerror(
                "Fehler",
                f"Wortlistendatei '{WORDLIST_FILE}' nicht gefunden!\n\n"
                f"Bitte stellen Sie sicher, dass sich '{WORDLIST_FILE}' im selben Verzeichnis wie das Skript befindet.",
            )
            return None

        try:
            with open(WORDLIST_FILE, "r", encoding="utf-8") as f:
                words = [line.strip() for line in f if line.strip()]

            if len(words) != 2048:
                messagebox.showerror(
                    "Fehler",
                    f"Die Wortliste '{WORDLIST_FILE}' ist ungültig.\n\n"
                    f"Sie enthält {len(words)} Wörter, aber es sollten genau 2048 sein.",
                )
                return None

            return words
        except Exception as e:
            messagebox.showerror(
                "Fehler beim Lesen der Datei", f"Ein Fehler ist aufgetreten: {e}"
            )
            return None

    def clear_frame(self):
        """Entfernt alle Widgets aus dem Hauptfenster."""
        for widget in self.root.winfo_children():
            widget.destroy()

    def create_welcome_frame(self):
        """Zeigt den anfänglichen Auswahlbildschirm für die Länge des Mnemonics an."""
        self.clear_frame()
        frame = ttk.Frame(self.root, padding="20")
        frame.pack(expand=True, fill="both")

        ttk.Label(frame, text="BIP39 Mnemonic Recovery", style="Header.TLabel").pack(
            pady=20
        )
        ttk.Label(
            frame, text="Bitte wählen Sie die Länge Ihrer Seed-Phrase:", wraplength=400
        ).pack(pady=10)

        ttk.Button(
            frame, text="12 Wörter", command=lambda: self.start_recovery(12)
        ).pack(pady=10, fill="x")
        ttk.Button(
            frame, text="18 Wörter", command=lambda: self.start_recovery(18)
        ).pack(pady=10, fill="x")
        ttk.Button(
            frame, text="24 Wörter", command=lambda: self.start_recovery(24)
        ).pack(pady=10, fill="x")

        ttk.Label(
            frame,
            text="Dieses Tool arbeitet zu 100 % offline. Es werden keine Daten gesendet.",
            style="Warning.TLabel",
        ).pack(pady=30)

    def start_recovery(self, length):
        """Startet den Wiederherstellungsprozess für die angegebene Länge."""
        self.mnemonic_length = length
        self.current_word_index = 0
        self.recovered_words = []
        self.reset_current_word()
        self.create_recovery_frame()

    def create_recovery_frame(self):
        """Erstellt die Haupt-GUI für die Eingabe von Zahlen."""
        self.clear_frame()
        frame = ttk.Frame(self.root, padding="20")
        frame.pack(expand=True, fill="both")

        # --- Dynamische Titel ---
        self.title_label = ttk.Label(frame, text="", style="Header.TLabel")
        self.title_label.pack(pady=(0, 20))

        # --- Eingabebereich ---
        input_frame = ttk.Frame(frame)
        input_frame.pack(fill="x", pady=10)
        ttk.Label(input_frame, text="Zahl eingeben (z. B. 2, 4, 256):").pack(
            side="left"
        )
        self.number_entry = ttk.Entry(input_frame, font=("Helvetica", 12), width=10)
        self.number_entry.pack(side="left", padx=10)
        self.add_button = ttk.Button(
            input_frame, text="Zahl hinzufügen", command=self.add_number
        )
        self.add_button.pack(side="left")
        self.root.bind("<Return>", lambda event: self.add_number())

        # --- Anzeige des aktuellen Wortes ---
        self.current_inputs_label = ttk.Label(
            frame, text="Eingegebene Zahlen: ", wraplength=550
        )
        self.current_inputs_label.pack(anchor="w", pady=5)
        self.current_word_label = ttk.Label(
            frame, text="Aktuelles Wort: ", style="Result.TLabel"
        )
        self.current_word_label.pack(anchor="w", pady=10)

        # --- Steuerung ---
        self.next_word_button = ttk.Button(
            frame, text="Wort bestätigen & Nächstes", command=self.process_next_word
        )
        self.next_word_button.pack(pady=20, fill="x")

        # --- Anzeige des wiederhergestellten Satzes ---
        ttk.Label(frame, text="Bisher wiederhergestellte Wörter:").pack(
            anchor="w", pady=(20, 5)
        )
        self.recovered_words_display = tk.Text(
            frame,
            height=5,
            width=60,
            font=("Courier", 11),
            wrap="word",
            relief="solid",
            borderwidth=1,
        )
        self.recovered_words_display.pack(fill="x")
        self.recovered_words_display.config(state="disabled")

        self.update_recovery_display()

    def add_number(self):
        """Verarbeitet die eingegebene Zahl."""
        try:
            num_str = self.number_entry.get().strip()
            if not num_str:
                return

            num = int(num_str)

            if num not in VALID_INPUT_NUMBERS:
                messagebox.showwarning(
                    "Ungültige Eingabe",
                    f"Bitte geben Sie eine gültige Potenz von 2 ein (1, 2, 4, ..., 1024).",
                )
                self.number_entry.delete(0, tk.END)
                return

            if num in self.current_word_inputs:
                messagebox.showwarning(
                    "Doppelte Eingabe",
                    f"Die Zahl {num} wurde bereits für dieses Wort hinzugefügt.",
                )
            else:
                self.current_word_inputs.append(num)
                self.current_word_sum += num

            self.number_entry.delete(0, tk.END)
            self.update_recovery_display()

        except ValueError:
            messagebox.showwarning(
                "Ungültige Eingabe", "Bitte geben Sie eine gültige ganze Zahl ein."
            )
            self.number_entry.delete(0, tk.END)

    def process_next_word(self):
        """Bestätigt das aktuelle Wort und geht zum nächsten über."""
        if self.current_word_sum == 0:
            messagebox.showwarning(
                "Keine Eingabe",
                "Bitte geben Sie mindestens eine Zahl für dieses Wort ein.",
            )
            return

        word_index = self.current_word_sum - 1
        if 0 <= word_index < 2048:
            word = self.wordlist[word_index]
            self.recovered_words.append(word)
            self.current_word_index += 1

            if self.current_word_index >= self.mnemonic_length:
                self.show_final_result()
            else:
                self.reset_current_word()
                self.update_recovery_display()
        else:
            messagebox.showerror(
                "Fehler",
                "Die Summe der Zahlen ist ungültig und ergibt kein gültiges Wort.",
            )

    def reset_current_word(self):
        """Setzt den Zustand für die Eingabe des nächsten Wortes zurück."""
        self.current_word_sum = 0
        self.current_word_inputs = []

    def update_recovery_display(self):
        """Aktualisiert alle Labels und Anzeigen in der GUI."""
        # Titel aktualisieren
        self.title_label.config(
            text=f"Wort {self.current_word_index + 1} von {self.mnemonic_length} wiederherstellen"
        )

        # Liste der eingegebenen Zahlen aktualisieren
        inputs_str = ", ".join(map(str, sorted(self.current_word_inputs)))
        self.current_inputs_label.config(text=f"Eingegebene Zahlen: {inputs_str}")

        # Aktuell berechnetes Wort anzeigen
        if self.current_word_sum > 0:
            word_index = self.current_word_sum - 1
            if 0 <= word_index < 2048:
                word = self.wordlist[word_index]
                self.current_word_label.config(
                    text=f"Aktuelles Wort: [Summe: {self.current_word_sum}] -> Index {word_index + 1} -> '{word}'"
                )
            else:
                self.current_word_label.config(
                    text=f"Aktuelles Wort: [Summe: {self.current_word_sum}] -> UNGÜLTIGER INDEX"
                )
        else:
            self.current_word_label.config(text="Aktuelles Wort: (warten auf Eingabe)")

        # Anzeige der wiederhergestellten Wörter aktualisieren
        self.recovered_words_display.config(state="normal")
        self.recovered_words_display.delete("1.0", tk.END)
        self.recovered_words_display.insert("1.0", " ".join(self.recovered_words))
        self.recovered_words_display.config(state="disabled")

    def show_final_result(self):
        """Zeigt den endgültigen wiederhergestellten Satz an."""
        self.clear_frame()
        frame = ttk.Frame(self.root, padding="20")
        frame.pack(expand=True, fill="both")

        ttk.Label(
            frame, text="Wiederherstellung erfolgreich!", style="Header.TLabel"
        ).pack(pady=20)
        ttk.Label(frame, text="Ihre wiederhergestellte BIP39 Seed-Phrase lautet:").pack(
            pady=10
        )

        result_text = tk.Text(
            frame,
            height=6,
            width=60,
            font=("Courier", 12),
            wrap="word",
            relief="solid",
            borderwidth=1,
        )
        result_text.insert("1.0", " ".join(self.recovered_words))
        result_text.config(state="disabled")
        result_text.pack(pady=10)

        ttk.Label(
            frame,
            text="SICHERHEITSHINWEIS: Schließen Sie dieses Fenster, nachdem Sie Ihren Satz gesichert haben.",
            style="Warning.TLabel",
        ).pack(pady=20)

        ttk.Button(frame, text="Neu starten", command=self.create_welcome_frame).pack(
            pady=10, fill="x"
        )
        ttk.Button(frame, text="Beenden", command=self.root.quit).pack(pady=5, fill="x")


if __name__ == "__main__":
    root = tk.Tk()
    app = BIP39RecoveryApp(root)
    root.mainloop()
