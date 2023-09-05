from flask import Flask, render_template, request
from bleach import clean
import requests
import bs4

from utils import r_category_ids

app = Flask("ScratchedDB")

@app.get("/")
def home():
    return render_template("home.html")
@app.get("/v1/forum/category/topics/<category>/<page>")
def topic_list(category, page):
    args = request.args.to_dict()
    id = r_category_ids()[category]
    response = requests.get(f"https://scratch.mit.edu/discuss/{id}" , timeout=10)
    soup = bs4.BeautifulSoup(response.content, 'html.parser')
    TRs = []
    for tr in soup.find_all('tr'):
        TRs.append(tr)
    return str(TRs)

app.run()
