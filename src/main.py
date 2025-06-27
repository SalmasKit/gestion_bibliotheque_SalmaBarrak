import sys
from pathlib import Path

from bibliotheque import Bibliotheque
from exceptions import (
    MembreInexistantError,
    LivreInexistantError,
    LivreIndisponibleError,
    QuotaEmpruntDepasseError
)
import visualisations as vis


def menu():
    """
    Affiche le menu principal de l'application en mode console.
    """
    print("\n=== Gestion Bibliothèque ===")
    print("1. Lister les livres")
    print("2. Ajouter un livre")
    print("3. Supprimer un livre")
    print("4. Lister les membres")
    print("5. Enregistrer un membre")
    print("6. Emprunter un livre")
    print("7. Retourner un livre")
    print("8. Afficher historique")
    print("9. Afficher statistiques")
    print("0. Quitter")


def main(data_dir):
    """
    Fonction principale en mode console qui gère les interactions avec l'utilisateur.
    Charge les données, affiche le menu et exécute les actions choisies.
    """
    # Initialisber biblio
    biblio = Bibliotheque(data_dir=data_dir)
    biblio.charger_tout()

    # Boucle infinie jusqu'à ce que l'utilisateur choisi de quitter
    while True:
        menu()
        choix = input("Choix: ").strip()

        if choix == "1":
            # Affiche tous les livres
            biblio.lister_livres()

        elif choix == "2":
            # Ajout d'un nouveau livre
            isbn = input("ISBN: ").strip()
            titre = input("Titre: ").strip()
            auteur = input("Auteur: ").strip()
            try:
                annee = int(input("Année: ").strip())
            except ValueError:
                print("[!] Année invalide.")
                continue
            genre = input("Genre: ").strip()
            biblio.ajouter_livre(isbn=isbn, titre=titre, auteur=auteur, annee=annee, genre=genre)
            biblio.sauvegarder_tout()

        elif choix == "3":
            # Suppression d'un livre existant
            isbn = input("ISBN à supprimer: ").strip()
            try:
                biblio.supprimer_livre(isbn)
                biblio.sauvegarder_tout()
            except LivreInexistantError as e:
                print(f"[!] {e}")

        elif choix == "4":
            # Affiche tous les membres
            biblio.lister_membres()

        elif choix == "5":
            # Enregistrement d'un nouveau membre
            idm = input("ID membre: ").strip()
            nom = input("Nom: ").strip()
            biblio.enregistrer_membre(id_membre=idm, nom=nom)
            biblio.sauvegarder_tout()

        elif choix == "6":
            # Emprunt d'un livre
            isbn = input("ISBN à emprunter: ").strip()
            idm = input("ID membre: ").strip()
            try:
                biblio.emprunter(isbn, idm)
                biblio.sauvegarder_tout()
            except (MembreInexistantError, LivreInexistantError, LivreIndisponibleError, QuotaEmpruntDepasseError) as e:
                print(f"[!] {e}")

        elif choix == "7":
            # Retour d'un livre
            isbn = input("ISBN à retourner: ").strip()
            idm = input("ID membre: ").strip()
            try:
                biblio.retourner(isbn, idm)
                biblio.sauvegarder_tout()
            except (MembreInexistantError, LivreInexistantError) as e:
                print(f"[!] {e}")

        elif choix == "8":
            # Affiche l'historique des emprunts et retours
            biblio.afficher_historique()

        elif choix == "9":
            # Affiche les statistiques via les visualisations
            vis.diagramme_pourcentage_genres(biblio.livres)
            vis.top_auteurs_populaires(biblio.historique, biblio.livres)
            vis.courbe_activite_emprunts(biblio.historique)

        elif choix == "0":
            # Sauvegarde des données et sortie propre
            biblio.sauvegarder_tout()
            print("Au revoir.")
            sys.exit(0)

        else:
            # Gestion des choix invalides
            print("[!] Choix invalide.")


if __name__ == "__main__":
    # Définition des chemins relatifs au dossier racine
    ROOT_DIR = Path(__file__).resolve().parent.parent
    DATA_DIR = ROOT_DIR / "data"

    # Choix du mode d'affichage : console ou interface graphique
    choix_mode = input("Choisissez le mode (1=Console, 2=GUI): ").strip()
    if choix_mode == "2":
        from interface_tk import BibliothequeGUI
        app = BibliothequeGUI(DATA_DIR)
        app.mainloop()
        sys.exit(0)
    else:
        main(DATA_DIR)
