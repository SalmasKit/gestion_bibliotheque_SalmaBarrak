import datetime
import csv
from pathlib import Path

from exceptions import (
    LivreIndisponibleError,
    QuotaEmpruntDepasseError,
    MembreInexistantError,
    LivreInexistantError
)

# ===================== CLASSE Livre =====================

class Livre:
    def __init__(self, isbn: str, titre: str, auteur: str, annee: int, genre: str, statut: str = "disponible"):
        self.isbn = isbn
        self.titre = titre
        self.auteur = auteur
        self.annee = annee
        self.genre = genre
        self.statut = statut  # "disponible" ou "emprunté"

    def est_disponible(self):
        return self.statut == "disponible"

    def emprunter(self):
        if not self.est_disponible():
            raise LivreIndisponibleError(f"Le livre '{self.titre}' (ISBN {self.isbn}) n'est pas disponible.")
        self.statut = "emprunté"

    def retourner(self):
        self.statut = "disponible"

    def to_line(self):
        titre = self.titre.replace(";", ",")
        auteur = self.auteur.replace(";", ",")
        genre = self.genre.replace(";", ",")
        return ";".join([self.isbn, titre, auteur, str(self.annee), genre, self.statut])

    @classmethod
    def from_line(cls, line: str):
        parts = line.strip().split(";")
        if len(parts) < 6:
            raise ValueError(f"Ligne livre invalide: '{line}'")
        isbn, titre, auteur, annee_str, genre, statut = parts[:6]
        try:
            annee = int(annee_str)
        except ValueError:
            annee = 0
        return cls(isbn=isbn, titre=titre, auteur=auteur, annee=annee, genre=genre, statut=statut)

    def __str__(self):
        return f"{self.titre} ({self.auteur}, {self.annee}) - {self.genre} [{self.statut}]"


# ===================== CLASSE Membre =====================

class Membre:
    def __init__(self, id_membre: str, nom: str, quota_max: int = 5):
        self.id_membre = id_membre
        self.nom = nom
        self.livres_empruntes = []
        self.quota_max = quota_max

    def peut_emprunter(self):
        return len(self.livres_empruntes) < self.quota_max

    def emprunter(self, isbn: str):
        if not self.peut_emprunter():
            raise QuotaEmpruntDepasseError(f"Le membre '{self.nom}' (ID {self.id_membre}) a atteint son quota.")
        self.livres_empruntes.append(isbn)

    def retourner(self, isbn: str):
        if isbn in self.livres_empruntes:
            self.livres_empruntes.remove(isbn)

    def to_line(self):
        nom = self.nom.replace(";", ",")
        emprunts = ",".join(self.livres_empruntes)
        return ";".join([self.id_membre, nom, emprunts])

    @classmethod
    def from_line(cls, line: str):
        parts = line.strip().split(";")
        if len(parts) < 2:
            raise ValueError(f"Ligne membre invalide: '{line}'")
        id_membre, nom = parts[0], parts[1]
        m = cls(id_membre=id_membre, nom=nom)
        if len(parts) >= 3 and parts[2]:
            m.livres_empruntes = parts[2].split(",")
        return m

    def __str__(self):
        return f"{self.nom} (ID {self.id_membre}) - emprunts: {len(self.livres_empruntes)}"


# ===================== CLASSE Bibliotheque =====================

class Bibliotheque:
    def __init__(self, data_dir: str | Path):
        self.data_dir = Path(data_dir)
        self.file_livres = self.data_dir / "livres.txt"
        self.file_membres = self.data_dir / "membres.txt"
        self.file_historique = self.data_dir / "historique.csv"
        self.livres = {}
        self.membres = {}
        self.historique = []

    def charger_tout(self):
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.charger_livres()
        self.charger_membres()
        self.charger_historique()

    def sauvegarder_tout(self):
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.sauvegarder_livres()
        self.sauvegarder_membres()
        self.sauvegarder_historique()

    def charger_livres(self):
        self.livres.clear()
        if not self.file_livres.exists():
            return
        with open(self.file_livres, "r", encoding="utf-8") as f:
            for ligne in f:
                if ligne.strip():
                    try:
                        livre = Livre.from_line(ligne)
                        self.livres[livre.isbn] = livre
                    except Exception:
                        pass

    def sauvegarder_livres(self):
        with open(self.file_livres, "w", encoding="utf-8") as f:
            for livre in self.livres.values():
                f.write(livre.to_line() + "\n")

    def charger_membres(self):
        self.membres.clear()
        if not self.file_membres.exists():
            return
        with open(self.file_membres, "r", encoding="utf-8") as f:
            for ligne in f:
                if ligne.strip():
                    try:
                        membre = Membre.from_line(ligne)
                        self.membres[membre.id_membre] = membre
                    except Exception:
                        pass

    def sauvegarder_membres(self):
        with open(self.file_membres, "w", encoding="utf-8") as f:
            for membre in self.membres.values():
                f.write(membre.to_line() + "\n")

    def charger_historique(self):
        self.historique.clear()
        if not self.file_historique.exists():
            return
        with open(self.file_historique, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                date = row.get("date", "").strip()
                isbn = row.get("isbn", "").strip()
                idm = row.get("id_membre", "").strip()
                action = row.get("action", "").strip()
                if date and isbn and idm and action:
                    self.historique.append((date, isbn, idm, action))

    def sauvegarder_historique(self):
        with open(self.file_historique, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["date", "isbn", "id_membre", "action"])
            for rec in self.historique:
                writer.writerow(rec)

    def lister_livres(self):
        if not self.livres:
            print("Aucun livre en base.")
            return
        for livre in self.livres.values():
            print(f"- {livre}")

    def ajouter_livre(self, isbn: str, titre: str, auteur: str, annee: int, genre: str):
        if isbn in self.livres:
            print(f"[!] Le livre ISBN {isbn} existe déjà.")
            return
        livre = Livre(isbn=isbn, titre=titre, auteur=auteur, annee=annee, genre=genre)
        self.livres[isbn] = livre
        print(f"Livre ajouté : {livre}")

    def supprimer_livre(self, isbn: str):
        if isbn not in self.livres:
            raise LivreInexistantError(f"ISBN {isbn} introuvable.")
        titre = self.livres[isbn].titre
        print(f"Livre supprimé : '{titre}' (ISBN {isbn})")
        del self.livres[isbn]

    def lister_membres(self):
        if not self.membres:
            print("Aucun membre en base.")
            return
        for membre in self.membres.values():
            print(f"- {membre}")

    def enregistrer_membre(self, id_membre: str, nom: str):
        if id_membre in self.membres:
            print(f"[!] Le membre ID {id_membre} existe déjà.")
            return
        membre = Membre(id_membre=id_membre, nom=nom)
        self.membres[id_membre] = membre
        print(f"Membre ajouté : {membre.nom} (ID {membre.id_membre})")

    def chercher_livre_par_titre(self, titre: str):
        return [livre for livre in self.livres.values() if titre.lower() in livre.titre.lower()]

    def chercher_membre_par_nom(self, nom: str):
        return [membre for membre in self.membres.values() if nom.lower() in membre.nom.lower()]

    def emprunter(self, isbn: str, id_membre: str):
        if id_membre not in self.membres:
            raise MembreInexistantError(f"Membre ID {id_membre} introuvable.")
        if isbn not in self.livres:
            raise LivreInexistantError(f"ISBN {isbn} introuvable.")
        livre = self.livres[isbn]
        membre = self.membres[id_membre]
        livre.emprunter()
        membre.emprunter(isbn)
        date_iso = datetime.date.today().isoformat()
        self.historique.append((date_iso, isbn, id_membre, "emprunt"))
        print(f"Emprunt : {membre.nom} (ID {id_membre}) a emprunté '{livre.titre}' (ISBN {isbn}) le {date_iso}")

    def retourner(self, isbn: str, id_membre: str):
        if id_membre not in self.membres:
            raise MembreInexistantError(f"Membre ID {id_membre} introuvable.")
        if isbn not in self.livres:
            raise LivreInexistantError(f"ISBN {isbn} introuvable.")
        livre = self.livres[isbn]
        membre = self.membres[id_membre]
        livre.retourner()
        membre.retourner(isbn)
        date_iso = datetime.date.today().isoformat()
        self.historique.append((date_iso, isbn, id_membre, "retour"))
        print(f"Retour : {membre.nom} (ID {id_membre}) a retourné '{livre.titre}' (ISBN {isbn}) le {date_iso}")

    def afficher_historique(self, max_lignes: int = 20):
        if not self.historique:
            print("Aucun historique.")
            return
        for rec in self.historique[-max_lignes:]:
            date, isbn, idm, action = rec
            titre = self.livres[isbn].titre if isbn in self.livres else "Titre inconnu"
            nom = self.membres[idm].nom if idm in self.membres else "Nom inconnu"
            print(f"{date} - {action} - '{titre}' (ISBN {isbn}) - {nom} (ID {idm})")
