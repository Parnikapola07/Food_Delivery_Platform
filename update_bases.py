import os
import glob

base_dir = r"c:\Users\Parnika\OneDrive\Desktop\Flask class\Food Delivery Platform\templates"

def replace_in_files(pattern, replacement):
    for filepath in glob.glob(pattern):
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Also handle potential trailing spaces
        new_content = content.replace("{% extends 'base.html' %}", f"{{% extends '{replacement}' %}}")
        new_content = new_content.replace('{% extends "base.html" %}', f"{{% extends '{replacement}' %}}")
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(new_content)

# User templates
replace_in_files(os.path.join(base_dir, "user", "*.html"), "base_user.html")

# Restaurant templates
replace_in_files(os.path.join(base_dir, "restaurant", "*.html"), "base_restaurant.html")

# Delivery templates
replace_in_files(os.path.join(base_dir, "delivery", "*.html"), "base_delivery.html")

# Auth templates
replace_in_files(os.path.join(base_dir, "auth", "*_user.html"), "base_user.html")
replace_in_files(os.path.join(base_dir, "auth", "*_restaurant.html"), "base_restaurant.html")
replace_in_files(os.path.join(base_dir, "auth", "*_delivery.html"), "base_delivery.html")

print("Templates updated.")
