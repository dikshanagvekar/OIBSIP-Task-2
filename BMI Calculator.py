import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox, filedialog
import json, os, csv
from datetime import datetime
import matplotlib.pyplot as plt
import winsound  # For soft chime

# ---------- Config ----------
DATA_FILE = "bmi_data.json"
SETTINGS_FILE = "settings.json"

# Load saved theme
def load_settings():
    if os.path.exists(SETTINGS_FILE):
        with open(SETTINGS_FILE, "r") as file:
            return json.load(file)
    return {"theme": "light"}

def save_settings(settings):
    with open(SETTINGS_FILE, "w") as file:
        json.dump(settings, file)

settings = load_settings()
ctk.set_appearance_mode(settings.get("theme", "light"))
ctk.set_default_color_theme("blue")

# ---------- Data Handling ----------
def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as file:
            return json.load(file)
    return {}

def save_data(data):
    with open(DATA_FILE, "w") as file:
        json.dump(data, file, indent=4)

def clear_user_data(name):
    data = load_data()
    if name in data:
        del data[name]
        save_data(data)

# ---------- BMI Logic ----------
def calculate_bmi(weight, height):
    return weight / (height ** 2)

def get_category(bmi):
    if bmi < 18.5:
        return "Underweight", "#1E90FF"
    elif 18.5 <= bmi < 25:
        return "Normal weight", "#2E8B57"
    elif 25 <= bmi < 30:
        return "Overweight", "#FFA500"
    else:
        return "Obese", "#FF4500"

# ---------- Animate Circular Progress ----------
def animate_circular_progress(target_bmi, max_bmi=40):
    steps = 60
    for i in range(steps + 1):
        progress = (target_bmi / max_bmi) * 360 * (i / steps)
        canvas.delete("progress")
        canvas.create_arc(10, 10, 190, 190, start=90, extent=-progress,
                        style="arc", outline=current_color, width=15, tags="progress")
        app.update()
        app.after(10)

# ---------- Horizontal Range Bar ----------
def draw_range_bar():
    range_canvas.delete("all")
    segments = [
        (0, 18.5, "#1E90FF"),
        (18.5, 25, "#2E8B57"),
        (25, 30, "#FFA500"),
        (30, 40, "#FF4500")
    ]
    width = 280
    height = 20
    for start, end, color in segments:
        x1 = (start / 40) * width
        x2 = (end / 40) * width
        range_canvas.create_rectangle(x1, 0, x2, height, fill=color, width=0)
    range_canvas.create_text(width/2, height+10, text="BMI Range", font=("Helvetica", 10))

# ---------- Main Functions ----------
def submit():
    global current_color
    name = name_entry.get().strip()

    try:
        weight = float(weight_entry.get())
        height = float(height_entry.get())

        # Convert cm to meters if > 3
        if height > 3:
            height = height / 100

        if weight <= 0 or height <= 0:
            messagebox.showerror("Error", "Enter valid weight/height.")
            return

        bmi = calculate_bmi(weight, height)
        category, color = get_category(bmi)
        current_color = color

        # Animate circular progress
        animate_circular_progress(bmi)

        # Show BMI value and category
        result_label.configure(text=f"{bmi:.1f}\n{category}", text_color=color)

        # Save history
        data = load_data()
        if name not in data:
            data[name] = []
        data[name].append({"date": str(datetime.now().date()), "bmi": bmi})
        save_data(data)

    except ValueError:
        messagebox.showerror("Error", "Enter numeric values only.")

def show_history():
    name = name_entry.get().strip()
    data = load_data()

    if name not in data or len(data[name]) == 0:
        messagebox.showinfo("History", "No data found for this user.")
        return

    bmis = [entry['bmi'] for entry in data[name]]
    dates = [entry['date'] for entry in data[name]]

    plt.plot(dates, bmis, marker='o', color='purple')
    plt.title(f"BMI Trend for {name}")
    plt.xlabel("Date")
    plt.ylabel("BMI")
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()

def export_csv():
    name = name_entry.get().strip()
    data = load_data()

    if name not in data or len(data[name]) == 0:
        messagebox.showinfo("Export", "No data to export for this user.")
        return

    file_path = filedialog.asksaveasfilename(defaultextension=".csv",
                                            filetypes=[("CSV files", "*.csv")],
                                            title="Save as")
    if file_path:
        with open(file_path, "w", newline="") as file:
            writer = csv.writer(file)
            writer.writerow(["Date", "BMI"])
            for entry in data[name]:
                writer.writerow([entry["date"], entry["bmi"]])
        messagebox.showinfo("Export", "Data exported successfully!")

def clear_history():
    name = name_entry.get().strip()
    if not name:
        messagebox.showerror("Error", "Enter a name to clear history.")
        return

    confirm = messagebox.askyesno("Confirm", f"Clear all BMI history for {name}?")
    if confirm:
        clear_user_data(name)
        messagebox.showinfo("Cleared", f"History cleared for {name}.")

# ---------- Theme Toggle ----------
def toggle_theme():
    current_mode = ctk.get_appearance_mode()
    new_mode = "dark" if current_mode == "Light" else "light"
    ctk.set_appearance_mode(new_mode)
    save_settings({"theme": new_mode})

# ---------- Main BMI App Window ----------
def open_main_app():
    global app, canvas, range_canvas, result_label, name_entry, weight_entry, height_entry, current_color

    # Play soft Windows system notification sound
    winsound.PlaySound("SystemNotification", winsound.SND_ALIAS | winsound.SND_ASYNC)

    app = ctk.CTk()
    app.title("Modern BMI Calculator")
    app.geometry("400x600")
    app.resizable(False, False)

    title = ctk.CTkLabel(app, text="BMI Calculator", font=("Helvetica", 24, "bold"))
    title.pack(pady=10)

    canvas = ctk.CTkCanvas(app, width=200, height=200, bg=app.cget("bg"), highlightthickness=0)
    canvas.pack(pady=10)
    current_color = "#2E8B57"

    result_label = ctk.CTkLabel(app, text="--\nResult", font=("Helvetica", 18, "bold"))
    result_label.pack(pady=5)

    range_canvas = ctk.CTkCanvas(app, width=280, height=35, bg=app.cget("bg"), highlightthickness=0)
    range_canvas.pack(pady=5)
    draw_range_bar()

    name_entry = ctk.CTkEntry(app, placeholder_text="Enter your name", width=250)
    name_entry.pack(pady=8)

    weight_entry = ctk.CTkEntry(app, placeholder_text="Weight (kg)", width=250)
    weight_entry.pack(pady=8)

    height_entry = ctk.CTkEntry(app, placeholder_text="Height (m or cm)", width=250)
    height_entry.pack(pady=8)

    ctk.CTkButton(app, text="Calculate BMI", command=submit, width=200).pack(pady=10)
    ctk.CTkButton(app, text="Show History", command=show_history, width=200).pack(pady=5)
    ctk.CTkButton(app, text="Export History to CSV", command=export_csv, width=200).pack(pady=5)
    ctk.CTkButton(app, text="Clear History", command=clear_history, width=200).pack(pady=5)
    ctk.CTkButton(app, text="Toggle Dark Mode", command=toggle_theme, width=200).pack(pady=10)

    footer = ctk.CTkLabel(app, text="Track your BMI over time", font=("Helvetica", 10))
    footer.pack(side="bottom", pady=10)

    app.mainloop()

# ---------- Splash Screen ----------
def create_splash():
    global splash, after_id, gradient_id
    splash = ctk.CTk()
    splash.geometry("300x300")
    splash.title("Loading...")
    splash.resizable(False, False)
    splash.eval('tk::PlaceWindow . center')

    # Gradient canvas
    canvas_bg = tk.Canvas(splash, width=300, height=300, highlightthickness=0)
    canvas_bg.pack(fill="both", expand=True)

    # Function to get gradient colors dynamically
    def get_gradient_colors():
        if ctk.get_appearance_mode() == "Dark":
            return (75, 0, 130), (0, 0, 0)  # purple → black
        else:
            return (135, 206, 250), (255, 255, 255)  # light blue → white

    # Animated gradient
    def draw_gradient(shift=0):
        global gradient_id
        start_color, end_color = get_gradient_colors()
        steps = 100
        for i in range(steps):
            r = int(start_color[0] + (end_color[0]-start_color[0]) * i/steps)
            g = int(start_color[1] + (end_color[1]-start_color[1]) * i/steps)
            b = int(start_color[2] + (end_color[2]-start_color[2]) * i/steps)
            r = (r + shift) % 256
            color = f"#{r:02x}{g:02x}{b:02x}"
            canvas_bg.create_line(0, i*3, 300, i*3, fill=color, width=3)
        gradient_id = splash.after(100, draw_gradient, (shift+2) % 256)

    # Loading ring
    def get_bg_color():
        return "#000000" if ctk.get_appearance_mode() == "Dark" else "#FFFFFF"

    ring_canvas = tk.Canvas(canvas_bg, width=150, height=150, bg=get_bg_color(), highlightthickness=0)
    ring_canvas.place(relx=0.5, rely=0.5, anchor="center")

    splash_label = tk.Label(canvas_bg, text="BMI Calculator", font=("Helvetica", 20, "bold"),
                            fg="white" if ctk.get_appearance_mode()=="Dark" else "black", bg=get_bg_color())
    splash_label.place(relx=0.5, rely=0.8, anchor="center")

    # Skip splash on click
    def skip(event=None):
        fade_out(0)  # instantly fade out

    canvas_bg.bind("<Button-1>", skip)
    ring_canvas.bind("<Button-1>", skip)
    splash_label.bind("<Button-1>", skip)

    def animate(angle=0):
        global after_id
        ring_canvas.delete("arc")
        ring_canvas.create_arc(10, 10, 140, 140, start=angle, extent=90, style="arc",
                            outline="#FFFFFF" if ctk.get_appearance_mode()=="Dark" else "#4B0082",
                            width=6, tags="arc")
        after_id = splash.after(50, animate, (angle+10) % 360)

    def fade_out(alpha=1.0):
        if alpha > 0:
            splash.attributes("-alpha", alpha)
            splash.after(50, fade_out, alpha-0.1)
        else:
            close_splash()

    def close_splash():
        # Cancel both callbacks safely
        for cb in [after_id, gradient_id]:
            if cb:
                try:
                    splash.after_cancel(cb)
                except:
                    pass
        splash.destroy()
        open_main_app()

    after_id = None
    gradient_id = None
    draw_gradient()
    animate()
    splash.after(2500, fade_out)  # fade out after 2.5s
    splash.mainloop()

# Run splash first
create_splash()
