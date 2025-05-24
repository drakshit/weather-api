import json
import pandas as pd
from flask import render_template, Flask

PORT = 5001

df = pd.read_csv("data_small/stations.txt", skiprows=17)
headers = df.columns
sta_id = headers[0]
sta_name = headers[1]
station_info = df[[sta_id, sta_name]]


def read_file(station_id, date=None, year=None, month=None):
    file_name = f"data_small/TG_STAID{str(station_id).zfill(6)}.txt"
    df_tg = pd.read_csv(file_name, skiprows=20, parse_dates=["    DATE"])

    if date is not None:
        temp = df_tg.loc[(df_tg[' Q_TG'] < 3) & (df_tg["    DATE"] == date)]["   TG"]
        return int(temp.squeeze()) / 10
    elif year is not None and month is None:
        df_tg["    DATE"] = df_tg["    DATE"].astype(str)
        temp = df_tg.loc[(df_tg[' Q_TG'] < 3) & (df_tg["    DATE"].str.startswith(year))][["    DATE", "   TG"]]
        response = temp.to_json(orient="records")
        return response
    elif year is not None and month is not None:
        yr_m = f"{year}-{month}"
        df_tg["    DATE"] = df_tg["    DATE"].astype(str)
        temp = pd.DataFrame(df_tg.loc[(df_tg[' Q_TG'] < 3) & (df_tg["    DATE"].str.startswith(yr_m))][['   TG', '    DATE']])
        response = temp.to_json(orient="records")
        return response

app = Flask(__name__)


@app.route("/")
def home():
    return render_template("home.html", data=station_info.to_html(), port=PORT)


# API route for stations
@app.route("/api/v1/<station>/")
def api_stations(station):
    file_name = f"data_small/TG_STAID{str(station).zfill(6)}.txt"
    df_tg = pd.read_csv(file_name, skiprows=20, parse_dates=["    DATE"])
    result = df_tg.to_dict(orient="records")
    return result


# API route for specific station on specific date
@app.route("/api/v1/<station>/<date>/")
def api_date(station, date):
    station_name = df.loc[df[sta_id] == int(station)][sta_name].squeeze().strip()
    temperature = read_file(station, date=date)
    response = {"station": station_name, "date": date, "temperature": temperature}
    return response


# API route for a specific station on a specific year
@app.route("/api/v1/yearly/<station>/<year>/")
def api_year(station, year):
    station_name = df.loc[df[sta_id] == int(station)][sta_name].squeeze().strip()
    temperature = read_file(station, year=year)
    response = {"station": station_name, "yyyy": year, "temperature": json.loads(temperature)}
    return response


# API route for a specific station on a specific year/month
@app.route("/api/v1/<station>/<year>/<month>/")
def api_year_month(station, year, month):
    station_name = df.loc[df[sta_id] == int(station)][sta_name].squeeze().strip()
    temperature = read_file(station, year=year, month=month)
    response = {"station": station_name, "yyyy-mm": year+'-'+month, "temperature": json.loads(temperature)}
    return response


if __name__ == "__main__":
    app.run(debug=True, port=PORT)
