import os
import sys
import speech_recognition as sr
import pyttsx3
import threading
import pystray
from PIL import Image, ImageDraw
import pyautogui
import pygame
import subprocess
import webbrowser

# ================= SETTINGS =================
WAKE_WORD = "jarvis"
MUSIC_FOLDER = "music"
RUNNING = True
# ============================================

engine = pyttsx3.init()
engine.setProperty('rate', 170)

def speak(text):
    print("JARVIS:", text)
    engine.say(text)
    engine.runAndWait()

# -------- FILE SEARCH --------
def search_and_open(filename):
    for root, dirs, files in os.walk("C:\\"):
        for file in files:
            if file.lower() == filename.lower():
                os.startfile(os.path.join(root, file))
                speak(f"File '{filename}' mil gayi aur open kar raha hoon")
                return
    speak(f"File '{filename}' nahi mili")

# -------- APP CONTROL --------
def open_app(command):
    if "chrome" in command:
        subprocess.Popen("C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe")
        speak("Chrome open kar raha hoon")
    elif "notepad" in command:
        subprocess.Popen("notepad.exe")
        speak("Notepad open kar raha hoon")
    elif "vs code" in command:
        subprocess.Popen("code")
        speak("VS Code open kar raha hoon")

# -------- WEBSITE --------
def open_website(command):
    if "youtube" in command:
        webbrowser.open("https://youtube.com")
        speak("YouTube open kar raha hoon")
    elif "google" in command:
        webbrowser.open("https://google.com")
        speak("Google open kar raha hoon")

# -------- SCREENSHOT --------
def take_screenshot():
    screenshot = pyautogui.screenshot()
    screenshot.save("screenshot.png")
    speak("Screenshot le liya")

# -------- MUSIC --------
def play_music():
    try:
        songs = os.listdir(MUSIC_FOLDER)
        song = os.path.join(MUSIC_FOLDER, songs[0])
        pygame.mixer.init()
        pygame.mixer.music.load(song)
        pygame.mixer.music.play()
        speak("Music play kar raha hoon")
    except:
        speak("Music folder nahi mila ya empty hai")

# -------- COMMAND PROCESSOR --------
def process_command(command):
    global RUNNING

    command = command.lower()
    
    if "shutdown" in command:
        speak("Goodbye")
        RUNNING = False
        icon.stop()

    elif "open" in command:
        words = command.split()
        if len(words) > 1:
            try:
                filename = words[words.index("open") + 1]
                search_and_open(filename)
            except:
                open_app(command)
                open_website(command)
        else:
            speak("Kya open karna hai?")

    elif "screenshot" in command:
        take_screenshot()

    elif "play music" in command:
        play_music()

    else:
        speak("Command samajh nahi aayi")

# -------- MAIN LOOP --------
def assistant_loop():
    speak("JARVIS activated. Boliye kya karna hai")

    recognizer = sr.Recognizer()
    while RUNNING:
        try:
            with sr.Microphone() as source:
                recognizer.adjust_for_ambient_noise(source, duration=0.5)
                print("Listening for wake word...")
                audio = recognizer.listen(source, timeout=5, phrase_time_limit=5)
            command = recognizer.recognize_google(audio).lower()
            if WAKE_WORD in command:
                speak("Haan, boliye")
                with sr.Microphone() as source2:
                    recognizer.adjust_for_ambient_noise(source2, duration=0.5)
                    audio2 = recognizer.listen(source2, timeout=5, phrase_time_limit=5)
                command2 = recognizer.recognize_google(audio2).lower()
                print(f"Recognized command: {command2}")
                process_command(command2)
        except sr.WaitTimeoutError:
            continue
        except sr.UnknownValueError:
            continue
        except sr.RequestError as e:
            print(f"Google Speech API error: {e}")

# -------- SYSTEM TRAY --------
def create_image():
    image = Image.new('RGB', (64, 64), color=(0, 0, 0))
    d = ImageDraw.Draw(image)
    d.ellipse((16, 16, 48, 48), fill=(0, 255, 0))
    return image

def on_quit(icon, item):
    global RUNNING
    RUNNING = False
    icon.stop()
    sys.exit()

# -------- MAIN --------
icon = pystray.Icon("JARVIS")
icon.icon = create_image()
icon.menu = pystray.Menu(
    pystray.MenuItem("Exit", on_quit)
)

thread = threading.Thread(target=assistant_loop)
thread.daemon = True
thread.start()

icon.run()
