from flask import Flask, render_template, request, redirect, url_for, session
from flask_session import Session
import pandas as pd
import sys

path = r'C:\Users\User\Desktop\Ahmad\Stages\SurfMetrics\Git\Flask\esg_topic'

sys.path.append(path+'/my_model')

from esg_topic import ESG_Topic

app=Flask(__name__,template_folder='templates') 
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)


@app.route('/', methods=['GET','POST'])
def parameters():
      session['topicer'] = None
      if request.method == "POST":
            model_number = int(request.form.get('model'))
            semi_sup = int(request.form.get('sem_sup'))
            lang = request.form.get('lang')
            dim = int(request.form.get('dim'))
            cluster_model = int(request.form.get('cluster_model'))
            # nr_topics = int(request.form.get('nb_clusters'))
            min_topic_size = int(request.form.get('min_topic_size'))
            do_mmr = int(request.form.get('do_mmr'))

            topicer = ESG_Topic(model_number=model_number,
                              semi_sup=semi_sup,
                              lang=lang,
                              cluster_model=cluster_model,
                              min_topic_size=min_topic_size,
                              dim=dim,
                              do_mmr=do_mmr)
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
      # global keywords
      # df = pd.read_csv('tesla_topics.csv')
      #keywords = keywords

      df = topicer.df
      keywords = topicer.get_topics()
      grouped = df.groupby('Topic')
      result=[]
      for topic, cluster in grouped:
            keyword = [e[0] for e in keywords[topic]]
            hashtags = topicer._extract_hashtags(cluster)
            result += [(len(cluster), [cluster[['Document']].to_html(classes='data', header="true")], keyword, hashtags)]
      return render_template('visualize.html', result=result)


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=8080, debug=True, use_reloader=False)