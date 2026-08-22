# Secure Login System with User Details & File Access

A secure authentication and file-access system implemented using **two different backends**:

1. **Custom Backend** — Python with Flask + PostgreSQL
2. **Managed Backend** — Appwrite

The same provided web testing client is used to interact with both implementations. The project focuses on authentication, authorization, user-data isolation, secure file access, and session handling rather than UI styling.

---

## Project Structure

```text
secure-login-system/
│
├── client/
│
├── custom-backend/
│
├── venv/
│
├── app.py
├── models.py
├── seed.py
├── requirements.txt
│
├── appwrite-adapter.js
├── index.html
├── mock-api.js
├── seed-data.json
│
├── storage/
│
├── .env
├── .env.example
├── .gitignore
└── README.md
```

### Important files

| File                  | Purpose                                                                |
| --------------------- | ---------------------------------------------------------------------- |
| `index.html`          | Provided testing client used for interacting with the system           |
| `mock-api.js`         | Provided mock/reference implementation; not used as the actual backend |
| `seed-data.json`      | Provided sample/reference data                                         |
| `app.py`              | Custom Flask backend                                                   |
| `models.py`           | Database models/data structure for the custom backend                  |
| `seed.py`             | Seeds test users and associated data                                   |
| `appwrite-adapter.js` | Appwrite-based implementation/adapter                                  |
| `requirements.txt`    | Python dependencies                                                    |
| `.env.example`        | Template for required environment variables                            |
| `.env`                | Local environment configuration; not committed to Git                  |
| `storage/`            | Local file storage used by the custom implementation                   |

---

# 1. Features

Both implementations support the core requirements of the task:

* User registration using email and password
* User login
* Authenticated sessions
* Logout
* Protected user profile access
* User-specific file listing
* Individual file access
* User-to-user data isolation
* Multiple seeded test accounts
* Password hashing
* Generic failed-login responses
* Protection against repeated failed login attempts
* Authentication validation on protected routes

---

# 2. Custom Backend

The custom implementation uses:

* **Python**
* **Flask**
* **PostgreSQL**
* Password hashing
* Authentication/session validation
* Server-side authorization checks

## Database

The application uses PostgreSQL for persistent application data.

The database connection is configured through:

```env
DATABASE_URL=postgresql://postgres:YOUR_PASSWORD@localhost:5432/secure_login_db
```

The actual `.env` file is intentionally excluded from version control.

---

# 3. Authentication Design

## Why session-based authentication?

For the custom backend, authentication is handled using a server-controlled session approach rather than relying only on a stateless token stored on the client.

The important requirement in this task is that **logout must invalidate the session server-side**.

A server-controlled session makes this straightforward:

```text
Login
  ↓
Credentials verified
  ↓
Authenticated session created
  ↓
Client uses the session for protected requests
  ↓
Logout
  ↓
Server invalidates the session
```

This means simply keeping an old authentication value on the client does not allow the user to continue accessing protected resources after logout.

---

# 4. Password Security

Passwords are **not stored in plaintext**.

During registration, the supplied password is hashed before being stored in the database.

During login, the submitted password is verified against the stored password hash.

Therefore, the database does not need to store the user's original password.

---

# 5. Login Error Handling

Failed login attempts return a generic authentication error rather than revealing whether a particular email address exists.

For example, the application does not intentionally distinguish between:

```text
Email does not exist
```

and:

```text
Password is incorrect
```

Instead, both are treated as an unsuccessful login attempt.

This reduces the possibility of user/email enumeration.

---

# 6. Rate Limiting / Failed Login Protection

Repeated failed authentication attempts are restricted using rate-limiting/failed-login protection.

This provides a basic defense against repeatedly guessing passwords and satisfies the requirement for protection after repeated failed login attempts.

---

# 7. User Data Isolation

A key security requirement of this project is that an authenticated user must only be able to access their own data.

The authenticated user's identity is obtained from the validated authentication/session information.

The application does **not** trust a user-supplied ID to decide whose data should be returned.

Conceptually:

```text
Request
   ↓
Validate authentication
   ↓
Identify authenticated user
   ↓
Use authenticated user's ID
   ↓
Retrieve only that user's data
```

This prevents a user from attempting to access another user's profile simply by changing an identifier in the request.

For example:

```text
User A → authenticated as A

Requesting A's data → allowed

Requesting B's data by changing an ID → rejected
```

---

# 8. File Access Security

Each seeded user has files associated with their account.

The application provides authenticated access to the user's files.

For a single-file request, ownership is checked before returning the file.

The important authorization rule is:

```text
Authenticated User ID == File Owner ID
```

If the requested file belongs to another user, the request is rejected rather than returning the file.

This provides protection against insecure direct object references where a user attempts to change a file ID in the URL/request to access someone else's file.

The implementation also distinguishes between:

* a file that does not exist, and
* a file that exists but belongs to another user.

---

# 9. Seed Data

The project includes a seed script:

```text
seed.py
```

The seed setup provides at least three separate test users, with each user having their own profile and associated files.

The test data is intended to make it possible to verify:

```text
User 1
 ├── Profile
 └── Files

User 2
 ├── Profile
 └── Files

User 3
 ├── Profile
 └── Files
```

The users can be used to verify that authentication and authorization are isolated between accounts.

The exact test credentials are defined by the seed configuration and should be checked in `seed.py` / `seed-data.json`.

---

# 10. Appwrite Implementation

The second implementation uses **Appwrite** as the managed backend.

The Appwrite configuration uses:

```text
Endpoint: https://sgp.cloud.appwrite.io/v1
```

The project uses an Appwrite project and storage bucket for the managed implementation.

The project ID and bucket ID are configuration identifiers and are kept configurable through environment variables.

Sensitive credentials, such as an Appwrite API key if used by a server-side component, must never be committed to the repository.

---

# 11. What Appwrite Handles

Appwrite provides managed backend functionality instead of requiring the application to implement everything from scratch.

In the Appwrite implementation, Appwrite is responsible for the managed authentication and storage infrastructure used by the application.

This includes functionality such as:

* User account management
* Authentication/session management
* User identity generation
* File storage
* Access control/permissions for Appwrite resources

The application is still responsible for configuring Appwrite correctly and ensuring that the client uses the authenticated user's identity when accessing protected resources.

---

# 12. What We Configure Ourselves

The application configures:

* Appwrite endpoint
* Appwrite project
* Storage bucket
* Authentication flow used by the testing client
* File access behavior
* User-specific access rules
* Environment variables
* Seed/test data

The Appwrite configuration is kept separate from the custom PostgreSQL implementation.

---

# 13. Environment Variables

Create a local `.env` file using `.env.example` as a template.

Example:

```env
DATABASE_URL=postgresql://postgres:YOUR_PASSWORD@localhost:5432/secure_login_db

APPWRITE_ENDPOINT=https://sgp.cloud.appwrite.io/v1
APPWRITE_PROJECT_ID=YOUR_APPWRITE_PROJECT_ID
APPWRITE_BUCKET_ID=YOUR_APPWRITE_BUCKET_ID
```

### Important

`.env` contains local configuration and must **not** be committed to Git.

`.env.example` is safe to commit because it contains placeholders rather than secrets.

---

# 14. Installation

## Clone the repository

```bash
git clone <YOUR_REPOSITORY_URL>
cd <YOUR_REPOSITORY_FOLDER>
```

## Create a Python virtual environment

```bash
python -m venv venv
```

### Windows

```bash
venv\Scripts\activate
```

### macOS/Linux

```bash
source venv/bin/activate
```

## Install dependencies

```bash
pip install -r requirements.txt
```

---

# 15. PostgreSQL Setup

Create a PostgreSQL database named:

```text
secure_login_db
```

Then configure the connection in `.env`:

```env
DATABASE_URL=postgresql://postgres:YOUR_PASSWORD@localhost:5432/secure_login_db
```

Use your own local PostgreSQL username/password.

---

# 16. Seed the Test Data

Run the seed script:

```bash
python seed.py
```

The seed process creates the required test users and their associated data/files.

After seeding, use the credentials provided by the seed configuration to test the system with multiple accounts.

---

# 17. Run the Custom Backend

Start the Flask application using:

```bash
python app.py
```

The backend can then be accessed by the provided testing client.

Use the provided:

```text
index.html
```

for testing the authentication and file-access functionality.

---

# 18. Testing User Isolation

The recommended test procedure is to use at least two different seeded accounts.

### Test 1 — Registration

Register a new account using:

```text
Email
Password
```

Verify that the account is created successfully.

### Test 2 — Login

Log in using a valid seeded account.

Verify that authentication succeeds.

### Test 3 — Profile

After login, access the authenticated user's profile.

Verify that only that user's information is returned.

### Test 4 — File Listing

Request the authenticated user's files.

Verify that only files belonging to that user are returned.

### Test 5 — Cross-user file access

Log in as User A.

Attempt to request a file belonging to User B.

The request must be rejected.

### Test 6 — Logout

Log out as User A.

Attempt to access a protected route using the previous authentication state.

The request should no longer be authorized because the server-side session has been invalidated.

---

# 19. Appwrite Setup

The Appwrite implementation requires an Appwrite project with the required storage configuration.

Configure the values in `.env`:

```env
APPWRITE_ENDPOINT=https://sgp.cloud.appwrite.io/v1
APPWRITE_PROJECT_ID=YOUR_APPWRITE_PROJECT_ID
APPWRITE_BUCKET_ID=YOUR_APPWRITE_BUCKET_ID
```

The Appwrite project must have the required authentication and storage functionality enabled.

The Appwrite adapter is responsible for connecting the testing client to the configured Appwrite project.

---

# 20. Provided Mock Files

The task provides:

```text
mock-api.js
seed-data.json
```

These files are reference/mockup files supplied with the task.

They are **not used as the actual backend implementation**.

The real implementations are:

```text
Custom Backend → Flask + PostgreSQL

Managed Backend → Appwrite
```

The provided `index.html` remains the testing client as required by the task.

---

# 21. Security Considerations

The implementation focuses on the following security principles:

### Password hashing

Passwords are hashed rather than stored in plaintext.

### Authentication

Protected routes require valid authentication.

### Authorization

Authentication alone is not treated as permission to access arbitrary user data.

Resources are checked against the authenticated user's identity.

### User isolation

A user cannot access another user's profile or files by simply supplying another user's identifier.

### File ownership

Individual file requests verify that the authenticated user owns the requested file.

### Generic authentication errors

Failed login responses do not intentionally reveal whether an email address is registered.

### Rate limiting

Repeated failed login attempts are restricted.

### Environment secrets

Local secrets and database credentials are stored in `.env` and excluded from Git.

---

# 22. `.gitignore`

The repository excludes local and sensitive files such as:

```text
.env
venv/
__pycache__/
*.pyc
```

The `.env.example` file is committed so that another developer can see which environment variables are required.

---

# 23. Design Decisions

The implementation intentionally keeps the frontend simple because the task evaluates:

* Authentication correctness
* Authorization
* Session handling
* Data isolation
* File access control
* Security practices

rather than visual design.

The provided testing client is therefore used instead of creating a separate GUI.

---

# 24. What I Would Improve With More Time

Given additional development time, the following improvements could be made:

### Automated testing

Add a complete automated test suite covering:

* Registration
* Login
* Logout
* Invalid credentials
* Rate limiting
* Profile isolation
* File isolation
* Cross-user access attempts

### Stronger production security

For a production deployment, I would further strengthen:

* Secure cookie configuration
* CSRF protection where applicable
* Security headers
* Request validation
* More granular rate limiting
* Secret management
* HTTPS-only deployment

### Better file handling

The file subsystem could be extended with:

* File type validation
* File size limits
* Safer file naming
* Malware scanning
* Streaming downloads
* More granular permissions

### Deployment

The project could also be deployed with:

* A production PostgreSQL instance
* HTTPS
* Managed secret storage
* Production Appwrite configuration
* Proper monitoring and logging

---

# 25. Summary

This project implements the same core secure-login requirements using two different backend approaches:

```text
                 Secure Login System
                         │
              ┌──────────┴──────────┐
              │                     │
       Custom Backend         Appwrite Backend
              │                     │
           Flask                Appwrite
              │                     │
        PostgreSQL             Auth + Storage
              │                     │
              └──────────┬──────────┘
                         │
                  Provided Client
                     index.html
```

Both implementations are designed around the same security requirement:

> An authenticated user should only be able to access resources belonging to that user.

The project therefore emphasizes secure authentication, server-side session handling, password hashing, rate limiting, authorization checks, and strict user/file ownership validation.
