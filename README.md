# Credit Card Payment System

A learning project that combines Django REST Framework and FastAPI to provide user authentication, card metadata management, simulated payment processing, transaction history, and administration using MySQL.

## Technologies

* Python
* Django and Django REST Framework
* Simple JWT
* FastAPI and Pydantic
* SQLAlchemy
* MySQL
* PyMySQL
* pytest, pytest-django, and pytest-cov

## Project Structure

* `users/` — user registration, login, profile, and logout
* `cards/` — card metadata management
* `transactions/` — transaction history, filtering, and CSV export
* `admin_logs/` — administrative activity logs
* `fastapi_app/` — payment processing API and tests
* `config/` — Django settings and URL configuration
* `templates/` — custom Django admin templates
* `credit_card_payment_system.postman_collection.json` — Postman API collection
* `requirements.txt` — Python dependencies
* `.env.example` — environment variable template

## Prerequisites

* Python and pip
* MySQL Server
* Git
* Postman (for API testing)

## Setup

Run the following commands from the project root in PowerShell.

### 1. Create and activate a virtual environment

If you already have a working virtual environment, activate it instead.

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

### 2. Install dependencies

```powershell
python -m pip install -r requirements.txt
```

### 3. Create the MySQL database

Create the project database in MySQL:

```sql
CREATE DATABASE credit_card_payment_db;
```

### 4. Configure environment variables

Create your local `.env` file using `.env.example` as a template. Replace the placeholder values with your own local settings.

The required variables are:

* `DJANGO_SECRET_KEY` — a strong, private Django secret key
* `DATABASE_URL` — the SQLAlchemy connection URL for your MySQL database

Example URL format:

```text
mysql+pymysql://DB_USER:DB_PASSWORD@localhost:3306/credit_card_payment_db
```

Use your own database username and password. URL-encode special characters in the password when required by the connection URL format.

**Security:** Never commit `.env`, real passwords, secret keys, access tokens, or other credentials to GitHub.

### 5. Apply database migrations

```powershell
python manage.py migrate
```

### 6. Create a Django admin account

```powershell
python manage.py createsuperuser
```

Follow the prompts to create your local admin account.

## Start the Services

Open two PowerShell terminals in the project folder and activate the virtual environment in both.

### Django service

```powershell
python manage.py runserver 127.0.0.1:8000
```

* Base URL: `http://127.0.0.1:8000`
* Admin site: `http://127.0.0.1:8000/admin/`

### FastAPI payment service

In the second terminal:

```powershell
python -m uvicorn fastapi_app.main:app --host 127.0.0.1 --port 8001
```

* Base URL: `http://127.0.0.1:8001`
* Swagger documentation: `http://127.0.0.1:8001/docs`

## API Endpoints

### Django API

Base URL: `http://127.0.0.1:8000`

| Method | Endpoint                | Purpose                                   |
| ------ | ----------------------- | ----------------------------------------- |
| POST   | `/api/users/register/`  | Register a user                           |
| POST   | `/api/users/login/`     | Obtain JWT tokens                         |
| GET    | `/api/users/profile/`   | Retrieve the authenticated user's profile |
| POST   | `/api/users/logout/`    | Blacklist a refresh token                 |
| POST   | `/api/cards/add/`       | Add card metadata                         |
| GET    | `/api/cards/`           | List the authenticated user's cards       |
| DELETE | `/api/cards/{card_id}/` | Delete the authenticated user's card      |
| GET    | `/api/transactions/`    | Retrieve transaction history              |

### FastAPI API

Base URL: `http://127.0.0.1:8001`

| Method | Endpoint     | Purpose                            |
| ------ | ------------ | ---------------------------------- |
| GET    | `/`          | Check payment service availability |
| POST   | `/payments/` | Process a simulated payment        |

The payment endpoint requires a valid JWT access token and verifies that the selected card belongs to the authenticated user.

## Example Requests

### Register a user

`POST /api/users/register/`

```json
{
  "username": "demo_user",
  "email": "demo@example.com",
  "password": "Use-A-Strong-Local-Password"
}
```

### Log in

`POST /api/users/login/`

```json
{
  "username": "demo_user",
  "password": "Use-A-Strong-Local-Password"
}
```

Use the returned access token as a Bearer token for protected endpoints. The logout endpoint expects the refresh token.

### Add card metadata

`POST /api/cards/add/`

```json
{
  "card_type": "CREDIT",
  "cardholder_name": "Demo User",
  "masked_card_number": "**** **** **** 1234",
  "last_four_digits": "1234",
  "expiry_date": "2028-12-31"
}
```

Use values accepted by the project's model. Never submit or store a full card number or CVV.

### Submit a payment

`POST http://127.0.0.1:8001/payments/`

Headers:

```text
Authorization: Bearer YOUR_ACCESS_TOKEN
Content-Type: application/json
```

Body:

```json
{
  "card_id": 1,
  "amount": 250.00
}
```

Replace the example card ID with a card belonging to the authenticated user.

The service simulates a payment outcome and returns a transaction ID, amount, initial status, and final status. The final result is randomly selected as `SUCCESS` or `FAILED`. This is a simulation, not a connection to a real payment gateway.

## Transaction Filtering and Export

The transaction history endpoint supports optional query parameters:

* `status` — for example, `SUCCESS` or `FAILED`
* `min_amount` — minimum transaction amount
* `max_amount` — maximum transaction amount
* `start_date` — start date in `YYYY-MM-DD` format
* `end_date` — end date in `YYYY-MM-DD` format

Example:

```text
/api/transactions/?status=SUCCESS&min_amount=100&max_amount=1000
```

The project also supports exporting transaction records as CSV.

## Administration

Visit `http://127.0.0.1:8000/admin/` and sign in with your Django superuser account.

The Django admin interface provides access to the configured user, card, transaction, and administrative log records.

The daily transaction summary is available at:

```text
http://127.0.0.1:8000/admin/transactions/transaction/daily-summary/
```

## Run Tests

Run the Django test suite:

```powershell
python manage.py test
```

Run the FastAPI tests:

```powershell
python -m pytest fastapi_app/test_main.py -v
```

Run the combined test suite with coverage:

```powershell
python -m pytest users/tests.py cards/tests.py transactions/tests.py fastapi_app/test_main.py --ds=config.settings --cov=users --cov=cards --cov=transactions --cov=fastapi_app --cov-report=term-missing
```

The latest recorded combined test run passed **20 tests** and reported **91% total coverage**. Re-run the command in your environment to confirm the current result.

## Security Notes

* Django handles password hashing through its user authentication system.
* The FastAPI payment endpoint validates the JWT access token and checks card ownership.
* Card records should contain only masked card details and the last four digits.
* Never store CVV values or full card numbers.
* Keep `.env` and all real credentials out of source control.
* Use parameterized database queries and validated request data.
* Payment outcomes are simulated; no real payment gateway is connected.
* Use dummy data for development and testing. This project is for learning and should receive a security review before production use.

## Postman

Import `credit_card_payment_system.postman_collection.json` into Postman.

Register and log in first. Use the returned access token for protected Django requests and FastAPI payments. Ensure the selected card belongs to the logged-in user before testing a payment.

## License

This project is intended for learning and demonstration purposes.
