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
cd CS432-Assignment-3
```

3. Install the required dependencies by running:

```
pip install -r requirements.txt
```

## Database Setup

This application uses a MySQL database. To set up the database locally, follow these steps:

1. Install MySQL Server if you haven't already.

2. Create a new database for the application:

```bash
mysql -u root -p
```

Enter your root password when prompted.

```sql
CREATE DATABASE maintenance;
EXIT;
```

3. Import the `dump.sql` file into the newly created database. This file contains the database schema and initial data.

```bash
mysql -u root -p maintenance < dump.sql
```

Enter your root password when prompted. This command will import the contents of `dump.sql` into the `iitgn_maintenance` database.

4. Update the `config.py` file with your local MySQL connection details:

```python
SQLALCHEMY_DATABASE_URI = 'mysql://username:password@localhost/maintenance'
```

Replace `username` and `password` with your actual MySQL credentials.

5. Start the Flask development server:

```
python app.py
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

## Dependencies

The project relies on the following dependencies:

- Flask
- SQLAlchemy (or any other database library used)
- Any other dependencies listed in the `requirements.txt` file