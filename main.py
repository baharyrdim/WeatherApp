#BersayYakıcı-20200601059
#BaharYardım-20200601060
#BarkanUzun-20210601062

#Here the libraries that we had used.
import os #It offers various functions for working with files and directories, accessing environment variables, executing system commands, and more.
from tkinter import *
from bs4 import BeautifulSoup
from utils import retrieve_rendered_weather_page, TodayWeatherInfo, ForecastWeatherInfo
from tkinter import messagebox
from PIL import Image, ImageTk
import time
import requests
import tksvg
from tkinter import OptionMenu

#This is our first function. It saves the selected city and unit to settings.txt if there is no settings.txt it created itself.
def save_settings():
    global selected_city
    global selected_unit

    settings = f"City: {selected_city.get()}\n"
    settings += f"Temperature Unit: {selected_unit.get()}"

    with open(SETTINGS_FILE, "w", encoding="utf-8") as file:
        file.write(settings)

#This is our second function and it is for showing the saved unit and city.
def load_settings():
    global selected_city
    global selected_unit

    try:
        with open(SETTINGS_FILE, "r", encoding="utf-8") as file:
            settings = file.read().splitlines()
            for line in settings:
                if line.startswith("City:"):
                    city_name = line.split(":")[1].strip().capitalize()
                    selected_city.set(city_name)
                elif line.startswith("Temperature Unit:"):
                    selected_unit.set(line.split(":")[1].strip())
    except FileNotFoundError:
        pass

#This is our third function. It is for the weather window.
def show_weather():
    global BASE_URL
    global selected_city
    global selected_unit
    global window
    global forecast_data_list

    selected_city_name = selected_city.get()
    unit_label.config(text="Temperature unit: " + selected_unit.get())

    if not selected_city_name or selected_city_name == "Select a city":
        messagebox.showwarning("Warning", "Please select a city.")
        return

    selected_city.set(selected_city_name.lower())

    try:
        html = retrieve_rendered_weather_page(f"{BASE_URL}/?il={selected_city.get()}")
    except Exception as e:
        messagebox.showerror("Error", "An error occurred while retrieving weather information:\n" + str(e))
        return

    soup = BeautifulSoup(html, 'html.parser')

    #In these lines we make user to choose the unit.
    today_temp_celsius = float(soup.find('span', class_='pull-left').text.strip().replace("\n°C", "").replace(",", "."))
    if selected_unit.get() == "Fahrenheit":
        today_temp_fahrenheit = (today_temp_celsius * 9 / 5) + 32
        temp_unit = "°F"
        today_temp = today_temp_fahrenheit
    else:
        temp_unit = "°C"
        today_temp = today_temp_celsius

    today_weather_information = soup.select_one(
        'section.weather.ng-scope > div > div.left > div.instant-weather > div > p').text.strip()
    today_proximity_percentage = soup.select_one(
        "section.weather.ng-scope > div > div.left > div.instant-weather > div > h3 > span.details.expanded > div > span.detail.humidity > span.value.ng-binding").text.strip()
    today_wind_kmh = soup.select_one(
        "section.weather.ng-scope > div > div.left > div.instant-weather > div > h3 > span.details.expanded > div > span.detail.wind > div > div > span.ng-binding").text.strip()
    today_pressure_hpascal = soup.select_one(
        "section.weather.ng-scope > div > div.left > div.instant-weather > div > h3 > span.details.expanded > div > span.detail.pressure > span.value.ng-binding").text.strip()

    today_data = TodayWeatherInfo(weather_information=today_weather_information, temp=today_temp,
                                  proximity_percentage=today_proximity_percentage, wind_kmh=today_wind_kmh,
                                  pressure_value=today_pressure_hpascal)

    forecast_div = soup.find('div', class_='forecast')
    tahmin_divs = forecast_div.find_all('div', class_='tahmin')

    #Extract forecast weather information.
    forecast_data_list = []
    for tahmin_div in tahmin_divs:
        tahminTarih = tahmin_div.find('div', class_='tahminTarih').text.strip()
        weather_information = tahmin_div.find("div", class_="tahminHadise").text
        temperature_day_celsius = float(tahmin_div.find("div", class_="tahminMin").find("span", class_="deger").text)
        temperature_night_celsius = float(tahmin_div.find("div", class_="tahminMax").find("span", class_="deger").text)
        wind_kmh = tahmin_div.find("div", class_="ruzgarDeger").find("span", class_="deger").text
        wind_direction = tahmin_div.find("div", class_="ruzgarYon").find("span").text
        proximity_percentage = tahmin_div.find(class_='nem').find_next(class_='deger').text.strip()

        img_tag = tahmin_div.find('img')
        img_src = img_tag['src'] if img_tag else ""
        img_src = BASE_URL + img_src.replace("..", "")
        filename = os.path.basename(img_src)
        svg_local_path = os.path.join("images", filename)
        if not os.path.exists(svg_local_path):
            os.makedirs("images", exist_ok=True)
            response = requests.get(img_src)
            if response.status_code == 200:
                with open(svg_local_path, 'wb') as file:
                    file.write(response.content)
                print("SVG file downloaded and saved successfully.")
            else:
                print("Failed to download SVG file.")

        if selected_unit.get() == "Fahrenheit":
            temperature_day_fahrenheit = (temperature_day_celsius * 9 / 5) + 32
            temperature_night_fahrenheit = (temperature_night_celsius * 9 / 5) + 32
            temp_unit = "°F"
            temperature_day = temperature_day_fahrenheit
            temperature_night = temperature_night_fahrenheit
        else:
            temp_unit = "°C"
            temperature_day = temperature_day_celsius
            temperature_night = temperature_night_celsius

        forecast_data = ForecastWeatherInfo(day_of_the_week=tahminTarih, icon=svg_local_path, weather_information=weather_information,
                                            temp_day=temperature_day, temp_night=temperature_night,
                                            wind_kmh=wind_kmh, wind_direction=wind_direction,
                                            proximity_percentage=proximity_percentage)
        forecast_data_list.append(forecast_data)

    #Display today's weather information.
    messagebox.showinfo("Weather forecast", f"City: {selected_city_name}\n"
                                       f"Temperature: {today_data.temp} {temp_unit}\n"
                                       f"Weather condition: {today_data.weather_information}\n"
                                       f"Humidity: %{today_data.proximity_percentage}\n"
                                       f"Wind: {today_data.wind_kmh} km/h\n"
                                       f"Pressure: {today_data.pressure_value} ")

    #Display forecast weather information.
    forecast_info = "5 Day Weather Forecast:\n"

    display_next_forecast()

    save_settings()
#This is our fourth function. This is for the 5 day forecast images.
def show_custom_messagebox(svg_path, title, message):
    global window
    window_mb = Toplevel(window)
    window_mb.title(title)

    svg_image = tksvg.SvgImage(file=svg_path)
    label = Label(window_mb, image=svg_image)
    label.pack()

    #Create a label for the message.
    message_label = Label(window_mb, text=message)
    message_label.pack(padx=10, pady=10)

    #Bind the close event of the window to a callback function.
    window_mb.protocol("WM_DELETE_WINDOW", lambda: on_window_close(window_mb))
    window_mb.mainloop()

def on_window_close(window_mb):
    window_mb.destroy()
    display_next_forecast()
#It simply destroys the window by calling the destroy() method on the window object.

def display_next_forecast():
    global forecast_data_list
    global selected_unit

    if selected_unit.get() == "Fahrenheit":
        temp_unit = "°F"
    else:
        temp_unit = "°C"

    if forecast_data_list:
        forecast_data = forecast_data_list.pop(0)

        forecast_info = f"\nDate: {forecast_data.day_of_the_week}\n"
        forecast_info += f"Weather condition: {forecast_data.weather_information}\n"
        forecast_info += f"Day temperature: {forecast_data.temp_night} {temp_unit}\n"
        forecast_info += f"Night temperature: {forecast_data.temp_day} {temp_unit}\n"
        forecast_info += f"Wind: {forecast_data.wind_kmh} km/h\n"
        forecast_info += f"Wind direction: {forecast_data.wind_direction}\n"
        forecast_info += f"Humidity: %{forecast_data.proximity_percentage}\n\n"

        show_custom_messagebox(forecast_data.icon, "Weather Forecast", forecast_info)
    else:
        save_settings()
#This function is for showing the 5 day forecast.
def create_welcome_page():
    window1 = Tk()
    window1.title('Welcome Page')
    window1.geometry('700x400+300+200')
    window1.config(background="#C6E2FF")

    load_settings()

    welcome_message = "Welcome! \n The last city you checked was: " + selected_city.get() +  "\nDefault temperature unit: " + selected_unit.get()

    welcome_label = Label(window1, text=welcome_message, font=("Arial", 20))
    welcome_label.pack(pady=20)

    continue_button = Button(window1, text="Continue", command=lambda: [window1.destroy(), window.deiconify()])
    continue_button.pack(pady=20)
#This function is for creating a welcome page.

def toggle_units():
    if selected_unit.get() == "Celsius":
        selected_unit.set("Fahrenheit")
    else:
        selected_unit.set("Celsius")

def show_help_message():
    help_text = """
    Here is how to use this application:
    1. Select a city from the list.
    2. Select/Toggle the temperature unit (Celsius or \n        Fahrenheit).
    3. Click on 'Show Weather' to get today's weather and \n        5-day forecast.
    """
    messagebox.showinfo("Help", help_text)

if __name__ == "__main__":
    BASE_URL = "http://www.mgm.gov.tr"  #This is our url. This is a Turkish website that we pull data so the info's are Turkish.
    CITY_FILE = "sehirler.txt"
    SETTINGS_FILE = "Settings.txt"

    selected_city = ""
    selected_unit = ""
    forecast_data_list = []

    window = Tk()
    window.title('Weather App')
    window.geometry('900x500+300+200')
    window.config(background="#C6E2FF")
    window.resizable(False, False)
    window.withdraw()

    img = Image.open("weather-of-izmir-in-turkey.jpg")
    imgtk = ImageTk.PhotoImage(img)
    label = Label(window, image=imgtk)
    label.place(x=0, y=0)

    selected_city = StringVar()
    selected_unit = StringVar()

    create_welcome_page()

    load_settings()

    cities = []

    try:
        with open(CITY_FILE, "r", encoding="utf-8") as file:
            cities = file.read().splitlines()
    except FileNotFoundError:
        messagebox.showwarning("Warning", "Could not find the sehirler file")

    selected_city = StringVar(window)
    selected_city.set("Select a city")  # Default option

    city_option_menu = OptionMenu(window, selected_city, *cities)
    city_option_menu.config(width=30)
    city_option_menu.pack()

    unit_label = Label(window, text="Temperature unit:")
    unit_label.pack()
    unit_frame = Frame(window)
    unit_frame.pack()

    celsius_radio = Radiobutton(unit_frame, text="Celsius", variable=selected_unit, value="Celsius")
    celsius_radio.pack(side=LEFT)
    fahrenheit_radio = Radiobutton(unit_frame, text="Fahrenheit", variable=selected_unit, value="Fahrenheit")
    fahrenheit_radio.pack(side=LEFT)

    if selected_unit.get() == "Fahrenheit":
        fahrenheit_radio.select()
    else:
        celsius_radio.select()

    show_weather_button = Button(window, text="Show Weather Conditions", command=show_weather)
    show_weather_button.pack()

    help_button = Button(window, text="Help", command=show_help_message)
    help_button.pack()

    toggle_button = Button(window, text="Toggle Units", command=toggle_units)
    toggle_button.pack()

    current_time = time.strftime("%H:%M")
    current_time_label = Label(window, text="Current Time: " + current_time, font=("Arial", 14))
    current_time_label.place(x=0, y=0)

    window.mainloop()