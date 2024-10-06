import mysql.connector
from mysql.connector import errorcode
import tkinter as tk
from tkinter import simpledialog, messagebox


def create_database(username, rds_user, rds_password):
    db_name = f"wedding_db_{username.lower()}"  # Utiliser le nom d'utilisateur pour créer le nom de la base
    db_counter = 0  # Démarrer à 0 pour wedding_db_username_0, wedding_db_username_1, etc.

    # Connexion à MySQL sur Amazon RDS (assurez-vous d'utiliser l'endpoint principal)
    connection = mysql.connector.connect(
        host="database-2.cluster-cvgwggwma7dz.eu-north-1.rds.amazonaws.com",  # Endpoint principal de votre RDS
        user=rds_user,  # Utiliser le nom d'utilisateur saisi par l'utilisateur
        password=rds_password  # Utiliser le mot de passe saisi par l'utilisateur
    )
    cursor = connection.cursor()

    while True:
        try:
            # Vérifier si la base de données existe déjà
            cursor.execute("SHOW DATABASES")
            databases = [db[0] for db in cursor.fetchall()]

            # Si le nom de base de données n'existe pas, créez-la
            if db_name not in databases:
                cursor.execute(f"CREATE DATABASE {db_name}")
                connection.commit()
                print(f"Base de données '{db_name}' créée avec succès.")
                return db_name
            else:
                print(f"La base de données '{db_name}' existe déjà. Incrémentation du compteur.")
                db_counter += 1
                db_name = f"wedding_db_{username.lower()}_{db_counter}"

        except mysql.connector.Error as err:
            if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
                print("Erreur : Mauvais nom d'utilisateur ou mot de passe")
                break
            else:
                print(f"Erreur : {err}")
                break

    cursor.close()
    connection.close()


# Fonction pour créer les tables
def create_tables(username, rds_user, rds_password):
    db_name = create_database(username, rds_user, rds_password)  # Obtenez le nom de la base de données
    try:
        db = mysql.connector.connect(
            host="database-2.cluster-cvgwggwma7dz.eu-north-1.rds.amazonaws.com",  # Endpoint principal de votre RDS
            user=rds_user,  # Utiliser le nom d'utilisateur saisi par l'utilisateur
            password=rds_password,  # Utiliser le mot de passe saisi par l'utilisateur
            database=db_name
        )
        cursor = db.cursor()

        # Définition des tables à créer
        TABLES = {
            'guests': """
                CREATE TABLE IF NOT EXISTS guests (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    name VARCHAR(100) NOT NULL,
                    category ENUM('famille', 'amis', 'collegues', 'autres') NOT NULL,
                    table_number INT NOT NULL
                );
            """,
            'tables': """
                CREATE TABLE IF NOT EXISTS tables (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    table_number INT NOT NULL,
                    seats_available INT NOT NULL
                );
            """
        }

        # Création des tables
        for table_name, table_sql in TABLES.items():
            try:
                print(f"Création de la table {table_name}...")
                cursor.execute(table_sql)
                print(f"Table {table_name} créée avec succès !")
            except mysql.connector.Error as err:
                if err.errno == errorcode.ER_TABLE_EXISTS_ERROR:
                    print(f"Erreur : La table {table_name} existe déjà.")
                else:
                    print(err.msg)

        db.commit()

        # Afficher une boîte de dialogue de succès
        show_success_dialog()

    except mysql.connector.Error as err:
        print(f"Erreur de connexion à la base de données: {err}")

    finally:
        if cursor:
            cursor.close()
        if db:
            db.close()


def show_success_dialog():
    # Créer une fenêtre tkinter pour montrer le succès
    root = tk.Tk()
    root.withdraw()  # Cacher la fenêtre principale
    messagebox.showinfo("Succès", "La base de données et les tables ont été créées avec succès !")
    root.destroy()  # Fermer la fenêtre tkinter


def get_rds_credentials():
    # Demander à l'utilisateur de saisir son nom d'utilisateur RDS et mot de passe
    root = tk.Tk()
    root.withdraw()  # Cacher la fenêtre principale
    rds_user = simpledialog.askstring("Nom d'utilisateur RDS", "Entrez votre nom d'utilisateur RDS:")
    rds_password = simpledialog.askstring("Mot de passe RDS", "Entrez votre mot de passe RDS:", show='*')
    root.destroy()  # Fermer la fenêtre tkinter
    return rds_user, rds_password


def get_username():
    # Demander à l'utilisateur de saisir son nom d'utilisateur pour la base de données
    root = tk.Tk()
    root.withdraw()  # Cacher la fenêtre principale
    username = simpledialog.askstring("Nom d'utilisateur", "Entrez votre nom d'utilisateur:")
    root.destroy()  # Fermer la fenêtre tkinter
    return username


if __name__ == "__main__":
    # Récupérer les informations RDS (nom d'utilisateur et mot de passe)
    rds_user, rds_password = get_rds_credentials()

    if rds_user and rds_password:
        # Récupérer le nom d'utilisateur pour la création de la base de données
        username = get_username()

        if username:
            create_tables(username, rds_user, rds_password)
        else:
            print("Nom d'utilisateur non fourni. Abandon de la création de la base de données.")
    else:
        print("Identifiants RDS non fournis. Abandon de la création de la base de données.")
