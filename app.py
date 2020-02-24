import urllib.request, urllib.parse, urllib.error
import twurl
import ssl
import folium
from geopy.geocoders import Nominatim
from geopy.extra.rate_limiter import RateLimiter
from flask import Flask, render_template, request
import json
geolocator = Nominatim(user_agent="specify_your_app_name_here", timeout=3)
geocode = RateLimiter(geolocator.geocode, min_delay_seconds=2, max_retries=4)


app = Flask(__name__)
app.debug = True


def twitter_func(path):
    """
    (str) -> dict
    Return dict with information from Twitter API.
    """
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    TWITTER_URL = 'https://api.twitter.com/1.1/friends/list.json'
    url = twurl.augment(TWITTER_URL, {'screen_name': path, 'count': '5'})
    connection = urllib.request.urlopen(url, context=ctx)
    data = connection.read().decode()
    js = json.loads(data)
    return js


def generate_tuples(x):
    """
    Returns a list of tuples with name of the friend and his/her location.
    """
    lst = []
    for i in x['users']:
        name = i['screen_name']
        location = i['location']
        lst.append((name, location))
    return lst


def make_map(path):
    """
    (str) -> None
    Generates map, based on information from Twitter API.
    """
    my_map = folium.Map(location=[0, 0], zoom_start=1.5, tiles='Stamen Terrain')
    fg_friends = folium.FeatureGroup(name="Friends")
    data = twitter_func(path)
    my_tuples = generate_tuples(data)
    for i in my_tuples:
        try:
            location_geo = geolocator.geocode(i[1], timeout=5)
            latitude_geo, longitude_geo = location_geo.latitude, location_geo.longitude
            fg_friends.add_child(folium.CircleMarker(location=(latitude_geo, longitude_geo),
                                                     radius=10,
                                                     popup=i[0],
                                                     fill_color='yellow',
                                                     color='blue',
                                                     fill_opacity=0.6))
        except:
            continue
    my_map.add_child(fg_friends)
    my_map.add_child(folium.LayerControl())
    my_map.save('/home/dariaomelkina/web_app_twitter1/templates/Map.html')


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/map", methods=["POST"])
def web_map():
    try:
        path = request.form.get("name")
        if not path:
            return render_template("failure.html")
        make_map(path)
        return render_template("Map.html")
    except:
        return render_template("failure.html")


# if __name__ == '__main__':
#     app.run()
