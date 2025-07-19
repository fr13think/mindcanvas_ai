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
# PROMPT_TEMPLATES dengan instruksi Koneksi Jurnal yang sudah dinamis
# ==============================================================================
PROMPT_TEMPLATES = {
    "en": """
You are "Mind Canvas", an expert journaling assistant with a deep understanding of psychology and human emotion. Your tone is empathetic, insightful, and supportive.
Analyze the user's current journal entry in depth, considering the past entry if provided.
The entire response, including all headers and content, must be in English.

{previous_entry_section}
Current Journal Entry:
---
{current_entry}
---

Based on the provided texts, perform the following tasks:
1.  **Core Summary:** Synthesize the core emotional themes and underlying tensions in the current entry.
2.  **Dominant Sentiment:** Classify the primary emotion of the current entry.
3.  **Main Topics:** Identify up to three main topics.
4.  **Cognitive Pattern:** Identify ONE potential cognitive distortion, quote a specific phrase as evidence, and briefly explain it. If none, state "Your thinking appears balanced and reflective."
5.  **Actionable Suggestion:** Provide ONE gentle, concrete, and highly practical small step connected to the main problem.
6.  **Journal Connection:** Based on the past entry provided, briefly mention any connection, pattern, or contrast you notice. If no past entry was provided, state "This is one of your first entries, keep writing to discover connections over time."

Use the following exact format for your response:
### Core Summary
[Your summary here]
### Dominant Sentiment
[Your classification here]
### Main Topics
[Topic 1, Topic 2]
### Cognitive Pattern
[Your analysis here]
### Actionable Suggestion
[Your suggestion here]
### Journal Connection
[Your connection insight here]
""",
    "id": """
Anda adalah "Mind Canvas", seorang asisten jurnal ahli dengan pemahaman mendalam tentang psikologi dan emosi manusia. Nada Anda empatik, berwawasan, dan suportif.
Analisis entri jurnal pengguna saat ini secara mendalam, pertimbangkan entri sebelumnya jika ada.
Seluruh respons, termasuk semua judul dan konten, harus dalam Bahasa Indonesia.

{previous_entry_section}
Entri Jurnal Saat Ini:
---
{current_entry}
---

Berdasarkan teks yang diberikan, lakukan tugas-tugas berikut:
1.  **Ringkasan Inti:** Sintesiskan tema emosional inti dan ketegangan yang mendasari tulisan ini.
2.  **Sentimen Dominan:** Klasifikasikan emosi utama dari entri saat ini.
3.  **Topik Utama:** Identifikasi hingga tiga topik utama.
4.  **Pola Pikir:** Identifikasi SATU potensi distorsi kognitif, kutip frasa spesifik sebagai bukti, dan jelaskan secara singkat. Jika tidak ada, nyatakan "Pola pikir Anda tampak seimbang dan reflektif."
5.  **Saran Aksi:** Berikan SATU langkah kecil yang lembut, konkret, dan sangat praktis yang terhubung dengan masalah utama.
6.  **Koneksi Jurnal:** Berdasarkan entri sebelumnya yang diberikan, sebutkan secara singkat koneksi, pola, atau kontras yang Anda perhatikan. Jika tidak ada entri sebelumnya, nyatakan "Ini adalah salah satu entri pertama Anda, teruslah menulis untuk menemukan koneksi dari waktu ke waktu."

Gunakan format yang sama persis untuk respons Anda:
### Ringkasan Inti
[Ringkasan Anda di sini]
### Sentimen Dominan
[Klasifikasi Anda di sini]
### Topik Utama
[Topik 1, Topik 2]
### Pola Pikir
[Analisis Anda di sini]
### Saran Aksi
[Saran Anda di sini]
### Koneksi Jurnal
[Wawasan koneksi Anda di sini]
"""
}

# --- Kunci Parsing Multi-Bahasa (tetap sama) ---
PARSING_KEYS = {
    "en": ["### Core Summary", "### Dominant Sentiment", "### Main Topics", "### Cognitive Pattern", "### Actionable Suggestion", "### Journal Connection"],
    "id": ["### Ringkasan Inti", "### Sentimen Dominan", "### Topik Utama", "### Pola Pikir", "### Saran Aksi", "### Koneksi Jurnal"]
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
    
    # --- Diubah: Menyiapkan bagian entri sebelumnya untuk prompt ---
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
            model="meta/llama3-8b-instruct",
            messages=[{"role": "user", "content": prompt_content}],
            temperature=0.3,
            top_p=0.7,
            max_tokens=500,
            stream=False
        )
        
        response_text = chat_completion.choices[0].message.content.strip()

        parts = {
            "summary": response_text.split(keys[1])[0].replace(keys[0], "").strip(),
            "sentiment": response_text.split(keys[2])[0].split(keys[1])[1].strip(),
            "topics": response_text.split(keys[3])[0].split(keys[2])[1].strip(),
            "pattern": response_text.split(keys[4])[0].split(keys[3])[1].strip(),
            "suggestion": response_text.split(keys[5])[0].split(keys[4])[1].strip(),
            "connection": response_text.split(keys[5])[1].strip()
        }
        return parts

    except Exception as e:
        return {"summary": f"Error saat menghubungi API NVIDIA: {e}", "sentiment": "N/A", "topics": "N/A", "pattern": "N/A", "suggestion": "N/A", "connection": "N/A"}