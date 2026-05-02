import pandas as pd
import numpy as np
import os
import matplotlib.pyplot as plt
import seaborn as sns
import joblib
from sklearn.model_selection import train_test_split
from sklearn.ensemble import ExtraTreesClassifier, RandomForestClassifier, StackingClassifier, VotingClassifier
from xgboost import XGBClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score

# Proje ana dizini bul
ana_dizin = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
base_path = ana_dizin

# Yollar
input_file = os.path.join(base_path, "3_Model_Egitimi_ve_Degerlendirme", "Ciktilar", "1_Veri_Hazirlik", "Egitim_Verisi_Dengelenmis.xlsx")
model_dir = os.path.join(base_path, "3_Model_Egitimi_ve_Degerlendirme", "Modeller", "4_Hibrit_Model")
gorsel_dir = os.path.join(base_path, "3_Model_Egitimi_ve_Degerlendirme", "Gorseller", "4_Hibrit_Model")
cikti_dir = os.path.join(base_path, "3_Model_Egitimi_ve_Degerlendirme", "Ciktilar", "4_Hibrit_Model")

import shutil
def setup_folders():
    for folder in [model_dir, gorsel_dir, cikti_dir]:
        if os.path.exists(folder): shutil.rmtree(folder)
        os.makedirs(folder, exist_ok=True)

def gorsel_turnuva_sonuclari(sonuclar_df):
    print("> Model Turnuvası Sonuçları Görselleştiriliyor...")
    plt.figure(figsize=(12, 7))
    sonuclar_df = sonuclar_df.sort_values(by="Doğruluk (%)", ascending=True)
    
    # Renk paleti: Bireyseller gri, Hibritler turuncu tonları
    colors = ['#95a5a6' if "Hibrit" not in x else '#e67e22' for x in sonuclar_df['Model']]
    
    bars = plt.barh(sonuclar_df['Model'], sonuclar_df['Doğruluk (%)'], color=colors)
    
    for bar in bars:
        width = bar.get_width()
        plt.text(width + 0.5, bar.get_y() + bar.get_height()/2, f'%{width:.2f}', 
                 va='center', fontweight='bold', fontsize=11)
    
    plt.title("Figür 3-4: Hibrit vs Bireysel Model Turnuvası (Raporluk)", fontsize=14, fontweight='bold')
    plt.xlabel("Doğruluk Oranı (%)")
    plt.xlim(min(sonuclar_df['Doğruluk (%)']) - 5, 105)
    plt.grid(axis='x', linestyle='--', alpha=0.6)
    plt.tight_layout()
    plt.savefig(os.path.join(gorsel_dir, "01_Hibrit_Turnuva_Sonuclari.png"), dpi=300)
    plt.close()

def gorsel_sampiyon_detay(weights, names, model_name):
    print(f"> Şampiyon Model ({model_name}) Reçetesi Görselleştiriliyor...")
    plt.figure(figsize=(10, 8))
    colors = ['#3498db', '#e74c3c', '#2ecc71']
    explode = [0.05] * len(weights)
    
    plt.pie(weights, labels=names, autopct='%1.1f%%', startangle=140, 
            colors=colors, explode=explode, pctdistance=0.85,
            textprops={'fontsize': 12, 'fontweight': 'bold'})
    
    centre_circle = plt.Circle((0,0), 0.70, fc='white')
    plt.gca().add_artist(centre_circle)
    
    plt.title(f"Şampiyon Model Reçetesi: {model_name}\n(Hangi Yöntem Ne Kadar Katkı Sağladı?)", fontsize=15, fontweight='bold')
    plt.axis('equal')
    plt.tight_layout()
    plt.savefig(os.path.join(gorsel_dir, "02_Sampiyon_Model_Analizi.png"), dpi=300)
    plt.close()

def hibrit_turnuva_ve_insa():
    print("\n" + "="*60)
    print("FAZ 3 - ADIM 4: HİBRİT MODEL TURNUVASI VE ŞAMPİYON İNŞASI")
    print("="*60)
    
    setup_folders()
    df = pd.read_excel(input_file)
    X = df.drop(columns=["Kredi Skoru"])
    y = df["Kredi Skoru"]
    X_train, X_val, y_train, y_val = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)

    # 1. AŞAMA: Bireysel Modellerin Eğitimi
    print("> 1. AŞAMA: Bireysel modeller yarıştırılıyor...")
    et = ExtraTreesClassifier(n_estimators=100, random_state=42, n_jobs=1)
    rf = RandomForestClassifier(n_estimators=100, random_state=42, n_jobs=1)
    xgb = XGBClassifier(use_label_encoder=False, eval_metric='mlogloss', random_state=42, n_jobs=1)

    modeller = [("ExtraTrees", et), ("RandomForest", rf), ("XGBoost", xgb)]
    skorlar = []

    for isim, model in modeller:
        model.fit(X_train, y_train)
        acc = accuracy_score(y_val, model.predict(X_val)) * 100
        skorlar.append({"Model": isim, "Doğruluk (%)": acc, "Tür": "Bireysel"})
        print(f"  - {isim}: %{acc:.2f}")

    # 2. AŞAMA: Hibrit Yöntemlerin Denenmesi
    print("\n> 2. AŞAMA: Hibrit yöntemler deneniyor...")
    
    # Basit Oylama (Soft Voting)
    voting_soft = VotingClassifier(estimators=modeller, voting='soft', n_jobs=1)
    voting_soft.fit(X_train, y_train)
    acc_soft = accuracy_score(y_val, voting_soft.predict(X_val)) * 100
    skorlar.append({"Model": "Hibrit (Basit Oylama)", "Doğruluk (%)": acc_soft, "Tür": "Hibrit"})
    print(f"  - Basit Oylama: %{acc_soft:.2f}")

    # Ağırlıklı Oylama (Weighted Voting - Manuel/Blend)
    # Örn: %40 ET, %30 RF, %30 XGB
    voting_weight = VotingClassifier(estimators=modeller, voting='soft', weights=[0.4, 0.3, 0.3], n_jobs=1)
    voting_weight.fit(X_train, y_train)
    acc_weight = accuracy_score(y_val, voting_weight.predict(X_val)) * 100
    skorlar.append({"Model": "Hibrit (Ağırlıklı Blend)", "Doğruluk (%)": acc_weight, "Tür": "Hibrit"})
    print(f"  - Ağırlıklı Blend: %{acc_weight:.2f}")

    # Stacking (Meta-Learner ile Akıllı Hibrit)
    stack_model = StackingClassifier(estimators=modeller, final_estimator=LogisticRegression(), cv=3, n_jobs=1)
    stack_model.fit(X_train, y_train)
    acc_stack = accuracy_score(y_val, stack_model.predict(X_val)) * 100
    skorlar.append({"Model": "Hibrit (Stacking Ensemble)", "Doğruluk (%)": acc_stack, "Tür": "Hibrit"})
    print(f"  - Stacking Ensemble: %{acc_stack:.2f}")

    # 3. AŞAMA: Şampiyonun Belirlenmesi ve Kurcalanması
    sonuclar_df = pd.DataFrame(skorlar)
    sampiyon_row = sonuclar_df.loc[sonuclar_df['Doğruluk (%)'].idxmax()]
    sampiyon_isim = sampiyon_row['Model']
    sampiyon_skor = sampiyon_row['Doğruluk (%)']
    
    print("\n" + "*"*60)
    print(f"ŞAMPİYON BELİRLENDİ: {sampiyon_isim}")
    print(f"EN YÜKSEK DOĞRULUK ORANI: %{sampiyon_skor:.2f}")
    print("*"*60)

    # Görselleştirme
    gorsel_turnuva_sonuclari(sonuclar_df)
    
    # Şampiyon Analizi (Ağırlıklar)
    if "Stacking" in sampiyon_isim:
        coefs = np.abs(stack_model.final_estimator_.coef_)
        if coefs.shape[1] == len(modeller) * len(stack_model.classes_):
            w = [coefs[:, i*3:(i+1)*3].sum() for i in range(len(modeller))]
        else:
            w = coefs.sum(axis=0)
        norm_w = (np.array(w) / np.sum(w)) * 100
        gorsel_sampiyon_detay(norm_w, [n for n, _ in modeller], "Stacking Ensemble")
        joblib.dump(stack_model, os.path.join(model_dir, "hibrit_stacking_model.joblib"), compress=3)
    elif "Ağırlıklı" in sampiyon_isim:
        gorsel_sampiyon_detay([40, 30, 30], [n for n, _ in modeller], "Ağırlıklı Blend")
        joblib.dump(voting_weight, os.path.join(model_dir, "hibrit_stacking_model.joblib"), compress=3)
    else:
        gorsel_sampiyon_detay([33.3, 33.3, 33.4], [n for n, _ in modeller], "Basit Oylama")
        joblib.dump(voting_soft, os.path.join(model_dir, "hibrit_stacking_model.joblib"), compress=3)

    # Excel Kaydı
    sonuclar_df.to_excel(os.path.join(cikti_dir, "Hibrit_Model_Turnuva_Raporu.xlsx"), index=False)
    print(f"\n> Tüm sonuçlar raporlandı: {cikti_dir}")

if __name__ == "__main__":
    hibrit_turnuva_ve_insa()
