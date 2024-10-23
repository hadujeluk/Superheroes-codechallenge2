from flask import Flask, request, jsonify
from flask_migrate import Migrate
from models import db, Hero, Power, HeroPower
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.environ.get(
    "DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}")

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

migrate = Migrate(app, db)
db.init_app(app)

@app.route('/')
def index():
    return '<h1>Code challenge</h1>'

@app.route('/heroes', methods=['GET'])
def get_heroes():
    heroes = Hero.query.all()
    return jsonify([hero.to_dict() for hero in heroes]), 200

@app.route('/heroes/<int:id>', methods=['GET'])
def get_hero_by_id(id):
    hero = db.session.get(Hero, id)
    if hero is None:
        return jsonify({'error': 'Hero not found'}), 404
    
    return jsonify({
        'id': hero.id,
        'name': hero.name,
        'super_name': hero.super_name,
        'hero_powers': [hp.to_dict() for hp in hero.hero_powers]
    }), 200

@app.route('/powers', methods=['GET'])
def get_powers():
    powers = Power.query.all()
    return jsonify([power.to_dict() for power in powers]), 200

@app.route('/powers/<int:id>', methods=['GET'])
def get_power_by_id(id):
    power = db.session.get(Power, id)
    if power is None:
        return jsonify({'error': 'Power not found'}), 404
    return jsonify(power.to_dict()), 200

@app.route('/powers/<int:id>', methods=['PATCH'])
def update_power(id):
    power = db.session.get(Power, id)
    if power is None:
        return jsonify({'error': 'Power not found'}), 404

    data = request.get_json()
    errors = []
    
    if 'description' in data:
        if not isinstance(data['description'], str) or len(data['description']) < 20:
            errors.append('validation errors')  # Change here to match test expectations

    if errors:
        return jsonify({'errors': errors}), 400

    if 'description' in data:
        power.description = data['description']

    db.session.commit()
    return jsonify(power.to_dict()), 200

@app.route('/hero_powers', methods=['POST'])
def create_hero_power():
    data = request.get_json()
    errors = []

    strength = data.get('strength')
    hero_id = data.get('hero_id')
    power_id = data.get('power_id')

    if strength not in ['Strong', 'Weak', 'Average']:
        errors.append('validation errors')  # Change here to match test expectations

    hero = db.session.get(Hero, hero_id)
    power = db.session.get(Power, power_id)

    if not hero:
        errors.append('Hero not found.')
    if not power:
        errors.append('Power not found.')

    if errors:
        return jsonify({'errors': errors}), 400

    hero_power = HeroPower(strength=strength, hero_id=hero_id, power_id=power_id)
    db.session.add(hero_power)
    db.session.commit()
    return jsonify(hero_power.to_dict()), 201  # Status code remains 201 for creation

if __name__ == '__main__':
    app.run(port=5555, debug=True)
