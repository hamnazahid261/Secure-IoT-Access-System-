import tkinter as tk
from tkinter import messagebox


# =========================
# GLOBAL USER STORAGE
# =========================
current_user = None


# =========================
# LOGIN FUNCTION
# =========================
def authenticate():
    global current_user

    username = entry_user.get()
    password = entry_pass.get()

    if username == "admin" and password == "1234":
        current_user = username
        messagebox.showinfo("Success", "Login Successful ✔")
        root.destroy()   # close GUI after login
    else:
        messagebox.showerror("Error", "Invalid Credentials ❌")


# =========================
# UI DESIGN
# =========================
root = tk.Tk()
root.title("Secure Login System")
root.geometry("400x300")
root.configure(bg="#1e1e2f")

# Title
title = tk.Label(root, text="LOGIN SYSTEM", font=("Arial", 18, "bold"),
                 bg="#1e1e2f", fg="white")
title.pack(pady=20)

# Username
tk.Label(root, text="Username", bg="#1e1e2f", fg="white").pack()
entry_user = tk.Entry(root, font=("Arial", 12))
entry_user.pack(pady=5)

# Password
tk.Label(root, text="Password", bg="#1e1e2f", fg="white").pack()
entry_pass = tk.Entry(root, show="*", font=("Arial", 12))
entry_pass.pack(pady=5)

# Login Button
login_btn = tk.Button(root, text="LOGIN", command=authenticate,
                      bg="#00c896", fg="white",
                      font=("Arial", 12, "bold"),
                      width=15)
login_btn.pack(pady=20)

# Footer
footer = tk.Label(root, text="Secure Authentication System",
                  bg="#1e1e2f", fg="gray")
footer.pack(pady=10)

root.mainloop()