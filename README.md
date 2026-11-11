# mrboxs brand kit

Kit identitas digital dari `mrboxs-logo.svg` milik mrboxs. Bentuk simbol asli dipertahankan. Ekspor baru membersihkan metadata Illustrator, memisahkan simbol dari latar, dan menambahkan wordmark serta varian untuk beragam ukuran.

Mulai dari `05-guidelines/brand-overview.png` untuk lihat keseluruhan kit, lalu baca `05-guidelines/brand-guidelines.md` untuk aturan pemakaian.

![Preview brand kit mrboxs](05-guidelines/brand-overview.png)

## Pilih file

| Kebutuhan | File / folder |
|---|---|
| Logo di latar terang | `01-logos/light/` (gambar hitam, transparan) |
| Logo di latar gelap | `01-logos/dark/` (gambar putih, transparan) |
| Logo mengikuti tema OS | `01-logos/adaptive/` |
| Logo mengikuti warna CSS | `01-logos/inline/` (tempel SVG langsung ke HTML/JSX) |
| Logo di navbar | `mrboxs-horizontal.svg` |
| Nama saja | `mrboxs-wordmark.svg` |
| Susunan vertikal | `mrboxs-stacked.svg` |
| Badge seperti logo asli | `mrboxs-badge.svg` |
| Favicon + PWA | `02-icons/web/` |
| Ikon aplikasi square/rounded | `02-icons/app/light/` atau `dark/` |
| Windows / macOS | `mrboxs-windows.ico` / `mrboxs-macos.icns` |
| iOS | `02-icons/app/ios/<tema>/AppIcon.appiconset/` |
| Android + themed icon | `02-icons/app/android/res/` |
| Avatar dan social card | `03-social/<tema>/` |
| CSS, token warna, pola | `04-brand/` |
| Panduan dan hasil pengecekan | `05-guidelines/` |
| Font + lisensi OFL | `06-typography/` |
| Sumber asli | `00-source/mrboxs-logo-original.svg` |

`light` dan `dark` menunjukkan **latar tempat aset dipakai**. Logo `light` berwarna hitam untuk latar terang, logo `dark` berwarna putih untuk latar gelap. Ikon, avatar, dan social card sudah punya latar masing-masing.

## Pasang di website

Salin direktori berikut ke direktori public proyek:

```text
02-icons/web/     -> public/brand/icons/
01-logos/        -> public/brand/logos/
03-social/       -> public/brand/social/
04-brand/        -> public/brand/system/
06-typography/   -> public/brand/typography/
```

1. Tempel `02-icons/web/head-snippet.html` ke `<head>`.
2. Muat `/brand/system/brand.css` kalau mau memakai token dan font.
3. Pakai `01-logos/logo-snippet.html`, atau tempel SVG `currentcolor` sebagai inline SVG.
4. Untuk tema manual, set `<html data-theme="light">` atau `dark`. Hapus atributnya atau isi `system` untuk mengikuti OS. `theme-sync.js` menyelaraskan favicon dan warna browser dengan atribut ini.
5. Pakai social card 1200×630 sebagai `og:image` dan `twitter:image`. Isi URL HTTPS absolut dari domain lu sendiri setelah aset diunggah. Pakai `twitter:card=summary_large_image`, `og:image:width=1200`, `og:image:height=630`, dan alt `Logo mrboxs`.

Path snippet memakai `/brand/`. Jika situs di subpath, sesuaikan prefix. Manifest memakai URL ikon relatif terhadap file manifest, sementara `id`, `start_url`, dan `scope` default `/`: ubah ketiganya mengikuti aplikasi tujuan sebelum deploy. Kit aset ini belum menyertakan service worker atau aplikasi PWA.

File `adaptive/*-auto.svg` dan favicon otomatis membaca **tema OS**, bukan otomatis membaca tema manual dalam aplikasi. Untuk tema manual, pakai CSS dari kit, inline SVG `currentColor`, atau pasangan file light/dark. `currentColor` dalam SVG eksternal yang dipasang lewat `<img>` tidak mewarisi warna elemen induknya.

Manifest di snippet memilih ikon dark secara konsisten untuk instalasi. Tersedia manifest light sebagai alternatif. Ikon PWA yang sudah terpasang, Apple Touch Icon, dan ikon desktop biasa tidak dijamin berubah saat tema berganti; pergantian favicon hanya berlaku di tab browser. Pilih versi instalasi yang lu mau sebelum rilis.

## Aplikasi native

- **iOS:** pilih satu `AppIcon.appiconset` light/dark, lalu masukkan ke asset catalog Xcode. Semua PNG iOS opaque dan persegi; sistem yang membuat mask sudut. Kedua set adalah alternatif yang dipilih saat build. Ini bukan satu asset catalog yang otomatis berganti dengan tema iOS.
- **Android:** gabungkan `android/res/` ke resources aplikasi dan set `android:icon="@mipmap/ic_launcher"`, `android:roundIcon="@mipmap/ic_launcher_round"` pada application manifest. Periksa konflik nama resource sebelum merge. Adaptive icon tersedia untuk API 26+, monochrome untuk API 33+, fallback raster untuk versi lama. Warna day/night disediakan; launcher dapat menyimpan cache atau memakai warna wallpaper untuk themed icon.
- **Windows:** gunakan `.ico` multiukuran. Pilih light atau dark saat packaging.
- **macOS:** gunakan `.icns`; file tersedia dalam kedua tema sebagai alternatif packaging, bukan pergantian otomatis.
- **App store / launcher:** gunakan PNG square 1024 tanpa mask untuk sistem yang memberi mask sendiri. Rounded PNG cocok untuk presentasi atau tempat yang tidak memberi mask.

## Bangun ulang

Dependensi: Python 3, `fonttools`, `Pillow`, dan `rsvg-convert` (librsvg). Tidak butuh browser atau koneksi jaringan saat build setelah dependensi tersedia.

```sh
python3 -m venv .venv
.venv/bin/pip install fonttools pillow
.venv/bin/python tools/build.py
.venv/bin/python tools/verify.py
# Opsional: butuh Chromium, menguji perpindahan tema di browser tanpa server.
.venv/bin/python tools/check-browser.py
.venv/bin/python tools/package.py
```

Jalankan dari dalam folder kit. Script mencari master dan font relatif terhadap lokasinya sendiri, jadi tidak tergantung font terpasang di komputer. `tools/build.py` memperbarui aset hasil generate; README, panduan, CSS, dan snippet tetap diedit sebagai file sumber. `tools/package.py` memperbarui inventaris, checksum, dan ZIP setelah verifikasi.

Font Adwaita Sans didistribusikan sesuai SIL OFL 1.1; lisensi ada di `06-typography/OFL.txt`. Wordmark sudah berupa path, jadi tidak perlu font terpasang untuk membuka SVG. Kit tidak mengubah status kepemilikan atau lisensi logo asli lu.
