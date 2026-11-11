# Laporan pemeriksaan

12 November 2026 · Kit 1.0

## File dan geometri

| Pemeriksaan | Hasil | Bukti |
|---|---|---|
| Sumber asli | PASS | Salinan `00-source/mrboxs-logo-original.svg` identik byte-per-byte dengan file yang diberikan. File awal tidak ditimpa. |
| Integritas raster | PASS | 140 PNG berhasil didekode lewat Pillow. |
| Struktur vector | PASS | 49 SVG hasil generate valid XML, berjudul, tanpa `<text>`, raster tertanam, script, atau filter. Wordmark berupa outline. |
| Transparansi | PASS | PNG symbol, horizontal, stacked, dan wordmark memiliki latar transparan untuk kedua tema. |
| Konsistensi tema | PASS | Mask alpha master light/dark identik; warna foreground dibalik. |
| Favicon | PASS | ICO 16/32/48 tersedia dalam kedua tema; SVG auto serta fixed light/dark tersedia. Small cut dipakai di 16–32 px. |
| Windows | PASS | Frame 16/24/32/48/64/128/256 didekode. Tiga frame terkecil identik dengan artwork small-cut PNG masing-masing. |
| macOS | PASS | Kedua file ICNS berhasil dibaca dan didekode oleh Pillow. |
| iOS | PASS | Dua asset catalog, masing-masing 18 slot, punya dimensi sesuai metadata. Semua PNG RGB tanpa kanal alpha. |
| Android | PASS untuk struktur | 8 XML resources valid, dengan warna day/night, adaptive API 26, dan monochrome API 33. Belum dibangun menggunakan Android SDK. |
| PWA | PASS | Semua referensi ikon pada manifest tersedia dan dimensi cocok. Simbol maskable berada di lingkaran aman berdiameter 80% canvas. |
| Avatar | PASS | Seluruh artwork berada di dalam lingkaran crop. |

Data pemeriksaan otomatis lengkap ada di `verification.json`. Inventaris dan SHA-256 disertakan di root paket.

## Inspeksi visual

PNG berikut dirender dengan librsvg dan dilihat langsung:

- `brand-overview.png`: keseimbangan simbol dan wordmark, pasangan tema, ikon aplikasi, favicon, avatar, dan signature horizontal.
- `size-and-crop-checks.png`: ukuran native 16/24/32/48/64 px, pembesaran nearest-neighbour untuk melihat piksel, serta crop avatar lingkaran.
- `03-social/dark/social-card-1200x630.png`: pemisahan ruang logo dari pola pada bidang hitam.
- Render 512 px dari SVG asli sebelum ekspor, untuk membandingkan bentuk.

Hasil iterasi: lapisan atas disederhanakan untuk favicon, diamond diperbesar, ruang vertikal small cut diseimbangkan; crop avatar pada lembar presentasi diperbaiki; jarak signature horizontal diperlebar dari tepi; pola social card dipisahkan dari area logo. Badge mempertahankan proporsi dan radius sudut sumber, sementara app tile menggunakan padding dan radius khusus ikon.

Audit `svg_audit.py` dari skill logo-design memberi skor heuristik 91/100 untuk symbol light, symbol dark, dan symbol-small; horizontal 88/100 karena proporsi lebar, kompleksitas outline teks, dan presisi koordinat. Tidak ada FAIL. Peringatan sudut mendekati 30° berasal dari geometri asli dan tidak diubah dalam pekerjaan ekspor ini. Stacked dan symbol disertakan untuk ruang sempit.

## Perilaku tema di browser

`tools/check-browser.py` menjalankan Chromium headless dengan preferensi OS light lalu dark. Masing-masing lulus 21 assertion:

- CSS mengikuti tema OS pada awal load.
- Preferensi manual dark/light mengalahkan tema OS.
- Hanya pasangan logo yang sesuai yang ditampilkan.
- Favicon menunjuk varian yang tepat saat tema berubah.
- Warna browser mengikuti preferensi manual.
- Preferensi system mengembalikan media query.
- SVG favicon auto benar-benar dirender dengan warna bidang yang sesuai.

Versi Chromium dan hasil per assertion tercatat di `browser-verification.json`. Syntax JavaScript juga lolos `node --check`.

## Kontras teks

| Tema | Pasangan | Rasio |
|---|---|---|
| Light | foreground / background | 21.00:1 |
| Light | foreground / surface | 18.93:1 |
| Light | muted / background | 7.46:1 |
| Light | muted / surface | 6.72:1 |
| Dark | foreground / background | 21.00:1 |
| Dark | foreground / surface | 17.93:1 |
| Dark | muted / background | 10.59:1 |
| Dark | muted / surface | 9.04:1 |

Semua pasangan teks di atas melewati 4.5:1. Border dekoratif bukan warna teks atau indikator fokus.

## Batas pemeriksaan

Tidak dilakukan instalasi pada perangkat fisik, build Xcode/Android SDK, pengujian semua launcher, pencarian merek dagang, ataupun proof cetak. SVG dan PNG adalah master RGB. CMYK pada panduan hanya perkiraan grayscale. Ikon aplikasi yang terpasang tidak dijanjikan berubah otomatis mengikuti tema; mekanisme dan pilihan varian dijelaskan di README.
