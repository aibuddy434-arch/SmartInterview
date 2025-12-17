import React, { useState, useEffect } from 'react';
import { X, Sparkles, Loader2, CheckCircle } from 'lucide-react';
import { Card, CardHeader, CardBody, CardFooter } from './ui/Card';
import Button from './ui/Button';
import Input from './ui/Input';
import Textarea from './ui/Textarea';
import Select from './ui/Select';
import Checkbox from './ui/Checkbox';
import toast from 'react-hot-toast';

const AIQuestionModal = ({ 
  isOpen, 
  onClose, 
  onQuestionsGenerated, 
  interviewService,
  initialData = {}
}) => {
  const [loading, setLoading] = useState(false);
  const [generatedQuestions, setGeneratedQuestions] = useState([]);
  const [formData, setFormData] = useState({
    job_role: initialData.job_role || '',
    job_description: initialData.job_description || '',
    difficulty: initialData.difficulty || 'medium',
    number_of_questions: initialData.number_of_questions || 5,
    focus_areas: initialData.focus || []
  });

  const focusAreas = interviewService.getFocusAreas();
  const difficultyLevels = interviewService.getDifficultyLevels();

  // Update form data when initialData changes
  useEffect(() => {
    if (isOpen && initialData) {
      setFormData({
        job_role: initialData.job_role || '',
        job_description: initialData.job_description || '',
        difficulty: initialData.difficulty || 'medium',
        number_of_questions: initialData.number_of_questions || 5,
        focus_areas: initialData.focus || []
      });
    }
  }, [isOpen, initialData]);

  const handleInputChange = (field, value) => {
    setFormData(prev => ({
      ...prev,
      [field]: value
    }));
  };

  const handleFocusAreaChange = (area, checked) => {
    setFormData(prev => ({
      ...prev,
      focus_areas: checked 
        ? [...prev.focus_areas, area]
        : prev.focus_areas.filter(f => f !== area)
    }));
  };

  const handleGenerateQuestions = async () => {
    if (!formData.job_role || !formData.job_description) {
      toast.error('Please fill in job role and description');
      return;
    }

    if (formData.focus_areas.length === 0) {
      toast.error('Please select at least one focus area');
      return;
    }

    setLoading(true);
    try {
      // Mock questions for testing since backend might not be available
      const baseQuestions = [
        `Tell me about your experience with ${formData.job_role} and how it relates to this position.`,
        `Describe a challenging project you've worked on in ${formData.job_role} and how you overcame obstacles.`,
        `How do you stay updated with the latest trends and technologies in ${formData.job_role}?`,
        `What's your approach to problem-solving in complex ${formData.job_role} scenarios?`,
        `How do you handle teamwork and collaboration in ${formData.job_role} projects?`,
        `What specific skills do you bring to this ${formData.job_role} position?`,
        `How do you prioritize tasks when working on multiple ${formData.job_role} projects?`,
        `Describe a time when you had to learn a new technology for a ${formData.job_role} project.`,
        `How do you ensure quality in your ${formData.job_role} work?`,
        `What's your experience with agile methodologies in ${formData.job_role} development?`
      ];
      
      // Generate the requested number of questions
      const requestedCount = parseInt(formData.number_of_questions) || 5;
      const mockQuestions = baseQuestions.slice(0, Math.min(requestedCount, baseQuestions.length));

      // Transform the mock questions into the expected format
      const questions = mockQuestions.map((q, index) => ({
        id: `ai_${Date.now()}_${index}`,
        text: q,
        type: 'ai_generated',
        order: index + 1,
        tags: ['technical', 'experience']
      }));

      setGeneratedQuestions(questions);
      toast.success(`Generated ${questions.length} AI questions successfully!`);
      
      // Automatically call onQuestionsGenerated when questions are generated
      console.log('Calling onQuestionsGenerated with:', questions);
      onQuestionsGenerated(questions);
      
    } catch (err) {
      console.error('Failed to generate questions:', err);
      toast.error(err.response?.data?.detail || 'Failed to generate AI questions');
    } finally {
      setLoading(false);
    }
  };


  const handleClose = () => {
    setGeneratedQuestions([]);
    setFormData({
      job_role: '',
      job_description: '',
      difficulty: 'medium',
      number_of_questions: 5,
      focus_areas: []
    });
    onClose();
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
      <div className="bg-white rounded-2xl shadow-2xl max-w-4xl w-full max-h-[90vh] overflow-hidden">
        <Card className="h-full flex flex-col">
          <CardHeader className="flex flex-row items-center justify-between border-b">
            <div className="flex items-center space-x-2">
              <Sparkles className="h-5 w-5 text-blue-600" />
              <h2 className="text-xl font-semibold text-gray-900">
                AI Question Generator
              </h2>
            </div>
            <Button
              variant="outline"
              size="sm"
              onClick={handleClose}
              className="p-2"
            >
              <X className="h-4 w-4" />
            </Button>
          </CardHeader>

          <CardBody className="flex-1 overflow-y-auto">
            <div className="space-y-6">
              {/* Form Section */}
              <div className="space-y-4">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Job Role *
                    </label>
                    <Input
                      value={formData.job_role}
                      onChange={(e) => handleInputChange('job_role', e.target.value)}
                      placeholder="e.g., Frontend Developer, Data Scientist"
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Difficulty Level
                    </label>
                    <Select
                      value={formData.difficulty}
                      onChange={(e) => handleInputChange('difficulty', e.target.value)}
                    >
                      {difficultyLevels.map((level) => (
                        <option key={level.value} value={level.value}>
                          {level.label}
                        </option>
                      ))}
                    </Select>
                  </div>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Job Description *
                  </label>
                  <Textarea
                    value={formData.job_description}
                    onChange={(e) => handleInputChange('job_description', e.target.value)}
                    placeholder="Describe the role, responsibilities, requirements, and expectations..."
                    rows={4}
                  />
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Number of Questions
                    </label>
                    <Input
                      type="number"
                      min="1"
                      max="20"
                      value={formData.number_of_questions}
                      onChange={(e) => handleInputChange('number_of_questions', e.target.value)}
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Focus Areas *
                    </label>
                    <div className="space-y-2">
                      {focusAreas.map((area) => (
                        <Checkbox
                          key={area.value}
                          checked={formData.focus_areas.includes(area.value)}
                          onChange={(checked) => handleFocusAreaChange(area.value, checked)}
                        >
                          <span className="text-sm">{area.label}</span>
                        </Checkbox>
                      ))}
                    </div>
                  </div>
                </div>
              </div>

              {/* Generated Questions Section */}
              {generatedQuestions.length > 0 && (
                <div className="space-y-4">
                  <div className="flex items-center space-x-2">
                    <CheckCircle className="h-5 w-5 text-green-600" />
                    <h3 className="text-lg font-medium text-gray-900">
                      Generated Questions ({generatedQuestions.length})
                    </h3>
                  </div>
                  
                  <div className="space-y-3 max-h-60 overflow-y-auto">
                    {generatedQuestions.map((question, index) => (
                      <div
                        key={question.id}
                        className="p-3 bg-gray-50 rounded-lg border"
                      >
                        <div className="flex items-start space-x-3">
                          <span className="flex-shrink-0 w-6 h-6 bg-blue-100 text-blue-600 rounded-full flex items-center justify-center text-sm font-medium">
                            {index + 1}
                          </span>
                          <p className="text-sm text-gray-800 flex-1">
                            {question.text}
                          </p>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          </CardBody>

          <CardFooter className="border-t bg-gray-50">
            <div className="flex justify-end space-x-3 w-full">
              <Button
                variant="outline"
                onClick={handleClose}
              >
                Cancel
              </Button>
              
              {generatedQuestions.length === 0 ? (
                <Button
                  onClick={handleGenerateQuestions}
                  loading={loading}
                  disabled={loading || !formData.job_role || !formData.job_description || formData.focus_areas.length === 0}
                >
                  {loading ? (
                    <>
                      <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                      Generating...
                    </>
                  ) : (
                    <>
                      <Sparkles className="h-4 w-4 mr-2" />
                      Generate Questions
                    </>
                  )}
                </Button>
              ) : (
                <Button
                  onClick={handleClose}
                >
                  <CheckCircle className="h-4 w-4 mr-2" />
                  Close
                </Button>
              )}
            </div>
          </CardFooter>
        </Card>
      </div>
    </div>
  );
};

export default AIQuestionModal;

