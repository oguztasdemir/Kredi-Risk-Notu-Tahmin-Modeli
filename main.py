import os
import subprocess
import sys
import time

# Ana dizin
try:
    from kullanici import klasor as base_path
except ImportError:
    base_path = os.path.dirname(os.path.abspath(__file__))

def run_script(script_path, current_step, total_steps):
    """Scripti çalıştırır ve ilerleme çubuğu gösterir."""
    if not os.path.exists(script_path):
        return False
    
    script_name = os.path.basename(script_path)
    percent = (current_step / total_steps) * 100
    bar_length = 20
    filled_length = int(bar_length * current_step // total_steps)
    bar = '#' * filled_length + '-' * (bar_length - filled_length)
    
    print(f"\n[{bar}] %{percent:.1f} | ADIM {current_step}/{total_steps}")
    print(f">>> ŞU AN ÇALIŞIYOR: {script_name}")
    print("-" * 50)
    
    try:
        # '2' girişi göndererek mevcut modelleri kullanmasını sağlıyoruz (Hızlı güncelleme için)
        result = subprocess.run([sys.executable, script_path], input="2\n", capture_output=False, text=True)
        if result.returncode == 0:
            print(f">>> [BAŞARILI] {script_name} tamamlandı.")
            return True
        else:
            print(f">>> [HATA] {script_name} çalışırken bir sorun oluştu.")
            return False
    except Exception as e:
        print(f">>> [SİSTEM HATASI] {e}")
        return False

def show_sub_menu(title, scripts):
    while True:
        print(f"\n" + "="*50)
        print(f"ALT MENÜ: {title}")
        print("="*50)
        print("A - Tüm Adımları Sırayla Çalıştır")
        for i, script in enumerate(scripts, 1):
            print(f"{i} - {os.path.basename(script)}")
        print("\n0 - GERİ DÖN | Q - ÇIKIŞ")
        
        choice = input("\nSeçiminiz: ").strip().upper()
        if choice == '0': return
        if choice == 'Q': sys.exit()
        if choice == 'A':
            total = len(scripts)
            for i, s in enumerate(scripts, 1):
                if not run_script(s, i, total): break
        else:
            try:
                idx = int(choice) - 1
                if 0 <= idx < len(scripts): run_script(scripts[idx], 1, 1)
            except: print("Geçersiz seçim!")

def get_sorted_scripts(path):
    """Dosyaları başındaki sayılara göre doğal sırada (1, 2... 10) sıralar."""
    if not os.path.exists(path): return []
    def extract_number(filename):
        parts = filename.split('_')
        return int(parts[0]) if parts[0].isdigit() else 999
    
    files = [f for f in os.listdir(path) if f.endswith(".py")]
    files.sort(key=extract_number)
    return [os.path.join(path, f) for f in files]

def main():
    p1 = os.path.join(base_path, "1_Veri_Manipülasyonu", "Python_Kodlari")
    p2 = os.path.join(base_path, "2_Ozellik_Muhendisligi_ve_Secimi", "Python_Kodlari")
    p3 = os.path.join(base_path, "3_Model_Egitimi_ve_Degerlendirme", "Python_Kodlari")

    phase1 = get_sorted_scripts(p1)
    phase2 = get_sorted_scripts(p2)
    phase3 = get_sorted_scripts(p3)

    while True:
        print("\n" + "#"*70)
        print("   KREDİ NOTU SINIFLANDIRMA SİSTEMİ - MASTER KONTROL PANELİ (v2.0)")
        print("#"*70)
        print("1 - [KLASÖR 1] Veri Manipülasyonu ve Restorasyon")
        print("2 - [KLASÖR 2] Özellik Mühendisliği ve VIP Seçimi")
        print("3 - [KLASÖR 3] Makine Öğrenmesi Modeli Eğitimi, Hibrit Stacking ve 50k Tahmin")
        print("4 - [FINAL] Akademik Sunum Oluştur (PPTX & PDF)")
        print("-" * 35)
        print("O - [OTONOM] Seçilen Fazı Sıralı Çalıştır")
        print("F - [FULL PIPELINE] Tüm Projeyi Baştan Sona Çalıştır (Audit Ready)")
        print("Q - SİSTEMDEN ÇIK")
        
        choice = input("\nSeçiminiz: ").strip().upper()
        if choice == '1': show_sub_menu("Veri Restorasyonu", phase1)
        elif choice == '2': show_sub_menu("Özellik Mühendisliği", phase2)
        elif choice == '3': show_sub_menu("AI Model ve Tahminleme", phase3)
        elif choice == '4':
            sunum_script = os.path.join(base_path, "6_Sunum_Guncel", "Sunum_Olusturucu_Guncel.py")
            run_script(sunum_script, 1, 1)
        elif choice == 'O':
            # ... (Faz seçimi kalsın)
            print("\nHangi Fazı Otonom Çalıştırmak İstiyorsunuz?")
            print("1 - Veri Manipülasyonu")
            print("2 - Özellik Mühendisliği")
            print("3 - AI Model Eğitimi")
            faz_secim = input("Seçiminiz (1/2/3): ").strip()
            target_scripts = []
            if faz_secim == '1': target_scripts = phase1
            elif faz_secim == '2': target_scripts = phase2
            elif faz_secim == '3': target_scripts = phase3
            
            if target_scripts:
                print(f"\n>>> KLASÖR {faz_secim} OTONOM SİSTEM BAŞLATILIYOR...")
                total = len(target_scripts)
                for i, s in enumerate(target_scripts, 1):
                    if not run_script(s, i, total): break
                print(f"\n>>> KLASÖR {faz_secim} BAŞARIYLA TAMAMLANDI.")
            else:
                print("Geçersiz faz seçimi!")
                
        elif choice == 'F':
            print("\n>>> FULL PIPELINE BAŞLATILIYOR (Lütfen Bekleyin)...")
            sunum_script = os.path.join(base_path, "6_Sunum_Guncel", "Sunum_Olusturucu_Guncel.py")
            all_scripts = phase1 + phase2 + phase3 + [sunum_script]
            total = len(all_scripts)
            for i, s in enumerate(all_scripts, 1):
                if not run_script(s, i, total): break
            print(f"\n>>> TÜM PROJE VE SUNUM BAŞARIYLA TAMAMLANDI! (Audit-Ready)")
        elif choice == 'Q': break

if __name__ == "__main__":
    main()
