from flask import Flask, render_template, request, redirect, url_for, session
from flask_session import Session
import pandas as pd
import sys

path = r'C:\Users\User\Desktop\Ahmad\Stages\SurfMetrics\Git\Flask\esg_topic'

sys.path.append(path+'/my_model')

from esg_topic import ESG_Topic
from _scraper import Scraper

app=Flask(__name__,template_folder='templates') 
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)


@app.route("/scraping", methods=['GET','POST'])
def scraper():
    if request.method == 'POST':
      query = request.form.get('query')
      size = int(request.form.get('size'))
      lang = request.form.get('lang')
      sdate = request.form.get('sdate').replace("-", "") + "0000"
      edate = request.form.get('edate').replace("-", "") + "0000"

      scraper = Scraper(query=query,
                        size=size,
                        lang=lang,
                        sdate=sdate,
                        edate=edate)

      df = scraper.df
      return redirect(url_for('parameters'))
    else:
        return render_template('scraping.html')


@app.route('/', methods=['GET','POST'])
def parameters():
      session['topicer'] = None
      if request.method == "POST":
            embed_model = int(request.form.get('embed_model'))
            dim = int(request.form.get('dim'))
            cluster_model = int(request.form.get('cluster_model'))
            esg_model = int(request.form.get('esg_model'))
            keywords_model = int(request.form.get('keywords_model'))
            sent_model = int(request.form.get('sent_model'))
            min_topic_size = int(request.form.get('min_topic_size'))
            use_umap = int(request.form.get('use_umap'))
      
            topicer = ESG_Topic(embed_model = embed_model,
                              esg_model = esg_model,
                              cluster_model = cluster_model, 
                              keywords_model = keywords_model,
                              sent_model = sent_model,
                              use_umap = use_umap,
                              dim = dim, 
                              min_topic_size = min_topic_size)
            session['topicer'] = topicer
            return redirect(url_for('dataframe'))
      else:
            return render_template('parameters.html', step = "Generate")


@app.route('/dataframe', methods=['GET','POST'])
def dataframe():

      try:
            topicer = session['topicer']

      except Exception:
            return render_template('parameters.html', step = "Generate")

      if request.method == "POST":

            df_name = request.form.get('df')
            if df_name == "tesla":
                  df = pd.read_csv(path+"/Data/"+"tesla.csv")
                  topicer.fit_transform(df.tweet, df_name)
            elif df_name == "air":
                  df = pd.read_csv(path+"/Data/"+"air_liquide.csv")
                  print(len(df))
                  topicer.fit_transform(df.tweet, df_name)
            elif df_name == "fnsea":
                  df = pd.read_csv(path+"/Data/"+"fnsea.csv")
                  topicer.fit_transform(df.tweet, df_name)
            elif df_name == "amaen":
                  df = pd.read_csv(path+"/Data/"+"amazon_en.csv")
                  topicer.fit_transform(df.tweet, df_name)
            elif df_name == "amafr":
                  df = pd.read_csv(path+"/Data/"+"amazon_fr.csv")
                  topicer.fit_transform(df.tweet, df_name)
            topicer.df.to_csv("testing.csv")
            session['topicer'] = topicer
            return redirect('visualize')
      else:
            return render_template('parameters.html', step = "Test")


@app.route('/visualize')
def visualize():
      try:
            topicer = session['topicer']
      except Exception:
            return render_template('parameters.html', step = "Generate")


      df = topicer.df
      keywords = topicer.get_topics()
      grouped = df.groupby('Topic')
      result=[]
      for topic, cluster in grouped:
            keyword = [e[0] for e in keywords[topic]]
            hashtags = topicer.topics_hashtags[topic]
            sentiment = topicer.topics_sentiment[topic]
            result += [(len(cluster), [cluster[['Document', 'ESG_class']].to_html(classes='data', header="true")], keyword, hashtags, sentiment)]
      return render_template('visualize.html', result=result)


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=8080, debug=True, use_reloader=False)