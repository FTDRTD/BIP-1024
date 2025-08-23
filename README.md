# BIP39 DotMap Generator

[中文版本](README.md) | [English Version](README_EN.md)
一个用于生成BIP39助记词点图的Python工具，专为物理雕刻和手动恢复场景优化。

## 项目简介

本项目的主要功能：

- **BIP39 DotMap Generator**: 用于生成 BIP39 助记词点图，专为物理雕刻和手动恢复场景优化。

## 功能特性

- **点图转换**: 将2048个BIP39英文单词转换为易于识别的点图格式
- **手动恢复优化**: 点位按权重从低到高排列，便于手动计算
- **PDF生成**: 使用ReportLab生成高质量PDF文档
- **字体支持**: 支持自定义字体以完美显示●和○符号
- **分页处理**: 自动处理大量数据并分页显示

## 工作原理

1. 读取 `english.txt`文件中的2048个BIP39单词
2. 将每个单词的索引号（1-2048）转换为11位二进制
3. 将二进制位反转，使权重从低到高排列（1, 2, 4, 8, 16, 32, 64, 128, 256, 512, 1024）
4. 使用●（实心点）表示1，○（空心点）表示0
5. 生成包含单词和对应点图的PDF文档

## 文件说明

- `main.py` - 主程序文件
- `english.txt` - BIP39英文单词列表（2048个单词）
- `requirements.txt` - Python依赖包列表
- `DejaVuSans.ttf` - 常规字体文件
- `DejaVuSans-Bold.ttf` - 粗体字体文件
- `msyh.ttc` - 中文字体文件（微软雅黑）
- `bip39_dotmap_for_engraving.pdf` - 生成的PDF输出文件

## 系统要求

- Python 3.6+
- ReportLab 3.0+
- 支持UTF-8编码的文本编辑器

## 快速开始

### 环境准备

1. 安装 Python 3.6+
2. 安装 ReportLab 3.0+

### 安装依赖

使用 requirements.txt 安装依赖：

```bash
pip install -r requirements.txt
```

或手动安装 ReportLab：

```bash
pip install reportlab
```

## 使用方法

1.  确保所有必需文件在同一目录下：
    *   `main.py`
    *   `english.txt`
    *   `DejaVuSans.ttf`
    *   `DejaVuSans-Bold.ttf`
2.  运行程序：
    ```bash
    python main.py
    ```
3.  根据提示选择模式：
    *   输入 `1` 选择 **1-1024** 模式 (11个点)。
    *   输入 `2` 选择 **1-2048** 模式 (12个点)。
4.  程序将根据您的选择生成对应的 PDF 文件：
    *   `bip39_dotmap_1024_for_engraving.pdf` (1024模式)
    *   `bip39_dotmap_2048_for_engraving.pdf` (2048模式)

## 输出格式说明

PDF文档包含以下信息：

*   **标题**: 根据所选模式显示 `BIP39 Mnemonic DotMap (1024 words, 11 dots)` 或 `BIP39 Mnemonic DotMap (2048 words, 12 dots)`。
*   **点图含义说明**: 解释 ● (实心点) 和 ○ (空心点) 的含义。
*   **权重顺序说明**:
    *   **1024 模式 (11 点)**: `1 | 2 | 4 | 8 || 16 | 32 | 64 | 128 || 256 | 512 | 1024`
    *   **2048 模式 (12 点)**: `1 | 2 | 4 | 8 || 16 | 32 | 64 | 128 || 256 | 512 | 1024 | 2048`
*   **表格**: 包含索引号、英文单词以及对应点图。

## 点图解读

- **●** (实心点) = 1 = 该权重被选中
- **○** (空心点) = 0 = 该权重未被选中

要手动恢复单词，需要：

1. 找到对应的点图行
2. 从左到右读取三个点图列
3. 将●转换为1，○转换为0
4. 按权重计算：点图位 × 对应权重
5. 累加所有权重得到索引号
6. 根据索引号在BIP39单词表中查找对应的单词

## 故障排除

### 字体文件未找到

```
错误：字体文件 'DejaVuSans.ttf' 或 'DejaVuSans-Bold.ttf' 未找到！
请确保这些文件和 main.py 在同一个文件夹下。
```

**解决方法**：确保字体文件存在，或程序将自动回退到Helvetica字体。

### 英文单词文件未找到

```
Error: 'english.txt' not found. Please ensure it is in the same directory as the script.
```

**解决方法**：确保 `english.txt`文件存在于程序目录中。

### 单词数量不匹配

```
Error: english.txt has X words (should be 2048).
```

**解决方法**：确保 `english.txt`包含完整的2048个BIP39单词。

## 许可证

本项目采用 [MIT License](LICENSE) 开源许可证。

您可以自由地：

- 使用、复制和修改代码
- 商业使用
- 分发原始或修改版本

使用时只需保留原始版权声明和许可证文件即可。

**重要提醒**：本项目仅供学习和研究使用。在使用BIP39相关功能时，请确保遵守当地法律法规和相关加密货币监管要求。

## 贡献

[中文版本](README.md) | [English Version](README_EN.md)
欢迎提交 Issue 和 Pull Request 来改进这个项目。

如果您有任何问题或建议，请随时提出。

## 离线运行

1. 确保已安装所有依赖。
2. 在没有网络连接的情况下运行程序，以保证程序无后门，100% 离线运行。

程序将生成 `bip39_dotmap_for_engraving.pdf` 文件。
