from fastapi import FastAPI

app = FastAPI()

URL = "https://philkotse.com/used-cars-for-sale"


@app.get("/")
def system_check():
    return {"status": "ok"}

def scrape_Webpage():
    return "Scraping"

@app.get("/scrape")
def scrape():
    print(scrape_Webpage)