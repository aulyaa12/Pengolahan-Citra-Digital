
```markdown
# ANALISIS HISTOGRAM DAN IDENTIFIKASI PERMASALAHAN KUALITAS CITRA DOKUMEN IJAZAH MENGGUNAKAN METODE GRAYSCALE, HISTOGRAM EQUALIZATION, DAN CLAHE

Repositori ini berisi penyelesaian **Tugas Pertemuan 3** mata kuliah Pengolahan Citra Digital untuk menganalisis karakteristik citra ijazah, distribusi intensitas piksel melalui histogram, serta evaluasi metode peningkatan kualitas citra (*image enhancement*).

---

## Deskripsi & Studi Kasus

Studi kasus pada penelitian ini menggunakan sembilan citra dokumen ijazah (`ijazah1.jpg` hingga `ijazah9.jpg`) yang diambil dalam kondisi pencahayaan dan kualitas yang berbeda-beda. Setiap citra dikonversi dari RGB ke *grayscale*, kemudian dianalisis histogramnya untuk mengidentifikasi permasalahan seperti citra terlalu terang, terlalu gelap, kontras rendah, pencahayaan tidak merata, atau *noise*, sebelum ditentukan metode *enhancement* yang paling sesuai untuk masing-masing citra.

---

## 📁 Struktur Folder Proyek

```text
.
├── Analisis_Citra_Ijazah.py    # Skrip Python utama
├── Laporan_Analisis.pdf        # File laporan analisis formal
├── ijazah1.jpg ... ijazah9.jpg # Citra ijazah asli (Input)
└── output/                     # Folder hasil citra grayscale & histogram
```

## Cara Menjalankan Program

1. **Instalasi Pustaka**

```bash
pip install opencv-python numpy matplotlib

```

2. **Eksekusi Program**

```bash
python Analisis_Citra_Ijazah.py

```

*Seluruh grafik histogram dan citra hasil olahan akan tersimpan secara otomatis di dalam folder `output/`.*

## Rekapitulasi Permasalahan & Metode Terpilih

Tabel berikut menyajikan rekapitulasi permasalahan utama beserta metode *enhancement* yang dipilih untuk masing-masing dari kesembilan citra ijazah berdasarkan hasil analisis histogram:

| No | Citra           | Permasalahan Utama       | Metode Terpilih | Alasan                                                                                   |
| -- | --------------- | ------------------------ | --------------- | ---------------------------------------------------------------------------------------- |
| 1  | `ijazah1.jpg` | Kontras rendah           | **CLAHE** | Histogram sempit di tengah. Equalization berisiko menimbulkan*noise* pada latar polos. |
| 2  | `ijazah2.jpg` | Terlalu terang           | **CLAHE** | Piksel menumpuk di kanan. Peregangan global rentan memunculkan*noise* butiran.         |
| 3  | `ijazah3.jpg` | Terlalu terang           | **CLAHE** | Pencahayaan tidak seragam antar kanal warna. Perlu penyesuaian kontras lokal.            |
| 4  | `ijazah4.jpg` | Terlalu terang (ekstrem) | **CLAHE** | Piksel jenuh mendekati maksimum. Data untuk diregangkan global sangat terbatas.          |
| 5  | `ijazah5.jpg` | Terlalu terang           | **CLAHE** | Kejenuhan tinggi disertai*noise* pada kanal biru. Equalization dapat memperkuatnya.    |
| 6  | `ijazah6.jpg` | Terlalu terang           | **CLAHE** | Pola serupa citra 5,*noise* ringan pada kanal biru perlu ditangani secara lokal.       |
| 7  | `ijazah7.jpg` | Terlalu terang           | **CLAHE** | Kejenuhan piksel paling tinggi dan variasi data untuk equalization sangat minim.         |
| 8  | `ijazah8.jpg` | Terlalu terang           | **CLAHE** | Konsisten dengan citra 5–7,*noise* pada kanal biru berisiko diperkuat equalization.   |
| 9  | `ijazah9.jpg` | Kontras rendah           | **CLAHE** | Histogram sangat sempit dan equalization berisiko pola*blocky* yang mengganggu.        |

## Analisis & Hasil Pembahasan

### Hubungan Sebaran Histogram dengan Kualitas Citra

> **Jawaban:** **Histogram yang lebih tersebar tidak selalu menjamin kualitas citra yang lebih baik.**

**Penjelasan Berdasarkan Hasil Laporan:**
Berdasarkan hasil analisis, histogram yang lebih tersebar tidak selalu menjamin kualitas citra yang lebih baik. Hal ini terlihat jelas pada hasil *Histogram Equalization* di seluruh sembilan citra ijazah, di mana histogramnya berhasil diregangkan menjadi jauh lebih tersebar dan mendekati distribusi merata dibanding histogram *grayscale* aslinya, namun secara visual justru menghasilkan **pola *blocky*** dan ***noise* butiran** yang mengganggu keterbacaan teks dokumen.

Sebaliknya, hasil **CLAHE** yang histogramnya tidak setersebar justru menghasilkan citra dengan teks yang lebih jelas dan bersih. Hal ini menunjukkan bahwa sebaran histogram yang luas hanya mencerminkan pemakaian rentang dinamis piksel yang lebih besar, bukan jaminan kualitas persepsual atau keterbacaan citra, karena peregangan yang terlalu agresif dapat memperkuat *noise* dan artefak yang justru menurunkan kualitas citra visual.
