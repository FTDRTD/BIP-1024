import tkinter as tk
from ttkbootstrap.constants import *
import ttkbootstrap as ttk
from ttkbootstrap.dialogs import Messagebox
import os

# --- 词典：用于国际化 (i18n) ---
LANGUAGES = {
    "en": {
        "window_title": "Offline BIP39 Mnemonic Recovery Tool",
        "welcome_header": "BIP39 Mnemonic Recovery",
        "select_length_prompt": "Please select the length of your seed phrase:",
        "12_words": "12 Words",
        "18_words": "18 Words",
        "24_words": "24 Words",
        "offline_warning": "This tool is 100% offline. No data is ever sent.",
        "wordlist_file_error_title": "Wordlist File Error",
        "wordlist_not_found": "Wordlist file '{filename}' not found!\n\nPlease ensure it is in the same directory as the script.",
        "wordlist_invalid_length": "The wordlist '{filename}' is invalid.\n\nIt contains {count} words, but it must contain exactly 2048.",
        "file_read_error_title": "File Read Error",
        "file_read_error_message": "An error occurred while reading the file: {error}",
        "recovering_word_title": "Recovering Word {current} of {total}",
        "enter_number_label": "Enter number (e.g., 2, 4, 256):",
        "add_number_button": "Add Number",
        "entered_numbers_label": "Entered Numbers: {numbers}",
        "current_word_label": "Current Word: {status}",
        "status_waiting": "(waiting for input)",
        "status_invalid_index": "[Sum: {sum}] -> INVALID INDEX",
        "status_valid_word": "[Sum: {sum}] -> Index {index} -> '{word}'",
        "confirm_and_next_button": "Confirm Word & Next",
        "recovered_words_header": "Recovered Words so far:",
        "invalid_input_title": "Invalid Input",
        "invalid_input_int_warning": "Please enter a valid whole number.",
        "invalid_input_power_of_2_warning": "Please enter a valid power of 2 (1, 2, 4, ..., 1024).",
        "duplicate_input_warning": "The number {num} has already been added for this word.",
        "no_input_title": "No Input",
        "no_input_warning": "Please add at least one number for this word.",
        "sum_error_title": "Error",
        "sum_error_message": "The sum of the numbers is invalid and does not correspond to a valid word.",
        "recovery_complete_header": "Recovery Successful!",
        "your_seed_phrase_is": "Your recovered BIP39 seed phrase is:",
        "security_note": "SECURITY NOTE: Please close this window after you have secured your phrase.",
        "restart_button": "Restart",
        "quit_button": "Quit",
    },
    "zh": {
        "window_title": "离线BIP39助记词恢复工具",
        "welcome_header": "BIP39 助记词恢复",
        "select_length_prompt": "请选择您的助记词短语长度：",
        "12_words": "12个单词",
        "18_words": "18个单词",
        "24_words": "24个单词",
        "offline_warning": "本工具为100%离线工具，绝不发送任何数据。",
        "wordlist_file_error_title": "词库文件错误",
        "wordlist_not_found": "词库文件 '{filename}' 未找到！\n\n请确保该文件与脚本在同一目录下。",
        "wordlist_invalid_length": "词库文件 '{filename}' 无效。\n\n它包含 {count} 个单词，但必须是2048个。",
        "file_read_error_title": "文件读取错误",
        "file_read_error_message": "读取文件时发生错误: {error}",
        "recovering_word_title": "正在恢复第 {current} / {total} 个单词",
        "enter_number_label": "输入数字 (例如 2, 4, 256):",
        "add_number_button": "添加数字",
        "entered_numbers_label": "已输入的数字: {numbers}",
        "current_word_label": "当前单词: {status}",
        "status_waiting": "(等待输入)",
        "status_invalid_index": "[总和: {sum}] -> 无效索引",
        "status_valid_word": "[总和: {sum}] -> 索引 {index} -> '{word}'",
        "confirm_and_next_button": "确认单词并继续",
        "recovered_words_header": "已恢复的单词:",
        "invalid_input_title": "无效输入",
        "invalid_input_int_warning": "请输入一个有效的整数。",
        "invalid_input_power_of_2_warning": "请输入一个有效的2的幂（1, 2, 4, ..., 1024）。",
        "duplicate_input_warning": "数字 {num} 已经为这个单词添加过了。",
        "no_input_title": "没有输入",
        "no_input_warning": "请至少为这个单词添加一个数字。",
        "sum_error_title": "错误",
        "sum_error_message": "数字总和无效，无法对应到一个有效的单词。",
        "recovery_complete_header": "恢复成功！",
        "your_seed_phrase_is": "您恢复的BIP39助记词短语是：",
        "security_note": "【安全提示】在您安全备份好助记词后，请关闭本窗口。",
        "restart_button": "重新开始",
        "quit_button": "退出",
    },
}

# --- 配置和常量 ---
WORDLIST_FILE = "english.txt"
VALID_INPUT_NUMBERS = {2**i for i in range(11)}


class BIP39RecoveryApp:
    def __init__(self, root):
        self.root = root
        self.root.geometry("650x600")
        self.root.resizable(False, False)

        self.style = ttk.Style.get_instance()
        self.style.configure("Result.TLabel", font=("Courier", 14, "bold"))
        self.style.configure("Header.TLabel", font=("Helvetica", 18, "bold"))

        self.wordlist = self.load_wordlist()
        if not self.wordlist:
            self.root.destroy()
            return

        self.mnemonic_length = 0
        self.current_word_index = 0
        self.recovered_words = []
        self.current_word_sum = 0
        self.current_word_inputs = []

        self.current_lang = "zh"
        self.T = lambda key: LANGUAGES[self.current_lang].get(key, key)
        self.active_frame_builder = None

        self.create_welcome_frame()

    def set_language(self, lang_code):
        """设置显示语言并重绘当前框架。"""
        self.current_lang = lang_code
        self.T = lambda key: LANGUAGES[self.current_lang].get(key, key)  # 更新翻译函数
        if self.active_frame_builder:
            self.active_frame_builder()

    def load_wordlist(self):
        """从文件加载BIP39词库。"""
        if not os.path.exists(WORDLIST_FILE):
            Messagebox.show_error(
                title=LANGUAGES["en"]["wordlist_file_error_title"],
                message=LANGUAGES["en"]["wordlist_not_found"].format(
                    filename=WORDLIST_FILE
                ),
            )
            return None
        try:
            with open(WORDLIST_FILE, "r", encoding="utf-8") as f:
                words = [line.strip() for line in f if line.strip()]
            if len(words) != 2048:
                Messagebox.show_error(
                    title=LANGUAGES["en"]["wordlist_file_error_title"],
                    message=LANGUAGES["en"]["wordlist_invalid_length"].format(
                        filename=WORDLIST_FILE, count=len(words)
                    ),
                )
                return None
            return words
        except Exception as e:
            Messagebox.show_error(
                title=LANGUAGES["en"]["file_read_error_title"],
                message=LANGUAGES["en"]["file_read_error_message"].format(error=e),
            )
            return None

    def clear_frame(self):
        """从主窗口移除所有部件。"""
        for widget in self.root.winfo_children():
            widget.destroy()

    def start_recovery(self, length):
        """为指定长度开始恢复过程。"""
        self.mnemonic_length = length
        self.current_word_index = 0
        self.recovered_words = []
        self.reset_current_word()
        self.create_recovery_frame()

    def add_number(self):
        """处理输入的数字。"""
        try:
            num_str = self.number_entry.get().strip()
            if not num_str:
                return
            num = int(num_str)
            if num not in VALID_INPUT_NUMBERS:
                Messagebox.show_warning(
                    self.T("invalid_input_power_of_2_warning"),
                    self.T("invalid_input_title"),
                )
                self.number_entry.delete(0, tk.END)
                return
            if num in self.current_word_inputs:
                Messagebox.show_warning(
                    self.T("duplicate_input_warning").format(num=num),
                    self.T("invalid_input_title"),
                )
            else:
                self.current_word_inputs.append(num)
                self.current_word_sum += num
            self.number_entry.delete(0, tk.END)
            self.update_recovery_display()
        except ValueError:
            Messagebox.show_warning(
                self.T("invalid_input_int_warning"), self.T("invalid_input_title")
            )
            self.number_entry.delete(0, tk.END)

    def process_next_word(self):
        """确认当前单词并处理下一个。"""
        if self.current_word_sum == 0:
            Messagebox.show_warning(
                self.T("no_input_warning"), self.T("no_input_title")
            )
            return
        word_index = self.current_word_sum - 1
        if 0 <= word_index < 2048:
            word = self.wordlist[word_index]
            self.recovered_words.append(word)
            self.current_word_index += 1
            if self.current_word_index >= self.mnemonic_length:
                self.show_final_result()
            else:
                self.reset_current_word()
                self.update_recovery_display()
        else:
            Messagebox.show_error(
                self.T("sum_error_message"), self.T("sum_error_title")
            )

    def reset_current_word(self):
        """重置状态以输入下一个单词。"""
        self.current_word_sum = 0
        self.current_word_inputs = []

    def create_language_switcher(self, parent_frame):
        """创建语言切换按钮。"""
        lang_frame = ttk.Frame(parent_frame)
        lang_frame.pack(anchor="ne", padx=10, pady=5)

        en_button = ttk.Button(
            lang_frame,
            text="English",
            bootstyle="outline-secondary",
            command=lambda: self.set_language("en"),
        )
        en_button.pack(side="left", padx=5)

        zh_button = ttk.Button(
            lang_frame,
            text="中文",
            bootstyle="outline-secondary",
            command=lambda: self.set_language("zh"),
        )
        zh_button.pack(side="left")

    def create_welcome_frame(self):
        """显示初始的助记词长度选择屏幕。"""
        self.active_frame_builder = self.create_welcome_frame
        self.clear_frame()
        self.root.title(self.T("window_title"))

        self.create_language_switcher(self.root)
        frame = ttk.Frame(self.root, padding="40 20")
        frame.pack(expand=True, fill="both")

        ttk.Label(frame, text=self.T("welcome_header"), style="Header.TLabel").pack(
            pady=(0, 30)
        )
        ttk.Label(frame, text=self.T("select_length_prompt"), wraplength=500).pack(
            pady=10
        )

        ttk.Button(
            frame,
            text=self.T("12_words"),
            bootstyle="primary-outline",
            command=lambda: self.start_recovery(12),
        ).pack(pady=10, fill="x", ipady=5)
        ttk.Button(
            frame,
            text=self.T("18_words"),
            bootstyle="primary-outline",
            command=lambda: self.start_recovery(18),
        ).pack(pady=10, fill="x", ipady=5)
        ttk.Button(
            frame,
            text=self.T("24_words"),
            bootstyle="primary-outline",
            command=lambda: self.start_recovery(24),
        ).pack(pady=10, fill="x", ipady=5)

        ttk.Label(frame, text=self.T("offline_warning"), bootstyle="secondary").pack(
            side=BOTTOM, pady=20
        )

    def create_recovery_frame(self):
        """创建用于输入数字的主GUI。"""
        self.active_frame_builder = self.create_recovery_frame
        self.clear_frame()
        self.root.title(self.T("window_title"))
        self.create_language_switcher(self.root)

        frame = ttk.Frame(self.root, padding="40 20")
        frame.pack(expand=True, fill="both")

        self.title_label = ttk.Label(frame, text="", style="Header.TLabel")
        self.title_label.pack(pady=(0, 20))

        input_frame = ttk.Frame(frame)
        input_frame.pack(fill="x", pady=10)
        self.enter_num_label = ttk.Label(input_frame, text="")
        self.enter_num_label.pack(side="left", padx=(0, 10))
        self.number_entry = ttk.Entry(input_frame, font=("Helvetica", 12), width=10)
        self.number_entry.pack(side="left", fill="x", expand=True)
        self.add_button = ttk.Button(
            input_frame, text="", command=self.add_number, bootstyle="success"
        )
        self.add_button.pack(side="left", padx=(10, 0))
        self.root.bind("<Return>", lambda event: self.add_number())

        self.current_inputs_label = ttk.Label(frame, text="", wraplength=550)
        self.current_inputs_label.pack(anchor="w", pady=10)
        self.current_word_label = ttk.Label(frame, text="", style="Result.TLabel")
        self.current_word_label.pack(anchor="w", pady=10)

        self.next_word_button = ttk.Button(
            frame, text="", command=self.process_next_word, bootstyle="primary"
        )
        self.next_word_button.pack(pady=20, fill="x", ipady=5)

        self.recovered_words_header_label = ttk.Label(frame, text="")
        self.recovered_words_header_label.pack(anchor="w", pady=(20, 5))
        self.recovered_words_display = tk.Text(
            frame,
            height=5,
            width=60,
            font=("Courier", 11),
            wrap="word",
            relief="solid",
            borderwidth=1,
        )
        self.recovered_words_display.pack(fill="x")
        self.recovered_words_display.config(state="disabled")

        self.update_ui_texts()
        self.update_recovery_display()
        self.number_entry.focus()

    def update_ui_texts(self):
        """更新恢复视图中的所有静态文本。"""
        self.enter_num_label.config(text=self.T("enter_number_label"))
        self.add_button.config(text=self.T("add_number_button"))
        self.next_word_button.config(text=self.T("confirm_and_next_button"))
        self.recovered_words_header_label.config(text=self.T("recovered_words_header"))

    def update_recovery_display(self):
        """更新GUI中所有动态标签和显示。"""
        title_text = self.T("recovering_word_title").format(
            current=self.current_word_index + 1, total=self.mnemonic_length
        )
        self.title_label.config(text=title_text)

        inputs_str = ", ".join(map(str, sorted(self.current_word_inputs)))
        self.current_inputs_label.config(
            text=self.T("entered_numbers_label").format(numbers=inputs_str)
        )

        status_text = ""
        if self.current_word_sum > 0:
            word_index = self.current_word_sum - 1
            if 0 <= word_index < 2048:
                word = self.wordlist[word_index]
                status_text = self.T("status_valid_word").format(
                    sum=self.current_word_sum, index=word_index + 1, word=word
                )
            else:
                status_text = self.T("status_invalid_index").format(
                    sum=self.current_word_sum
                )
        else:
            status_text = self.T("status_waiting")
        self.current_word_label.config(
            text=self.T("current_word_label").format(status=status_text)
        )

        self.recovered_words_display.config(state="normal")
        self.recovered_words_display.delete("1.0", tk.END)
        self.recovered_words_display.insert("1.0", " ".join(self.recovered_words))
        self.recovered_words_display.config(state="disabled")

    def show_final_result(self):
        """显示最终恢复的短语。"""
        self.active_frame_builder = self.show_final_result
        self.clear_frame()
        self.root.title(self.T("window_title"))
        self.create_language_switcher(self.root)

        frame = ttk.Frame(self.root, padding="40 20")
        frame.pack(expand=True, fill="both")

        ttk.Label(
            frame, text=self.T("recovery_complete_header"), style="Header.TLabel"
        ).pack(pady=20)
        ttk.Label(frame, text=self.T("your_seed_phrase_is")).pack(pady=10)

        result_text = tk.Text(
            frame,
            height=6,
            width=60,
            font=("Courier", 12),
            wrap="word",
            relief="solid",
            borderwidth=1,
        )
        result_text.insert("1.0", " ".join(self.recovered_words))
        result_text.config(state="disabled")
        result_text.pack(pady=10)

        ttk.Label(frame, text=self.T("security_note"), bootstyle="danger").pack(pady=20)

        ttk.Button(
            frame,
            text=self.T("restart_button"),
            command=self.create_welcome_frame,
            bootstyle="info",
        ).pack(pady=10, fill="x", ipady=5)
        ttk.Button(
            frame,
            text=self.T("quit_button"),
            command=self.root.quit,
            bootstyle="secondary",
        ).pack(pady=5, fill="x", ipady=5)


if __name__ == "__main__":
    # 使用 ttkbootstrap.Window 创建带主题的窗口
    # 可用亮色主题: litera, cosmo, flatly, journal, lumen, minty, pulse, sandstone, united, yeti
    # 可用暗色主题: darkly, superhero, solar, cyborg
    root = ttk.Window(themename="litera")
    app = BIP39RecoveryApp(root)
    root.mainloop()
