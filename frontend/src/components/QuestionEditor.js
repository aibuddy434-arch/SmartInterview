import React, { useState } from 'react';
import { Trash2, Edit3, Save, X } from 'lucide-react';
import Button from './ui/Button';
import Textarea from './ui/Textarea';

const QuestionEditor = ({ questions, onQuestionsChange, onRemoveQuestion }) => {
  const [editingId, setEditingId] = useState(null);
  const [editText, setEditText] = useState('');

  const handleEdit = (question) => {
    setEditingId(question.id);
    setEditText(question.text);
  };

  const handleSave = (questionId) => {
    const updatedQuestions = questions.map(q => 
      q.id === questionId ? { ...q, text: editText } : q
    );
    onQuestionsChange(updatedQuestions);
    setEditingId(null);
    setEditText('');
  };

  const handleCancel = () => {
    setEditingId(null);
    setEditText('');
  };

  const handleRemove = (questionId) => {
    if (onRemoveQuestion) {
      onRemoveQuestion(questionId);
    } else {
      const updatedQuestions = questions.filter(q => q.id !== questionId);
      onQuestionsChange(updatedQuestions);
    }
  };

  if (questions.length === 0) {
    return (
      <div className="text-center py-8 text-gray-500">
        <p>No questions added yet. Use the "AI Generate Questions" button to get started.</p>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      <h3 className="text-lg font-medium text-gray-900">Interview Questions</h3>
      
      {questions.map((question, index) => (
        <div key={question.id} className="border border-gray-200 rounded-lg p-4 bg-gray-50">
          {editingId === question.id ? (
            <div className="space-y-3">
              <Textarea
                value={editText}
                onChange={(e) => setEditText(e.target.value)}
                rows={3}
                placeholder="Enter question text..."
                className="w-full"
              />
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-2">
                  <span className="text-sm text-gray-500">
                    Question {index + 1} • {question.type === 'ai_generated' ? 'AI Generated' : 'Manual'}
                  </span>
                  {question.tags && Array.isArray(question.tags) && question.tags.length > 0 && (
                    <div className="flex space-x-1">
                      {question.tags.map((tag, tagIndex) => (
                        <span
                          key={tagIndex}
                          className="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-blue-100 text-blue-800"
                        >
                          {typeof tag === 'string' ? tag : JSON.stringify(tag)}
                        </span>
                      ))}
                    </div>
                  )}
                </div>
                <div className="flex space-x-2">
                  <Button
                    size="sm"
                    variant="success"
                    onClick={() => handleSave(question.id)}
                  >
                    <Save className="h-4 w-4 mr-1" />
                    Save
                  </Button>
                  <Button
                    size="sm"
                    variant="outline"
                    onClick={handleCancel}
                  >
                    <X className="h-4 w-4 mr-1" />
                    Cancel
                  </Button>
                </div>
              </div>
            </div>
          ) : (
            <div className="space-y-3">
              <p className="text-gray-900">{question.text}</p>
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-2">
                  <span className="text-sm text-gray-500">
                    Question {index + 1} • {question.type === 'ai_generated' ? 'AI Generated' : 'Manual'}
                  </span>
                  {question.tags && Array.isArray(question.tags) && question.tags.length > 0 && (
                    <div className="flex space-x-1">
                      {question.tags.map((tag, tagIndex) => (
                        <span
                          key={tagIndex}
                          className="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-blue-100 text-blue-800"
                        >
                          {typeof tag === 'string' ? tag : JSON.stringify(tag)}
                        </span>
                      ))}
                    </div>
                  )}
                </div>
                <div className="flex space-x-2">
                  <Button
                    size="sm"
                    variant="outline"
                    onClick={() => handleEdit(question)}
                  >
                    <Edit3 className="h-4 w-4 mr-1" />
                    Edit
                  </Button>
                  <Button
                    size="sm"
                    variant="danger"
                    onClick={() => handleRemove(question.id)}
                  >
                    <Trash2 className="h-4 w-4 mr-1" />
                    Remove
                  </Button>
                </div>
              </div>
            </div>
          )}
        </div>
      ))}
    </div>
  );
};

export default QuestionEditor;


