import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os

base_path = r"c:\Users\User\Desktop\Kredi Hesaplaması"
report_file = os.path.join(base_path, "3_Siniflandirma_Modelleri", "Ciktilar", "9_Model_Gelistirme_Raporu.xlsx")
output_dir = os.path.join(base_path, "3_Siniflandirma_Modelleri", "Gorseller", "9_Optuna_Optimizasyon")
os.makedirs(output_dir, exist_ok=True)

def generate_visuals():
    if not os.path.exists(report_file):
        print("Rapor dosyası bulunamadı.")
        return

    df = pd.read_excel(report_file)
    
    # 1. En İyi 10 Deneme (Accuracy)
    plt.figure(figsize=(12, 7))
    top_10 = df.sort_values("Dogruluk", ascending=False).head(10).copy()
    top_10["Etiket"] = top_10["Modeller"] + "\n" + top_10["Agirliklar"].astype(str)
    
    plt.style.use('seaborn-v0_8-whitegrid')
    ax = sns.barplot(data=top_10, x='Dogruluk', y='Etiket', palette='flare')
    plt.title("ADIM 9: Optuna Optimizasyonu - En İyi 10 Hibrit Kombinasyonu", fontweight='bold', fontsize=14)
    plt.xlabel("Doğruluk (Accuracy)")
    plt.xlim(top_10['Dogruluk'].min() - 0.01, top_10['Dogruluk'].max() + 0.005)
    
    for p in ax.patches:
        ax.annotate(f'%{p.get_width()*100:.2f}', (p.get_width(), p.get_y() + p.get_height() / 2.),
                    ha='left', va='center', xytext=(5, 0), textcoords='offset points', fontweight='bold')
    
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, "Figure_9_1_Optimization_Top_10.png"), dpi=300)
    plt.close()

    # 2. Hibrit Tipleri Dağılımı (Box Plot)
    plt.figure(figsize=(10, 6))
    sns.boxplot(data=df, x='Hibrit_Tipi', y='Dogruluk', palette='Set2')
    plt.title("Hibrit Mimarilerin Performans Dağılımı", fontweight='bold')
    plt.savefig(os.path.join(output_dir, "Figure_9_2_Hybrid_Distributions.png"), dpi=300)
    plt.close()

    print(f"Görseller oluşturuldu: {output_dir}")

if __name__ == "__main__":
    generate_visuals()
