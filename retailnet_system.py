import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from PIL import Image, ImageTk
import sqlite3
import datetime
import os

class RetailNetSystem:
    def __init__(self, root):
        self.root = root
        self.root.title("RetailNet Smart System")
        self.root.geometry("1200x700")
        self.root.minsize(1000, 600)
        
        # Database setup
        self.db_connection = sqlite3.connect('retailnet.db')
        self.create_tables()
        
        # UI styling
        self.setup_styles()
        
        # Background images
        self.bg_images = {}
        self.load_background_images()
        
        # Current user and sale data
        self.current_user = None
        self.current_sale = []
        self.total_sale_amount = 0.0
        
        # Show login screen first
        self.show_login_screen()
    
    def setup_styles(self):
        style = ttk.Style()
        
        # Configure styles
        style.configure("Title.TLabel", font=('Arial', 24, 'bold'), foreground="white",background="black")
        style.configure("Header.TLabel", font=('Arial', 14, 'bold'), foreground="white",background="black")
        style.configure("Normal.TLabel", font=('Arial', 12),foreground="white",background="black")
        style.configure("Total.TLabel", font=('Arial', 16, 'bold'), foreground="white",background="black")
        style.configure("Clock.TLabel", font=('Arial', 12), foreground="white",background="black")
        
        # Button styles
        #style.theme_use('clam')
        style.configure("Primary.TButton", font=('Arial', 12,"bold"), padding=10,  foreground="black",background="black",border="green")
        style.configure("Secondary.TButton", font=('Arial', 12,"bold"), padding=10,  foreground="black",background="black")
        style.configure("Danger.TButton", font=('Arial', 12,"bold"), padding=10,  foreground="black",background="black")
        
        # Entry styles
        style.configure("TEntry", font=('Arial', 12), padding=5)
        
        # Frame styles
        style.configure("TFrame", background="systemTransparent")
        style.configure("Transparent.TFrame", background="")
        
        # Treeview styles
        style.configure("Treeview", font=('Arial', 11), rowheight=25)
        style.configure("Treeview.Heading", font=('Arial', 12, 'bold'))
        style.map("Treeview", background=[('selected', '#347083')])
    
    def load_background_images(self):
        try:
            # Create images directory if it doesn't exist
            if not os.path.exists('images'):
                os.makedirs('images')
                
            # Try to load images from images directory
            login_bg = Image.open("images/login_bg.jpg").resize((1920, 1080), Image.Resampling.LANCZOS)
            main_bg = Image.open("images/main_bg.jpg").resize((1920, 1080), Image.Resampling.LANCZOS)
            
            self.bg_images = {
                "login": ImageTk.PhotoImage(login_bg),
                "main": ImageTk.PhotoImage(main_bg)
            }
        except Exception as e:
            print(f"Error loading background images: {e}")
            # Fallback if images can't be loaded
            self.bg_images = None
    
    def create_tables(self):
        cursor = self.db_connection.cursor()
        
        # Users table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL
            )
        ''')
        
        # Inventory table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS inventory (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                item_name TEXT UNIQUE NOT NULL,
                price REAL NOT NULL,
                quantity INTEGER NOT NULL,
                last_updated TEXT
            )
        ''')
        
        # Sales table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS sales (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                item_name TEXT NOT NULL,
                quantity INTEGER NOT NULL,
                price REAL NOT NULL,
                total REAL NOT NULL,
                sale_date TEXT NOT NULL,
                sale_time TEXT NOT NULL
            )
        ''')
        
        # Add default admin user if not exists
        cursor.execute("SELECT * FROM users WHERE username='admin'")
        if not cursor.fetchone():
            cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", 
                         ("admin", "admin123"))
        
        self.db_connection.commit()
    
    def update_clock(self):
        """Update the clock label with current date/time"""
        now = datetime.datetime.now()
        current_time = now.strftime("%Y-%m-%d %H:%M:%S")
        if hasattr(self, 'clock_label'):
            self.clock_label.config(text=current_time)
        self.root.after(1000, self.update_clock)  # Update every second
    
    def show_login_screen(self):
        # Clear existing widgets
        for widget in self.root.winfo_children():
            widget.destroy()
        
        # Background
        if self.bg_images:
            bg_label = tk.Label(self.root, image=self.bg_images["login"])
            bg_label.place(x=0, y=0, relwidth=1, relheight=1)
        
        # Login frame
        login_frame = ttk.Frame(self.root, style="Transparent.TFrame")
        login_frame.place(relx=0.5, rely=0.5, anchor="center")
        
        # Title
        ttk.Label(login_frame, text="RetailNet Login Page", style="Title.TLabel").grid(
            row=0, column=0, columnspan=2, pady=(0, 40))
        
        # User ID
        ttk.Label(login_frame, text="USER ID:", style="Header.TLabel").grid(
            row=1, column=0, sticky="e", pady=5)
        self.user_id_entry = ttk.Entry(login_frame, style="TEntry", width=25)
        self.user_id_entry.grid(row=1, column=1, pady=5, padx=10)
        
        # Password
        ttk.Label(login_frame, text="PASSWORD:", style="Header.TLabel").grid(
            row=2, column=0, sticky="e", pady=5)
        self.password_entry = ttk.Entry(login_frame, style="TEntry", show="*", width=25)
        self.password_entry.grid(row=2, column=1, pady=5, padx=10)
        
        # Buttons frame
        buttons_frame = ttk.Frame(login_frame, style="Transparent.TFrame")
        buttons_frame.grid(row=3, column=0, columnspan=2, pady=(20, 0))
        
        # Login button
        login_button = ttk.Button(buttons_frame, text="Login", style="Primary.TButton",
                                command=self.attempt_login)
        login_button.pack(side=tk.LEFT, padx=10)
        
        # Exit button
        exit_button = ttk.Button(buttons_frame, text="Exit", style="Danger.TButton",
                               command=self.root.quit)
        exit_button.pack(side=tk.LEFT, padx=10)
        
        # Bind Enter key to login
        self.password_entry.bind('<Return>', lambda e: self.attempt_login())
        self.user_id_entry.focus()
    
    def attempt_login(self):
        username = self.user_id_entry.get().strip()
        password = self.password_entry.get().strip()
    
    # Validate empty fields
        if not username and not password:
            messagebox.showerror("Login Failed", "Please enter both username and password")
            self.user_id_entry.focus()
            return
        
        if not username:
            messagebox.showerror("Login Failed", "Please enter your username")
            self.user_id_entry.focus()
            return
        
        if not password:
            messagebox.showerror("Login Failed", "Please enter your password")
            self.password_entry.focus()
            return
    
        cursor = self.db_connection.cursor()
    
    # Check username exists first
        cursor.execute("SELECT username FROM users WHERE username=?", (username,))
        if not cursor.fetchone():
            messagebox.showerror("Login Failed", "Username not found")
            self.user_id_entry.focus()
            self.user_id_entry.select_range(0, tk.END)
            return
    
    # Now check password
        cursor.execute("SELECT * FROM users WHERE username=? AND password=?", 
                  (username, password))
        user = cursor.fetchone()
    
        if user:
            self.current_user = username
            self.show_main_menu()
        else:
            messagebox.showerror("Login Failed", "Incorrect password")
            self.password_entry.focus()
            self.password_entry.delete(0, tk.END)
    
    def show_main_menu(self):
        # Clear existing widgets
        for widget in self.root.winfo_children():
            widget.destroy()
            
       
        # Background
        if self.bg_images:
            bg_label = tk.Label(self.root, image=self.bg_images["main"])
            bg_label.place(x=0, y=0, relwidth=1, relheight=1)
        
        # Main frame
        main_frame = ttk.Frame(self.root, style="Transparent.TFrame")
        main_frame.pack(fill=tk.BOTH, expand=True, padx=100, pady=100)
        
        # Title
        ttk.Label(main_frame, text="WELCOME\nRETAILNET SMART SYSTEM", 
                 style="Title.TLabel", justify="center").pack(pady=(0, 1))
        
        # Buttons frame
        buttons_frame = ttk.Frame(main_frame, style="Transparent.TFrame")
        buttons_frame.pack(expand=True)
        
        # Start button
        start_button = ttk.Button(buttons_frame, text="START", style="Primary.TButton",
                                command=self.show_scan_page)
        start_button.grid(row=0, column=0, padx=20, pady=20, ipadx=30, ipady=20)
        
        # Inventory Check button
        inventory_button = ttk.Button(buttons_frame, text="INVENTORY CHECK", 
                                    style="Secondary.TButton",
                                    command=self.show_inventory_options)
        inventory_button.grid(row=0, column=1, padx=20, pady=20, ipadx=30, ipady=20)
        
        # Logout button
        logout_button = ttk.Button(buttons_frame, text="LOGOUT", style="Danger.TButton",
                                 command=self.logout)
        logout_button.grid(row=0, column=2, padx=20, pady=20, ipadx=30, ipady=20)
    
    def show_scan_page(self):
        # Clear existing widgets
        for widget in self.root.winfo_children():
            widget.destroy()
        
        # Background
        if self.bg_images:
            bg_label = tk.Label(self.root, image=self.bg_images["main"])
            bg_label.place(x=0, y=0, relwidth=1, relheight=1)
            
        # Main frame
        main_frame = ttk.Frame(self.root, style="systemTransparent.TFrame")
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Title frame with clock
        title_frame = ttk.Frame(main_frame, style="Transparent.TFrame")
        title_frame.pack(fill=tk.X, pady=(0, 20))
        
        # System title
        ttk.Label(title_frame, text="RETAILNET SMART SYSTEM", style="Title.TLabel").pack(side=tk.TOP)
        
        # Clock frame
        clock_frame = ttk.Frame(title_frame, style="Transparent.TFrame")
        clock_frame.pack(side=tk.RIGHT)
        
        ttk.Label(clock_frame, text="Date/Time:", style="Header.TLabel").pack(anchor="e")
        #ttk.Label(clock_frame, text="Time:", style="Header.TLabel").pack(anchor="e")
        self.clock_label = ttk.Label(clock_frame, text="", style="Clock.TLabel")
        self.clock_label.pack(anchor="e")
        
        # Start the clock
        self.update_clock()
        
        # Content frame
        content_frame = ttk.Frame(main_frame, style="TFrame")
        content_frame.pack(fill=tk.BOTH, expand=True)
        
        # Left panel - Scan and items
        left_frame = ttk.Frame(content_frame, style="TFrame")
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Scanned item entry
        ttk.Label(left_frame, text="Scanned Item:", style="Header.TLabel").pack(anchor="w", pady=(0, 5))
        self.scanned_item_entry = ttk.Entry(left_frame, style="TEntry")
        self.scanned_item_entry.pack(fill=tk.X, pady=(0, 10))
        self.scanned_item_entry.bind('<Return>', lambda e: self.add_scanned_item())
        
        # Current sale items treeview
        self.sale_tree = ttk.Treeview(left_frame, columns=("name", "price", "qty", "total"), 
                                     show="headings", style="Treeview")
        self.sale_tree.heading("name", text="Item Name")
        self.sale_tree.heading("price", text="Price")
        self.sale_tree.heading("qty", text="Qty")
        self.sale_tree.heading("total", text="Total")
        
        self.sale_tree.column("name", width=200, anchor="center")
        self.sale_tree.column("price", width=100, anchor="center")
        self.sale_tree.column("qty", width=80, anchor="center")
        self.sale_tree.column("total", width=120, anchor="center")
        
        self.sale_tree.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # Scrollbar for sale tree
        scrollbar = ttk.Scrollbar(left_frame, orient="vertical", command=self.sale_tree.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.sale_tree.configure(yscrollcommand=scrollbar.set)
        
        # Total amount
        total_frame = ttk.Frame(left_frame, style="TFrame")
        total_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(total_frame, text="Total Amount:", style="Header.TLabel").pack(side=tk.LEFT)
        self.total_label = ttk.Label(total_frame, text="0.00", style="Total.TLabel")
        self.total_label.pack(side=tk.LEFT, padx=10)
        
        # Buttons frame
        buttons_frame = ttk.Frame(left_frame, style="TFrame")
        buttons_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Finalize sale button
        finalize_button = ttk.Button(buttons_frame, text="Finalize Sale", 
                                   style="Primary.TButton",
                                   command=self.finalize_sale)
        finalize_button.pack(side=tk.LEFT, padx=5)
        
        # Remove button
        remove_button = ttk.Button(buttons_frame, text="Remove Item", 
                                 style="Danger.TButton",
                                 command=self.remove_item)
        remove_button.pack(side=tk.LEFT, padx=5)
        
        # Right panel - Functions
        right_frame = ttk.Frame(content_frame, style="TFrame")
        right_frame.pack(side=tk.LEFT, fill=tk.BOTH, padx=10, pady=10)
        
        # Inventory search button
        search_button = ttk.Button(right_frame, text="Item Search", 
                                 style="Secondary.TButton",
                                 command=self.show_inventory_search)
        search_button.pack(fill=tk.X, pady=5)
        
        # Inventory check button
        inventory_button = ttk.Button(right_frame, text="Inventory Check", 
                                    style="Secondary.TButton",
                                    command=self.show_inventory_options)
        inventory_button.pack(fill=tk.X, pady=5)
        
        # Total day sale button
        day_sale_button = ttk.Button(right_frame, text="Total Day Sale", 
                                   style="Secondary.TButton",
                                   command=self.show_day_sales)
        day_sale_button.pack(fill=tk.X, pady=5)
        
        # Items sold button
        items_sold_button = ttk.Button(right_frame, text="Items Sold", 
                                     style="Secondary.TButton",
                                     command=self.show_items_sold)
        items_sold_button.pack(fill=tk.X, pady=5)
        
        # Inventory edit button
        edit_button = ttk.Button(right_frame, text="Inventory Edit", 
                               style="Secondary.TButton",
                               command=self.show_inventory_edit)
        edit_button.pack(fill=tk.X, pady=5)
        
        # Logout button
        logout_button = ttk.Button(right_frame, text="Logout", 
                                 style="Danger.TButton",
                                 command=self.logout)
        logout_button.pack(fill=tk.X, pady=5)
        
        # Initialize current sale
        self.current_sale = []
        self.total_sale_amount = 0.0
        self.update_sale_display()
    
    def add_scanned_item(self):
        item_name = self.scanned_item_entry.get().strip()
        if not item_name:
            messagebox.showwarning("Warning", "Please enter an item name")
            return
        
        cursor = self.db_connection.cursor()
        cursor.execute("SELECT * FROM inventory WHERE item_name=?", (item_name,))
        item = cursor.fetchone()
        
        if not item:
            messagebox.showerror("Error", "Item not found in inventory")
            self.scanned_item_entry.delete(0, tk.END)
            return
        
        item_id, item_name, price, quantity, _ = item
        
        # Check if item already in current sale
        for sale_item in self.current_sale:
            if sale_item["name"] == item_name:
                if sale_item["quantity"] < quantity:
                    sale_item["quantity"] += 1
                    sale_item["total"] = sale_item["price"] * sale_item["quantity"]
                else:
                    messagebox.showerror("Error", "Not enough stock available")
                self.update_sale_display()
                self.scanned_item_entry.delete(0, tk.END)
                return
        
        # Add new item to sale
        if quantity > 0:
            self.current_sale.append({
                "name": item_name,
                "price": price,
                "quantity": 1,
                "total": price
            })
            self.update_sale_display()
            self.scanned_item_entry.delete(0, tk.END)
        else:
            messagebox.showerror("Error", "Item out of stock")
    
    def update_sale_display(self):
        # Clear current display
        for item in self.sale_tree.get_children():
            self.sale_tree.delete(item)
        
        # Add current sale items
        self.total_sale_amount = 0.0
        for item in self.current_sale:
            self.sale_tree.insert("", tk.END, values=(
                item["name"],
                f"{item['price']:.2f}",
                item["quantity"],
                f"{item['total']:.2f}"
            ))
            self.total_sale_amount += item["total"]
        
        # Update total label
        self.total_label.config(text=f"{self.total_sale_amount:.2f}")
    
    def remove_item(self):
        selected_item = self.sale_tree.selection()
        if not selected_item:
            messagebox.showwarning("Warning", "Please select an item to remove")
            return
        
        # Get the item details from the selected row
        item_values = self.sale_tree.item(selected_item, "values")
        item_name = item_values[0]
        current_qty = int(item_values[2])
        
        # Ask how many to remove
        remove_qty = simpledialog.askinteger(
            "Remove Items",
            f"How many of '{item_name}' would you like to remove? (Current: {current_qty})",
            parent=self.root,
            minvalue=1,
            maxvalue=current_qty
        )
        
        if remove_qty is None:  # User cancelled
            return
        
        # Update the quantity or remove the item
        for i, item in enumerate(self.current_sale):
            if item["name"] == item_name:
                if remove_qty == current_qty:
                    del self.current_sale[i]  # Remove entire item
                else:
                    item["quantity"] -= remove_qty
                    item["total"] = item["price"] * item["quantity"]
                break
        
        self.update_sale_display()
    
    def finalize_sale(self):
        if not self.current_sale:
            messagebox.showwarning("Warning", "No items in the current sale")
            return
        
        # Update inventory and record sale
        cursor = self.db_connection.cursor()
        now = datetime.datetime.now()
        sale_date = now.strftime("%Y-%m-%d")
        sale_time = now.strftime("%H:%M:%S")
        
        try:
            for item in self.current_sale:
                # Update inventory
                cursor.execute("UPDATE inventory SET quantity = quantity - ? WHERE item_name = ?", 
                             (item["quantity"], item["name"]))
                
                # Record sale
                cursor.execute(
                    "INSERT INTO sales (item_name, quantity, price, total, sale_date, sale_time) "
                    "VALUES (?, ?, ?, ?, ?, ?)",
                    (item["name"], item["quantity"], item["price"], item["total"], 
                     sale_date, sale_time)
                )
            
            self.db_connection.commit()
            
            # Show receipt
            self.show_receipt()
            
            # Clear current sale
            self.current_sale = []
            self.total_sale_amount = 0.0
            self.update_sale_display()
            
            messagebox.showinfo("Success", "Sale completed successfully")
        except Exception as e:
            self.db_connection.rollback()
            messagebox.showerror("Error", f"Failed to complete sale: {str(e)}")
    
    def show_receipt(self):
        receipt_window = tk.Toplevel(self.root)
        receipt_window.title("Sale Receipt")
        receipt_window.geometry("500x600")
        
        # Title
        ttk.Label(receipt_window, text="RETAILNET SALE RECEIPT", 
                 font=('Arial', 16, 'bold')).pack(pady=10)
        
        # Date and time
        now = datetime.datetime.now()
        ttk.Label(receipt_window, 
                 text=f"Date: {now.strftime('%Y-%m-%d %H:%M:%S')}",
                 font=('Arial', 12)).pack(pady=5)
        
        # Items frame
        items_frame = ttk.Frame(receipt_window)
        items_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        # Treeview for items
        receipt_tree = ttk.Treeview(items_frame, columns=("name", "qty", "price", "total"), 
                                   show="headings", height=15)
        receipt_tree.heading("name", text="Item")
        receipt_tree.heading("qty", text="Qty")
        receipt_tree.heading("price", text="Price")
        receipt_tree.heading("total", text="Total")
        
        receipt_tree.column("name", width=200, anchor="center")
        receipt_tree.column("qty", width=80, anchor="center")
        receipt_tree.column("price", width=100, anchor="center")
        receipt_tree.column("total", width=100, anchor="center")
        
        receipt_tree.pack(fill=tk.BOTH, expand=True)
        
        # Add items to receipt
        for item in self.current_sale:
            receipt_tree.insert("", tk.END, values=(
                item["name"],
                item["quantity"],
                f"{item['price']:.2f}",
                f"{item['total']:.2f}"
            ))
        
        # Total
        ttk.Label(receipt_window, 
                 text=f"TOTAL: {self.total_sale_amount:.2f}",
                 font=('Arial', 14, 'bold')).pack(pady=10)
        
        # Close button
        ttk.Button(receipt_window, text="Close", 
                  command=receipt_window.destroy).pack(pady=10)
    
    def show_inventory_search(self):
        search_window = tk.Toplevel(self.root)
        search_window.title("Item Search")
        search_window.geometry("600x400")
        
        # Search frame
        search_frame = ttk.Frame(search_window)
        search_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Label(search_frame, text="Search Item:").pack(side=tk.LEFT)
        self.search_entry = ttk.Entry(search_frame)
        self.search_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        self.search_entry.bind("<KeyRelease>", lambda e: self.search_inventory_items())
        
        # Results treeview
        self.search_tree = ttk.Treeview(search_window, columns=("name", "price", "qty"), 
                                      show="headings")
        self.search_tree.heading("name", text="Item Name")
        self.search_tree.heading("price", text="Price")
        self.search_tree.heading("qty", text="Quantity")
        
        self.search_tree.column("name", width=300, anchor="center")
        self.search_tree.column("price", width=150, anchor="center")
        self.search_tree.column("qty", width=150, anchor="center")
        
        self.search_tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))
        
        # Select button
        select_button = ttk.Button(search_window, text="Select Item", 
                                 command=self.select_searched_item)
        select_button.pack(pady=(0, 10))
        
        # Load all items initially
        self.search_inventory_items()
    
    def search_inventory_items(self):
        search_term = self.search_entry.get().lower()
        
        # Clear existing items
        for item in self.search_tree.get_children():
            self.search_tree.delete(item)
        
        # Search in database
        cursor = self.db_connection.cursor()
        cursor.execute("SELECT item_name, price, quantity FROM inventory")
        items = cursor.fetchall()
        
        # Add matching items
        for item in items:
            name, price, qty = item
            if search_term in name.lower():
                self.search_tree.insert("", tk.END, values=(name, f"{price:.2f}", qty))
    
    def select_searched_item(self):
        selected_item = self.search_tree.selection()
        if not selected_item:
            messagebox.showwarning("Warning", "Please select an item")
            return
        
        item_name = self.search_tree.item(selected_item, "values")[0]
        self.scanned_item_entry.delete(0, tk.END)
        self.scanned_item_entry.insert(0, item_name)
        self.search_tree.master.destroy()  # Close the search window
    
    def show_inventory_options(self):
        option_window = tk.Toplevel(self.root)
        option_window.title("Inventory Check")
        option_window.geometry("400x200")
        
        # Title
        ttk.Label(option_window, text="Select Inventory Option", 
                 font=('Arial', 14, 'bold')).pack(pady=10)
        
        # Available stock button
        available_button = ttk.Button(option_window, text="Available Stock", 
                                    command=lambda: self.show_inventory_list(True))
        available_button.pack(fill=tk.X, padx=50, pady=15)
        
        # Unavailable stock button
        unavailable_button = ttk.Button(option_window, text="Unavailable Stock", 
                                      command=lambda: self.show_inventory_list(False))
        unavailable_button.pack(fill=tk.X, padx=50, pady=15)
    
    def show_inventory_list(self, available=True):
        list_window = tk.Toplevel(self.root)
        list_window.title("Available Stock" if available else "Unavailable Stock")
        list_window.geometry("600x400")
        
        # Treeview
        inventory_tree = ttk.Treeview(list_window, columns=("name", "price", "qty"), 
                                    show="headings")
        inventory_tree.heading("name", text="Item Name")
        inventory_tree.heading("price", text="Price")
        inventory_tree.heading("qty", text="Quantity")
        
        inventory_tree.column("name", width=300, anchor="center")
        inventory_tree.column("price", width=150, anchor="center")
        inventory_tree.column("qty", width=150, anchor="center")
        
        inventory_tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Load items
        cursor = self.db_connection.cursor()
        if available:
            cursor.execute("SELECT item_name, price, quantity FROM inventory WHERE quantity > 0")
        else:
            cursor.execute("SELECT item_name, price, quantity FROM inventory WHERE quantity <= 0")
        
        items = cursor.fetchall()
        for item in items:
            inventory_tree.insert("", tk.END, values=item)
    
    def show_day_sales(self):
        sales_window = tk.Toplevel(self.root)
        sales_window.title("Today's Sales")
        sales_window.geometry("800x500")
        
        # Title
        ttk.Label(sales_window, text="Today's Sales Summary", 
                 font=('Arial', 16, 'bold')).pack(pady=10)
        
        # Date
        today = datetime.date.today().strftime("%Y-%m-%d")
        ttk.Label(sales_window, text=f"Date: {today}").pack()
        
        # Treeview
        sales_tree = ttk.Treeview(sales_window, 
                                columns=("time", "item", "qty", "price", "total"), 
                                show="headings")
        sales_tree.heading("time", text="Time")
        sales_tree.heading("item", text="Item")
        sales_tree.heading("qty", text="Qty")
        sales_tree.heading("price", text="Price")
        sales_tree.heading("total", text="Total")
        
        sales_tree.column("time", width=100, anchor="center")
        sales_tree.column("item", width=200, anchor="center")
        sales_tree.column("qty", width=80, anchor="center")
        sales_tree.column("price", width=100, anchor="center")
        sales_tree.column("total", width=100, anchor="center")
        
        sales_tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(sales_window, orient="vertical", command=sales_tree.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        sales_tree.configure(yscrollcommand=scrollbar.set)
        
        # Load today's sales
        cursor = self.db_connection.cursor()
        cursor.execute("""
            SELECT sale_time, item_name, quantity, price, total 
            FROM sales 
            WHERE sale_date = ?
            ORDER BY sale_time
        """, (today,))
        
        sales = cursor.fetchall()
        total_amount = 0.0
        
        for sale in sales:
            sales_tree.insert("", tk.END, values=sale)
            total_amount += sale[4]  # Add to total
        
        # Total
        ttk.Label(sales_window, 
                 text=f"TOTAL SALES TODAY: {total_amount:.2f}",
                 font=('Arial', 14, 'bold')).pack(pady=10)
    
    def show_items_sold(self):
        items_window = tk.Toplevel(self.root)
        items_window.title("Items Sold Today")
        items_window.geometry("600x400")
        
        # Title
        ttk.Label(items_window, text="Items Sold Today", 
                 font=('Arial', 16, 'bold')).pack(pady=10)
        
        # Treeview
        items_tree = ttk.Treeview(items_window, columns=("item", "qty", "total"), 
                                show="headings")
        items_tree.heading("item", text="Item")
        items_tree.heading("qty", text="Total Qty")
        items_tree.heading("total", text="Total Amount")
        
        items_tree.column("item", width=300, anchor="center")
        items_tree.column("qty", width=150, anchor="center")
        items_tree.column("total", width=150, anchor="center")
        
        items_tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Load today's items
        today = datetime.date.today().strftime("%Y-%m-%d")
        cursor = self.db_connection.cursor()
        cursor.execute("""
            SELECT item_name, SUM(quantity), SUM(total) 
            FROM sales 
            WHERE sale_date = ?
            GROUP BY item_name
            ORDER BY SUM(quantity) DESC
        """, (today,))
        
        items = cursor.fetchall()
        for item in items:
            items_tree.insert("", tk.END, values=item)
    
    def show_inventory_edit(self):
        edit_window = tk.Toplevel(self.root)
        edit_window.title("Inventory Edit")
        edit_window.geometry("800x500")
        
        # Title
        ttk.Label(edit_window, text="Inventory Edit", 
                 font=('Arial', 16, 'bold')).pack(pady=10)
        
        # Treeview
        self.edit_tree = ttk.Treeview(edit_window, columns=("name", "price", "qty"), 
                                    show="headings")
        self.edit_tree.heading("name", text="Item Name")
        self.edit_tree.heading("price", text="Price")
        self.edit_tree.heading("qty", text="Quantity")
        
        self.edit_tree.column("name", width=300, anchor="center")
        self.edit_tree.column("price", width=200, anchor="center")
        self.edit_tree.column("qty", width=200, anchor="center")
        
        self.edit_tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(edit_window, orient="vertical", command=self.edit_tree.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.edit_tree.configure(yscrollcommand=scrollbar.set)
        
        # Buttons frame
        buttons_frame = ttk.Frame(edit_window)
        buttons_frame.pack(fill=tk.X, padx=10, pady=(0, 10))
        
        # Add button
        add_button = ttk.Button(buttons_frame, text="Add Item", 
                              command=self.show_add_item_dialog)
        add_button.pack(side=tk.LEFT, padx=5)
        
        # Edit button
        edit_button = ttk.Button(buttons_frame, text="Edit Item", 
                               command=self.edit_selected_item)
        edit_button.pack(side=tk.LEFT, padx=5)
        
        # Delete button
        delete_button = ttk.Button(buttons_frame, text="Delete Item", 
                                 command=self.delete_selected_item)
        delete_button.pack(side=tk.LEFT, padx=5)
        
        # Close button
        close_button = ttk.Button(buttons_frame, text="Close", 
                                command=edit_window.destroy)
        close_button.pack(side=tk.RIGHT, padx=5)
        
        # Load inventory
        self.load_inventory_to_edit()
    
    def load_inventory_to_edit(self):
        # Clear existing items
        for item in self.edit_tree.get_children():
            self.edit_tree.delete(item)
        
        # Load from database
        cursor = self.db_connection.cursor()
        cursor.execute("SELECT item_name, price, quantity FROM inventory ORDER BY item_name")
        items = cursor.fetchall()
        
        for item in items:
            self.edit_tree.insert("", tk.END, values=item)
    
    def show_add_item_dialog(self):
        dialog = tk.Toplevel(self.root)
        dialog.title("Add New Item")
        dialog.geometry("400x300")
        
        # Title
        ttk.Label(dialog, text="Add New Item", font=('Arial', 14, 'bold')).pack(pady=10)
        
        # Form frame
        form_frame = ttk.Frame(dialog)
        form_frame.pack(padx=20, pady=10)
        
        # Item name
        ttk.Label(form_frame, text="Item Name:").grid(row=0, column=0, sticky="e", pady=5)
        name_entry = ttk.Entry(form_frame)
        name_entry.grid(row=0, column=1, pady=5, padx=5)
        
        # Price
        ttk.Label(form_frame, text="Price:").grid(row=1, column=0, sticky="e", pady=5)
        price_entry = ttk.Entry(form_frame)
        price_entry.grid(row=1, column=1, pady=5, padx=5)
        
        # Quantity
        ttk.Label(form_frame, text="Quantity:").grid(row=2, column=0, sticky="e", pady=5)
        qty_entry = ttk.Entry(form_frame)
        qty_entry.grid(row=2, column=1, pady=5, padx=5)
        
        # Buttons frame
        buttons_frame = ttk.Frame(dialog)
        buttons_frame.pack(pady=10)
        
        def add_item():
            name = name_entry.get().strip()
            price = price_entry.get().strip()
            quantity = qty_entry.get().strip()
            
            if not name:
                messagebox.showerror("Error", "Item name is required")
                return
            
            try:
                price_val = float(price)
                if price_val <= 0:
                    raise ValueError("Price must be positive")
            except ValueError:
                messagebox.showerror("Error", "Invalid price value")
                return
            
            try:
                qty_val = int(quantity)
                if qty_val < 0:
                    raise ValueError("Quantity cannot be negative")
            except ValueError:
                messagebox.showerror("Error", "Invalid quantity value")
                return
            
            # Add to database
            cursor = self.db_connection.cursor()
            try:
                cursor.execute(
                    "INSERT INTO inventory (item_name, price, quantity, last_updated) "
                    "VALUES (?, ?, ?, datetime('now'))",
                    (name, price_val, qty_val)
                )
                self.db_connection.commit()
                messagebox.showinfo("Success", "Item added successfully")
                dialog.destroy()
                self.load_inventory_to_edit()
            except sqlite3.IntegrityError:
                messagebox.showerror("Error", "Item name already exists")
        
        ttk.Button(buttons_frame, text="Add", command=add_item).pack(side=tk.LEFT, padx=10)
        ttk.Button(buttons_frame, text="Cancel", command=dialog.destroy).pack(side=tk.LEFT, padx=10)
    
    def edit_selected_item(self):
        selected_item = self.edit_tree.selection()
        if not selected_item:
            messagebox.showwarning("Warning", "Please select an item to edit")
            return
        
        item_values = self.edit_tree.item(selected_item, "values")
        item_name = item_values[0]
        
        dialog = tk.Toplevel(self.root)
        dialog.title("Edit Item")
        dialog.geometry("400x300")
        
        # Title
        ttk.Label(dialog, text="Edit Item", font=('Arial', 14, 'bold')).pack(pady=10)
        
        # Form frame
        form_frame = ttk.Frame(dialog)
        form_frame.pack(padx=20, pady=10)
        
        # Item name (display only)
        ttk.Label(form_frame, text="Item Name:").grid(row=0, column=0, sticky="e", pady=5)
        name_label = ttk.Label(form_frame, text=item_name)
        name_label.grid(row=0, column=1, pady=5, padx=5, sticky="w")
        
        # Price
        ttk.Label(form_frame, text="Price:").grid(row=1, column=0, sticky="e", pady=5)
        price_entry = ttk.Entry(form_frame)
        price_entry.insert(0, item_values[1])
        price_entry.grid(row=1, column=1, pady=5, padx=5)
        
        # Quantity
        ttk.Label(form_frame, text="Quantity:").grid(row=2, column=0, sticky="e", pady=5)
        qty_entry = ttk.Entry(form_frame)
        qty_entry.insert(0, item_values[2])
        qty_entry.grid(row=2, column=1, pady=5, padx=5)
        
        # Buttons frame
        buttons_frame = ttk.Frame(dialog)
        buttons_frame.pack(pady=10)
        
        def update_item():
            price = price_entry.get().strip()
            quantity = qty_entry.get().strip()
            
            try:
                price_val = float(price)
                if price_val <= 0:
                    raise ValueError("Price must be positive")
            except ValueError:
                messagebox.showerror("Error", "Invalid price value")
                return
            
            try:
                qty_val = int(quantity)
                if qty_val < 0:
                    raise ValueError("Quantity cannot be negative")
            except ValueError:
                messagebox.showerror("Error", "Invalid quantity value")
                return
            
            # Update in database
            cursor = self.db_connection.cursor()
            cursor.execute(
                "UPDATE inventory SET price = ?, quantity = ?, last_updated = datetime('now') "
                "WHERE item_name = ?",
                (price_val, qty_val, item_name)
            )
            self.db_connection.commit()
            messagebox.showinfo("Success", "Item updated successfully")
            dialog.destroy()
            self.load_inventory_to_edit()
        
        ttk.Button(buttons_frame, text="Update", command=update_item).pack(side=tk.LEFT, padx=10)
        ttk.Button(buttons_frame, text="Cancel", command=dialog.destroy).pack(side=tk.LEFT, padx=10)
    
    def delete_selected_item(self):
        selected_item = self.edit_tree.selection()
        if not selected_item:
            messagebox.showwarning("Warning", "Please select an item to delete")
            return
        
        item_name = self.edit_tree.item(selected_item, "values")[0]
        
        if messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete '{item_name}'?"):
            cursor = self.db_connection.cursor()
            cursor.execute("DELETE FROM inventory WHERE item_name = ?", (item_name,))
            self.db_connection.commit()
            messagebox.showinfo("Success", "Item deleted successfully")
            self.load_inventory_to_edit()
    
    def logout(self):
        self.current_user = None
        self.current_sale = []
        self.total_sale_amount = 0.0
        self.show_login_screen()

if __name__ == "__main__":
    root = tk.Tk()
    app = RetailNetSystem(root)
    root.mainloop()