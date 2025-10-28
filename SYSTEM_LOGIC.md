# NeuraSynth System Logic

This document provides a high-level overview of the NeuraSynth system's architecture and the detailed logic of each component.

## High-Level Architecture

The NeuraSynth system is a Flask-based web application that provides a platform for connecting talent with projects. The system is designed with a modular architecture, with each component responsible for a specific set of functionalities.

The main components of the system are:

*   **Application:** The main application, responsible for creating and configuring the Flask application instance.
*   **Authentication:** The authentication module, responsible for user authentication, registration, and JWT token management.
*   **User Management:** The user management module, responsible for managing user profiles.
*   **Project Management:** The project management module, responsible for managing projects.
*   **AI Matching:** The AI matching module, responsible for matching freelancers with projects.
*   **Contributors Hub:** The contributors hub module, responsible for managing contributor equity and performance.

## Detailed Logic

### Application

The application is created and configured using the app factory pattern. The `create_app` function in the `src/app.py` file is responsible for creating a Flask application instance and configuring it with the appropriate settings for the current environment.

The `create_app` function also initializes the database and registers the blueprints for the different modules.

### Authentication

The authentication module is responsible for user authentication, registration, and JWT token management. The `AuthManager` class in the `src/auth.py` file provides the following functionalities:

*   **User Registration:** The `register_user` method registers a new user. It takes the user's email, password, and user type as input, and it creates a new `User` object and saves it to the database.
*   **User Authentication:** The `authenticate_user` method authenticates a user. It takes the user's email and password as input, and it verifies the user's credentials against the database.
*   **JWT Token Management:** The `generate_token` method generates a JWT token for a user. The `verify_token` method verifies a JWT token.

### User Management

The user management module is responsible for managing user profiles. The `UserManager` class in the `src/user.py` file provides the following functionalities:

*   **Get User Profile:** The `get_user_profile` method gets a user's profile. It takes the user's ID as input, and it returns a dictionary with the user's profile information.
*   **Update User Profile:** The `update_user_profile` method updates a user's profile. It takes the user's ID and a dictionary with the updated profile information as input, and it updates the user's profile in the database.

### Project Management

The project management module is responsible for managing projects. The `ProjectManager` class in the `src/project.py` file provides the following functionalities:

*   **Create Project:** The `create_project` method creates a new project. It takes a dictionary with the project information as input, and it creates a new `Project` object and saves it to the database.
*   **Get Project:** The `get_project` method gets a project. It takes the project's ID as input, and it returns a dictionary with the project information.

### AI Matching

The AI matching module is responsible for matching freelancers with projects. The `AdvancedMatchingEngine` class in the `src/advanced_ai_systems.py` file provides the following functionalities:

*   **Find Matches:** The `find_matches_for_project` method finds the best freelancer matches for a project. It takes the project's ID as input, and it returns a list of the best matches.

### Contributors Hub

The contributors hub module is responsible for managing contributor equity and performance. The `ContributorsHub` class in the `src/contributors_hub.py` file provides the following functionalities:

*   **Get Equity Holdings:** The `get_equity_holdings` method gets a contributor's equity holdings. It takes the contributor's ID as input, and it returns a dictionary with the contributor's equity holdings.
*   **Get Performance Metrics:** The `get_performance_metrics` method gets a contributor's performance metrics. It takes the contributor's ID as input, and it returns a dictionary with the contributor's performance metrics.
