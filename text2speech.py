import pyttsx3       #text to speech conversion library

engine = pyttsx3.init()

text ="This will help me consume the literature in a more efficient way. I can listen to the books while doing other tasks, which saves time and allows me to multitask."

engine.say(text)

#playing the speech
engine.runAndWait()
