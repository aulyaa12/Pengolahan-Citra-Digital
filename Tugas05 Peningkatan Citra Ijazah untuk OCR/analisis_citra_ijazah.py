import cv2
import numpy as np
import pytesseract
import os
import re
import glob
import csv
from collections import defaultdict

# ================== KONFIGURASI ==================
FOLDER_CITRA = "citra_ijazah"  #nama folder berisi 9 gambar
GROUND_TRUTH = "571012022000056"      
OUTPUT_FOLDER = "hasil_filter"
os.makedirs(OUTPUT_FOLDER, exist_ok=True)


# ================== ROTASI, CROP NOMOR IJAZAH, & GRAYSCALE ==================
def rotasi_upright(img):
    #Jika ijazah portrait maka ubah jadi landscape (putar 90 derajat) 
    h, w = img.shape[:2]
    if h > w:
        return cv2.rotate(img, cv2.ROTATE_90_CLOCKWISE)
    return img

def crop_nomor_ijazah(img_upright):
    #Crop bagian 'Nomor ijazah: xxxxxxxxxxxxxxx' saja (hanya angkanya)
    h, w = img_upright.shape[:2]
    y1, y2 = int(0.887 * h), int(0.988 * h)
    x1, x2 = int(0.157 * w), int(0.314 * w)
    return img_upright[y1:y2, x1:x2]

def siapkan_citra_nomor(path_citra):
    #Baca file -> jadikan tegak -> crop area nomor ijazah -> grayscale.
    img = cv2.imread(path_citra)
    if img is None:
        raise FileNotFoundError(f"Tidak bisa membaca citra: {path_citra}")
    img = rotasi_upright(img)
    crop = crop_nomor_ijazah(img)
    gray = cv2.cvtColor(crop, cv2.COLOR_BGR2GRAY)
    return gray


# ================== 4 FUNGSI FILTER ==================
def mean_filter(img):
    return cv2.blur(img, (3, 3))

def median_filter(img):
    return cv2.medianBlur(img, 3)

def gaussian_filter(img):
    return cv2.GaussianBlur(img, (3, 3), 0)

def sharpen(img):
    #Penajaman (sharpening): mempertegas tepi/garis pada teks.
    kernel = np.array([[0, -1, 0],
                        [-1, 5, -1],
                        [0, -1, 0]])
    return cv2.filter2D(img, -1, kernel)


# ================== FUNGSI OCR ==================
def ocr_text(img_gray):
    #OCR khusus satu baris angka. psm 7 = anggap citra berisi satu baris teks.
    config = "--psm 7 -c tessedit_char_whitelist=0123456789"
    return pytesseract.image_to_string(img_gray, config=config).strip()

def bersihkan_teks(teks):
    #Hanya sisakan digit/angka
    return re.sub(r"[^0-9]", "", teks)

def hitung_akurasi(hasil_ocr, ground_truth):
    #Bandingkan digit hasil OCR dengan ground truth posisi-per-posisi.
    ocr_bersih = bersihkan_teks(hasil_ocr)
    gt_bersih = bersihkan_teks(ground_truth)
    if len(gt_bersih) == 0:
        return 0, 0.0
    n = max(len(ocr_bersih), len(gt_bersih))
    ocr_pad = ocr_bersih.ljust(n)
    gt_pad = gt_bersih.ljust(n)
    jumlah_benar = sum(1 for a, b in zip(ocr_pad, gt_pad) if a == b and a != " ")
    akurasi = jumlah_benar / len(gt_bersih) * 100
    return jumlah_benar, akurasi


# ================== PROSES UTAMA ==================
def proses_satu_citra(path_citra, ground_truth):
    nama_file = os.path.basename(path_citra)
    nomor_gray = siapkan_citra_nomor(path_citra)

    metode = {
        "Asli": nomor_gray,
        "Mean_Filter": mean_filter(nomor_gray),
        "Median_Filter": median_filter(nomor_gray),
        "Gaussian_Filter": gaussian_filter(nomor_gray),
        "Sharpening": sharpen(nomor_gray),
    }

    hasil = []
    for nama_metode, citra in metode.items():
        nama_output = f"{OUTPUT_FOLDER}/{os.path.splitext(nama_file)[0]}_{nama_metode}.png"
        cv2.imwrite(nama_output, citra)

        teks_ocr = ocr_text(citra)
        benar, akurasi = hitung_akurasi(teks_ocr, ground_truth)

        hasil.append({
            "file": nama_file,
            "metode": nama_metode.replace("_", " "),
            "hasil_ocr": teks_ocr,
            "karakter_benar": f"{benar}/{len(bersihkan_teks(ground_truth))}",
            "akurasi": round(akurasi, 2),
        })
    return hasil


def cetak_header_tabel():
    #Cetak baris header + garis pemisah tabel (dipakai berulang per file).
    print(f"{'File':<30}{'Metode':<18}{'Hasil OCR':<20}{'Char Benar':<12}{'Akurasi (%)'}")
    print("-" * 97)


def cetak_tabel_per_file(semua_hasil):
    #Cetak hasil OCR dalam tabel terpisah untuk tiap file citra,
    #supaya tidak tertimpa jadi satu tabel besar dan lebih enak dibaca.
    hasil_per_file = defaultdict(list)
    for r in semua_hasil:
        hasil_per_file[r["file"]].append(r)

    for nama_file, daftar_hasil in hasil_per_file.items():
        cetak_header_tabel()
        for r in daftar_hasil:
            print(f"{r['file']:<30}{r['metode']:<18}{r['hasil_ocr']:<20}{r['karakter_benar']:<12}{r['akurasi']}")
        print()  # baris kosong pemisah antar tabel/gambar


def main():
    semua_hasil = []
    daftar_citra = sorted(
        glob.glob(f"{FOLDER_CITRA}/*.png")
        + glob.glob(f"{FOLDER_CITRA}/*.jpg")
        + glob.glob(f"{FOLDER_CITRA}/*.jpeg")
    )

    if not daftar_citra:
        print(f"Tidak ada citra ditemukan di folder '{FOLDER_CITRA}'. "
              f"Pastikan 9 gambar sudah dimasukkan ke folder tersebut.")
        return

    for path in daftar_citra:
        semua_hasil.extend(proses_satu_citra(path, GROUND_TRUTH))

    # cetak tabel terpisah per file (satu tabel per gambar)
    cetak_tabel_per_file(semua_hasil)

    # ringkasan rata-rata akurasi per metode (dari 9 gambar) -> untuk tabel laporan
    akumulasi = defaultdict(list)
    for r in semua_hasil:
        akumulasi[r["metode"]].append(r["akurasi"])

    print("=== Ringkasan rata-rata akurasi per metode (dari semua citra) ===")
    print(f"{'Metode':<18}{'Rata-rata Akurasi (%)'}")
    print("-" * 45)
    urutan = ["Asli", "Mean Filter", "Median Filter", "Gaussian Filter", "Sharpening"]
    for m in urutan:
        if m in akumulasi:
            rata = sum(akumulasi[m]) / len(akumulasi[m])
            print(f"{m:<18}{round(rata, 2)}")

    print("\nHasil lengkap tersimpan di 'hasil_ocr.csv'")
    print(f"Citra hasil crop + tiap filter tersimpan di folder '{OUTPUT_FOLDER}/'")


if __name__ == "__main__":
    main()