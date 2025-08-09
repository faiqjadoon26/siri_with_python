import speech_recognition as sr
import pyttsx3
import pywhatkit
import datetime
import wikipedia
import pyjokes
import requests
import tkinter as tk
from tkinter import scrolledtext
from googlesearch import search

# Initialize the Tkinter window
window = tk.Tk()
window.title("Alexa")
window.configure(bg='#333333')
window.minsize(800, 600)  # Increase the window size
window.iconbitmap("amazon_alexa_icon_130998.ico")

# Initialize the text-to-speech engine
engine = pyttsx3.init()

# Initialize the speech recognition listener
listener = sr.Recognizer()
voices = engine.getProperty('voices')
engine.setProperty('voice', voices[1].id)

# Create a scrolled text widget for displaying responses
response_text = scrolledtext.ScrolledText(window, width=60, height=30, wrap=tk.WORD)
response_text.grid(row=0, column=0, columnspan=4, padx=10, pady=10)
response_text.config(bg='#000000', fg='white')

# Label for user input
input_label = tk.Label(window, text="Ask something", font=("Arial", 12), bg='#333333', fg="white")
input_label.grid(row=1, column=0, padx=5, pady=10)

# Create an entry widget for user input
user_input_entry = tk.Entry(window, width=50)
user_input_entry.grid(row=1, column=1, padx=10, pady=10)


# Function to get user input from the entry widget
def get_user_input():
    user_input = user_input_entry.get()
    process_user_input(user_input)
    user_input_entry.delete(0, tk.END)


def talk(text):
    engine.say(text)
    engine.runAndWait()


def get_weather(api_key, city):
    base_url = "http://api.openweathermap.org/data/2.5/weather"
    params = {"q": city, "appid": api_key, "units": "metric"}  # Use metric units for temperature in Celsius

    try:
        response = requests.get(base_url, params=params)
        data = response.json()

        if response.status_code == 200:
            temperature = data["main"]["temp"]
            return temperature
        else:
            return None
    except Exception as e:
        print(e)
        return None


# Function to update the response text in the scrolled text widget
def update_response_text(response):
    response_text.config(state=tk.NORMAL)
    response_text.insert(tk.END, response + "\n")
    response_text.config(state=tk.DISABLED)
    response_text.yview(tk.END)


# Function to handle user input and update the GUI
def process_user_input(user_input):
    update_response_text("User: " + user_input)

    if 'play' in user_input:
        song = user_input.replace('play', '').strip()
        update_response_text('Playing ' + song)
        talk(f"Playing {song}")
        pywhatkit.playonyt(song)
        time.sleep(7)
    elif 'time' in user_input:
        current_time = datetime.datetime.now().strftime('%I:%M %p')
        response = 'Current time is ' + current_time
        update_response_text(response)
        talk(response)
    elif 'who is' in user_input:
        person = user_input.replace('who is', '').strip()
        info = wikipedia.summary(person, 3)
        update_response_text(info)
        talk(info)
    elif 'do you want to go on a date' in user_input:
        response = 'Sorry, I have a headache'
        update_response_text(response)
        talk(response)
    elif 'joke' in user_input:
        joke = pyjokes.get_joke()
        update_response_text(joke)
        talk(joke)
    elif 'temperature' in user_input:
        city = "Markham"  # Replace with the desired city
        api_key = "44063949fa5886747f67b7e0cdf657b5"  # Replace with your actual OpenWeatherMap API key
        temperature = get_weather(api_key, city)

        if temperature is not None:
            response = f"The current temperature in {city} is {temperature} degrees Celsius."
            update_response_text(response)
            talk(response)
        else:
            response = "Sorry, I couldn't fetch the temperature at the moment."
            update_response_text(response)
            talk(response)
    elif 'news' in user_input:
        news_url = "https://newsapi.org/v2/top-headlines"
        news_params = {"country": "ca", "apiKey": "dcc96d85844d4ac6bed351c5444270fe"}  # Replace with your News API key

        try:
            response = requests.get(news_url, params=news_params)
            response.raise_for_status()  # Raise an HTTPError for bad responses
            news_data = response.json()

            if response.status_code == 200 and news_data["status"] == "ok":
                articles = news_data["articles"]
                if articles:
                    for i, article in enumerate(articles):
                        text = f"News {i + 1}: {article['title']}"
                        update_response_text(text)
                        talk(text)
                else:
                    talk("No news articles found.")
            else:
                talk(f"News API returned an error: {news_data.get('message', 'Unknown error')}")
        except requests.exceptions.RequestException as e:
            talk(f"Error fetching news data: {e}")

    elif 'search for' in user_input:
        query = user_input.replace('search for', '').strip()

        search_results = list(search(query, num_results=3))

        if search_results:
            response = f"Here are some search results for '{query}':"
            for i, result in enumerate(search_results, start=1):
                response += f"\n{i}. {result}"
            update_response_text(response)
            talk(response)
        else:
            response = f"Sorry, I couldn't find any results for '{query}'."
            update_response_text(response)
            talk(response)

    elif 'hi alexa' in user_input:
        response = "Thanks for asking, I am fine. What about you?"
        update_response_text(response)
        talk(response)

    else:
        response = f"Sorry, I couldn't find any results for '{user_input}'."
        update_response_text(response)
        talk(response)


# Function to handle voice command
def voice_command():
    try:
        with sr.Microphone() as source:
            talk('Listening for voice command...')
            listener.adjust_for_ambient_noise(source)
            voice = listener.listen(source)
            user_input = listener.recognize_google(voice).lower()
            process_user_input(user_input)
    except sr.UnknownValueError:
        talk("Sorry, I could not understand. Please repeat.")
    except sr.RequestError as e:
        talk(f"Could not request results from Google Speech Recognition service; {e}")
    except Exception as e:
        talk(f"An unexpected error occurred {e}.")


# Bind the Enter key to the get_user_input function
user_input_entry.bind('<Return>', get_user_input)

# Button to trigger voice command
voice_button = tk.Button(window, text="Microphone", command=voice_command, bg='#333333', fg='white')
voice_button.grid(row=1, column=3, padx=10, pady=5)

# Start the Tkinter event loop
talk("Hi, I am Alexa, your virtual assistant.")
talk("How can I help you?")
window.mainloop()
talk("Thanks for using me. Have a great day.")
