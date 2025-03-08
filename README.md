# Simple SSO

This is a mini project that I submitted to my professor in the web development course. I chose to create a simple SSO, but I didn’t focus on making it production-ready. So if you’re looking for a repository for a fully functional SSO, this repo is not the answer.

## Environment

I used Python 3.12 and Flask, SQLAlchemy as the backend, with the website being SSR (server-side rendering). In the future, it may not run as expected, so I left the requirements lock file like the previous mini project I did.

## Setup

Once you have your environment ready, create a .env file in the root of the repo to define values for the following two variables

```env
SECRET_KEY
SQLALCHEMY_DATABASE_URI
```

Create the database

```sh
python -m simple_sso --init-db
```

Run

```sh
# Add --dev to enable debug mode
python -m simple_sso
```

### Docker

Account: `admin`:`pass`

```sh
docker build -t simple_sso_image .
docker run -p 5000:5000 simple_sso_image
```

## Admin Rights

You can add admin rights directly in the database.

```sql
UPDATE user SET is_admin = TRUE WHERE username = 'your username'
```
