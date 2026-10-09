# Credit Card Payment System

A learning project that uses Django REST Framework for user authentication, card management, transaction history, and administration, with a separate FastAPI service for payment processing and MySQL as the database.

## Technologies
- Python
- Django and Django REST Framework
- Simple JWT
- FastAPI and Pydantic
- SQLAlchemy
- MySQL
- pytest and pytest-cov

## Project Structure
- `users/` — registration, login, profile, and logout
- `cards/` — card metadata management
- `transactions/` — transaction history and filters
- `admin_logs/` — administrative activity logs
- `fastapi_app/` — payment processing service and tests
- `config/` — Django settings and URL configuration
- `templates/` — Django admin templates

## Setup

Run commands from the project root in PowerShell.

1. Activate your virtual environment:

   ```powershell
   .\venv\Scripts\Activate.ps1
   ```

2. Ensure the project dependencies are installed in the virtual environment.

3. Create the MySQL database:

   ```sql
   CREATE DATABASE credit_card_payment_db;
   ```

4. Configure the MySQL connection in Django settings and `fastapi_app/database.py` using your own local database credentials. Never commit passwords or tokens to Git.

5. Apply migrations:

   ```powershell
   python manage.py migrate
   ```

6. Create an admin account if needed:

   ```powershell
   python manage.py createsuperuser
   ```

## Start the Services

Open two terminals from the project folder and activate the virtual environment in both.

### Django

```powershell
python manage.py runserver 127.0.0.1:8000
```

Admin: http://127.0.0.1:8000/admin/

### FastAPI

```powershell
python -m uvicorn fastapi_app.main:app --host 127.0.0.1 --port 8001
```

API documentation: http://127.0.0.1:8001/docs

## API Endpoints

Django base URL: `http://127.0.0.1:8000`

| Method | Endpoint | Purpose |
|---|---|---|
| POST | `/api/users/register/` | Register a user |
| POST | `/api/users/login/` | Obtain JWT tokens |
| GET | `/api/users/profile/` | Get the authenticated user's profile |
| POST | `/api/users/logout/` | Blacklist a refresh token |
| POST | `/api/cards/add/` | Add card metadata |
| GET | `/api/cards/` | List the authenticated user's cards |
| DELETE | `/api/cards/{card_id}/` | Delete the authenticated user's card |
| GET | `/api/transactions/` | View transaction history |

FastAPI base URL: `http://127.0.0.1:8001`

| Method | Endpoint | Purpose |
|---|---|---|
| GET | `/` | Check that the payment service is running |
| POST | `/payments/` | Submit a simulated payment request |

## Example Requests

### Register

`POST /api/users/register/`

```json
{
  "username": "demo_user",
  "email": "demo@example.com",
  "password": "Use-A-Strong-Local-Password"
}
```

### Login

`POST /api/users/login/`

```json
{
  "username": "demo_user",
  "password": "Use-A-Strong-Local-Password"
}
```

Use the returned access token as a Bearer token for protected Django endpoints. The logout endpoint expects the refresh token.

### Add Card

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

Use values accepted by the project's model. Do not send or store a full card number or CVV.

### Submit Payment

`POST http://127.0.0.1:8001/payments/`

```json
{
  "user_id": 1,
  "card_id": 1,
  "amount": 250.00
}
```

The IDs must refer to valid records in the database used by the payment service. The current implementation randomly returns `SUCCESS` or `FAILED`; it is a simulation, not a real payment gateway.

## Transaction Filters

The transaction history endpoint supports these optional query parameters:
- `status` — such as `SUCCESS` or `FAILED`
- `min_amount`
- `max_amount`
- `start_date` — `YYYY-MM-DD`
- `end_date` — `YYYY-MM-DD`

Example:

`/api/transactions/?status=SUCCESS&min_amount=100&max_amount=1000`

## Run Tests

Run the Django tests:

```powershell
python manage.py test
```

Run the FastAPI tests:

```powershell
python -m pytest fastapi_app/test_main.py -v
```

Run all 18 tests with combined coverage:

```powershell
python -m pytest users/tests.py cards/tests.py transactions/tests.py fastapi_app/test_main.py --ds=config.settings --cov=users --cov=cards --cov=transactions --cov=fastapi_app --cov-report=term-missing
```

The development test run passed 18 tests and reported 92% coverage. Run the command again to verify results in your environment.

## Security Notes

- Django's user creation API hashes passwords.
- Card records should contain only masked card details and the last four digits. Never store CVV or full card numbers.
- Keep database credentials and JWT tokens out of source control.
- The current FastAPI payment endpoint does not authenticate the caller or verify card ownership. Add authentication and ownership validation before any production use.
- Payment outcomes are simulated; no real payment gateway is connected.
- Use dummy test data only.

## Postman

Import `credit_card_payment_system.postman_collection.json` into Postman. Register and log in first, then use the saved access token for protected Django requests. Set valid `userId` and `cardId` values before submitting a payment.
