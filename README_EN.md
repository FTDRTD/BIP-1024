# BIP39 DotMap Generator

A Python tool for generating BIP39 mnemonic dot maps, specifically optimized for physical engraving and manual recovery scenarios.

[中文版本](README.md) | [English Version](README_EN.md)

## Features

- **Dot Map Conversion**: Converts 2048 BIP39 English words into easily recognizable dot map format
- **Manual Recovery Optimization**: Dots are arranged from lowest to highest weight for easy manual calculation
- **PDF Generation**: Uses ReportLab to generate high-quality PDF documents
- **Font Support**: Supports custom fonts for perfect display of ● and ○ symbols
- **Pagination**: Automatically handles large datasets with page breaks

## How It Works

1. Reads 2048 BIP39 words from `english.txt` file
2. Converts each word's index number (1-2048) to 11-bit binary
3. Reverses the binary bits so weights are ordered from low to high (1, 2, 4, 8, 16, 32, 64, 128, 256, 512, 1024)
4. Uses ● (solid dot) for 1 and ○ (hollow dot) for 0
5. Generates a PDF document containing words and their corresponding dot maps

## File Structure

- `main.py` - Main program file
- `english.txt` - BIP39 English word list (2048 words)
- `DejaVuSans.ttf` - Regular font file
- `DejaVuSans-Bold.ttf` - Bold font file
- `bip39_dotmap_for_engraving.pdf` - Generated PDF output file

## System Requirements

- Python 3.6+
- ReportLab 3.0+
- Text editor with UTF-8 encoding support

## Installation

```bash
pip install reportlab
```

## Usage

1. Ensure all required files are in the same directory:
   - `main.py`
   - `english.txt`
   - `DejaVuSans.ttf`
   - `DejaVuSans-Bold.ttf`

2. Run the program:
```bash
python main.py
```

3. The program will generate `bip39_dotmap_for_engraving.pdf`

## Output Format

The PDF document includes:
- Title: BIP39 Mnemonic DotMap (Manual Recovery Optimized)
- Dot meaning explanation
- Weight order explanation (1 | 2 | 4 | 8 || 16 | 32 | 64 | 128 || 256 | 512 | 1024)
- Table with: Index number, English word, three dot map columns (corresponding to different weight ranges)

## Dot Map Interpretation

- **●** (Solid Dot) = 1 = Weight is selected
- **○** (Hollow Dot) = 0 = Weight is not selected

To manually recover a word:
1. Find the corresponding dot map row
2. Read the three dot map columns from left to right
3. Convert ● to 1 and ○ to 0
4. Calculate by weight: dot position × corresponding weight
5. Sum all weights to get the index number
6. Look up the corresponding word in the BIP39 word list by index

## Troubleshooting

### Font Files Not Found
```
Error: Font files 'DejaVuSans.ttf' or 'DejaVuSans-Bold.ttf' not found!
Please ensure these files are in the same directory as the script.
```
**Solution**: Ensure font files exist, or the program will automatically fall back to Helvetica font.

### English Word File Not Found
```
Error: 'english.txt' not found. Please ensure it is in the same directory as the script.
```
**Solution**: Ensure `english.txt` exists in the program directory.

### Word Count Mismatch
```
Error: english.txt has X words (should be 2048).
```
**Solution**: Ensure `english.txt` contains the complete set of 2048 BIP39 words.

## License

This project is licensed under the [MIT License](LICENSE).

You are free to:
- Use, copy, and modify the code
- Use commercially
- Distribute original or modified versions

Simply retain the original copyright notice and license file when using.

**Important Notice**: This project is for educational and research purposes only. Please ensure compliance with local laws and cryptocurrency regulations when using BIP39-related features.

## Contributing

Issues and Pull Requests are welcome to improve this project.

---

[中文版本](README.md) | [English Version](README_EN.md)