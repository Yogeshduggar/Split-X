# Split-X

Split-X is a Django-based application for managing user accounts and providing a RESTful API with JWT authentication.

## Features

- User registration and authentication
- JWT-based authentication
- API documentation with Swagger

## Installation

1. Clone the repository:
    ```sh
    git clone https://github.com/yourusername/splitx.git
    cd splitx
    ```

2. Create a virtual environment and activate it:
    ```sh
    python -m venv venv
    source venv/bin/activate  # On Windows use `venv\Scripts\activate`
    ```

3. Install the dependencies:
    ```sh
    pip install -r requirement.txt
    ```

4. Apply migrations:
    ```sh
    python manage.py migrate
    ```

5. Create a superuser:
    ```sh
    python manage.py createsuperuser
    ```

6. Run the development server:
    ```sh
    python manage.py runserver
    ```

## Usage

- Access the admin panel at `http://127.0.0.1:8000/admin/`
- Access the API documentation at `http://127.0.0.1:8000/swagger/`


