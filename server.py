#Code by Aki.no.Alice@Tyrant_Rex

from flask import Flask,request,render_template
from feature_extractor import FeatureExtractor
import os,shutil,sqlite3,pickle,time
from datetime import datetime
from pathlib import Path
from PIL import Image
import numpy as np
import time

app = Flask(__name__,static_folder="/")

fe = FeatureExtractor()

def locate(query):
    global score
    conn = sqlite3.connect("img_data.db" , isolation_level=None)
    cursor = conn.cursor()
    count = cursor.execute("select rowid from nhentai order by rowid desc").fetchone()[0]
    step = 5000
    print("load done")
    for i in range(0,count,step):
        scores = []
        rng = i + step
        feature = []
        cursor.execute(f"select feature from nhentai where rowid >= {i} and rowid < {rng}")
        data_fe = np.array(cursor.fetchall())
        cursor.execute(f"select code,path from nhentai where rowid >= {i} and rowid < {rng}")
        data_code_path = cursor.fetchall()

        for item in data_fe:
            feature.append(pickle.loads(item))
        dists = np.linalg.norm(feature - query,axis=1)
        ids = np.argsort(dists)[:5]
        sc = [(dists[id],data_code_path[id]) for id in ids]
        for x in sc:
            scores.append(x)
        score = sorted(scores,key = lambda scores: scores[0])

        if len(score) > 20:
            score = score[:20]

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        file = request.files["query_img"]

        
        img = Image.open(file.stream)
        if len(os.listdir("./static/uploaded")) >= 100:
            shutil.rmtree(Path("./static/uploaded"))
            os.makedirs(Path("./static/uploaded"))
            
        uploaded_img_path = "static/uploaded/" + datetime.now().isoformat().replace(":", ".") + "_" + file.filename
        img.save(uploaded_img_path)

        query = fe.extract(img)
        start = time.time()
        locate(query)
        end = time.time() - start
        print("Found")

        return render_template("index.html",query_path=uploaded_img_path,scores=score,end=end)

    else:
        return render_template("index.html",end=0)

if __name__=="__main__":
    app.run("0.0.0.0", debug=True)
