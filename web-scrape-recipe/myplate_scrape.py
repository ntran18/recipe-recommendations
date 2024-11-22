import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
import time
import os
import json

from diet import *

BASE_URL = "https://www.myplate.gov"
all_recipe_links = []

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

food_groups = {
    "Fruits": "3A88",
    "Vegetables": "3A91",
    "Grains": "3A97",
    "Protein Foods": "3A100",
    "Dairy": "3A108",
}

cuisines = {
    "American": "3A132",
    "American_Indian&Alaska_Native": "3A137",
    "Asian&Pacific_Islander": "3A133",
    "Carribean_(Haitian,_Jamaican)": "3A1193",
    "Latin_American&Hispanic": "3A134",
    "Mediterranean": "3A135",
    "Middle_Eastern": "3A136",
    "Southern": "3A138",
    "Vegetarian": "3A139",
}

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

def scrape_all_recipes_by_category(category_name, category_dict, folder_name):
    """
    Scrapes all recipe links by a given category (courses, food groups, cuisines)
    
    Parameters:
    - category_name (str): The name of the category (e.g., 'courses', 'food_groups', 'cuisines').
    - category_dict (dict): A dictionary where keys are category names (e.g., 'Appetizers', 'Breakfast') and values are category IDs.
    - folder_name (str): The name of the folder to save the recipe links (e.g., 'courses', 'food_groups', 'cuisines').
    """
    os.makedirs(f"data/{folder_name}", exist_ok=True)

    for category, category_id in category_dict.items():
        URL = f"{BASE_URL}/myplate-kitchen/recipes?f[0]={category_name}%{category_id}&page="
        all_recipe_links = get_recipe_links(URL)
        save_recipe_links_to_file(all_recipe_links, f"data/{folder_name}/{category}.txt")
        print(f"Scraped {len(all_recipe_links)} links for {category}.")

def scrape_all_recipes_by_course():
    """
    Scrape all recipe by courses from the MyPlate Kitchen website.
    """
    scrape_all_recipes_by_category("course", courses, "courses")
        
def scrape_all_recipes_by_food_groups():
    """
    Scrape all recipe by food groups from the MyPlate Kitchen website.
    """
    scrape_all_recipes_by_category("food_groups", food_groups, "food_groups")

def scrape_all_recipes_by_cuisines():
    """
    Scrape all recipe by cuisines from the MyPlate Kitchen website.
    """
    scrape_all_recipes_by_category("cuisine", cuisines, "cuisines")

# =================== SCRAPE RECIPES LINKS ===================
# scrape_all_recipes_links()
# scrape_all_recipes_by_course()
# scrape_all_recipes_by_food_groups()
# scrape_all_recipes_by_cuisines()
# =================== SCRAPE RECIPES DETAILS ===================

# Ensure the directory exists for saving individual JSON files
os.makedirs("data/meet_requirements_recipes", exist_ok=True)
os.makedirs("data/other_recipes", exist_ok=True)
## Scrape recipe details
# Load recipe links from text file
with open("data/myplate_recipe_links.txt", "r") as f:
    all_recipe_links = f.read().splitlines()

all_recipe_links = all_recipe_links[99:]

recipes_by_categories = {}
for category in ["courses", "food_groups", "cuisines"]:
    recipes_by_categories[category] = {}
    for file_name in os.listdir(f"data/{category}"):
        with open(f"data/{category}/{file_name}", "r") as f:
            recipes_by_categories[category][file_name.replace(".txt", "")] = set(f.read().splitlines())
            

# Scrape recipe details
for recipe_link in all_recipe_links:
    page = requests.get(recipe_link, timeout=10)
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
        
        nutrition_info = {}
        for row in nutrition_rows:
            cells = row.find_elements(By.TAG_NAME, "td")
            
            if len(cells) >= 2:
                nutrient_name = cells[0].text.strip()
                nutrient_value = cells[1].text.strip()
                if nutrient_name and nutrient_value:
                    nutrition_info[nutrient_name] = nutrient_value

    finally:
        # Close the browser
        driver.quit()

    if nutrition_info == {}:
        print(f"Could not scrape nutrition info for {title}. Skipping...")
        continue
    # ======== CATEGORIES ========
    recipe_categories = {}
    
    for category, categories_groups in recipes_by_categories.items():
        for key, value in categories_groups.items():
            if recipe_link in value:
                if category in recipe_categories:
                    recipe_categories[category].append(key)
                else:
                    recipe_categories[category] = [key]
    
    # ======== DIETS ========
    
    # Check if the recipe is gluten-free
    diets_dict = {}
    diets_dict["gluten_free"] = is_gluten_free(ingredients)
    diets_dict["vegetarian"] = is_vegetarian(ingredients)
    diets_dict["vegan"] = is_vegan(ingredients)
    diets_dict["pescetarian"] = is_pescetarian(ingredients)
    diets_dict["dairy_free"] = is_dairy_free(ingredients)
    diets_dict["seafood_free"] = is_seafood_free(ingredients)
    diets_dict["nut_free"] = is_nut_free(ingredients)
    
    diets = [diet for diet, is_diet in diets_dict.items() if is_diet]
    # ======== SAVE RECIPE DATA TO JSON FILE ========
    recipe_data = {
        "title": title,
        "recipe_url": recipe_link,
        "image_url": image_url,
        "servings": servings,
        "description": description,
        "ingredients": ingredients,
        "instructions": instructions,
        "nutrition_info": nutrition_info,
        "courses": recipe_categories.get("courses", []),
        "food_groups": recipe_categories.get("food_groups", []),
        "cuisines": recipe_categories.get("cuisines", []),
        "diets": diets
    }
    
    # at least 5 gram of fiber and at most 5 g of saturated fat
    if int(nutrition_info["Dietary Fiber"].split(" ")[0]) < 5 or int(nutrition_info["Saturated Fat"].split(" ")[0]) > 5:
        file_name = f"data/other_recipes/{title.replace(' ', '_').replace('/', '_')}.json"
    else :
        file_name = f"data/meet_requirements_recipes/{title.replace(' ', '_').replace('/', '_')}.json"

    # Write the recipe data to a JSON file
    with open(file_name, "w") as f:
        json.dump(recipe_data, f, indent=2)

    print(f"Recipe '{title}' saved as {file_name}")
