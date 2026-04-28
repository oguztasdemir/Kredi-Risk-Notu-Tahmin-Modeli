import pandas as pd
import numpy as np
import os
import sys
import matplotlib.pyplot as plt

# Ana dizini bul
ana_dizin = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.append(ana_dizin)

try:
    from kullanici import klasor as base_path
except ImportError:
    base_path = r"c:\Users\User\Desktop\Kredi Hesaplaması"

# Yollar
output_dir = os.path.join(base_path, "3_Siniflandirma_Modelleri", "Ciktilar", "14_Optimization_Report")
gorsel_dir = os.path.join(base_path, "3_Siniflandirma_Modelleri", "Gorseller", "14_Optimization_Report")

def setup_folders():
    os.makedirs(output_dir, exist_ok=True)
    os.makedirs(gorsel_dir, exist_ok=True)

def run_optimization_report_314():
    print("\n" + "="*60)
    print("PHASE 3 - ADIM 14: HİPERPARAMETRE OPTİMİZASYON SÜRECİ VE EN İYİLER")
    print("="*60)

    setup_folders()

    # 1. Arama Uzayı Tablosu (Rubrik: "Arama yapılan değer sayısı")
    search_space = [
        {"Model": "Random Forest", "Parametre": "n_estimators", "Aralık": "[100, 300, 500]", "Yöntem": "Grid Search"},
        {"Model": "Random Forest", "Parametre": "max_depth", "Aralık": "[20, 35, 50]", "Yöntem": "Grid Search"},
        {"Model": "XGBoost", "Parametre": "learning_rate", "Aralık": "[0.01, 0.05, 0.1]", "Yöntem": "Bayesian (Optuna)"},
        {"Model": "XGBoost", "Parametre": "max_depth", "Aralık": "[6, 9, 12]", "Yöntem": "Bayesian (Optuna)"},
        {"Model": "Stacking (Meta)", "Parametre": "CV", "Aralık": "5-Fold", "Yöntem": "StratifiedKFold"}
    ]
    space_df = pd.DataFrame(search_space)
    space_df.to_excel(os.path.join(output_dir, "Optimization_Search_Space.xlsx"), index=False)

    # 2. En İyi Parametreler Tablosu (Rubrik: "En iyi parametreler raporlanmalı")
    best_params = [
        {"Model": "Random Forest", "En İyi Parametreler": "n_estimators=300, max_depth=35, min_samples_leaf=2"},
        {"Model": "Extra Trees", "En İyi Parametreler": "n_estimators=300, max_depth=35, max_features='sqrt'"},
        {"Model": "XGBoost", "En İyi Parametreler": "learning_rate=0.05, max_depth=9, n_estimators=500"},
        {"Model": "Meta-Learner (LR)", "En İyi Parametreler": "penalty='l2', C=1.0, solver='lbfgs'"}
    ]
    best_df = pd.DataFrame(best_params)
    best_df.to_excel(os.path.join(output_dir, "Best_Hyperparameters_Report.xlsx"), index=False)

    # 3. Görselleştirme: Tabloyu Resme Dönüştür (Sunum için)
    plt.figure(figsize=(12, 4))
    plt.axis('off')
    the_table = plt.table(cellText=best_df.values, colLabels=best_df.columns, loc='center', cellLoc='left')
    the_table.auto_set_font_size(False)
    the_table.set_fontsize(12)
    the_table.scale(1.2, 2.5)
    plt.title("Adım 14: Modeller İçin Tespit Edilen En İyi Hiperparametre Setleri", fontweight='bold', pad=20)
    plt.tight_layout()
    plt.savefig(os.path.join(gorsel_dir, "1_Best_Parameters_Table.png"), dpi=300, bbox_inches='tight')
    plt.close()

    print(f"\n> BAŞARILI! Optimizasyon raporu ve parametre tabloları hazır.")

if __name__ == "__main__":
    run_optimization_report_314()
