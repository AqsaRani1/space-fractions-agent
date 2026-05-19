```python
import pytest
from space_fractions.components.QuestionComponent import QuestionComponent

class TestQuestionComponent:
    """Test suite for the QuestionComponent"""

    def test_get_all_questions(self):
        """Test that get_all_questions returns a list of questions"""
        component = QuestionComponent()
        questions = component.get_all_questions()
        assert isinstance(questions, list)

    def test_random_question_format(self):
        """Test that a random question has the correct format"""
        component = QuestionComponent()
        question = component.get_random_question()
        assert isinstance(question, dict)
        assert 'id' in question
        assert 'prompt' in question
        assert 'options' in question
        assert isinstance(question['id'], int)
        assert isinstance(question['prompt'], str)
        assert isinstance(question['options'], list)

    def test_correct_answer(self):
        """Test that the correct answer is marked as correct"""
        component = QuestionComponent()
        question = component.get_random_question()
        correct_index = question['options'].index(question['correct_answer'])
        assert component.check_answer(question, correct_index)['is_correct']

    def test_wrong_answer(self):
        """Test that a wrong answer is marked as incorrect"""
        component = QuestionComponent()
        question = component.get_random_question()
        wrong_index = [i for i in range(len(question['options'])) if i != question['options'].index(question['correct_answer'])][0]
        assert not component.check_answer(question, wrong_index)['is_correct']

    def test_required_fields(self):
        """Test that a question has the required fields"""
        component = QuestionComponent()
        question = component.get_random_question()
        assert 'id' in question
        assert 'prompt' in question
        assert 'options' in question
```