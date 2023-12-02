import tkinter as tk
from tkinter import ttk
import psycopg2

class RestaurantManagerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Restaurant Manager")

        # Connect to the PostgreSQL database
        self.conn = psycopg2.connect(
            database="postgres",
            user="postgres",
            password="password1",
            host="localhost",
            port="5432",
        )
        self.cursor = self.conn.cursor()

        # Set the initial size of the window
        self.root.geometry("800x600")  # Set your desired width and height

        # Create and set up the main tabbed interface
        self.tab_control = ttk.Notebook(self.root)
        self.create_order_tab()
        self.create_menu_tab()
        self.tab_control.pack(expand=1, fill="both")

    def create_order_tab(self):
        order_tab = ttk.Frame(self.tab_control)
        self.tab_control.add(order_tab, text="Orders")

    def create_menu_tab(self):
        menu_tab = ttk.Frame(self.tab_control)
        self.tab_control.add(menu_tab, text="Menu")
        
        # Entry widgets for adding a new menu item
        menu_item_id_label = ttk.Label(menu_tab, text="Menu ID:")
        menu_item_id_label.grid(row=0, column=0, pady=5, padx=5, sticky="E")
    
        menu_item_id_entry = ttk.Entry(menu_tab)
        menu_item_id_entry.grid(row=0, column=1, pady=5, padx=5, sticky="W")
    
        item_name_label = ttk.Label(menu_tab, text="Item Name:")
        item_name_entry = ttk.Entry(menu_tab)
        item_name_label.grid(row=1, column=0, pady=5, padx=5, sticky="E")
        item_name_entry.grid(row=1, column=1, pady=5, padx=5, sticky="W")
    
        description_label = ttk.Label(menu_tab, text="Description:")
        description_entry = ttk.Entry(menu_tab)
        description_label.grid(row=2, column=0, pady=5, padx=5, sticky="E")
        description_entry.grid(row=2, column=1, pady=5, padx=5, sticky="W")
    
        category_label = ttk.Label(menu_tab, text="Category:")
        category_entry = ttk.Entry(menu_tab)
        category_label.grid(row=3, column=0, pady=5, padx=5, sticky="E")
        category_entry.grid(row=3, column=1, pady=5, padx=5, sticky="W")
    
        price_label = ttk.Label(menu_tab, text="Price:")
        price_entry = ttk.Entry(menu_tab)
        price_label.grid(row=4, column=0, pady=5, padx=5, sticky="E")
        price_entry.grid(row=4, column=1, pady=5, padx=5, sticky="W")
    
        add_button = ttk.Button(menu_tab, text="Add Menu Item", command=lambda: self.add_menu_item(
            int(menu_item_id_entry.get()),  # Assuming menu_item_id is an integer
            item_name_entry.get(),
            description_entry.get(),
            category_entry.get(),
            float(price_entry.get())
        ))
        add_button.grid(row=5, column=0, columnspan=2, pady=10)
    
    
    def add_menu_item(self, menu_item_id, item_name, description, category, price):
        query = "INSERT INTO MenuItem (menu_item_id, item_name, description, category, price) VALUES (%s, %s, %s, %s, %s) RETURNING menu_item_id"
        values = (menu_item_id, item_name, description, category, price)
    
        # Execute the query and fetch the menu_item_id
        self.cursor.execute(query, values)
        new_menu_item_id = self.cursor.fetchone()[0]
        self.conn.commit()
    
        # Print or use the new_menu_item_id as needed
        print(f"New menu item added with ID: {new_menu_item_id}")



    def view_menu(self):
        query = "SELECT * FROM MenuItem"
        self.cursor.execute(query)
        menu_items = self.cursor.fetchall()
        # Display menu_items in the GUI

    def place_order(self, customer_id, order_datetime, order_type, total_amount, chef_employee_id, waiter_employee_id):
        query = "INSERT INTO Orders (customer_id, order_datetime, order_type, total_amount, chef_employee_id, waiter_employee_id) VALUES (%s, %s, %s, %s, %s, %s)"
        values = (customer_id, order_datetime, order_type, total_amount, chef_employee_id, waiter_employee_id)
        self.cursor.execute(query, values)
        self.conn.commit()

    def view_orders(self):
        query = "SELECT * FROM Orders"
        self.cursor.execute(query)
        orders = self.cursor.fetchall()
        # Display orders in the GUI

    def add_employee(self, fName, lName, role, dept_name):
        query = "INSERT INTO Employee (fName, lName, role, dept_name) VALUES (%s, %s, %s, %s)"
        values = (fName, lName, role, dept_name)
        self.cursor.execute(query, values)
        self.conn.commit()

    def view_employees(self):
        query = "SELECT * FROM Employee"
        self.cursor.execute(query)
        employees = self.cursor.fetchall()
        # Display employees in the GUI

    def make_reservation(self, customer_id, reservation_datetime, table_num):
        query = "INSERT INTO Reservation (customer_id, reservation_datetime, table_num) VALUES (%s, %s, %s)"
        values = (customer_id, reservation_datetime, table_num)
        self.cursor.execute(query, values)
        self.conn.commit()

    def view_reservations(self):
        query = "SELECT * FROM Reservation"
        self.cursor.execute(query)
        reservations = self.cursor.fetchall()
        # Display reservations in the GUI

    def add_rating(self, order_id, rating):
        query = "INSERT INTO Ratings (order_id, rating) VALUES (%s, %s)"
        values = (order_id, rating)
        self.cursor.execute(query, values)
        self.conn.commit()

    def view_ratings(self):
        query = "SELECT * FROM Ratings"
        self.cursor.execute(query)
        ratings = self.cursor.fetchall()
        # Display ratings in the GUI

    def run(self):
        self.root.mainloop()

# Example usage
if __name__ == "__main__":
    root = tk.Tk()
    app = RestaurantManagerApp(root)
    app.run()

