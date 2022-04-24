# StockOverflow
Hackabull 2022 Submission

## Inspiration
Our team's leading financial expert, Eric Higgins, pitched us an idea for a website. [Yahoo Finance](https://finance.yahoo.com)'s website is a bloated, confusing mess. With [StockOverflow](https://hackabull22.marcusweinberger.repl.co), you know exactly what you're getting: a clean, and visually pleasing dashboard with only the most **critical** of information (plus a news feed)!

## What it does
We scrape stock market data from Yahoo using [the yfinance library](https://pypi.org/project/yfinance/) and [WrapAPI](https://wrapapi.com/api/dupl/hackabull/yf-trending/0.0.1), then load it into [CockroachDB](https://www.cockroachlabs.com/) as a cache. By using CockroachDB, loading speeds are **drastically** reduced, and an extra layer of reliability is added (CockroachDB is a "distributed SQL database designed for speed, scale, and survival; trusted by thousands of innovators around the globe").

## How we built it
We started off our project by creating a new Python3 repository on [Replit](https://replit.com): an online IDE with handy hosting and multiplayer features. This allowed us to collaborate in real-time from the get-go. I (Marcus Weinberger) decided to choose the [Flask](https://flask.palletsprojects.com/en/2.0.x/) web framework to develop StockOverflow as it provides templating features and a simple syntax. Additionally, our team member Michael Clark has previous experience with it. 

We found ways to scrape data from Yahoo Finance, but after realising it was a little slow, we decided to integrate CockroachDB as a cache. This was done using Flask-SQLAlchemy to ensure thread safety, so that multiple operations on the database don't collide. The frontend website contains little-to-no JavaScript, so that we can achieve maximum performace. This is why Flask was a good choice, as the templating features let us loop through data with a familiar Python syntax.

## Challenges we ran into
Learning CockroachDB took some time, as Marcus was used to document-collection based databases, and no one had extensive experience with SQL. However, once we realised we could create schemas in Python, this solved a lot of our issues with data validation.

We also struggled a lot with designing the frontend, as we tend to favor backend development.

## Accomplishments that we're proud of
The python `yfinance` library was missing one key feature that we needed - the ability to scrape "trending" stocks. This was resolved by using the third-party scraping service, WrapAPI. Deciphering Yahoo's class names gave us all a headache. ([image](https://ibb.co/4WNLD14))

## What we learned
Two of our members learned the Flask framework, as this was their first time using it. Another member learned from the CSS experience of our lead frontend developer, Michael. This was also a first time using CockroachDB for all of us, so we all gained another tool in our arsenal.

## What's next for Stock Overflow
Adding charts, and graph data is the first step in our future, as we feel some of the depth of our data is lacking. We are also searching for new ways to use CockroachDB. I also plan on exploring AWS Lambda, as I'm certain some of our web scraping functions could run on their serverless architecture - potentially speeding up our service.
