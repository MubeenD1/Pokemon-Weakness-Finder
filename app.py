from flask import Flask, render_template, request, flash
from dotenv import load_dotenv
import os
import requests

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('KEY')

@app.route("/")
def home():
    flash("To get started, enter the name of a pokemon below!")
    return render_template("index.html")

@app.route("/name", methods=["POST","GET"])
def name():
    pokename = str(request.form['pokemon_name'])
    apiURL = f"https://pokeapi.co/api/v2/pokemon/{pokename.lower()}/"

    response = requests.get(apiURL)
    data = response.json()

    types = []
    sprite = data['sprites']['front_default']

    for type_info in data['types']:
        type_name = type_info['type']['name']
        types.append(type_name)

    flash("Your chosen Pokemon is: " + "<h1>" + pokename + "</h1>")
    flash(f"<img src='{sprite}' style='width:200px; height:200px;'>")
    
    if (len(types) == 1):
        flash("Their type is: " + ', '.join(types) + "<br><br>")
    else:
        flash("Their types are: " + ', '.join(types)+ "<br><br>")

    weaknesses = calculate_pokemon_weaknesses(types)

    flash(f"Here is a list of the types that {pokename} is weak to:" + "<br>")
    for weakness in weaknesses:
            flash("<b>" + weakness + "</b>")

    return render_template("name.html")

def get_type_effectiveness(type_name):
    url = f"https://pokeapi.co/api/v2/type/{type_name}/"
    response = requests.get(url)
    data = response.json()
    
    effectiveness = {}
    for damage_relation, multiplier in [
        ("double_damage_from", 2),
        ("half_damage_from", 0.5),
        ("no_damage_from", 0)
    ]:
        for type_info in data['damage_relations'][damage_relation]:
            effectiveness[type_info['name']] = effectiveness.get(type_info['name'], 1) * multiplier
    return effectiveness

def calculate_pokemon_weaknesses(pokemon_types):
    combined_effectiveness = {}
    
    for poke_type in pokemon_types:
        type_effectiveness = get_type_effectiveness(poke_type)
        for effectiveness_type, multiplier in type_effectiveness.items():
            if effectiveness_type in combined_effectiveness:
                combined_effectiveness[effectiveness_type] *= multiplier
            else:
                combined_effectiveness[effectiveness_type] = multiplier
    
    weaknesses = [type_name for type_name, effectiveness in combined_effectiveness.items() if effectiveness > 1]
    return weaknesses


if __name__ == "__main__":
    app.run(debug=True)