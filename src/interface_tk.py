#imports
import tkinter as tk
from tkinter import messagebox
from pathlib import Path
import re

from ttkbootstrap import Style
from ttkbootstrap.widgets import Frame, Button, Label, Entry, Notebook, Treeview, Labelframe

from bibliotheque import Bibliotheque
from exceptions import (
    LivreIndisponibleError, QuotaEmpruntDepasseError,
    MembreInexistantError, LivreInexistantError
)
import visualisations as vis


class BibliothequeGUI(tk.Tk):
    def __init__(self, data_dir: Path):
        super().__init__()
        #Configuration principale de la fenêtre
        self.title("Gestion de Bibliothèque")
        self.geometry("900x650")

        #Palette de couleurs que jai choisi
        PRIMARY_BG    = "#b19e85"
        CARD_BG       = "#846e51"
        HEADER_BG     = "#643f24"
        BTN_BG        = "#541908"
        BTN_ACTIVE_BG = "#2d1409"

        #Application du thème Bootstrap
        self.style = Style(theme="minty")
        self.configure(bg=PRIMARY_BG)
        self.style.configure('TFrame', background=PRIMARY_BG)
        self.style.configure('Card.TFrame', background=CARD_BG, borderwidth=1, relief='solid')
        self.style.configure('Header.TFrame', background=HEADER_BG)
        self.style.configure('TLabel', background=PRIMARY_BG, foreground='black', font=('Segoe UI', 10))
        self.style.configure('Header.TLabel', background=HEADER_BG, foreground='white', font=('Segoe UI', 14, 'bold'))
        self.style.configure('Accent.TButton', background=BTN_BG, foreground='white', font=('Segoe UI', 10, 'bold'), padding=6)
        self.style.map('Accent.TButton', background=[('active', BTN_ACTIVE_BG)])

        #Création de la barre de titre
        header = Frame(self, style='Header.TFrame', height=60)
        header.pack(fill="x")
        Label(header, text="Bibliothèque Bayt al-Hikma", style='Header.TLabel').pack(pady=15, padx=20)

        #Création du notebook pour les onglets
        self.notebook = Notebook(self, bootstyle="light")
        self.notebook.pack(fill="both", expand=True, padx=10, pady=10)

        #Chargement des données via la classe Bibliotheque
        self.biblio = Bibliotheque(data_dir)
        self.biblio.charger_tout()

        #Construction des onglets
        self._build_tab_livres()
        self._build_tab_membres()
        self._build_tab_emprunt()
        self._build_tab_retour()
        self._build_tab_stats()

    def _make_card(self, parent, title: str):
        """
        Crée et retourne un cadre stylisé (card) avec un titre.
        """
        card = Frame(parent, style='Card.TFrame', padding=15)
        card.pack(fill="both", expand=True, padx=5, pady=5)
        Label(card, text=title, font=("Segoe UI", 12, "bold"), background="#846e51", foreground="white").pack(anchor="w", pady=(0,10))
        return card

    # ===== Onglet Gestion des Livres =====
    def _build_tab_livres(self):
        tab = Frame(self.notebook)
        self.notebook.add(tab, text="Livres")

        # Liste des livres sous forme de Treeview
        card = self._make_card(tab, "Liste des Livres")
        cols = ("ISBN", "Titre", "Auteur", "Année", "Genre", "Statut")
        self.tree_livres = Treeview(card, columns=cols, show="headings", bootstyle="info")
        for c in cols:
            self.tree_livres.heading(c, text=c)
            width = 200 if c == "Titre" else 100
            self.tree_livres.column(c, width=width, anchor="center")
        self.tree_livres.pack(fill="both", expand=True, pady=5)

        # Boutons d'ajout et de suppression
        btnf = Frame(card)
        btnf.pack(fill="x", pady=(0,10))
        Button(btnf, text="Ajouter", style='Accent.TButton', command=self._show_add_livre).pack(side="left", padx=5)
        Button(btnf, text="Supprimer", style='Accent.TButton', command=self._delete_livre).pack(side="left")

        # Formulaire masqué pour ajouter un livre
        self.add_livre_frame = Labelframe(tab, text="Ajouter un livre")
        for idx, field in enumerate(["ISBN","Titre","Auteur","Année","Genre"]):
            Label(self.add_livre_frame, text=field).grid(row=idx, column=0, sticky="w", padx=5, pady=2)
            entry = Entry(self.add_livre_frame)
            entry.grid(row=idx, column=1, sticky="ew", padx=5, pady=2)
            setattr(self, f"entry_{field.lower()}", entry)
        self.add_livre_frame.columnconfigure(1, weight=1)
        Button(self.add_livre_frame, text="Valider", style='Accent.TButton', command=self._add_livre).grid(row=5, column=0, columnspan=2, pady=10)
        self.add_livre_frame.pack_forget()

        # Chargement initial des livres
        self._refresh_livres()

    def _refresh_livres(self):
        """Efface et recharge la liste des livres depuis la bibliothèque."""
        for item in self.tree_livres.get_children():
            self.tree_livres.delete(item)
        for livre in self.biblio.livres.values():
            statut = "Disponible" if livre.statut == "disponible" else "Emprunté"
            self.tree_livres.insert("", "end", values=(livre.isbn, livre.titre, livre.auteur, livre.annee, livre.genre, statut))

    def _show_add_livre(self):
        """Affiche le formulaire d'ajout de livre."""
        self.add_livre_frame.pack(fill="x", padx=10, pady=5)

    def _add_livre(self):
        """Récupère les données du formulaire, valide et ajoute un livre."""
        isbn  = self.entry_isbn.get().strip()
        titre = self.entry_titre.get().strip()
        auteur= self.entry_auteur.get().strip()
        an    = self.entry_année.get().strip()
        genre = self.entry_genre.get().strip()
        if not all([isbn, titre, auteur, an, genre]):
            messagebox.showerror("Erreur", "Tous les champs sont requis.")
            return
        if not re.fullmatch(r"(\d{10}|\d{13})", isbn):
            messagebox.showerror("Erreur", "ISBN invalide.")
            return
        try:
            annee = int(an)
        except ValueError:
            messagebox.showerror("Erreur", "Année invalide.")
            return
        try:
            self.biblio.ajouter_livre(isbn, titre, auteur, annee, genre)
            self.biblio.sauvegarder_tout()
            messagebox.showinfo("Succès", f"Livre '{titre}' ajouté.")
            self._refresh_livres()
            self.add_livre_frame.pack_forget()
        except Exception as e:
            messagebox.showerror("Erreur", str(e))

    def _delete_livre(self):
        """Supprime le livre sélectionné après confirmation."""
        sel = self.tree_livres.selection()
        if not sel:
            messagebox.showerror("Erreur", "Veuillez sélectionner un livre à supprimer.")
            return
        values = self.tree_livres.item(sel[0], 'values')
        isbn, titre = values[0], values[1]
        if messagebox.askyesno("Confirmation", f"Supprimer le livre '{titre}' (ISBN {isbn}) ?"):
            try:
                self.biblio.supprimer_livre(isbn)
                self.biblio.sauvegarder_tout()
                messagebox.showinfo("Succès", f"Livre '{titre}' supprimé.")
                self._refresh_livres()
            except LivreInexistantError as e:
                messagebox.showerror("Erreur", str(e))

    # ===== Onglet Gestion des Membres =====
    def _build_tab_membres(self):
        tab = Frame(self.notebook)
        self.notebook.add(tab, text="Membres")

        # Liste des membres
        card = self._make_card(tab, "Liste des Membres")
        cols = ("ID", "Nom")
        self.tree_membres = Treeview(card, columns=cols, show="headings", bootstyle="info")
        for c in cols:
            self.tree_membres.heading(c, text=c)
            self.tree_membres.column(c, width=200, anchor="center")
        self.tree_membres.pack(fill="both", expand=True, pady=5)

        # Bouton d'ajout
        btnf = Frame(card)
        btnf.pack(fill="x", pady=(0,10))
        Button(btnf, text="Ajouter", style='Accent.TButton', command=self._show_add_membre).pack(side="left")

        # Formulaire masqué pour ajouter un membre
        self.add_membre_frame = Labelframe(tab, text="Ajouter un membre")
        Label(self.add_membre_frame, text="ID").grid(row=0, column=0, padx=5, pady=2, sticky="w")
        self.entry_idm = Entry(self.add_membre_frame)
        self.entry_idm.grid(row=0, column=1, sticky="ew", padx=5, pady=2)
        Label(self.add_membre_frame, text="Nom").grid(row=1, column=0, padx=5, pady=2, sticky="w")
        self.entry_nom = Entry(self.add_membre_frame)
        self.entry_nom.grid(row=1, column=1, sticky="ew", padx=5, pady=2)
        self.add_membre_frame.columnconfigure(1, weight=1)
        Button(self.add_membre_frame, text="Valider", style='Accent.TButton', command=self._add_membre).grid(row=2, column=0, columnspan=2, pady=10)
        self.add_membre_frame.pack_forget()

        # Chargement initial des membres
        self._refresh_membres()

    def _refresh_membres(self):
        """Efface et recharge la liste des membres."""
        for item in self.tree_membres.get_children():
            self.tree_membres.delete(item)
        for membre in self.biblio.membres.values():
            self.tree_membres.insert("", "end", values=(membre.id_membre, membre.nom))

    def _show_add_membre(self):
        """Affiche le formulaire d'ajout de membre."""
        self.add_membre_frame.pack(fill="x", padx=10, pady=5)

    def _add_membre(self):
        """Récupère les infos du formulaire et enregistre un nouveau membre."""
        idm = self.entry_idm.get().strip()
        nom = self.entry_nom.get().strip()
        if not idm or not nom:
            messagebox.showerror("Erreur", "Tous les champs sont requis.")
            return
        try:
            self.biblio.enregistrer_membre(id_membre=idm, nom=nom)
            self.biblio.sauvegarder_tout()
            messagebox.showinfo("Succès", f"Membre '{nom}' ajouté.")
            self._refresh_membres()
            self.add_membre_frame.pack_forget()
        except Exception as e:
            messagebox.showerror("Erreur", str(e))

    # ===== Onglet Emprunt =====
    def _build_tab_emprunt(self):
        tab = Frame(self.notebook)
        self.notebook.add(tab, text="Emprunter")

        # Champ de saisie pour le titre du livre à emprunter
        Label(tab, text="Titre du livre :", background="#b19e85").pack(pady=5, anchor="w", padx=10)
        self.entry_emp_titre = Entry(tab)
        self.entry_emp_titre.pack(fill="x", padx=10)

        # Champ de saisie pour le nom du membre emprunteur
        Label(tab, text="Nom du membre :", background="#b19e85").pack(pady=5, anchor="w", padx=10)
        self.entry_emp_nom = Entry(tab)
        self.entry_emp_nom.pack(fill="x", padx=10)

        # Bouton de validation d'emprunt
        Button(tab, text="Emprunter", style='Accent.TButton', command=self._emprunter).pack(pady=15)

    def _emprunter(self):
        """Traite l'emprunt d'un livre par un membre."""
        titre = self.entry_emp_titre.get().strip()
        nom   = self.entry_emp_nom.get().strip()
        if not titre or not nom:
            messagebox.showerror("Erreur", "Veuillez remplir tous les champs.")
            return
        # Recherche du livre et du membre
        livres = self.biblio.chercher_livre_par_titre(titre)
        membres = self.biblio.chercher_membre_par_nom(nom)
        if not livres:
            messagebox.showerror("Erreur", f"Aucun livre trouvé pour '{titre}'.")
            return
        if not membres:
            messagebox.showerror("Erreur", f"Aucun membre trouvé pour '{nom}'.")
            return
        livre, membre = livres[0], membres[0]
        try:
            self.biblio.emprunter(livre.isbn, membre.id_membre)
            self.biblio.sauvegarder_tout()
            messagebox.showinfo("Succès", f"Le livre '{livre.titre}' a été emprunté par {membre.nom}.")
            self._refresh_livres()
            self._refresh_membres()
        except (LivreIndisponibleError, QuotaEmpruntDepasseError, MembreInexistantError, LivreInexistantError) as e:
            messagebox.showerror("Erreur", str(e))

    # ===== Onglet Retour =====
    def _build_tab_retour(self):
        tab = Frame(self.notebook)
        self.notebook.add(tab, text="Retourner")

        # Champ de saisie pour le titre du livre à retourner
        Label(tab, text="Titre du livre :", background="#b19e85").pack(pady=5, anchor="w", padx=10)
        self.entry_ret_titre = Entry(tab)
        self.entry_ret_titre.pack(fill="x", padx=10)

        # Champ de saisie pour le nom du membre qui retourne
        Label(tab, text="Nom du membre :", background="#b19e85").pack(pady=5, anchor="w", padx=10)
        self.entry_ret_nom = Entry(tab)
        self.entry_ret_nom.pack(fill="x", padx=10)

        # Bouton de validation de retour
        Button(tab, text="Retourner", style='Accent.TButton', command=self._retourner).pack(pady=15)

    def _retourner(self):
        """Traite le retour d'un livre par un membre."""
        titre = self.entry_ret_titre.get().strip()
        nom   = self.entry_ret_nom.get().strip()
        if not titre or not nom:
            messagebox.showerror("Erreur", "Veuillez remplir tous les champs.")
            return
        # Recherche du livre et du membre
        livres = self.biblio.chercher_livre_par_titre(titre)
        membres = self.biblio.chercher_membre_par_nom(nom)
        if not livres:
            messagebox.showerror("Erreur", f"Aucun livre trouvé pour '{titre}'.")
            return
        if not membres:
            messagebox.showerror("Erreur", f"Aucun membre trouvé pour '{nom}'.")
            return
        livre, membre = livres[0], membres[0]
        try:
            self.biblio.retourner(livre.isbn, membre.id_membre)
            self.biblio.sauvegarder_tout()
            messagebox.showinfo("Succès", f"Le livre '{livre.titre}' a été retourné par {membre.nom}.")
            self._refresh_livres()
            self._refresh_membres()
        except (MembreInexistantError, LivreInexistantError) as e:
            messagebox.showerror("Erreur", str(e))

    # ===== Onglet Statistiques =====
    def _build_tab_stats(self):
        tab = Frame(self.notebook)
        self.notebook.add(tab, text="Statistiques")

        # Bouton diagramme des pourcentages par genre
        Button(tab, text="Diagramme % Genres", bootstyle="info",
               command=lambda: vis.diagramme_pourcentage_genres(self.biblio.livres)
              ).pack(fill="x", padx=20, pady=5)
        # Bouton top auteurs les plus empruntés
        Button(tab, text="Top Auteurs", bootstyle="info",
               command=lambda: vis.top_auteurs_populaires(self.biblio.historique, self.biblio.livres)
              ).pack(fill="x", padx=20, pady=5)
        # Bouton courbe d'activité des emprunts mensuels
        Button(tab, text="Emprunts/Mois", bootstyle="info",
               command=lambda: vis.courbe_activite_emprunts(self.biblio.historique)
              ).pack(fill="x", padx=20, pady=5)


if __name__ == "__main__":
    # Dossier de données (texte et historique)
    DATA_DIR = Path("data")
    app = BibliothequeGUI(DATA_DIR)
    app.mainloop()
