# NeuraSynth Studios

NeuraSynth Studios is a Flask-based web application that provides a platform for connecting talent with projects.

## Setup

1.  Clone the repository:
    ```
    git clone https://github.com/your-username/neurasynth.git
    ```
2.  Install the dependencies:
    ```
    pip install -r requirements.txt
    ```
3.  Create a `.env` file in the project root and add the following environment variables:
    ```
    FLASK_CONFIG=development
    SECRET_KEY=a-very-secret-key
    ```
4.  Run the application:
    ```
    python run.py
    ```

## Running the Tests

To run the tests, run the following command:
```
python -m unittest discover tests
```

## API Endpoints

### Automation

-   `POST /api/v1/automation/rules`: Add a new automation rule.
-   `DELETE /api/v1/automation/rules/<rule_id>`: Remove an automation rule.
-   `GET /api/v1/automation/stats`: Get automation engine statistics.
-   `POST /api/v1/projects/<project_id>/monitor`: Analyze and report project health.

### Financial

-   `POST /api/v1/financial/expenses`: Create a new expense.
-   `GET /api/v1/financial/expenses/<expense_id>`: Get an expense by ID.
-   `POST /api/v1/financial/invoices`: Create a new invoice.
-   `GET /api/v1/financial/invoices/<invoice_id>`: Get an invoice by ID.
-   `POST /api/v1/financial/payments`: Create a new payment.
-   `GET /api/v1/financial/payments/<payment_id>`: Get a payment by ID.
