from pymongo import MongoClient
import tkinter as tk
from tkinter import messagebox, simpledialog
from pymongo import MongoClient

class ContactApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Contact Management System")

        # MongoDB Connection
        self.client = MongoClient('mongodb://localhost:27017')
        self.db = self.client['contact_db']
        self.contacts_collection = self.db['contacts']

        self.name_var = tk.StringVar()
        self.phone_var = tk.StringVar()
        self.email_var = tk.StringVar()
        self.search_var = tk.StringVar()

        self.setup_ui()

    def setup_ui(self):
        # Adding Contact Frame
        add_frame = tk.Frame(self.root)
        add_frame.pack(pady=10)

        tk.Label(add_frame, text="Name").grid(row=0, column=0, padx=10, pady=5)
        tk.Entry(add_frame, textvariable=self.name_var).grid(row=0, column=1, padx=10, pady=5)

        tk.Label(add_frame, text="Phone").grid(row=1, column=0, padx=10, pady=5)
        tk.Entry(add_frame, textvariable=self.phone_var).grid(row=1, column=1, padx=10, pady=5)

        tk.Label(add_frame, text="Email").grid(row=2, column=0, padx=10, pady=5)
        tk.Entry(add_frame, textvariable=self.email_var).grid(row=2, column=1, padx=10, pady=5)

        tk.Button(add_frame, text="Add Contact", command=self.add_contact).grid(row=4, column=0, columnspan=2, pady=10)

        # Search and Display Frame
        search_frame = tk.Frame(self.root)
        search_frame.pack(pady=10)

        tk.Label(search_frame, text="Search").grid(row=0, column=0, padx=10, pady=5)
        tk.Entry(search_frame, textvariable=self.search_var).grid(row=0, column=1, padx=10, pady=5)
        tk.Button(search_frame, text="Search", command=self.search_contact).grid(row=0, column=2, padx=10, pady=5)
        tk.Button(search_frame, text="View All", command=self.view_contacts).grid(row=0, column=3, padx=10, pady=5)

        # Listbox for displaying contacts
        self.contact_listbox = tk.Listbox(self.root, width=50, height=15)
        self.contact_listbox.pack(pady=10)
        self.contact_listbox.bind('<Double-1>', self.update_contact_dialog)

        # Delete Button
        tk.Button(self.root, text="Delete Contact", command=self.delete_contact).pack(pady=10)

    def add_contact(self):
        name = self.name_var.get()
        phone = self.phone_var.get()
        email = self.email_var.get()
        
        if name and phone:
            self.contacts_collection.insert_one({"name": name, "phone": phone, "email": email})
            messagebox.showinfo("Success", "Contact added successfully!")
            self.clear_form()
            self.view_contacts()
        else:
            messagebox.showerror("Error", "Name and Phone are required fields.")

    def view_contacts(self):
        self.contact_listbox.delete(0, tk.END)
        contacts = self.contacts_collection.find()
        for contact in contacts:
            self.contact_listbox.insert(tk.END, f"{contact['name']} - {contact['phone']}")

    def search_contact(self):
        query = self.search_var.get()
        self.contact_listbox.delete(0, tk.END)
        contacts = self.contacts_collection.find({"$or": [{"name": {"$regex": query, "$options": "i"}}, {"phone": {"$regex": query}}]})
        for contact in contacts:
            self.contact_listbox.insert(tk.END, f"{contact['name']} - {contact['phone']}")

    def delete_contact(self):
        selected_contact = self.contact_listbox.get(tk.ACTIVE)
        if selected_contact:
            name, phone = selected_contact.split(" - ")
            self.contacts_collection.delete_one({"name": name, "phone": phone})
            messagebox.showinfo("Success", "Contact deleted successfully!")
            self.view_contacts()
        else:
            messagebox.showerror("Error", "No contact selected.")

    def update_contact_dialog(self, event):
        selected_contact = self.contact_listbox.get(tk.ACTIVE)
        if selected_contact:
            name, phone = selected_contact.split(" - ")
            contact = self.contacts_collection.find_one({"name": name, "phone": phone})
            if contact:
                self.name_var.set(contact['name'])
                self.phone_var.set(contact['phone'])
                self.email_var.set(contact['email'])

                if simpledialog.askstring("Update Contact", "Update contact details and press OK") == "OK":
                    self.update_contact(contact['_id'])

    def update_contact(self, contact_id):
        name = self.name_var.get()
        phone = self.phone_var.get()
        email = self.email_var.get()

        if name and phone:
            self.contacts_collection.update_one({"_id": contact_id}, {"$set": {"name": name, "phone": phone, "email": email}})
            messagebox.showinfo("Success", "Contact updated successfully!")
            self.clear_form()
            self.view_contacts()
        else:
            messagebox.showerror("Error", "Name and Phone are required fields.")

    def clear_form(self):
        self.name_var.set("")
        self.phone_var.set("")
        self.email_var.set("")


if __name__ == "__main__":
    root = tk.Tk()
    app = ContactApp(root)
    root.mainloop()

