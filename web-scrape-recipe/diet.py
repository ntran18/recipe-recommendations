# Utility function to read and return the contents of a file as a list
def read_ingredients(file_path):
    with open(file_path, "r") as f:
        return [ingredient.strip().lower() for ingredient in f.read().splitlines()]

# Load all ingredients from their respective files
seafood = read_ingredients("data/seafoods.txt")
red_meat = read_ingredients("data/red_meats.txt")
egg_products = read_ingredients("data/egg.txt")
dairy_products = read_ingredients("data/dairy.txt")
gluten_products = read_ingredients("data/gluten.txt")
nuts = read_ingredients("data/nut.txt")

# General function to check if any ingredient from the list appears in the recipe ingredients
def contains_ingredient(ingredients, ingredient_list):
    return any(ingredient in ingredients for ingredient in ingredient_list)

# Check functions
def is_gluten_free(ingredients):
    return not contains_ingredient([ingredient.lower() for ingredient in ingredients], gluten_products)

def is_vegetarian(ingredients):
    # Vegetarian: No seafood or red meat
    return not contains_ingredient([ingredient.lower() for ingredient in ingredients], seafood + red_meat)

def is_vegan(ingredients):
    # Vegan: No animal products (seafood, red meat, eggs, dairy)
    return not contains_ingredient([ingredient.lower() for ingredient in ingredients], seafood + red_meat + egg_products + dairy_products)

def is_pescetarian(ingredients):
    # Pescetarian: No red meat or dairy, but seafood is allowed
    return not contains_ingredient([ingredient.lower() for ingredient in ingredients], red_meat + dairy_products)

def is_dairy_free(ingredients):
    return not contains_ingredient([ingredient.lower() for ingredient in ingredients], dairy_products)

def is_seafood_free(ingredients):
    return not contains_ingredient([ingredient.lower() for ingredient in ingredients], seafood)

def is_nut_free(ingredients):
    return not contains_ingredient([ingredient.lower() for ingredient in ingredients], nuts)