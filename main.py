from fastapi import FastAPI, HTTPException
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine, Column, Integer, String, Date
from selenium import webdriver
from sqlalchemy import text
from selenium.webdriver.common.by import By
import time
import re
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

app = FastAPI()

# Database Setup
Base = declarative_base()

class Car(Base):
    __tablename__ = "cars"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    price = Column(Integer)
    sold_date = Column(Date)

DATABASE_URL = "postgresql://postgres:root@localhost:5432/cars_db"
engine = create_engine(DATABASE_URL)
Base.metadata.create_all(bind=engine)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# System Health Check
@app.get("/")
def system_check():
    try:
        db = SessionLocal()
        print(db.execute(text("SELECT * from cars")).fetchall())
        db.close()
        return {"status": "ok", "message": "System is up and running successfully."}
    except Exception as e:
        return {"status": "error", "message": str(e)}

# Placeholder Scraping Function
def scrape_webpage():
    return "Scraping in progress..."

# Scraping API Endpoint
@app.get("/scrape")
def scrape():
    URL = "https://philkotse.com/used-cars-for-sale"
    try:
        driver = webdriver.Chrome()
        driver.get(URL)

        url = "https://philkotse.com/used-cars-for-sale"
        driver.get(url)

        wait = WebDriverWait(driver, 10)
        
        # Keep clicking "Load More" until it disappears
        while True:
            try:
                load_more_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Load More')]")))
                ActionChains(driver).move_to_element(load_more_button).click().perform()
                time.sleep(3)  # Allow time for more data to load
            except:
                print("No more 'Load More' button found. All data loaded.")
                break

        time.sleep(5)  # Final wait to ensure all content is loaded

        cars = []  # ✅ Ensure list starts fresh

        # Extract Titles and Prices
        car_titles = driver.find_elements(By.XPATH, "//div[@class='info']/h3[@class='title']/a")
        car_prices = driver.find_elements(By.XPATH, "//div[@class='price-repossessed']/div[@class='price']")

        for title_elem, price_elem in zip(car_titles, car_prices):
            title = title_elem.text.strip()
            price_text = price_elem.text.strip()

            # Extract numeric price (remove "₱" and ",")
            price = int(re.sub(r"[^\d]", "", price_text)) if price_text else 0

            cars.append({"title": title, "price": price})
        print(cars,end="\n") 
        driver.quit()  # Close browser

        # ✅ Store fresh data only
        # store_in_db(cars)

        return {"message": f"Scraped {len(cars)} cars successfully!"}
    except Exception as e:
        return {"message": str(e)}
    finally:
        driver.quit()

# Store data in PostgreSQL
def store_in_db(cars):
    db: Session = SessionLocal()
    for car in cars:
        db_car = Car(title=car["title"], price=car["price"])
        db.add(db_car)
    
    # db.commit()
    db.close()

    return {"message": "Scraping in progress..."}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 