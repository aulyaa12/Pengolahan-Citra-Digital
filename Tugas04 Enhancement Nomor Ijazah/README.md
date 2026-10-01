### ANALISIS PERBANDINGAN METODE BRIGHTNESS ADJUSTMENT, CONTRAST STRETCHING, DAN HISTOGRAM EQUALIZATION UNTUK PENINGKATAN KUALITAS CITRA NOMOR IJAZAH PADA PROSES OPTICAL CHARACTER RECOGNITION (OCR)

Repositori ini berisi penyelesaian **Tugas Pertemuan 4** mata kuliah Pengolahan Citra Digital untuk meningkatkan kualitas (*image enhancement*) khusus pada area nomor ijazah menggunakan metode *Brightness Adjustment*, *Contrast Stretching*, dan *Histogram Equalization* guna mengoptimalkan akurasi pembacaan *Optical Character Recognition* (OCR).

## Deskripsi & Studi Kasus

Studi kasus pada laporan ini difokuskan pada peningkatan kualitas citra area nomor ijazah dari tiga sampel ijazah (`Gambar1.jpg`, `Gambar2.png`, dan `Gambar3.png`). Ketiga sampel dipilih karena memiliki karakteristik latar belakang dan tingkat kontras yang berbeda-beda.

Ketiga sampel ini dapat mewakili variasi kondisi citra ijazah yang umum dijumpai, mulai dari citra berkontras rendah dengan latar polos, hingga citra dengan latar bertekstur seperti motif garis dan *watermark* logo universitas. Pada tiap sampel, area nomor ijazah diambil (*crop*) dari citra ijazah utuh, kemudian diterapkan tiga metode *enhancement* secara terpisah, dan hasilnya dibandingkan baik secara visual, histogram, maupun tingkat keberhasilan pembacaan OCR.

## 📁 Struktur Folder Proyek

```text
Tugas_4_Enhancement_Nomor_Ijazah/
├── hasil/                      # Hasil keluaran crop, citra olahan, dan grafik histogram
├── Enhancement_NoIjazah.py     # Skrip utama pemrosesan citra & analisis OCR
├── Gambar1.jpg                 # Sample citra ijazah masukan 1
├── Gambar2.png                 # Sample citra ijazah masukan 2
├── Gambar3.png                 # Sample citra ijazah masukan 3
├── Laporan Enhancement...pdf   # Dokumen laporan resmi
└── README.md                   # Dokumentasi ringkas & hasil analisis
```

## Cara Menjalankan Program

1. **Instalasi Pustaka**

```bash
pip install opencv-python numpy matplotlib pytesseract
```

2. **Eksekusi Program**

```bash
python Enhancement_NoIjazah.py
```

*Hasil pemotongan (crop) nomor ijazah, perbandingan metode, grafik histogram, dan pengujian OCR akan tersimpan secara otomatis di dalam folder `hasil/`.*

## Pembahasan Pertanyaan Analisis

### 1. Mengapa Peningkatan Contrast Dapat Membantu OCR Mengenali Karakter Nomor Ijazah?

**Jawaban:**
OCR mengenali karakter berdasarkan perbedaan intensitas piksel antara tulisan dan latar belakang. Pada citra berkontras rendah, selisih intensitas ini kecil sehingga tepi karakter kabur dan sulit dipisahkan secara numerik. Peningkatan *contrast* memperbesar selisih tersebut, membuat tepi karakter lebih tajam sehingga proses binarisasi/thresholding pada OCR bisa memisahkan tulisan dari latar dengan lebih akurat, dan bentuk karakter yang terbentuk lebih mudah dikenali.

**Bukti Eksperimen:**
Ketiga citra asli memiliki histogram yang menumpuk sempit (kontras rendah). Namun, setelah *contrast stretching* meregangkan histogram tersebut ke rentang $0–255$, tulisan pada ketiga sampel tampak lebih tegas secara visual. Pada Ijazah Airlangga, perbaikan ini bahkan terbukti kuantitatif, skor OCR naik dari **78,3% (asli)** menjadi **80,9% (tertinggi di antara semua metode)**. Ini menunjukkan bahwa penajaman selisih intensitas tulisan-latar benar-benar membantu OCR mengenali karakter dengan lebih akurat.

### 2. Apakah Histogram Equalization Selalu Merupakan Metode Terbaik?

> **Jawaban:** **TIDAK, bahkan merupakan metode terburuk untuk citra dokumen resmi.**

**Penjelasan Berdasarkan Hasil Eksperimen:**
Hasil eksperimen justru menunjukkan *Histogram Equalization* (HE) sebagai metode terburuk dengan skor OCR rata-rata **0,0%** pada ketiga sampel. HE gagal total bahkan dibanding citra asli yang belum diberi *enhancement* sama sekali.

Penyebabnya terlihat jelas dari histogram dan citra hasilnya: ketiga ijazah memiliki latar bertekstur (motif garis bergelombang pada Ijazah Sriwijaya, *watermark* logo pada Ijazah Airlangga, dan variasi warna pada Ijazah UI). *Histogram Equalization* meratakan intensitas secara global tanpa membedakan piksel tulisan dari tekstur latar, sehingga pada Ijazah Sriwijaya dan Airlangga tekstur tersebut berubah menjadi **garis dan pola hitam pekat (*noise*)** yang menutupi tulisan.

Sementara itu, pada Ijazah UI yang latarnya lebih polos, dampaknya sedikit lebih ringan namun tetap menurunkan akurasi menjadi **38,1%**. Ini membuktikan bahwa *Histogram Equalization* hanya cocok untuk citra berlatar polos dan tidak cocok untuk citra dokumen resmi seperti ijazah yang umumnya punya elemen pengaman berupa *watermark* atau motif pada latarnya.
