
import json, random, time, tkinter as tk, os
from tkinter import ttk, messagebox
from pathlib import Path
import csv, datetime, hashlib

# Save results to a user-writable location
RESULTS_DIR = Path.home() / "Documents" / "TechPlus_Practice_Exam"
RESULTS_DIR.mkdir(parents=True, exist_ok=True)

RESULTS_CSV = RESULTS_DIR / "results.csv"
QUESTION_HISTORY_CSV = RESULTS_DIR / "question_history.csv"

PASSING_SCORE = 650
TOTAL_QUESTIONS = 75
TIME_LIMIT_SECONDS = 105 * 60
QUESTIONS_FILE = Path(__file__).with_name("questions.json")

def make_qid(question_text: str) -> str:
    """Short, stable ID for a question (based on its text)."""
    return hashlib.sha256(question_text.encode("utf-8")).hexdigest()[:12]

def save_question_history_csv(selected_questions, exam_id: str):
    """Append one row per question answered in this exam run."""
    write_header = not QUESTION_HISTORY_CSV.exists()
    with QUESTION_HISTORY_CSV.open("a", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        if write_header:
            w.writerow(["date", "exam_id", "qid", "question",
                        "your_answer", "correct_answer", "is_correct"])
        now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
        for q in selected_questions:
            qid = make_qid(q["q"])
            your = q.get("user") or ""
            correct = q["answer"]
            is_ok = 1 if your == correct else 0
            w.writerow([now, exam_id, qid, q["q"], your, correct, is_ok])

def scaled_score(correct, total):
    return int(100 + (correct / total) * 800)

def save_result_csv(correct, total, score, passed, csv_path: Path | None = None):
    csv_path = Path(csv_path) if csv_path else RESULTS_CSV
    csv_path.parent.mkdir(parents=True, exist_ok=True)  # ensure folder exists

    write_header = not csv_path.exists()
    with csv_path.open("a", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        if write_header:
            w.writerow(["Date", "Correct", "Total", "Score", "Result"])
        w.writerow([
            datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),
            correct,
            total,
            score,
            "PASS" if passed else "FAIL",
        ])

def load_questions(path):
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    qs = []
    for item in data:
        qs.append({
            "q": item["question"],
            "choices": item["options"],
            "answer": item["options"][item["answer"]],
            "user": None
        })
    if len(qs) < TOTAL_QUESTIONS:
        raise ValueError(f"Need at least {TOTAL_QUESTIONS} questions; found {len(qs)}.")
    return qs

class QuizApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("CompTIA Tech+ Practice Exam")
        self.geometry("950x640")
        self.style = ttk.Style(self)
        self.style.configure("TButton", padding=8)
        self.style.configure("TLabel", wraplength=840, justify="left")
        self.resizable(True, True)

        self.bank = load_questions(QUESTIONS_FILE)
        self.selected_questions = random.sample(self.bank, TOTAL_QUESTIONS)
        self.index = 0
        self.start_time = None
        self.time_left = TIME_LIMIT_SECONDS

        self.build_start()

    def build_start(self):
        self.clear()
        frame = ttk.Frame(self, padding=24)
        frame.pack(fill="both", expand=True)
        ttk.Label(frame, text="CompTIA Tech+ Practice Exam", font=("Segoe UI", 22, "bold")).pack(pady=10)
        intro = (f"You will answer {TOTAL_QUESTIONS} randomly-selected questions in {TIME_LIMIT_SECONDS//60} minutes.\n"
                 f"Passing score: {PASSING_SCORE}/900 (scaled).")
        ttk.Label(frame, text=intro).pack(pady=6)
        ttk.Button(frame, text="Start", command=self.start_exam).pack(pady=10)

    def start_exam(self):
        self.start_time = time.time()
        self.after(1000, self.tick)
        self.build_question()

    def tick(self):
        elapsed = int(time.time() - self.start_time)
        self.time_left = max(0, TIME_LIMIT_SECONDS - elapsed)
        if self.time_left <= 0:
            self.submit()
            return
        if hasattr(self, "timer_var"):
            m, s = divmod(self.time_left, 60)
            self.timer_var.set(f"Time remaining: {m:02d}:{s:02d}")
        self.after(1000, self.tick)

    def build_question(self):
        self.clear()
        q = self.selected_questions[self.index]

        top = ttk.Frame(self, padding=12)
        top.pack(fill="x")
        self.timer_var = tk.StringVar(value="")
        ttk.Label(top, textvariable=self.timer_var, foreground="#0a6").pack(side="right")
        ttk.Label(top, text=f"Question {self.index+1} of {TOTAL_QUESTIONS}", font=("Segoe UI", 12, "bold")).pack(side="left")
        
        body = ttk.Frame(self, padding=20)
        body.pack(fill="both", expand=True)
        ttk.Label(body, text=q["q"], font=("Segoe UI", 14)).pack(anchor="w", pady=(0,10))

        self.choice_var = tk.StringVar(value=q.get("user"))
        for choice in q["choices"]:
            ttk.Radiobutton(body, text=choice, variable=self.choice_var, value=choice).pack(anchor="w", pady=4)

        nav = ttk.Frame(self, padding=10)
        nav.pack(fill="x", side="bottom")
        ttk.Button(nav, text="Previous", command=self.prev).pack(side="left")
        ttk.Button(nav, text="Next", command=self.next).pack(side="left", padx=6)
        ttk.Button(nav, text="Submit Exam", command=self.submit).pack(side="right")

    def prev(self):
        self.save_current()
        if self.index > 0:
            self.index -= 1
            self.build_question()

    def next(self):
        self.save_current()
        if self.index < TOTAL_QUESTIONS - 1:
            self.index += 1
            self.build_question()

    def save_current(self):
        q = self.selected_questions[self.index]
        q["user"] = self.choice_var.get()

    def submit(self):
        self.save_current()
        correct = sum(1 for q in self.selected_questions if q.get("user") == q["answer"])
        score = scaled_score(correct, TOTAL_QUESTIONS)
        passed = score >= PASSING_SCORE

        # Tag this run so all 75 rows share the same exam_id
        exam_id = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")

        # Save the summary results
        try:
            save_result_csv(correct, TOTAL_QUESTIONS, score, passed)
        except Exception as e:
            messagebox.showerror("Save error", f"Could not save results summary:\n{e}")

        # Save per-question history
        try:
            save_question_history_csv(self.selected_questions, exam_id)
        except Exception as e:
            messagebox.showerror("Save error", f"Could not save question history:\n{e}")

        self.build_results(correct, score, passed)

    def build_results(self, correct, score, passed):
        self.clear()
        frame = ttk.Frame(self, padding=20)
        frame.pack(fill="both", expand=True)

        ttk.Label(frame, text="Exam Complete", font=("Segoe UI", 20, "bold")).pack(pady=10)
        ttk.Label(frame, text=f"Correct: {correct}/{TOTAL_QUESTIONS}").pack()
        ttk.Label(frame, text=f"Scaled Score (approx.): {score} / 900", font=("Segoe UI", 12, "bold")).pack(pady=5)
        verdict = "PASS 🎉" if passed else "FAIL"
        color = "#0a6" if passed else "#c00"
        ttk.Label(frame, text=verdict, font=("Segoe UI", 16, "bold"), foreground=color).pack(pady=5)

        ttk.Button(frame, text="Review Answers", command=self.build_review).pack(pady=10)
        ttk.Button(frame, text="Open Results Folder", 
                  command=lambda: os.startfile(RESULTS_DIR)).pack(pady=5)
        ttk.Button(frame, text="Exit", command=self.destroy).pack()

    def build_review(self):
        self.clear()
        container = ttk.Frame(self, padding=10)
        container.pack(fill="both", expand=True)

        left = ttk.Frame(container)
        left.pack(side="left", fill="y", padx=(0,10))
        right = ttk.Frame(container)
        right.pack(side="left", fill="both", expand=True)

        # Use Listbox instead of Text for better selection handling
        self.q_list = tk.Listbox(left, height=25, width=40)
        for i, q in enumerate(self.selected_questions, start=1):
            is_correct = q.get("user")==q["answer"]
            mark = "✓" if is_correct else "✗"
            self.q_list.insert("end", f"{i:02d} {mark}  {q['q'][:36]}{'...' if len(q['q'])>36 else ''}")
            # Color the whole line based on correctness
            self.q_list.itemconfig(i-1, fg="#0a6" if is_correct else "#c00")
        
        self.q_list.pack(fill="y")
        scrollbar = ttk.Scrollbar(left, orient="vertical", command=self.q_list.yview)
        scrollbar.pack(side="right", fill="y")
        self.q_list.configure(yscrollcommand=scrollbar.set)
        
        # Bind selection to review display
        self.q_list.bind("<<ListboxSelect>>", lambda e: self.show_review(right))

        self.review_text = tk.Text(right, wrap="word")
        self.review_text.pack(fill="both", expand=True)

        btns = ttk.Frame(self, padding=10)
        btns.pack(fill="x", side="bottom")
        ttk.Button(btns, text="Back to Start", command=self.build_start).pack(side="left")
        ttk.Button(btns, text="Exit", command=self.destroy).pack(side="right")

        # Show the first question by default
        if len(self.selected_questions) > 0:
            self.show_review_from_text(right)

    def show_review(self, right):
        sel = self.q_list.curselection()
        if not sel:
            return
        idx = sel[0]
        q = self.selected_questions[idx]
        
        self.review_text.config(state="normal")
        self.review_text.delete("1.0", "end")
        
        # Configure tags for colored results
        self.review_text.tag_configure("correct", foreground="#0a6")  # green
        self.review_text.tag_configure("incorrect", foreground="#c00")  # red
        
        # Insert question details
        self.review_text.insert("end", f"Question {idx+1}:\n{q['q']}\n\n")
        
        # Insert choices
        for c in q["choices"]:
            self.review_text.insert("end", f" - {c}\n")
            
        # Insert answers
        self.review_text.insert("end", "\nYour answer: ")
        user_answer = q.get("user") or "(no answer)"
        self.review_text.insert("end", user_answer)
        self.review_text.insert("end", "\n")
        
        self.review_text.insert("end", "Correct answer: ")
        self.review_text.insert("end", q["answer"])
        self.review_text.insert("end", "\n")
        
        # Show result with color
        ok = q.get("user") == q["answer"]
        result_mark = "✓ Correct" if ok else "✗ Incorrect"
        self.review_text.insert("end", "\nResult: ")
        self.review_text.insert("end", result_mark, "correct" if ok else "incorrect")
        self.review_text.insert("end", "\n")
        
        self.review_text.config(state="disabled")

    def clear(self):
        for w in self.winfo_children():
            w.destroy()

if __name__ == "__main__":
    app = QuizApp()
    app.mainloop()
