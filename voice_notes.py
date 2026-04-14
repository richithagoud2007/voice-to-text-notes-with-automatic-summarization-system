import speech_recognition as sr
import nltk

nltk.download('punkt')

from sumy.parsers.plaintext import PlaintextParser
from sumy.nlp.tokenizers import Tokenizer
from sumy.summarizers.lsa import LsaSummarizer


def voice_to_text():
    r = sr.Recognizer()

    with sr.Microphone() as source:
        print("Adjusting noise...")
        r.adjust_for_ambient_noise(source)

        print("Speak something...")
        audio = r.listen(source)

    try:
        text = r.recognize_google(audio)
        print("Text:", text)
        return text
    except:
        print("Could not understand")
        return ""


def summarize_text(text):
    parser = PlaintextParser.from_string(text, Tokenizer("english"))
    summarizer = LsaSummarizer()

    summary = summarizer(parser.document, 1)

    print("\nSummary:")
    for sentence in summary:
        print(sentence)


text = voice_to_text()

if text != "":
    summarize_text(text)