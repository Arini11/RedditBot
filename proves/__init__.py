from gtts import gTTS
frase = """Tú iluminaste mi vida,
por eso, mujer querida
te canto esta noche azul.
Por eso vengo a robarte
un rayito de tu luz."""
tts = gTTS(frase, lang='es', tld='com.mx')
tts.save('hola.mp3')