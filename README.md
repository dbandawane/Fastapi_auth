# FastAPI User Authentication App

This project is a simple user authentication system built using FastAPI, PostgreSQL, and bcrypt for password hashing. The app provides routes for user login, signup, forgot password, and change password, and includes JWT token-based authentication.

## Features

- **Signup Route**: Allows a new user to register.
- **Login Route**: Authenticates an existing user using email and password and returns a JWT token.
- **Forgot Password Route**: Sends a verification code to the user's email.
- **Change Password Route**: Allows the user to change the password using the verification code.
- **Validation**: Includes input validation for name and phone number fields.
- **Unsuccessful Login Attempts**: Locks the account after 3 failed login attempts.

## Technologies

- **FastAPI**: Web framework for building APIs.
- **PostgreSQL**: Database for storing user information.
- **bcrypt**: Library for password hashing.
- **JWT**: JSON Web Tokens for secure authentication.

## Setup Instructions

### 1. Clone the repository
```bash
git clone https://github.com/your-username/fastapi-user-auth.git
cd fastapi-user-auth
