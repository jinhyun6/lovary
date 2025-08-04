-- Add diary_photos table
CREATE TABLE IF NOT EXISTS diary_photos (
    id SERIAL PRIMARY KEY,
    diary_id INTEGER NOT NULL REFERENCES diaries(id) ON DELETE CASCADE,
    photo_url VARCHAR NOT NULL,
    original_filename VARCHAR,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Add index on diary_id for faster queries
CREATE INDEX idx_diary_photos_diary_id ON diary_photos(diary_id);