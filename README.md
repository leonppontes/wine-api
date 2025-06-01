
# 🇧🇷 Brazil Wine Data API

A Flask-based REST API for accessing wine production, processing, commercialization, import, and export data in Brazil, powered by web scraping from [vitibrasil.cnpuv.embrapa.br](http://vitibrasil.cnpuv.embrapa.br).

## 📦 Features

- ✅ JWT-protected endpoints  
- 📊 Swagger UI for API documentation  
- 🍇 Data categories:
  - Production
  - Processing (by grape type)
  - Commercialization
  - Import (by product and country)
  - Export (by product and country)
- 🔐 Login route for token-based access control

---

## 🚀 Getting Started

### 1. Clone the repository

```bash
git clone https://github.com/your-username/brazil-wine-api.git
cd brazil-wine-api
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Run the app

```bash
python app.py
```

### 4. Access the API

- Base URL: `http://localhost:5000`
- Swagger UI: `http://localhost:5000/apidocs`

---

## 🔐 Authentication

Generate a JWT token:

**POST** `/login`

Request body:

```json
{
  "username": "admin",
  "password": "password123"
}
```

Use the token in the `Authorization` header as:

```
Bearer <your_token>
```

---

## 📚 Endpoints

### 🟢 Public

#### `GET /`
Health check or root welcome message.

#### `GET /import/<year>/<category>`
**Tags**: `Importação`

Retrieve import data by year and product category.

- **Categories**:  
  - `table`  
  - `sparkling`  
  - `fresh`  
  - `raisins`  
  - `juice`

Example:

```
GET /import/2023/table
```

Response example:

```json
{
  "country": "Argentina",
  "quantity": 12345,
  "value": 67890
}
```

#### `GET /export/<year>/<category>`
**Tags**: `Exportação`

Retrieve export data by year and product category.

- **Categories**:  
  - `table`  
  - `sparkling`  
  - `fresh`  
  - `juice`

Example:

```
GET /export/2023/juice
```

Response example:

```json
{
  "country": "USA",
  "quantity": 54321,
  "value": 98765
}
```

---

### 🔒 Protected (require JWT)

#### `GET /production/<year>`
**Tags**: `Production`

Retrieve wine production data for the given year.

#### `GET /processing/<year>/<category>`
**Tags**: `Processing`

Retrieve grape processing data by year and grape type.

- **Categories**:  
  - `vinifera`  
  - `americans`  
  - `table`  
  - `unclassified`

Example:

```
GET /processing/2023/vinifera
```

#### `GET /commercialization/<year>`
**Tags**: `Comercialização`

Retrieve commercialization volumes by product for a specific year.

---

## 📑 API Documentation

Swagger UI is available at:

```
http://localhost:5000/apidocs
```

Use it to explore all routes, parameters, and responses interactively.

---

## 📌 Notes

- Data is fetched in real-time from vitibrasil.cnpuv.embrapa.br using BeautifulSoup.
- Internet connection is required to use the API.
- Replace the hardcoded secret key in `app.py` with a secure environment variable for production use.

---

## 📃 License

MIT License
