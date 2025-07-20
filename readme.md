# 🎨 Mind Canvas: Jurnal Anda, Kini Memahami Anda

**Mind Canvas** adalah sebuah aplikasi web jurnal cerdas yang berfungsi sebagai partner refleksi pribadi Anda. Aplikasi ini dirancang untuk mengubah tulisan jurnal bebas menjadi sebuah kanvas wawasan yang terstruktur, membantu pengguna memahami pikiran dan emosi mereka secara lebih mendalam.

Aplikasi ini dibangun menggunakan Python, Flask, dan didukung oleh model AI canggih yang diakses melalui API, serta di-deploy pada platform cloud modern yang gratis.

---

## ✨ Fitur Utama

* **Analisis Multi-Bahasa:** Secara otomatis mendeteksi input dalam Bahasa Indonesia atau Inggris dan memberikan respons dalam bahasa yang sama.
* **Analisis Mendalam & Insightful:**
    * **Gambaran Besarnya:** Mensintesiskan narasi emosional inti dari tulisan Anda.
    * **Meteran Pikiran Anda:** Memberikan skor visual pada dimensi kunci seperti Tingkat Energi, Kejernihan Emosi, dan Welas Asih Diri.
    * **Sorotan pada Pikiran Anda:** Mengidentifikasi potensi distorsi kognitif dengan kutipan sebagai bukti.
    * **Sebuah Langkah ke Depan:** Memberikan saran aksi yang konkret dan memberdayakan.
* **Fitur Analisis Klasik:**
    * **Ringkasan Inti:** Ringkasan singkat satu kalimat.
    * **Sentimen Dominan:** Mengklasifikasikan emosi utama.
    * **Topik Utama:** Mengidentifikasi hingga tiga topik utama.
* **Koneksi Jurnal Dinamis:** Menghubungkan entri hari ini dengan jurnal dari masa lalu (berdasarkan pilihan: acak, 1 jam lalu, atau kemarin) untuk menemukan pola dari waktu ke waktu.
* **Penyimpanan Personal:** Setiap jurnal disimpan dengan aman dan dihubungkan ke pengguna secara anonim melalui browser `localStorage`.

---

## 🛠️ Tumpukan Teknologi (Tech Stack)

* **Backend:** Python 3.11, Flask
* **Frontend:** HTML5, CSS3, JavaScript (Vanilla)
* **Database:** PostgreSQL (dihosting di **Neon** - Serverless Postgres)
* **Platform AI:** **NVIDIA NIM API**
* **Model AI:** `meta/llama3-8b-instruct`
* **Deployment:** **Render** (Platform as a Service)
* **WSGI Server:** Gunicorn

---

## 🚀 Pengaturan & Instalasi Lokal

Untuk menjalankan aplikasi ini di komputer lokal Anda, ikuti langkah-langkah berikut:

1.  **Clone Repositori**
    ```bash
    git clone [https://github.com/NAMA_ANDA/nama-repo-anda.git](https://github.com/NAMA_ANDA/nama-repo-anda.git)
    cd nama-repo-anda
    ```

2.  **Buat dan Aktifkan Virtual Environment**
    ```bash
    # Membuat venv
    python -m venv venv

    # Mengaktifkan venv (Windows Git Bash)
    source venv/Scripts/activate
    
    # Mengaktifkan venv (macOS/Linux)
    # source venv/bin/activate
    ```

3.  **Instal Dependensi**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Atur Environment Variables**
    * Buat sebuah file bernama `.env` di direktori utama proyek.
    * Salin isi dari `.env.example` (jika ada) atau tambahkan variabel berikut:
        ```
        NVIDIA_API_KEY=nvapi-xxxxxxxxxxxxxxxxxxxxxx
        DATABASE_URL=postgresql://user:password@.../dbname
        ```
    * Ganti nilainya dengan API Key NVIDIA dan URL koneksi database Neon Anda.

5.  **Jalankan Aplikasi**
    ```bash
    python app.py
    ```
    Aplikasi akan berjalan di `http://127.0.0.1:5000`.

---

## ☁️ Deployment ke Render

Aplikasi ini dikonfigurasi untuk deployment yang mudah di Render.

1.  **Siapkan Repositori GitHub:** Pastikan semua kode Anda sudah di-push ke repositori GitHub.
2.  **Buat Database di Neon:** Dapatkan URL koneksi database PostgreSQL gratis dari [Neon.tech](https://neon.tech).
3.  **Konfigurasi di Render:**
    * Buat **"Web Service"** baru dan hubungkan ke repositori GitHub Anda. Render akan otomatis membaca file `render.yaml`.
    * Pergi ke menu **"Environment"**.
    * Tambahkan **Environment Variables** berikut:
        * `NVIDIA_API_KEY`: Tempelkan API key NVIDIA Anda.
        * `DATABASE_URL`: Tempelkan URL koneksi dari Neon.
    * Simpan perubahan. Render akan secara otomatis men-deploy aplikasi Anda.

---
*Proyek ini dibuat sebagai bagian dari [Nama Hackathon] dan menunjukkan bagaimana teknologi AI modern dapat digunakan untuk menciptakan alat refleksi diri yang personal dan berdampak.*
