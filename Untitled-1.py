import tkinter as tk
from tkinter import messagebox, ttk
import pandas as pd
import hashlib
import requests
import json

FILE_USERS = "utilisateurs.csv"
FILE_PRODUCTS = "produits.csv"
FILE_COMMANDS = "commandes.json"

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def is_password_compromised(password):
    sha1_hash = hashlib.sha1(password.encode('utf-8')).hexdigest().upper()
    suffix = sha1_hash[5:]
    prefix = sha1_hash[:5]

    url = f"https://api.pwnedpasswords.com/range/{prefix}"
    response = requests.get(url)

    if response.status_code != 200:
        raise RuntimeError(f"erreur avec l'API pwndpass : {response.status_code}")

    hashes = (line.split(':') for line in response.text.splitlines())
    for returned_suffix, count in hashes:
        if returned_suffix == suffix:
            return int(count)
    return 0

def load_users():
    try:
        return pd.read_csv(FILE_USERS)
    except FileNotFoundError:
        return pd.DataFrame(columns=["Utilisateur", "Mot_de_passe"])

def save_users(users):
    users.to_csv(FILE_USERS, index=False)

def load_products():
    try:
        return pd.read_csv(FILE_PRODUCTS)
    except FileNotFoundError:
        return pd.DataFrame(columns=["User", "Nom", "Prix", "Stock"])

def save_products(products):
    products.to_csv(FILE_PRODUCTS, index=False)

def load_commands():
    try:
        with open(FILE_COMMANDS, "r") as file:
            return json.load(file)
    except FileNotFoundError:
        return []

def save_commands(commands):
    with open(FILE_COMMANDS, "w") as file:
        json.dump(commands, file, indent=4)

class Application(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Gestion des stocks - Multi-utilisateurs")
        self.geometry("600x400")
        self.current_user = None
        self.users = load_users()
        self.products = load_products()
        self.show_login_screen()

    def show_login_screen(self):
        for widget in self.winfo_children():
            widget.destroy()

        tk.Label(self, text="Connexion", font=("Arial", 20)).pack(pady=10)

        tk.Label(self, text="Nom d'user:").pack()
        username_entry = tk.Entry(self)
        username_entry.pack()

        tk.Label(self, text="Mot de passe:").pack()
        password_entry = tk.Entry(self, show="*")
        password_entry.pack()

        tk.Button(self, text="Se connecter.", command=lambda: self.login(username_entry.get(), password_entry.get())).pack(pady=5)
        tk.Button(self, text="S'inscrire.", command=lambda: self.show_register_screen()).pack(pady=5)

    def show_register_screen(self):
        for widget in self.winfo_children():
            widget.destroy()

        tk.Label(self, text="Inscription", font=("Arial", 20)).pack(pady=10)

        tk.Label(self, text="Nom d'utilisateur:").pack()
        username_entry = tk.Entry(self)
        username_entry.pack()

        tk.Label(self, text="Mot de passe:").pack()
        password_entry = tk.Entry(self, show="*")
        password_entry.pack()

        tk.Button(self, text="S'inscrire", command=lambda: self.register(username_entry.get(), password_entry.get())).pack(pady=5)
        tk.Button(self, text="Retour", command=lambda: self.show_login_screen()).pack(pady=5)

    def login(self, username, password):
        hashed_password = hash_password(password)
        if not self.users[(self.users["Utilisateur"] == username) & (self.users["Mot_de_passe"] == hashed_password)].empty:
            self.current_user = username
            self.show_product_management_screen()
        else:
            messagebox.showerror("Erreur", "Nom d'utilisateur ou mot de passe incorrect.")

    def register(self, username, password):
        if username.strip() == "" or password.strip() == "":
            messagebox.showerror("Erreur", "Veuillez remplir tous les champs.")
            return

        if not self.users[self.users["Utilisateur"] == username].empty:
            messagebox.showerror("Erreur", "Ce nom d'utilisateur est déjà pris.")
            return

        if len(password) <= 8:
            messagebox.showerror("Erreur MDP", f"Veuillez choisir un mot de passe de plus de 8 caractères.")
            return

        try:
            compromised_count = is_password_compromised(password)
            if compromised_count > 0:
                messagebox.showerror(
                    "Erreur",
                    f"Ce mot de passe est trop faible. Il a été compromis {compromised_count} fois dans des violations de données. Veuillez choisir un mot de passe plus sécurisé."
                )
                return
        except RuntimeError as e:
            messagebox.showerror("Erreur", f"Problème lors de la vérification du mot de passe : {e}")
            return

        new_user = {"Utilisateur": username, "Mot_de_passe": hash_password(password)}
        self.users = pd.concat([self.users, pd.DataFrame([new_user])], ignore_index=True)
        save_users(self.users)

        messagebox.showinfo("Succès", "Inscription réussie.")
        self.show_login_screen()

    def show_product_management_screen(self):
        for widget in self.winfo_children():
            widget.destroy()

        tk.Label(self, text=f"Gestion des produits - {self.current_user}", font=("Arial", 20)).pack(pady=10)

        product_frame = tk.Frame(self)
        product_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        columns = ["Nom", "Prix", "Stock"]
        self.tree = ttk.Treeview(product_frame, columns=columns, show="headings")
        for col in columns:
            self.tree.heading(col, text=col, command=lambda c=col: self.treeview_sort_column(c, False))
        self.tree.pack(fill=tk.BOTH, expand=True)

        btn_frame = tk.Frame(self)
        btn_frame.pack(fill=tk.X, padx=10, pady=5)

        tk.Button(btn_frame, text="Ajouter un produit", command=self.add_product).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="Supprimer un produit", command=self.delete_product).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="Déconnexion", command=self.show_login_screen).pack(side=tk.RIGHT, padx=5)
        tk.Button(btn_frame, text="Voir les commandes", command=self.show_orders).pack(side=tk.LEFT, padx=5)

        self.update_product_tree()

    def update_product_tree(self):
        for row in self.tree.get_children():
            self.tree.delete(row)

        user_products = self.products[self.products["User"] == self.current_user]
        for _, product in user_products.iterrows():
            self.tree.insert("", "end", values=(product["Nom"], product["Prix"], product["Stock"]))

    def add_product(self):
        def save_new_product():
            nom = entry_nom.get()
            try:
                prix = float(entry_prix.get())
                stock = int(entry_stock.get())
            except ValueError:
                messagebox.showerror("Erreur", "Prix et stock doivent être des nombres.")
                return

            new_product = {"User": self.current_user, "Nom": nom, "Prix": prix, "Stock": stock}
            self.products = pd.concat([self.products, pd.DataFrame([new_product])], ignore_index=True)
            save_products(self.products)
            self.update_product_tree()
            add_window.destroy()

        add_window = tk.Toplevel(self)
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

        tk.Button(add_window, text="Ajouter", command=save_new_product).grid(row=3, column=0, columnspan=2)

    def delete_product(self):
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showwarning("Avertissement", "Veuillez sélectionner un produit à supprimer.")
            return

        nom = self.tree.item(selected_item, "values")[0]
        self.products = self.products[(self.products["Nom"] != nom) | (self.products["User"] != self.current_user)]
        save_products(self.products)
        self.update_product_tree()

    def show_orders(self):
        for widget in self.winfo_children():
            widget.destroy()

        tk.Label(self, text=f"Commandes pour {self.current_user}", font=("Arial", 20)).pack(pady=10)

        orders = load_commands()
        user_orders = [order for order in orders if order["marchand"] == self.current_user]

        if not user_orders:
            tk.Label(self, text="Aucune commande en attente.").pack(pady=10)
            tk.Button(self, text="Retour", command=self.show_product_management_screen).pack(pady=10)
            return

        frame_orders = tk.Frame(self)
        frame_orders.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        tree_orders = ttk.Treeview(frame_orders, columns=["Produit", "Quantité", "Statut"], show="headings")
        tree_orders.heading("Produit", text="Produit")
        tree_orders.heading("Quantité", text="Quantité")
        tree_orders.heading("Statut", text="Statut")
        tree_orders.pack(fill=tk.BOTH, expand=True)

        for order in user_orders:
            tree_orders.insert("", "end", values=(order["produit"], order["quantite"], order["status"]))

        btn_frame = tk.Frame(self)
        btn_frame.pack(fill=tk.X, padx=10, pady=5)

        tk.Button(btn_frame, text="Valider commande",
                  command=lambda: self.process_order(tree_orders, user_orders, "traitée :) ")).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="Rejeter commande",
                  command=lambda: self.process_order(tree_orders, user_orders, "rejetée :/")).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="Retour", command=self.show_product_management_screen).pack(side=tk.RIGHT, padx=5)

    def process_order(self, tree_orders, user_orders, new_status):
        selected_item = tree_orders.selection()
        if not selected_item:
            messagebox.showwarning("Avertissement", "Veuillez sélectionner une commande à traiter !")
            return

        index = int(tree_orders.index(selected_item[0]))
        selected_order = user_orders[index]

        if new_status == "traitée":
            product = self.products[
                (self.products["User"] == self.current_user) & (self.products["Nom"] == selected_order["produit"])
                ]

            if product.empty:
                messagebox.showerror("Erreur", "Produit introuvable dans votre stock.")
                return

            stock = product.iloc[0]["Stock"]
            if stock < selected_order["quantite"]:
                messagebox.showerror("Erreur", "Stock insuffisant pour traiter la commande.")
                return

            self.products.loc[
                (self.products["User"] == self.current_user) & (
                            self.products["Nom"] == selected_order["produit"]), "Stock"
            ] -= selected_order["quantite"]
            save_products(self.products)

        commands = load_commands()
        for command in commands:
            if (
                    command["marchand"] == selected_order["marchand"]
                    and command["produit"] == selected_order["produit"]
                    and command["quantite"] == selected_order["quantite"]
            ):
                command["status"] = new_status
                break

        save_commands(commands)
        self.show_orders()

    def treeview_sort_column(self, col, reverse):
        l = [(self.tree.set(k, col), k) for k in self.tree.get_children('')]
        if col in ["Prix", "Stock"]:
            l.sort(key=lambda x: float(x[0]), reverse=reverse)
        else:
            l.sort(reverse=reverse)
        for index, (_, k) in enumerate(l):
            self.tree.move(k, '', index)
        for column in self.tree["columns"]:
            self.tree.heading(column, text=column)
        if reverse:
            self.tree.heading(col, text=f"{col} ▼")
        else:
            self.tree.heading(col, text=f"{col} ▲")

        self.tree.heading(col, command=lambda: self.treeview_sort_column(col, not reverse))

if __name__ == "__main__":
    app = Application()
    app.mainloop()