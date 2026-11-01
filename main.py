#!/usr/bin/env python3
"""
main.py — tambah 1 sampai 10 commit ke aktivitas.txt, lalu push sekali.

Opsi:
  --dry-run            hanya menampilkan rencana; tidak mengubah, commit, atau push
  --interval DETIK     jeda antar-commit (default 0; bila tidak diisi, ditanya)

Prasyarat:
  * Git terpasang dan autentikasi sudah diatur (GitHub CLI / SSH / Credential Manager)
  * Berjalan di dalam repo Git milikmu yang punya remote "origin"
  * Working tree bersih, file aktivitas.txt sudah di-commit sekali sebelumnya
"""

import argparse
import random
import re
import shutil
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path

REPO_DIR = Path(__file__).resolve().parent
TARGET_NAME = "aktivitas.txt"
LOG_NAME = "log.txt"
MIN_COMMITS, MAX_COMMITS = 1, 10

TEKS = [
    "merapikan catatan kerja",
    "menyelesaikan satu tugas kecil",
    "membaca dokumentasi teknis",
    "menyusun daftar pekerjaan berikutnya",
    "membersihkan folder proyek",
    "menguji perubahan terakhir",
    "menulis ringkasan harian",
]


def keluar(pesan, kode=1):
    catat("berhenti: " + pesan.splitlines()[0])
    print()
    print(pesan)
    sys.exit(kode)


def catat(pesan):
    """Tulis satu baris ke log lokal (log.txt, masuk .gitignore)."""
    path = REPO_DIR / LOG_NAME
    try:
        with path.open("a", encoding="utf-8", newline="\n") as f:
            f.write(f"{datetime.now():%Y-%m-%d %H:%M:%S} | {pesan}\n")
    except OSError as e:
        print(f"  (peringatan: gagal menulis {LOG_NAME}: {e})")


def jalankan_git(*args):
    """Jalankan git dari REPO_DIR. Mengembalikan CompletedProcess, tidak melempar exception."""
    return subprocess.run(
        ["git", *args],
        cwd=str(REPO_DIR),
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )


def baca_argumen():
    p = argparse.ArgumentParser(
        description="Tambah 1-10 commit ke aktivitas.txt lalu push sekali ke origin."
    )
    p.add_argument(
        "--dry-run",
        action="store_true",
        default=None,
        help="tampilkan rencana saja: tidak mengubah berkas, tidak commit, tidak push",
    )
    p.add_argument(
        "--interval",
        type=float,
        default=None,
        metavar="DETIK",
        help="jeda antar-commit dalam detik (0 = tanpa jeda)",
    )
    return p.parse_args()


def periksa_lingkungan():
    """Semua pemeriksaan dijalankan SEBELUM berkas diubah."""
    if shutil.which("git") is None:
        keluar(
            "Git tidak ditemukan.\n"
            "  Instal dari https://git-scm.com/downloads lalu buka lagi terminal."
        )

    p = jalankan_git("rev-parse", "--is-inside-work-tree")
    if p.returncode != 0 or p.stdout.strip() != "true":
        keluar(
            "Folder ini bukan repo Git.\n"
            "  Jalankan start.bat dari dalam folder repo milikmu,\n"
            "  atau buat repo baru dengan:  git init"
        )

    p = jalankan_git("remote", "get-url", "origin")
    if p.returncode != 0 or not p.stdout.strip():
        keluar(
            "Remote 'origin' belum dikonfigurasi.\n"
            "  Lihat daftar remote:  git remote -v\n"
            "  Atur remote:         git remote add origin https://github.com/USERNAME/REPO.git"
        )

    for opsi in ("user.name", "user.email"):
        p = jalankan_git("config", "--get", opsi)
        if p.returncode != 0 or not p.stdout.strip():
            keluar(
                f"Identitas Git belum diatur ({opsi}). Set dulu:\n"
                '  git config --global user.name "Nama Kamu"\n'
                '  git config --global user.email "email@kamu.com"'
            )

    p = jalankan_git("status", "--porcelain")
    if p.returncode != 0:
        keluar("Gagal membaca status working tree:\n" + (p.stderr or "").strip())
    if p.stdout.strip():
        keluar(
            "Working tree tidak bersih — ada perubahan yang belum di-commit.\n"
            "  Lihat:   git status\n"
            "  Simpan:  git stash -u   (atau commit dulu perubahanmu)\n"
            "Program berhenti tanpa mengubah berkas."
        )

    if not (REPO_DIR / TARGET_NAME).exists():
        keluar(
            f"File {TARGET_NAME} tidak ditemukan di {REPO_DIR}.\n"
            f"  Buat dulu file itu, lalu commit sekali: git add {TARGET_NAME} && git commit -m \"Awal\""
        )


def minta_jumlah():
    """Ambil dan validasi jumlah commit: bilangan bulat 1..10."""
    while True:
        try:
            teks = input(f"Jumlah commit ({MIN_COMMITS}-{MAX_COMMITS}): ").strip()
        except (EOFError, KeyboardInterrupt):
            keluar("\nDibatalkan oleh pengguna.", 130)

        if teks == "":
            print(f"  Input kosong. Masukkan bilangan bulat {MIN_COMMITS} sampai {MAX_COMMITS}.")
            continue
        if not re.fullmatch(r"[0-9]+", teks):
            print(f"  '{teks}' bukan bilangan bulat yang valid (contoh salah: 0, abc, 2.5).")
            continue
        nilai = int(teks)
        if nilai < MIN_COMMITS or nilai > MAX_COMMITS:
            print(f"  {nilai} di luar rentang. Masukkan angka {MIN_COMMITS} sampai {MAX_COMMITS}.")
            continue
        return nilai


def tanya_ya_tidak(pertanyaan):
    while True:
        try:
            j = input(f"{pertanyaan} [y/n]: ").strip().lower()
        except (EOFError, KeyboardInterrupt):
            keluar("\nDibatalkan oleh pengguna.", 130)
        if j in ("y", "yes"):
            return True
        if j in ("n", "no"):
            return False
        print("  Jawab dengan y atau n.")


def minta_interval():
    while True:
        try:
            teks = input("Jeda antar-commit dalam detik (0 = tanpa jeda): ").strip()
        except (EOFError, KeyboardInterrupt):
            keluar("\nDibatalkan oleh pengguna.", 130)
        if teks == "":
            return 0.0
        try:
            nilai = float(teks)
        except ValueError:
            print(f"  '{teks}' bukan angka. Contoh valid: 0, 2, 2.5")
            continue
        if nilai < 0:
            print("  Jeda tidak boleh negatif.")
            continue
        return nilai


def baris_acak(nomor):
    """Satu baris unik: timestamp + nomor + teks acak, dijamin beda antar iterasi."""
    sekarang = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    return f"[{sekarang}] aktivitas #{nomor}: {random.choice(TEKS)} (catatan {random.randint(1000, 9999)})"


def buat_commit(nomor, total, kering=False):
    pesan = f"Catat aktivitas {nomor}/{total}: {random.choice(TEKS)}"

    if kering:
        print(f"  [dry-run] commit {nomor}/{total} -> {pesan}")
        catat(f"dry-run | commit {nomor}/{total} direncanakan: {pesan}")
        return

    path = REPO_DIR / TARGET_NAME
    with path.open("a", encoding="utf-8", newline="\n") as f:
        f.write(baris_acak(nomor) + "\n")

    p = jalankan_git("add", "--", TARGET_NAME)
    if p.returncode != 0:
        keluar(
            "git add gagal:\n" + (p.stderr or "").strip() +
            "\nPerbaiki lalu jalankan ulang start.bat. Cek status: git status"
        )

    p = jalankan_git("commit", "-m", pesan)
    if p.returncode != 0:
        keluar(
            "git commit gagal:\n" + (p.stderr or "").strip() +
            "\nPeriksa identitas Git:\n"
            '  git config --global user.name "Nama Kamu"\n'
            '  git config --global user.email "email@kamu.com"'
        )
    print(f"  commit {nomor}/{total} -> {pesan}")
    catat(f"commit {nomor}/{total} dibuat: {pesan}")


def dorong_satu_kali(kering=False):
    p = jalankan_git("rev-parse", "--abbrev-ref", "HEAD")
    cabang = (p.stdout or "").strip() or "HEAD"

    if kering:
        print(f"  [dry-run] akan push sekali: git push origin {cabang}")
        catat(f"dry-run | push direncanakan: git push origin {cabang}")
        return

    print(f"\nMendorong {cabang} ke origin ...")
    p = jalankan_git("push", "origin", cabang)
    if p.returncode != 0:
        keluar(
            "PUSH GAGAL. Commit lokal tetap tersimpan (tidak dihapus, tidak di-reset).\n"
            "Coba push lagi kapan saja dengan:\n"
            f"  git push origin {cabang}\n\n"
            "Detail error:\n" + (p.stderr or p.stdout or "").strip()
        )
    print("Push berhasil — commit sudah ada di GitHub.")
    catat(f"push origin/{cabang} berhasil")


def main():
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

    print("=== Tambah commit otomatis ===")
    print(f"Repo: {REPO_DIR}")

    args = baca_argumen()
    periksa_lingkungan()

    jumlah = minta_jumlah()
    kering = args.dry_run if args.dry_run is not None else tanya_ya_tidak("Mode dry-run (tanpa mengubah apa pun)?")
    interval = args.interval if args.interval is not None else minta_interval()
    if interval < 0:
        keluar("Jeda antar-commit tidak boleh negatif.")

    mode = "DRY-RUN" if kering else "LIVE"
    print(f"\nMode: {mode} · {jumlah} commit · jeda {interval:g} detik")
    catat(f"mulai: mode={mode}, jumlah={jumlah}, interval={interval:g}s")

    for i in range(1, jumlah + 1):
        buat_commit(i, jumlah, kering)
        if interval > 0 and i < jumlah:
            print(f"  ... jeda {interval:g} detik ...")
            time.sleep(interval)

    dorong_satu_kali(kering)
    catat("selesai")


if __name__ == "__main__":
    main()