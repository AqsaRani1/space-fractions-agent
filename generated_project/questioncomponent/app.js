const { Pool } = require('pg');

/**
 * Main service for QuestionComponent
 * Responsible for question management and data persistence
 */
class QuestionService {
  constructor() {
    this.pool = new Pool({
      host: 'localhost',
      port: 5432,
      database: 'postgres',
      user: 'postgres',
      password: 'password'
    });
  }

  async getQuestions() {
    // FR-1: Get questions
    try {
      const result = await this.pool.query('SELECT * FROM questions');
      return result.rows;
    } catch (err) {
      console.error('Error getting questions:', err);
      throw err;
    }
  }

  async createQuestion(question) {
    // FR-2: Create new question
    try {
      const { text, difficulty, answer } = question;
      const result = await this.pool.query(
        'INSERT INTO questions (text, difficulty, answer) VALUES ($1, $2, $3) RETURNING *',
        [text, difficulty, answer]
      );
      return result.rows[0];
    } catch (err) {
      console.error('Error creating question:', err);
      throw err;
    }
  }

  async updateQuestion(id, updates) {
    // FR-3: Update existing question
    try {
      const { text, difficulty, answer } = updates;
      const result = await this.pool.query(
        'UPDATE questions SET text = $1, difficulty = $2, answer = $3 WHERE id = $4 RETURNING *',
        [text, difficulty, answer, id]
      );
      return result.rows[0];
    } catch (err) {
      console.error('Error updating question:', err);
      throw err;
    }
  }

  async deleteQuestion(id) {
    // FR-4: Delete question
    try {
      const result = await this.pool.query('DELETE FROM questions WHERE id = $1 RETURNING *', [id]);
      return result.rows[0];
    } catch (err) {
      console.error('Error deleting question:', err);
      throw err;
    }
  }
}

module.exports = QuestionService;