import pandas as pd
import numpy as np
import os
import sys
import matplotlib.pyplot as plt
import seaborn as sns
import joblib
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score

# Ana dizini bul
ana_dizin = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.append(ana_dizin)

try:
    from kullanici import klasor as base_path
except ImportError:
    base_path = r"c:\Users\User\Desktop\Kredi Hesaplaması"

# Yollar
input_file = os.path.join(base_path, "3_Siniflandirma_Modelleri", "Ciktilar", "1_Veri_Hazirlik", "Egitim_Datasi.xlsx")
gorsel_dir = os.path.join(base_path, "3_Siniflandirma_Modelleri", "Gorseller", "8_Overfit_Kontrolu")
model_path = os.path.join(base_path, "3_Siniflandirma_Modelleri", "Modeller", "6_Final_Model", "champion_hybrid_final.joblib")

def setup():
    os.makedirs(gorsel_dir, exist_ok=True)

def analyze_overfit_and_leakage():
    print("\n" + "="*60)
    print("ADIM 8: OVERFIT (EZBERLEME) VE VERİ SIZINTISI (LEAKAGE) KONTROLÜ")
    print("="*60)

    setup()

    if not os.path.exists(model_path):
        print("HATA: Şampiyon model bulunamadı! Önce 6. adımı çalıştırın.")
        return

    print("> Veri ve Model Yükleniyor...")
    df = pd.read_excel(input_file, engine='openpyxl')
    y = df["Kredi Skoru"]
    
    champion = joblib.load(model_path)
    
    # Modelin beklediği sütunları seç (Önceki eleme adımlarından dolayı)
    expected_features = champion.feature_names_in_
    X = df[expected_features]
    
    # 6. adımdakiyle aynı seed (42) ile bölüyoruz
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)
    
    print("> Metrikler Hesaplanıyor (Train vs Test)...")
    # Eğitim Seti Metrikleri
    y_train_pred = champion.predict(X_train)
    train_acc = accuracy_score(y_train, y_train_pred)
    train_f1 = f1_score(y_train, y_train_pred, average='weighted')

    # Test Seti Metrikleri
    y_test_pred = champion.predict(X_test)
    test_acc = accuracy_score(y_test, y_test_pred)
    test_f1 = f1_score(y_test, y_test_pred, average='weighted')

    print(f"  Eğitim Doğruluğu (Train Accuracy) : %{train_acc*100:.2f}")
    print(f"  Test Doğruluğu (Test Accuracy)   : %{test_acc*100:.2f}")
    
    fark = (train_acc - test_acc) * 100
    print(f"  Fark (Overfit Göstergesi)        : %{fark:.2f}")

    if fark < 5:
        durum = "MÜKEMMEL (Ezberleme Yok)"
        renk = '#2ecc71'
    elif fark < 10:
        durum = "KABUL EDİLEBİLİR (Hafif Overfit)"
        renk = '#f1c40f'
    else:
        durum = "RİSKLİ (Yüksek Overfit)"
        renk = '#e74c3c'
        
    print(f"  Sonuç                            : {durum}")

    # 1. GÖRSEL: Train vs Test Performans Bar Grafiği
    plt.style.use('seaborn-v0_8-whitegrid')
    plt.figure(figsize=(10, 6))
    
    labels = ['Doğruluk (Accuracy)', 'F1 Skoru (F1-Score)']
    train_scores = [train_acc, train_f1]
    test_scores = [test_acc, test_f1]
    
    x = np.arange(len(labels))
    width = 0.35
    
    fig, ax = plt.subplots(figsize=(10, 6))
    rects1 = ax.bar(x - width/2, train_scores, width, label='Eğitim (Train) Seti', color='#34495e')
    rects2 = ax.bar(x + width/2, test_scores, width, label='Test Seti', color=renk)
    
    ax.set_ylabel('Skor', fontweight='bold')
    ax.set_title('ADIM 8: Modelin Ezberleme (Overfit) Analizi', fontweight='bold', pad=20, fontsize=14)
    ax.set_xticks(x)
    ax.set_xticklabels(labels, fontweight='bold')
    ax.legend()
    ax.set_ylim(0, 1.1)

    # Değerleri bar üzerine yaz
    for rects in [rects1, rects2]:
        for rect in rects:
            height = rect.get_height()
            ax.annotate(f'%{height*100:.1f}',
                        xy=(rect.get_x() + rect.get_width() / 2, height),
                        xytext=(0, 3),  
                        textcoords="offset points",
                        ha='center', va='bottom', fontweight='bold')
                        
    plt.text(0.5, 0.95, f"Durum: {durum} (Fark: %{fark:.1f})", 
             ha='center', va='center', transform=ax.transAxes, 
             bbox=dict(facecolor='white', alpha=0.8, edgecolor=renk), fontweight='bold')
             
    plt.tight_layout()
    plt.savefig(os.path.join(gorsel_dir, "1_Train_vs_Test_Performance.png"), dpi=300)
    plt.close()

    # 2. GÖRSEL: Veri Sızıntısı (Leakage) Kontrol Tablosu
    print("\n> Veri Sızıntısı (Data Leakage) Analizi Yapılıyor...")
    
    correlations = df.corr(numeric_only=True)['Kredi Skoru'].abs().sort_values(ascending=False)
    correlations = correlations.drop('Kredi Skoru') # Kendisini çıkar
    
    top_5 = correlations.head(5)
    
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.axis('tight')
    ax.axis('off')
    
    table_data = []
    table_data.append(["Özellik (Feature)", "Hedefle Korelasyonu", "Sızıntı Durumu"])
    
    leakage_found = False
    for feature, corr in top_5.items():
        if corr > 0.95:
            status = "❌ RİSK (Sızıntı İhtimali)"
            leakage_found = True
        else:
            status = "✅ GÜVENLİ"
            
        table_data.append([feature, f"%{corr*100:.1f}", status])
        
    table = ax.table(cellText=table_data, loc='center', cellLoc='center')
    table.auto_set_font_size(False)
    table.set_fontsize(12)
    table.scale(1, 2)
    
    # Başlıkları formatla
    for i in range(len(table_data[0])):
        table[(0, i)].set_text_props(weight='bold', color='white')
        table[(0, i)].set_facecolor('#2c3e50')
        
    for i in range(1, len(table_data)):
        if "RİSK" in table_data[i][2]:
            table[(i, 2)].set_facecolor('#ffb8b8')
        else:
            table[(i, 2)].set_facecolor('#d4edda')
            
    # Genel Sonuç Alt Yazısı
    genel_sonuc = "KONTROL SONUCU: Hedef değişkeni %100 oranında önceden açıklayan\nhiçbir şüpheli sütuna rastlanmamıştır (Data Leakage Yoktur)." if not leakage_found else "DİKKAT: Bazı sütunlar hedef değişkenle aşırı ilişkili, sızıntı kontrol edilmeli!"
    
    plt.title("ADIM 8: Veri Sızıntısı (Data Leakage) Diagnostik Raporu", fontweight='bold', pad=20, fontsize=14)
    plt.text(0.5, 0.1, genel_sonuc, ha='center', fontweight='bold', fontsize=12, color='green' if not leakage_found else 'red')
    
    plt.tight_layout()
    plt.savefig(os.path.join(gorsel_dir, "2_Leakage_Diagnostic_Dashboard.png"), dpi=300)
    plt.close()

    print("\nİŞLEM TAMAMLANDI! (Görseller 8_Overfit_Kontrolu klasörüne kaydedildi.)")

if __name__ == "__main__":
    analyze_overfit_and_leakage()
