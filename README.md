# EmailChecker

EmailChecker is a Django application designed to help you monitor email deliverability and performance. It allows you to configure email accounts, automatically sends test emails, and tracks their delivery status and time.

## Key Features

*   **Email Account Configuration:** Set up and manage multiple email accounts for monitoring, including sender/receiver credentials and SMTP/IMAP server details.
*   **Automated Email Checks:** Periodically sends test emails between configured accounts to verify deliverability.
*   **Delivery Status Tracking:** Monitors and records the status of each test email (e.g., pending, sent, received, failed).
*   **Performance Metrics:** Calculates and displays email delivery times.
*   **Comprehensive Dashboard:** Provides an overview of email check statistics, including success rates, average delivery times, and recent activity.
*   **User Authentication:** Secure access to configurations and monitoring data.
*   **Manual Email Tests:** Option to trigger email checks on demand.
*   **Check History & Filtering:** View detailed logs of all email checks, with options to search and filter results.

## Getting Started

These instructions will get you a copy of the project up and running on your local machine for development and testing purposes.

### Prerequisites

*   Python (3.8 or higher recommended)
*   pip (Python package installer)
*   Git

### Installation

1.  **Clone the repository:**
    ```bash
    git clone <repository_url> # Replace <repository_url> with the actual URL
    cd EmailChecker
    ```

2.  **Create and activate a virtual environment (recommended):**
    ```bash
    python -m venv venv
    # On Windows
    venv\Scripts\activate
    # On macOS/Linux
    source venv/bin/activate
    ```

3.  **Install dependencies:**
    ```bash
    pip install -r requrment.txt
    ```
    *Note: The requirements file is named `requrment.txt`. If this is a typo and should be `requirements.txt`, please adjust the command accordingly.*

4.  **Apply database migrations:**
    ```bash
    python manage.py migrate
    ```

5.  **Create a superuser (for accessing the admin panel and the application):**
    ```bash
    python manage.py createsuperuser
    ```
    Follow the prompts to set up your username, email, and password.

### Running the Development Server

1.  **Start the Django development server:**
    ```bash
    python manage.py runserver
    ```

2.  Open your web browser and navigate to `http://127.0.0.1:8000/`.
    *   You should be redirected to the login page. Use the superuser credentials you created earlier to log in.
    *   The main dashboard will be available at `http://127.0.0.1:8000/dashboard/`.

*(The project uses Celery for asynchronous tasks. For production or more thorough testing of background tasks, you'll also need to set up and run a Celery worker and a message broker like Redis or RabbitMQ. This setup is not covered in this basic getting started guide.)*

## Technology Stack

*   **Backend:** Python, Django
*   **Asynchronous Tasks:** Celery
*   **Frontend:** HTML, CSS (likely with Django Templates)
*   **Database:** SQLite (default for Django, can be configured for others like PostgreSQL, MySQL)

## Project Structure

The project follows a standard Django application structure:

```
EmailChecker/
├── EmailChecker/       # Main project configuration (settings.py, urls.py, wsgi.py, asgi.py, celery.py)
├── account/            # Django app for user authentication (login, registration)
├── core/               # Django app containing the core logic for email configurations and checks
├── dashboard/          # Django app for the user dashboard and statistics display
├── templates/          # HTML templates used across different apps
├── manage.py           # Django's command-line utility
├── requrment.txt       # Python package dependencies
└── README.md           # This file
```

*   **`EmailChecker/` (inner directory):** Contains the main Django project settings, URL configurations, and configurations for WSGI/ASGI servers and Celery.
*   **`account/`:** Handles user registration, login, logout, and potentially profile management.
*   **`core/`:** The heart of the application. It defines the models for email configurations (`EmailConfiguration`) and email check records (`EmailCheck`), along with the views and forms to manage them, and the Celery tasks for sending emails.
*   **`dashboard/`:** Provides the views to display aggregated data and statistics to the logged-in user.
*   **`templates/`:** Contains the HTML files that render the user interface for each application.

## Contributing

Contributions are welcome! If you have suggestions for improvements or find any issues, please feel free to open an issue or submit a pull request.

*(Further details on the contribution process, coding standards, and setup for development can be added here in the future.)*

## License

This project is currently not under a specific license. Please check back later or contact the maintainers for more information.
