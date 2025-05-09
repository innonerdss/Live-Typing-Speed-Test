import sqlite3
import tkinter as tk
from tkinter import messagebox, simpledialog
import random
import time

# ---------------- DATABASE FUNCTIONS ----------------

def setup_database():
    conn = sqlite3.connect("scores.db")
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS scores (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            wpm REAL NOT NULL,
            accuracy REAL NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

def save_score(name, wpm, accuracy):
    conn = sqlite3.connect("scores.db")
    cursor = conn.cursor()
    cursor.execute("INSERT INTO scores (name, wpm, accuracy) VALUES (?, ?, ?)", (name, wpm, accuracy))
    conn.commit()
    conn.close()

def get_leaderboard(limit=10):
    conn = sqlite3.connect("scores.db")
    cursor = conn.cursor()
    cursor.execute("SELECT name, wpm, accuracy FROM scores ORDER BY wpm DESC, accuracy DESC LIMIT ?", (limit,))
    leaderboard = cursor.fetchall()
    conn.close()
    return leaderboard

# ---------------- LOGIC FUNCTIONS ----------------

sample_paragraphs = [
    "Typing is an essential skill in the digital age. Whether you're a writer, programmer, or student, typing quickly and accurately can save you a lot of time and effort. Practicing regularly can help improve your speed and reduce errors.",
    "The art of touch typing involves muscle memory and consistent practice. Many people rely on looking at their keyboards, but with patience and training, you can type efficiently without even glancing at the keys.",
    "In the world of computers, every second counts. Efficient typing not only increases productivity but also reduces mental fatigue. It's a skill worth mastering for anyone who spends considerable time at a computer.",
    "A high typing speed combined with strong accuracy can be a significant advantage in many professions. From data entry to content creation, being able to type quickly means you can get your ideas down faster and with less friction.",
    "Improving your typing takes time, but it's a journey worth taking. Set daily goals, test your speed, and most importantly, stay consistent. Over time, you’ll notice your fingers flying over the keys effortlessly."
]

def get_random_paragraph():
    return random.choice(sample_paragraphs)

def calculate_results(typed_text, original_text, elapsed_time_sec):
    typed_chars = len(typed_text)
    correct_chars = sum(1 for t, o in zip(typed_text, original_text) if t == o)
    total_chars = len(original_text)

    elapsed_minutes = elapsed_time_sec / 60
    wpm = (typed_chars / 5) / elapsed_minutes if elapsed_minutes > 0 else 0
    accuracy = (correct_chars / total_chars) * 100 if total_chars > 0 else 0

    return round(wpm, 2), round(accuracy, 2)

# ---------------- GUI FRONTEND ----------------

class TypingTestApp:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Typing Speed Test")
        self.root.geometry("900x600")
        self.root.configure(bg="lightblue")

        self.given_text = ""
        self.time_left = 60
        self.start_time = None
        self.timer_running = False

        self.text_label = tk.Label(self.root, text="", font=("Times New Roman", 14),
                                   justify="left", wraplength=800, bg="lightblue")
        self.text_label.pack(pady=20)

        self.text_input = tk.Text(self.root, font=("Times New Roman", 14), height=7, width=90)
        self.text_input.pack(pady=20)
        self.text_input.bind("<KeyPress>", self.on_key_press)

        self.timer_label = tk.Label(self.root, text=f"Time left: {self.time_left}s",
                                    font=("Times New Roman", 16), bg="lightblue")
        self.timer_label.pack(pady=10)

        self.result_label = tk.Label(self.root, text="", font=("Times New Roman", 16), bg="lightblue")
        self.result_label.pack(pady=10)

        self.start_button = tk.Button(self.root, text="Start New Test", command=self.start_test,
                                      font=("Times New Roman", 14))
        self.start_button.pack(pady=10)

        self.leaderboard_button = tk.Button(self.root, text="Show Leaderboard", command=self.show_leaderboard,
                                            font=("Times New Roman", 14))
        self.leaderboard_button.pack(pady=5)

        setup_database()
        self.start_test()  # Automatically start with the first test
        self.root.mainloop()

    def start_test(self):
        self.given_text = get_random_paragraph()
        self.text_label.config(text=self.given_text)
        self.text_input.delete("1.0", tk.END)
        self.text_input.focus()
        self.time_left = 60
        self.timer_running = False
        self.start_time = None
        self.timer_label.config(text=f"Time left: {self.time_left}s")
        self.result_label.config(text="")

    def on_key_press(self, event):
        if not self.timer_running:
            self.start_time = time.time()
            self.timer_running = True
            self.update_timer()

    def update_timer(self):
        if self.time_left > 0:
            self.time_left -= 1
            self.timer_label.config(text=f"Time left: {self.time_left}s")
            self.root.after(1000, self.update_timer)
        else:
            self.timer_label.config(text="Time's up!")
            self.check_result()

    def check_result(self):
        typed_text = self.text_input.get("1.0", tk.END).strip()
        elapsed_time = time.time() - self.start_time if self.start_time else 60
        wpm, accuracy = calculate_results(typed_text, self.given_text, elapsed_time)

        name = simpledialog.askstring("Name Entry", "Enter your name:")
        if name:
            save_score(name, wpm, accuracy)

        self.result_label.config(text=f"✅ Results:\nWPM: {wpm}\nAccuracy: {accuracy:.2f}%")

    def show_leaderboard(self):
        leaderboard = get_leaderboard()
        if not leaderboard:
            messagebox.showinfo("Leaderboard", "No entries yet.")
            return

        leaderboard_text = "🏆 Leaderboard:\n\n"
        for i, (name, wpm, acc) in enumerate(leaderboard, 1):
            leaderboard_text += f"{i}. {name} - WPM: {wpm}, Accuracy: {acc}%\n"

        messagebox.showinfo("Leaderboard", leaderboard_text)

# ---------------- RUN APP ----------------

if __name__ == "__main__":
    TypingTestApp()
