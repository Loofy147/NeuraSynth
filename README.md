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
