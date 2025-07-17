import os
import random
import tkinter as tk
from tkinter import ttk, messagebox, filedialog

class Word:
    def __init__(self, jp, kana, ch, partOfSpeech):
        self.jp = jp
        if kana == jp or kana[0].isascii():
            self.kana = jp
            self.jp = ""
        else:
            self.kana = kana
        self.ch = ch
        self.partOfSpeech = partOfSpeech if partOfSpeech != "."  else ""
    def __str__(self):
        return f"{self.jp}, {self.kana}, {self.ch}, {self.partOfSpeech}"

class Flashcards:
    INIT = 0
    LOADING = 1
    READY = 2
    QUIZ= 3
    FINISH= 4

    @staticmethod
    def load_vocabulary(path):
        words = []
        with open(path, encoding="utf-8", mode="r") as file:
            lines = file.read().splitlines()
            for line in lines[1:]:
                try:
                    new_word = Word(*line.replace(' ', '').split(","))
                except:
                    messagebox.showerror("Error", f"{os.path.split(path)[1]}讀取失敗")
                    return []
                words.append(new_word)
        return words

    def __init__(self):
        self.init_state()
        self.create_window_elements()
        self.refresh()

    def init_state(self):
        self.state = Flashcards.INIT
        self.current_number_of_quiz = 0
        self.total_numberr_of_quiz = 0
        self.correct = 0
        self.wrong = 0
        self.hint = False
        self.shuffle = True
        self.words = []
        self.wrong_words = []

    def create_window_elements(self):
        self.window_root = tk.Tk()
        self.window_root.title("單字練習器")
        width, height = 800, 350
        screen_width = self.window_root.winfo_screenwidth()
        screen_height = self.window_root.winfo_screenheight()
        x = (screen_width - width) // 2
        y = (screen_height - height) // 2
        self.window_root.geometry(f'{width}x{height}+{x}+{y}')

        # 功能區
        self.load_button = tk.Button(self.window_root, text="選取表格", font=("Arial", 18, "bold"), command=self.select_files)
        self.load_button.place(relx=0.05, rely=0.01)
        self.start_button = tk.Button(self.window_root, text="顯示單字", font=("Arial", 18, "bold"), command=self.show_selected_words)
        self.start_button.place(relx=0.25, rely=0.01)
        self.start_button = tk.Button(self.window_root, text="開始作答", font=("Arial", 18, "bold"), command=self.start_quiz)
        self.start_button.place(relx=0.45, rely=0.01)
        self.restart_button = tk.Button(self.window_root, text="錯誤練習", font=("Arial", 18, "bold"), command=self.restart_quiz)
        self.restart_button.place(relx=0.65, rely=0.01)
        self.shuffle_check = tk.Checkbutton(self.window_root, text="單字亂序", font=("Arial", 18, "bold"), command=self.toggle_shuffle)
        self.shuffle_check.place(relx=0.83, rely=0.03)
        self.shuffle_check.select()

        # 統計區
        self.total_question_title = tk.Label(self.window_root, text="總題數:", font=("Arial", 20, "bold"))
        self.total_question_title.place(relx=0.01, rely=0.2)
        self.total_question_counter = tk.Label(self.window_root, text=f"{0:03d}", font=("Arial", 20, "bold"))
        self.total_question_counter.place(relx=0.15, rely=0.2)
    
        self.answered_question_title = tk.Label(self.window_root, text="已作答:", font=("Arial", 20, "bold"))
        self.answered_question_title.place(relx=0.01, rely=0.35)
        self.answered_question_counter = tk.Label(self.window_root, text=f"{0:03d}", font=("Arial", 20, "bold"))
        self.answered_question_counter.place(relx=0.15, rely=0.35)

        self.correct_title = tk.Label(self.window_root, text="正確:", font=("Arial", 20, "bold"))
        self.correct_title.place(relx=0.8, rely=0.2)
        self.correct_counter = tk.Label(self.window_root, text=f"{0:03d}", font=("Arial", 20, "bold"))
        self.correct_counter.place(relx=0.9, rely=0.2)

        self.worng_title = tk.Label(self.window_root, text="錯誤:", font=("Arial", 20, "bold"))
        self.worng_title.place(relx=0.8, rely=0.35)
        self.worng_counter = tk.Label(self.window_root, text=f"{0:03d}", font=("Arial", 20, "bold"))
        self.worng_counter.place(relx=0.9, rely=0.35)

        # 題目區
        self.ch_title = tk.Label(self.window_root, text=f"中文:", font=('Arial',20,'bold'))
        self.ch_title.place(relx=0.01, rely=0.55)
        self.ch_question = tk.Label(self.window_root, text=f"?????", font=('Arial',20,'bold'))
        self.ch_question.place(relx=0.1, rely=0.55)
        self.giveup_button = tk.Button(self.window_root, text="放棄作答", font=('Arial',15,'bold'), command=self.giveup)
        self.giveup_button.place(relx=0.8, rely=0.53)
        # 提示區
        self.jp_title = tk.Label(self.window_root, text=f"日文:", font=('Arial',20,'bold'))
        self.jp_title.place(relx=0.01, rely=0.7)
        self.jp_question = tk.Label(self.window_root, text=f"?????", font=('Arial',20,'bold'))
        self.jp_question.place(relx=0.1, rely=0.7)
        self.hint_button = tk.Button(self.window_root, text="顯示日文", font=('Arial',15,'bold'), command=self.update_hint)
        self.hint_button.place(relx=0.8, rely=0.68)

        # 作答區
        self.kana_title = tk.Label(self.window_root, text=f"假名:", font=('Arial',20,'bold'))
        self.kana_title.place(relx=0.01, rely=0.85)
        self.answer_box = tk.Entry(self.window_root, width=20, font=('Arial',20,'bold'))
        self.answer_box.bind("<Return>", lambda event: self.validate())
        self.answer_box.bind("<Shift_L>", lambda event: self.update_hint())
        self.answer_box.bind("<Shift_R>", lambda event: self.update_hint())
        self.answer_box.place(relx=0.12, rely=0.85)
        self.compare_button = tk.Button(self.window_root, text="送出答案", font=('Arial',15,'bold'), command=self.validate)
        self.compare_button.place(relx=0.8, rely=0.83)

    def refresh(self):
        self.total_question_counter["text"] = f"{self.total_numberr_of_quiz:3d}"
        self.answered_question_counter["text"] = f"{self.current_number_of_quiz:3d}"
        self.correct_counter["text"] = f"{self.correct:3d}"
        self.worng_counter["text"] = f"{self.wrong:3d}"
        self.answer_box.delete(0, 'end')
        if self.state != Flashcards.QUIZ:
            self.ch_question["text"] = ""
            self.jp_question["text"] = ""
        else:
            self.ch_question["text"] = self.words[self.current_number_of_quiz].ch
            if self.words[self.current_number_of_quiz].partOfSpeech != "":
                self.ch_question["text"] += f"({self.words[self.current_number_of_quiz].partOfSpeech})"

            if self.words[self.current_number_of_quiz].jp == "":
                self.hint_button.config(state="disabled")
            else:
                self.hint_button.config(state="normal")
            if self.hint:
                self.jp_question["text"] = self.words[self.current_number_of_quiz].jp
                self.hint_button["text"] = "隱藏日文"
            else:
                self.jp_question["text"] = ""
                self.hint_button["text"] = "顯示日文"

    def show_selected_words(self):
        if self.state == Flashcards.READY:
            self.show_words(self.words)

    def show_wrong_words(self):
        if self.state == Flashcards.FINISH:
            self.show_words(self.wrong_words)

    def show_words(self, words):
        if len(words) == 0:
            return

        root = tk.Toplevel(self.window_root)
        root.title("錯誤單字")
        width, height = 800, 300
        screen_width = self.window_root.winfo_screenwidth()
        screen_height = self.window_root.winfo_screenheight()
        x = (screen_width - width) // 2
        y = (screen_height - height) // 2
        root.geometry(f'{width}x{height}+{x}+{y}')

        frame = tk.Frame(root)
        frame.pack(fill=tk.BOTH, expand=True)

        columns = ("日文", "假名", "中文", "詞性")
        tree = ttk.Treeview(frame, columns=columns, show="headings")
        style = ttk.Style()
        style.configure("Treeview.Heading", font=("Arial", 22, "bold"), rowheight=30)
        style.configure("Treeview", font=("Arial", 18, "bold"), rowheight=30)
        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=140, anchor="center")
        scrollbar = ttk.Scrollbar(frame, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)

        for word in words:
            tree.insert("", tk.END, values=(word.jp, word.kana, word.ch, word.partOfSpeech))
        tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        root.mainloop()

    def select_files(self):
        file_paths = filedialog.askopenfilenames(filetypes=[("單字表", ".csv")], initialdir=os.getcwd())
        if len(file_paths) == 0:
            return

        self.init_state()
        self.state = Flashcards.LOADING
        for file_path in file_paths:
            self.words.extend(Flashcards.load_vocabulary(file_path))
        self.total_numberr_of_quiz = len(self.words)
        if self.total_numberr_of_quiz != 0:
            self.state = Flashcards.READY
        self.refresh()

    def giveup(self):
        self.load_button.config(state="normal")
        self.shuffle_check.config(state="normal")
        self.init_state()
        self.refresh()

    def start_quiz(self):
        if self.state == Flashcards.READY:        
            self.state = Flashcards.QUIZ
            self.shuffle_check.config(state="disabled")
            self.load_button.config(state="disabled")
            if self.shuffle:
                random.shuffle(self.words)
            self.show_question()
        if self.state == Flashcards.INIT:        
            messagebox.showinfo("Info", f"請先選取表格")

    def restart_quiz(self):
        if self.state != Flashcards.FINISH or self.wrong_words == []:
            messagebox.showinfo("Info", f"沒有錯誤題目")
            return
        temp = self.wrong_words
        self.init_state()

        self.words = temp
        self.total_numberr_of_quiz = len(self.words)
        self.state = Flashcards.READY
        self.start_quiz()

    def show_question(self):
        if self.current_number_of_quiz == self.total_numberr_of_quiz:
            self.state = Flashcards.FINISH
        self.hint= False
        self.refresh()
        if self.state == Flashcards.FINISH:
            self.load_button.config(state="normal")
            self.shuffle_check.config(state="normal")
            self.show_wrong_words()

    def update_hint(self):
        if self.state != Flashcards.QUIZ or self.words[self.current_number_of_quiz].jp == "":
            return
        self.hint = not self.hint
        self.refresh()

    def toggle_shuffle(self):
        if self.state != Flashcards.QUIZ:
            self.shuffle = not self.shuffle

    def validate(self):
        if self.state != Flashcards.QUIZ:
            return
        response = self.answer_box.get()
        answer = self.words[self.current_number_of_quiz].kana
        if response == answer:
            self.correct += 1
        else:
            self.wrong += 1
            self.wrong_words.append(self.words[self.current_number_of_quiz])

        self.current_number_of_quiz += 1
        self.show_question()

    def main(self):
        self.window_root.mainloop()

if __name__ == "__main__":
    cards = Flashcards()
    cards.main()