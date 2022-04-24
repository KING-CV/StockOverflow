'''
About   :  This program allows us to assess risk related to               Stocks and Crypto.
Authors :  Chirag Singh, Eric Higgins, Marcus Weinberger,                 Michael Clark
'''
from flask import Flask, jsonify, request, render_template
from flask_sqlalchemy import SQLAlchemy
from cockroachdb.sqlalchemy import run_transaction
from google_images_search import GoogleImagesSearch
from pathlib import Path
import sqlalchemy.orm
import requests
import yfinance
import _thread
import time
import os

from config import AppConfig

app = Flask(__name__)
app.config.from_object(AppConfig())
db = SQLAlchemy(app)
sessionmaker = sqlalchemy.orm.sessionmaker(db.engine)

GIS = lambda: GoogleImagesSearch(os.getenv('GOOGLE'), '9188ab17ef4ef4892')

os.system('curl --create-dirs -o $HOME/.postgresql/root.crt -O https://cockroachlabs.cloud/clusters/2250ae84-cb06-4051-b10c-e89e5cd74c97/cert') # install ssl certificate for connection

def update_trending():
    for name in yf_trending():
        if Logos.query.filter_by(name=name).first() is None:
            ticker = yfinance.Ticker(name)
            if (url := ticker.info.get('logo_url')):
                logo = Logos(name, time.time(), url)
            else:
                gis = GIS()
                gis.search({
                    'q': f'{name.upper()} logo',
                    'num': 1,
                    'imgSize': 'icon',
                    'fileType': 'png'
                })
                url = list(gis.results())[0].url
                logo = Logos(name, time.time(), url)
            def callback(session):
                session.add(logo)
            run_transaction(sessionmaker, callback)
    print('Updated trending')

class Logos(db.Model):
    __tablename__ = 'logos'
    
    name = db.Column(db.String, primary_key=True)
    url = db.Column(db.String, default='/static/blank.png')
    ts = db.Column(db.Integer)

    def __init__(self, name: str, ts: int, url: str=None):
        self.name = name
        self.url = url
        self.ts = ts * 10000000

class Info(db.Model):
    __tablename__ = 'info'

    name = db.Column(db.String, primary_key=True)
    circulatingsupply = db.Column(db.Integer)
    currentprice = db.Column(db.Float)
    debttoequity = db.Column(db.Float)
    ebitda = db.Column(db.Integer)
    forwardeps = db.Column(db.Float)
    forwardpe = db.Column(db.Float)
    grossmargins = db.Column(db.Float)
    grossprofits = db.Column(db.Integer)
    industry = db.Column(db.String)
    longname = db.Column(db.String)
    marketcap = db.Column(db.Integer)
    recommendationkey = db.Column(db.String)
    sector = db.Column(db.String)
    symbol = db.Column(db.String)
    totalrevenue = db.Column(db.Integer)
    volume = db.Column(db.Integer)
    website = db.Column(db.String)
    ts = db.Column(db.Integer)

    def __init__(
        self,
        name: str,
        circulatingSupply: int,
        currentPrice: float,
        debtToEquity: float,
        ebitda: int,
        forwardEps: float,
        forwardPE: float,
        grossMargins: float,
        grossProfits: int,
        industry: str,
        longName: str,
        marketCap: int,
        recommendationKey: str,
        sector: str,
        symbol: str,
        totalRevenue: int,
        volume: int,
        website: str,
        ts: float
    ):
        self.name = name
        self.circulatingsupply = circulatingSupply
        self.currentprice = currentPrice
        self.debttoequity = debtToEquity
        self.ebitda = ebitda
        self.forwardeps = forwardEps
        self.forwardpe = forwardPE
        self.grossmargins = grossMargins
        self.grossprofits = grossProfits
        self.industry = industry
        self.longname = longName
        self.marketcap = marketCap
        self.recommendationkey = recommendationKey
        self.sector = sector
        self.symbol = symbol
        self.totalrevenue = totalRevenue
        self.volume = volume
        self.website = website
        self.ts = ts * 10000000

def static_logos():
    return {x.name.split('.')[0].upper(): f'/{x.as_posix()}' for x in Path('static/logos').iterdir() if x.is_file()}

def yf_trending():
    r = requests.post('https://wrapapi.com/use/mjwrap/hackabull/yf-trending/0.0.1', json={
        'wrapAPIKey': os.getenv('WRAP')
    })
    res = r.json()
    if res['success']:
        data = res['data']['output']
        return list(set([x.lstrip('/quote/').split('?')[0].split('-')[0] for x in data]))
    return res

def get_info(ticker_name: str) -> dict:
    '''Get info on {ticker_name} as a dict'''
    ticker = yfinance.Ticker(ticker_name)
    return {
        key: ticker.info.get(key) for key in [
            'circulatingSupply',
            'currentPrice',
            'debtToEquity',
            'ebitda',
            'forwardEps',
            'forwardPE',
            'grossMargins',
            'grossProfits',
            'industry',
            'longName',
            'marketCap',
            'recommendationKey',
            'sector',
            'symbol',
            'totalRevenue',
            'volume',
            'website'         
        ]
    }

def get_news(ticker_name: str) -> list:
    """Get list of news on {ticker_name}"""
    ticker = yfinance.Ticker(ticker_name)
    return list(ticker.news)

def revenue(revenue:int, gross_profit:int,  c_rev:int):
    assert revenue>0 , f'Revenue is always greater than 0. COME ON!!!!'
    net_p = gross_profit - c_rev
    np_margin = (net_p/revenue)*100
    if net_p <0:
        situation = 'loss'
    else:
        situation = 'profit'
    if np_margin <= 5:
        position = 'This investment has higher risk :('
    elif 10<=np_margin < 20:
        position = 'This investment has average risk :|'
    elif np_margin >= 20:
        position = 'This investment has lower risk:)'
    return f"This company {situation} is {net_p}$ and the net {situation} percent is {abs(np_margin):.1f}%\n" \
           f"{position}"
print(revenue(1000,200, 10))

@app.route('/')
def app_index():
    def callback(session):
        trending = session.query(Logos).order_by(Logos.ts.desc()).limit(15).all()
        return render_template('index.html', trending=trending, logos=static_logos())
    return run_transaction(sessionmaker, callback)

@app.route('/<name>')
def app_view(name: str):
    try:
        news = get_news(name)
    except Exception as e:
        print('err getting news:', e)
        news = []
    def callback(session):
        if (info := session.query(Info).filter_by(name=name).first()):
            # check how old data is
            tsnow = time.time() * 10000000
            fivemin = 50000000 * 60
            if (tsnow - info.ts) >= fivemin:
                # update
                infod = {k.lower(): v for k, v in get_info(name).items()}
                infod.update({'ts': time.time() * 10000000, 'name': name})
                session.query(Info).filter_by(name=name).update(infod)
        else:
            infod = get_info(name)
            infod.update({'ts': time.time(), 'name': name})
            info = Info(**infod)
            session.add(info)
        try:
            analysis = revenue(info.totalrevenue, info.grossprofits, info.currentprice)
        except:
            analysis = ''
        return render_template('stock.html', info=info, news=news, aa=analysis)
    return run_transaction(sessionmaker, callback)

if __name__ == '__main__':
    _thread.start_new_thread(update_trending, ())
    app.run(host='0.0.0.0', port=8080)

