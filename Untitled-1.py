import os

def charger_produits(nom_fichier):
    produits = []
    if os.path.exists(nom_fichier):
        with open(nom_fichier, "r") as fichier:
            for ligne in fichier:
                produits.append(ligne.strip())
    else:
        print(f"Le fichier {nom_fichier} n'existe pas.")
    return produits

def enregistrer_produits(nom_fichier, produits):
    with open(nom_fichier, "w") as fichier:
        for produit in produits:
            fichier.write(produit + "\n")

def afficher_produits(produits):
    if produits:
        print("\nListe des produits :")
        for i, produit in enumerate(produits, 1):
            print(f"{i}. {produit}")
    else:
        print("\nLa liste des produits est vide.")

def ajouter_produit(produits):
    produit = input("Entrez le nom du produit à ajouter : ").strip()
    if produit:
        produits.append(produit)
        print(f"Produit '{produit}' ajouté avec succès.")
    else:
        print("Le nom du produit ne peut pas être vide.")

def supprimer_produit(produits):
    afficher_produits(produits)
    try:
        index = int(input("Entrez le numéro du produit à supprimer : ")) - 1
        if 0 <= index < len(produits):
            produit_supprime = produits.pop(index)
            print(f"Produit '{produit_supprime}' supprimé avec succès.")
        else:
            print("Numéro invalide.")
    except ValueError:
        print("Entrée invalide. Veuillez entrer un numéro valide.")

def rechercher_produit(produits):
    recherche = input("Entrez le nom du produit à rechercher : ").strip()
    resultats = [p for p in produits if recherche.lower() in p.lower()]
    if resultats:
        print("\nProduits trouvés :")
        for produit in resultats:
            print(f"- {produit}")
    else:
        print(f"Aucun produit ne correspond à '{recherche}'.")

def trier_produits(produits):
    produits.sort()
    print("\nListe des produits triée avec succès.")

def menu_principal():
    nom_fichier = "produits.txt"
    produits = charger_produits(nom_fichier)

    while True:
        print("\n=== Gestion des Produits ===")
        print("1. Afficher la liste des produits")
        print("2. Ajouter un produit")
        print("3. Supprimer un produit")
        print("4. Rechercher un produit")
        print("5. Trier les produits par ordre alphabétique")
        print("6. Enregistrer et quitter")

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
            trier_produits(produits)
        elif choix == "6":
            enregistrer_produits(nom_fichier, produits)
            print("Modifications enregistrées. Au revoir !")
            break
        else:
            print("Choix invalide, veuillez réessayer.")

if __name__ == "__main__":
    menu_principal()
