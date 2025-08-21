import os
from pydub import AudioSegment

def add_jingles(news_audio_path, intro_path, outro_path, output_path):
    """
    Fügt Jingles vor und nach der Nachrichtensendung hinzu.

    :param news_audio_path: Pfad zur Nachrichtensendung (z. B. .mp3).
    :param intro_path: Pfad zum Intro-Jingle (z. B. .m4a).
    :param outro_path: Pfad zum Outro-Jingle (z. B. .m4a).
    :param output_path: Pfad zur finalen Ausgabe (z. B. .mp3).
    """
    # Lade die Audiodateien
    news_audio = AudioSegment.from_file(news_audio_path)
    intro_jingle = AudioSegment.from_file(intro_path)
    outro_jingle = AudioSegment.from_file(outro_path)

    # Berechne Startzeitpunkte
    intro_start = intro_jingle[-11500:]  # Letzte 11,5 Sekunden des Intros
    outro_start = outro_jingle[:6000]    # Erste 6 Sekunden des Outros

    # Überlagere das Intro mit der Nachrichtensendung
    combined_intro = intro_start.overlay(news_audio, position=0)

    # Überlagere das Outro mit der Nachrichtensendung
    combined_outro = combined_intro.overlay(outro_start, position=len(combined_intro) - len(outro_start))

    # Speichere die finale Datei
    combined_outro.export(output_path, format="mp3")
    print(f"Finale Datei mit Jingles gespeichert unter: {output_path}")

if __name__ == "__main__":
    # Standardpfade
    script_dir = os.path.dirname(os.path.abspath(__file__))
    default_news_path = os.path.join(script_dir, "outputs", "results", "speech", "news_output.mp3")
    default_intro_path = os.path.join(script_dir, "input", "jingles", "waa_intro_jingle.m4a")
    default_outro_path = os.path.join(script_dir, "input", "jingles", "waa_outro_jingle.m4a")
    default_output_path = os.path.join(script_dir, "outputs", "results", "speech", "news_with_jingles.mp3")

    # Eingabe der Pfade über das Terminal
    news_audio_path = input(f"Pfad zur Nachrichtensendung (Standard: {default_news_path}): ").strip() or default_news_path
    intro_path = input(f"Pfad zum Intro-Jingle (Standard: {default_intro_path}): ").strip() or default_intro_path
    outro_path = input(f"Pfad zum Outro-Jingle (Standard: {default_outro_path}): ").strip() or default_outro_path
    output_path = input(f"Pfad zur Ausgabedatei (Standard: {default_output_path}): ").strip() or default_output_path

    # Überprüfe, ob die Eingabedateien existieren
    if not os.path.exists(news_audio_path):
        print(f"Fehler: Die Nachrichtensendung '{news_audio_path}' wurde nicht gefunden.")
        exit(1)
    if not os.path.exists(intro_path):
        print(f"Fehler: Das Intro-Jingle '{intro_path}' wurde nicht gefunden.")
        exit(1)
    if not os.path.exists(outro_path):
        print(f"Fehler: Das Outro-Jingle '{outro_path}' wurde nicht gefunden.")
        exit(1)

    # Füge Jingles hinzu
    add_jingles(news_audio_path, intro_path, outro_path, output_path)