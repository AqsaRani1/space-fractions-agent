const { Pool } = require('pg');

/** 
 * Main service for QuestionComponent
 * Responsible for question management and data persistence
 */
class QuestionService {
  constructor() {
    this.pool = new Pool({
      user: 'postgres',
      host: 'localhost',
      database: 'spacefract',
      password: 'changeme',
      port: 5432,
    });
  }

  /**
   * Retrieves a question from the database
   * @param {number} id - The ID of the question to retrieve
   * @returns {Promise<Object>} The question data
   */
  async getQuestion(id) {
    try {
      const result = await this.pool.query('SELECT * FROM questions WHERE id = $1', [id]);
      return result.rows[0];
    } catch (err) {
      console.error('Error retrieving question:', err);
      throw err;
    }
  }

  /**
   * Creates a new question in the database
   * @param {Object} questionData - The question data to create
   * @returns {Promise<number>} The ID of the created question
   */
  async createQuestion(questionData) {
    try {
      const { text, answer, difficulty } = questionData;
      const result = await this.pool.query('INSERT INTO questions (text, answer, difficulty) VALUES ($1, $2, $3) RETURNING id', [text, answer, difficulty]);
      return result.rows[0].id;
    } catch (err) {
      console.error('Error creating question:', err);
      throw err;
    }
  }

  /**
   * Updates an existing question in the database
   * @param {number} id - The ID of the question to update
   * @param {Object} questionData - The updated question data
   * @returns {Promise<void>}
   */
  async updateQuestion(id, questionData) {
    try {
      const { text, answer, difficulty } = questionData;
      await this.pool.query('UPDATE questions SET text = $1, answer = $2, difficulty = $3 WHERE id = $4', [text, answer, difficulty, id]);
    } catch (err) {
      console.error('Error updating question:', err);
      throw err;
    }
  }

  /**
   * Deletes a question from the database
   * @param {number} id - The ID of the question to delete
   * @returns {Promise<void>}
   */
  async deleteQuestion(id) {
    try {
      await this.pool.query('DELETE FROM questions WHERE id = $1', [id]);
    } catch (err) {
      console.error('Error deleting question:', err);
      throw err;
    }
  }
}

module.exports = QuestionService;