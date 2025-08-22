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


def number_to_dotmap(n: int):
    """将单词索引号 n (1-2048) 转换为 11 位二进制的点图 (为手动解码优化)"""
    # 1. 生成标准的 11 位二进制字符串 (高位在前)
    bits = bin(n - 1)[2:].zfill(11)

    # 2. 【关键】将二进制字符串反转，以实现 1 -> 1024 的顺序 (低位在前)
    reversed_bits = bits[::-1]

    # 3. 根据反转后的字符串生成点图
    dots = ["●" if b == "1" else "○" for b in reversed_bits]

    col1 = "".join(dots[0:4])
    col2 = "".join(dots[4:8])
    col3 = "".join(dots[8:11])
    return col1, col2, col3


def generate_pdf(words, output_file="bip39_dotmap_for_engraving.pdf"):
    """为物理雕刻和手动恢复场景，生成优化后的 PDF"""
    c = canvas.Canvas(output_file, pagesize=A4)
    width, height = A4

    x_margin = 20 * mm
    y_margin = 20 * mm
    line_height = 5 * mm

    y = height - y_margin
    c.setFont(FONT_NAME_BOLD, 16)
    c.drawString(x_margin, y, "BIP39 Mnemonic DotMap (Manual Recovery Optimized)")
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
        "FOR EASY MANUAL CALCULATION, the 11 dot positions are ordered from LOWEST to HIGHEST weight:"
    )

    text.setFont(FONT_NAME_BOLD, 9)
    # 使用空格手动对齐，以匹配新的权重值宽度
    text.textLine("     1 | 2 | 4 | 8 || 16 | 32 | 64 | 128 || 256 | 512 | 1024")

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
        c.drawString(x_col1, y_pos, "Dots 1-4")
        c.drawString(x_col2, y_pos, "Dots 5-8")
        c.drawString(x_col3, y_pos, "Dots 9-11")
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

        col1, col2, col3 = number_to_dotmap(i)

        c.drawString(x_index, y, str(i))
        c.drawString(x_word, y, word)
        c.drawString(x_col1, y, col1)
        c.drawString(x_col2, y, col2)
        c.drawString(x_col3, y, col3)

        y -= line_height

    c.save()
    print(f"[Success] PDF generated: {output_file}")


if __name__ == "__main__":
    try:
        with open("english.txt", "r", encoding="utf-8") as f:
            words = [line.strip() for line in f if line.strip()]

        if len(words) != 2048:
            raise ValueError(
                f"Error: english.txt has {len(words)} words (should be 2048)."
            )

        generate_pdf(words)

    except FileNotFoundError:
        print(
            "Error: 'english.txt' not found. Please ensure it is in the same directory as the script."
        )
    except ValueError as e:
        print(e)
