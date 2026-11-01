# Commit Otomatis (aktivitas.txt)

Alat kecil Windows: jalankan `start.bat`, masukkan jumlah commit (1–10), dan
program menambah satu baris acak ke `aktivitas.txt` untuk tiap commit, lalu
melakukan **satu kali push** ke GitHub. Setiap putaran juga dicatat ke
`log.txt` (lokal, tidak ikut di-commit).

## Instalasi

1. **Python 3.8+** — https://www.python.org/downloads/ — centang
   *Add python.exe to PATH* saat instalasi.
2. **Git** — https://git-scm.com/downloads/
3. Kloning **repo milikmu sendiri**, lalu salin berkas ini ke dalamnya:

   ```
   start.bat
   main.py
   aktivitas.txt
   .gitignore
   README.md
   ```

## Konfigurasi pertama kali

```bat
cd path\ke\repo-kamu
git config --global user.name  "Nama Kamu"
git config --global user.email "email@kamu.com"
git remote -v                       <- harus menampilkan origin
git add aktivitas.txt .gitignore README.md start.bat main.py
git commit -m "Awal: skeleton commit-otomatis"
```

Autentikasi (pilih satu, **jangan pernah** simpan token di kode/repo):

* **GitHub CLI:** `gh auth login`
* **SSH:** buat kunci `ssh-keygen -t ed25519`, tambahkan ke GitHub, lalu
  `git remote set-url origin git@github.com:USERNAME/REPO.git`
* **Windows Git Credential Manager:** dipakai otomatis saat clone via HTTPS.

## Cara pakai

```
start.bat
Jumlah commit (1-10): 5
Mode dry-run (tanpa mengubah apa pun)? [y/n]: n
Jeda antar-commit dalam detik (0 = tanpa jeda): 0

Mode: LIVE · 5 commit · jeda 0 detik
  commit 1/5 -> Catat aktivitas 1/5: menyelesaikan satu tugas kecil
  commit 2/5 -> Catat aktivitas 2/5: membaca dokumentasi teknis
  commit 3/5 -> Catat aktivitas 3/5: menulis ringkasan harian
  commit 4/5 -> Catat aktivitas 4/5: merapikan catatan kerja
  commit 5/5 -> Catat aktivitas 5/5: menguji perubahan terakhir

Mendorong main ke origin ...
Push berhasil — commit sudah ada di GitHub.
```

Masukan yang ditolak (program meminta ulang, tidak ada perubahan apa pun):

```
Jumlah commit (1-10):          -> Input kosong. Masukkan bilangan bulat 1 sampai 10.
Jumlah commit (1-10): abc      -> 'abc' bukan bilangan bulat yang valid
Jumlah commit (1-10): 2.5      -> '2.5' bukan bilangan bulat yang valid
Jumlah commit (1-10): 0        -> 0 di luar rentang. Masukkan angka 1 sampai 10.
Jumlah commit (1-10): 11       -> 11 di luar rentang. Masukkan angka 1 sampai 10.
Jeda antar-commit ...: -1      -> Jeda tidak boleh negatif.
```

### Mode dry-run

Menjalankan seluruh pemeriksaan lalu **hanya mencetak** rencana — tidak ada
berkas yang diubah, tidak ada commit, tidak ada push:

```bat
start.bat --dry-run --interval 0
Jumlah commit (1-10): 2

Mode: DRY-RUN · 2 commit · jeda 0 detik
  [dry-run] commit 1/2 -> Catat aktivitas 1/2: ...
  [dry-run] commit 2/2 -> Catat aktivitas 2/2: ...
  [dry-run] akan push sekali: git push origin main
```

### Jeda antar-commit (`--interval`)

`--interval 5` (atau pilihan interaktif) membuat jeda 5 detik antar-commit —
berguna agar commit tidak bertempat sama persis. Tanpa opsi ini, semua commit
dibuat beruntun.

## Log lokal (`log.txt`)

Setiap putaran ditambahkan ke `log.txt` di folder repo: waktu, mode
(LIVE/DRY-RUN), tiap commit yang dibuat, dan hasil push. File ini masuk
`.gitignore`, jadi tidak pernah ikut ter-commit. Buka dengan Notepad kapan
saja untuk melihat riwayat pemakaian.

## Perilaku

* Hanya `aktivitas.txt` yang diubah dan di-stage (`git add -- aktivitas.txt`).
  Tidak pernah memakai `git add .`.
* Push dilakukan **sekali di akhir**, bukan per commit.
* Tidak pernah: force-push, reset, amend, hapus riwayat, atau ubah tanggal commit.
* Kalau push gagal, commit lokal tetap ada — jalankan ulang `start.bat`
  atau `git push origin <cabang>`.

## Pemecahan masalah

| Gejala | Penyebab & solusi |
| --- | --- |
| "Python tidak ditemukan" | Belum instal / tidak dicentang *Add to PATH*. Ulangi instalasi, lalu buka ulang terminal. Jika muncul Microsoft Store, matikan alias-nya: Settings → Apps → Advanced app settings → App execution aliases → matikan Python. |
| "Git tidak ditemukan" | Instal Git, tutup & buka lagi terminal. |
| "Folder ini bukan repo Git" | `start.bat` dijalankan di luar repo. Pindah ke folder repo atau `git init`. |
| "Remote 'origin' belum dikonfigurasi" | `git remote add origin https://github.com/USERNAME/REPO.git` |
| "Identitas Git belum diatur" | `git config --global user.name/user.email` |
| "Working tree tidak bersih" | `git status`, lalu commit atau `git stash -u`. |
| Commit gagal: *Please tell me who you are* | Identitas belum diatur (lihat di atas). |
| Push gagal: *Authentication failed* / *Permission denied* | `gh auth login`, atau cek kunci SSH (`ssh -T git@github.com`), atau `git config --global credential.helper manager`. |
| Push gagal: *rejected / non-fast-forward* | Ada commit remote baru: `git pull --rebase origin <cabang>`, lalu push ulang. Commit lokal tetap aman. |
| Opsi tidak dikenal | `start.bat` meneruskan argumen ke `main.py`; format benar: `start.bat --dry-run --interval 5`. |

Program ini **tidak** membuat atau mengubah repo GitHub mana pun — repo harus
sudah ada dan jadi milikmu sendiri.