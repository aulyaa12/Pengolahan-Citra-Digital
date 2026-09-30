import cv2
import numpy as np
import matplotlib.pyplot as plt
import glob
import os

# KONFIGURASI
# Menentukan folder script dan folder output secara otomatis
FOLDER_SCRIPT = os.path.dirname(os.path.abspath(__file__))
FOLDER_OUTPUT = os.path.join(FOLDER_SCRIPT, 'output')
os.makedirs(FOLDER_OUTPUT, exist_ok=True)

# Mendeteksi seluruh file ijazah dengan pola nama ijazah*.jpg
daftar_ijazah = sorted(glob.glob(os.path.join(FOLDER_SCRIPT, 'ijazah*.jpg')))

print("Folder script :", FOLDER_SCRIPT)
print("Folder output :", FOLDER_OUTPUT)
print("Jumlah file ijazah yang ditemukan:", len(daftar_ijazah))
for f in daftar_ijazah:
    print("   -", os.path.basename(f))
print()

# PROSES UTAMA
statistik_semua = []

for path_file in daftar_ijazah:
    nama_file = os.path.basename(path_file)
    base_name = os.path.splitext(nama_file)[0]
    print("Memproses:", nama_file)
  
    # 1. Load citra dan konversi ke grayscale
    img_bgr = cv2.imread(path_file)
    img_rgb = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB)
    img_gray = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2GRAY)

    # 2. Perhitungan statistik intensitas piksel
    stats = {
        'nama'   : nama_file,
        'min'    : int(img_gray.min()),
        'max'    : int(img_gray.max()),
        'mean'   : float(img_gray.mean()),
        'median' : float(np.median(img_gray)),
        'std'    : float(img_gray.std()),
    }
    statistik_semua.append(stats)

    print("  Nilai minimum  :", stats['min'])
    print("  Nilai maksimum :", stats['max'])
    print("  Nilai rata-rata:", round(stats['mean'], 2))
    print("  Nilai median   :", round(stats['median'], 2))
    print("  Standar deviasi:", round(stats['std'], 2))

    # 3. Enhancement citra
    # Metode 1: Histogram Equalization (global)
    eq_img = cv2.equalizeHist(img_gray)

    # Metode 2: CLAHE (Contrast Limited Adaptive Histogram Equalization)
    clahe = cv2.createCLAHE(clipLimit=2, tileGridSize=(8, 8))
    clahe_img = clahe.apply(img_gray)

    # 4. Penyimpanan citra hasil
    cv2.imwrite(os.path.join(FOLDER_OUTPUT, f'{base_name}_rgb.png'),   img_rgb)
    cv2.imwrite(os.path.join(FOLDER_OUTPUT, f'{base_name}_gray.png'),  img_gray)
    cv2.imwrite(os.path.join(FOLDER_OUTPUT, f'{base_name}_eq.png'),    eq_img)
    cv2.imwrite(os.path.join(FOLDER_OUTPUT, f'{base_name}_clahe.png'), clahe_img)

    # 5. Visualisasi gabungan: 2 baris x 4 kolom
    #    Baris 1: citra (RGB, grayscale, equalization, CLAHE)
    #    Baris 2: histogram dari masing-masing citra
    fig, axes = plt.subplots(2, 4, figsize=(22, 11))
    fig.suptitle(f"Analisis Citra: {nama_file}", fontsize=16, fontweight='bold')

    # ---------- BARIS 1: CITRA ----------
    # Kolom 1: Citra RGB asli
    axes[0, 0].imshow(img_rgb)
    axes[0, 0].set_title("Citra Asli (RGB)", fontsize=12)
    axes[0, 0].axis('off')

    # Kolom 2: Citra grayscale
    axes[0, 1].imshow(img_gray, cmap='gray')
    axes[0, 1].set_title("Citra Grayscale", fontsize=12)
    axes[0, 1].axis('off')

    # Kolom 3: Hasil Histogram Equalization
    axes[0, 2].imshow(eq_img, cmap='gray')
    axes[0, 2].set_title("Histogram Equalization", fontsize=12)
    axes[0, 2].axis('off')

    # Kolom 4: Hasil CLAHE
    axes[0, 3].imshow(clahe_img, cmap='gray')
    axes[0, 3].set_title("CLAHE (clipLimit = 2)", fontsize=12)
    axes[0, 3].axis('off')

    # ---------- BARIS 2: HISTOGRAM ----------
    # Kolom 1: Histogram RGB asli (3 kanal)
    for i, color in enumerate(('r', 'g', 'b')):
        hist_rgb = cv2.calcHist([img_rgb], [i], None, [256], [0, 256])
        axes[1, 0].plot(hist_rgb, color=color, label=color.upper(), linewidth=1)
    axes[1, 0].set_title("Histogram RGB (Citra Asli)", fontsize=12)
    axes[1, 0].set_xlim([0, 256])
    axes[1, 0].set_xlabel("Intensitas Piksel")
    axes[1, 0].set_ylabel("Frekuensi")
    axes[1, 0].legend()
    axes[1, 0].grid(True, alpha=0.3)

    # Kolom 2: Histogram grayscale
    hist_gray = cv2.calcHist([img_gray], [0], None, [256], [0, 256])
    axes[1, 1].plot(hist_gray, color='black', linewidth=1)
    axes[1, 1].set_title("Histogram Grayscale", fontsize=12)
    axes[1, 1].set_xlim([0, 256])
    axes[1, 1].set_xlabel("Intensitas Piksel")
    axes[1, 1].set_ylabel("Frekuensi")
    axes[1, 1].grid(True, alpha=0.3)

    # Kolom 3: Histogram setelah equalization
    hist_eq = cv2.calcHist([eq_img], [0], None, [256], [0, 256])
    axes[1, 2].plot(hist_eq, color='orange', linewidth=1)
    axes[1, 2].set_title("Histogram Equalization", fontsize=12)
    axes[1, 2].set_xlim([0, 256])
    axes[1, 2].set_xlabel("Intensitas Piksel")
    axes[1, 2].set_ylabel("Frekuensi")
    axes[1, 2].grid(True, alpha=0.3)

    # Kolom 4: Histogram setelah CLAHE
    hist_clahe = cv2.calcHist([clahe_img], [0], None, [256], [0, 256])
    axes[1, 3].plot(hist_clahe, color='green', linewidth=1)
    axes[1, 3].set_title("Histogram CLAHE", fontsize=12)
    axes[1, 3].set_xlim([0, 256])
    axes[1, 3].set_xlabel("Intensitas Piksel")
    axes[1, 3].set_ylabel("Frekuensi")
    axes[1, 3].grid(True, alpha=0.3)

    # Tata letak dan penyimpanan figure
    plt.tight_layout(rect=[0, 0, 1, 0.96])
    plt.savefig(os.path.join(FOLDER_OUTPUT, f'{base_name}_analysis.png'),
                dpi=120, bbox_inches='tight')
    plt.close()

    print("  Hasil disimpan sebagai:", f'{base_name}_analysis.png')

# TABEL PERBANDINGAN SELURUH IJAZAH
print()
print("TABEL PERBANDINGAN STATISTIK SELURUH IJAZAH")
print(f"{'File':<15} {'Min':>5} {'Max':>5} {'Mean':>8} {'Median':>8} {'Std':>7}")
print("-" * 80)

for s in statistik_semua:
    print(f"{s['nama']:<15} {s['min']:>5} {s['max']:>5} "
          f"{s['mean']:>8.2f} {s['median']:>8.2f} {s['std']:>7.2f}")

