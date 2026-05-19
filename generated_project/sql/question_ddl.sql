CREATE TABLE questions (
  id SERIAL PRIMARY KEY,
  prompt TEXT NOT NULL,
  difficulty INTEGER NOT NULL,
  category_id INTEGER NOT NULL,
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE answers (
  id SERIAL PRIMARY KEY, 
  question_id INTEGER NOT NULL,
  answer_text TEXT NOT NULL,
  is_correct BOOLEAN NOT NULL,
  display_order INTEGER NOT NULL,
  FOREIGN KEY (question_id) REFERENCES questions(id)
);

CREATE TABLE categories (
  id SERIAL PRIMARY KEY,
  name VARCHAR(255) NOT NULL
);

CREATE INDEX ON questions (category_id);

INSERT INTO categories (name) VALUES
  ('Fractions'),
  ('Algebra'),
  ('Geometry'),
  ('Statistics'),
  ('Logic');

INSERT INTO questions (prompt, difficulty, category_id) VALUES
  ('What is 1/2 + 1/4?', 1, 1),
  ('Simplify the fraction 6/12', 1, 1), 
  ('What is 3/5 - 1/10?', 2, 1),
  ('Convert 5/8 to a decimal', 2, 1),
  ('Multiply 1/3 and 2/5', 3, 1);

INSERT INTO answers (question_id, answer_text, is_correct, display_order) VALUES
  (1, '3/4', true, 1),
  (1, '5/8', false, 2), 
  (1, '1/2', false, 3),
  (1, '1/4', false, 4),
  (2, '1/2', true, 1),
  (2, '1/3', false, 2),
  (2, '1/4', false, 3),
  (2, '1/6', false, 4),
  (3, '1/2', true, 1),
  (3, '2/5', false, 2),
  (3, '1/10', false, 3),
  (3, '1/15', false, 4),
  (4, '0.625', true, 1),
  (4, '0.8', false, 2),
  (4, '0.5', false, 3),
  (4, '0.375', false, 4),
  (5, '1/15', true, 1),
  (5, '2/15', false, 2),
  (5, '3/15', false, 3),
  (5, '6/15', false, 4);