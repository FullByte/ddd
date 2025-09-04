Es gibt einen W3C SSML Standard:
https://www.w3.org/TR/speech-synthesis11

Die Hauptelemente sind:

<speak> → Wurzelelement.
<voice> → Stimme wählen (Sprache, Geschlecht, evtl. Name).
<prosody> → rate (Geschwindigkeit), pitch (Tonhöhe), volume.
<break> → Pause (time oder strength).
<emphasis> → Betonung (strong, moderate, reduced).
<say-as> → spezielle Lesarten (Zahlen, Datum, Uhrzeit, Buchstaben).
<phoneme> → phonetische Aussprache (IPA oder andere Alphabete).
<sub> → Ersatztext („substitution“).
<p>, <s> → Absätze/Sätze.

Würde sagen wir erstellen in den konkreten workflows hierfür schon input und machen es dann im zentralen fertig für das verwendete TTS model.
