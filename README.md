# IITGN Maintenance Database Management System

This is a web application built using Flask backend and HTML frontend for managing the maintenance requests and resources at IIT Gandhinagar. The application provides a centralized system for managing users, workers, domains, locations, and maintenance requests.

## Getting Started

To run the application locally, follow these steps:

1. Clone the repository:

```
git clone https://github.com/Shubh-81/CS432-Assignment-3.git
```

2. Navigate to the project directory:

```
cd iitgn-maintenance
```

3. Install the required dependencies by running:

```
pip install -r requirements.txt
```

4. Start the Flask development server:

```
python server/app.py
```

The application will be running locally on `http://localhost:5000`.

## Application Structure

The application consists of the following routes:

- `/` - The main maintenance home page.
- `/users` - Displays the user table.
- `/workers` - Displays the worker table.
- `/domains` - Displays the domain table.
- `/requests` - Displays the request table.
- `/locations` - Displays the location table.

## Database

The application uses a database to store and manage the data. The database is initialized and created using the `db.create_all()` function in the `app.py` file.

## Dependencies

The project relies on the following dependencies:

- Flask
- SQLAlchemy (or any other database library used)
- Any other dependencies listed in the `requirements.txt` file