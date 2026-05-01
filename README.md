# Kredi Skoru Sınıflandırma ve Tahmin Modeli

Bu proje, bankacılık verileri üzerinde kapsamlı veri temizliği, özellik seçimi ve gelişmiş makine öğrenmesi tekniklerini kullanarak kredi skorlarını (İyi, Standart, Kötü) tahmin eden uçtan uca bir boru hattı (pipeline) sunmaktadır. Proje, 100.000+ finansal kayıt üzerinde gerçekleştirilen 3 ana aşamadan oluşmaktadır.

## Proje Aşamaları

### 1. Veri Hazırlama ve Restorasyon
*   **Veri Onarımı:** Eksik ve hatalı verilerin (ID bazlı trend analiziyle) bilimsel olarak doldurulması.
*   **Normalizasyon:** Aykırı değerlerin (outliers) temizlenmesi ve verinin standart ölçeğe (Scaling) getirilmesi.
*   **Kategorik Dönüşüm:** Metin tabanlı verilerin makine öğrenmesine uygun sayısal formata getirilmesi.

### 2. Özellik Seçimi (Feature Selection)
*   **İstatistiksel Eleme:** Filter (Correlation), Wrapper (RFE) ve Embedded yöntemlerin kıyaslanması.
*   **Boyut İndirgeme:** PCA (Temel Bileşen Analizi) ve Manifold Öğrenme (t-SNE) ile veri temsilinin optimize edilmesi.
*   **Data Leakage Önleme:** ID, İsim gibi tahmin gücü olmayan ancak modelin ezberlemesine (leakage) neden olan sütunların sistematik olarak dışlanması.

### 3. Sınıflandırma Modelleri ve Hibrit Mimari
*   **Algoritma Havuzu:** XGBoost, LightGBM, CatBoost, Random Forest ve Yapay Sinir Ağları (ANN) dahil 20+ algoritmanın benchmark testleri.
*   **Hibrit Sistem:** En iyi sonuç veren modellerin 'Stacking Ensemble' yöntemiyle birleştirilmesi.
*   **Metrik Analizi:** SMOTE ile dengelenmiş veri seti üzerinde ROC/PR eğrileri ve F1-Skoru optimizasyonu.

## Kullanılan Teknolojiler
*   **Dil:** Python 3.x
*   **Veri Analizi:** Pandas, NumPy
*   **Makine Öğrenmesi:** Scikit-learn, XGBoost, LightGBM, CatBoost
*   **Optimizasyon:** Optuna (Bayesian Optimization)
*   **Görselleştirme:** Matplotlib, Seaborn
*   **Raporlama:** Python-pptx (Otomatik sunum), Pandas ExcelWriter

## Dosya Yapısı
*   `1_Veri_Manipulasyonu/`: Veri temizleme ve hazırlık scriptleri.
*   `2_Feature_Selection/`: Özellik mühendisliği ve seçim yöntemleri.
*   `3_Siniflandirma_Modelleri/`: Model eğitimi, testleri ve final hibrit sistem.
*   `0_Dataset/`: Ham ve işlenmiş veri dosyaları (Excel formatında).
*   `main.py`: Tüm sistemi yöneten interaktif konsol menüsü.

## Kurulum ve Çalıştırma
Projeyi yerel ortamınızda çalıştırmak için:

1. Depoyu klonlayın.
2. Gerekli kütüphaneleri yükleyin: `pip install pandas numpy scikit-learn matplotlib seaborn optuna xgboost lightgbm catboost python-pptx openpyxl`
3. **kullanici.py Yapılandırması:** Proje ana dizininde bulunan `kullanici.py` dosyasını açın ve `klasor` değişkenine projenin bilgisayarınızdaki tam yolunu yazın (Örn: `klasor = r"C:\Projeler\Kredi_Hesaplamasi"`). Bu ayar, tüm scriptlerin veri yollarını otomatik olarak bulmasını sağlar.
4. Ana dizindeki `main.py` dosyasını çalıştırarak interaktif menü üzerinden istediğiniz adımı tetikleyebilirsiniz.

## Final Notu
Bu çalışma, veri sızıntısından arındırılmış, %81.31 test başarısına sahip ve denetlenebilir (Forensic Audit) raporlar üreten akademik standartlarda bir makine öğrenmesi projesidir.

---
**Not:** Proje kapsamında eğitilen yüksek boyutlu model dosyaları (`.joblib`), GitHub'ın dosya boyutu limitlerini (100MB) aşması nedeniyle bu depoya dahil edilmemiştir. Bu modeller yerel ortamda eğitim scriptleri çalıştırılarak yeniden oluşturulabilir.
