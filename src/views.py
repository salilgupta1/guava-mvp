from flask import render_template, session, request, redirect, url_for
from models.recipe_set import RecipeSet
from models.recipe import Recipe
from models.user_ingredients import UserIngredients
from src import app, db

@app.route('/')
def home():
	if 'name' in session:
		return redirect(url_for('ingredients', username=session['name']))
	return render_template('index.html')

@app.route('/login', methods=['POST'])
def login():
	session['name'] = request.form['name']
	return redirect(url_for('ingredients', username=session['name']))

@app.route('/recipe-sets')
def recipe_sets():
	rs = RecipeSet()
	return render_template('recipe-sets.html', recipe_sets=rs.sets)

@app.route('/set/id/<int:set_id>')
def set(set_id):
	recipes = Recipe()
	return render_template('set.html', set=recipes.recipes[set_id], set_id=set_id)

@app.route('/select-set', methods=['POST'])
def add_set():
	set_id = request.form['setID']
	ui = UserIngredients(session['name'], set_id)
	db.session.add(ui)
	db.session.commit()
	return redirect(url_for('ingredients', username=session['name']))

@app.route('/ingredients/<string:username>')
def ingredients(username):
	does_exist = UserIngredients.query.filter(UserIngredients.name == username).first()

	if does_exist:
		set_id = does_exist.recipe_set
		recipe = Recipe()
		recipes = recipe.recipes[set_id]

		incomplete_recipes = range(0,4)
		
		if does_exist.recipes_completed is not None:
			recipes_completed = does_exist.recipes_completed.split(',')
			print recipes_completed
			incomplete_recipes = [x for x in range(0,4) if str(x) not in recipes_completed]

		your_recipes = [{"id":i,"recipe":recipes[i]} for i in incomplete_recipes]
		
		return render_template('ingredients.html', recipes=your_recipes)
	else:
		return redirect(url_for('recipe_sets'))

@app.route('/complete-recipe', methods=['POST'])
def complete_recipe():
	obj = UserIngredients.query.filter(UserIngredients.name == session['name']).first()
	if obj.recipes_completed is not None:
		completed_recipes = obj.recipes_completed.split(',')
		completed_recipes.append(request.form['recipe_id'])
	else :
		completed_recipes = []
	obj.recipes_completed = ','.join(completed_recipes)
	db.session.commit()	

	return redirect(url_for('ingredients', username=session['name']))