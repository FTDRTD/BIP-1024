import os
import sys

# --- Import PySide6 components ---
from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QLabel,
    QLineEdit,
    QTextEdit,
    QStackedWidget,
    QMessageBox,
)
from PySide6.QtGui import QFont, QIcon
from PySide6.QtCore import Qt, QSize

# --- 词典：用于国际化 (i18n) - Unchanged ---
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

# --- 配置和常量 - Unchanged ---
WORDLIST_FILE = "english.txt"
VALID_INPUT_NUMBERS = {2**i for i in range(11)}


# --- 资源路径函数 - Unchanged ---
def get_resource_path(relative_path):
    """获取资源文件的绝对路径，兼容打包后的情况"""
    if hasattr(sys, "_MEIPASS"):
        return os.path.join(sys._MEIPASS, relative_path)
    try:
        base_path = os.path.dirname(os.path.abspath(__file__))
    except NameError:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)


class BIP39RecoveryApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.wordlist = self.load_wordlist()
        if not self.wordlist:
            sys.exit(1)  # Exit if wordlist fails to load

        # --- Application State ---
        self.mnemonic_length = 0
        self.current_word_index = 0
        self.recovered_words = []
        self.current_word_sum = 0
        self.current_word_inputs = []
        self.current_lang = "zh"
        self.T = lambda key: LANGUAGES[self.current_lang].get(key, key)

        # --- UI Setup ---
        self.setFixedSize(650, 600)
        self.setup_styles()

        self.stacked_widget = QStackedWidget()
        self.setCentralWidget(self.stacked_widget)

        # --- Create Pages ---
        self.welcome_widget = QWidget()
        self.recovery_widget = QWidget()
        self.result_widget = QWidget()

        self.create_welcome_page()
        self.create_recovery_page()
        self.create_result_page()

        self.stacked_widget.addWidget(self.welcome_widget)
        self.stacked_widget.addWidget(self.recovery_widget)
        self.stacked_widget.addWidget(self.result_widget)

        self.update_ui_text()

    def show_message(self, level, title, message):
        """Helper to show QMessageBox."""
        box = QMessageBox(self)
        box.setWindowTitle(title)
        box.setText(message)
        if level == "error":
            box.setIcon(QMessageBox.Icon.Critical)
        elif level == "warning":
            box.setIcon(QMessageBox.Icon.Warning)
        else:
            box.setIcon(QMessageBox.Icon.Information)
        box.exec()

    def load_wordlist(self):
        """从文件加载BIP39词库。"""
        wordlist_path = get_resource_path(WORDLIST_FILE)
        if not os.path.exists(wordlist_path):
            self.show_message(
                "error",
                LANGUAGES["en"]["wordlist_file_error_title"],
                LANGUAGES["en"]["wordlist_not_found"].format(filename=WORDLIST_FILE),
            )
            return None
        try:
            with open(wordlist_path, "r", encoding="utf-8") as f:
                words = [line.strip() for line in f if line.strip()]
            if len(words) != 2048:
                self.show_message(
                    "error",
                    LANGUAGES["en"]["wordlist_file_error_title"],
                    LANGUAGES["en"]["wordlist_invalid_length"].format(
                        filename=WORDLIST_FILE, count=len(words)
                    ),
                )
                return None
            return words
        except Exception as e:
            self.show_message(
                "error",
                LANGUAGES["en"]["file_read_error_title"],
                LANGUAGES["en"]["file_read_error_message"].format(error=e),
            )
            return None

    def setup_styles(self):
        """Apply global styles using QSS."""
        self.setStyleSheet("""
            QWidget {
                font-family: 'Segoe UI', 'Microsoft YaHei', 'Helvetica';
                font-size: 14px;
            }
            QLabel#HeaderLabel {
                font-size: 24px;
                font-weight: bold;
            }
            QLabel#ResultLabel {
                font-family: 'Courier New', 'monospace';
                font-size: 18px;
                font-weight: bold;
                color: #005a9e;
            }
            QLabel#ErrorLabel {
                color: #D32F2F;
            }
            QPushButton {
                padding: 10px;
                border: 1px solid #ADADAD;
                border-radius: 4px;
                background-color: #F0F0F0;
            }
            QPushButton:hover {
                background-color: #E0E0E0;
            }
            QPushButton#PrimaryButton {
                background-color: #0078D7;
                color: white;
                border: none;
            }
            QPushButton#PrimaryButton:hover {
                background-color: #005a9e;
            }
            QLineEdit, QTextEdit {
                border: 1px solid #ADADAD;
                border-radius: 4px;
                padding: 5px;
            }
            QTextEdit {
                font-family: 'Courier New', monospace;
            }
        """)

    # --- Page Creation ---

    def create_language_switcher(self, layout):
        """Creates and adds a language switcher to the given layout."""
        lang_layout = QHBoxLayout()
        lang_layout.addStretch()  # Pushes buttons to the right

        en_button = QPushButton("English")
        en_button.setFixedSize(80, 30)
        en_button.clicked.connect(lambda: self.set_language("en"))
        lang_layout.addWidget(en_button)

        zh_button = QPushButton("中文")
        zh_button.setFixedSize(80, 30)
        zh_button.clicked.connect(lambda: self.set_language("zh"))
        lang_layout.addWidget(zh_button)

        layout.addLayout(lang_layout)

    def create_welcome_page(self):
        layout = QVBoxLayout(self.welcome_widget)
        layout.setContentsMargins(40, 20, 40, 20)
        layout.setSpacing(15)

        self.create_language_switcher(layout)
        layout.addStretch(1)  # Add space

        self.welcome_header = QLabel()
        self.welcome_header.setObjectName("HeaderLabel")
        self.welcome_header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.welcome_header)

        self.select_prompt = QLabel()
        self.select_prompt.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.select_prompt)
        layout.addSpacing(20)

        self.button12 = QPushButton()
        self.button12.clicked.connect(lambda: self.start_recovery(12))
        layout.addWidget(self.button12)

        self.button18 = QPushButton()
        self.button18.clicked.connect(lambda: self.start_recovery(18))
        layout.addWidget(self.button18)

        self.button24 = QPushButton()
        self.button24.clicked.connect(lambda: self.start_recovery(24))
        layout.addWidget(self.button24)

        layout.addStretch(2)

        self.offline_warning = QLabel()
        self.offline_warning.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.offline_warning.setStyleSheet("color: grey;")
        layout.addWidget(self.offline_warning)

    def create_recovery_page(self):
        layout = QVBoxLayout(self.recovery_widget)
        layout.setContentsMargins(40, 20, 40, 20)

        self.create_language_switcher(layout)

        self.recovery_title_label = QLabel()
        self.recovery_title_label.setObjectName("HeaderLabel")
        layout.addWidget(self.recovery_title_label)

        # Input Frame
        input_layout = QHBoxLayout()
        self.enter_num_label = QLabel()
        input_layout.addWidget(self.enter_num_label)
        self.number_entry = QLineEdit()
        self.number_entry.setFixedWidth(120)
        self.number_entry.returnPressed.connect(self.add_number)  # Enter key submits
        input_layout.addWidget(self.number_entry)
        self.add_button = QPushButton()
        self.add_button.setObjectName("PrimaryButton")
        self.add_button.clicked.connect(self.add_number)
        input_layout.addWidget(self.add_button)
        input_layout.addStretch()
        layout.addLayout(input_layout)

        self.current_inputs_label = QLabel()
        self.current_inputs_label.setWordWrap(True)
        layout.addWidget(self.current_inputs_label)

        self.current_word_label = QLabel()
        self.current_word_label.setObjectName("ResultLabel")
        layout.addWidget(self.current_word_label)

        self.next_word_button = QPushButton()
        self.next_word_button.setObjectName("PrimaryButton")
        self.next_word_button.clicked.connect(self.process_next_word)
        layout.addWidget(self.next_word_button)

        layout.addSpacing(20)

        self.recovered_words_header_label = QLabel()
        layout.addWidget(self.recovered_words_header_label)

        self.recovered_words_display = QTextEdit()
        self.recovered_words_display.setReadOnly(True)
        self.recovered_words_display.setFixedHeight(120)
        layout.addWidget(self.recovered_words_display)

        layout.addStretch()

    def create_result_page(self):
        layout = QVBoxLayout(self.result_widget)
        layout.setContentsMargins(40, 20, 40, 20)
        layout.setSpacing(15)

        self.create_language_switcher(layout)
        layout.addStretch(1)

        self.result_header = QLabel()
        self.result_header.setObjectName("HeaderLabel")
        self.result_header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.result_header)

        self.result_prompt = QLabel()
        self.result_prompt.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.result_prompt)

        self.result_text = QTextEdit()
        self.result_text.setReadOnly(True)
        self.result_text.setFixedHeight(150)
        layout.addWidget(self.result_text)

        self.security_note = QLabel()
        self.security_note.setObjectName("ErrorLabel")
        self.security_note.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.security_note)

        layout.addStretch(1)

        self.restart_button = QPushButton()
        self.restart_button.clicked.connect(
            lambda: self.stacked_widget.setCurrentWidget(self.welcome_widget)
        )
        layout.addWidget(self.restart_button)

        self.quit_button = QPushButton()
        self.quit_button.clicked.connect(self.close)
        layout.addWidget(self.quit_button)

    # --- Logic & Control ---

    def set_language(self, lang_code):
        """Sets display language and updates all UI text."""
        self.current_lang = lang_code
        self.T = lambda key: LANGUAGES[self.current_lang].get(key, key)
        self.update_ui_text()

    def update_ui_text(self):
        """Update all text elements in the UI based on the current language."""
        self.setWindowTitle(self.T("window_title"))

        # Welcome Page
        self.welcome_header.setText(self.T("welcome_header"))
        self.select_prompt.setText(self.T("select_length_prompt"))
        self.button12.setText(self.T("12_words"))
        self.button18.setText(self.T("18_words"))
        self.button24.setText(self.T("24_words"))
        self.offline_warning.setText(self.T("offline_warning"))

        # Recovery Page
        self.enter_num_label.setText(self.T("enter_number_label"))
        self.add_button.setText(self.T("add_number_button"))
        self.next_word_button.setText(self.T("confirm_and_next_button"))
        self.recovered_words_header_label.setText(self.T("recovered_words_header"))
        self.update_recovery_display()  # Update dynamic text

        # Result Page
        self.result_header.setText(self.T("recovery_complete_header"))
        self.result_prompt.setText(self.T("your_seed_phrase_is"))
        self.security_note.setText(self.T("security_note"))
        self.restart_button.setText(self.T("restart_button"))
        self.quit_button.setText(self.T("quit_button"))

    def start_recovery(self, length):
        """Starts the recovery process for a given mnemonic length."""
        self.mnemonic_length = length
        self.current_word_index = 0
        self.recovered_words = []
        self.reset_current_word()
        self.update_recovery_display()
        self.stacked_widget.setCurrentWidget(self.recovery_widget)
        self.number_entry.setFocus()

    def add_number(self):
        """Processes the number entered by the user."""
        try:
            num_str = self.number_entry.text().strip()
            if not num_str:
                return
            num = int(num_str)

            if num not in VALID_INPUT_NUMBERS:
                self.show_message(
                    "warning",
                    self.T("invalid_input_title"),
                    self.T("invalid_input_power_of_2_warning"),
                )
                self.number_entry.clear()
                return

            if num in self.current_word_inputs:
                self.show_message(
                    "warning",
                    self.T("invalid_input_title"),
                    self.T("duplicate_input_warning").format(num=num),
                )
            else:
                self.current_word_inputs.append(num)
                self.current_word_sum += num

            self.number_entry.clear()
            self.update_recovery_display()
        except ValueError:
            self.show_message(
                "warning",
                self.T("invalid_input_title"),
                self.T("invalid_input_int_warning"),
            )
            self.number_entry.clear()

    def process_next_word(self):
        """Confirms the current word and moves to the next one."""
        if not self.current_word_inputs:
            self.show_message(
                "warning", self.T("no_input_title"), self.T("no_input_warning")
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
            self.show_message(
                "error", self.T("sum_error_title"), self.T("sum_error_message")
            )

    def reset_current_word(self):
        """Resets the state for recovering the next word."""
        self.current_word_sum = 0
        self.current_word_inputs = []
        self.number_entry.clear()

    def update_recovery_display(self):
        """Updates all dynamic labels on the recovery page."""
        title_text = self.T("recovering_word_title").format(
            current=self.current_word_index + 1, total=self.mnemonic_length
        )
        self.recovery_title_label.setText(title_text)

        inputs_str = ", ".join(map(str, sorted(self.current_word_inputs)))
        self.current_inputs_label.setText(
            self.T("entered_numbers_label").format(numbers=inputs_str)
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
        self.current_word_label.setText(
            self.T("current_word_label").format(status=status_text)
        )

        self.recovered_words_display.setPlainText(" ".join(self.recovered_words))

    def show_final_result(self):
        """Displays the fully recovered mnemonic phrase."""
        final_phrase = " ".join(self.recovered_words)
        self.result_text.setPlainText(final_phrase)
        self.stacked_widget.setCurrentWidget(self.result_widget)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = BIP39RecoveryApp()
    window.show()
    sys.exit(app.exec())
