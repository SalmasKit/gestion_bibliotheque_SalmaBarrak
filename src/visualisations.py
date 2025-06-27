from collections import Counter
import datetime
import matplotlib.pyplot as plt

from collections import Counter
import matplotlib.pyplot as plt

#diagramme circulaire % par genre
def diagramme_pourcentage_genres(livres: dict[str, any]):
    genres = [livre.genre for livre in livres.values()]
    counts = Counter(genres)
    labels = list(counts.keys())
    sizes = list(counts.values())

    if not labels:
        print("Aucun livre pour générer le diagramme.")
        return

    # my palette
    colors = ['#2d1409', '#541308', '#643f24', '#846e51', '#b19c85']

    # Ajuste le nombre de couleurs à celui des genres
    colors = colors[:len(labels)]

    plt.figure()
    plt.pie(sizes, labels=labels, autopct='%1.1f%%', colors=colors)
    plt.title("Répartition des livres par genre")
    plt.tight_layout()
    plt.show()

#Histogramme des 10 auteurs plus populaires
def top_auteurs_populaires(historique: list[tuple[str, str, str, str]], livres: dict[str, any], top_n: int = 10):
    emprunts = [isbn for (date, isbn, idm, action) in historique if action == "emprunt"]
    if not emprunts:
        print("Aucun emprunt pour générer le top auteurs.")
        return

    # Compter emprunts par auteur
    auteur_counts = Counter()
    for isbn in emprunts:
        if isbn in livres:
            auteur = livres[isbn].auteur
            if auteur:  # éviter les auteurs vides
                auteur_counts[auteur] += 1

    if not auteur_counts:
        print("Aucun auteur à afficher.")
        return

    # Trier par nombre d'emprunts décroissant
    sorted_auteurs = auteur_counts.most_common()

    # Inclure les ex-aequo du dernier
    top = []
    seuil = 0
    for auteur, count in sorted_auteurs:
        if len(top) < top_n:
            top.append((auteur, count))
            seuil = count
        elif count == seuil:
            top.append((auteur, count))
        else:
            break

    auteurs, emprunt_counts = zip(*top)

    couleurs_palette = ['#2d1409', '#541308', '#643f24', '#846e51', '#b19c85']
    couleurs = [couleurs_palette[i % len(couleurs_palette)] for i in range(len(auteurs))]

    plt.figure(figsize=(12, 6))
    bars = plt.bar(auteurs, emprunt_counts, color=couleurs)
    plt.xticks(rotation=45, ha='right', fontsize=10)
    plt.title(f"Top {top_n} des auteurs les plus empruntés ", fontsize=14, fontweight='bold')

    # Ajouter les valeurs au-dessus des barres
    for bar, count in zip(bars, emprunt_counts):
        plt.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.2,
                 str(count), ha='center', va='bottom', fontsize=9)

    plt.tight_layout()
    plt.show()

#courbe des emprunts dans un mois     
def courbe_activite_emprunts(historique: list[tuple[str,str,str,str]], jours: int = 30):
    today = datetime.date.today()
    dates = [datetime.date.fromisoformat(date) for (date, isbn, idm, action) in historique if action == "emprunt"]
    if not dates:
        print("Aucune activité d'emprunt pour la courbe.")
        return
    counter = Counter([d for d in dates if (today - d).days < jours])
    jours_list = [today - datetime.timedelta(days=i) for i in range(jours-1, -1, -1)]
    counts = [counter.get(d, 0) for d in jours_list]
    plt.figure()
    plt.plot(jours_list, counts, marker='o')
    plt.xticks(rotation=45, ha='right')
    plt.title("Activité des emprunts (30 derniers jours)")
    plt.tight_layout()
    plt.show()

