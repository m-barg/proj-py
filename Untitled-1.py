import os
import shutil

def charger_produits(nom_fichier):
    produits = []
    if os.path.exists(nom_fichier):
        with open(nom_fichier, "r") as fichier:
            for ligne in fichier:
                try:
                    nom, quantite, prix = ligne.strip().split(",")
                    produits.append({"nom": nom, "quantite": int(quantite), "prix": float(prix)})
                except ValueError:
                    print(f"Ligne ignorée : {ligne.strip()}")
    else:
        print(f"Le fichier {nom_fichier} n'existe pas.")
    return produits

def enregistrer_produits(nom_fichier, produits):
    with open(nom_fichier, "w") as fichier:
        for produit in produits:
            fichier.write(f"{produit['nom']},{produit['quantite']},{produit['prix']}\n")

def afficher_produits(produits):
    if produits:
        print("\nListe des produits :")
        print(f"{'#':<5}{'Nom':<20}{'Quantité':<10}{'Prix':<10}")
        print("-" * 45)
        for i, produit in enumerate(produits, 1):
            print(f"{i:<5}{produit['nom']:<20}{produit['quantite']:<10}{produit['prix']:<10.2f}")
    else:
        print("\nLa liste des produits est vide.")

def ajouter_produit(produits):
    nom = input("Entrez le nom du produit à ajouter : ").strip()
    if nom:
        try:
            quantite = int(input("Entrez la quantité : ").strip())
            prix = float(input("Entrez le prix : ").strip())
            produits.append({"nom": nom, "quantite": quantite, "prix": prix})
            print(f"Produit '{nom}' ajouté avec succès.")
        except ValueError:
            print("Quantité ou prix invalide. Veuillez réessayer.")
    else:
        print("Le nom du produit ne peut pas être vide.")

def supprimer_produit(produits):
    afficher_produits(produits)
    try:
        index = int(input("Entrez le numéro du produit à supprimer : ")) - 1
        if 0 <= index < len(produits):
            produit_supprime = produits.pop(index)
            print(f"Produit '{produit_supprime['nom']}' supprimé avec succès.")
        else:
            print("Numéro invalide.")
    except ValueError:
        print("Entrée invalide. Veuillez entrer un numéro valide.")

def modifier_produit(produits):
    afficher_produits(produits)
    try:
        index = int(input("Entrez le numéro du produit à modifier : ")) - 1
        if 0 <= index < len(produits):
            produit = produits[index]
            print(f"Produit sélectionné : {produit['nom']}")
            nouveau_quantite = input(f"Entrez la nouvelle quantité (actuelle : {produit['quantite']}) ou laissez vide pour ne pas changer : ").strip()
            nouveau_prix = input(f"Entrez le nouveau prix (actuel : {produit['prix']:.2f}) ou laissez vide pour ne pas changer : ").strip()

            if nouveau_quantite:
                try:
                    produit['quantite'] = int(nouveau_quantite)
                except ValueError:
                    print("Quantité invalide. Modifications annulées.")
                    return

            if nouveau_prix:
                try:
                    produit['prix'] = float(nouveau_prix)
                except ValueError:
                    print("Prix invalide. Modifications annulées.")
                    return

            print(f"Produit '{produit['nom']}' modifié avec succès.")
        else:
            print("Numéro invalide.")
    except ValueError:
        print("Entrée invalide. Veuillez entrer un numéro valide.")

def rechercher_produit(produits):
    print("\nChoisissez un mode de recherche :")
    print("1. Recherche par nom")
    print("2. Recherche dichotomique")
    choix_recherche = input("Entrez votre choix : ").strip()

    if choix_recherche == "1":
        recherche = input("Entrez le nom du produit à rechercher : ").strip()
        resultats = [p for p in produits if recherche.lower() in p['nom'].lower()]
        if resultats:
            print("\nProduits trouvés :")
            print(f"{'Nom':<20}{'Quantité':<10}{'Prix':<10}")
            print("-" * 45)
            for produit in resultats:
                print(f"{produit['nom']:<20}{produit['quantite']:<10}{produit['prix']:<10.2f}")
        else:
            print(f"Aucun produit ne correspond à '{recherche}'.")
    elif choix_recherche == "2":
        produits.sort(key=lambda p: p['nom'].lower())
        print("\nListe entièrement triée pour recherche dichotomique.")
        recherche_dichotomique(produits)
    else:
        print("Choix invalide pour la recherche.")

def recherche_dichotomique(produits):
    cible = input("Entrez le nom du produit à rechercher (recherche dichotomique) : ").strip().lower()
    gauche, droite = 0, len(produits) - 1
    while gauche <= droite:
        milieu = (gauche + droite) // 2
        produit_nom = produits[milieu]['nom'].lower()

        if produit_nom == cible:
            print(f"\nProduit trouvé : {produits[milieu]['nom']}, Quantité : {produits[milieu]['quantite']}, Prix : {produits[milieu]['prix']:.2f}")
            return
        elif produit_nom < cible:
            gauche = milieu + 1
        else:
            droite = milieu - 1

    print(f"\nLe produit '{cible}' n'a pas été trouvé dans la liste.")

def trier_produits(produits):
    print("\nChoisissez un critère de tri :")
    print("1. Par ordre alphabétique")
    print("2. Par quantité")
    print("3. Par prix")
    choix_critere = input("Entrez votre choix : ").strip()

    if choix_critere == "1":
        produits.sort(key=lambda p: p['nom'].lower())
        print("\nListe des produits triée par ordre alphabétique.")
    elif choix_critere == "2":
        tri_bulle_quantite(produits)
        print("\nListe des produits triée par quantité (ordre décroissant).")
    elif choix_critere == "3":
        tri_par_prix()
        print("\nListe des produits triée par prix dans le fichier.")
    else:
        print("Choix invalide. Aucun tri effectué.")

def tri_bulle_quantite(produits):
    n = len(produits)
    for i in range(n):
        for j in range(0, n-i-1):
            if produits[j]['quantite'] < produits[j+1]['quantite']:
                produits[j], produits[j+1] = produits[j+1], produits[j]

def quicksort_prix(lignes):
    lignes = [ligne for ligne in lignes if ligne.strip()]  
    if len(lignes) <= 1:
        return lignes

    try:
        pivot = float(lignes[-1].strip().split(",")[2])  
    except (IndexError, ValueError):
        print("Erreur dans le format des données.")
        return lignes

    moins_que_pivot = [ligne for ligne in lignes[:-1] if float(ligne.strip().split(",")[2]) <= pivot]
    plus_que_pivot = [ligne for ligne in lignes[:-1] if float(ligne.strip().split(",")[2]) > pivot]

    return quicksort_prix(moins_que_pivot) + [lignes[-1]] + quicksort_prix(plus_que_pivot)

def tri_par_prix():
    nom_fichier = "produits.txt"
    if os.path.exists(nom_fichier):
        shutil.copy(nom_fichier, f"{nom_fichier}.backup")  #j'ai creer un backup pour sauvegarder le fichier,n'y touche pass
        with open(nom_fichier, "r") as liste:
            lignes = liste.readlines()

        lignes_triees = quicksort_prix(lignes)
        with open(nom_fichier, "w") as fichier:
            for ligne in lignes_triees:
                fichier.write(ligne.strip() + "\n")

        print("Le tri par prix avec QuickSort a été effectué et enregistré dans le fichier.")
    else:
        print(f"Le fichier {nom_fichier} n'existe pas.")

def menu_principal():
    nom_fichier = "produits.txt"
    produits = charger_produits(nom_fichier)

    while True:
        print("\n=== Gestion des Produits ===")
        print("1. Afficher la liste des produits")
        print("2. Ajouter un produit")
        print("3. Supprimer un produit")
        print("4. Rechercher un produit")
        print("5. Modifier un produit")
        print("6. Trier les produits")
        print("7. Enregistrer et quitter")

        choix = input("Entrez votre choix : ").strip()

        if choix == "1":
            afficher_produits(produits)
        elif choix == "2":
            ajouter_produit(produits)
        elif choix == "3":
            supprimer_produit(produits)
        elif choix == "4":
            rechercher_produit(produits)
        elif choix == "5":
            modifier_produit(produits)
        elif choix == "6":
            trier_produits(produits)
        elif choix == "7":
            enregistrer_produits(nom_fichier, produits)
            print("Modifications enregistrées. Au revoir !")
            break
        else:
            print("Choix invalide, veuillez réessayer.")

if __name__ == "__main__":
    menu_principal()
