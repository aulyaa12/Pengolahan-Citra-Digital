"""
buat_data_uji.py
Fungsi: Menghasilkan dataset citra ijazah TANPA tanda tangan 
dengan cara menimpa area ROI tanda tangan menggunakan warna latar kertas.
"""

import os
import cv2

# 1. TENTUKAN PATH 3 FILE YANG INGIN DIPROSES SECARA MANUAL DI SINI
DAFTAR_PATH_FILE = [
    "C:\\Users\\LENOVO\\Downloads\\deteksi-tanda-tangan-ijazah\\citra_ijazah\\01_HighQuality_Enhanced.jpg",
    "C:\\Users\\LENOVO\\Downloads\\deteksi-tanda-tangan-ijazah\\citra_ijazah\\02_LowContrast.jpg",
    "C:\\Users\\LENOVO\\Downloads\\deteksi-tanda-tangan-ijazah\\citra_ijazah\\03_Blurred.jpg"
]

FOLDER_TANPA_TTD = "citra_tanpa_ttd"

# Koordinat Area Tanda Tangan (x1, x2, y1, y2)
ROI_CONFIG = {
    "rektor": (0.13, 0.40, 0.70, 0.83),
    "dekan": (0.615, 0.88, 0.70, 0.83),
}

# 2. FUNGSI PEMROSESAN
def hapus_tanda_tangan_manual():
    os.makedirs(FOLDER_TANPA_TTD, exist_ok=True)

    if not DAFTAR_PATH_FILE:
        print("[ERROR] Daftar path file kosong!")
        return
    for path in DAFTAR_PATH_FILE:
        if not os.path.exists(path):
            print(f"[GAGAL] File tidak ditemukan: {path}")
            continue
        img = cv2.imread(path)
        if img is None:
            print(f"[GAGAL] Gambar tidak bisa dibaca: {path}")
            continue
        tinggi, lebar = img.shape[:2]
        
        # Putar jika posisi portrait
        if tinggi > lebar:
            img = cv2.rotate(img, cv2.ROTATE_90_CLOCKWISE)
            tinggi, lebar = img.shape[:2]

        img_tanpa_ttd = img.copy()

        # Timpa area ROI Rektor dan Dekan dengan warna kertas
        for nama_roi, (x1, x2, y1, y2) in ROI_CONFIG.items():
            px_x1, px_x2 = int(x1 * lebar), int(x2 * lebar)
            px_y1, px_y2 = int(y1 * tinggi), int(y2 * tinggi)

            crop_roi = img[px_y1:px_y2, px_x1:px_x2]
            warna_kertas = cv2.mean(crop_roi)[:3]
            img_tanpa_ttd[px_y1:px_y2, px_x1:px_x2] = warna_kertas

        # Ubah nama file menjadi ..._NonTTD.jpg
        nama_file_asli = os.path.basename(path)
        nama_tanpa_ext, ext = os.path.splitext(nama_file_asli)
        nama_file_baru = f"{nama_tanpa_ext}_NonTTD{ext}"
        
        path_out = os.path.join(FOLDER_TANPA_TTD, nama_file_baru)
        cv2.imwrite(path_out, img_tanpa_ttd)
        
        # Print ringkas di terminal
        print(f"[BERHASIL] {nama_file_baru}")

if __name__ == "__main__":
    hapus_tanda_tangan_manual()