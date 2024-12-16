import tkinter as tk
from tkinter import ttk, messagebox
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# Fonctions pour la gestion des produits
def load_produits_from_file():
    try:
        with open("produits.txt", "r") as file:
            lignes = file.readlines()
            produits = []
            for ligne in lignes:
                try:
                    nom, stock, prix = ligne.strip().split(",")
                    produits.append({"nom": nom, "stock": int(stock), "prix": float(prix)})
                except ValueError:
                    continue
    except FileNotFoundError:
        produits = []
    return produits

def save_produits_to_file(produits):
    with open("produits.txt", "w") as file:
        for produit in produits:
            file.write(f"{produit['nom']},{produit['stock']},{produit['prix']}\n")

def load_commandes_from_file():
    try:
        with open("commandes.txt", "r") as file:
            lignes = file.readlines()
            commandes = []
            for ligne in lignes:
                try:
                    id, contenu, statut = ligne.strip().split(",")
                    commandes.append({"id": id, "contenu": contenu, "statut": statut})
                except ValueError:
                    continue
    except FileNotFoundError:
        commandes = []
    return commandes

def save_commandes_to_file(commandes):
    with open("commandes.txt", "w") as file:
        for commande in commandes:
            file.write(f"{commande['id']},{commande['contenu']},{commande['statut']}\n")

def update_products_tree(produits):
    for row in tree.get_children():
        tree.delete(row)

    for produit in produits:
        tree.insert("", "end", values=(produit['nom'], produit['prix'], produit['stock']))

def add_product(produits):
    def save_product():
        nom = entry_nom.get()
        try:
            prix = float(entry_prix.get())
            stock = int(entry_stock.get())
        except ValueError:
            messagebox.showerror("Erreur", "Veuillez entrer des valeurs valides pour le prix et le stock.")
            return

        produits.append({"nom": nom, "prix": prix, "stock": stock})
        save_produits_to_file(produits)
        update_products_tree(produits)
        add_window.destroy()

    add_window = tk.Toplevel(root)
    add_window.title("Ajouter un produit")

    tk.Label(add_window, text="Nom:").grid(row=0, column=0)
    entry_nom = tk.Entry(add_window)
    entry_nom.grid(row=0, column=1)

    tk.Label(add_window, text="Prix:").grid(row=1, column=0)
    entry_prix = tk.Entry(add_window)
    entry_prix.grid(row=1, column=1)

    tk.Label(add_window, text="Stock:").grid(row=2, column=0)
    entry_stock = tk.Entry(add_window)
    entry_stock.grid(row=2, column=1)

    tk.Button(add_window, text="Sauvegarder", command=save_product).grid(row=3, column=0, columnspan=2)

def delete_product(produits):
    selected_item = tree.selection()
    if not selected_item:
        messagebox.showwarning("Avertissement", "Veuillez sélectionner un produit à supprimer.")
        return

    nom = tree.item(selected_item, "values")[0]
    produits = [p for p in produits if p['nom'] != nom]
    save_produits_to_file(produits)
    update_products_tree(produits)
    messagebox.showinfo("Suppression", f"Le produit '{nom}' a été supprimé.")

def display_commandes():
    commandes = load_commandes_from_file()
    commandes_window = tk.Toplevel(root)
    commandes_window.title("Commandes")

    tree_commandes = ttk.Treeview(commandes_window, columns=("ID", "Contenu", "Statut"), show="headings")
    tree_commandes.heading("ID", text="ID")
    tree_commandes.heading("Contenu", text="Contenu")
    tree_commandes.heading("Statut", text="Statut")

    tree_commandes.pack(fill=tk.BOTH, expand=True)

    for commande in commandes:
        tree_commandes.insert("", "end", values=(commande['id'], commande['contenu'], commande['statut']))

def display_statistics(produits):
    stats_window = tk.Toplevel(root)
    stats_window.title("Statistiques")

    fig = Figure(figsize=(6, 4), dpi=100)
    ax = fig.add_subplot(111)

    noms = [produit['nom'] for produit in produits]
    stocks = [produit['stock'] for produit in produits]

    ax.bar(noms, stocks, color="blue")
    ax.set_title("Stock des produits")
    ax.set_xlabel("Produits")
    ax.set_ylabel("Quantité en stock")

    canvas = FigureCanvasTkAgg(fig, master=stats_window)
    canvas.draw()
    canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

def treeview_sort_column(tv, col, reverse):
    l = [(tv.set(k, col), k) for k in tv.get_children('')]
    if col == "Stock":
        l.sort(key=lambda x: int(x[0]), reverse=reverse)
    else:
        l.sort(reverse=reverse)

    for index, (val, k) in enumerate(l):
        tv.move(k, '', index)

    for column in tv["columns"]:
        tv.heading(column, text=column)
    if reverse:
        tv.heading(col, text=f"{col} ▲")
    else:
        tv.heading(col, text=f"{col} ▼")

    tv.heading(col, command=lambda: treeview_sort_column(tv, col, not reverse))

root = tk.Tk()
root.title("Gestion des commandes")

frame_products = tk.Frame(root)
frame_products.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

tree = ttk.Treeview(frame_products, columns=("Nom", "Prix", "Stock"), show="headings")
tree.heading("Nom", text="Nom", command=lambda: treeview_sort_column(tree, "Nom", False))
tree.heading("Prix", text="Prix", command=lambda: treeview_sort_column(tree, "Prix", False))
tree.heading("Stock", text="Stock", command=lambda: treeview_sort_column(tree, "Stock", False))

tree.pack(fill=tk.BOTH, expand=True)

produits = load_produits_from_file()
update_products_tree(produits)

btn_frame = tk.Frame(root)
btn_frame.pack(fill=tk.X, padx=10, pady=10)

tk.Button(btn_frame, text="Ajouter un produit", command=lambda: add_product(produits)).pack(side=tk.LEFT, padx=5)
tk.Button(btn_frame, text="Supprimer un produit", command=lambda: delete_product(produits)).pack(side=tk.LEFT, padx=5)
tk.Button(btn_frame, text="Afficher les commandes", command=display_commandes).pack(side=tk.LEFT, padx=5)
tk.Button(btn_frame, text="Statistiques", command=lambda: display_statistics(produits)).pack(side=tk.LEFT, padx=5)

root.mainloop()
