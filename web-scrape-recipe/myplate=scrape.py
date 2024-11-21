import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
import time
import os
import json

BASE_URL = "https://www.myplate.gov"
all_recipe_links = []

def save_recipe_links_to_file(recipe_links, file_name):
    """Save a list of recipe links to a text file."""
    with open(file_name, "w") as f:
        for link in recipe_links:
            f.write(link + "\n")
            
def get_recipe_links(URL):
    """Get all recipe links from a given URL."""
    
    all_recipe_links = []
    page_number = 0
    
    while True:
        page = requests.get(URL + str(page_number))
        print(f"Fetching page {page_number}: {URL}")

        soup = BeautifulSoup(page.content, "html.parser")
        results = soup.find(class_="view-content")

        if results is None:
            break
        recipe_cards = results.find_all("div", class_="mp-recipe-teaser__title")

        recipe_links = [BASE_URL + recipe_card.find("a")["href"] for recipe_card in recipe_cards]
        all_recipe_links.extend(recipe_links)
        page_number += 1
    print(f"Total number of recipes: {len(all_recipe_links)}")
    return all_recipe_links

def scrape_all_recipes_links():
    """
    Scrape all recipe links from the MyPlate Kitchen website.
    """
    print("Scraping all recipe links...")
    URL = f"{BASE_URL}/myplate-kitchen/recipes?sort_bef_combine=title_ASC&items_per_page=100&page="
    all_recipe_links = get_recipe_links(URL)
    # Save all recipe links to a text file
    save_recipe_links_to_file(all_recipe_links, "data/myplate_recipe_links.txt")
    
def scrape_all_recipes_by_course():
    """
    Scrape all recipe by courses from the MyPlate Kitchen website.
    """
    courses = {
        "Appertizers": "3A116",
        "Beverages": "3A117",
        "Breads": "3A118",
        "Breakfast": "3A119",
        "Desserts": "3A120",
        "Main Dishes": "3A121",
        "Salads": "3A122",
        "Sabdwiches": "3A123",
        "Sauces, Condiments and Seasonings": "3A124",
        "Side Dishes": "3A125",
        "Snacks": "3A126",
        "Soups and Stews": "3A127"
    }
    for course, course_id in courses.items():
        URL = f"{BASE_URL}/myplate-kitchen/recipes?f[0]=course%{course_id}&page="
        all_recipe_links = get_recipe_links(URL)
        # Save all recipe links to a text file
        save_recipe_links_to_file(all_recipe_links, f"data/courses/myplate_recipe_links_{course}.txt")
        
def scrape_all_recipes_by_food_groups():
    os.makedirs("data/food_groups", exist_ok=True)
    food_groups = {
        "Fruits": "3A88",
        "Vegetables": "3A91",
        "Grains": "3A97",
        "Protein Foods": "3A100",
        "Dairy": "3A108",
    }
    
    for food_group, food_group_id in food_groups.items():
        URL = f"{BASE_URL}/myplate-kitchen/recipes?f[0]=food_groups%{food_group_id}&page="
        all_recipe_links = get_recipe_links(URL)
        # Save all recipe links to a text file
        save_recipe_links_to_file(all_recipe_links, f"data/food_groups/myplate_recipe_links_{food_group}.txt")


# =================== SCRAPE RECIPES LINKS ===================
scrape_all_recipes_links()
scrape_all_recipes_by_course()
scrape_all_recipes_by_food_groups()
## =================== SCRAPE RECIPES DETAILS ===================

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
        ingredients.append(" ".join(item.strip() for item in ingredients_info if item.strip()))

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
