#### ANALISIS PERBANDINGAN METODE MEAN FILTER, MEDIAN FILTER, GAUSSIAN FILTER, DAN SHARPENING UNTUK PENINGKATAN KUALITAS CITRA NOMOR IJAZAH PADA PROSES OPTICAL CHARACTER RECOGNITION (OCR)

Dokumentasi ini berisi penyelesaian **Tugas Pertemuan 5** mata kuliah Pengolahan Citra Digital dengan fokus pada *Filtering*, *Noise Reduction*, dan *Sharpening* untuk meningkatkan kualitas citra nomor ijazah ber-*noise* agar menghasilkan akurasi pembacaan *Optical Character Recognition* (OCR) yang optimal.

## Deskripsi & Studi Kasus

Penelitian ini berfokus pada pengujian citra nomor ijazah yang memiliki *noise* atau kualitas rendah dengan menerapkan empat teknik pengolahan citra, yaitu **Mean Filter**, **Median Filter**, **Gaussian Filter**, dan **Teknik Penajaman (*Sharpening*)**.

Kemudian hasil dari masing-masing metode dibandingkan secara visual maupun digunakan sebagai input untuk proses OCR guna melihat pengaruhnya terhadap tingkat akurasi pengenalan nomor ijazah, sekaligus menjawab pertanyaan analisis terkait efektivitas *Median Filter* pada citra ber-*noise salt and pepper* serta hubungan antara kualitas visual citra dengan tingkat akurasi OCR yang dihasilkan.

## 📁 Struktur Folder Proyek

```text
Tugas05 Peningkatan Citra Ijazah/
├── citra_ijazah/                       # Dataset citra masukan
├── hasil_filter/                       # Hasil keluaran filtering, sharpening, & OCR
├── analisis_citra_ijazah.py            # Skrip pemrosesan Mean, Median, Gaussian, Sharpening & OCR
├── Laporan Peningkatan Citra untuk OCR.pdf # Dokumen laporan resmi
└── README.md                           # Dokumentasi ringkas & hasil analisis
```

## Cara Menjalankan Program

1. **Instalasi Pustaka**

```bash
pip install opencv-python numpy matplotlib pytesseract
```

2. **Eksekusi Program**

```bash
python analisis_citra_ijazah.py
```

*Program akan memproses filter, menajamkan citra, mengevaluasi akurasi OCR, dan menyimpan hasilnya secara otomatis di folder `hasil_filter/`.*

## Analisis & Pembahasan Soal

### 1. Mengapa Median Filter Dapat Memberikan Hasil OCR yang Lebih Baik pada Citra yang Mengandung Salt and Pepper Noise?

> **Jawaban:**
> Median Filter bekerja dengan mengganti setiap piksel menggunakan nilai tengah (median) dari piksel-piksel di sekitarnya dalam suatu jendela kecil. Karena *noise salt and pepper* selalu bernilai ekstrem (sangat terang atau sangat gelap), nilai tersebut akan selalu berada di posisi paling ujung setelah diurutkan, sehingga hampir tidak pernah terpilih sebagai median dan otomatis terbuang, sementara bentuk tepi karakter di sekitarnya tetap terjaga.

Berbeda halnya dengan *Mean Filter* dan *Gaussian Filter* yang bekerja dengan menghitung rata-rata dari seluruh piksel dalam jendela, sehingga nilai ekstrem dari *noise* tetap ikut tercampur dalam perhitungan dan hanya menyebar menjadi kekaburan, bukan benar-benar hilang. Sifat Median Filter yang mampu menghilangkan *noise* sekaligus mempertahankan ketajaman tepi karakter inilah yang membuatnya lebih unggul dibanding Mean dan Gaussian Filter pada citra ber-*noise* acak. Hal ini sejalan dengan hasil pengujian pada **Citra 4**, di mana Median Filter tetap menghasilkan tampilan paling bersih di antara metode lain dan berhasil mempertahankan **akurasi OCR sebesar 100%**.

### 2. Apakah Citra yang Paling Bagus Secara Visual Selalu Menghasilkan OCR dengan Akurasi Tertinggi?

> **Jawaban:** **TIDAK SELALU.**

**Penjelasan Berdasarkan Hasil Laporan:**
Tidak selalu, karena kualitas visual yang dinilai oleh mata manusia dan tingkat keberhasilan OCR yang dinilai oleh algoritma pengenalan karakter merupakan dua hal yang berbeda.

Bukti paling jelas terlihat pada **Citra 4**, di mana hasil *Sharpening* tampak paling tajam dan paling kontras secara visual dibanding metode lainnya, namun justru menghasilkan **akurasi OCR sebesar 0%**. Hal ini terjadi karena proses penajaman tidak hanya memperkuat tepi karakter, tetapi juga ikut memperkuat *noise* di sekitarnya sehingga bentuk digit asli menjadi sulit dibedakan dari *noise* yang telah dipertegas.

Dengan demikian, dapat disimpulkan bahwa OCR menilai suatu citra berdasarkan **kejelasan dan konsistensi struktur tepi karakter**, bukan berdasarkan tingkat ketajaman yang dipersepsikan mata manusia, sehingga pemilihan metode praproses citra untuk keperluan OCR sebaiknya didasarkan pada pengujian akurasi secara kuantitatif, bukan hanya penilaian visual semata.
