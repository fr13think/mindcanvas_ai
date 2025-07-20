import os
import openai
from langdetect import detect, LangDetectException
import re

# --- Konfigurasi Klien NVIDIA NIM ---
NVIDIA_API_KEY = os.environ.get("NVIDIA_API_KEY")
client = openai.OpenAI(
  base_url = "https://integrate.api.nvidia.com/v1",
  api_key = NVIDIA_API_KEY
)

# ==============================================================================
# PROMPT TEMPLATES dengan instruksi yang lebih tegas
# ==============================================================================
PROMPT_TEMPLATES = {
    "en": """
You are "Mind Canvas," an expert journaling assistant. Your tone is empathetic and insightful.
Analyze the user's current journal entry in depth, considering the past entry if provided.
The entire response, including all headers and content, must be in English.

{previous_entry_section}
Current Journal Entry:
---
{current_entry}
---

Based on the provided texts, perform ALL of the following tasks:
1.  **A Friendly Hello:** A warm, one-sentence opening.
2.  **The Big Picture:** Synthesize the core emotional narrative.
3.  **Your Mind Meter:** You **must** always provide scores (1-5) for the following three dimensions. Base the score on the context. For example, if the user is happy, Energy Level might be high. If they are confused, Emotional Clarity might be low.
4.  **Spotlight on Your Thoughts:** Identify ONE cognitive distortion, quote evidence, and explain it. If none, state "Your thinking appears balanced."
5.  **A Path Forward:** Provide ONE gentle, concrete, small step.
6.  **A Little Nugget for the Road:** A witty or insightful quote.
7.  **Dominant Sentiment:** Classify the primary emotion.
8.  **Main Topics:** Identify up to three main topics.
9.  **Journal Connection:** Based on the past entry, mention a connection or pattern.

Use the following exact format for your response:
### A Friendly Hello
[Your greeting here]
### The Big Picture
[Your analysis here]
### Your Mind Meter
[Your meter here in the format:
Energy Level:      [Score]/5
Emotional Clarity: [Score]/5
Self-Compassion:   [Score]/5
]
### Spotlight on Your Thoughts
[Your analysis here]
### A Path Forward
[Your suggestion here]
### A Little Nugget for the Road
[Your quote here]
### Dominant Sentiment
[Your classification here]
### Main Topics
[Topic 1, Topic 2]
### Journal Connection
[Your connection insight here]
""",
    "id": """
Anda adalah "Mind Canvas", seorang asisten jurnal ahli. Nada Anda empatik dan berwawasan.
Analisis entri jurnal pengguna saat ini secara mendalam, pertimbangkan entri sebelumnya jika ada.
Seluruh respons, termasuk semua judul dan konten, harus dalam Bahasa Indonesia.

{previous_entry_section}
Entri Jurnal Saat Ini:
---
{current_entry}
---

Berdasarkan teks yang diberikan, lakukan SEMUA tugas berikut:
1.  **Halo Hangat:** Satu kalimat pembuka yang hangat.
2.  **Gambaran Besarnya:** Sintesiskan narasi emosional inti.
3.  **Meteran Pikiran Anda:** Anda **wajib** selalu memberikan skor (1-5) untuk tiga dimensi berikut. Dasarkan skor pada konteks tulisan. Contohnya, jika pengguna merasa senang, Tingkat Energi mungkin tinggi. Jika mereka merasa bingung, Kejernihan Emosi mungkin rendah.
4.  **Sorotan pada Pikiran Anda:** Identifikasi SATU distorsi kognitif, kutip buktinya, dan jelaskan. Jika tidak ada, nyatakan "Pola pikir Anda tampak seimbang."
5.  **Sebuah Langkah ke Depan:** Berikan SATU langkah kecil yang lembut dan konkret.
6.  **Sedikit Permata untuk Bekal:** Sebuah kutipan jenaka atau berwawasan.
7.  **Sentimen Dominan:** Klasifikasikan emosi utama.
8.  **Topik Utama:** Identifikasi hingga tiga topik utama.
9.  **Koneksi Jurnal:** Berdasarkan entri sebelumnya, sebutkan koneksi atau polanya.

Gunakan format yang sama persis untuk respons Anda:
### Halo Hangat
[Sapaan Anda di sini]
### Gambaran Besarnya
[Analisis Anda di sini]
### Meteran Pikiran Anda
[Meteran Anda di sini dalam format:
Tingkat Energi:   [Skor]/5
Kejernihan Emosi: [Skor]/5
Welas Asih Diri:  [Skor]/5
]
### Sorotan pada Pikiran Anda
[Analisis Anda di sini]
### Sebuah Langkah ke Depan
[Saran Anda di sini]
### Sedikit Permata untuk Bekal
[Kutipan Anda di sini]
### Sentimen Dominan
[Klasifikasi Anda di sini]
### Topik Utama
[Topik 1, Topik 2]
### Koneksi Jurnal
[Wawasan koneksi Anda di sini]
"""
}

# --- Kunci Parsing Multi-Bahasa (Lengkap) ---
PARSING_KEYS = {
    "en": ["### A Friendly Hello", "### The Big Picture", "### Your Mind Meter", "### Spotlight on Your Thoughts", "### A Path Forward", "### A Little Nugget for the Road", "### Dominant Sentiment", "### Main Topics", "### Journal Connection"],
    "id": ["### Halo Hangat", "### Gambaran Besarnya", "### Meteran Pikiran Anda", "### Sorotan pada Pikiran Anda", "### Sebuah Langkah ke Depan", "### Sedikit Permata untuk Bekal", "### Sentimen Dominan", "### Topik Utama", "### Koneksi Jurnal"]
}

# --- Kunci Dictionary untuk Frontend (PENTING!) ---
FRONTEND_KEYS = ["greeting", "summary", "meter", "pattern", "suggestion", "nugget", "sentiment", "topics", "connection"]


def robust_parser(response_text, keys):
    """Fungsi parsing yang andal dan tidak bergantung pada urutan."""
    parts = {key: "N/A" for key in FRONTEND_KEYS}
    
    found_keys = []
    for i, key in enumerate(keys):
        for match in re.finditer(re.escape(key), response_text, re.IGNORECASE):
            found_keys.append({
                "start": match.start(),
                "end": match.end(),
                "frontend_key": FRONTEND_KEYS[i]
            })

    if not found_keys:
        return parts
        
    found_keys.sort(key=lambda x: x["start"])

    for i, key_info in enumerate(found_keys):
        start_content_index = key_info["end"]
        
        end_content_index = len(response_text)
        if i + 1 < len(found_keys):
            end_content_index = found_keys[i+1]["start"]
            
        content = response_text[start_content_index:end_content_index].strip()
        
        if content:
            parts[key_info["frontend_key"]] = content
            
    return parts


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
    
    previous_entry_section = ""
    if previous_entry:
        header = "Past Journal Entry (for context):" if lang == 'en' else "Entri Jurnal Sebelumnya (untuk konteks):"
        previous_entry_section = f"{header}\n---\n{previous_entry}\n---\n\n"

    prompt_content = prompt_template.format(
        current_entry=current_entry, 
        previous_entry_section=previous_entry_section
    )
    
    try:
        chat_completion = client.chat.completions.create(
            model="ibm/granite-3.3-8b-instruct",
            messages=[{"role": "user", "content": prompt_content}],
            temperature=0.4,
            top_p=0.8,
            max_tokens=800,
            stream=False
        )
        
        response_text = chat_completion.choices[0].message.content.strip()

        parts = robust_parser(response_text, keys)
        return parts

    except Exception as e:
        return {"summary": f"Error saat menghubungi API NVIDIA: {e}", "sentiment": "N/A", "topics": "N/A", "pattern": "N/A", "suggestion": "N/A", "connection": "N/A"}
