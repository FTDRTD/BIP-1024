# main.py
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import mm
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics
import os

# --- 字体设置 ---
# 使用 DejaVu 字体以完美显示 ● 和 ○ 符号。
FONT_FILE_REGULAR = "DejaVuSans.ttf"
FONT_FILE_BOLD = "DejaVuSans-Bold.ttf"
FONT_NAME = "DejaVuSans"
FONT_NAME_BOLD = "DejaVuSans-Bold"

try:
    if not os.path.exists(FONT_FILE_REGULAR) or not os.path.exists(FONT_FILE_BOLD):
        raise FileNotFoundError()

    pdfmetrics.registerFont(TTFont(FONT_NAME, FONT_FILE_REGULAR))
    pdfmetrics.registerFont(TTFont(FONT_NAME_BOLD, FONT_FILE_BOLD))
    print(f"成功加载字体文件: {FONT_FILE_REGULAR}, {FONT_FILE_BOLD}")

except FileNotFoundError:
    print(f"错误：字体文件 'DejaVuSans.ttf' 或 'DejaVuSans-Bold.ttf' 未找到！")
    print("请确保这些文件和 main.py 在同一个文件夹下。")
    FONT_NAME = "Helvetica"
    FONT_NAME_BOLD = "Helvetica-Bold"
except Exception as e:
    print(f"加载字体时发生未知错误: {e}")
    FONT_NAME = "Helvetica"
    FONT_NAME_BOLD = "Helvetica-Bold"


def number_to_dotmap(n: int, bits_count: int):
    """将单词索引号 n 转换为指定位数二进制的点图 (为手动解码优化)"""
    # 1. 生成标准的 bits_count 位二进制字符串 (高位在前)
    bits = bin(n)[2:].zfill(bits_count)

    # 2. 【关键】将二进制字符串反转，以实现 1 -> 2^(bits_count-1) 的顺序 (低位在前)
    reversed_bits = bits[::-1]

    # 3. 根据反转后的字符串生成点图
    dots = ["●" if b == "1" else "○" for b in reversed_bits]

    # 根据位数调整分栏
    if bits_count == 12:
        col1 = "".join(dots[0:4])
        col2 = "".join(dots[4:8])
        col3 = "".join(dots[8:12])
    elif bits_count == 11:
        col1 = "".join(dots[0:4])
        col2 = "".join(dots[4:8])
        col3 = "".join(dots[8:11])
    else:  # Fallback for other bit counts
        col1 = "".join(dots[0:4])
        col2 = "".join(dots[4:8])
        col3 = "".join(dots[8:])
    return col1, col2, col3


def generate_pdf(words, mode, output_file="bip39_dotmap_for_engraving.pdf"):
    """为物理雕刻和手动恢复场景，生成优化后的 PDF"""
    c = canvas.Canvas(output_file, pagesize=A4)
    width, height = A4

    bits_count = 12 if mode == 2048 else 11

    x_margin = 20 * mm
    y_margin = 20 * mm
    line_height = 5 * mm

    y = height - y_margin
    c.setFont(FONT_NAME_BOLD, 16)
    c.drawString(x_margin, y, f"BIP39 Mnemonic DotMap ({mode} words, {bits_count} dots)")
    y -= 12 * mm

    text = c.beginText(x_margin, y)
    text.setFont(FONT_NAME, 10)
    text.setLeading(14)

    text.textLine("The meaning of each dot is as follows:")
    text.textLine("  ● (Solid Dot)   represents a 1 (the weight is selected)")
    text.textLine("  ○ (Hollow Dot)  represents a 0 (the weight is not selected)")
    text.textLine(" ")

    # 【关键】更新说明文字，明确指出这是为手动累加优化的顺序
    text.textLine(
        f"FOR EASY MANUAL CALCULATION, the {bits_count} dot positions are ordered from LOWEST to HIGHEST weight:"
    )

    text.setFont(FONT_NAME_BOLD, 9)
    # 生成权重说明
    weights = [str(2**i) for i in range(bits_count)]
    if bits_count == 12:
        weights_str = f"     {' | '.join(weights[0:4])} || {' | '.join(weights[4:8])} || {' | '.join(weights[8:12])}"
    elif bits_count == 11:
        weights_str = f"     {' | '.join(weights[0:4])} || {' | '.join(weights[4:8])} || {' | '.join(weights[8:11])}"
    else:
        weights_str = " | ".join(weights)
    text.textLine(weights_str)

    c.drawText(text)
    y = text.getY() - 10 * mm

    font_size = 9
    x_index = x_margin
    x_word = x_margin + 18 * mm
    x_col1 = x_margin + 55 * mm
    x_col2 = x_margin + 85 * mm
    x_col3 = x_margin + 115 * mm

    def draw_header(y_pos):
        c.setFont(FONT_NAME_BOLD, font_size)
        c.drawString(x_index, y_pos, "Index")
        c.drawString(x_word, y_pos, "Word")
        if bits_count == 12:
            c.drawString(x_col1, y_pos, "Dots 1-4")
            c.drawString(x_col2, y_pos, "Dots 5-8")
            c.drawString(x_col3, y_pos, "Dots 9-12")
        elif bits_count == 11:
            c.drawString(x_col1, y_pos, "Dots 1-4")
            c.drawString(x_col2, y_pos, "Dots 5-8")
            c.drawString(x_col3, y_pos, "Dots 9-11")
        else:
            c.drawString(x_col1, y_pos, "Dots")
        c.line(x_margin, y_pos - 1.5 * mm, width - x_margin, y_pos - 1.5 * mm)

    draw_header(y)
    y -= line_height * 1.5

    c.setFont(FONT_NAME, font_size)
    for i, word in enumerate(words, start=1):
        if y < y_margin:
            c.showPage()
            y = height - y_margin
            draw_header(y)
            y -= line_height * 1.5
            c.setFont(FONT_NAME, font_size)

        col1, col2, col3 = number_to_dotmap(i, bits_count)

        c.drawString(x_index, y, str(i))
        c.drawString(x_word, y, word)
        c.drawString(x_col1, y, col1)
        c.drawString(x_col2, y, col2)
        c.drawString(x_col3, y, col3)

        y -= line_height

    c.save()
    print(f"[Success] PDF generated: {output_file}")


if __name__ == "__main__":
    while True:
        choice = input("请选择模式: 1-1024 (11 dots) 或 1-2048 (12 dots): ")
        if choice in ["1", "2"]:
            break
        print("无效输入，请输入 1 或 2。")

    if choice == "1":
        mode = 1024
        output_filename = "bip39_dotmap_1024_for_engraving.pdf"
    else:
        mode = 2048
        output_filename = "bip39_dotmap_2048_for_engraving.pdf"

    try:
        # 始终读取全部2048个单词
        with open("english.txt", "r", encoding="utf-8") as f:
            words_to_process = [line.strip() for line in f if line.strip()]

        if len(words_to_process) != 2048:
            raise ValueError(
                f"Error: english.txt has {len(words_to_process)} words (should be 2048)."
            )

        generate_pdf(words_to_process, mode, output_filename)

    except FileNotFoundError:
        print(
            "Error: 'english.txt' not found. Please ensure it is in the same directory as the script."
        )
    except ValueError as e:
        print(e)
