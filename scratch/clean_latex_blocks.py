import re

def clean_latex(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    def clean_block(match):
        block = match.group(0)
        # Turkish character mapping
        mapping = {
            'ç': 'c', 'Ç': 'C',
            'ğ': 'g', 'Ğ': 'G',
            'ı': 'i', 'İ': 'I',
            'ö': 'o', 'Ö': 'O',
            'ş': 's', 'Ş': 'S',
            'ü': 'u', 'Ü': 'U'
        }
        for tr, en in mapping.items():
            block = block.replace(tr, en)
        return block

    # Find all lstlisting blocks and clean them
    cleaned_content = re.sub(r'\\begin\{lstlisting\}.*?\\end\{lstlisting\}', clean_block, content, flags=re.DOTALL)

    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(cleaned_content)

if __name__ == "__main__":
    clean_latex(r"c:\Users\User\Desktop\Kredi Hesaplaması\4_Rapor_ve_Sunum\main.tex")
