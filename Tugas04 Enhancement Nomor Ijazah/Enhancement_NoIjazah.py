import os
import json
import difflib

import cv2
import numpy as np
import matplotlib.pyplot as plt
import pytesseract

#KONFIGURAS
OUT_DIR = "hasil"
os.makedirs(OUT_DIR, exist_ok=True)

# Data ijazah ini berisi: path file, ROI (fraksi x0,y0,x1,y1 relatif terhadap ukuran citra),
# dan nomor ijazah asli (ground truth) untuk mengukur akurasi OCR.
DATA_IJAZAH = {
    "ui": {
        "path": r"E:\CITRA SM 5\ocr\Tugas Ayu\Gambar1.jpg",
        "roi": (0.0, 0.905, 0.30, 0.955),          # kiri-bawah
        "nomor_asli": "571012022000056",
        "label": "Universitas Indonesia (Low Contrast)",
    },
    "sriwijaya": {
        "path": r"E:\CITRA SM 5\ocr\Tugas Ayu\Gambar2.png",
        "roi": (0.755, 0.03, 1.0, 0.16),          # kanan-atas
        "nomor_asli": "066690-02-2007",
        "label": "Universitas Sriwijaya",
    },
    "airlangga": {
        "path": "E:\CITRA SM 5\ocr\Tugas Ayu\Gambar3.png",
        "roi": (0.0, 0.0, 0.40, 0.09),             # kiri-atas
        "nomor_asli": "7834/001004/07.3/S1/2015",
        "label": "Universitas Airlangga",
    },

}

TARGET_H = 160   # Digunakan untuk menentukan tinggi standar gambar hasil crop, 
                 # supaya semua crop sebanding ukurannya untuk diproses/OCR
BETA_BRIGHTNESS = 40   # konstanta penambah kecerahan untuk brightness adjustment


# 1. CROP AREA NOMOR IJAZAH (ROI)
#Fungsi untuk  mengambil bagian tertentu dari gambar.
def crop_roi(img, roi): 
    h, w = img.shape[:2]
    x0, y0, x1, y1 = roi
    crop = img[int(y0 * h):int(y1 * h), int(x0 * w):int(x1 * w)].copy()

    ch, cw = crop.shape[:2]
    scale = TARGET_H / ch
    crop = cv2.resize(crop, (int(cw * scale), TARGET_H), interpolation=cv2.INTER_CUBIC)
    return crop


# 2. TIGA METODE IMAGE ENHANCEMEN
# a. Funsgi brightness_adjustment digunakan untuk meningkatkan kecerahan gambar.
def brightness_adjustment(gray, beta=BETA_BRIGHTNESS):
    return cv2.convertScaleAbs(gray, alpha=1.0, beta=beta)

# b. Fungsi contrast_stretching digunakan untuk meningkatkan kontras.
# Tujuannya memperjelas perbedaan tulisan dengan background.
def contrast_stretching(gray):
    mn, mx = gray.min(), gray.max()
    if mx == mn:
        return gray.copy()
    stretched = (gray.astype(np.float32) - mn) * 255.0 / (mx - mn)
    return np.clip(stretched, 0, 255).astype(np.uint8)

# c. Fungsi Histogram Equalization
#Tujuannya meningkatkan kontras berdasarkan distribusi intensitas piksel.
def hist_equalization(gray):
    return cv2.equalizeHist(gray)


# 3. OCR & PENGUKURAN AKURAS
def ocr_read(img_gray, upscale=3):
    #Ini adalah fungsi untuk membaca teks.
    big = cv2.resize(img_gray, None, fx=upscale, fy=upscale, interpolation=cv2.INTER_CUBIC)
    config = "--psm 7"
    return pytesseract.image_to_string(big, config=config).strip()

def similarity(pred, ground_truth):
    #Hitung persentase kemiripan string antara hasil OCR dan nomor ijazah asli 
    pred_clean = "".join(ch for ch in pred if ch.isalnum()).upper()
    gt_clean = "".join(ch for ch in ground_truth if ch.isalnum()).upper()
    if not gt_clean:
        return 0.0
    return difflib.SequenceMatcher(None, pred_clean, gt_clean).ratio() * 100.0


# 4. PROSES UTAMA: crop -> enhancement -> tampilkan -> OC
# Ini adalah fungsi utama untuk memproses satu gambar ijazah.
def proses_satu_ijazah(nama, info): # OpenCV membaca gambar dari path.
    img = cv2.imread(info["path"])
    if img is None:
        raise FileNotFoundError(f"Tidak bisa membaca file: {info['path']}")

    roi_bgr = crop_roi(img, info["roi"]) # Crop ROI (Mengambil area nomor ijazah)
    gray = cv2.cvtColor(roi_bgr, cv2.COLOR_BGR2GRAY) #Grayscale

    versi_citra = { #Membuat Empat Versi Gamba
        "Asli (sebelum)": gray,
        "Brightness Adjustment": brightness_adjustment(gray),
        "Contrast Stretching": contrast_stretching(gray),
        "Histogram Equalization": hist_equalization(gray),
    }

    # ---- (a) simpan tiap citra individual (before & after per metode) ----
    for judul, im in versi_citra.items():
        fname = judul.lower().replace(" ", "_").replace("(", "").replace(")", "")
        cv2.imwrite(f"{OUT_DIR}/{nama}_{fname}.png", im)

    # ---- (b) satu figure gabungan: citra + histogram sebelum & sesudah ----
    fig, axes = plt.subplots(2, 4, figsize=(15, 5.2))
    fig.suptitle(f"Perbandingan Enhancement — Nomor Ijazah {info['label']}",
                 fontsize=12, fontweight="bold")
    for i, (judul, im) in enumerate(versi_citra.items()):
        axes[0, i].imshow(im, cmap="gray", vmin=0, vmax=255)
        axes[0, i].set_title(judul, fontsize=10)
        axes[0, i].axis("off")

        axes[1, i].hist(im.ravel(), bins=256, range=(0, 255), color="steelblue")
        axes[1, i].set_title("Histogram", fontsize=9)
        axes[1, i].set_xlim(0, 255)
        axes[1, i].set_yticks([])
    plt.tight_layout()
    fig.savefig(f"{OUT_DIR}/perbandingan_{nama}.png", dpi=150)
    plt.close(fig)

    # ---- (c) OCR tiap versi & catat hasil ----
    hasil = []
    print(f"\n=== {info['label']} (nomor asli: {info['nomor_asli']}) ===")
    for judul, im in versi_citra.items():
        teks = ocr_read(im)
        akurasi = similarity(teks, info["nomor_asli"])
        print(f"  {judul:24s} -> OCR: '{teks}'  | kemiripan: {akurasi:.1f}%")
        hasil.append({"ijazah": nama, "metode": judul, "ocr_text": teks, "akurasi": akurasi})

    return hasil


def main():
    semua_hasil = []
    for nama, info in DATA_IJAZAH.items():
        semua_hasil.extend(proses_satu_ijazah(nama, info))

    # ---- ringkasan rata-rata akurasi per metode ----
    print("\n\n=== RINGKASAN RATA-RATA KEMIRIPAN PER METODE (semua ijazah) ===")
    metode_list = ["Asli (sebelum)", "Brightness Adjustment",
                   "Contrast Stretching", "Histogram Equalization"]
    ringkasan = {}
    for m in metode_list:
        vals = [r["akurasi"] for r in semua_hasil if r["metode"] == m]
        rata = float(np.mean(vals))
        ringkasan[m] = rata
        print(f"  {m:24s}: rata-rata = {rata:5.1f}%   (per file: {[round(v, 1) for v in vals]})")

    metode_terbaik = max(ringkasan, key=ringkasan.get)
    print(f"\n>> Metode dengan rata-rata kemiripan OCR tertinggi: {metode_terbaik} "
          f"({ringkasan[metode_terbaik]:.1f}%)")

    with open(f"{OUT_DIR}/summary.json", "w") as f:
        json.dump({"detail": semua_hasil, "ringkasan": ringkasan}, f, indent=2)
    print(f"\nSemua citra, histogram, dan ringkasan JSON disimpan di folder: {OUT_DIR}/")


if __name__ == "__main__":
    main()

