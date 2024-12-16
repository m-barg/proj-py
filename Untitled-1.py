import tkinter as tk
from tkinter import ttk, messagebox
import json
import sqlite3
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

def setup_database():
    conn = sqlite3.connect("commerce.db")
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS produits (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nom TEXT,
        prix REAL,
        stock INTEGER
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS commandes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        contenu TEXT,
        statut TEXT
    )
    """)

    conn.commit()
    conn.close()

def reset_autoincrement():
    conn = sqlite3.connect("commerce.db")
    cursor = conn.cursor()
    cursor.execute("DELETE FROM sqlite_sequence WHERE name='produits'")
    conn.commit()
    conn.close()

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

    conn = sqlite3.connect("commerce.db")
    cursor = conn.cursor()

    cursor.execute("DELETE FROM produits")
    for produit in produits:
        cursor.execute(
            "INSERT INTO produits (nom, prix, stock) VALUES (?, ?, ?)",
            (produit["nom"], produit["prix"], produit["stock"]),
        )

    conn.commit()
    conn.close()

def load_commandes():
    try:
        with open("commandes.json", "r") as file:
            commandes = json.load(file)
    except FileNotFoundError:
        commandes = []
    except json.JSONDecodeError:
        commandes = []

    return commandes

def save_commandes(commandes):
    with open("commandes.json", "w") as file:
        json.dump(commandes, file, indent=4)

def update_products_tree():
    for row in tree.get_children():
        tree.delete(row)

    conn = sqlite3.connect("commerce.db")
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT * FROM produits")
        for row in cursor.fetchall():
            tree.insert("", "end", values=row)
    except sqlite3.OperationalError:
        messagebox.showerror("Erreur", "La table 'produits' n'existe pas. Veuillez vérifier la base de données.")
    finally:
        conn.close()

def add_product():
    def save_product():
        nom = entry_nom.get()
        try:
            prix = float(entry_prix.get())
            stock = int(entry_stock.get())
        except ValueError:
            messagebox.showerror("Erreur", "Veuillez entrer des valeurs valides pour le prix et le stock.")
            return

        conn = sqlite3.connect("commerce.db")
        cursor = conn.cursor()
        cursor.execute("INSERT INTO produits (nom, prix, stock) VALUES (?, ?, ?)", (nom, prix, stock))
        conn.commit()
        conn.close()

        update_products_tree()
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

def delete_product():
    selected_item = tree.selection()
    if not selected_item:
        messagebox.showwarning("Avertissement", "Veuillez sélectionner un produit à supprimer.")
        return

    product_id = tree.item(selected_item, "values")[0]

    conn = sqlite3.connect("commerce.db")
    cursor = conn.cursor()
    cursor.execute("DELETE FROM produits WHERE id=?", (product_id,))
    conn.commit()
    conn.close()

    update_products_tree()
    messagebox.showinfo("Suppression", f"Le produit avec l'ID {product_id} a été supprimé.")

def display_commandes():
    commandes = load_commandes()
    commandes_window = tk.Toplevel(root)
    commandes_window.title("Commandes")

    tree_commandes = ttk.Treeview(commandes_window, columns=("ID", "Contenu", "Statut"), show="headings")
    tree_commandes.heading("ID", text="ID")
    tree_commandes.heading("Contenu", text="Contenu")
    tree_commandes.heading("Statut", text="Statut")

    tree_commandes.pack(fill=tk.BOTH, expand=True)

    for idx, commande in enumerate(commandes):
        tree_commandes.insert("", "end", values=(idx + 1, json.dumps(commande.get("contenu", "")), commande.get("statut", "")))

def display_statistics():
    conn = sqlite3.connect("commerce.db")
    cursor = conn.cursor()

    try:
        cursor.execute("SELECT nom, stock FROM produits")
        products = cursor.fetchall()
    except sqlite3.OperationalError:
        messagebox.showerror("Erreur", "La table 'produits' n'existe pas. Veuillez vérifier la base de données.")
        return
    finally:
        conn.close()

    stats_window = tk.Toplevel(root)
    stats_window.title("Statistiques")

    fig = Figure(figsize=(6, 4), dpi=100)
    ax = fig.add_subplot(111)

    noms = [product[0] for product in products]
    stocks = [product[1] for product in products]

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

tree = ttk.Treeview(frame_products, columns=("ID", "Nom", "Prix", "Stock"), show="headings")
tree.heading("ID", text="ID", command=lambda: treeview_sort_column(tree, "ID", False))
tree.heading("Nom", text="Nom", command=lambda: treeview_sort_column(tree, "Nom", False))
tree.heading("Prix", text="Prix", command=lambda: treeview_sort_column(tree, "Prix", False))
tree.heading("Stock", text="Stock", command=lambda: treeview_sort_column(tree, "Stock", False))

tree.pack(fill=tk.BOTH, expand=True)
update_products_tree()

btn_frame = tk.Frame(root)
btn_frame.pack(fill=tk.X, padx=10, pady=10)

tk.Button(btn_frame, text="Ajouter un produit", command=add_product).pack(side=tk.LEFT, padx=5)
tk.Button(btn_frame, text="Supprimer un produit", command=delete_product).pack(side=tk.LEFT, padx=5)
tk.Button(btn_frame, text="Afficher les commandes", command=display_commandes).pack(side=tk.LEFT, padx=5)
tk.Button(btn_frame, text="Statistiques", command=display_statistics).pack(side=tk.LEFT, padx=5)

setup_database()
load_produits_from_file()
reset_autoincrement()
root.mainloop()
