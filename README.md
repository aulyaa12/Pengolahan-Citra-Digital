# Portfolio Pengolahan Citra Digital (Digital Image Processing)

Repositori ini berisi kumpulan tugas dan Mini Project mata kuliah Pengolahan Citra Digital yang berfokus pada teknik perbaikan kualitas citra, ekstraksi fitur, deteksi objek, dan integrasi Optical Character Recognition (OCR) Tesseract pada dokumen resmi (ijazah).

## 📁 Daftar Tugas & Proyek

| Folder                                    | Topik Utama                       | Deskripsi / Fokus                                                                                               |
| ----------------------------------------- | --------------------------------- | --------------------------------------------------------------------------------------------------------------- |
| 📁`Tugas_3_Analisis_Histogram`          | Histogram & Enhancement           | Analisis Grayscale, Histogram Equalization, dan CLAHE pada 9 Citra Ijazah                                       |
| 📁`Tugas_4_Enhancement_Nomor_Ijazah`    | Enhancement & OCR                 | Perbandingan Brightness, Contrast Stretching, & HE untuk Optimalisasi OCR                                       |
| 📁`Tugas05 Peningkatan Citra Ijazah`    | Filtering & Sharpening            | Filtering (Mean, Median, Gaussian) & Sharpening untuk Noise Reduction OCR                                       |
| 📁`Tugas06 Deteksi Tanda Tangan Ijazah` | Segmentation & Morphology         | Deteksi Tanda Tangan Otomatis via ROI Cropping, Binarization, & Morphology                                      |
| 📁`Tugas07 Integrasi Proyek Mini`       | Mini Project / System Integration | Verifikasi Keaslian Ijazah (Deteksi Tanda Tangan) + Auto Orientation (OSD) + ROI Enhancement & Evaluasi CER OCR |

---

## Teknologi & Pustaka Utama

Seluruh proyek dalam repositori ini dikembangkan menggunakan stack berikut:

* **Python 3.x**
* **OpenCV (cv2):** Pemrosesan citra dasar, konversi warna, filtering, morfologi, dan segmentasi
* **PyTesseract:** Ekstraksi teks otomatis (OCR) dan OSD (Orientation and Script Detection)
* **NumPy:** Operasi matriks dan manipulasi array piksel
* **JiWER:** Evaluasi tingkat kesalahan pembacaan karakter (Character Error Rate / CER)
* **Pandas & OpenPyXL:** Tabulasi data dan rekapitulasi hasil analisis ke format spreadsheet
