from flask import Flask, render_template
import pandas as pd

df = pd.read_csv("data_small/stations.txt", skiprows=17)
headers = df.columns
sta_id = headers[0]
sta_name = headers[1]

def read_file(station_id, date):
    file_name = f"data_small/TG_STAID{str(station_id).zfill(6)}.txt"
    df_tg = pd.read_csv(file_name, skiprows=20, parse_dates=["    DATE"])
    min_temp = df_tg.loc[df_tg["    DATE"] == date]['   TG']
    return int(min_temp.squeeze()) / 10

app = Flask(__name__)

@app.route("/")
def home():
    return render_template("home.html")


# API route
@app.route("/api/v1/<station>/<date>/")
def api(station, date):
    station_name = df.loc[df[sta_id] == int(station)][sta_name].squeeze().strip()
    temperature = read_file(station,date)
    response = {"station": station_name, "date": date, "temperature": temperature}
    return response


if __name__ == "__main__":
    app.run(debug=True, port=5001)
