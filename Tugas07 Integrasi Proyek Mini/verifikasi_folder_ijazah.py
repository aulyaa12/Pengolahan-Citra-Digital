import glob
import os
import re

import cv2
import numpy as np
import pytesseract

# ================== INPUT ==================
FOLDER_CITRA = r"E:\Pengolahan-Citra-Digital\Tugas07 Integrasi Proyek Mini\citra_ijazah"
GROUND_TRUTH = "571012022000056"               # nomor ijazah asli

# ================== KONFIGURASI ==================
ROI_NOMOR = (0.157, 0.314, 0.887, 0.988)   # (x1, x2, y1, y2) rasio 0-1
ROI_TTD = {
    "rektor": (0.13, 0.40, 0.70, 0.83),
    "dekan": (0.615, 0.88, 0.70, 0.83),
}
OCR_CONFIG = "--psm 7 -c tessedit_char_whitelist=0123456789"

MIN_RASIO = 0.8
MIN_LEBAR = 0.40
MIN_KONTRAS = 30

# ================== METODE ENHANCEMENT AREA NOMOR ==================
SHARPEN = np.array([
    [0, -1, 0],
    [-1, 5, -1],
    [0, -1, 0],
])

ENHANCEMENT = {
    "Asli": lambda img: img,
    "Mean Filter": lambda img: cv2.blur(img, (3, 3)),
    "Median Filter": lambda img: cv2.medianBlur(img, 3),
    "Gaussian Filter": lambda img: cv2.GaussianBlur(img, (3, 3), 0),
    "Sharpening": lambda img: cv2.filter2D(img, -1, SHARPEN),
}


# ================== TAHAP BERSAMA ==================
def siapkan(path):
    img = cv2.imread(path)
    if img is None:
        raise FileNotFoundError(f"Tidak bisa membaca citra: {path}")
    if img.shape[0] > img.shape[1]:
        img = cv2.rotate(img, cv2.ROTATE_90_CLOCKWISE)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    return cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8)).apply(gray)


def potong(gray, roi):
    h, w = gray.shape
    x1, x2, y1, y2 = roi
    return gray[int(y1 * h):int(y2 * h), int(x1 * w):int(x2 * w)]


# ================== CABANG NOMOR IJAZAH ==================
def baca_nomor(gray, metode):
    area = ENHANCEMENT[metode](potong(gray, ROI_NOMOR))
    teks = pytesseract.image_to_string(area, config=OCR_CONFIG)
    return re.sub(r"[^0-9]", "", teks)


def hitung_matriks_evaluasi(hasil, benar):
    """Menghitung jarak Levenshtein (jarak edit) -> CER, jumlah benar, dan Akurasi."""
    sebelumnya = list(range(len(benar) + 1))
    for i, a in enumerate(hasil, start=1):
        saat_ini = [i]
        for j, b in enumerate(benar, start=1):
            saat_ini.append(min(
                sebelumnya[j] + 1,
                saat_ini[j - 1] + 1,
                sebelumnya[j - 1] + (a != b),
            ))
        sebelumnya = saat_ini
    
    jarak_edit = sebelumnya[-1]
    len_benar = len(benar)
    
    # CER (%)
    cer = (jarak_edit / len_benar) * 100
    
    # Karakter Benar = Total Karakter Target - Jarak Edit (Min 0)
    karakter_benar = max(0, len_benar - jarak_edit)
    
    # Akurasi (%)
    akurasi = max(0.0, 100.0 - cer)
    
    return cer, karakter_benar, akurasi


# ================== CABANG TANDA TANGAN ==================
def ada_tanda_tangan(gray, roi):
    area = cv2.GaussianBlur(potong(gray, roi), (5, 5), 0)
    _, biner = cv2.threshold(area, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
    biner = cv2.morphologyEx(biner, cv2.MORPH_OPEN, np.ones((3, 3), np.uint8))
    biner = cv2.morphologyEx(biner, cv2.MORPH_CLOSE, np.ones((5, 5), np.uint8))

    tinta = cv2.countNonZero(biner)
    rasio = tinta / biner.size * 100

    n, _, stats, _ = cv2.connectedComponentsWithStats(biner, connectivity=8)
    lebar = 0.0
    if n > 1:
        terbesar = stats[1:, cv2.CC_STAT_AREA].argmax() + 1
        lebar = stats[terbesar, cv2.CC_STAT_WIDTH] / biner.shape[1]

    kontras = 0.0
    if 0 < tinta < biner.size:
        kontras = float(np.median(area[biner == 0]) - np.mean(area[biner > 0]))

    return rasio >= MIN_RASIO and lebar >= MIN_LEBAR and kontras >= MIN_KONTRAS


# ================== PROGRAM UTAMA ==================
def main():
    ekstensi = ("*.jpg", "*.jpeg", "*.png", "*.JPG", "*.JPEG", "*.PNG")
    daftar_gambar = []
    for ext in ekstensi:
        daftar_gambar.extend(glob.glob(os.path.join(FOLDER_CITRA, ext)))

    daftar_gambar = sorted(list(set(daftar_gambar)))

    if not daftar_gambar:
        print(f"Tidak ada file citra yang ditemukan di folder: {FOLDER_CITRA}")
        return

    total_target = len(GROUND_TRUTH)

    print("=" * 80)
    print(f"MEMPROSES {len(daftar_gambar)} GAMBAR DARI FOLDER: {FOLDER_CITRA}")
    print(f"TARGET GROUND TRUTH : {GROUND_TRUTH} ({total_target} Digit)")
    print("=" * 80)

    for idx, path_gambar in enumerate(daftar_gambar, start=1):
        nama_file = os.path.basename(path_gambar)
        try:
            gray = siapkan(path_gambar)
            ada = all(ada_tanda_tangan(gray, roi) for roi in ROI_TTD.values())

            # Evaluasi ke-5 metode enhancement
            hasil_metode = {}
            for me in ENHANCEMENT:
                teks_ocr = baca_nomor(gray, me)
                cer_val, k_benar, akurasi_val = hitung_matriks_evaluasi(teks_ocr, GROUND_TRUTH)
                hasil_metode[me] = {
                    "teks": teks_ocr,
                    "cer": cer_val,
                    "k_benar": k_benar,
                    "akurasi": akurasi_val,
                }

            # Cari metode dengan CER terkecil (Akurasi tertinggi)
            metode_terbaik = min(hasil_metode, key=lambda k: hasil_metode[k]["cer"])
            d_terbaik = hasil_metode[metode_terbaik]

            print(f"\n[{idx}/{len(daftar_gambar)}] FILE: {nama_file}")
            print("-" * 80)
            print(f"Hasil OCR Terbaik  : {d_terbaik['teks'] or '(tidak terbaca)'} (Metode: {metode_terbaik})")
            print(f"Karakter Benar     : {d_terbaik['k_benar']}/{total_target} Digit")
            print(f"Tingkat Error (CER): {d_terbaik['cer']:.2f}%")
            print(f"Akurasi OCR        : {d_terbaik['akurasi']:.2f}%")
            print(f"Status Tanda Tangan: {'PRESENT' if ada else 'ABSENT'}")
            
            print("\nRincian Perbandingan Metode Enhancement:")
            header = f"  {'Metode Enhancement':<18} | {'Hasil OCR':<18} | {'Benar':<8} | {'CER (%)':<9} | {'Akurasi (%)':<10}"
            print(header)
            print("  " + "-" * (len(header) - 2))
            
            # Urutkan dari CER terkecil
            for nama_m, data in sorted(hasil_metode.items(), key=lambda x: x[1]["cer"]):
                teks_tampil = data["teks"] if data["teks"] else "(kosong)"
                print(
                    f"  {nama_m:<18} | {teks_tampil:<18} | "
                    f"{data['k_benar']:>2}/{total_target:<5} | "
                    f"{data['cer']:>7.2f}% | "
                    f"{data['akurasi']:>9.2f}%"
                )
            print("-" * 80)

        except Exception as e:
            print(f"\n[{idx}/{len(daftar_gambar)}] FILE: {nama_file} -> Gagal diproses ({e})")

    print("\n" + "=" * 80)
    print("PROSES BATCH SELESAI")
    print("=" * 80)


if __name__ == "__main__":
    main()