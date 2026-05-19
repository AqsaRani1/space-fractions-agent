CREATE TABLE games (
  id SERIAL PRIMARY KEY,
  game_state JSONB NOT NULL,
  student_id INTEGER NOT NULL,
  created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX ON games (student_id);
CREATE INDEX ON games (created_at);
CREATE INDEX ON games (updated_at);

COMMENT ON TABLE games IS 'Stores game data and metadata';
COMMENT ON COLUMN games.id IS 'Unique identifier for the game';
COMMENT ON COLUMN games.game_state IS 'JSON-encoded game state data';
COMMENT ON COLUMN games.student_id IS 'Foreign key reference to the student who played the game';
COMMENT ON COLUMN games.created_at IS 'Timestamp of when the game was created';
COMMENT ON COLUMN games.updated_at IS 'Timestamp of when the game was last updated';

CREATE TABLE scores (
  id SERIAL PRIMARY KEY,
  game_id INTEGER NOT NULL REFERENCES games(id),
  student_id INTEGER NOT NULL,
  final_score NUMERIC(10,2) NOT NULL,
  completed_at TIMESTAMP WITH TIME ZONE NOT NULL
);

CREATE INDEX ON scores (game_id);
CREATE INDEX ON scores (student_id);
CREATE INDEX ON scores (completed_at);

COMMENT ON TABLE scores IS 'Stores final scores for completed games';
COMMENT ON COLUMN scores.id IS 'Unique identifier for the score record';
COMMENT ON COLUMN scores.game_id IS 'Foreign key reference to the game';
COMMENT ON COLUMN scores.student_id IS 'Foreign key reference to the student who played the game';
COMMENT ON COLUMN scores.final_score IS 'The final score for the completed game';
COMMENT ON COLUMN scores.completed_at IS 'Timestamp of when the game was completed';