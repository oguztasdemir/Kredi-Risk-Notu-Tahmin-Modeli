import pandas as pd
import numpy as np
import os
import matplotlib.pyplot as plt
import seaborn as sns
import joblib
import optuna
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.ensemble import ExtraTreesClassifier
from sklearn.metrics import accuracy_score

# Proje ana dizini bul
ana_dizin = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
base_path = ana_dizin

# Yollar
input_file = os.path.join(base_path, "3_Model_Egitimi_ve_Degerlendirme", "Ciktilar", "1_Veri_Hazirlik", "Egitim_Verisi_Dengelenmis.xlsx")
output_dir = os.path.join(base_path, "3_Model_Egitimi_ve_Degerlendirme", "Ciktilar", "3_Hiperparametre")
gorsel_dir = os.path.join(base_path, "3_Model_Egitimi_ve_Degerlendirme", "Gorseller", "3_Hiperparametre")
model_save_dir = os.path.join(base_path, "3_Model_Egitimi_ve_Degerlendirme", "Modeller", "3_Hiperparametre")

import shutil

def setup_folders():
    for folder in [output_dir, gorsel_dir, model_save_dir]:
        if os.path.exists(folder):
            shutil.rmtree(folder)
        os.makedirs(folder, exist_ok=True)

def objective(trial, X, y):
    # Optuna'nın deneyeceği parametre havuzu
    params = {
        'n_estimators': trial.suggest_int('n_estimators', 50, 300),
        'max_depth': trial.suggest_int('max_depth', 10, 50),
        'min_samples_split': trial.suggest_int('min_samples_split', 2, 10),
        'criterion': trial.suggest_categorical('criterion', ['gini', 'entropy'])
    }
    
    model = ExtraTreesClassifier(**params, random_state=42)
    score = cross_val_score(model, X, y, n_jobs=-1, cv=3).mean()
    return score

def hiperparametre_optimizasyonu_optuna():
    """
    Bu adımda 'Optuna' (Bayesian Optimization) kullanarak akıllı bir parametre araması yapıyoruz.
    GridSearch her şeyi denerken, Optuna geçmiş deneyimlerinden ders çıkararak en iyiye odaklanır.
    """
    print("\n" + "="*60)
    print("ADIM 3.3: AKILLI OPTİMİZASYON (BAYESIAN - OPTUNA)")
    print("="*60)

    setup_folders()

    if not os.path.exists(input_file):
        print("HATA: Veri dosyası bulunamadı!")
        return

    df = pd.read_excel(input_file)
    X = df.drop(columns=["Kredi Skoru"])
    y = df["Kredi Skoru"]
    
    # Optimizasyon için alt küme (Hız için %10)
    X_train, X_val, y_train, y_val = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)
    X_opt, _, y_opt, _ = train_test_split(X_train, y_train, train_size=0.2, random_state=42, stratify=y_train)

    print(f"> Optuna çalışma başlatılıyor (20 deneme)...")
    study = optuna.create_study(direction='maximize')
    
    # İlerlemeyi görmek için callback ekleyelim
    def callback(study, trial):
        print(f"  [Deneme {trial.number+1}/20] Mevcut Skor: %{trial.value*100:.2f} | En İyi: %{study.best_value*100:.2f}")

    study.optimize(lambda trial: objective(trial, X_opt, y_opt), n_trials=20, callbacks=[callback])

    print(f"\n" + "-"*30)
    print(f"> OPTİMİZASYON TAMAMLANDI!")
    print(f"> EN İYİ PARAMETRELER: {study.best_params}")
    
    # Final Model Başarısı
    best_model = ExtraTreesClassifier(**study.best_params, random_state=42)
    best_model.fit(X_train, y_train)
    final_acc = accuracy_score(y_val, best_model.predict(X_val))

    # Kayıt
    joblib.dump(study.best_params, os.path.join(model_save_dir, "best_params_extra_trees.joblib"))

    # Görselleştirme 1: Optimizasyon Geçmişi
    plt.figure(figsize=(10, 6))
    scores = [t.value for t in study.trials if t.value is not None]
    plt.plot(scores, marker='o', linestyle='-', color='#2980b9')
    plt.title("Optuna Optimizasyon Süreci: Başarı Gelişimi", fontsize=14, fontweight='bold')
    plt.xlabel("Deneme Sayısı")
    plt.ylabel("Doğruluk Skoru")
    plt.grid(True, alpha=0.3)
    plt.savefig(os.path.join(gorsel_dir, "Optuna_Optimization_History.png"), dpi=300)
    plt.close()

    # Görselleştirme 2: Başarı Artışı (Bar Chart)
    baseline_score = scores[0] if scores else 0
    best_score = study.best_value
    
    plt.figure(figsize=(10, 6))
    labels = ['İlk Deneme (Baseline)', 'En İyi Deneme (Optuna)']
    values = [baseline_score, best_score]
    bars = plt.bar(labels, values, color=['#95a5a6', '#27ae60'], width=0.5)
    
    # Sayıları bar üzerine ekle
    for bar in bars:
        yval = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2, yval + 0.01, f'%{yval*100:.2f}', ha='center', fontweight='bold')

    plt.ylim(0, 1.1)
    plt.title("Hiperparametre Optimizasyonu Başarı Farkı", fontweight='bold')
    
    # Bilgi Notu
    note = f"Yöntem: Bayesian Optimization\nMotor: Optuna\nDeneme: {len(scores)}"
    plt.text(0.65, 0.1, note, transform=plt.gca().transAxes, fontsize=10, 
             bbox=dict(facecolor='white', alpha=0.8, boxstyle='round'))

    plt.savefig(os.path.join(gorsel_dir, "Optimization_Success_Comparison.png"), dpi=300)
    plt.close()

    print(f"> Başarılı: Optimize Model Doğruluğu: %{final_acc*100:.1f}")

if __name__ == "__main__":
    hiperparametre_optimizasyonu_optuna()



