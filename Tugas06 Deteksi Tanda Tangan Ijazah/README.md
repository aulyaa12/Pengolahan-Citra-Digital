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

Komputer tidak memiliki kemampuan persepsi visual seperti manusia untuk mengenali bentuk atau keberadaan objek langsung dari citra *grayscale* yang memiliki rentang intensitas bertingkat (0–255). Proses *thresholding* (binarisasi) sangat diperlukan untuk memisahkan objek tinta tanda tangan secara tegas dari latar belakang kertas ijazah. Melalui pemisahan ini, piksel gelap tinta diubah menjadi *foreground* (1), sedangkan piksel terang kertas menjadi *background* (0), sehingga perbedaan intensitas yang bervariasi akibat pencahayaan atau bayangan dapat dieliminasi secara objektif.

Setelah citra berhasil diubah menjadi format biner, komputer baru dapat melakukan pemrosesan tingkat lanjut dan ekstraksi fitur secara presisi. Citra biner ini menjadi landasan wajib untuk menjalankan operasi morfologi seperti *Opening* (pembersihan *noise*) dan *Closing* (penyambungan goresan terputus). Selain itu, binarisasi memungkinkan komputer menghitung parameter kuantitatif secara pasti—seperti total jumlah piksel *foreground* dan luas area tanda tangan—yang menjadi dasar utama penentuan keputusan aturan klasifikasi `SIGNATURE PRESENT` atau `SIGNATURE ABSENT`.

---

### 2. Apa masalah yang terjadi jika ambang batas (thresholding) terlalu tinggi atau terlalu rendah?

**Jika Ambang Batas Terlalu Tinggi (*Over-thresholding*):**

Nilai piksel batas yang ditetapkan terlalu mendekati nilai maksimum (255).

**Dampak:** Piksel latar belakang kertas yang sedikit redup atau memiliki bayangan tipis akan keliru terdeteksi sebagai piksel *foreground* (tinta). Hal ini menyebabkan munculnya banyak *noise* hitam pekat yang membuat citra tanpa tanda tangan keliru terdeteksi sebagai **`SIGNATURE PRESENT`** (*False Positive*).

**Jika Ambang Batas Terlalu Rendah (*Under-thresholding*):**

Nilai piksel batas yang ditetapkan terlalu mendekati nilai minimum (0).

**Dampak:** Hanya goresan tinta yang sangat hitam pekat yang terdeteksi. Goresan halus, tipis, atau warna tinta yang agak pudar pada tanda tangan asli akan terpotong dan terhapus (dianggap sebagai latar belakang). Akibatnya, jumlah piksel *foreground* menjadi sangat kecil dan citra yang memiliki tanda tangan keliru terdeteksi sebagai **`SIGNATURE ABSENT`** (*False Negative*).
