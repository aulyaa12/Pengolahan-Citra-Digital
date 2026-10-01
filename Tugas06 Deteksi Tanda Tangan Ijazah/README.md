# MINI PROJECT: SISTEM DETEKSI KEBERADAAN TANDA TANGAN PADA DOKUMEN IJAZAH

Dokumentasi ini berisi penyelesaian **Tugas 06 / Mini Project** mata kuliah Pengolahan Citra Digital untuk membangun sistem otomatisasi deteksi keberadaan tanda tangan kepala sekolah pada dokumen ijazah menggunakan teknik *ROI Cropping*, *Thresholding*, Operasi Morfologi, dan Ekstraksi Piksel Latar Depan (*Foreground Pixel Counting*).

## Deskripsi & Alur Kerja Sistem

Sistem ini memproses citra ijazah dengan alur kerja sebagai berikut:

1. **ROI Cropping:** Memotong area spasial tanda tangan kepala sekolah dari dokumen ijazah secara konsisten.
2. **Konversi Grayscale:** Mengubah citra RGB menjadi skala abu-abu.
3. **Thresholding (Pengambangan):** Membandingkan metode *Global Thresholding* dan *Otsu / Adaptive Thresholding* untuk memisahkan goresan tinta (*foreground*) dari latar belakang kertas.
4. **Operasi Morfologi:** Mengaplikasikan *Opening* (menghilangkan *noise* bintik kecil) dan *Closing* (menyambungkan goresan tanda tangan yang terputus).
5. **Hitung Karakteristik Area:** Menghitung total jumlah piksel latar depan (*foreground pixels* / piksel putih hasil binarisasi).
6. **Klasifikasi Aturan Sederhana:**

* **SIGNATURE PRESENT**: jika Jumlah Piksel Foreground >= Threshold Piksel
* **SIGNATURE ABSENT**: jika Jumlah Piksel Foreground < Threshold Piksel

## 📁 Struktur Folder Proyek

```text
Tugas06 Deteksi Tanda Tangan Ijazah/
├── citra_ijazah/               # Dataset citra masukan ber-tanda tangan
├── citra_tanpa_ttd/            # Dataset citra masukan tanpa tanda tangan
├── hasil_deteksi/              # Folder penyimpanan hasil segmentasi & binarisasi
├── buat_data_uji.py            # Skrip pembantu pembuat data uji otomatis/manual
├── code_signature_detection.py # Skrip utama deteksi tanda tangan & analisis
├── hasil_deteksi.xlsx          # Rekapitulasi kuantitatif & hasil klasifikasi Excel
└── README.md                   # Dokumentasi ringkas & penjelasan analisis
```

## Cara Menjalankan Program

1. **Instalasi Pustaka**

```bash
pip install opencv-python numpy matplotlib pandas openpyxl
```

2. **Menyiapkan Data Uji (Opsional)**

```bash
python buat_data_uji.py
```

*Skrip ini akan menyiapkan file citra uji baik yang memiliki tanda tangan maupun yang tidak memiliki tanda tangan (_NonTTD).*

3. **Eksekusi Program Utama**

```bash
python code_signature_detection.py
```

*Program akan memotong area ROI, mengaplikasikan thresholding dan operasi morfologi, menentukan status SIGNATURE PRESENT atau SIGNATURE ABSENT, serta mengeksport laporan ke hasil_deteksi.xlsx dan citra ke folder hasil_deteksi/.*

## Analisis & Pembahasan Soal

### 1. Mengapa diperlukan ambang batas (thresholding) sebelum melakukan analisis keberadaan tanda tangan?

**Jawaban:**

Komputer tidak dapat mengukur luas atau menghitung jumlah piksel objek dari citra grayscale yang memiliki variasi intensitas warna (0–255). Proses thresholding (binarisasi) diperlukan untuk memisahkan goresan tinta tanda tangan dari latar belakang kertas ijazah secara tegas menjadi format biner (0 dan 1).

Setelah citra menjadi biner, variasi bayangan dan pencahayaan kertas otomatis tereliminasi. Hal ini memungkinkan komputer melakukan operasi morfologi ( *Opening/Closing* ) untuk membersihkan *noise* serta menghitung jumlah piksel *foreground* secara pasti sebagai dasar keputusan `SIGNATURE PRESENT` atau `SIGNATURE ABSENT`.

### 2. Apa masalah yang terjadi jika ambang batas (thresholding) terlalu tinggi atau terlalu rendah?

**Jawaban:**

* **Jika Ambang Batas Terlalu Tinggi (*Over-thresholding*):**
  Piksel latar belakang kertas yang redup atau berbayangan akan keliru terdeteksi sebagai tinta. Hal ini memunculkan banyak *noise* hitam pekat yang membuat citra tanpa tanda tangan salah terdeteksi sebagai **`SIGNATURE PRESENT`** (*False Positive*).
* **Jika Ambang Batas Terlalu Rendah (*Under-thresholding*):**
  Hanya goresan tinta yang sangat hitam pekat yang terdeteksi, sedangkan garis halus atau pudar akan terhapus. Akibatnya, jumlah piksel *foreground* menjadi sangat kecil dan citra yang bertanda tangan salah terdeteksi sebagai **`SIGNATURE ABSENT`** (*False Negative*).
