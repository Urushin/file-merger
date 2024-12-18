import os
import sys
import logging
import json
from pathlib import Path
from tkinter import (
    Tk, filedialog, messagebox, simpledialog, Listbox, Button,
    Scrollbar, RIGHT, Y, END, LEFT, BOTH, SINGLE, Toplevel, Label,
    StringVar, Entry, Checkbutton, IntVar, Menu
)
from tkinter.ttk import Progressbar, Combobox
import tkinter as tk
import zipfile
import threading
import schedule
import time
import platform

# Importing PyPDF2 for PDF handling
try:
    import PyPDF2
except ImportError:
    messagebox.showerror("Erreur", "Le module PyPDF2 n'est pas installé. Veuillez l'installer en exécutant 'pip install PyPDF2'.")
    sys.exit(1)

# Importing tkPDFViewer for PDF preview
try:
    from tkPDFViewer import tkPDFViewer as pdf
except ImportError:
    messagebox.showerror("Erreur", "Le module tkPDFViewer n'est pas installé. Veuillez l'installer en exécutant 'pip install tkPDFViewer'.")
    sys.exit(1)

# Importing tkinterdnd2 for drag-and-drop
try:
    from tkinterdnd2 import DND_FILES, TkinterDnD
except ImportError:
    messagebox.showerror("Erreur", "Le module tkinterdnd2 n'est pas installé. Veuillez l'installer en exécutant 'pip install tkinterdnd2'.")
    sys.exit(1)

class FileMerger:
    def __init__(self):
        self.all_files = []
        self.setup_logging()
        self.encoding = 'utf-8'
        self.generate_toc = False
        self.compress_output = False
        self.output_compressed = False
        self.output_zip_path = ""
        self.merge_type = 'Text'  # 'Text' or 'PDF'
        self.errors = []

        # Configuration file path
        self.config_file = "mergeFile_config.json"

        # Initialize the main window with drag-and-drop capabilities
        self.root = TkinterDnD.Tk()
        self.root.title("Programme de Combinaison de Fichiers")
        self.root.geometry("800x600")
        self.root.resizable(True, True)

        self.create_menu()
        self.create_widgets()

    def setup_logging(self):
        """Configure le module de logging."""
        logging.basicConfig(
            level=logging.DEBUG,
            format='[%(asctime)s] [%(levelname)s] %(message)s',
            handlers=[
                logging.FileHandler("mergeFile.log", encoding='utf-8'),
                logging.StreamHandler(sys.stdout)
            ]
        )
        logging.info("Initialisation du programme de combinaison de fichiers.")

    def create_menu(self):
        """Crée la barre de menu de l'application."""
        menubar = Menu(self.root)
        
        # Menu Fichier
        file_menu = Menu(menubar, tearoff=0)
        file_menu.add_command(label="Ajouter Fichiers", command=self.add_files)
        file_menu.add_command(label="Ajouter Dossier", command=self.add_folder)
        file_menu.add_command(label="Fusionner", command=self.merge_files)
        file_menu.add_separator()
        file_menu.add_command(label="Exporter Configuration", command=self.export_config)
        file_menu.add_command(label="Importer Configuration", command=self.import_config)
        file_menu.add_separator()
        file_menu.add_command(label="Quitter", command=self.root.quit)
        menubar.add_cascade(label="Fichier", menu=file_menu)
        
        # Menu Aide
        help_menu = Menu(menubar, tearoff=0)
        help_menu.add_command(label="À propos", command=self.show_about)
        menubar.add_cascade(label="Aide", menu=help_menu)
        
        self.root.config(menu=menubar)

    def create_widgets(self):
        """Crée les widgets de l'interface utilisateur."""
        # Frame pour la liste des fichiers
        list_frame = tk.Frame(self.root)
        list_frame.pack(pady=10, padx=10, fill=BOTH, expand=True)

        scrollbar = Scrollbar(list_frame)
        scrollbar.pack(side=RIGHT, fill=Y)

        self.listbox = Listbox(list_frame, selectmode=SINGLE, yscrollcommand=scrollbar.set, font=("Arial", 12))
        self.listbox.pack(side=LEFT, fill=BOTH, expand=True)
        scrollbar.config(command=self.listbox.yview)

        # Configurer le drag-and-drop sur la listbox
        self.listbox.drop_target_register(DND_FILES)
        self.listbox.dnd_bind('<<Drop>>', self.drop)

        # Frame pour les boutons
        button_frame = tk.Frame(self.root)
        button_frame.pack(pady=5)

        add_btn = Button(button_frame, text="Ajouter Fichiers", width=15, command=self.add_files)
        add_btn.grid(row=0, column=0, padx=5, pady=5)

        add_folder_btn = Button(button_frame, text="Ajouter Dossier", width=15, command=self.add_folder)
        add_folder_btn.grid(row=0, column=1, padx=5, pady=5)

        remove_btn = Button(button_frame, text="Supprimer Sélection", width=18, command=self.remove_selected)
        remove_btn.grid(row=0, column=2, padx=5, pady=5)

        move_up_btn = Button(button_frame, text="Monter", width=10, command=self.move_up)
        move_up_btn.grid(row=0, column=3, padx=5, pady=5)

        move_down_btn = Button(button_frame, text="Descendre", width=10, command=self.move_down)
        move_down_btn.grid(row=0, column=4, padx=5, pady=5)

        preview_btn = Button(button_frame, text="Prévisualiser", width=15, command=self.preview_file)
        preview_btn.grid(row=0, column=5, padx=5, pady=5)

        # Frame pour les options
        options_frame = tk.LabelFrame(self.root, text="Options de Fusion")
        options_frame.pack(pady=10, padx=10, fill=BOTH, expand=True)

        # Encodage
        enc_label = Label(options_frame, text="Encodage des Fichiers :")
        enc_label.grid(row=0, column=0, padx=5, pady=5, sticky='e')

        self.encoding_var = StringVar(value='utf-8')
        enc_combo = Combobox(options_frame, textvariable=self.encoding_var, values=[
            'utf-8', 'latin-1', 'iso-8859-1', 'cp1252', 'utf-16'
        ], state='readonly')
        enc_combo.grid(row=0, column=1, padx=5, pady=5, sticky='w')

        # Type de fusion
        merge_type_label = Label(options_frame, text="Type de Fusion :")
        merge_type_label.grid(row=1, column=0, padx=5, pady=5, sticky='e')

        self.merge_type_var = StringVar(value='Text')
        merge_type_combo = Combobox(options_frame, textvariable=self.merge_type_var, values=[
            'Text', 'PDF'
        ], state='readonly')
        merge_type_combo.grid(row=1, column=1, padx=5, pady=5, sticky='w')

        # Générer la table des matières
        self.toc_var = IntVar()
        toc_check = Checkbutton(options_frame, text="Générer une Table des Matières", variable=self.toc_var)
        toc_check.grid(row=2, column=0, columnspan=2, padx=5, pady=5, sticky='w')

        # Compresser le fichier de sortie
        self.compress_var = IntVar()
        compress_check = Checkbutton(options_frame, text="Compresser le Fichier de Sortie (ZIP)", variable=self.compress_var)
        compress_check.grid(row=3, column=0, columnspan=2, padx=5, pady=5, sticky='w')

        # Planifier une fusion
        self.schedule_var = IntVar()
        schedule_check = Checkbutton(options_frame, text="Planifier une Fusion", variable=self.schedule_var, command=self.toggle_schedule_options)
        schedule_check.grid(row=4, column=0, columnspan=2, padx=5, pady=5, sticky='w')

        # Options de planification
        self.schedule_time_label = Label(options_frame, text="Heure de Fusion (HH:MM):")
        self.schedule_time_label.grid(row=5, column=0, padx=5, pady=5, sticky='e')
        self.schedule_time_entry = Entry(options_frame)
        self.schedule_time_entry.grid(row=5, column=1, padx=5, pady=5, sticky='w')
        self.schedule_time_label.configure(state='disabled')
        self.schedule_time_entry.configure(state='disabled')

        # Bouton de fusion
        merge_btn = Button(self.root, text="Fusionner les Fichiers", width=20, command=self.merge_files)
        merge_btn.pack(pady=10)

        # Barre de progression
        self.progress = Progressbar(self.root, orient='horizontal', length=700, mode='determinate')
        self.progress.pack(pady=10)

    def drop(self, event):
        """Gestion du drop des fichiers dans la listbox."""
        files = self.root.splitlist(event.data)
        self.add_files(files)

    def add_files(self, files=None):
        """Ajoute des fichiers ou des dossiers à la liste."""
        if not files:
            logging.debug("Ouverture de la boîte de dialogue de sélection de fichiers.")
            filetypes = [
                ("Tous les fichiers", "*.*")
            ]
            files = filedialog.askopenfilenames(
                title="Sélectionnez un ou plusieurs fichiers",
                filetypes=filetypes,
                parent=self.root
            )
            if not files:
                logging.debug("Aucun fichier sélectionné.")
                return

        selected_files = list(files)
        logging.debug(f"Fichiers/Dossiers sélectionnés : {selected_files}")

        # Suppression des doublons et ajout des fichiers
        unique_files = []
        for f in selected_files:
            path = Path(f).resolve()
            if path.is_dir():
                for file in path.rglob('*'):
                    if file.is_file() and str(file) not in self.all_files:
                        self.all_files.append(str(file))
                        unique_files.append(str(file))
            elif path.is_file():
                if str(path) not in self.all_files:
                    self.all_files.append(str(path))
                    unique_files.append(str(path))

        if not unique_files:
            logging.info("Aucun nouveau fichier ajouté (doublons ignorés).")
            messagebox.showinfo("Information", "Aucun nouveau fichier ajouté (doublons ignorés).")
            return

        for file in unique_files:
            self.listbox.insert(END, file)

        logging.debug(f"Fichiers ajoutés : {unique_files}")

    def add_folder(self):
        """Ajoute tous les fichiers d'un dossier à la liste."""
        folder = filedialog.askdirectory(
            title="Sélectionnez un dossier",
            parent=self.root
        )
        if not folder:
            logging.debug("Aucun dossier sélectionné.")
            return

        folder_path = Path(folder).resolve()
        logging.debug(f"Dossier sélectionné : {folder_path}")

        unique_files = []
        for file in folder_path.rglob('*'):
            if file.is_file() and str(file) not in self.all_files:
                self.all_files.append(str(file))
                unique_files.append(str(file))

        if not unique_files:
            logging.info("Aucun nouveau fichier ajouté depuis le dossier (doublons ignorés).")
            messagebox.showinfo("Information", "Aucun nouveau fichier ajouté depuis le dossier (doublons ignorés).")
            return

        for file in unique_files:
            self.listbox.insert(END, file)

        logging.debug(f"Fichiers ajoutés depuis le dossier : {unique_files}")

    def remove_selected(self):
        """Supprime le fichier sélectionné de la liste."""
        selected = self.listbox.curselection()
        if not selected:
            messagebox.showwarning("Aucune Sélection", "Veuillez sélectionner un fichier à supprimer.")
            return
        index = selected[0]
        file_path = self.listbox.get(index)
        self.listbox.delete(index)
        self.all_files.remove(file_path)
        logging.debug(f"Fichier supprimé : {file_path}")

    def move_up(self):
        """Déplace le fichier sélectionné vers le haut dans la liste."""
        selected = self.listbox.curselection()
        if not selected:
            messagebox.showwarning("Aucune Sélection", "Veuillez sélectionner un fichier à déplacer.")
            return
        index = selected[0]
        if index == 0:
            return  # Déjà en haut
        file = self.listbox.get(index)
        self.listbox.delete(index)
        self.listbox.insert(index - 1, file)
        self.listbox.selection_set(index - 1)
        self.all_files[index], self.all_files[index - 1] = self.all_files[index - 1], self.all_files[index]
        logging.debug(f"Fichier déplacé vers le haut : {file}")

    def move_down(self):
        """Déplace le fichier sélectionné vers le bas dans la liste."""
        selected = self.listbox.curselection()
        if not selected:
            messagebox.showwarning("Aucune Sélection", "Veuillez sélectionner un fichier à déplacer.")
            return
        index = selected[0]
        if index == len(self.listbox.get(0, END)) - 1:
            return  # Déjà en bas
        file = self.listbox.get(index)
        self.listbox.delete(index)
        self.listbox.insert(index + 1, file)
        self.listbox.selection_set(index + 1)
        self.all_files[index], self.all_files[index + 1] = self.all_files[index + 1], self.all_files[index]
        logging.debug(f"Fichier déplacé vers le bas : {file}")

    def preview_file(self):
        """Prévisualise le fichier sélectionné."""
        selected = self.listbox.curselection()
        if not selected:
            messagebox.showwarning("Aucune Sélection", "Veuillez sélectionner un fichier à prévisualiser.")
            return
        index = selected[0]
        file_path = self.listbox.get(index)
        logging.debug(f"Prévisualisation du fichier : {file_path}")

        merge_type = self.merge_type_var.get()
        if merge_type == 'PDF' and file_path.lower().endswith('.pdf'):
            self.preview_pdf(file_path)
        elif merge_type == 'Text':
            self.preview_text(file_path)
        else:
            messagebox.showwarning("Type de Fichier Incompatible", "La prévisualisation n'est disponible que pour les fichiers de type sélectionné.")

    def preview_text(self, file_path):
        """Affiche le contenu d'un fichier texte dans une nouvelle fenêtre."""
        try:
            with open(file_path, 'r', encoding=self.encoding_var.get()) as infile:
                content = infile.read()
        except Exception as e:
            logging.error(f"Erreur lors de la lecture du fichier {file_path} : {e}")
            messagebox.showerror("Erreur", f"Erreur lors de la lecture du fichier {file_path} :\n{e}")
            return

        preview_window = Toplevel(self.root)
        preview_window.title(f"Prévisualisation : {Path(file_path).name}")
        preview_window.geometry("600x400")

        scrollbar = Scrollbar(preview_window)
        scrollbar.pack(side=RIGHT, fill=Y)

        text_area = tk.Text(preview_window, wrap='word', yscrollcommand=scrollbar.set, font=("Arial", 12))
        text_area.pack(expand=True, fill='both')
        scrollbar.config(command=text_area.yview)

        text_area.insert(END, content)
        text_area.config(state='disabled')  # Rendre la zone de texte en lecture seule

    def preview_pdf(self, file_path):
        """Affiche le contenu d'un fichier PDF dans une nouvelle fenêtre."""
        try:
            preview_window = Toplevel(self.root)
            preview_window.title(f"Prévisualisation : {Path(file_path).name}")
            preview_window.geometry("800x600")

            v1 = pdf.ShowPdf()
            v2 = v1.pdf_view(preview_window, pdf_location=file_path, width=800, height=600)
            v2.pack()
        except Exception as e:
            logging.error(f"Erreur lors de la prévisualisation du PDF {file_path} : {e}")
            messagebox.showerror("Erreur", f"Erreur lors de la prévisualisation du PDF {file_path} :\n{e}")

    def merge_files(self):
        """Fusionne les fichiers sélectionnés en un seul fichier de sortie."""
        if not self.all_files:
            messagebox.showwarning("Aucun Fichier", "Veuillez ajouter des fichiers à fusionner.")
            return

        # Récupérer les options
        self.encoding = self.encoding_var.get()
        self.generate_toc = self.toc_var.get()
        self.compress_output = self.compress_var.get()
        self.merge_type = self.merge_type_var.get()
        self.errors = []

        # Définir le nom par défaut
        default_name = "merged_files"
        if self.merge_type == 'PDF':
            default_ext = ".pdf"
            filetypes = [("Fichiers PDF", "*.pdf")]
        else:
            default_ext = ".txt"
            filetypes = [("Fichiers texte", "*.txt"), ("Tous les fichiers", "*.*")]

        # Demander à l'utilisateur de sélectionner le fichier de sortie avec le nom par défaut
        logging.debug("Ouverture de la boîte de dialogue d'enregistrement du fichier de sortie.")
        output_path = filedialog.asksaveasfilename(
            title="Enregistrez le fichier de sortie",
            initialfile=default_name,
            defaultextension=default_ext,
            filetypes=filetypes,
            parent=self.root
        )
        if not output_path:
            logging.debug("Aucun emplacement de sauvegarde sélectionné.")
            messagebox.showinfo("Information", "Aucun fichier de sortie sélectionné. Opération annulée.")
            return

        logging.debug(f"Emplacement de sauvegarde sélectionné : {output_path}")

        # Demander si l'utilisateur veut compresser le fichier de sortie
        if self.compress_output:
            zip_path = filedialog.asksaveasfilename(
                title="Enregistrez le fichier ZIP de sortie",
                defaultextension=".zip",
                filetypes=[("Fichiers ZIP", "*.zip")],
                parent=self.root
            )
            if not zip_path:
                logging.debug("Aucun emplacement de sauvegarde ZIP sélectionné.")
                messagebox.showinfo("Information", "Aucun fichier ZIP sélectionné. Compression ignorée.")
                self.compress_output = False
            else:
                self.output_zip_path = zip_path
                logging.debug(f"Emplacement de sauvegarde ZIP sélectionné : {zip_path}")

        # Planifier une fusion si nécessaire
        if self.schedule_var.get():
            schedule_time = self.schedule_time_entry.get()
            if not self.validate_time_format(schedule_time):
                messagebox.showerror("Format d'Heure Invalide", "Veuillez entrer une heure valide au format HH:MM.")
                return
            schedule.every().day.at(schedule_time).do(self.perform_merge, output_path)
            threading.Thread(target=self.run_scheduler, daemon=True).start()
            messagebox.showinfo("Planification", f"Fusion planifiée à {schedule_time} chaque jour.")
            logging.info(f"Fusion planifiée à {schedule_time} chaque jour.")
            return

        # Fusionner les fichiers
        self.run_merge(output_path)

    def run_merge(self, output_path):
        """Exécute la fusion des fichiers."""
        try:
            self.progress["maximum"] = len(self.all_files)
            self.progress["value"] = 0
            self.root.update_idletasks()

            if self.generate_toc and self.merge_type == 'Text':
                # Générer la table des matières
                with open(output_path, 'w', encoding=self.encoding) as outfile:
                    outfile.write("=== Table des Matières ===\n")
                    line_number = 1
                    toc_entries = []
                    for idx, file_path in enumerate(self.all_files, start=1):
                        toc_entries.append(f"{idx}. {Path(file_path).name} - Début à la ligne {line_number}\n")
                        with open(file_path, 'r', encoding=self.encoding) as infile:
                            content = infile.read()
                            line_number += content.count('\n') + 3  # Approximation
                    outfile.writelines(toc_entries)
                    outfile.write("\n")

            if self.merge_type == 'Text':
                with open(output_path, 'a', encoding=self.encoding) as outfile:
                    for idx, file_path in enumerate(self.all_files, start=1):
                        logging.debug(f"Traitement du fichier : {file_path}")
                        try:
                            with open(file_path, 'r', encoding=self.encoding) as infile:
                                outfile.write(f"=== {Path(file_path).name} ===\n")
                                outfile.write(infile.read() + "\n\n")
                        except Exception as e:
                            logging.error(f"Erreur lors de la lecture du fichier {file_path} : {e}")
                            self.errors.append(f"{file_path} : {e}")
                        self.progress["value"] = idx
                        self.root.update_idletasks()
            elif self.merge_type == 'PDF':
                merger = PyPDF2.PdfMerger()
                for idx, file_path in enumerate(self.all_files, start=1):
                    logging.debug(f"Traitement du fichier PDF : {file_path}")
                    try:
                        merger.append(file_path)
                    except Exception as e:
                        logging.error(f"Erreur lors de la fusion du PDF {file_path} : {e}")
                        self.errors.append(f"{file_path} : {e}")
                    self.progress["value"] = idx
                    self.root.update_idletasks()
                merger.write(output_path)
                merger.close()

            logging.info(f"Écriture terminée dans : {output_path}")
            if self.generate_toc and self.merge_type == 'PDF':
                messagebox.showinfo("Succès", f"La table des matières n'est pas supportée pour les PDF.\nLe fichier PDF fusionné a été sauvegardé sous :\n{output_path}")
            else:
                messagebox.showinfo("Succès", f"Le fichier combiné a été sauvegardé sous :\n{output_path}")

            # Compression du fichier de sortie
            if self.compress_output and self.output_zip_path:
                with zipfile.ZipFile(self.output_zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                    zipf.write(output_path, arcname=Path(output_path).name)
                logging.info(f"Fichier compressé créé : {self.output_zip_path}")
                messagebox.showinfo("Succès", f"Le fichier compressé a été sauvegardé sous :\n{self.output_zip_path}")

            # Notifications visuelles uniquement
            messagebox.showinfo("Notification", "La fusion est terminée.")

            # Résumé des erreurs si présentes
            if self.errors:
                error_message = "Certaines erreurs sont survenues lors de la fusion :\n\n" + "\n".join(self.errors)
                messagebox.showwarning("Erreurs", error_message)
        except Exception as e:
            logging.error(f"Erreur lors de la fusion des fichiers : {e}")
            messagebox.showerror("Erreur", f"Erreur lors de la fusion des fichiers :\n{e}")
        finally:
            self.progress["value"] = 0
            self.root.update_idletasks()

    def perform_merge(self, output_path):
        """Effectue la fusion des fichiers planifiée."""
        self.run_merge(output_path)

    def run_scheduler(self):
        """Exécute le scheduler dans un thread séparé."""
        while True:
            schedule.run_pending()
            time.sleep(1)

    def validate_time_format(self, time_str):
        """Valide le format de l'heure (HH:MM)."""
        try:
            time.strptime(time_str, '%H:%M')
            return True
        except ValueError:
            return False

    def toggle_schedule_options(self):
        """Active ou désactive les options de planification."""
        if self.schedule_var.get():
            self.schedule_time_label.configure(state='normal')
            self.schedule_time_entry.configure(state='normal')
        else:
            self.schedule_time_label.configure(state='disabled')
            self.schedule_time_entry.configure(state='disabled')

    def export_config(self):
        """Exportez la configuration actuelle (liste des fichiers et options) dans un fichier JSON."""
        config = {
            "files": self.all_files,
            "encoding": self.encoding_var.get(),
            "merge_type": self.merge_type_var.get(),
            "generate_toc": self.toc_var.get(),
            "compress_output": self.compress_var.get(),
            "schedule": {
                "enabled": self.schedule_var.get(),
                "time": self.schedule_time_entry.get() if self.schedule_var.get() else ""
            }
        }
        save_path = filedialog.asksaveasfilename(
            title="Exporter la Configuration",
            defaultextension=".json",
            filetypes=[("Fichiers JSON", "*.json")],
            parent=self.root
        )
        if not save_path:
            logging.debug("Aucun emplacement de sauvegarde de configuration sélectionné.")
            return
        try:
            with open(save_path, 'w', encoding='utf-8') as config_file:
                json.dump(config, config_file, ensure_ascii=False, indent=4)
            logging.info(f"Configuration exportée vers : {save_path}")
            messagebox.showinfo("Succès", f"La configuration a été exportée vers :\n{save_path}")
        except Exception as e:
            logging.error(f"Erreur lors de l'exportation de la configuration : {e}")
            messagebox.showerror("Erreur", f"Erreur lors de l'exportation de la configuration :\n{e}")

    def import_config(self):
        """Importez une configuration depuis un fichier JSON."""
        load_path = filedialog.askopenfilename(
            title="Importer une Configuration",
            defaultextension=".json",
            filetypes=[("Fichiers JSON", "*.json")],
            parent=self.root
        )
        if not load_path:
            logging.debug("Aucun fichier de configuration sélectionné pour l'importation.")
            return
        try:
            with open(load_path, 'r', encoding='utf-8') as config_file:
                config = json.load(config_file)
            # Charger les fichiers
            for file_path in config.get("files", []):
                resolved = str(Path(file_path).resolve())
                if resolved not in self.all_files:
                    self.all_files.append(resolved)
                    self.listbox.insert(END, resolved)
            # Charger les options
            self.encoding_var.set(config.get("encoding", 'utf-8'))
            self.merge_type_var.set(config.get("merge_type", 'Text'))
            self.toc_var.set(config.get("generate_toc", False))
            self.compress_var.set(config.get("compress_output", False))
            # Charger la planification
            schedule_info = config.get("schedule", {})
            if schedule_info.get("enabled", False):
                self.schedule_var.set(1)
                self.toggle_schedule_options()
                self.schedule_time_entry.delete(0, END)
                self.schedule_time_entry.insert(0, schedule_info.get("time", ""))
                # Planifier la fusion
                schedule_time = schedule_info.get("time", "")
                if self.validate_time_format(schedule_time):
                    schedule.every().day.at(schedule_time).do(self.perform_merge, config.get("output_path", "merged_files.txt") if self.merge_type_var.get() == 'Text' else "merged_files.pdf")
                    threading.Thread(target=self.run_scheduler, daemon=True).start()
            else:
                self.schedule_var.set(0)
                self.toggle_schedule_options()
            logging.info(f"Configuration importée depuis : {load_path}")
            messagebox.showinfo("Succès", f"La configuration a été importée depuis :\n{load_path}")
        except Exception as e:
            logging.error(f"Erreur lors de l'importation de la configuration : {e}")
            messagebox.showerror("Erreur", f"Erreur lors de l'importation de la configuration :\n{e}")

    def show_about(self):
        """Affiche une fenêtre 'À propos'."""
        about_text = (
            "Programme de Combinaison de Fichiers\n"
            "Version 1.0\n\n"
            "Développé par OpenAI ChatGPT\n"
            "Permet de fusionner des fichiers texte et PDF avec diverses options.\n\n"
            "Fonctionnalités :\n"
            "- Ajout/Suppression de fichiers ou dossiers\n"
            "- Réorganisation de l'ordre des fichiers\n"
            "- Prévisualisation des fichiers\n"
            "- Génération d'une table des matières (uniquement pour les fichiers texte)\n"
            "- Compression du fichier de sortie\n"
            "- Planification de tâches de fusion\n"
            "- Sauvegarde et chargement des configurations\n"
            "- Support des fichiers PDF\n"
            "- Drag-and-Drop pour ajouter des fichiers ou dossiers\n"
            "- Nom par défaut 'merged_files' lors de la fusion"
        )
        messagebox.showinfo("À propos", about_text)

    def run_scheduler(self):
        """Exécute le scheduler dans un thread séparé."""
        while True:
            schedule.run_pending()
            time.sleep(1)

    def validate_time_format(self, time_str):
        """Valide le format de l'heure (HH:MM)."""
        try:
            time.strptime(time_str, '%H:%M')
            return True
        except ValueError:
            return False

    def toggle_schedule_options(self):
        """Active ou désactive les options de planification."""
        if self.schedule_var.get():
            self.schedule_time_label.configure(state='normal')
            self.schedule_time_entry.configure(state='normal')
        else:
            self.schedule_time_label.configure(state='disabled')
            self.schedule_time_entry.configure(state='disabled')

    def save_config(self):
        """Sauvegarde la configuration actuelle."""
        config = {
            "files": self.all_files,
            "encoding": self.encoding_var.get(),
            "merge_type": self.merge_type_var.get(),
            "generate_toc": self.toc_var.get(),
            "compress_output": self.compress_var.get(),
            "schedule": {
                "enabled": self.schedule_var.get(),
                "time": self.schedule_time_entry.get() if self.schedule_var.get() else ""
            }
        }
        try:
            with open(self.config_file, 'w', encoding='utf-8') as config_file:
                json.dump(config, config_file, ensure_ascii=False, indent=4)
            logging.info(f"Configuration sauvegardée dans : {self.config_file}")
        except Exception as e:
            logging.error(f"Erreur lors de la sauvegarde de la configuration : {e}")

    def load_config(self):
        """Charge la configuration depuis le fichier de configuration."""
        if not Path(self.config_file).exists():
            logging.debug("Aucun fichier de configuration trouvé pour le chargement.")
            return
        try:
            with open(self.config_file, 'r', encoding='utf-8') as config_file:
                config = json.load(config_file)
            # Charger les fichiers
            for file_path in config.get("files", []):
                resolved = str(Path(file_path).resolve())
                if resolved not in self.all_files:
                    self.all_files.append(resolved)
                    self.listbox.insert(END, resolved)
            # Charger les options
            self.encoding_var.set(config.get("encoding", 'utf-8'))
            self.merge_type_var.set(config.get("merge_type", 'Text'))
            self.toc_var.set(config.get("generate_toc", False))
            self.compress_var.set(config.get("compress_output", False))
            # Charger la planification
            schedule_info = config.get("schedule", {})
            if schedule_info.get("enabled", False):
                self.schedule_var.set(1)
                self.toggle_schedule_options()
                self.schedule_time_entry.delete(0, END)
                self.schedule_time_entry.insert(0, schedule_info.get("time", ""))
                # Planifier la fusion
                schedule_time = schedule_info.get("time", "")
                if self.validate_time_format(schedule_time):
                    output_default = "merged_files.txt" if self.merge_type_var.get() == 'Text' else "merged_files.pdf"
                    schedule.every().day.at(schedule_time).do(self.perform_merge, output_default)
                    threading.Thread(target=self.run_scheduler, daemon=True).start()
            else:
                self.schedule_var.set(0)
                self.toggle_schedule_options()
            logging.info("Configuration chargée avec succès.")
        except Exception as e:
            logging.error(f"Erreur lors du chargement de la configuration : {e}")

    def run(self):
        """Démarre l'application."""
        self.load_config()  # Charger la configuration au démarrage
        self.root.mainloop()  # Lancer la boucle principale de l'interface graphique

if __name__ == "__main__":
    merger = FileMerger()
    merger.run()
