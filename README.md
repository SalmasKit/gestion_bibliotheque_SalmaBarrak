# Gestion Bibliothèque

**Auteur :** Salma Barrak

## Guide d'installation

1. **Prérequis** :  
   - Python 3.7 ou supérieur  
   - Bibliothèque matplotlib (pour les visualisations)  

2. **Installation des dépendances** :  
   Ouvre un terminal et lance :  
   pip install matplotlib
   
Organisation des fichiers :
-Place le dossier data à la racine du projet (contenant les fichiers de données).
-Les fichiers sources sont dans src/ (par exemple bibliotheque.py, exceptions.py, visualisations.py, etc.).
-Le script principal (celui avec le menu) est dans src/main.py

Lancement de l'application :
Depuis le dossier racine, exécute :
python src/main.py


3. **Exemples d'utilisation**:
L'application propose deux modes : console ou interface graphique (GUI).

-Mode console
Au lancement, choisis le mode console en entrant 1.


Choisissez le mode (1=Console, 2=GUI): 1

=== Gestion Bibliothèque ===
1. Lister les livres
2. Ajouter un livre
3. Supprimer un livre
4. Lister les membres
5. Enregistrer un membre
6. Emprunter un livre
7. Retourner un livre
8. Afficher historique
9. Afficher statistiques
0. Quitter

Ajouter un livre
Choix: 2
ISBN: 9781234567890
Titre: Le Petit Prince
Auteur: Antoine de Saint-Exupéry
Année: 1943
Genre: Roman

Emprunter un livre
Choix: 6
ISBN à emprunter: 9781234567890
ID membre: M001

Afficher les statistiques
Choix: 9
Cela affiche des graphiques avec :

La répartition des livres par genre

Le top des auteurs les plus empruntés

La courbe d'activité des emprunts sur 30 jours




-Mode interface graphique (GUI)
Au lancement, choisis le mode GUI en entrant 2.

Une fenêtre s'ouvre avec les différentes options pour gérer la bibliothèque de manière visuelle.

Remarques
Les données sont automatiquement chargées au démarrage et sauvegardées après chaque modification.

Les exceptions (livres inexistants, membres inconnus, etc.) sont gérées avec des messages clairs à l'utilisateur.

[Video Presentation (Google Drive)](https://drive.google.com/drive/folders/1vZ1h3LzWy861giLfJ2akHJsqoRjri3hT?usp=sharing)

Merci!!

