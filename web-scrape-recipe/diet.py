
with open("data/meats.txt", "r") as f:
    meats = f.read().splitlines()
    
with open("data/egg.txt", "r") as f:
    egg_products = f.read().splitlines()

with open("data/dairy.txt", "r") as f:
    dairy_products = f.read().splitlines()
    
with open("data/gluten.txt", "r") as f:
    gluten_products = f.read().splitlines()

def is_gluten_free(ingredients) -> bool:
    for ingredient in ingredients:
        for gluten_ingredient in gluten_products:
            if gluten_ingredient.lower() in ingredient.lower():
                return False
    return True

def is_vegetarian(ingredients) -> bool:
    """ No ingredients may contain meat or meat by-products, such as bones or gelatin. """
    for ingredient in ingredients:
        for non_vegetarian_ingredient in meats:
            if non_vegetarian_ingredient.lower().strip() in ingredient.lower():
                return False
    return True

def is_vegan(ingredients) -> bool:
    """ 
        No ingredients may contain meat or meat by-products, such as bones or gelatin, nor may they contain eggs, dairy, or honey.
    """
    non_vegan_ingredients = meats + egg_products + dairy_products
    for ingredient in ingredients:
        for non_vegan_ingredient in non_vegan_ingredients:
            if non_vegan_ingredient.lower() in ingredient.lower():
                return False
    return True

def is_lacto_vegetarian(ingredients) -> bool:
    """
        No ingredients may contain meat or meat by-products, such as bones or gelatin, nor may they contain eggs.
        Dairy is allowed.
    """
    non_lacto_vegetarian_ingredients = meats + egg_products
    for ingredient in ingredients:
        for non_lacto_vegetarian_ingredient in non_lacto_vegetarian_ingredients:
            if non_lacto_vegetarian_ingredient.lower() in ingredient.lower():
                return False
    return True

def is_ovo_vegetarian(ingredients) -> bool:
    """
        No ingredients may contain meat or meat by-products, such as bones or gelatin, nor may they contain dairy or honey.
        Eggs are allowed.
    """
    non_ovo_vegetarian_ingredients = meats + dairy_products
    for ingredient in ingredients:
        for non_ovo_vegetarian_ingredient in non_ovo_vegetarian_ingredients:
            if non_ovo_vegetarian_ingredient.lower() in ingredient.lower():
                return False
    return True

def is_keto(nutrition_info):
    """
    Determines if a recipe fits the Ketogenic (Keto) diet based on its macronutrient breakdown.
    Fat: 55-80% of the total calories should come from fat.
    Protein: 15-35% of the total calories should come from protein.
    Carbohydrates: Less than 10% of the total calories should come from carbohydrates.
    
    This formula are based on Spoonacular diet analysis guidelines.
    
    Parameters:
    - nutrition_info (dict): A dictionary containing the nutritional information with keys:
        - 'fat': Fat in grams
        - 'protein': Protein in grams
        - 'carbs': Carbohydrates in grams
        - 'calories': Total calories (optional, but can be calculated from macronutrients if not provided)
    
    Returns:
    - bool: True if the recipe is keto-friendly, False otherwise
    """
    # Macronutrient caloric values
    CALORIES_PER_GRAM_FAT = 9
    CALORIES_PER_GRAM_PROTEIN = 4
    CALORIES_PER_GRAM_CARBS = 4

    calories = int(nutrition_info['Total Calories'])
    
    fat_calories = CALORIES_PER_GRAM_FAT * int(nutrition_info["Total Fat"].split(" ")[0])
    protein_calories = CALORIES_PER_GRAM_PROTEIN * int(nutrition_info["Protein"].split(" ")[0])
    carb_calories = CALORIES_PER_GRAM_CARBS * int(nutrition_info["Carbohydrates"].split(" ")[0])
    
    fat_percent = fat_calories / calories * 100
    protein_percent = protein_calories / calories * 100
    carb_percent = carb_calories / calories * 100
    
    return (fat_percent > 54 and fat_percent < 81) and (protein_percent > 14 and protein_percent < 36) and carb_percent < 10


