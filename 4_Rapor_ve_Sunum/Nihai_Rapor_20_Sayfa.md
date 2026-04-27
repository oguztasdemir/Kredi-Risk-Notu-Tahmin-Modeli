# KREDİ NOTU SINIFLANDIRMA VE TAHMİNLEME PROJESİ: TEKNİK RAPOR
**Hazırlayan:** [İsim Soyisim]  
**Tarih:** 27 Nisan 2026  
**Konu:** Yapay Zeka Destekli Finansal Risk Analizi ve Hibrit Model Optimizasyonu

## ÖZET (ABSTRACT)
Bu çalışma, 150.000 satırlık devasa ve kirli bir finansal veri setinin, modern veri bilimi teknikleriyle restore edilmesini, en anlamlı özelliklerin seçilmesini ve %82.56 doğruluk oranına sahip bir "Hibrit Şampiyon Model" ile 50.000 kişilik bir tahmin havuzunun analiz edilmesini kapsamaktadır...

---

## 1. GİRİŞ
Finansal dünyada kredi skoru tahmini, bankacılık ve risk yönetimi için hayati bir önem taşır. Ancak ham veriler genellikle eksik, hatalı ve gürültülüdür. Bu proje, ham veriyi "işlenebilir altın" değerine getiren 22 adımlık bir hattı (Pipeline) temsil eder...

---

## 2. VERİ RESTORASYONU VE TEMİZLİK (PHASE 1)
### 2.1. ID Bazlı Eksik Veri Tamamlama
Veri setindeki en büyük sorun olan %35'lik eksiklik oranı, "Müşteri ID" bazlı deterministik bir restorasyon algoritmasıyla %0'a indirilmiştir.

### 2.2. Finansal Anomali Onarımı
Negatif kredi borcu, imkansız yaş (120+) ve tutarsız gelir-gider dengeleri, istatistiksel sınırlar (Z-Score) kullanılarak düzeltilmiştir...

---

## 3. ÖZELLİK MÜHENDİSLİĞİ (PHASE 2)
### 3.1. Çok Boyutlu İstatistiksel Eleme
Korelasyon matrisi ve PCA (Temel Bileşen Analizi) kullanılarak 50 değişken içerisinden model başarısına doğrudan katkı sağlayan en iyi 20 değişken (VIP Özellikler) izole edilmiştir...

---

## 4. MAKİNE ÖĞRENMESİ METODOLOJİSİ (PHASE 3)
### 4.1. Mega Benchmark ve Scaling
20 farklı algoritma (XGBoost, CatBoost, MLP, Random Forest vb.) 'StandardScaler' ölçeklendirmesi altında yarıştırılmıştır.

### 4.2. Hibrit Yapı: Voting Classifier
Extra Trees, Random Forest ve XGBoost modellerinin "Yumuşak Oylama" (Soft Voting) yöntemiyle birleştirilmesiyle en stabil sonuç elde edilmiştir...

---

## 5. SONUÇLAR VE ANALİZ
### 5.1. Performans Metrikleri
- Doğruluk: %82.56
- MAE: 0.21
- RMSE: 0.44

[... 20 Sayfalık Devam Eden Teknik Detaylar ...]
