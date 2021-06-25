#Code by AkinoAlice@Tyrant_Rex

import aiohttp,asyncio,requests,shutil,time,re,os
from feature_extractor import FeatureExtractor
from bs4 import BeautifulSoup
from PIL import ImageFile
from pathlib import Path
from PIL import Image
import numpy as np

def pre_code():
    html = requests.get("https://nhentai.net/")
    soup = BeautifulSoup(html.text, "lxml")
    page = soup.find_all(href=re.compile("/g/"))[5]
    code = page.get("href")
    code = code.replace("g", "")
    code = code.replace("/", "")
    return str(code)

def download(code):
    async def main(): 
        async with aiohttp.ClientSession() as session:
            async with session.get(f"https://nhentai.net/g/{code}/") as response:
                html = await response.text()
                soup = BeautifulSoup(html, "lxml")
                page = soup.find_all(src=re.compile("https://t.nhentai.net/galleries/"))
                trush = soup.find_all(src=re.compile("/thumb")) + soup.find_all(src=re.compile("/cover"))

                image_trush = [result.get("src") for result in trush]
                image = [result.get("src") for result in page]

                while len(image_trush) != 0:
                    image.remove(image_trush[0])
                    image_trush.remove(image_trush[0])

        async with aiohttp.ClientSession() as session:
            tasks = [asyncio.create_task(fetch(link, session)) for link in image]
            await asyncio.gather(*tasks)

    async def fetch(link, session):
        async with session.get(link) as resp:
            while resp.status != 200:
                async with session.get(link) as resp:
                    if resp.status == 200:
                        break
            if not os.path.exists(Path(f"./swap/{code}/")):
                os.makedirs(Path(f"./swap/{code}/"))

            link = link.replace("/","-")
            file_name = str(Path(f"./swap/{code}/" + "/" + f"{link}"))
            file_name = file_name.replace("https:--t.nhentai.net-galleries-","")
            file_name = file_name.replace("t", "")
            file_name = file_name.replace(".png", ".jpg")

            with open(file_name, "wb") as f:
                while True:
                    chunk = await resp.content.read()
                    if not chunk:
                        break
                    f.write(chunk)

    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())

def extraction(code):
        fe= FeatureExtractor()

        for img_path in sorted(Path(f"./swap/{code}/").glob("*.jpg")):
            feature = fe.extract(img=Image.open(img_path))

            path = img_path.stem.replace("-", "/")
            feature_path = Path(f"./static/feature/{code}") / (img_path.stem + ".npy")

            if not os.path.exists(Path(f"./static/feature/{code}")):
                os.makedirs(Path(f"./static/feature/{code}"))
                
            np.save(feature_path, feature)

        shutil.rmtree(Path(f"./swap/{code}/"), ignore_errors=True)

if __name__ == "__main__":
    shutil.rmtree(Path(f"./swap/"), ignore_errors=True)
    code = pre_code()

    shutil.rmtree(Path(f"./static/feature/{code}/"), ignore_errors=True)

    while True:
        if not os.path.exists(Path("./static/feature/")):
                os.makedirs(Path("./static/feature/"))

        if code == 1:
            code = pre_code()

        elif not os.path.exists(Path(f"./static/feature/{code}/")):
            os.makedirs(Path(f"./static/feature/{code}/"))
            start_time = time.time()
            download(code)
            extraction(code)

            print("==================================================")
            print(f"Code:{code}","|","Time:",str(time.time() - start_time))
            print("==================================================")
            code = int(code) - 1

        else:
            while os.path.exists(Path(f"./static/feature/{code}/")):
                exists_code = int(code)
                code = int(code) - 1

            shutil.rmtree(Path(f"./static/feature/{exists_code}/"), ignore_errors=True)

            print("==================================================")
            print(f"Code:{exists_code} <==Removed")
            print("==================================================")

            start_time = time.time()
            download(exists_code)
            extraction(exists_code)

            print("==================================================")
            print(f"Code:{exists_code}","|","Time:",str(time.time() - start_time)),"|",f"Exists:{exists_code}"
            print("==================================================")