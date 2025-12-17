import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useForm } from 'react-hook-form';
import { Sparkles, Save, Copy, Check, X, Edit3 } from 'lucide-react';
import toast from 'react-hot-toast';
import { interviewService } from '../services/interviewService';
import { Card, CardHeader, CardBody, CardFooter } from '../components/ui/Card';
import Button from '../components/ui/Button';
import Input from '../components/ui/Input';
import Textarea from '../components/ui/Textarea';
import Select from '../components/ui/Select';
import Checkbox from '../components/ui/Checkbox';
import QuestionEditor from '../components/QuestionEditor';
import AIQuestionModal from '../components/AIQuestionModal';

// AI Question Preview Item Component
const AIQuestionPreviewItem = ({ question, index, onEdit }) => {
  const [isEditing, setIsEditing] = useState(false);
  const [editText, setEditText] = useState(question.text);

  const handleSave = () => {
    onEdit(question.id, editText);
    setIsEditing(false);
  };

  const handleCancel = () => {
    setEditText(question.text);
    setIsEditing(false);
  };

  return (
    <div className="p-4 bg-white rounded-lg border border-gray-200 shadow-sm">
      <div className="flex items-start space-x-3">
        <span className="flex-shrink-0 w-6 h-6 bg-blue-100 text-blue-600 rounded-full flex items-center justify-center text-sm font-medium">
          {index + 1}
        </span>
        <div className="flex-1 min-w-0">
          {isEditing ? (
            <div className="space-y-3">
              <Textarea
                value={editText}
                onChange={(e) => setEditText(e.target.value)}
                rows={3}
                className="w-full"
                placeholder="Enter question text..."
              />
              <div className="flex space-x-2">
                <Button
                  size="sm"
                  onClick={handleSave}
                  className="bg-green-600 hover:bg-green-700"
                >
                  <Check className="h-4 w-4 mr-1" />
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
          ) : (
            <div className="space-y-2">
              <p className="text-sm text-gray-800">{question.text}</p>
              <div className="flex items-center justify-between">
                <span className="text-xs text-gray-500">
                  AI Generated Question
                </span>
                <Button
                  size="sm"
                  variant="outline"
                  onClick={() => setIsEditing(true)}
                >
                  <Edit3 className="h-4 w-4 mr-1" />
                  Edit
                </Button>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

const InterviewCreator = () => {
  const navigate = useNavigate();
  const [showAIModal, setShowAIModal] = useState(false);
  const [questions, setQuestions] = useState([]);
  const [loading, setLoading] = useState(false);
  const [copied, setCopied] = useState(false);
  const [createdConfig, setCreatedConfig] = useState(null);
  const [aiGeneratedQuestions, setAiGeneratedQuestions] = useState([]);
  const [showQuestionPreview, setShowQuestionPreview] = useState(false);

  const {
    register,
    handleSubmit,
    formState: { errors },
    watch,
    reset
  } = useForm({
    defaultValues: {
      job_role: '',
      job_description: '',
      interview_type: 'general',
      difficulty: 'medium',
      focus: [],
      time_limit: '',
      avatar: 'professional',
      voice: 'neutral',
      number_of_questions: 5
    }
  });

  const watchedValues = watch();

  const handleQuestionsChange = (newQuestions) => {
    setQuestions(newQuestions);
  };

  const handleAIQuestionsGenerated = (aiQuestions) => {
    console.log('AI Questions Generated:', aiQuestions);
    setAiGeneratedQuestions(aiQuestions);
    setShowQuestionPreview(true);
    toast.success(`Generated ${aiQuestions.length} AI questions! Review and edit them before adding to your interview.`);
  };

  const handleRemoveQuestion = (questionId) => {
    const updatedQuestions = questions.filter(q => q.id !== questionId);
    setQuestions(updatedQuestions);
  };

  const handleAcceptAIQuestions = () => {
    setQuestions(aiGeneratedQuestions);
    setAiGeneratedQuestions([]);
    setShowQuestionPreview(false);
    toast.success('AI questions added to your interview!');
  };

  const handleRejectAIQuestions = () => {
    setAiGeneratedQuestions([]);
    setShowQuestionPreview(false);
  };

  const handleRegenerateAIQuestions = () => {
    setShowAIModal(true);
  };

  const handleEditAIQuestion = (questionId, newText) => {
    setAiGeneratedQuestions(prev => 
      prev.map(q => q.id === questionId ? { ...q, text: newText } : q)
    );
  };

  const handleCopyLink = async () => {
    if (createdConfig) {
      const link = `${window.location.origin}/interview/${createdConfig.id}`;
      try {
        await navigator.clipboard.writeText(link);
        setCopied(true);
        toast.success('Interview link copied to clipboard!');
        setTimeout(() => setCopied(false), 2000);
      } catch (err) {
        toast.error('Failed to copy link');
      }
    }
  };

  const onSubmit = async (data) => {
    if (questions.length === 0) {
      toast.error('Please add at least one question before saving');
      return;
    }

    setLoading(true);
    try {
      const configData = {
        ...data,
        questions: questions,
        number_of_questions: questions.length
      };

      const created = await interviewService.createInterviewConfig(configData);
      setCreatedConfig(created);
      
      toast.success('Interview configuration created successfully!');
      
      // Reset form
      reset();
      setQuestions([]);
      
    } catch (err) {
      console.error('Failed to create interview config:', err);
      toast.error(err.response?.data?.detail || 'Failed to create interview configuration');
    } finally {
      setLoading(false);
    }
  };

  const focusAreas = interviewService.getFocusAreas();
  const difficultyLevels = interviewService.getDifficultyLevels();
  const interviewTypes = interviewService.getInterviewTypes();
  const avatars = interviewService.getAvailableAvatars();
  const voices = interviewService.getAvailableVoices();

  if (createdConfig) {
    return (
      <div className="space-y-6">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Interview Created Successfully!</h1>
          <p className="mt-1 text-sm text-gray-500">
            Your interview configuration has been saved. Share the link below with candidates.
          </p>
        </div>

        <Card>
          <CardHeader>
            <h3 className="text-lg font-medium text-gray-900">Interview Details</h3>
          </CardHeader>
          <CardBody>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700">Job Role</label>
                <p className="mt-1 text-sm text-gray-900">{createdConfig.job_role}</p>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700">Interview Type</label>
                <p className="mt-1 text-sm text-gray-900">
                  {interviewTypes.find(t => t.value === createdConfig.interview_type)?.label}
                </p>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700">Difficulty</label>
                <p className="mt-1 text-sm text-gray-900">
                  {difficultyLevels.find(d => d.value === createdConfig.difficulty)?.label}
                </p>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700">Questions</label>
                <p className="mt-1 text-sm text-gray-900">{createdConfig.questions.length} questions</p>
              </div>
            </div>
          </CardBody>
          <CardFooter>
            <div className="flex items-center space-x-3 w-full">
              <Input
                value={`${window.location.origin}${createdConfig.shareable_link}`}
                readOnly
                className="flex-1"
              />
              <Button
                onClick={handleCopyLink}
                variant={copied ? "success" : "outline"}
              >
                {copied ? <Check className="h-4 w-4 mr-2" /> : <Copy className="h-4 w-4 mr-2" />}
                {copied ? 'Copied!' : 'Copy Link'}
              </Button>
            </div>
          </CardFooter>
        </Card>

        <div className="flex space-x-3">
          <Button
            onClick={() => {
              setCreatedConfig(null);
              navigate('/admin/interviews');
            }}
            variant="outline"
          >
            View All Interviews
          </Button>
          <Button
            onClick={() => {
              setCreatedConfig(null);
              reset();
              setQuestions([]);
            }}
          >
            Create Another Interview
          </Button>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Create Interview</h1>
        <p className="mt-1 text-sm text-gray-500">
          Set up a new interview session with custom configurations and AI-generated questions
        </p>
      </div>

      <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
        <Card>
          <CardHeader>
            <h3 className="text-lg font-medium text-gray-900">Basic Information</h3>
          </CardHeader>
          <CardBody className="space-y-6">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Job Role *
                </label>
                <Input
                  {...register('job_role', { required: 'Job role is required' })}
                  placeholder="e.g., Frontend Developer, Data Scientist"
                  error={!!errors.job_role}
                />
                {errors.job_role && (
                  <p className="mt-1 text-sm text-red-600">{errors.job_role.message}</p>
                )}
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Interview Type
                </label>
                <Select
                  {...register('interview_type')}
                >
                  {interviewTypes.map((type) => (
                    <option key={type.value} value={type.value}>
                      {type.label}
                    </option>
                  ))}
                </Select>
                <p className="mt-1 text-sm text-gray-500">
                  {interviewTypes.find(t => t.value === watchedValues.interview_type)?.description}
                </p>
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Job Description *
              </label>
              <Textarea
                {...register('job_description', { required: 'Job description is required' })}
                placeholder="Describe the role, responsibilities, requirements, and expectations..."
                rows={4}
                error={!!errors.job_description}
              />
              {errors.job_description && (
                <p className="mt-1 text-sm text-red-600">{errors.job_description.message}</p>
              )}
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Difficulty Level
                </label>
                <Select
                  {...register('difficulty')}
                >
                  {difficultyLevels.map((level) => (
                    <option key={level.value} value={level.value}>
                      {level.label}
                    </option>
                  ))}
                </Select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Time Limit (minutes)
                </label>
                <Input
                  {...register('time_limit', { 
                    min: { value: 5, message: 'Minimum 5 minutes' },
                    max: { value: 180, message: 'Maximum 180 minutes' }
                  })}
                  type="number"
                  placeholder="Optional"
                  min="5"
                  max="180"
                  error={!!errors.time_limit}
                />
                {errors.time_limit && (
                  <p className="mt-1 text-sm text-red-600">{errors.time_limit.message}</p>
                )}
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Number of Questions
                </label>
                <Input
                  {...register('number_of_questions', { 
                    required: 'Number of questions is required',
                    min: { value: 1, message: 'Minimum 1 question' },
                    max: { value: 20, message: 'Maximum 20 questions' }
                  })}
                  type="number"
                  min="1"
                  max="20"
                  error={!!errors.number_of_questions}
                />
                {errors.number_of_questions && (
                  <p className="mt-1 text-sm text-red-600">{errors.number_of_questions.message}</p>
                )}
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Focus Areas *
              </label>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
                {focusAreas.map((area) => (
                  <Checkbox
                    key={area.value}
                    {...register('focus', { 
                      required: 'Please select at least one focus area',
                      validate: (value) => value.length > 0 || 'Please select at least one focus area'
                    })}
                    value={area.value}
                  >
                    <span className="text-sm">{area.label}</span>
                  </Checkbox>
                ))}
              </div>
              {errors.focus && (
                <p className="mt-1 text-sm text-red-600">{errors.focus.message}</p>
              )}
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  AI Avatar
                </label>
                <Select
                  {...register('avatar')}
                >
                  {avatars.map((avatar) => (
                    <option key={avatar.value} value={avatar.value}>
                      {avatar.label}
                    </option>
                  ))}
                </Select>
                <p className="mt-1 text-sm text-gray-500">
                  {avatars.find(a => a.value === watchedValues.avatar)?.description}
                </p>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Voice
                </label>
                <Select
                  {...register('voice')}
                >
                  {voices.map((voice) => (
                    <option key={voice.value} value={voice.value}>
                      {voice.label}
                    </option>
                  ))}
                </Select>
                <p className="mt-1 text-sm text-gray-500">
                  {voices.find(v => v.value === watchedValues.voice)?.description}
                </p>
              </div>
            </div>
          </CardBody>
        </Card>

        <Card>
          <CardHeader>
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-3">
                <h3 className="text-lg font-medium text-gray-900">Interview Questions</h3>
                {questions.length > 0 && (
                  <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800">
                    {questions.length} questions added
                  </span>
                )}
              </div>
              <Button
                type="button"
                onClick={() => setShowAIModal(true)}
                variant="outline"
              >
                <Sparkles className="h-4 w-4 mr-2" />
                AI Generate Questions
              </Button>
            </div>
          </CardHeader>
          <CardBody>
            <QuestionEditor
              questions={questions}
              onQuestionsChange={handleQuestionsChange}
              onRemoveQuestion={handleRemoveQuestion}
            />
          </CardBody>
        </Card>

        {/* AI Generated Questions Preview */}
        {console.log('Preview state:', { showQuestionPreview, aiGeneratedQuestions: aiGeneratedQuestions.length })}
        {showQuestionPreview && aiGeneratedQuestions.length > 0 && (
          <Card className="border-blue-200 bg-blue-50">
            <CardHeader>
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-2">
                  <Sparkles className="h-5 w-5 text-blue-600" />
                  <h3 className="text-lg font-medium text-gray-900">
                    AI Generated Questions Preview
                  </h3>
                  <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
                    {aiGeneratedQuestions.length} questions
                  </span>
                </div>
                <div className="flex space-x-2">
                  <Button
                    type="button"
                    variant="outline"
                    size="sm"
                    onClick={handleRegenerateAIQuestions}
                  >
                    <Sparkles className="h-4 w-4 mr-1" />
                    Regenerate
                  </Button>
                  <Button
                    type="button"
                    variant="outline"
                    size="sm"
                    onClick={handleRejectAIQuestions}
                  >
                    <X className="h-4 w-4 mr-1" />
                    Reject
                  </Button>
                </div>
              </div>
              <p className="text-sm text-gray-600 mt-2">
                Review and edit the AI-generated questions below. Click "Accept Questions" to add them to your interview.
              </p>
            </CardHeader>
            <CardBody>
              <div className="space-y-3 max-h-96 overflow-y-auto">
                {aiGeneratedQuestions.map((question, index) => (
                  <AIQuestionPreviewItem
                    key={question.id}
                    question={question}
                    index={index}
                    onEdit={handleEditAIQuestion}
                  />
                ))}
              </div>
              <div className="mt-6 flex justify-end space-x-3">
                <Button
                  type="button"
                  variant="outline"
                  onClick={handleRejectAIQuestions}
                >
                  Cancel
                </Button>
                <Button
                  type="button"
                  onClick={handleAcceptAIQuestions}
                  className="bg-blue-600 hover:bg-blue-700"
                >
                  <Check className="h-4 w-4 mr-2" />
                  Accept Questions
                </Button>
              </div>
            </CardBody>
          </Card>
        )}

        <div className="flex justify-end space-x-3">
          <Button
            type="button"
            variant="outline"
            onClick={() => navigate('/admin/interviews')}
          >
            Cancel
          </Button>
          <div className="flex flex-col items-end">
            <Button
              type="submit"
              loading={loading}
              disabled={loading || questions.length === 0}
            >
              <Save className="h-4 w-4 mr-2" />
              {questions.length > 0 
                ? `Create Interview (${questions.length} questions)` 
                : 'Create Interview'
              }
            </Button>
            {questions.length === 0 && aiGeneratedQuestions.length > 0 && (
              <p className="mt-2 text-sm text-amber-600 font-medium">
                ⚠️ Please click "Accept Questions" above to add the AI-generated questions first
              </p>
            )}
            {questions.length === 0 && aiGeneratedQuestions.length === 0 && (
              <p className="mt-2 text-sm text-gray-500">
                Add questions manually or generate them with AI
              </p>
            )}
          </div>
        </div>
      </form>

      <AIQuestionModal
        isOpen={showAIModal}
        onClose={() => setShowAIModal(false)}
        onQuestionsGenerated={handleAIQuestionsGenerated}
        interviewService={interviewService}
        initialData={watchedValues}
      />
    </div>
  );
};

export default InterviewCreator;
