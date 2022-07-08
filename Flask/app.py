from flask import Flask, render_template, request, redirect, url_for
import sys
import pandas as pd
from flask_sqlalchemy import SQLAlchemy
from flask_sqlalchemy_report import Reporter 
from datetime import datetime

sys.path.append('C:/Users/User/Desktop/Ahmad/Stages/SurfMetrics/Git/Code/First_Full_model')

app=Flask(__name__,template_folder='templates')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///tweets.db'

#Initialize the database
db = SQLAlchemy(app)

#Create db model
class Tweets(db.Model):
      id = db.Column(db.Integer, primary_key= True)
      tweet = db.Column(db.String(1000),nullable=False)
      lang = db.Column(db.String(10),nullable=False)
      True_label = db.Column(db.String(10),nullable=True)
      FB_label = db.Column(db.String(10),nullable=True)
      Mean_label = db.Column(db.String(10),nullable=True)
      GS_label = db.Column(db.String(10),nullable=True)
      date_created = db.Column(db.DateTime, default= datetime.utcnow)
      #Create a function to return a string when we add something
      def __repr__(self):
            return '<tweet %r>' % self.id


# Manual trials

from ESG_filters import gs_esg, mean_esg
from Finbert_esg_filter import finbert_esg

@app.route('/<int:id>', methods=['GET','POST'])
def manual(id):
      tweet = Tweets.query.get_or_404(id)
      if request.method == "POST":
            if request.form.get("btn")=="Classify":
                  query = request.form.get('query')
                  models = request.form.getlist('filter')
                  lang = request.form.get('lang')

                  if 'Mean' in models:
                        resmean = mean_esg(query, lang)
                  else:
                        resmean = None 
                  if "Bert" in models:
                        resbert = finbert_esg(query, lang)
                  else:
                        resbert = None
                  if "GS" in models:
                        resgs = gs_esg(query, lang)
                  else: 
                        resgs = None
                  new_tweet = Tweets(tweet=query, lang=lang, FB_label=resbert, Mean_label=resmean, GS_label=resgs)

                  db.session.add(new_tweet)
                  db.session.commit()
                  return redirect(url_for('manual', id=new_tweet.id))

            elif request.form.get("btn")=="Finish":
                  true_label  = request.form.get('tlabel')
                  tweet.True_label = true_label
                  db.session.commit()
                  return redirect(url_for('manual_1'))
      else:
            results = [tweet.Mean_label, tweet.FB_label, tweet.GS_label]
            return render_template('manual.html', label = results, id=id)


@app.route('/', methods=['GET','POST'])
def manual_1():
      if request.method == "POST":
            query = request.form.get('query')
            models = request.form.getlist('filter')
            lang = request.form.get('lang')

            if 'Mean' in models:
                  resmean = mean_esg(query, lang)
            else:
                  resmean = None 
            if "Bert" in models:
                  resbert = finbert_esg(query, lang)
            else:
                  resbert = None
            if "GS" in models:
                  resgs = gs_esg(query, lang)
            else: 
                  resgs = None
            new_tweet = Tweets(tweet=query, lang=lang, FB_label=resbert, Mean_label=resmean, GS_label=resgs)
            db.session.add(new_tweet)
            db.session.commit()
            return redirect(url_for('manual', id=new_tweet.id))
      else:
            return render_template('manual.html')


@app.route('/db')
def listOfPersons():
      reportTitle = "Tweets Database"
      sqlQuery = "SELECT id as 'id', tweet as 'Text', lang as'Language', True_label as 'True Label', FB_label as 'FinBERT', Mean_label as 'Mean Model', GS_label as 'GramSchmidt'   FROM Tweets"
      fontName = "Arial"
      headerRowBackgroundColor = '#ffeeee'
      evenRowsBackgroundColor = '#ffeeff'
      oddRowsBackgroundColor = '#ffffff'
      return Reporter.generateFromSql(db.session, reportTitle, sqlQuery, 
                                    "ltr", fontName, "Total Salary", True,
                                    headerRowBackgroundColor, evenRowsBackgroundColor, oddRowsBackgroundColor
                                    )


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=8080, debug=True, use_reloader=False)



# from scraping import scraper

# @app.route('/db')
# def database():
#       tweets = db.session.query(Tweets).all()
#       print(tweets)
#       return "Check the Terminal"

# global df
# df = pd.DataFrame()

# @app.route("/")
# def home():
#       return render_template('index.html')

# @app.route("/data")
# def visualize():
#       return render_template('visualize.html',
#                                 tables=[df.to_html(classes='data')], 
#                                 titles=df.columns.values)  

# sc = scraper()

# @app.route("/scraping", methods=['GET','POST'])
# def scrap():
#     if request.method == 'POST':
#       global df
#       l = request.form.getlist('scrap')
#       df = sc.week_s(text=l[0], size=int(l[1]), lang=l[2])
#       return redirect(url_for('filter'))
#     else:
#         return render_template('scraping.html', l = None) 


# @app.route("/filter", methods=['GET', 'POST'])
# def filter():
#     if request.method == 'POST':
#       l = request.form.getlist('filter')
#       return render_template('filter.html', l = request.form.getlist('filter'))
#     return render_template('filter.html', l =None)


