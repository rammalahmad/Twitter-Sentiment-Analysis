from flask import Flask, render_template, request, redirect, url_for
import sys
from flask_sqlalchemy_report import Reporter
from pyrsistent import T 
from esg_topic import ESG_Topic



app=Flask(__name__,template_folder='templates')



@app.route('/', methods=['GET','POST'])
def manual_1():
      if request.method == "POST":
            tweets_name = request.form.get('tweets')
            model_number = int(request.form.get('model'))
            semi_sup = int(request.form.get('sem_sup'))
            lang = request.form.get('lang')
            dim = request.form.get('dim')
            cluster_model = int(request.form.get('cluster_model'))
            nb_clusters = request.form.get('nb_clusters')
            min_topic_size = request.form.get('min_topic_size')

            topicer = ESG_Topic(model_number=model_number,
                              semi_sup=semi_sup,
                              lang=lang,
                              cluster_model=cluster_model,
                              min_topic_size=min_topic_size,
                              nb_clusters=nb_clusters,
                              dim=dim)

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
            if ((resmean == None) & (resbert == None) & (resgs == None)):
                  return render_template('manual.html', step = "Measure", warning = True)
            new_tweet = Tweets(tweet_text=query, lang=lang, FB_label=resbert, Mean_label=resmean, GS_label=resgs)
            db.session.add(new_tweet)
            db.session.commit()
            results = [new_tweet.Mean_label, new_tweet.FB_label, new_tweet.GS_label]
            return render_template('manual.html', label = results, id= new_tweet.id, step = "Truth")
      else:
            return render_template('manual.html', step = "Measure", warning = None)



@app.route('/<int:id>', methods=['GET','POST'])
def manual(id):
      tweet = Tweets.query.get_or_404(id)
      if request.method == "POST":
            true_label  = request.form.get('tlabel')
            tweet.True_label = true_label
            db.session.commit()
            if true_label == "N":
               return redirect(url_for('thanks'))   
            return render_template('sentiment.html', id=id, step="Measure")
      else:
            results = [tweet.Mean_label, tweet.FB_label, tweet.GS_label]
            return render_template('manual.html', label = results, id=id, step = "Truth")



@app.route('/sentiment/<int:id>', methods=['GET','POST'])
def sentiment(id):
      tweet = Tweets.query.get_or_404(id)
      if request.method == "POST":
            if request.form.get("btn")=="Measure Sentiment":
                  text = tweet.tweet_text
                  models = request.form.getlist('filter')
                  if 'RoBERTa' in models:
                        resro = rob_score(text)
                  else:
                        resro = None 
                  if "BertBase" in models:
                        rescase = uncased_score(text)
                  else:
                        rescase = None
                  if ((resro == None) & (rescase == None)):
                      return render_template('sentiment.html', id=id, step="Measure", warning=True)
                  result = [resro, rescase]
                  tweet.RoBERTa_sent = resro
                  tweet.BERT_uncased_sent = rescase
                  db.session.commit()
                  return render_template('sentiment.html', id=id, step="Truth", scores= result)
            elif request.form.get("btn")=="Finish":
                  true_sent  = request.form.get('tsent')
                  tweet.True_sent = true_sent
                  db.session.commit()
                  return redirect(url_for('thanks'))
      else:
            return render_template('sentiment.html', id=id, step="Measure", warning=None)


@app.route('/thanks', methods=['GET','POST'])
def thanks():
      if request.method == "POST":
            return redirect(url_for('manual_1'))
      else:
            return render_template('thanks.html')


@app.route('/db')
def listOfPersons():
      reportTitle = "Tweets Database"
      sqlQuery = "SELECT id as 'id', tweet_text as 'Text', lang as'Language', True_label as 'True Label',\
       FB_label as 'FinBERT', Mean_label as 'Mean Model', GS_label as 'GramSchmidt', True_sent as 'True Sentiment',\
      RoBERTa_sent as 'RoBERTa score', BERT_uncased_sent as 'BERT Base score' FROM Tweets"
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


