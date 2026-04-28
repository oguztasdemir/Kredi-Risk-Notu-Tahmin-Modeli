import pandas as pd
import numpy as np
import os
import sys
import joblib
import optuna
import warnings
from tqdm import tqdm
from sklearn.model_selection import train_test_split
from sklearn.ensemble import VotingClassifier, RandomForestClassifier, ExtraTreesClassifier
from sklearn.metrics import accuracy_score, mean_absolute_error, mean_squared_error
from xgboost import XGBClassifier
from catboost import CatBoostClassifier

warnings.filterwarnings('ignore')
optuna.logging.set_verbosity(optuna.logging.WARNING)

# Yol ayarları
ana_dizin = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.append(ana_dizin)

try:
    from kullanici import klasor as base_path
except ImportError:
    base_path = r"c:\Users\User\Desktop\Kredi Hesaplaması"

input_file = os.path.join(base_path, "3_Siniflandirma_Modelleri", "Ciktilar", "1_Veri_Hazirlik", "Egitim_Datasi.xlsx")
rapor_file = os.path.join(base_path, "3_Siniflandirma_Modelleri", "Ciktilar", "9_Model_Gelistirme_Raporu.xlsx")
model_path = os.path.join(base_path, "3_Siniflandirma_Modelleri", "Modeller", "6_Final_Model", "champion_hybrid_final.joblib")

def mape_calc(y_true, y_pred):
    return np.mean(np.abs((y_true - y_pred) / (y_true + 0.0001))) * 100

def run_optimization():
    print("\n" + "="*60)
    print("ADIM 9: %100 VERİ İLE NİHAİ MODEL OPTİMİZASYONU")
    print("="*60)

    if not os.path.exists(input_file):
        print(f"HATA: Giriş dosyası bulunamadı: {input_file}")
        return
    
    # DİKKAT: Artık örnekleme (sampling) yok. Verinin tamamı kullanılıyor.
    print("> Veri yükleniyor (%100)... Bu işlem biraz zaman alabilir.")
    df = pd.read_excel(input_file)
    # Predictif olmayan sütunları çıkar
    drop_cols = ["ID", "Müşteri ID", "İsim", "Kimlik No", "Ay", "Kredi Skoru"]
    X = df.drop(columns=drop_cols, errors='ignore')
    y = df["Kredi Skoru"]
    X_train, X_val, y_train, y_val = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)

    # Otomatik Optimizasyon (10 Deneme)
    n_trials = 10 

        new_results = []
        pbar = tqdm(total=n_trials, desc="Eğitiliyor (Full Data)", unit="deneme")
        
        def objective(trial):
            # Parametre Uzayını Genişletiyoruz (Overfit'i kontrol altında tutarak)
            xgb_d = trial.suggest_int("xgb_d", 6, 14)
            xgb_n = trial.suggest_int("xgb_n", 100, 300)
            
            rf_d = trial.suggest_int("rf_d", 10, 25)
            rf_n = trial.suggest_int("rf_n", 100, 300)

            # Ağırlıklar (Üçlü Sistem)
            w_xgb = trial.suggest_float("w_xgb", 0.1, 1.0)
            w_rf = trial.suggest_float("w_rf", 0.1, 1.0)
            w_et = trial.suggest_float("w_et", 0.1, 1.0) # ExtraTrees eklendi
            
            total_w = w_xgb + w_rf + w_et
            weights = [w_xgb/total_w, w_rf/total_w, w_et/total_w]

            # Modeller
            xgb = XGBClassifier(n_estimators=xgb_n, max_depth=xgb_d, learning_rate=0.05, n_jobs=-1, verbosity=0)
            rf = RandomForestClassifier(n_estimators=rf_n, max_depth=rf_d, n_jobs=-1)
            et = ExtraTreesClassifier(n_estimators=rf_n, max_depth=rf_d, n_jobs=-1)

            hybrid = VotingClassifier(
                estimators=[('xgb', xgb), ('rf', rf), ('et', et)],
                voting='soft',
                weights=weights
            )
            
            hybrid.fit(X_train, y_train)
            preds = hybrid.predict(X_val)
            acc = accuracy_score(y_val, preds)
            
            new_results.append({
                "Hibrit_Tipi": "UCLU_SAFKAN",
                "Modeller": "XGB, RF, ET",
                "Agirliklar": f"XGB:%{weights[0]*100:.1f}, RF:%{weights[1]*100:.1f}, ET:%{weights[2]*100:.1f}",
                "Dogruluk": round(acc, 4),
                "MAE": round(mean_absolute_error(y_val, preds), 4),
                "RMSE": round(np.sqrt(mean_squared_error(y_val, preds)), 4),
                "MAPE": round(mape_calc(y_val, preds), 4),
                "Veri_Orani": "%100"
            })
            pbar.update(1)
            return acc

        study = optuna.create_study(direction="maximize")
        study.optimize(objective, n_trials=n_trials)
        pbar.close()

        # Raporu Sheet'lere ayırarak kaydet
        if os.path.exists(rapor_file):
            xls = pd.ExcelFile(rapor_file)
            history_list = [pd.read_excel(xls, sheet_name=s) for s in xls.sheet_names]
            master_df = pd.concat(history_list, ignore_index=True)
        else:
            master_df = pd.DataFrame()

        final_df = pd.concat([master_df, pd.DataFrame(new_results)], ignore_index=True)
        if "Deneme_No" in final_df.columns: final_df = final_df.drop(columns=["Deneme_No"])
        final_df.insert(0, "Deneme_No", range(1, len(final_df) + 1))

        with pd.ExcelWriter(rapor_file, engine='openpyxl') as writer:
            for type_name, group in final_df.groupby("Hibrit_Tipi"):
                group.sort_values(by="Dogruluk", ascending=False).to_excel(writer, sheet_name=type_name.replace("'", "")[:30], index=False)
        
        print(f"\n> İşlem tamamlandı. %100 Veri ile En İyi Skor: %{study.best_value*100:.2f}")
        
        cont = input("\nDevam etmek ister misiniz? (E/H): ").strip().upper()
        if cont != 'E': break

if __name__ == "__main__":
    run_optimization()
