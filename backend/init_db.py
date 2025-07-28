from app.db.database import Base, engine
from app.models import User, Diary

print("Creating database tables...")
Base.metadata.create_all(bind=engine)
print("Database tables created successfully!")