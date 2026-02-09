# Scribble — Notes API


---

## Quickstart

1. Copy the repository to your machine.
2. Create a Python virtual environment and activate it.
3. Create a `.env` file with the values described below.
4. Install dependencies.
5. Run the app with Uvicorn.

Example (Windows PowerShell):

```powershell
python -m venv .venv; .\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
# create .env (see Environment section)
uvicorn main:app --reload --port 9000
```

The API will be available at `http://127.0.0.1:9000`.

---

## Requirements

- Python 3.11+ (project uses Python 3.14 bytecode in caches but targets 3.11+ features)
- MongoDB connection (Atlas or local)
- See `requirements.txt` for the full list of Python dependencies (FastAPI, motor/pymongo async client, jose, passlib, etc.)

---

## Environment variables

Create a `.env` file at the project root with the following entries (example values are placeholders — do not commit secrets):

```dotenv
MONGO_URI=mongodb+srv://<username>:<password>@cluster0.example.mongodb.net/?retryWrites=true&w=majority
MONGO_DB_NAME=scribble
JWT_SECRET_KEY=your-very-secret-key
```

- `MONGO_URI` — MongoDB connection string (required).
- `MONGO_DB_NAME` — database name (required).
- `JWT_SECRET_KEY` — secret used to sign JWT tokens (recommended: long random secret). If not set the app will use `CHANGE_ME` by default — set a secure value for production.

---

## Run & Dev notes

The project entrypoint is `main.py`. It configures a lifespan handler that connects to MongoDB when the app starts and closes the connection when it stops.

Run in development with hot-reload:

```powershell
uvicorn main:app --reload --port 9000
```

---

## Authentication overview

- JWT-based access + refresh tokens.
- Access tokens expire after 15 minutes (see `src/auth/security.py`).
- Refresh tokens expire after 7 days.
- All protected endpoints require the `Authorization: Bearer <access_token>` header.
- Refresh tokens are stored server-side in the user's `refresh_tokens` array (revocation possible).

Security note for frontend developers: prefer storing the access token in memory and the refresh token in a secure, httpOnly cookie. If you must store tokens in localStorage, understand XSS risks.

---

## API Reference (endpoints)

Base URL (development): `http://127.0.0.1:9000`

Summary of routers registered in `main.py`:
- `GET /` — health/root
- `POST /auth/register` — register a user
- `POST /auth/login` — email/password login
- `GET /auth/me` — get current user (protected)
- `POST /auth/refresh` — rotate refresh token
- `POST /auth/logout` — revoke refresh token
- `POST /notes` — create a note (protected)
- `GET /notes` — list user's notes (protected)
- `GET /notes/{note_id}` — read a single note (protected)
- `PUT /notes/{note_id}` — update a note (protected)
- `DELETE /notes/{note_id}` — delete a note (protected)

Below each endpoint is documented with input, output, validation rules, and examples.

### GET /
- Purpose: Simple root/health check.
- Method: GET
- Request: none
- Response (200):

```json
{ "message": "Notes API running" }
```

---

### Auth endpoints

#### POST /auth/register
- Purpose: Create a new user and return tokens.
- Method: POST
- Request body (JSON): `UserCreate`
  - `email` (string, valid email)
  - `password` (string)
    - Password rules (validated by `src/auth/models/user.py`):
      - Minimum 8 characters
      - At least one uppercase letter
      - At least one lowercase letter
      - At least one digit
      - At least one special character from `@$!%*?&`

Example request body:

```json
{
  "email": "alice@example.com",
  "password": "Str0ng@Passw0rd"
}
```

- Response (200):

```json
{
  "user_id": "<user-id>",
  "access_token": "<jwt-access-token>",
  "refresh_token": "<jwt-refresh-token>"
}
```

- Errors:
  - 400 Bad Request with validation messages (Pydantic)
  - 400 if email already registered (ValueError handled by app)


#### POST /auth/login
- Purpose: Authenticate a user by email+password and return tokens.
- Method: POST
- Request body (JSON): `UserLogin` — `email`, `password`.
- Response (200): same shape as register (user_id, access_token, refresh_token).
- Errors:
  - 400 Invalid email/password (ValueError)


#### GET /auth/me
- Purpose: Return currently authenticated user's public profile.
- Method: GET
- Auth: requires `Authorization: Bearer <access_token>` header.
- Response (200): `UserResponse`

```json
{
  "id": "<user-id>",
  "email": "alice@example.com",
  "created_at": "2026-02-02T12:34:56.789Z"
}
```

- Errors:
  - 400 for invalid/expired token (ValueError)


#### POST /auth/refresh
- Purpose: Rotate a refresh token and issue a new pair of tokens.
- Method: POST
- Request body (JSON): `RefreshTokenRequest` — `{ "refresh_token": "<token>" }`.
- Response (200):

```json
{
  "access_token": "<new-access-token>",
  "refresh_token": "<new-refresh-token>"
}
```

- Errors:
  - 400 if token invalid, expired, or revoked.


#### POST /auth/logout
- Purpose: Revoke a refresh token (log out user on server-side).
- Method: POST
- Request body (JSON): `LogoutRequest` — `{ "refresh_token": "<token>" }`.
- Response (200): `{ "message": "user logged out successfully" }`.

---

### Notes endpoints (prefix `/notes`)
All `/notes` endpoints are protected and require the Authorization header.

Pydantic models (from `src/model/note.py`):
- `NoteCreate` — {
  - `title` (str) min_length=1, max_length=50
  - `content` (str) min_length=0, max_length=10000
}

- `NoteUpdate` — both fields optional (`title?: string`, `content?: string`) — partial updates supported.

- `NoteResponse` — {
  - `id` (string),
  - `title` (string),
  - `content` (string),
  - `user_id` (string)
}


#### POST /notes
- Purpose: Create a new note for the authenticated user.
- Method: POST
- Auth: `Authorization: Bearer <access_token>`
- Request body: `NoteCreate` (JSON)
- Response (200):

```json
{ "id": "<note-id>" }
```

- Errors:
  - 400 validation errors if `title` missing or too long/short


#### GET /notes
- Purpose: Return all notes belonging to the authenticated user.
- Method: GET
- Auth: `Authorization: Bearer <access_token>`
- Response (200): Array of `NoteResponse` objects.

Example:

```json
[
  { "id": "607c...", "title": "Shopping", "content": "Buy milk", "user_id": "60a1..." },
  { "id": "607c...", "title": "Todo", "content": "Finish report", "user_id": "60a1..." }
]
```


#### GET /notes/{note_id}
- Purpose: Return a single note by ID. Only the owner can access.
- Method: GET
- Auth: `Authorization: Bearer <access_token>`
- Response (200): `NoteResponse`
- Errors:
  - 404 if note not found
  - 403 if the note does not belong to the authenticated user


#### PUT /notes/{note_id}
- Purpose: Patch fields on an existing note.
- Method: PUT
- Auth: `Authorization: Bearer <access_token>`
- Request body: partial `NoteUpdate` — fields sent are applied.
- Response (200): `{ "message": "Note updated" }`
- Errors: 404 if note not found, 403 if not owner.


#### DELETE /notes/{note_id}
- Purpose: Delete the note.
- Method: DELETE
- Auth: `Authorization: Bearer <access_token>`
- Response (200): `{ "message": "Note deleted" }`
- Errors: 404 if note not found, 403 if not owner.

---

## Error handling

The code registers a ValueError handler in `main.py` that will return a structured JSON for ValueError exceptions with status 400. Standard HTTPExceptions are used for 403/404 and will return standard FastAPI error JSON.

Example error response for value errors:

```json
{
  "error": "Bad Request",
  "message": "<explanation>",
  "path": "<request-path>"
}
```

---

## Frontend developer guide

This section focuses on how a frontend app should integrate with the API.

1. Login / Register flow
   - POST `/auth/login` (or `/auth/register`) with email & password.
   - On success: store `access_token` in memory and `refresh_token` in a secure cookie (httpOnly) if possible.
   - Use the access token in every protected request:

```http
Authorization: Bearer <access_token>
```

2. Making protected calls (JavaScript fetch example)

```javascript
// attach access token stored in memory
const res = await fetch('/notes', {
  method: 'GET',
  headers: {
    'Authorization': `Bearer ${accessToken}`,
    'Content-Type': 'application/json'
  }
});
const data = await res.json();
```

3. Refreshing tokens
   - When you receive a 401/invalid token error, call `POST /auth/refresh` with the refresh token:

```javascript
await fetch('/auth/refresh', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ refresh_token: storedRefreshToken })
});
```

Replace tokens in your client after a successful refresh.

4. Logout
   - Call `POST /auth/logout` with the refresh token. Server will remove the refresh token from the user's list.

5. Example create-note (POST /notes) request

```javascript
const body = { title: 'My title', content: 'Note body' };
await fetch('/notes', {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${accessToken}`,
    'Content-Type': 'application/json'
  },
  body: JSON.stringify(body)
});
```

6. Validation feedback
   - Rely on returned 400 error body from FastAPI to display field-specific messages. Pydantic errors will include which field failed and why.

---

## Example cURL requests

Register:

```bash
curl -X POST http://127.0.0.1:9000/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"alice@example.com","password":"Str0ng@Passw0rd"}'
```

Login:

```bash
curl -X POST http://127.0.0.1:9000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"alice@example.com","password":"Str0ng@Passw0rd"}'
```

Create note (replace <token>):

```bash
curl -X POST http://127.0.0.1:9000/notes \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"title":"Buy milk","content":"2 liters"}'
```

---

## Developer notes & next steps

- implement:- returning HTTP 201 for creates (`/auth/register`, `/notes`) for semantic correctness.
- upgrading to :-storing refresh tokens in httpOnly cookies to avoid localStorage exposure.
- Add unit tests and CI to validate endpoints and auth flows.

## Performance & reliability

### Redis-powered caching
- Notes list and individual note responses are cached in Redis for 60 seconds (`src/web/note.py`). Every write (create/update/delete) invalidates the relevant cache keys so the next read hits Mongo again.
- Cache keys use `notes:user:<user_id>` for list results and `note:<note_id>:user:<user_id>` for single notes; invalidations keep stale data off the feed.

### Sliding-window rate limiting
- The same Redis instance backs the `SlidingWindowRateLimiter` middleware (`src/core/sliding_rate_limiter.py`) that fences off abuse on `AUTH_*` and `NOTES_*` routes. It keeps per-client sorted sets, trims expired entries, and enforces the limits configured in `src/core/rate_limit_config.py`.
- Frontends should handle 429 responses by reading the `Retry-After` header and delaying retries.

## Testing

Tests reuse the real Mongo/Redis connections but the fixtures in `tests/conftest.py` drop collections and flush Redis before/after each run so suites start with a blank slate.

Before running any tests in PowerShell, set the helper environment flag:

```powershell
$env:ENV = "test"
```

Now run the suites you need:

```powershell
pytest tests/unit
pytest tests/integration
pytest tests/api
```

- `tests/unit` covers serializers, utilities, and helpers.
- `tests/integration` exercises services (auth, caching, note persistence) against Mongo/Redis lifecycles.
- `tests/api` drives the FastAPI app via `httpx.AsyncClient` and the ASGI transport, covering the happy paths for auth and note CRUD while honoring the rate-limiter/caching hooks.
