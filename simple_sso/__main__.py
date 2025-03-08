from sys import argv
from sqlalchemy import create_engine

from .db_schema import Base
from .config import SQLALCHEMY_DATABASE_URI
from .simple_sso import app

def init_db() -> None:
    engine = create_engine(SQLALCHEMY_DATABASE_URI, echo=True)
    Base.metadata.create_all(engine)

if __name__ == "__main__":
    if "--init-db" in argv:
        init_db()
    elif "--dev" in argv:
        app.run(debug=True)
    elif "--help" in argv:
        print(f"python {argv[0]} [option]")
        print("              -- Run flask app")
        print("    --dev     -- Run flask app in localhost and development mode")
        print("    --init-db -- Create database to URL")
        print("    --help    -- Show this message")
    else:
        app.run(host="0.0.0.0", port=5000)

