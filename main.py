import os
import subprocess
import sys
import time

# Ana dizin ve kullanıcı ayarları
try:
    from kullanici import klasor as base_path
except ImportError:
    base_path = os.path.dirname(os.path.abspath(__file__))

def run_script(script_path):
    """Verilen scripti çalıştırır ve sonucunu raporlar."""
    if not os.path.exists(script_path):
        print(f"\n[HATA] Script bulunamadı: {os.path.basename(script_path)}")
        return False
    
    print(f"\n" + "-"*40)
    print(f">>> BAŞLATILDI: {os.path.basename(script_path)}")
    print("-"*40)
    start_time = time.time()
    
    try:
        # Scripti çalıştır
        result = subprocess.run([sys.executable, script_path], capture_output=False, text=True)
        
        if result.returncode == 0:
            duration = time.time() - start_time
            print(f"\n[TAMAMLANDI] {os.path.basename(script_path)} (Süre: {duration:.2f} sn)")
            return True
        else:
            print(f"\n[HATA] {os.path.basename(script_path)} başarısız oldu.")
            return False
    except Exception as e:
        print(f"\n[KRİTİK SİSTEM HATASI] {str(e)}")
        return False

def show_sub_menu(title, scripts):
    """Alt menüyü gösterir ve seçim yaptırır."""
    while True:
        print(f"\n" + "="*50)
        print(f"ALT MENÜ: {title}")
        print("="*50)
        print("A - Tüm Adımları Sırayla Çalıştır")
        for i, script in enumerate(scripts, 1):
            print(f"{i} - {os.path.basename(script)}")
        print("\n0 - GERİ DÖN")
        print("Q - ÇIKIŞ")
        
        choice = input("\nSeçiminiz: ").strip().upper()
        
        if choice == '0':
            return True # Geri dön
        elif choice == 'Q':
            print("Sistemden çıkılıyor...")
            sys.exit()
        elif choice == 'A':
            for s in scripts:
                if not run_script(s): break
        else:
            try:
                idx = int(choice) - 1
                if 0 <= idx < len(scripts):
                    run_script(scripts[idx])
                else:
                    print("Geçersiz numara!")
            except ValueError:
                print("Lütfen geçerli bir seçim yapın!")

def main():
    # Script Listeleri
    p1_dir = os.path.join(base_path, "1_Veri_Manipülasyonu", "Python_Kodlari")
    p2_dir = os.path.join(base_path, "2_Feature_Selection", "Python_Kodlari")
    p3_dir = os.path.join(base_path, "3_Siniflandirma_Modelleri", "Python_Kodlari")

    phase1 = [
        os.path.join(p1_dir, "1_veri_temizleme_ve_cevirme.py"),
        os.path.join(p1_dir, "2_id_kontrolu.py"),
        os.path.join(p1_dir, "3_veri_birlestirme.py"),
        os.path.join(p1_dir, "9_anomali_duzeltme.py"),
        os.path.join(p1_dir, "11_final_kiyaslama_ve_denetim.py"),
        os.path.join(p1_dir, "12_musteri_tutarlilik_raporu.py")
    ]

    phase2 = [
        os.path.join(p2_dir, "1_filter_method_korelasyon.py"),
        os.path.join(p2_dir, "2_embedded_method_onem.py"),
        os.path.join(p2_dir, "3_pca_analizi.py"),
        os.path.join(p2_dir, "4_manifold_learning_tsne.py"),
        os.path.join(p2_dir, "5_final_ozet_karsilastirma.py")
    ]

    phase3 = [
        os.path.join(p3_dir, "1_veri_hazirlik_ve_bolme.py"),
        os.path.join(p3_dir, "2_karar_agaci_modeli.py"),
        os.path.join(p3_dir, "3_random_forest_modeli.py"),
        os.path.join(p3_dir, "4_mega_benchmark_20_model.py"),
        os.path.join(p3_dir, "5_hibrit_ve_optimizasyon.py"),
        os.path.join(p3_dir, "6_final_model_egitimi.py"),
        os.path.join(p3_dir, "7_final_tahminleme.py")
    ]

    while True:
        print("\n" + "#"*60)
        print("   KREDİ NOTU SINIFLANDIRMA SİSTEMİ - ANA KONTROL PANELİ")
        print("#"*60)
        print("1 - [KLASÖR] Veri Manipülasyonu ve Restorasyon")
        print("2 - [KLASÖR] Özellik Seçimi (Feature Selection)")
        print("3 - [KLASÖR] Sınıflandırma ve AI Modelleri")
        print("-" * 30)
        print("F - [FULL] Tüm Projeyi Baştan Sona Çalıştır")
        print("Q - ÇIKIŞ")
        
        choice = input("\nLütfen bir klasör seçin: ").strip().upper()
        
        if choice == '1':
            show_sub_menu("Veri Manipülasyonu", phase1)
        elif choice == '2':
            show_sub_menu("Özellik Seçimi", phase2)
        elif choice == '3':
            show_sub_menu("Sınıflandırma & AI", phase3)
        elif choice == 'F':
            all_scripts = phase1 + phase2 + phase3
            for s in all_scripts:
                if not run_script(s): break
        elif choice == 'Q':
            print("Sistem kapatılıyor. İyi çalışmalar!")
            break
        else:
            print("Geçersiz seçim!")

if __name__ == "__main__":
    main()
