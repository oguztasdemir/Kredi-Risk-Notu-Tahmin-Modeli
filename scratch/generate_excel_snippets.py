import pandas as pd
import matplotlib.pyplot as plt
import os

def save_df_as_excel_style(df, path, title, theme_color='#217346'):
    fig, ax = plt.subplots(figsize=(8, 3))
    ax.axis('off')
    tbl = ax.table(cellText=df.values, colLabels=df.columns, cellLoc='left', loc='center')
    tbl.auto_set_font_size(False)
    tbl.set_fontsize(10)
    tbl.scale(1.1, 1.8)
    
    for (row, col), cell in tbl.get_celld().items():
        cell.set_edgecolor('#D0D0D0')
        if row == 0:
            cell.set_text_props(weight='bold', color='white')
            cell.set_facecolor(theme_color)
        else:
            cell.set_facecolor('#F9F9F9') if row % 2 == 0 else cell.set_facecolor('white')

    plt.title(title, fontsize=12, pad=15, weight='bold')
    plt.savefig(path, bbox_inches='tight', dpi=150, facecolor='white')
    plt.close()

os.makedirs("5_Sunum/Gorseller/Excel_Snippets", exist_ok=True)

# Step 1: Ham Veri (Türkçe kolon isimleri ve değerleri)
df1_before = pd.DataFrame({
    'ID': ['C_001', 'C_002'],
    'Yıllık Gelir (Ham)': ['$12,500.00_', 'Unknown'],
    'Yaş (Ham)': ['-5', '23_']
})
df1_after = pd.DataFrame({
    'ID': ['C_001', 'C_002'],
    'Yıllık Gelir (Temiz)': [12500.0, None],
    'Yaş (Temiz)': [None, 23.0]
})
save_df_as_excel_style(df1_before, "5_Sunum/Gorseller/Excel_Snippets/Step1_Before.png", "ADIM 1: HAM VERİ (BEFORE)", theme_color='#A52A2A')
save_df_as_excel_style(df1_after, "5_Sunum/Gorseller/Excel_Snippets/Step1_After.png", "ADIM 1: TEMİZLENMİŞ (AFTER)")

# Step 9: Anomali Onarım (Türkçe)
df9_before = pd.DataFrame({
    'Müşteri ID': ['101', '101', '101'],
    'Ay': ['Ocak', 'Şubat', 'Mart'],
    'Yaş Girişi': [25, 120, 25]
})
df9_after = pd.DataFrame({
    'Müşteri ID': ['101', '101', '101'],
    'Ay': ['Ocak', 'Şubat', 'Mart'],
    'Yaş Onarılan': [25, 25, 25]
})
save_df_as_excel_style(df9_before, "5_Sunum/Gorseller/Excel_Snippets/Step9_Before.png", "ADIM 9: ANOMALİ (BEFORE)", theme_color='#A52A2A')
save_df_as_excel_style(df9_after, "5_Sunum/Gorseller/Excel_Snippets/Step9_After.png", "ADIM 9: ONARILMIŞ (AFTER)")

# Step 12: Kodlama (Türkçe)
df12_before = pd.DataFrame({
    'Müşteri ID': ['C1', 'C2'],
    'Meslek': ['Bilim İnsanı', 'Öğretmen']
})
df12_after = pd.DataFrame({
    'Müşteri ID': ['C1', 'C2'],
    'Meslek_Bilim': [1, 0],
    'Meslek_Öğretmen': [0, 1]
})
save_df_as_excel_style(df12_before, "5_Sunum/Gorseller/Excel_Snippets/Step12_Before.png", "ADIM 12: KATEGORİK (BEFORE)", theme_color='#A52A2A')
save_df_as_excel_style(df12_after, "5_Sunum/Gorseller/Excel_Snippets/Step12_After.png", "ADIM 12: ENCODED (AFTER)")

print("Türkçe Before-After görselleri oluşturuldu.")
