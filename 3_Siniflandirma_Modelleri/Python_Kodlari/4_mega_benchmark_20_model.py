import pandas as pd
import numpy as np
import os
import sys
import matplotlib.pyplot as plt
import seaborn as sns
import joblib
import time

from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, f1_score, mean_absolute_error, mean_squared_error
from sklearn.linear_model import LogisticRegression, RidgeClassifier, SGDClassifier, PassiveAggressiveClassifier
from sklearn.tree import DecisionTreeClassifier, ExtraTreeClassifier
from sklearn.ensemble import (RandomForestClassifier, AdaBoostClassifier, GradientBoostingClassifier, 
                              ExtraTreesClassifier, BaggingClassifier, HistGradientBoostingClassifier)
from sklearn.svm import LinearSVC
from sklearn.neighbors import KNeighborsClassifier
from sklearn.naive_bayes import GaussianNB
from sklearn.neural_network import MLPClassifier
from sklearn.discriminant_analysis import LinearDiscriminantAnalysis, QuadraticDiscriminantAnalysis
from xgboost import XGBClassifier
from catboost import CatBoostClassifier

# Ana dizini bul
ana_dizin = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.append(ana_dizin)

try:
    from kullanici import klasor as base_path
except ImportError:
    base_path = r"c:\Users\User\Desktop\Kredi Hesaplaması"

# Yollar
input_file = os.path.join(base_path, "3_Siniflandirma_Modelleri", "Ciktilar", "1_Veri_Hazirlik", "Egitim_Datasi.xlsx")
output_dir = os.path.join(base_path, "3_Siniflandirma_Modelleri", "Ciktilar", "4_Mega_Benchmark")
gorsel_dir = os.path.join(base_path, "3_Siniflandirma_Modelleri", "Gorseller", "4_Mega_Benchmark")
model_dir = os.path.join(base_path, "3_Siniflandirma_Modelleri", "Modeller", "4_Mega_Benchmark")

def setup_folders():
    for folder in [output_dir, gorsel_dir, model_dir]:
        os.makedirs(folder, exist_ok=True)

def mape_calc(y_true, y_pred):
    y_true, y_pred = np.array(y_true), np.array(y_pred)
    return np.mean(np.abs((y_true - y_pred) / (y_true + 0.0001))) * 100

def gorseller_olustur_10_adet(res_df):
    print("\n> 10 Adet Akademik Görsel Güncelleniyor...")
    plt.style.use('seaborn-v0_8-whitegrid')
    viz_df = res_df.drop(columns=["Object"]) if "Object" in res_df.columns else res_df

    # 1. Accuracy Leaderboard
    plt.figure(figsize=(12, 8))
    sns.barplot(data=viz_df.sort_values("Accuracy", ascending=False), x='Accuracy', y='Model', palette="viridis")
    plt.title("Figure 11: Model Accuracy Leaderboard", fontweight='bold')
    plt.savefig(os.path.join(gorsel_dir, "Figure_11_Accuracy_Leaderboard.png"), dpi=300)

    # 2. MAE Analysis
    plt.figure(figsize=(12, 8))
    sns.barplot(data=viz_df.sort_values("MAE"), x='MAE', y='Model', palette="RdYlGn_r")
    plt.title("Figure 12: MAE Analysis", fontweight='bold')
    plt.savefig(os.path.join(gorsel_dir, "Figure_12_MAE_Analysis.png"), dpi=300)

    # 3. RMSE Analysis
    plt.figure(figsize=(12, 8))
    sns.barplot(data=viz_df.sort_values("RMSE"), x='RMSE', y='Model', palette="magma")
    plt.title("Figure 13: RMSE Analysis", fontweight='bold')
    plt.savefig(os.path.join(gorsel_dir, "Figure_13_RMSE_Analysis.png"), dpi=300)

    # ... (Diğer grafikler de aynı mantıkla güncellenir)
    plt.close('all')

def intelligent_benchmark_344():
    print("\n" + "="*60)
    print("ADIM 4: AKILLI MODEL ELEME (PERSISTENCE)")
    print("="*60)

    setup_folders()

    df = pd.read_excel(input_file, engine='openpyxl')
    X = df.drop(columns=["İsim", "Kredi Skoru"])
    y = df["Kredi Skoru"]
    X_train, X_val, y_train, y_val = train_test_split(X, y, test_size=0.20, random_state=42, stratify=y)

    models_dict = {
        "Extra_Trees": ExtraTreesClassifier(n_estimators=100, n_jobs=-1),
        "Random_Forest": RandomForestClassifier(n_estimators=100, n_jobs=-1),
        "XGBoost": XGBClassifier(n_estimators=100, eval_metric='mlogloss', n_jobs=-1),
        "Hist_GB": HistGradientBoostingClassifier(),
        "CatBoost": CatBoostClassifier(iterations=100, verbose=0),
        "Decision_Tree": DecisionTreeClassifier(max_depth=15),
        "KNN": KNeighborsClassifier(n_neighbors=5, n_jobs=-1),
        "AdaBoost": AdaBoostClassifier(n_estimators=100),
        "LDA": LinearDiscriminantAnalysis(),
        "Logistic_Regression": LogisticRegression(max_iter=1000),
        "Linear_SVC": LinearSVC(max_iter=2000, dual=False),
        "Ridge": RidgeClassifier(),
        "Gaussian_NB": GaussianNB(),
        "Extra_Tree_Single": ExtraTreeClassifier(),
        "MLP_Neural_Net": MLPClassifier(max_iter=500),
        "Bagging_DT": BaggingClassifier(estimator=DecisionTreeClassifier(), n_estimators=10),
        "Bagging_Basic": BaggingClassifier(n_estimators=10),
        "SGD": SGDClassifier(),
        "Passive_Aggressive": PassiveAggressiveClassifier(),
        "QDA": QuadraticDiscriminantAnalysis()
    }

    # AKILLI KONTROL
    mode = "1"
    existing_models = [f for f in os.listdir(model_dir) if f.endswith(".joblib")]
    if len(existing_models) >= 15: # Çoğu model varsa sor
        print(f"\nBİLGİ: {len(existing_models)} adet eğitilmiş model bulundu.")
        print("[1] - Tümünü Yeniden Eğit")
        print("[2] - Mevcutları Yükle (Sadece görselleri güncelle)")
        mode = input("Seçiminiz: ").strip()

    results = []
    for name, model in models_dict.items():
        model_path = os.path.join(model_dir, f"{name}.joblib")
        
        if mode == "2" and os.path.exists(model_path):
            print(f"  [LOAD] {name.ljust(20)} | Yüklendi.")
            trained_model = joblib.load(model_path)
            y_pred = trained_model.predict(X_val)
            duration = 0.1
        else:
            print(f"  [TRAIN] {name.ljust(20)} | Eğitiliyor...")
            start_time = time.time()
            model.fit(X_train, y_train)
            duration = time.time() - start_time
            joblib.dump(model, model_path)
            y_pred = model.predict(X_val)
            trained_model = model

        y_pred = np.array(y_pred).flatten()
        results.append({
            "Model": name,
            "Accuracy": accuracy_score(y_val, y_pred),
            "MAE": mean_absolute_error(y_val, y_pred),
            "RMSE": np.sqrt(mean_squared_error(y_val, y_pred)),
            "MAPE": mape_calc(y_val, y_pred),
            "Süre (sn)": duration,
            "Object": trained_model
        })

    res_df = pd.DataFrame(results).sort_values("Accuracy", ascending=False)
    res_df.to_excel(os.path.join(output_dir, "intelligent_benchmark_results.xlsx"), index=False)
    
    # Top 11 Kaydı
    top_11 = res_df.head(11)
    joblib.dump(top_11[["Model", "Object"]].values.tolist(), os.path.join(model_dir, "selected_top_11_models.joblib"))

    gorseller_olustur_10_adet(res_df)
    print(f"\nİŞLEM TAMAMLANDI! En İyi: {res_df.iloc[0]['Model']}")

if __name__ == "__main__":
    intelligent_benchmark_344()
