import tkinter as tk
from tkinter import ttk, messagebox
import psycopg2
import datetime
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter

class RestaurantManagerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Restaurant Manager")
        self.conn = psycopg2.connect(
            database="postgres",
            user="postgres",
            password="password1",
            host="localhost",
            port="5432",
        )
        self.cursor = self.conn.cursor()
        self.root.geometry("800x600")
        self.tab_control = ttk.Notebook(self.root)
        self.create_menu_tab()
        self.create_orders_tab()
        self.create_reservations_tab()
        self.create_employees_tab()
        self.create_ratings_tab()
        self.tab_control.pack(expand=1, fill="both")

    def create_menu_tab(self):
        menu_tab = ttk.Frame(self.tab_control)
        menu_tab.columnconfigure(0, weight=1)
        menu_tab.columnconfigure(1, weight=1)
        self.tab_control.add(menu_tab, text="Menu")
        menu_tree = ttk.Treeview(menu_tab, columns=("ID", "Name", "Description", "Price"))
        menu_tree.heading("#0", text="Category")
        menu_tree.heading("ID", text="Menu Item ID")
        menu_tree.heading("Name", text="Name")
        menu_tree.heading("Description", text="Description")
        menu_tree.heading("Price", text="Price")
        predefined_categories = ["Appetizer", "Entree", "Drink", "Dessert"]
        for col in menu_tree['columns']:
            menu_tree.heading(col, text=col, anchor=tk.W)
            menu_tree.column(col, width=140)   
        menu_tree.grid(row=0, column=0, columnspan=2, padx=10, pady=10)
        menu_item_id_label = ttk.Label(menu_tab, text="Menu ID:")
        menu_item_id_entry = ttk.Entry(menu_tab)
        menu_item_id_label.grid(row=1, column=0, pady=5, padx=5, sticky="E")
        menu_item_id_entry.grid(row=1, column=1, pady=5, padx=5, sticky="W")
        item_name_label = ttk.Label(menu_tab, text="Item Name:")
        item_name_entry = ttk.Entry(menu_tab)
        item_name_label.grid(row=2, column=0, pady=5, padx=5, sticky="E")
        item_name_entry.grid(row=2, column=1, pady=5, padx=5, sticky="W")
        description_label = ttk.Label(menu_tab, text="Description:")
        description_entry = ttk.Entry(menu_tab)
        description_label.grid(row=3, column=0, pady=5, padx=5, sticky="E")
        description_entry.grid(row=3, column=1, pady=5, padx=5, sticky="W")
        category_label = ttk.Label(menu_tab, text="Category:")
        category_entry = ttk.Entry(menu_tab)
        category_label.grid(row=4, column=0, pady=5, padx=5, sticky="E")
        category_entry.grid(row=4, column=1, pady=5, padx=5, sticky="W")
        price_label = ttk.Label(menu_tab, text="Price:")
        price_entry = ttk.Entry(menu_tab)
        price_label.grid(row=5, column=0, pady=5, padx=5, sticky="E")
        price_entry.grid(row=5, column=1, pady=5, padx=5, sticky="W")
        add_button = ttk.Button(menu_tab, text="Add Menu Item", command=lambda: self.add_menu_item(
            menu_tree,
            predefined_categories,
            menu_item_id_entry.get(),
            item_name_entry.get(),
            description_entry.get(),
            category_entry.get(),
            float(price_entry.get())
            ))
        add_button.grid(row=6, column=0, columnspan=2, pady=5)
        update_button = ttk.Button(menu_tab, text="Update Menu Item", command=lambda: self.update_menu_item(
            menu_tree, predefined_categories, menu_item_id_entry, item_name_entry, description_entry, category_entry, price_entry))
        update_button.grid(row=7, column=0, columnspan=2, pady=5) 
        remove_button = ttk.Button(menu_tab, text="Remove Menu Item", command=lambda: self.remove_menu_item(menu_tree))
        remove_button.grid(row=8, column=0, columnspan=2, pady=5)
        menu_tree.bind("<ButtonRelease-1>", lambda event, menu_tree=menu_tree,
                        menu_item_id_entry=menu_item_id_entry,
                        item_name_entry=item_name_entry,
                        description_entry=description_entry,
                        category_entry=category_entry,
                        price_entry=price_entry:
                        self.edit_menu_item_entry(event, menu_tree, menu_item_id_entry,
                                                   item_name_entry, description_entry,
                                                   category_entry, price_entry))
        menu_tree.bind("<ButtonRelease-3>", lambda event, menu_tree=menu_tree,
                        menu_item_id_entry=menu_item_id_entry,
                        item_name_entry=item_name_entry,
                        description_entry=description_entry,
                        category_entry=category_entry,
                        price_entry=price_entry:
                        self.clear_menu_item_entry_fields(event, menu_tree, menu_item_id_entry,
                                                          item_name_entry, description_entry,
                                                          category_entry, price_entry))
        self.refresh_menu_tree(menu_tree, predefined_categories)
        
    def add_menu_item(self, menu_tree, predefined_categories, menu_item_id, item_name, description, category, price):
        if not all([menu_item_id, item_name, description, category, price]):
            messagebox.showerror("Error", "Please provide values for all fields.")
            return
        if category not in predefined_categories:
            messagebox.showerror("Invalid Category", f"Invalid category. Please choose from: {', '.join(predefined_categories)}")
            return
        query = "INSERT INTO MenuItem (menu_item_id, item_name, description, category, price) VALUES (%s, %s, %s, %s, %s) RETURNING menu_item_id"
        values = (menu_item_id, item_name, description, category, price)
        try:
            self.cursor.execute(query, values)
            new_menu_item_id = self.cursor.fetchone()[0]
            self.conn.commit()
            messagebox.showinfo("Success", f"New menu item added with ID: {new_menu_item_id}")
            predefined_categories = ["Appetizer", "Entree", "Drink", "Dessert"]
            self.refresh_menu_tree(menu_tree, predefined_categories)
        except Exception as e:
            messagebox.showerror("Error", f"Error adding menu item: {e}")
            self.conn.rollback()
            
    def clear_menu_item_entry_fields(self, event, menu_tree, menu_item_id_entry,
                                 item_name_entry, description_entry,
                                 category_entry, price_entry):
        menu_item_id_entry["state"] = "normal"
        menu_item_id_entry.delete(0, tk.END)
        item_name_entry.delete(0, tk.END)
        description_entry.delete(0, tk.END)
        category_entry.delete(0, tk.END)
        price_entry.delete(0, tk.END)
      
    def edit_menu_item_entry(self, event, menu_tree, menu_item_id_entry, item_name_entry, description_entry,
                         category_entry, price_entry):
        item = menu_tree.selection()
        if item:
            if menu_tree.parent(item):
                category = self.get_category_for_item(menu_tree, item)
                item_details = menu_tree.item(item, 'values')
                item_details = item_details[:3] + (category,) + item_details[3:]
                if item_details and len(item_details) >= 5:
                    menu_item_id_entry["state"] = "normal"
                    menu_item_id_entry.delete(0, tk.END)
                    menu_item_id_entry.insert(0, item_details[0]) 
                    item_name_entry.delete(0, tk.END)
                    item_name_entry.insert(0, item_details[1]) 
                    description_entry.delete(0, tk.END)
                    description_entry.insert(0, item_details[2]) 
                    category_entry.delete(0, tk.END)
                    category_entry.insert(0, category) 
                    price_entry.delete(0, tk.END)
                    price_entry.insert(0, item_details[4])  
                    menu_item_id_entry["state"] = "readonly"
            
    def get_category_for_item(self, menu_tree, selected_item):
        if not menu_tree.parent(selected_item):
            corrected_category = menu_tree.item(selected_item, 'text')[:len(menu_tree.item(selected_item, 'text')) - 1]
            return corrected_category
        else:
            parent_item = menu_tree.parent(selected_item)
            corrected_category = menu_tree.item(parent_item, 'text')[:len(menu_tree.item(parent_item, 'text')) - 1]
            return corrected_category
    
    def update_menu_item(self, menu_tree, predefined_categories, menu_item_id_entry, item_name_entry, description_entry, category_entry, price_entry):
        item = menu_tree.selection()
        if item:
            updated_menu_item_id = menu_item_id_entry.get()
            updated_item_name = item_name_entry.get()
            updated_description = description_entry.get()
            updated_category = category_entry.get()
            updated_price = float(price_entry.get())
            if updated_category not in predefined_categories:
                messagebox.showerror("Invalid Category", f"Invalid category. Please choose from: {', '.join(predefined_categories)}")
                return
            query = "UPDATE MenuItem SET item_name=%s, description=%s, category=%s, price=%s WHERE menu_item_id=%s"
            values = (updated_item_name, updated_description, updated_category, updated_price, updated_menu_item_id)
            try:
                self.cursor.execute(query, values)
                self.conn.commit()
                messagebox.showinfo("Success", f"Menu item updated with ID: {updated_menu_item_id}")
            except Exception as e:
                messagebox.showerror("Error", f"Error updating menu item: {e}")
            self.refresh_menu_tree(menu_tree, predefined_categories)

    def remove_menu_item(self, menu_tree):
        item = menu_tree.selection()
        if item:
            if not menu_tree.parent(item):
                return
            menu_item_id = int(menu_tree.item(item, 'values')[0])
            query = "DELETE FROM MenuItem WHERE menu_item_id = %s"
            try:
                self.cursor.execute(query, (menu_item_id,))
                self.conn.commit()
                messagebox.showinfo("Success", f"Menu item removed with ID: {menu_item_id}")
            except Exception as e:
                messagebox.showerror("Error", f"Error removing menu item: {e}")
                self.conn.rollback()
            predefined_categories = ["Appetizer", "Entree", "Drink", "Dessert"]
            self.refresh_menu_tree(menu_tree, predefined_categories)
            
    def refresh_menu_tree(self, menu_tree, predefined_categories):
        menu_tree.delete(*menu_tree.get_children())
        for category in predefined_categories:
            query = "SELECT * FROM MenuItem WHERE category = %s"
            self.cursor.execute(query, (category,))
            menu_items = self.cursor.fetchall()
            category_item = menu_tree.insert("", "end", text=f"{category}s")
            for item in menu_items:
                formatted_price = "{:.2f}".format(item[4])  # Format the price to two decimal places
                menu_tree.insert(category_item, "end", values=(item[0], item[1], item[2], formatted_price))

    def create_orders_tab(self):
        orders_tab = ttk.Frame(self.tab_control)
        orders_tab.columnconfigure(0, weight=1)
        orders_tab.columnconfigure(1, weight=1)
        self.tab_control.add(orders_tab, text="Orders")
        order_tree = ttk.Treeview(orders_tab, columns=("Customer ID", "Date", "Order Type", "Total Amount", "Chef ID", "Waiter ID"))
        order_tree.heading("#0", text="Order ID")
        order_tree.heading("Customer ID", text="Customer ID")
        order_tree.heading("Date", text="Date")
        order_tree.heading("Order Type", text="Order Type")
        order_tree.heading("Total Amount", text="Total Amount")
        order_tree.heading("Chef ID", text="Chef ID")
        order_tree.heading("Waiter ID", text="Waiter ID")
        order_tree.grid(row=0, column=0, columnspan=2, padx=10, pady=10)
        for col in order_tree['columns']:
            order_tree.heading(col, text=col, anchor=tk.W)
            order_tree.column(col, width=95)
        sort_options = ['Date', 'Chef', 'Waiter', 'Customer', 'Order Type']
        sort_combobox = ttk.Combobox(orders_tab, values=sort_options, state='readonly')
        sort_combobox.grid(row=1, column=0, padx=10, pady=5, sticky="W")
        sort_combobox.set('Select a column to sort')
        sort_combobox.bind("<<ComboboxSelected>>", lambda event: self.sort_orders(order_tree, sort_combobox.get()))
        print_button = ttk.Button(orders_tab, text="Print Orders", command=lambda: self.generate_order_report(order_tree))
        print_button.grid(row=1, column=1, padx=10, pady=5, sticky="E")
        order_id_label = ttk.Label(orders_tab, text="Order ID:")
        order_id_label.grid(row=2, column=0, sticky="E", padx=5, pady=5)
        order_id_entry = ttk.Entry(orders_tab)
        order_id_entry.grid(row=2, column=1, sticky="W", padx=5, pady=5)
        customer_id_label = ttk.Label(orders_tab, text="Customer ID:")
        customer_id_label.grid(row=3, column=0, sticky="E", padx=5, pady=5)
        customer_id_entry = ttk.Entry(orders_tab)
        customer_id_entry.grid(row=3, column=1, sticky="W", padx=5, pady=5)
        order_datetime_label = ttk.Label(orders_tab, text="Date:")
        order_datetime_label.grid(row=4, column=0, sticky="E", padx=5, pady=5)
        order_datetime_entry = ttk.Entry(orders_tab)
        order_datetime_entry.grid(row=4, column=1, sticky="W", padx=5, pady=5)
        order_type_label = ttk.Label(orders_tab, text="Order Type:")
        order_type_label.grid(row=5, column=0, sticky="E", padx=5, pady=5)
        order_type_entry = ttk.Entry(orders_tab)
        order_type_entry.grid(row=5, column=1, sticky="W", padx=5, pady=5)
        total_amount_label = ttk.Label(orders_tab, text="Total Amount:")
        total_amount_label.grid(row=6, column=0, sticky="E", padx=5, pady=5)
        total_amount_entry = ttk.Entry(orders_tab)
        total_amount_entry.grid(row=6, column=1, sticky="W", padx=5, pady=5)
        chef_employee_id_label = ttk.Label(orders_tab, text="Chef Employee ID:")
        chef_employee_id_label.grid(row=7, column=0, sticky="E", padx=5, pady=5)
        chef_employee_id_entry = ttk.Entry(orders_tab)
        chef_employee_id_entry.grid(row=7, column=1, sticky="W", padx=5, pady=5)
        waiter_employee_id_label = ttk.Label(orders_tab, text="Waiter Employee ID:")
        waiter_employee_id_label.grid(row=8, column=0, sticky="E", padx=5, pady=5)
        waiter_employee_id_entry = ttk.Entry(orders_tab)
        waiter_employee_id_entry.grid(row=8, column=1, sticky="W", padx=5, pady=5)
        add_order_button = ttk.Button(orders_tab, text="Add Order", command=lambda: self.add_order(
            order_tree,
            order_id_entry.get(),
            customer_id_entry.get(),
            order_datetime_entry.get(),
            order_type_entry.get(),
            total_amount_entry.get(),
            chef_employee_id_entry.get(),  
            waiter_employee_id_entry.get() 
        ))
        add_order_button.grid(row=9, column=0, columnspan=2, pady=5)
        delete_order_button = ttk.Button(orders_tab, text="Delete Order", command=lambda: self.delete_order(
            order_tree,
            order_id_entry.get()
        ))
        delete_order_button.grid(row=10, column=0, columnspan=2, pady=5)
        order_tree.bind("<ButtonRelease-1>", lambda event, order_tree=order_tree,
                        order_id_entry=order_id_entry,
                        customer_id_entry=customer_id_entry,
                        order_datetime_entry=order_datetime_entry,
                        order_type_entry=order_type_entry,
                        total_amount_entry=total_amount_entry:
                        self.view_order_entry(event, order_tree,
                                              order_id_entry, customer_id_entry,
                                              order_datetime_entry, order_type_entry,
                                              total_amount_entry, chef_employee_id_entry, 
                                              waiter_employee_id_entry))

        order_tree.bind("<ButtonRelease-3>", lambda event, order_tree=order_tree,
                        order_id_entry=order_id_entry,
                        customer_id_entry=customer_id_entry,
                        order_datetime_entry=order_datetime_entry,
                        order_type_entry=order_type_entry,
                        total_amount_entry=total_amount_entry,
                        chef_employee_id_entry=chef_employee_id_entry,  # Add this
                        waiter_employee_id_entry=waiter_employee_id_entry:  # And this
                        self.clear_order_entry_fields(event, order_tree,
                                              order_id_entry, customer_id_entry,
                                              order_datetime_entry, order_type_entry,
                                              total_amount_entry, chef_employee_id_entry,
                                              waiter_employee_id_entry))
        
        self.refresh_order_tree(order_tree)
    
    def add_order(self, order_tree, order_id, customer_id, order_datetime, order_type, total_amount, chef_employee_id, waiter_employee_id):
        query = "INSERT INTO Orders (order_id, customer_id, order_datetime, order_type, total_amount, chef_employee_id, waiter_employee_id) VALUES (%s, %s, %s, %s, %s, %s, %s)"
        values = (order_id, customer_id, order_datetime, order_type, total_amount, chef_employee_id, waiter_employee_id)
        try:
            self.cursor.execute(query, values)
            self.conn.commit()
            messagebox.showinfo("Success", f"New order added with ID: {order_id}")
            self.refresh_order_tree(order_tree)
        except Exception as e:
            messagebox.showerror("Error", f"Error adding order: {e}")
            self.conn.rollback()
       
    def view_order_entry(self, event, order_tree, order_id_entry, customer_id_entry, order_datetime_entry, order_type_entry, total_amount_entry, chef_employee_id_entry, waiter_employee_id_entry):
        selected_order = order_tree.selection()
        if selected_order:
            order_id_entry["state"] = "normal"
            customer_id_entry["state"] = "normal"
            order_datetime_entry["state"] = "normal"
            order_type_entry["state"] = "normal"
            total_amount_entry["state"] = "normal"
            chef_employee_id_entry["state"] = "normal"
            waiter_employee_id_entry["state"] = "normal"
            item_text = order_tree.item(selected_order, 'text')
            item_details = order_tree.item(selected_order, 'values')
            order_id_entry.delete(0, tk.END)
            order_id_entry.insert(0, int(item_text))
            customer_id_entry.delete(0, tk.END)
            customer_id_entry.insert(0, item_details[0])
            order_datetime_entry.delete(0, tk.END)
            order_datetime_entry.insert(0, item_details[1])
            order_type_entry.delete(0, tk.END)
            order_type_entry.insert(0, item_details[2])
            total_amount_entry.delete(0, tk.END)
            total_amount_entry.insert(0, item_details[3])
            chef_employee_id_entry.delete(0, tk.END)
            chef_employee_id_entry.insert(0, item_details[4])
            waiter_employee_id_entry.delete(0, tk.END)
            waiter_employee_id_entry.insert(0, item_details[5])
            order_id_entry["state"] = "readonly"
            customer_id_entry["state"] = "readonly"
            order_datetime_entry["state"] = "readonly"
            order_type_entry["state"] = "readonly"
            total_amount_entry["state"] = "readonly"
            chef_employee_id_entry["state"] = "readonly"
            waiter_employee_id_entry["state"] = "readonly"
        else:
            print("No order selected in the order tree")

    def clear_order_entry_fields(self, event, order_tree, order_id_entry, customer_id_entry, order_datetime_entry, order_type_entry, total_amount_entry, chef_employee_id_entry, waiter_employee_id_entry):
        selected_order = order_tree.selection()
        if selected_order:
            order_id_entry["state"] = "normal"
            customer_id_entry["state"] = "normal"
            order_datetime_entry["state"] = "normal"
            order_type_entry["state"] = "normal"
            total_amount_entry["state"] = "normal"
            chef_employee_id_entry["state"] = "normal"
            waiter_employee_id_entry["state"] = "normal"
            order_id_entry.delete(0, tk.END)
            customer_id_entry.delete(0, tk.END)
            order_datetime_entry.delete(0, tk.END)
            order_type_entry.delete(0, tk.END)
            total_amount_entry.delete(0, tk.END)
            chef_employee_id_entry.delete(0, tk.END)
            waiter_employee_id_entry.delete(0, tk.END)
    
    def delete_order(self, order_tree, order_id):
        if order_id:
            order_id = int(order_id)
            query = "DELETE FROM Orders WHERE order_id = %s"
            try:
                self.cursor.execute(query, (order_id,))
                self.conn.commit()
                messagebox.showinfo("Success", f"Order ID {order_id} deleted.")
            except Exception as e:
                messagebox.showerror("Error", f"Error deleting order: {e}")
                self.conn.rollback()
        self.refresh_order_tree(order_tree)
        
    def sort_orders(self, order_tree, sort_by):
        column_mapping = {
            'Date': 'order_datetime',
            'Chef': 'chef_employee_id',
            'Waiter': 'waiter_employee_id',
            'Customer': 'customer_id',
            'Order Type': 'order_type'
        }
        sort_column = column_mapping.get(sort_by)
        if not sort_column:
            return
        try:
            order_tree.delete(*order_tree.get_children())
            query = f"SELECT * FROM Orders ORDER BY {sort_column} ASC, order_datetime DESC"
            self.cursor.execute(query)
            sorted_orders = self.cursor.fetchall()
            for order in sorted_orders:
                order_list = list(order)
                order_list[4] = "{:.2f}".format(order_list[4])  # Format the total price
                order_tree.insert("", "end", text=str(order_list[0]), values=order_list[1:])
        except Exception as e:
            messagebox.showerror("Error", f"Error sorting orders: {e}")
            self.conn.rollback()

    def generate_order_report(self, order_tree):
        orders = []
        for item_id in order_tree.get_children():
            order_id = order_tree.item(item_id, 'text')
            item_values = list(order_tree.item(item_id, 'values'))
            orders.append([order_id] + item_values)
        current_time = datetime.datetime.now()
        formatted_time = current_time.strftime("Report_%m%d%Y-%H%M%S")
        pdf_filename = f"{formatted_time}.pdf"
        pdf = canvas.Canvas(pdf_filename, pagesize=letter)
        pdf.setTitle("Order Report")
        headers = ["Order ID", "Customer ID", "Date", "Order Type", "Total Amount", "Chef ID", "Waiter ID"]
        y_coordinate = 750
        pdf.setFont("Helvetica-Bold", 12)
        column_widths = [80, 80, 100, 80, 100, 80, 80]
        total_width = sum(column_widths)
        starting_x_coordinate = (letter[0] - total_width) / 2  # Center the content on the page
        for i, header in enumerate(headers):
            pdf.drawCentredString(starting_x_coordinate + sum(column_widths[:i]) + column_widths[i] / 2, y_coordinate, header)
        pdf.setFont("Helvetica", 8)
        y_coordinate -= 20
        for order in orders:
            x_coordinate = starting_x_coordinate
            for i, detail in enumerate(order):
                pdf.drawCentredString(x_coordinate + sum(column_widths[:i]) + column_widths[i] / 2, y_coordinate, str(detail))
            y_coordinate -= 15
            if y_coordinate < 50:
                pdf.showPage()
                y_coordinate = 750
        pdf.save()
        messagebox.showinfo("Success", f"Order report saved to {pdf_filename}")

    def refresh_order_tree(self, order_tree):
        order_tree.delete(*order_tree.get_children())
        query = "SELECT * FROM Orders"
        self.cursor.execute(query)
        orders = self.cursor.fetchall()
        for order in orders:
            formatted_order = list(order)
            formatted_order[4] = "{:.2f}".format(formatted_order[4])
            order_tree.insert("", "end", text=str(formatted_order[0]), values=formatted_order[1:])

    def create_reservations_tab(self):
        reservations_tab = ttk.Frame(self.tab_control)
        reservations_tab.columnconfigure(0, weight=1)
        reservations_tab.columnconfigure(1, weight=1)
        self.tab_control.add(reservations_tab, text="Reservations")
        reservation_tree = ttk.Treeview(reservations_tab, columns=("Customer ID", "Datetime", "Table Number"))
        reservation_tree.heading("#0", text="Reservation ID")
        reservation_tree.heading("Customer ID", text="Customer ID")
        reservation_tree.heading("Datetime", text="Datetime")
        reservation_tree.heading("Table Number", text="Table Number")
        for col in reservation_tree['columns']:
            reservation_tree.heading(col, text=col, anchor=tk.W)
            reservation_tree.column(col, width=190)
        reservation_tree.grid(row=0, column=0, columnspan=2, padx=10, pady=10)
        reservation_id_label = ttk.Label(reservations_tab, text="Reservation ID:")
        reservation_id_entry = ttk.Entry(reservations_tab)
        reservation_id_label.grid(row=1, column=0, pady=5, padx=5, sticky="E")
        reservation_id_entry.grid(row=1, column=1, pady=5, padx=5, sticky="W")
        customer_id_label = ttk.Label(reservations_tab, text="Customer ID:")
        customer_id_entry = ttk.Entry(reservations_tab)
        customer_id_label.grid(row=2, column=0, pady=5, padx=5, sticky="E")
        customer_id_entry.grid(row=2, column=1, pady=5, padx=5, sticky="W")
        reservation_datetime_label = ttk.Label(reservations_tab, text="Reservation Datetime:")
        reservation_datetime_entry = ttk.Entry(reservations_tab)
        reservation_datetime_label.grid(row=3, column=0, pady=5, padx=5, sticky="E")
        reservation_datetime_entry.grid(row=3, column=1, pady=5, padx=5, sticky="W")
        table_num_label = ttk.Label(reservations_tab, text="Table Number:")
        table_num_entry = ttk.Entry(reservations_tab)
        table_num_label.grid(row=4, column=0, pady=5, padx=5, sticky="E")
        table_num_entry.grid(row=4, column=1, pady=5, padx=5, sticky="W")
        add_reservation_button = ttk.Button(reservations_tab, text="Add Reservation", command=lambda: self.make_reservation(
            reservation_tree,
            int(reservation_id_entry.get()),
            int(customer_id_entry.get()),
            reservation_datetime_entry.get(),
            int(table_num_entry.get())
        ))
        add_reservation_button.grid(row=5, column=0, columnspan=2, pady=5)
        update_reservation_button = ttk.Button(reservations_tab, text="Update Reservation", command=lambda: self.update_reservation(
            reservation_tree,
            reservation_id_entry,
            customer_id_entry,
            reservation_datetime_entry,
            table_num_entry
        ))
        update_reservation_button.grid(row=6, column=0, columnspan=2, pady=5)
        delete_reservation_button = ttk.Button(reservations_tab, text="Delete Reservation", command=lambda: self.delete_reservation(
            reservation_tree,
            reservation_tree.item(reservation_tree.selection(), 'text')
        ))
        delete_reservation_button.grid(row=7, column=0, columnspan=2, pady=5)
        self.refresh_reservation_tree(reservation_tree)
        reservation_tree.bind("<ButtonRelease-1>", lambda event, reservation_tree=reservation_tree,
                            reservation_id_entry=reservation_id_entry,
                            customer_id_entry=customer_id_entry,
                            reservation_datetime_entry=reservation_datetime_entry,
                            table_num_entry=table_num_entry:
                            self.edit_reservation_entry(event, reservation_tree,
                                                       reservation_id_entry, customer_id_entry,
                                                       reservation_datetime_entry, table_num_entry))
        reservation_tree.bind("<ButtonRelease-3>", lambda event, reservation_tree=reservation_tree,
                            reservation_id_entry=reservation_id_entry,
                            customer_id_entry=customer_id_entry,
                            reservation_datetime_entry=reservation_datetime_entry,
                            table_num_entry=table_num_entry:
                            self.clear_reservation_entry_fields(event, reservation_tree,
                                                               reservation_id_entry, customer_id_entry,
                                                               reservation_datetime_entry, table_num_entry))



    def make_reservation(self, reservation_tree, reservation_id, customer_id, reservation_datetime, table_num):
        query = f"""
        DO $$ 
        BEGIN
            INSERT INTO reservation (reservation_id, customer_id, reservation_datetime, table_num)
            VALUES ({reservation_id}, {customer_id}, '{reservation_datetime}'::TIMESTAMP, {table_num});
            IF '{reservation_datetime}'::TIMESTAMP < NOW() OR (SELECT COUNT(*) FROM reservation WHERE table_num = {table_num}) >= 20 THEN
                RAISE EXCEPTION 'Invalid reservation conditions';
            END IF;
        END $$;
        """
        try:
            self.cursor.execute(query)
            self.conn.commit()
            messagebox.showinfo("Success", f"New reservation added with ID: {reservation_id}")
            self.refresh_reservation_tree(reservation_tree)
        except Exception as e:
            messagebox.showerror("Error", f"Error adding reservation: {e}")
            print(f"Error adding reservation: {e}")
            self.conn.rollback()

    def update_reservation(self, reservation_tree, reservation_id_entry, customer_id_entry, reservation_datetime_entry, table_num_entry):
        selected_reservation = reservation_tree.selection()
        if selected_reservation:
            updated_reservation_id = reservation_id_entry.get()
            updated_customer_id = customer_id_entry.get()
            updated_reservation_datetime = reservation_datetime_entry.get()
            updated_table_num = table_num_entry.get()
            query = "UPDATE Reservation SET customer_id=%s, reservation_datetime=%s, table_num=%s WHERE reservation_id=%s"
            values = (updated_customer_id, updated_reservation_datetime, updated_table_num, updated_reservation_id)
            try:
                self.cursor.execute(query, values)
                self.conn.commit()
                messagebox.showinfo("Success", f"Reservation updated with ID: {updated_reservation_id}")
            except Exception as e:
                messagebox.showerror("Error", f"Error updating reservation: {e}")
                self.conn.rollback()
            self.refresh_reservation_tree(reservation_tree)
    
    def edit_reservation_entry(self, event, reservation_tree, reservation_id_entry,
                            customer_id_entry, reservation_datetime_entry,
                            table_num_entry):
        selected_reservation = reservation_tree.selection()
        if selected_reservation:
            item_text = reservation_tree.item(selected_reservation, 'text')
            item_details = reservation_tree.item(selected_reservation, 'values')
            reservation_id_entry.delete(0, tk.END)
            reservation_id_entry.insert(0, int(item_text)) 
            customer_id_entry.delete(0, tk.END)
            customer_id_entry.insert(0, item_details[0])  
            reservation_datetime_entry.delete(0, tk.END)
            reservation_datetime_entry.insert(0, item_details[1])  
            table_num_entry.delete(0, tk.END)
            table_num_entry.insert(0, item_details[2])  
            reservation_id_entry["state"] = "readonly"
 
    def clear_reservation_entry_fields(self, event, reservation_tree, reservation_id_entry,
                                   customer_id_entry, reservation_datetime_entry,
                                   table_num_entry):
        selected_reservation = reservation_tree.selection()
        if selected_reservation:
            reservation_id_entry["state"] = "normal"
            reservation_id_entry.delete(0, tk.END)
            customer_id_entry.delete(0, tk.END)
            reservation_datetime_entry.delete(0, tk.END)
            table_num_entry.delete(0, tk.END)

    def delete_reservation(self, reservation_tree, reservation_id):
        if reservation_id:
            reservation_id = int(reservation_id)
            query = "DELETE FROM Reservation WHERE reservation_id = %s"
            try:
                self.cursor.execute(query, (reservation_id,))
                self.conn.commit()
                messagebox.showinfo("Success", f"Reservation ID {reservation_id} deleted.")
            except Exception as e:
                messagebox.showerror("Error", f"Error deleting reservation: {e}")
                self.conn.rollback()
        self.refresh_reservation_tree(reservation_tree)
        
    def refresh_reservation_tree(self, reservation_tree):
        reservation_tree.delete(*reservation_tree.get_children())
        query = "SELECT reservation_id, customer_id, reservation_datetime, table_num FROM Reservation"
        self.cursor.execute(query)
        reservations = self.cursor.fetchall()
        for reservation in reservations:
            reservation_str = tuple(str(value) for value in reservation)
            reservation_tree.insert("", "end", text=str(reservation[0]), values=reservation_str[1:])

    def create_employees_tab(self):
        employees_tab = ttk.Frame(self.tab_control)
        employees_tab.columnconfigure(0, weight=1)
        employees_tab.columnconfigure(1, weight=1)
        self.tab_control.add(employees_tab, text="Employees")
        employee_tree = ttk.Treeview(employees_tab, columns=("First Name", "Last Name", "Role", "Department"))
        employee_tree.heading("#0", text="Employee ID")
        employee_tree.heading("First Name", text="First Name")
        employee_tree.heading("Last Name", text="Last Name")
        employee_tree.heading("Role", text="Role")
        employee_tree.heading("Department", text="Department")
        for col in employee_tree['columns']:
            employee_tree.heading(col, text=col, anchor=tk.W)
            employee_tree.column(col, width=140)
        employee_tree.grid(row=0, column=0, columnspan=2, padx=10, pady=10)
        employee_id_label = ttk.Label(employees_tab, text="Employee ID:")
        employee_id_entry = ttk.Entry(employees_tab)
        employee_id_label.grid(row=1, column=0, padx=5, pady=5, sticky="E")
        employee_id_entry.grid(row=1, column=1, padx=5, pady=5, sticky="W")
        first_name_label = ttk.Label(employees_tab, text="First Name:")
        first_name_entry = ttk.Entry(employees_tab)
        first_name_label.grid(row=2, column=0, padx=5, pady=5, sticky="E")
        first_name_entry.grid(row=2, column=1, padx=5, pady=5, sticky="W")
        last_name_label = ttk.Label(employees_tab, text="Last Name:")
        last_name_entry = ttk.Entry(employees_tab)
        last_name_label.grid(row=3, column=0, padx=5, pady=5, sticky="E")
        last_name_entry.grid(row=3, column=1, padx=5, pady=5, sticky="W")
        role_label = ttk.Label(employees_tab, text="Role:")
        role_entry = ttk.Entry(employees_tab)
        role_label.grid(row=4, column=0, padx=5, pady=5, sticky="E")
        role_entry.grid(row=4, column=1, padx=5, pady=5, sticky="W")
        department_label = ttk.Label(employees_tab, text="Department:")
        department_entry = ttk.Entry(employees_tab)
        department_label.grid(row=5, column=0, padx=5, pady=5, sticky="E")
        department_entry.grid(row=5, column=1, padx=5, pady=5, sticky="W")
        add_employee_button = ttk.Button(employees_tab, text="Add Employee", command=lambda: self.make_employee(
            employee_tree,
            employee_id_entry.get(),
            first_name_entry.get(),
            last_name_entry.get(),
            role_entry.get(),
            department_entry.get()
        ))
        add_employee_button.grid(row=6, column=0, columnspan=2, pady=5)
        update_employee_button = ttk.Button(employees_tab, text="Update Employee", command=lambda: self.update_employee(
            employee_tree,
            employee_id_entry,
            first_name_entry,
            last_name_entry,
            role_entry,
            department_entry
        ))
        update_employee_button.grid(row=7, column=0, columnspan=2, pady=5)
        delete_employee_button = ttk.Button(employees_tab, text="Delete Employee", command=lambda: self.delete_employee(
            employee_tree,
            employee_id_entry.get()
        ))
        delete_employee_button.grid(row=8, column=0, columnspan=2, pady=5)
        self.refresh_employee_tree(employee_tree)
        employee_tree.bind("<ButtonRelease-1>", lambda event: self.edit_employee_entry(
            event, employee_tree, employee_id_entry, first_name_entry, last_name_entry, role_entry, department_entry
        ))
        employee_tree.bind("<ButtonRelease-3>", lambda event: self.clear_employee_entry_fields(
            event, employee_id_entry, first_name_entry, last_name_entry, role_entry, department_entry
        ))
    
    # Modify the existing functions to include employee_id
    def add_employee(self, employee_tree, employee_id, first_name, last_name, role, department):
        query = "INSERT INTO Employee (employee_id, fName, lName, role, dept_name) VALUES (%s, %s, %s, %s, %s)"
        values = (employee_id, first_name, last_name, role, department)
        try:
            self.cursor.execute(query, values)
            self.conn.commit()
            messagebox.showinfo("Success", f"New employee added with ID: {employee_id}")
            self.refresh_employee_tree(employee_tree)
        except Exception as e:
            messagebox.showerror("Error", f"Error adding employee: {e}")
            self.conn.rollback()

    def update_employee(self, employee_tree, employee_id_entry, first_name_entry, last_name_entry, role_entry, department_entry):
        updated_employee_id = employee_id_entry.get()
        updated_first_name = first_name_entry.get()
        updated_last_name = last_name_entry.get()
        updated_role = role_entry.get()
        updated_department = department_entry.get()
        query = "UPDATE Employee SET fName=%s, lName=%s, role=%s, dept_name=%s WHERE employee_id=%s"
        values = (updated_first_name, updated_last_name, updated_role, updated_department, updated_employee_id) 
        try:
            self.cursor.execute(query, values)
            self.conn.commit()
            messagebox.showinfo("Success", f"Employee updated with ID: {updated_employee_id}")
            self.refresh_employee_tree(employee_tree)
        except Exception as e:
            messagebox.showerror("Error", f"Error updating employee: {e}")
            self.conn.rollback()

    def edit_employee_entry(self, event, employee_tree, employee_id_entry, first_name_entry, last_name_entry, role_entry, department_entry):
        selected_employee = employee_tree.selection()
        if selected_employee:
            employee_id = employee_tree.item(selected_employee, 'text')
            employee_details = employee_tree.item(selected_employee, 'values')
            employee_id_entry["state"] = "normal"
            employee_id_entry.delete(0, tk.END)
            first_name_entry.delete(0, tk.END)
            last_name_entry.delete(0, tk.END)
            role_entry.delete(0, tk.END)
            department_entry.delete(0, tk.END)
            employee_id_entry.insert(0, int(employee_id))  
            first_name_entry.insert(0, employee_details[0])
            last_name_entry.insert(0, employee_details[1])
            role_entry.insert(0, employee_details[2])
            department_entry.insert(0, employee_details[3])  
            employee_id_entry["state"]="readonly"
    
    def delete_employee(self, employee_tree, employee_id):
        if employee_id:
            try:
                employee_id = int(employee_id)
                query = "DELETE FROM Employee WHERE employee_id = %s"
                self.cursor.execute(query, (employee_id,))
                self.conn.commit()
                messagebox.showinfo("Success", f"Employee ID {employee_id} deleted.")
                self.refresh_employee_tree(employee_tree)
            except Exception as e:
                messagebox.showerror("Error", f"Error deleting employee: {e}")
                self.conn.rollback()
    
    def clear_employee_entry_fields(self, event, employee_tree, employee_id_entry, first_name_entry, last_name_entry, role_entry, department_entry):
        selected_employee = employee_tree.selection()
        if selected_employee:
            employee_id_entry.delete(0, tk.END)
            first_name_entry.delete(0, tk.END)
            last_name_entry.delete(0, tk.END)
            role_entry.delete(0, tk.END)
            department_entry.delete(0, tk.END)
            employee_id_entry["state"] = "normal"

    def refresh_employee_tree(self, employee_tree):
        employee_tree.delete(*employee_tree.get_children())
        query = "SELECT employee_id, fName, lName, role, dept_name FROM Employee"
        self.cursor.execute(query)
        employees = self.cursor.fetchall()
        for employee in employees:
            employee_tree.insert("", "end", text=str(employee[0]), values=employee[1:])

    def create_ratings_tab(self):
        ratings_tab = ttk.Frame(self.tab_control)
        ratings_tab.columnconfigure(0, weight=1)
        ratings_tab.rowconfigure(0, weight=1)
        self.tab_control.add(ratings_tab, text="Ratings")
        ratings_tree = ttk.Treeview(ratings_tab, columns=("Order ID", "Rating"))
        ratings_tree.heading("#0", text="Rating ID")
        ratings_tree.heading("Order ID", text="Order ID")
        ratings_tree.heading("Rating", text="Rating")
        for col in ratings_tree['columns']:
            ratings_tree.column(col, width=120, anchor=tk.W)
        ratings_tree.grid(row=0, column=0, padx=10, pady=10, sticky='nsew')
        scrollbar = ttk.Scrollbar(ratings_tab, orient="vertical", command=ratings_tree.yview)
        scrollbar.grid(row=0, column=1, sticky='ns')
        ratings_tree.configure(yscrollcommand=scrollbar.set)
        self.refresh_ratings_tree(ratings_tree)


    def refresh_ratings_tree(self, ratings_tree):
        ratings_tree.delete(*ratings_tree.get_children())
        query = "SELECT * FROM Ratings"
        self.cursor.execute(query)
        ratings = self.cursor.fetchall()
        for rating in ratings:
            ratings_tree.insert("", "end", text=rating[0], values=(rating[1], rating[2]))     
                
    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    root = tk.Tk()
    app = RestaurantManagerApp(root)
    app.run()

