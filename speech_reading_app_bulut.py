# YERELDE ÇALIŞACAK VERSİYON

# YENİ VERSİYON
#streamlit run speech_reading_app_cloud.py   /bunu cmd'de de H: yap bunu yaz enter yap


#streamlit run speech_reading_app.py   /bunu cmd'de de H: yap bunu yaz enter yap

import docx
import re
import speech_recognition as sr
import difflib
import random
import streamlit as st
from streamlit.components.v1 import html
import os
from deep_translator import GoogleTranslator
import pronouncing
import winsound
import time
from gtts import gTTS

# Sabitler
ERROR_THRESHOLD = 0.3
TOTAL_TOPICS = 152  # Şu anki toplam konu sayısı

def get_text_from_docx(doc_path, topic_no):
    """Belirtilen dosya yolundan ve konu numarasından metni alır."""
    try:
        doc = docx.Document(doc_path)
        paragraphs = [p.text.strip() for p in doc.paragraphs if p.text.strip()]
        topics = []
        current_topic = ""
        current_number = None
        for p in paragraphs:
            match = re.match(r'^Konu\s*:\s*(\d+)', p)
            if match:
                if current_topic and current_number is not None:
                    topics.append({"number": current_number, "text": current_topic})
                current_number = int(match.group(1))
                current_topic = ""
            else:
                if current_number is not None:
                    current_topic += p + "\n"
        if current_topic and current_number is not None:
            topics.append({"number": current_number, "text": current_topic})
        for topic in topics:
            if topic["number"] == topic_no:
                topic["text"] = topic["text"].replace("=== KONU SONU ===", "").strip()
                return topic["text"]
        return None
    except Exception as e:
        st.error(f"Dosya okuma hatası: {e}")
        return None

def split_into_paragraphs(text):
    return [p.strip() for p in text.split('\n') if p.strip()]

def preprocess_text(text):
    return re.findall(r"\b\w+\b", text.lower())

def evaluate_speech(original, spoken):
    original_words = preprocess_text(original)
    spoken_words = preprocess_text(spoken)
    diff = difflib.SequenceMatcher(None, original_words, spoken_words)
    similarity = diff.ratio()
    error_rate = 1 - similarity
    extra_words = [word for word in spoken_words if word not in original_words]
    missing_words = [word for word in original_words if word not in spoken_words]
    return error_rate, extra_words, missing_words

import os
from gtts import gTTS

import os
from gtts import gTTS
import base64
import streamlit as st

import os
from gtts import gTTS
import base64
import streamlit as st

def read_paragraph(paragraph):
    clean_text = " ".join(paragraph.splitlines())
    clean_text = (clean_text.replace('"', '\\"')
                  .replace("'", "\\'")
                  .replace('{', '')
                  .replace('}', '')
                  .replace('\n', ' ')
                  .replace('\r', ' ')
                  .replace('\t', ' '))
    tts = gTTS(text=clean_text, lang='en', slow=False)
    audio_file = "temp_audio.mp3"
    tts.save(audio_file)
    audio_base64 = ""
    with open(audio_file, "rb") as audio_file_obj:
        audio_base64 = base64.b64encode(audio_file_obj.read()).decode('utf-8')
    os.remove(audio_file)  # Dosya kilitlendikten sonra silme
    audio_html = f"""
    <audio id="audio" controls>
        <source src="data:audio/mp3;base64,{audio_base64}" type="audio/mp3">
        Tarayıcınız ses oynatmayı desteklemiyor.
    </audio>
    <script>
        document.getElementById('audio').play();
    </script>
    """
    st.markdown(audio_html, unsafe_allow_html=True)
#------------------------------------------------------23.05.2025
def play_word(word):
    try:
        tts = gTTS(text=word, lang='en', slow=True)  # slow=True ile daha net telaffuz
        audio_file = "temp_word_audio.mp3"
        tts.save(audio_file)
        audio_base64 = ""
        with open(audio_file, "rb") as audio_file_obj:
            audio_base64 = base64.b64encode(audio_file_obj.read()).decode('utf-8')
        os.remove(audio_file)
        audio_html = f"""
        <audio id="word_audio_{word}" controls>
            <source src="data:audio/mp3;base64,{audio_base64}" type="audio/mp3">
            Tarayıcınız ses oynatmayı desteklemiyor.
        </audio>
        <script>
            document.getElementById('word_audio_{word}').play();
        </script>
        """
        st.markdown(audio_html, unsafe_allow_html=True)
    except Exception as e:
        st.error(f"Telaffuz oynatılamadı: {e}")

#-----------------------------------------------------------23.05.2025
def translate_word(word):
    try:
        return GoogleTranslator(source='en', target='tr').translate(word)
    except Exception:
        return "Çeviri yapılamadı"

def translate_paragraph(paragraph):
    try:
        return GoogleTranslator(source='en', target='tr').translate(paragraph)
    except Exception as e:
        return f"Paragraf çevirisi yapılamadı: {e}"

def report_errors(error_rate, extra_words, missing_words):
    error_rate_percent = round(error_rate * 100)
    st.write(f"**Hata Oranı:** {error_rate_percent}%")

    if extra_words:
        st.write("**Fazladan söylenen kelimeler:**")
        st.write(", ".join(extra_words))
    else:
        st.write("**Harika!** Fazladan kelime yok.")

    if missing_words:
        st.write("**Eksik kelimeler:**")
        missing_data = []
        for word in missing_words:
            phonetics = pronouncing.phones_for_word(word)
            phonetic = phonetics[0] if phonetics else "Telaffuz bulunamadı"
            translation = translate_word(word)
            missing_data.append({"Kelime": word, "Telaffuz": phonetic, "Türkçe": translation})
        st.table(missing_data)

def listen_and_convert():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        st.write("3 saniye bekleyin, 'bib' sesinden sonra konuşmaya başlayın...")
        time.sleep(2)  # 2 saniye gecikme
        winsound.Beep(500, 200)  # "bib" sesi
        st.write("Lütfen konuşmaya başlayın... (45 saniye)")
        recognizer.adjust_for_ambient_noise(source, duration=1)  # Daha kısa gürültü ayarı
        recognizer.energy_threshold = 300  # Daha yüksek eşik
        recognizer.pause_threshold = 1.0  # Sessizlik algılama süresi (1 saniye)
        audio = recognizer.listen(source, timeout=45, phrase_time_limit=40)
        try:
            spoken_text = recognizer.recognize_google(audio, language="en-US")
            return spoken_text
        except sr.UnknownValueError:
            return "Konuşma tanınamadı. Daha net konuşmayı deneyin."
        except sr.RequestError as e:
            return f"API hatası: {e}"
def main():
    st.title("Sesle Okuma Çalışması")
    st.write("DEBUG: App started")
    st.write("Rastgele sayı:", random.randint(1, 152))
    st.write(f"**Toplam Konu Sayısı:** {TOTAL_TOPICS}")

    if "paragraphs" not in st.session_state:
        st.session_state["paragraphs"] = []
        st.session_state["current_index"] = 0
        st.session_state["selected_word"] = None
        st.session_state["translation"] = ""
        st.session_state["doc_text"] = {}
        st.session_state["translated_paragraph"] = ""
        st.session_state["spoken_text"] = ""

    doc_path = st.text_input("Word Dosya Yolu", value="H:\\OCR_Ana_Cikti_Guncel.docx")
    topic_no = st.number_input("Konu No giriniz:", min_value=1, max_value=TOTAL_TOPICS, step=1, help=f"Toplam {TOTAL_TOPICS} konu mevcut. Lütfen 1 ile {TOTAL_TOPICS} arasında bir sayı seçin.")

    if st.button("Metni Yükle"):
        if doc_path and os.path.exists(doc_path):
            cache_key = f"{doc_path}_{topic_no}"
            if cache_key not in st.session_state["doc_text"]:
                text = get_text_from_docx(doc_path, topic_no)
                if text:
                    st.session_state["doc_text"][cache_key] = text
                    paragraphs = split_into_paragraphs(text)
                    st.session_state["paragraphs"] = paragraphs
                    st.session_state["current_index"] = 0
                    st.session_state["selected_word"] = None
                    st.session_state["translation"] = ""
                    st.session_state["translated_paragraph"] = ""
                    st.session_state["spoken_text"] = ""
                    st.success("Metin yüklendi!")
                else:
                    st.error("Konu bulunamadı!")
            else:
                text = st.session_state["doc_text"][cache_key]
                paragraphs = split_into_paragraphs(text)
                st.session_state["paragraphs"] = paragraphs
                st.session_state["current_index"] = 0
                st.session_state["selected_word"] = None
                st.session_state["translation"] = ""
                st.session_state["translated_paragraph"] = ""
                st.session_state["spoken_text"] = ""
                st.success("Metin önbellekten yüklendi!")
        else:
            st.error("Geçersiz dosya yolu!")

    if st.session_state["paragraphs"]:
        paragraphs = st.session_state["paragraphs"]
        current_index = st.session_state["current_index"]

        st.subheader(f"Paragraf {current_index + 1}/{len(paragraphs)}")
        st.write(f"DEBUG: Current paragraph index: {current_index}")
        st.write(paragraphs[current_index])

        if st.button("Paragrafı Çevir", key="translate_paragraph"):
            translated = translate_paragraph(paragraphs[current_index])
            st.session_state["translated_paragraph"] = translated

        if st.session_state["translated_paragraph"]:
            st.write("**Çevrilmiş Paragraf (Türkçe):**")
            st.write(st.session_state["translated_paragraph"])
#-------------------------------------
        st.write("**Kelime çevirisi için kelimelere tıklayın:**")
        cols = st.columns(5)
        for i, word in enumerate(paragraphs[current_index].split()):
            with cols[i % 5]:
                if st.button(word, key=f"word_{i}_{current_index}"):
                    st.session_state["selected_word"] = word
                    st.session_state["translation"] = translate_word(word)
                    play_word(word)  # Kelimeye tıklandığında telaffuzu oynat
        if st.session_state["selected_word"]:
            st.write(f"'{st.session_state['selected_word']}' çevirisi: {st.session_state['translation']}")
#-----------------------------------------------------------------

        col1, col2, col3, col4 = st.columns(4)
        with col1:
            if st.button("Paragrafı Oku", key="read_paragraph"):
                read_paragraph(paragraphs[current_index])
        with col2:
            if st.button("Sesimi Kaydet", key="record_speech"):
                spoken_text = listen_and_convert()
                st.session_state["spoken_text"] = spoken_text
                st.write("**Tanınan Metniniz (Sizin Okumanız):**")
                st.write(spoken_text)
            if st.session_state["spoken_text"] and not st.session_state["spoken_text"].startswith("Konuşma"):
                if st.button("Analizi Yap", key="analyze_speech"):
                    error_rate, extra_words, missing_words = evaluate_speech(paragraphs[current_index], st.session_state["spoken_text"])
                    if error_rate < ERROR_THRESHOLD:
                        st.success("Harika! Okumanız oldukça iyi.")
                    else:
                        st.warning("Bazı hatalar var. Aşağıdaki raporu inceleyin.")
                    report_errors(error_rate, extra_words, missing_words)
                    st.write("**Karşılaştırma:**")
                    st.write("Orijinal Paragraf:", paragraphs[current_index])
                    st.write("Sizin Okumanız:", st.session_state["spoken_text"])
        with col3:
            if st.button("Önceki"):
                if current_index > 0:
                    st.session_state["current_index"] -= 1
                    st.session_state["translated_paragraph"] = ""
                    st.session_state["spoken_text"] = ""
                    st.rerun()
                else:
                    st.warning("Bu ilk paragraf, daha geriye gidemezsiniz!")
        with col4:
            if st.button("Sonraki"):
                if current_index < len(paragraphs) - 1:
                    st.session_state["current_index"] += 1
                    st.session_state["translated_paragraph"] = ""
                    st.session_state["spoken_text"] = ""
                    st.rerun()
                else:
                    st.warning("Bu son paragraf, daha ileri gidemezsiniz!")

if __name__ == "__main__":
    main()
