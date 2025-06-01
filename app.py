import os
import requests
from flask import Flask, jsonify, request
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from bs4 import BeautifulSoup
from flasgger import Swagger, swag_from

app = Flask(__name__)

# JWT Config
app.config["JWT_SECRET_KEY"] = "yes_this_is_hardcoded_dont_do_it_at_home"
jwt = JWTManager(app)

# Swagger Config
swagger_config = {
    "headers": [],
    "title": "Brazil Wine Data API",
    "description": "API providing wine production and economics data in Brazil.",
    "version": "1.0.0",
    "specs": [
        {
            "endpoint": 'apispec',
            "route": '/apispec.json',
            "rule_filter": lambda rule: True,  # include all endpoints
            "model_filter": lambda tag: True,  # include all models
        }
    ],
    "static_url_path": "/flasgger_static",
    "swagger_ui": True,
}
swagger = Swagger(app, config=swagger_config)

# Dummy user database
users = {
    "admin": "password123"
}

@app.route("/login", methods=["POST"])
@swag_from({
    'tags': ['Auth'],
    'parameters': [
        {
            "name": "body",
            "in": "body",
            "required": True,
            "schema": {
                "type": "object",
                "properties": {
                    "username": {"type": "string"},
                    "password": {"type": "string"}
                },
                "required": ["username", "password"]
            }
        }
    ],
    'responses': {
        200: {
            "description": "Successful login",
            "schema": {
                "type": "object",
                "properties": {
                    "access_token": {"type": "string"}
                }
            }
        },
        401: {
            "description": "Invalid credentials"
        }
    }
})
def login():
    data = request.get_json()
    username = data.get("username")
    password = data.get("password")

    if users.get(username) == password:
        token = create_access_token(identity=username)
        return jsonify(access_token=token), 200
    else:
        return jsonify(msg="Invalid username or password"), 401


@app.route("/production/<int:year>", methods=["GET"])
@jwt_required()
@swag_from({
    'tags': ['Production'],
    'parameters': [
        {
            "name": "year",
            "in": "path",
            "type": "integer",
            "required": True,
            "description": "Year of wine production data"
        }
    ],
    'responses': {
        200: {
            "description": "Wine production data",
            "schema": {
                "type": "object",
                "example": {
                    "VINHO DE MESA": {
                        "Quantidade (L.)": "169.762.429",
                        "Tinto": "139.320.884",
                        "Branco": "27.910.299",
                        "Rosado": "2.531.246"
                    }
                }
            }
        },
        401: {"description": "Unauthorized"}
    }
})
def get_production(year):
    url = f"http://vitibrasil.cnpuv.embrapa.br/index.php?ano={year}&opcao=opt_02"
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")

    table = soup.find("table", class_="tb_base tb_dados")
    if not table:
        return jsonify({"error": "Table not found"}), 404

    data = {}
    current_category = None

    for row in table.find_all("tr"):
        cols = row.find_all("td")
        if len(cols) != 2:
            continue

        name = cols[0].get_text(strip=True)
        value = cols[1].get_text(strip=True)

        if "tb_item" in cols[0].get("class", []):
            current_category = name
            data[current_category] = {"Quantidade (L.)": value}
        elif "tb_subitem" in cols[0].get("class", []) and current_category:
            data[current_category][name] = value

    return jsonify(data)
@app.route('/processing/<int:year>/<string:category>', methods=['GET'])
@jwt_required()
@swag_from({
    'tags': ['processing'],
    'parameters': [
        {
            'name': 'year',
            'in': 'path',
            'type': 'integer',
            'required': True,
            'description': 'Year of the data (e.g. 2023)'
        },
        {
            'name': 'category',
            'in': 'path',
            'type': 'string',
            'required': True,
            'enum': ['vinifera', 'americans', 'table', 'unclassified'],
            'description': 'Category of grape (vinifera, americans, table, unclassified)'
        }
    ],
    'responses': {
        200: {
            'description': 'Hierarchical grape processing data',
            'examples': {
                'application/json': {
                    'ano': 2023,
                    'categoria': 'vinifera',
                    'dados': [
                        {
                            'Categoria': 'TINTAS',
                            'Quantidade (Kg)': '35.881.118',
                            'Subcategorias': [
                                {'Cultivar': 'Alicante Bouschet', 'Quantidade (Kg)': '4.108.858'},
                                {'Cultivar': 'Outro nome', 'Quantidade (Kg)': '1.000.000'}
                            ]
                        }
                    ]
                }
            }
        }
    }
})
def processing(year, category):
    category_map = {
        'vinifera': 'subopt_01',
        'americans': 'subopt_02',
        'table': 'subopt_03',
        'unclassified': 'subopt_04'
    }

    if category not in category_map:
        return jsonify({'error': 'Invalid category'}), 400

    sopcao = category_map[category]
    url = f'http://vitibrasil.cnpuv.embrapa.br/index.php?ano={year}&subopcao={sopcao}&opcao=opt_03'

    try:
        response = requests.get(url)
        soup = BeautifulSoup(response.content, 'html.parser')
        table = soup.find('table', class_='tb_base tb_dados')

        data = []
        current_category = None

        for row in table.find_all('tr'):
            cols = row.find_all('td')
            if len(cols) != 2:
                continue

            cell_class = cols[0].get('class')[0] if cols[0].get('class') else ''

            if cell_class == 'tb_item':
                # Start a new category
                current_category = {
                    'Categoria': cols[0].text.strip(),
                    'Quantidade (Kg)': cols[1].text.strip(),
                    'Subcategorias': []
                }
                data.append(current_category)

            elif cell_class == 'tb_subitem' and current_category:
                # Add to current category
                sub = {
                    'Cultivar': cols[0].text.strip(),
                    'Quantidade (Kg)': cols[1].text.strip()
                }
                current_category['Subcategorias'].append(sub)

        return jsonify({'ano': year, 'categoria': category, 'dados': data})

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route("/")
def index():
    return jsonify({"message": "Welcome to the Brazil Wine Data API!"})

if __name__ == "__main__":
    app.run(debug=True)
