import tkinter as tk
from tkinter import messagebox, simpledialog
import mysql.connector
from mysql.connector import errorcode


def connect_to_database(host, user, password, username):
    db_name = f"wedding_db_{username.lower()}"

    try:
        db = mysql.connector.connect(
            host=host,
            user=user,
            password=password,
            database=db_name
        )
        return db
    except mysql.connector.Error as err:
        if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
            messagebox.showerror("Erreur", "Mauvais nom d'utilisateur ou mot de passe")
        elif err.errno == errorcode.ER_BAD_DB_ERROR:
            messagebox.showerror("Erreur", "La base de données n'existe pas")
        else:
            messagebox.showerror("Erreur", f"Erreur de connexion à la base de données: {err}")


class WeddingApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Gestion des invités - Mariage")

        # Boîte de dialogue pour saisir les informations RDS
        self.show_rds_dialog()

    def show_rds_dialog(self):
        self.rds_dialog = tk.Toplevel(self.root)
        self.rds_dialog.title("Informations RDS")

        tk.Label(self.rds_dialog, text="Hôte RDS :").grid(row=0, column=0)
        self.host_entry = tk.Entry(self.rds_dialog)
        self.host_entry.grid(row=0, column=1)

        tk.Label(self.rds_dialog, text="Nom d'utilisateur :").grid(row=1, column=0)
        self.user_entry = tk.Entry(self.rds_dialog)
        self.user_entry.grid(row=1, column=1)

        tk.Label(self.rds_dialog, text="Mot de passe :").grid(row=2, column=0)
        self.password_entry = tk.Entry(self.rds_dialog, show='*')
        self.password_entry.grid(row=2, column=1)

        tk.Label(self.rds_dialog, text="Nom d'utilisateur de l'application :").grid(row=3, column=0)
        self.app_username_entry = tk.Entry(self.rds_dialog)
        self.app_username_entry.grid(row=3, column=1)

        connect_button = tk.Button(self.rds_dialog, text="Se connecter", command=self.connect_to_db)
        connect_button.grid(row=4, column=1)

    def connect_to_db(self):
        host = self.host_entry.get()
        user = self.user_entry.get()
        password = self.password_entry.get()
        app_username = self.app_username_entry.get()

        if not host or not user or not password or not app_username:
            messagebox.showwarning("Champs manquants", "Veuillez remplir tous les champs")
            return

        self.db = connect_to_database(host, user, password, app_username)
        if self.db:
            self.cursor = self.db.cursor()
            self.create_main_interface()
            self.rds_dialog.destroy()  # Ferme la boîte de dialogue une fois connecté
        else:
            messagebox.showerror("Erreur", "Impossible de se connecter à la base de données.")

    def create_main_interface(self):
        for widget in self.root.winfo_children():
            widget.destroy()

        tk.Label(self.root, text="Bienvenue dans la gestion des invités !").pack(pady=10)

        add_guest_button = tk.Button(self.root, text="Ajouter un invité", command=self.open_add_guest_interface)
        add_guest_button.pack(pady=5)

        add_table_button = tk.Button(self.root, text="Ajouter une table", command=self.open_add_table_interface)
        add_table_button.pack(pady=5)

        search_guest_button = tk.Button(self.root, text="Rechercher un invité",
                                        command=self.open_search_guest_interface)
        search_guest_button.pack(pady=5)

    def open_add_guest_interface(self):
        self.add_guest_window = tk.Toplevel(self.root)
        self.add_guest_window.title("Ajouter un invité")

        tk.Label(self.add_guest_window, text="Nom de l'invité :").grid(row=0, column=0)
        self.name_entry = tk.Entry(self.add_guest_window)
        self.name_entry.grid(row=0, column=1)

        tk.Label(self.add_guest_window, text="Catégorie :").grid(row=1, column=0)
        self.category_var = tk.StringVar(self.add_guest_window)
        self.category_var.set("famille")
        category_menu = tk.OptionMenu(self.add_guest_window, self.category_var, "famille", "amis", "collegues",
                                      "autres")
        category_menu.grid(row=1, column=1)

        tk.Label(self.add_guest_window, text="Numéro de table :").grid(row=2, column=0)
        self.table_number_entry = tk.Entry(self.add_guest_window)
        self.table_number_entry.grid(row=2, column=1)

        add_button = tk.Button(self.add_guest_window, text="Ajouter invité", command=self.add_guest)
        add_button.grid(row=3, column=1)

        seats_button = tk.Button(self.add_guest_window, text="Afficher chaises disponibles", command=self.show_seats)
        seats_button.grid(row=4, column=1)

        return_button = tk.Button(self.add_guest_window, text="Retour", command=self.add_guest_window.destroy)
        return_button.grid(row=5, column=1)

    def show_seats(self):
        table_number = self.table_number_entry.get()

        if not table_number:
            messagebox.showwarning("Champ manquant", "Veuillez saisir un numéro de table")
            return

        self.cursor.execute("SELECT seats_available FROM tables WHERE table_number = %s", (table_number,))
        result = self.cursor.fetchone()

        if result:
            total_seats = result[0]
            self.cursor.execute("SELECT COUNT(*) FROM guests WHERE table_number = %s", (table_number,))
            occupied_seats = self.cursor.fetchone()[0]
            remaining_seats = total_seats - occupied_seats
            messagebox.showinfo("Chaises disponibles",
                                f"Total chaises: {total_seats}\nChaises restantes: {remaining_seats}")
        else:
            messagebox.showinfo("Non trouvé", "Table non trouvée")

    def add_guest(self):
        name = self.name_entry.get()
        category = self.category_var.get()
        table_number = self.table_number_entry.get()

        if not name or not table_number:
            messagebox.showwarning("Champ manquant", "Veuillez remplir tous les champs")
            return

        # Vérification si l'invité existe déjà dans n'importe quelle table
        self.cursor.execute("SELECT * FROM guests WHERE name = %s", (name,))
        guest_exists = self.cursor.fetchone()

        if guest_exists:
            messagebox.showerror("Erreur", "Cet invité existe déjà dans la liste des invités.")
            return

        # Vérifier la disponibilité des chaises à la table
        self.cursor.execute("SELECT seats_available FROM tables WHERE table_number = %s", (table_number,))
        result = self.cursor.fetchone()

        if result:
            total_seats = result[0]
            self.cursor.execute("SELECT COUNT(*) FROM guests WHERE table_number = %s", (table_number,))
            occupied_seats = self.cursor.fetchone()[0]
            if occupied_seats >= total_seats:
                messagebox.showwarning("Chaises pleines", "Aucune chaise disponible à cette table")
                return

        try:
            self.cursor.execute("INSERT INTO guests (name, category, table_number) VALUES (%s, %s, %s)",
                                (name, category, table_number))
            self.db.commit()
            messagebox.showinfo("Succès", "Invité ajouté avec succès")
            self.name_entry.delete(0, tk.END)
            self.table_number_entry.delete(0, tk.END)
        except Exception as e:
            messagebox.showerror("Erreur", str(e))

    def open_add_table_interface(self):
        self.add_table_window = tk.Toplevel(self.root)
        self.add_table_window.title("Ajouter une table")

        tk.Label(self.add_table_window, text="Numéro de table :").grid(row=0, column=0)
        self.table_number_table_entry = tk.Entry(self.add_table_window)
        self.table_number_table_entry.grid(row=0, column=1)

        tk.Label(self.add_table_window, text="Nombre de chaises :").grid(row=1, column=0)
        self.seats_available_entry = tk.Entry(self.add_table_window)
        self.seats_available_entry.grid(row=1, column=1)

        add_table_button = tk.Button(self.add_table_window, text="Ajouter table", command=self.add_table)
        add_table_button.grid(row=2, column=1)

        return_button = tk.Button(self.add_table_window, text="Retour", command=self.add_table_window.destroy)
        return_button.grid(row=3, column=1)

    def add_table(self):
        table_number = self.table_number_table_entry.get()
        seats_available = self.seats_available_entry.get()

        if not table_number or not seats_available:
            messagebox.showwarning("Champ manquant", "Veuillez remplir tous les champs")
            return

        try:
            self.cursor.execute("INSERT INTO tables (table_number, seats_available) VALUES (%s, %s)",
                                (table_number, seats_available))
            self.db.commit()
            messagebox.showinfo("Succès", "Table ajoutée avec succès")
            self.table_number_table_entry.delete(0, tk.END)
            self.seats_available_entry.delete(0, tk.END)
        except Exception as e:
            messagebox.showerror("Erreur", str(e))

    def open_search_guest_interface(self):
        self.search_guest_window = tk.Toplevel(self.root)
        self.search_guest_window.title("Rechercher un invité")

        tk.Label(self.search_guest_window, text="Nom de l'invité :").grid(row=0, column=0)
        self.search_name_entry = tk.Entry(self.search_guest_window)
        self.search_name_entry.grid(row=0, column=1)

        search_button = tk.Button(self.search_guest_window, text="Rechercher", command=self.search_guest)
        search_button.grid(row=1, column=1)

        return_button = tk.Button(self.search_guest_window, text="Retour", command=self.search_guest_window.destroy)
        return_button.grid(row=2, column=1)

    def search_guest(self):
        name = self.search_name_entry.get()
        if not name:
            messagebox.showwarning("Champ manquant", "Veuillez entrer un nom")
            return

        self.cursor.execute("SELECT * FROM guests WHERE name LIKE %s", (f"%{name}%",))
        results = self.cursor.fetchall()

        if results:
            guests_list = "\n".join([f"{row[1]} - Table {row[3]} ({row[2]})" for row in results])
            messagebox.showinfo("Résultats de la recherche", guests_list)
        else:
            messagebox.showinfo("Résultats de la recherche", "Aucun invité trouvé")


if __name__ == "__main__":
    root = tk.Tk()
    app = WeddingApp(root)
    root.mainloop()
