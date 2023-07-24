
# Dynamic Tables API

This project provides an API for creating and managing dynamic tables in a database. Using this API, you can create new tables, add new fields to existing tables, update the structure of tables, and fetch rows from tables, all through a RESTful API.

## Tech Stack
- Python 3.11
- Django 4
- PostgreSQL 14

## API Documentation

API documentation is available via Swagger at: `http://localhost:8000/swagger`

## Docker Setup

1. Ensure Docker is installed on your machine.
2. Run the following command in the root directory of the project to start the Docker containers:

```
docker-compose up -d
```

This command starts the PostgreSQL container.

## Database Setup

1. Enter the PostgreSQL Docker container:

```
docker exec -it <container_id> bash
```

Replace `<container_id>` with the ID of your running PostgreSQL Docker container. You can get this by running `docker ps`.

2. Once inside the Docker container, run the following command to create a new PostgreSQL database:

```
psql -U postgres -c "CREATE DATABASE dynamic_tables_db;"
```

This command creates a new PostgreSQL database named `dynamic_tables_db` with the user `postgres`.

## Application Setup

1. Ensure you are in the root directory of the project.
2. Setup and activate a virtual environment:

    For Unix or MacOS systems, use the following commands:

    ```
    python3 -m venv env
    source env/bin/activate
    ```

    For Windows, use the following commands:

    ```
    py -m venv env
    env\Scripts\activate
    ```

3. Install the required Python packages:

    ```
    pip install -r requirements.txt
    ```

4. Run Django migrations:

    ```
    python manage.py migrate
    ```

5. Start the Django development server:

    ```
    python manage.py runserver
    ```

The API should now be available at: `http://localhost:8000`

Do remember to replace "env" with the name of your virtual environment if you have chosen a different name.


## Running Tests

Navigate to the `tests` directory and run the following command:

```
pytest
```

This command runs all the tests in the project.

---

Please update the URLs, file paths, and commands to match your actual project structure and configurations if needed.