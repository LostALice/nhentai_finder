#test

from pathlib import Path
import sqlite3,os,time
import numpy as np

conn = sqlite3.connect("img_data.db" , isolation_level=None)
cursor = conn.cursor()

try:
    cursor.execute("CREATE TABLE nhentai (feature BLOB,code INT,path NVARCHAR(20))")
except:
    pass

def to_db(code):
    start = time.time()
    i = 0
    for feature_path in Path(f"./static/feature/{code}").glob("*.npy"):
        i += 1
        try:
            x = np.ndarray.dumps(np.load(feature_path))
        except:
            f = open("error.txt", "a+")
            f.write(f"{code} | {feature_path}")
            f.close()

        codepath = feature_path.stem.replace("-", "/")
        cursor.execute(f"insert into nhentai (feature,code,path) values (?,{code},'{codepath}')",(x,))
    end = str(round(time.time() - start, 5))
    conn.commit()
    print(f"Finish:{code} | Time:{end} | Page(s):{i}")

def check_(code):
    foo = cursor.execute(f"select code from nhentai where code={code} ").fetchall()
    if len(foo) ==0:
        to_db(code)
    else:
        print(f"Exist:{code}")
    conn.commit()

if __name__ == "__main__":
    for code in os.listdir(Path("./static/feature")):
        check_(code)


conn.close()


