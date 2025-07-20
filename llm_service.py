import os
import openai
from langdetect import detect, LangDetectException

# --- Konfigurasi Klien NVIDIA NIM ---
NVIDIA_API_KEY = os.environ.get("NVIDIA_API_KEY")

client = openai.OpenAI(
  base_url = "https://integrate.api.nvidia.com/v1",
  api_key = NVIDIA_API_KEY
)

# ==============================================================================
# PROMPT_TEMPLATES yang sudah diperbaiki
# ==============================================================================
PROMPT_TEMPLATES = {
    "en": """
You are "Mind Canvas," a witty, empathetic, and deeply insightful AI reflection partner.
Your task is to analyze the user's journal entry.

**IMPORTANT INSTRUCTION:** First, think step-by-step internally about the user's entry to understand its core themes, emotions, and patterns. DO NOT show this internal thinking process in your final output.
Your final output that the user will see must begin EXACTLY with "### A Friendly Hello" and follow the structure below precisely.

Current Journal Entry:
---
{current_entry}
---

Structure your final, user-facing response as follows:
### A Friendly Hello
[A warm, one-sentence opening that acknowledges the user's feelings.]

### The Big Picture
[Your in-depth synthesis of the core emotional narrative.]

### Your Mind Meter
[Display scores from 1 to 5 using this text format:
Energy Level:      [Score]/5 ■■■□□
Emotional Clarity: [Score]/5 ■■■■□
Self-Compassion:   [Score]/5 ■■□□□
]

### Spotlight on Your Thoughts
[Your analysis of the Cognitive Pattern, quoting the user's own words as evidence.]

### A Path Forward
[Your Actionable Suggestion, framed as an empowering "experiment".]

### A Little Nugget for the Road
[Your witty quote or one-liner.]
""",
    "id": """
Anda adalah "Mind Canvas," seorang partner refleksi AI yang jenaka, empatik, dan sangat berwawasan.
Tugas Anda adalah menganalisis entri jurnal pengguna.

**INSTRUKSI PENTING:** Pertama, berpikirlah langkah demi langkah secara internal tentang tulisan pengguna untuk memahami tema inti, emosi, dan polanya. JANGAN tampilkan proses berpikir internal ini di output akhir Anda.
Output akhir Anda yang akan dilihat pengguna harus dimulai PERSIS dengan "### Halo Hangat" dan mengikuti struktur di bawah ini dengan tepat.

Entri Jurnal Saat Ini:
---
{current_entry}
---

Susun respons akhir Anda untuk pengguna sebagai berikut:
### Halo Hangat
[Satu kalimat pembuka yang hangat yang mengakui perasaan pengguna.]

### Gambaran Besarnya
[Sintesis mendalam Anda tentang narasi emosional inti.]

### Meteran Pikiran Anda
[Tampilkan skor dari 1 hingga 5 menggunakan format teks ini:
Tingkat Energi:   [Skor]/5 ■■■□□
Kejernihan Emosi: [Skor]/5 ■■■■□
Welas Asih Diri:  [Skor]/5 ■■□□□
]

### Sorotan pada Pikiran Anda
[Analisis Anda tentang Pola Pikir, kutip kata-kata pengguna sendiri sebagai bukti.]

### Sebuah Langkah ke Depan
[Saran Aksi Anda, yang dibingkai sebagai "eksperimen" memberdayakan.]

### Sedikit Permata untuk Bekal
[Kutipan atau candaan jenaka Anda.]
"""
}

# --- Kunci Parsing Multi-Bahasa (tetap sama) ---
PARSING_KEYS = {
    "en": ["### A Friendly Hello", "### The Big Picture", "### Your Mind Meter", "### Spotlight on Your Thoughts", "### A Path Forward", "### A Little Nugget for the Road"],
    "id": ["### Halo Hangat", "### Gambaran Besarnya", "### Meteran Pikiran Anda", "### Sorotan pada Pikiran Anda", "### Sebuah Langkah ke Depan", "### Sedikit Permata untuk Bekal"]
}


def analyze_journal_entry(current_entry, previous_entry=None, timeframe='random'):
    if not NVIDIA_API_KEY:
        return {"summary": "Error: NVIDIA_API_KEY belum diatur!", "sentiment": "N/A", "topics": "N/A", "pattern": "N/A", "suggestion": "N/A", "connection": "N/A"}
    if not current_entry or current_entry.isspace():
        return {"summary": "Jurnal Anda masih kosong.", "sentiment": "N/A", "topics": "N/A", "pattern": "N/A", "suggestion": "N/A", "connection": "N/A"}

    try:
        lang = detect(current_entry)
        lang = 'id' if lang == 'id' else 'en'
    except LangDetectException:
        lang = 'en'

    prompt_template = PROMPT_TEMPLATES[lang]
    keys = PARSING_KEYS[lang]
    
    prompt_content = prompt_template.format(current_entry=current_entry)
    
    try:
        chat_completion = client.chat.completions.create(
            model="meta/llama3-8b-instruct",
            messages=[{"role": "user", "content": prompt_content}],
            temperature=0.4,
            top_p=0.8,
            max_tokens=700,
            stream=False
        )
        
        response_text = chat_completion.choices[0].message.content.strip()

        # Parsing yang lebih kuat untuk struktur baru
        parts = {
            "greeting": response_text.split(keys[1])[0].replace(keys[0], "").strip(),
            "summary": response_text.split(keys[2])[0].split(keys[1])[1].strip(),
            "meter": response_text.split(keys[3])[0].split(keys[2])[1].strip(),
            "pattern": response_text.split(keys[4])[0].split(keys[3])[1].strip(),
            "suggestion": response_text.split(keys[5])[0].split(keys[4])[1].strip(),
            "connection": response_text.split(keys[5])[1].strip() # 'connection' sekarang menjadi 'nugget'
        }
        return parts

    except Exception as e:
        return {"summary": f"Error saat menghubungi API NVIDIA: {e}", "sentiment": "N/A", "topics": "N/A", "pattern": "N/A", "suggestion": "N/A", "connection": "N/A"}