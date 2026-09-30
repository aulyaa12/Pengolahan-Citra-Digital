
```markdown
# MINI PROJECT: SISTEM DETEKSI KEBERADAAN TANDA TANGAN PADA DOKUMEN IJAZAH

Dokumentasi ini berisi penyelesaian **Tugas 06 / Mini Project** mata kuliah Pengolahan Citra Digital untuk membangun sistem otomatisasi deteksi keberadaan tanda tangan kepala sekolah pada dokumen ijazah menggunakan teknik *ROI Cropping*, *Thresholding*, Operasi Morfologi, dan Ekstraksi Piksel Latar Depan (*Foreground Pixel Counting*).

---

## Deskripsi & Alur Kerja Sistem

Sistem ini memproses citra ijazah dengan alur kerja sebagai berikut:
1. **ROI Cropping:** Memotong area spasial tanda tangan kepala sekolah dari dokumen ijazah secara konsisten.
2. **Konversi Grayscale:** Mengubah citra RGB menjadi skala abu-abu.
3. **Thresholding (Pengambangan):** Membandingkan metode *Global Thresholding* dan *Otsu / Adaptive Thresholding* untuk memisahkan goresan tinta (*foreground*) dari latar belakang kertas.
4. **Operasi Morfologi:** Mengaplikasikan *Opening* (menghilangkan *noise* bintik kecil) dan *Closing* (menyambungkan goresan tanda tangan yang terputus).
5. **Hitung Karakteristik Area:** Menghitung total jumlah piksel latar depan (*foreground pixels* / piksel putih hasil binarisasi).
6. **Klasifikasi Aturan Sederhana:**
   $$\text{Status} = \begin{cases} \text{SIGNATURE PRESENT}, & \text{jika Jumlah Piksel Foreground} \ge \text{Threshold Piksel} \\ \text{SIGNATURE ABSENT}, & \text{jika Jumlah Piksel Foreground} < \text{Threshold Piksel} \end{cases}$$

---

## 📁 Struktur Folder Proyek

```text
Tugas06 Deteksi Tanda Tangan Ijazah/
├── citra_ijazah/               # Dataset citra masukan ber-tanda tangan
├── citra_tanpa_ttd/            # Dataset citra masukan tanpa tanda tangan
├── hasil_deteksi/              # Folder penyimpanan hasil segmentasi & binarisasi
├── buat_data_uji.py            # Skrip pembantu pembuat data uji otomatis/manual
├── code_signature_detection.py # Skrip utama deteksi tanda tangan & analisis
├── hasil_deteksi.xlsx          # Rekapitulasi kuantitatif & hasil klasifikasi Excel
└── README.md                   # 
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

*Skrip ini akan menyiapkan file citra uji baik yang memiliki tanda tangan maupun yang tidak memiliki tanda tangan (`_NonTTD`).*
3. **Eksekusi Program Utama**

```bash
python code_signature_detection.py

```

*Program akan memotong area ROI, mengaplikasikan thresholding dan operasi morfologi, menentukan status `SIGNATURE PRESENT` atau `SIGNATURE ABSENT`, serta mengeksport laporan ke `hasil_deteksi.xlsx` dan citra ke folder `hasil_deteksi/`.*

## Analisis & Pembahasan Soal

### 1. Mengapa diperlukan ambang batas (thresholding) sebelum melakukan analisis keberadaan tanda tangan?

> **Jawaban:**
> Komputer tidak dapat mengukur luas atau dimensi objek pada citra berwarna/grayscale secara presisi ($0–255$). *Thresholding* (binarisasi) mengonversi citra menjadi biner ($0$ dan $1$) untuk **memisahkan objek tinta tanda tangan secara tegas dari latar belakang kertas**, sehingga jumlah piksel dan dimensi tinta dapat dihitung secara pasti.

**Penjelasan Lengkap:**

Citra *grayscale* hanya berisi angka intensitas $0$ sampai $255$ per piksel, sehingga komputer tidak "melihat" bentuk goresan tanda tangan begitu saja. Ambang batas (*thresholding*) mengubah citra abu-abu menjadi citra biner ($0$ atau $1$): piksel gelap (tinta) menjadi *foreground*, sedangkan piksel terang (kertas) menjadi *background*. Baru setelah pemisahan ini dilakukan, kita bisa menghitung hal-hal yang menjadi dasar keputusan, seperti jumlah piksel *foreground*, jumlah komponen yang saling terhubung, dan lebar goresan.

### 2. Apa masalah yang terjadi jika ambang batas (thresholding) terlalu tinggi atau terlalu rendah?

> **Jawaban:**

* **Jika Ambang Batas Terlalu Tinggi (*Over-thresholding*):**
* Nilai piksel batas yang ditetapkan terlalu mendekati nilai maksimum ($255$).
* **Dampak:** Piksel latar belakang kertas yang sedikit redup atau memiliki bayangan tipis akan keliru terdeteksi sebagai piksel *foreground* (tinta). Hal ini menyebabkan munculnya banyak *noise* hitam pekat yang membuat citra tanpa tanda tangan keliru terdeteksi sebagai **`SIGNATURE PRESENT`** (*False Positive*).
* **Jika Ambang Batas Terlalu Rendah (*Under-thresholding*):**
* Nilai piksel batas yang ditetapkan terlalu mendekati nilai minimum ($0$).
* **Dampak:** Hanya goresan tinta yang sangat hitam pekat yang terdeteksi. Goresan halus, tipis, atau warna tinta yang agak pudar pada tanda tangan asli akan terpotong dan terhapus (dianggap sebagai latar belakang). Akibatnya, jumlah piksel *foreground* menjadi sangat kecil dan citra yang memiliki tanda tangan keliru terdeteksi sebagai **`SIGNATURE ABSENT`** (*False Negative*).
