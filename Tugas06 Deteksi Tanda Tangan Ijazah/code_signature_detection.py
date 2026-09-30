"""
TUGAS DETEKSI TANDA TANGAN IJAZAH
  crop area tanda tangan -> grayscale -> threshold (Global, Otsu, Adaptive)
  -> morfologi (opening lalu closing) -> hitung karakteristik -> putuskan PRESENT/ABSENT
"""

import glob
import os
import cv2
import numpy as np
import pandas as pd

# 1. KONFIGURASI PARAMETER UTAMA
# Area Tanda Tangan (x1, x2, y1, y2) dalam skala rasio 0 - 1
ROI_CONFIG = {
    "rektor": (0.13, 0.40, 0.70, 0.83),  # Kiri bawah
    "dekan": (0.615, 0.88, 0.70, 0.83),  # Kanan bawah
}

# Syarat Keputusan (Harus terpenuhi semua agar dianggap PRESENT)
MIN_RASIO = 0.8      # Minimal 0.8% area berisi tinta
MIN_LEBAR = 0.40     # Coretan tinta minimal selebar 40% dari ROI
MIN_KONTRAS = 30     # Tinta minimal 30 tingkat abu-abu lebih gelap dari kertas

# Dataset Folder Gambar
DATA_SET = [
    ("citra_ijazah", "dengan", "PRESENT"),
    ("citra_tanpa_ttd", "tanpa", "ABSENT"),
]

FOLDER_HASIL_GAMBAR = "hasil_deteksi"
FILE_LAPORAN_EXCEL = "hasil_deteksi.xlsx"


# 2. LANGKAH 1 dan 2: CROP ROI DAN GRAYSCALE
"""Memotong area tanda tangan, mengonversi ke grayscale, dan meredam noise."""

def potong_dan_grayscale(img, koordinat_roi):
    tinggi, lebar = img.shape[:2]
    # Putar gambar jika posisi input portrait (berdiri)
    if tinggi > lebar:
        img = cv2.rotate(img, cv2.ROTATE_90_CLOCKWISE)
        tinggi, lebar = img.shape[:2]

    x1, x2, y1, y2 = koordinat_roi
    crop = img[int(y1 * tinggi):int(y2 * tinggi), int(x1 * lebar):int(x2 * lebar)]
    
    # Grayscale + Smoothing
    gray = cv2.cvtColor(crop, cv2.COLOR_BGR2GRAY)
    gray = cv2.GaussianBlur(gray, (5, 5), 0)
    return crop, gray

# 3. LANGKAH 3: THRESHOLDING (3 METODE)
"""
Binarisasi citra abu-abu menjadi Hitam-Putih.
Menggunakan THRESH_BINARY_INV agar Tinta=Putih (255) dan Kertas=Hitam (0).
"""
def terapkan_threshold(gray):
    # 1. Global Thresholding (Manual T=127)
    _, biner_global = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY_INV)

    # 2. Otsu Thresholding (Nilai T dihitung otomatis dari varians)
    nilai_t_otsu, biner_otsu = cv2.threshold(
        gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU
    )

    # 3. Adaptive Thresholding (Nilai T dihitung dari blok lokal 35x35)
    biner_adaptive = cv2.adaptiveThreshold(
        gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 35, 15
    )

    biner_dict = {
        "Global": biner_global,
        "Otsu": biner_otsu,
        "Adaptive": biner_adaptive
    }
    return biner_dict, nilai_t_otsu


# 4. LANGKAH 4: OPERASI MORFOLOGI

def bersihkan_morfologi(biner):
    """
    Opening (Erosi -> Dilasi) : Menghapus bintik noda kotoran di kertas.
    Closing (Dilasi -> Erosi) : Menyambungkan goresan tinta yang terputus.
    """
    kernel_open = np.ones((3, 3), np.uint8)
    kernel_close = np.ones((5, 5), np.uint8)

    hasil_open = cv2.morphologyEx(biner, cv2.MORPH_OPEN, kernel_open)
    hasil_clean = cv2.morphologyEx(hasil_open, cv2.MORPH_CLOSE, kernel_close)
    return hasil_clean


# 5. LANGKAH 5: HITUNG KARAKTERISTIK (FITUR)
"""Menghitung Rasio Tinta (%), Lebar Objek Terbesar, dan Kontras Tinta/Kertas."""
def hitung_fitur(biner, gray):
    total_piksel = biner.size
    piksel_tinta = cv2.countNonZero(biner)
    
    # Fitur 1: Rasio Piksel Tinta
    rasio = (piksel_tinta / total_piksel) * 100

    # Fitur 2: Lebar Coretan Tinta Terbesar
    n_labels, _, stats, _ = cv2.connectedComponentsWithStats(biner, connectivity=8)
    if n_labels > 1:
        luas_objek = stats[1:, cv2.CC_STAT_AREA]
        idx_terbesar = luas_objek.argmax() + 1
        lebar = stats[idx_terbesar, cv2.CC_STAT_WIDTH] / biner.shape[1]
    else:
        lebar = 0.0

    # Fitur 3: Kontras Kecerahan
    if 0 < piksel_tinta < total_piksel:
        kontras = float(np.median(gray[biner == 0]) - np.mean(gray[biner > 0]))
    else:
        kontras = 0.0

    return rasio, lebar, kontras


# 6. LANGKAH 6: ATURAN KEPUTUSAN
"""PRESENT jika ketiga syarat terpenuhi sekaligus."""
def putuskan(rasio, lebar, kontras):
    if rasio >= MIN_RASIO and lebar >= MIN_LEBAR and kontras >= MIN_KONTRAS:
        return "SIGNATURE PRESENT"
    return "SIGNATURE ABSENT"


# SIMPAN VISUALISASI GRID 3 BARIS 
def beri_label_header(img, teks):
    if img.ndim == 2:
        img = cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)
    
    # Tinggi strip dinaikkan dari 22px menjadi 35px agar muat teks besar
    strip = np.full((35, img.shape[1], 3), 255, dtype=np.uint8)
    
    # FontScale dinaikkan ke 0.65 dan ketebalan 2 (Bolder & Bigger)
    teks_kapital = teks.upper()
    cv2.putText(strip, teks_kapital, (6, 24), cv2.FONT_HERSHEY_SIMPLEX, 0.65, (0, 0, 0), 2, cv2.LINE_AA)
    return np.vstack([strip, img])

def simpan_gambar_grid(judul, nama_file, crop, gray, biner_dict, morf_dict):
    """Menyusun gambar 3 baris grid dengan header judul utama yang diperbesar."""
    kosong = np.full_like(crop, 255)

    # Baris 1: Crop, Grayscale, Kosong
    baris1 = np.hstack([
        beri_label_header(crop, "Crop"),
        beri_label_header(gray, "Grayscale"),
        beri_label_header(kosong, "")
    ])

    # Baris 2: Hasil Thresholding (Global, Otsu, Adaptive)
    baris2 = np.hstack([beri_label_header(biner_dict[k], k) for k in biner_dict])

    # Baris 3: Hasil Thresholding + Morfologi
    baris3 = np.hstack([beri_label_header(morf_dict[k], f"{k} + Morfologi") for k in morf_dict])

    # Gabung ketiga baris secara vertikal
    grid = np.vstack([baris1, baris2, baris3])

    # Baris Judul Utama di paling atas dinaikkan tingginya ke 45px dan ketebalan teks 2
    bar_judul = np.full((45, grid.shape[1], 3), 255, dtype=np.uint8)
    judul_kapital = judul.upper()
    cv2.putText(bar_judul, judul_kapital, (8, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.75, (0, 0, 0), 2, cv2.LINE_AA)
    hasil_akhir = np.vstack([bar_judul, grid])

    # Simpan ke folder
    os.makedirs(FOLDER_HASIL_GAMBAR, exist_ok=True)
    cv2.imwrite(os.path.join(FOLDER_HASIL_GAMBAR, f"{nama_file}.png"), hasil_akhir)


# 7. EKSEKUSI UTAMA (MAIN LOOP, PRINT TERMINAL & EXCEL)
def main():
    laporan_hasil = []

    print("\n" + "="*95)
    print("                      PROSES DETEKSI TANDA TANGAN IJAZAH                      ")
    print("="*95)
    # Header Tabel Terminal
    print(f"{'FILE':<20} | {'ROI':<7} | {'OTSU T':<6} | {'RASIO(%)':<8} | {'LEBAR':<6} | {'KONTRAS':<7} | {'PREDIKSI':<17} | {'STATUS'}")
    print("-" * 95)

    for folder, tag, label_asli in DATA_SET:
        for path in sorted(glob.glob(os.path.join(folder, "*"))):
            img = cv2.imread(path)
            if img is None:
                continue

            nama_file = os.path.basename(path)

            for nama_roi, koordinat in ROI_CONFIG.items():
                # Step 1 & 2: Preprocessing
                crop, gray = potong_dan_grayscale(img, koordinat)
                
                # Step 3: Thresholding
                biner_dict, t_otsu = terapkan_threshold(gray)
                
                # Step 4: Morfologi
                morf_dict = {k: bersihkan_morfologi(v) for k, v in biner_dict.items()}
                
                # Step 5: Ekstraksi Fitur (dari hasil Otsu + Morfologi)
                rasio, lebar, kontras = hitung_fitur(morf_dict["Otsu"], gray)
                
                # Step 6: Logika Keputusan
                keputusan = putuskan(rasio, lebar, kontras)

                # Simpan Gambar Grid 3 Baris
                judul_gambar = f"[{tag}] {nama_file} | ROI: {nama_roi} | Otsu T={t_otsu:.0f} | {keputusan}"
                nama_out = f"{tag}_{os.path.splitext(nama_file)[0]}_{nama_roi}"
                simpan_gambar_grid(judul_gambar, nama_out, crop, gray, biner_dict, morf_dict)

                # Evaluasi Ketepatan
                is_benar = keputusan.endswith(label_asli)
                status_txt = "BENAR [OK]" if is_benar else "SALAH [X]"

                # PRINT OUTPUT KE TERMINAL SECARA REAL-TIME
                print(f"{nama_file[:20]:<20} | {nama_roi:<7} | {t_otsu:<6.0f} | {rasio:<8.2f} | {lebar:<6.2f} | {kontras:<7.1f} | {keputusan:<17} | {status_txt}")

                # Record Data untuk Excel
                laporan_hasil.append({
                    "file": nama_file,
                    "roi": nama_roi,
                    "label_asli": f"SIGNATURE {label_asli}",
                    "keputusan": keputusan,
                    "T_otsu": round(t_otsu),
                    "px_Global": cv2.countNonZero(morf_dict["Global"]),
                    "px_Otsu": cv2.countNonZero(morf_dict["Otsu"]),
                    "px_Adaptive": cv2.countNonZero(morf_dict["Adaptive"]),
                    "rasio_%": round(rasio, 2),
                    "lebar": round(lebar, 2),
                    "kontras": round(kontras, 1),
                    "benar": is_benar
                })

    if not laporan_hasil:
        print("\n[ERROR] Tidak ada citra yang diproses. Pastikan folder dataset sudah dibuat.")
        return

    # Export ke file Excel
    df_laporan = pd.DataFrame(laporan_hasil)
    with pd.ExcelWriter(FILE_LAPORAN_EXCEL) as writer:
        df_laporan.to_excel(writer, sheet_name="Hasil_Uji", index=False)
        pd.crosstab(df_laporan["label_asli"], df_laporan["keputusan"]).to_excel(writer, sheet_name="Confusion_Matrix")

    # Cetak Rangkuman Akurasi Akhir di Terminal
    total_uji = len(df_laporan)
    benar = df_laporan["benar"].sum()
    persen_akurasi = (benar / total_uji) * 100

    print("=" * 95)
    print(f" TOTAL UJI  : {total_uji} Sampel")
    print(f" PREDIKSI   : {benar} Benar, {total_uji - benar} Salah")
    print(f" AKURASI    : {persen_akurasi:.2f}%")
    print(f" EXCEL      : {FILE_LAPORAN_EXCEL}")
    print(f" GAMBAR GRID: {FOLDER_HASIL_GAMBAR}/ (Grid 3 Baris Sesuai Contoh)")
    print("=" * 95 + "\n")


if __name__ == "__main__":
    main()