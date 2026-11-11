# Panduan identitas mrboxs

Versi 1.0 · 12 November 2026

## Identitas

Simbol kubus berlapis dari logo asli menjadi pusat identitas. Karakternya geometris, terstruktur, dan tegas. Semua nama ditulis `mrboxs` dengan huruf kecil. Warna utama tetap hitam dan putih, sehingga bentuk menjadi pengenal utama.

Garis dan pola pendukung diambil dari ritme chevron pada sisi atas kubus. Pola boleh menjadi tekstur latar berkontras rendah; beri logo ruang bersih, jangan tumpuk simbol utama dengan pola.

## Varian logo

Gunakan **horizontal** sebagai signature utama untuk header, footer, README, dan dokumen. Gunakan **stacked** ketika ruang lebih vertikal. **Wordmark** untuk nama saja, **symbol** untuk tempat yang sudah mengenal identitasnya, **badge** untuk logo dalam kotak seperti file asli.

Varian `symbol-small` adalah adaptasi optik: chevron tengah di sisi atas dihilangkan dan diamond dibesarkan. Kedua sisi kubus tetap sama. Pakai hanya di 16–32 px; master penuh tetap dipakai untuk ukuran besar. Favicon SVG otomatis menggunakan small cut karena tab browser lazimnya kecil. PNG favicon 48/64 px memakai detail penuh.

Varian putih memakai geometri asli yang sama dengan hitam. Tidak ada klaim koreksi ketebalan reversed yang tidak dilakukan.

## Ruang aman dan ukuran

Tetapkan **x = seperempat lebar simbol yang terlihat**, bukan lebar canvas SVG. Sisakan minimal 1x pada setiap sisi logo terhadap teks, logo lain, atau tepi bidang. Pada lockup, x dihitung dari simbol di dalam lockup; untuk wordmark saja pakai setengah tinggi huruf kecil. Ruang ini tambahan di luar bounding box artwork, bukan selalu padding bawaan canvas.

| Aset | Ukuran minimum layar | Patokan cetak awal |
|---|---|---|
| Simbol penuh | canvas 40 px (artwork ±30 px tinggi) | artwork 10 mm tinggi |
| Symbol-small / favicon | canvas 16 px | tidak ditujukan untuk cetak |
| Horizontal | lebar 184 px (tinggi sekitar 40 px) | lebar 40 mm |
| Wordmark | lebar 96 px | lebar 24 mm |
| Stacked | lebar 112 px | lebar 28 mm |
| Avatar/app icon | 48 px; pakai small cut untuk 16–32 px | tidak ditujukan untuk cetak |

Ukuran cetak adalah titik awal konservatif, bukan hasil proof fisik. Untuk bordir, engraving, atau bahan bertekstur, perbesar sampai semua celah bisa direproduksi. Minta sampel produksi sebelum cetak massal.

## Warna dan tema

| Warna | HEX | RGB | CMYK indikatif | Peran |
|---|---|---|---|---|
| Black | `#000000` | 0, 0, 0 | 0, 0, 0, 100 | Logo light, bidang dark |
| White | `#FFFFFF` | 255, 255, 255 | 0, 0, 0, 0 | Logo dark, bidang light |
| Paper | `#F3F3F3` | 243, 243, 243 | 0, 0, 0, 5 | Surface light |
| Graphite | `#171717` | 23, 23, 23 | 0, 0, 0, 91 | Surface dark |
| Gray light | `#555555` | 85, 85, 85 | 0, 0, 0, 67 | Teks sekunder light |
| Gray dark | `#B8B8B8` | 184, 184, 184 | 0, 0, 0, 28 | Teks sekunder dark |

CMYK di atas hanya pendekatan grayscale, bukan konversi ICC. Master SVG/PNG menggunakan RGB, bukan file separasi CMYK. Untuk logo kecil pada cetak satu warna, gunakan tinta hitam tunggal sesuai arahan percetakan. Tidak ada Pantone yang diklaim sudah dicocokkan.

- Latar putih/paper: pakai logo hitam dari folder `light`.
- Latar hitam/graphite: pakai logo putih dari folder `dark`.
- Foto/latar ramai: pakai badge dengan bidang solid.
- Warna border untuk pemisah halus saja. Jangan pakai border abu-abu sebagai satu-satunya indikator fokus atau status.
- Teks utama hitam di putih dan putih di hitam memiliki rasio 21:1. Teks sekunder dihitung di laporan QA.

Palet pendukung hanya grayscale. Tidak ditambahkan warna aksen baru agar identitas asli tetap konsisten. Hirarki dibangun lewat ukuran, ruang, bobot teks, dan pembalikan bidang hitam-putih.

## Tipografi

Adwaita Sans dipilih sebagai pendamping yang tenang untuk simbol dengan detail rapat. Bentuk lowercase yang terbuka membuat nama mudah dibaca tanpa meniru struktur kubus di setiap huruf.

- Headline: Adwaita Sans 650, line-height 1.15–1.25.
- Body: 400, line-height 1.5–1.65.
- Label: 500, line-height 1.35.
- Wordmark: Adwaita Sans 650, optical size 32, dengan tracking khusus; sudah diekspor menjadi outline. Gunakan SVG yang disediakan, jangan ketik ulang untuk membuat logo.
- Fallback: `system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif`.
- Font variable yang dibundel mendukung weight 100–900 dan berlisensi SIL OFL 1.1. Jangan jual font sebagai produk terpisah; sertakan lisensinya saat redistribusi.

## Ikon dan crop

Badge mempertahankan radius sudut 3/32 lebar bidang dan proporsi artwork dari sumber asli. App icon rounded memakai radius 18,75% dengan padding yang lebih lega. Ikon aplikasi persegi adalah master untuk platform yang membuat mask sendiri. Avatar dan ikon PWA maskable menggunakan simbol yang lebih kecil sehingga sudut kubus tidak terpotong dalam lingkaran aman. File PNG iOS tidak punya transparansi.

Master ikon reguler memakai simbol penuh. Favicon 16–32 px memakai small cut dengan jarak yang lebih lega. Pada `.ico` Windows, frame 16/24/32 memakai varian small supaya tidak hanya mengecilkan gambar kompleks.

## Sosial

- Avatar: PNG 400, 800, atau 1024 px; aman untuk crop lingkaran.
- Social card: 1200×630 px; logo dan pola siap untuk Open Graph.
- Banner: 1500×500 px. Platform dapat memotong area berbeda di mobile; pratinjau di platform tujuan sebelum unggah.
- Semua tersedia dalam light dan dark. Social card adalah gambar statis; platform tidak menggantinya otomatis mengikuti tema pembaca.

## Jaga bentuk

Pertahankan rasio asli, jarak antar bagian, susunan lockup, dan arah kubus. Gunakan warna solid dari kit. Hindari meregangkan, memutar, mengganti rasio huruf, menambah outline, atau menambah bayangan ke master. Untuk background yang sulit, gunakan badge dan ruang aman.

## Sumber dan batas verifikasi

Logo asli disimpan utuh di `00-source/`. SVG master baru tidak memakai raster, filter, atau teks hidup. Sudut kecil yang sedikit berbeda dari grid 30° berasal dari sumber asli dan sengaja dipertahankan. Kit ini tidak mencakup redesign, penelusuran merek, proof cetak, atau uji instalasi pada perangkat fisik. Pengecekan aset dan inspeksi visual dicatat di `qa-report.md`.
