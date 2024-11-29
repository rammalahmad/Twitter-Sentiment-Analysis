from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime


app=Flask(__name__,template_folder='templates')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///tweets.db'

#Initialize the database
db = SQLAlchemy(app)

#Create db model
class Tweets(db.Model):
      id = db.Column(db.Integer, primary_key= True)
      tweet_text = db.Column(db.String(1000),nullable=False)
      lang = db.Column(db.String(10),nullable=False)
      True_label = db.Column(db.String(10),nullable=True)
      FB_label = db.Column(db.String(10),nullable=True)
      Mean_label = db.Column(db.String(10),nullable=True)
      GS_label = db.Column(db.String(10),nullable=True)
      True_sent = db.Column(db.Integer,nullable=True)
      RoBERTa_sent = db.Column(db.Float,nullable=True)
      BERT_uncased_sent = db.Column(db.Float,nullable=True)
      date_created = db.Column(db.DateTime, default= datetime.utcnow)

      #Create a function to return a string when we add something
      def __repr__(self):
            return '<tweet %r>' % self.id