import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
import time
import os
import json

BASE_URL = "https://www.myplate.gov"
all_recipe_links = []

# There are 11 pages of recipes from MyPlate Kitchen with 100 recipes per page
for page_number in range(0, 11):
    URL = f"{BASE_URL}/myplate-kitchen/recipes?sort_bef_combine=title_ASC&items_per_page=100&page={page_number}"
    page = requests.get(URL)
    print(f"Fetching page {page_number}: {URL}")

    soup = BeautifulSoup(page.content, "html.parser")
    results = soup.find(class_="view-content")

    recipe_cards = results.find_all("div", class_="mp-recipe-teaser__title")

    recipe_links = [BASE_URL + recipe_card.find("a")["href"] for recipe_card in recipe_cards]
    all_recipe_links.extend(recipe_links)
    
print(f"Total number of recipes: {len(all_recipe_links)}")

# Save all recipe links to a text file
with open("data/myplate_recipe_links.txt", "w") as f:
    for link in all_recipe_links:
        f.write(link + "\n")

# Ensure the directory exists for saving individual JSON files
os.makedirs("data/individual_recipes", exist_ok=True)

## Scrape recipe details
# Load recipe links from text file
with open("data/myplate_recipe_links.txt", "r") as f:
    all_recipe_links = f.read().splitlines()

recipes = []
# Scrape recipe details
for recipe_link in all_recipe_links:
    page = requests.get(recipe_link)
    soup = BeautifulSoup(page.content, "html.parser")

    recipe_article = soup.find("article", class_="mp-recipe-full__article")

    # ======== TITLE, SERVINGS, DESCRIPTION, IMAGE ========
    title = recipe_article.find("h1", class_="mp-recipe-full__title").get_text().replace("\n", "")
    servings = recipe_article.find("div", class_= "mp-recipe-full__overview").find_all("span", class_="mp-recipe-full__detail--data")[0].get_text().strip().split()[0]
    description = recipe_article.find("div", class_="mp-recipe-full__description").get_text().strip()
    image_url = recipe_article.find("img", class_="image-style-recipe-525-x-350-")["src"]

    # ======== INGREDIENTS ========
    full_details = recipe_article.find("div", class_="mp-recipe-full__details") # include ingredients and instructions
    ingredients_html = full_details.find("div", class_="field--name-field-ingredients").find_all("li")

    ingredients = []
    for ingredient in ingredients_html:
        ingredients_info = ingredient.get_text().strip().split("\n")
        ingredients = [" ".join(item.strip() for item in ingredients_info if item.strip())]

    # ======== INSTRUCTIONS ========
    instructions_html = full_details.find("div", class_="field--name-field-instructions").find_all("li")
    instructions = []
    for instruction in instructions_html:
        instructions.append(instruction.get_text().strip())

    # ======== NUTRITION INFO ========

    # Because the nutrition info is hidden behind a "Show Full Display" button, we need to use Selenium to click the button
    driver = webdriver.Chrome()

    try:
        driver.get(recipe_link)
        time.sleep(3)

        # Click the "Show Full Display" radio button to expand the nutrition info
        expand_button = driver.find_element(By.CSS_SELECTOR, "label[for='panel-expand']")
        expand_button.click()

        time.sleep(2)

        # Locate the expanded nutrition table
        nutrition_rows = driver.find_elements(By.CSS_SELECTOR, ".panel.panel-expanded tbody tr")
        
        nutrition_info = []
        for row in nutrition_rows:
            cells = row.find_elements(By.TAG_NAME, "td")
            
            if len(cells) >= 2:
                nutrient_name = cells[0].text.strip()
                nutrient_value = cells[1].text.strip()
                if nutrient_name and nutrient_value:
                    nutrition_info.append(f"{nutrient_name}: {nutrient_value}")

    finally:
        # Close the browser
        driver.quit()
    
    recipe_data = {
        "title": title,
        "image_url": image_url,
        "servings": servings,
        "description": description,
        "ingredients": ingredients,
        "instructions": instructions,
        "nutrition_info": nutrition_info
    }
    
    # Create a safe filename based on the title (e.g., replace spaces with underscores)
    file_name = f"data/individual_recipes/{title.replace(' ', '_').replace('/', '_')}.json"
    
    # Write the recipe data to a JSON file
    with open(file_name, "w") as f:
        json.dump(recipe_data, f, indent=2)

    print(f"Recipe '{title}' saved as {file_name}")
    
print(f"Total number of recipes scraped: {len(recipes)}")
