import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { Card, CardHeader, CardBody } from '../components/ui/Card';
import Button from '../components/ui/Button';
import { reportService } from '../services/reportService';
import toast from 'react-hot-toast';
import {
    ArrowLeft,
    User,
    Calendar,
    Clock,
    Award,
    MessageSquare,
    Briefcase,
    Mail,
    Phone,
    FileText,
    Printer,
    TrendingUp,
    Star,
    AlertCircle,
    CheckCircle,
    Target,
    ThumbsUp,
    ThumbsDown,
    Lightbulb,
    AlertTriangle
} from 'lucide-react';

const ReportDetail = () => {
    const { sessionId } = useParams();
    const navigate = useNavigate();
    const [report, setReport] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    useEffect(() => {
        loadReport();
    }, [sessionId]);

    const loadReport = async () => {
        try {
            setLoading(true);
            const data = await reportService.getReport(sessionId);
            setReport(data);
        } catch (err) {
            console.error('Failed to load report:', err);
            setError('Failed to load report');
            toast.error('Failed to load report');
        } finally {
            setLoading(false);
        }
    };

    const formatDate = (dateString) => {
        if (!dateString) return 'N/A';
        return new Date(dateString).toLocaleDateString('en-US', {
            year: 'numeric',
            month: 'long',
            day: 'numeric',
            hour: '2-digit',
            minute: '2-digit'
        });
    };

    const handlePrint = () => {
        window.print();
    };

    const getQualityBadge = (quality) => {
        const styles = {
            'Excellent': 'bg-green-100 text-green-800 border-green-200',
            'Good': 'bg-blue-100 text-blue-800 border-blue-200',
            'Needs Improvement': 'bg-yellow-100 text-yellow-800 border-yellow-200',
            'Poor': 'bg-red-100 text-red-800 border-red-200'
        };
        return styles[quality] || 'bg-gray-100 text-gray-800 border-gray-200';
    };

    if (loading) {
        return (
            <div className="flex items-center justify-center min-h-screen">
                <div className="text-center">
                    <div className="animate-spin rounded-full h-16 w-16 border-b-2 border-blue-600 mx-auto"></div>
                    <p className="mt-4 text-gray-600">Loading report...</p>
                </div>
            </div>
        );
    }

    if (error || !report) {
        return (
            <div className="flex flex-col items-center justify-center min-h-64">
                <AlertCircle className="h-16 w-16 text-red-500 mb-4" />
                <h2 className="text-xl font-semibold text-gray-900 mb-2">Error Loading Report</h2>
                <p className="text-gray-600 mb-4">{error || 'Report not found'}</p>
                <Button onClick={() => navigate('/reports')}>Back to Reports</Button>
            </div>
        );
    }

    const { candidate, interview, session, scores, responses, overall_rating, overall_assessment } = report;

    // Calculate average score
    const avgScore = scores ? Math.round((scores.communication + scores.technical + scores.confidence + scores.completeness) / 4) : 0;

    return (
        <div className="space-y-6 pb-12">
            {/* Header with navigation */}
            <div className="flex items-center justify-between print:hidden">
                <Button
                    onClick={() => navigate('/reports')}
                    variant="outline"
                    className="flex items-center"
                >
                    <ArrowLeft className="h-4 w-4 mr-2" />
                    Back to Reports
                </Button>
                <div className="flex space-x-2">
                    <Button onClick={handlePrint} variant="outline">
                        <Printer className="h-4 w-4 mr-2" />
                        Print Report
                    </Button>
                </div>
            </div>

            {/* Professional Report Header */}
            <div className="bg-gradient-to-r from-blue-600 to-purple-600 rounded-xl p-8 text-white shadow-lg">
                <div className="flex items-center justify-between">
                    <div>
                        <p className="text-blue-100 text-sm uppercase tracking-wide mb-2">Interview Report</p>
                        <h1 className="text-3xl font-bold mb-2">{candidate?.name}</h1>
                        <p className="text-blue-100">{interview?.job_role}</p>
                    </div>
                    <div className="text-right">
                        <div className={`inline-block px-6 py-3 rounded-lg ${overall_rating === 'Excellent' ? 'bg-green-500' :
                            overall_rating === 'Good' ? 'bg-blue-500' :
                                overall_rating === 'Satisfactory' ? 'bg-yellow-500' :
                                    overall_rating === 'Needs Improvement' ? 'bg-orange-500' :
                                        'bg-red-500'
                            }`}>
                            <p className="text-white/80 text-sm">Overall Rating</p>
                            <p className="text-2xl font-bold">{overall_rating}</p>
                        </div>
                    </div>
                </div>
            </div>

            {/* Hiring Recommendation Banner */}
            {overall_assessment && (
                <div className={`rounded-xl p-6 border-2 ${overall_assessment.recommendation === 'Strongly Recommend' ? 'bg-green-50 border-green-300' :
                    overall_assessment.recommendation === 'Recommend with Reservations' ? 'bg-blue-50 border-blue-300' :
                        overall_assessment.recommendation === 'Consider for Junior Role' ? 'bg-yellow-50 border-yellow-300' :
                            'bg-red-50 border-red-300'
                    }`}>
                    <div className="flex items-center justify-between">
                        <div className="flex items-center">
                            {overall_assessment.recommendation === 'Strongly Recommend' ? (
                                <ThumbsUp className="h-10 w-10 text-green-600 mr-4" />
                            ) : overall_assessment.recommendation === 'Not Recommended' ? (
                                <ThumbsDown className="h-10 w-10 text-red-600 mr-4" />
                            ) : (
                                <Star className="h-10 w-10 text-yellow-600 mr-4" />
                            )}
                            <div>
                                <h3 className="text-xl font-bold text-gray-900">{overall_assessment.recommendation}</h3>
                                <p className="text-gray-600">{overall_assessment.recommendation_detail}</p>
                            </div>
                        </div>
                        <div className="text-right">
                            <p className="text-sm text-gray-500">Average Score</p>
                            <p className={`text-3xl font-bold ${reportService.getScoreColor(overall_assessment.average_score)}`}>
                                {overall_assessment.average_score}%
                            </p>
                        </div>
                    </div>
                </div>
            )}

            {/* Main Content Grid */}
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                {/* Left Column - Candidate & Session Info */}
                <div className="space-y-6">
                    {/* Candidate Info Card */}
                    <Card>
                        <CardHeader>
                            <h2 className="text-lg font-semibold flex items-center">
                                <User className="h-5 w-5 mr-2 text-blue-500" />
                                Candidate Information
                            </h2>
                        </CardHeader>
                        <CardBody className="space-y-4">
                            <div className="flex items-center">
                                <div className="h-16 w-16 bg-gradient-to-br from-blue-500 to-purple-600 rounded-full flex items-center justify-center text-white font-bold text-2xl mr-4">
                                    {candidate?.name?.charAt(0)?.toUpperCase() || '?'}
                                </div>
                                <div>
                                    <p className="font-semibold text-gray-900">{candidate?.name}</p>
                                    <p className="text-sm text-gray-500">Candidate</p>
                                </div>
                            </div>

                            <div className="space-y-2 pt-2 border-t">
                                <div className="flex items-center text-gray-600">
                                    <Mail className="h-4 w-4 mr-3 text-gray-400" />
                                    <span className="text-sm">{candidate?.email}</span>
                                </div>
                                {candidate?.phone && (
                                    <div className="flex items-center text-gray-600">
                                        <Phone className="h-4 w-4 mr-3 text-gray-400" />
                                        <span className="text-sm">{candidate?.phone}</span>
                                    </div>
                                )}
                                {candidate?.resume_path && (
                                    <div className="flex items-center text-gray-600 mt-2 pt-2 border-t">
                                        <FileText className="h-4 w-4 mr-3 text-purple-500" />
                                        <a
                                            href={`${process.env.REACT_APP_API_URL || 'http://localhost:8000'}/${candidate.resume_path}`}
                                            target="_blank"
                                            rel="noopener noreferrer"
                                            className="text-sm text-blue-600 hover:text-blue-800 hover:underline flex items-center"
                                        >
                                            View Resume
                                            <svg className="h-3 w-3 ml-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
                                            </svg>
                                        </a>
                                    </div>
                                )}
                            </div>
                        </CardBody>
                    </Card>

                    {/* Strengths & Improvements */}
                    {overall_assessment && (
                        <Card>
                            <CardHeader>
                                <h2 className="text-lg font-semibold flex items-center">
                                    <Lightbulb className="h-5 w-5 mr-2 text-yellow-500" />
                                    Key Insights
                                </h2>
                            </CardHeader>
                            <CardBody className="space-y-4">
                                {/* Strengths */}
                                <div>
                                    <h4 className="text-sm font-semibold text-green-700 mb-2 flex items-center">
                                        <CheckCircle className="h-4 w-4 mr-1" />
                                        Strengths
                                    </h4>
                                    <ul className="space-y-1">
                                        {overall_assessment.strengths?.map((strength, i) => (
                                            <li key={i} className="text-sm text-gray-600 flex items-start">
                                                <span className="inline-block w-1.5 h-1.5 bg-green-500 rounded-full mt-1.5 mr-2"></span>
                                                {strength}
                                            </li>
                                        ))}
                                    </ul>
                                </div>

                                {/* Areas for Improvement */}
                                <div className="pt-3 border-t">
                                    <h4 className="text-sm font-semibold text-orange-700 mb-2 flex items-center">
                                        <AlertTriangle className="h-4 w-4 mr-1" />
                                        Areas for Improvement
                                    </h4>
                                    <ul className="space-y-1">
                                        {overall_assessment.areas_for_improvement?.map((area, i) => (
                                            <li key={i} className="text-sm text-gray-600 flex items-start">
                                                <span className="inline-block w-1.5 h-1.5 bg-orange-500 rounded-full mt-1.5 mr-2"></span>
                                                {area}
                                            </li>
                                        ))}
                                    </ul>
                                </div>
                            </CardBody>
                        </Card>
                    )}

                    {/* Session Details Card */}
                    <Card>
                        <CardHeader>
                            <h2 className="text-lg font-semibold flex items-center">
                                <Calendar className="h-5 w-5 mr-2 text-green-500" />
                                Session Details
                            </h2>
                        </CardHeader>
                        <CardBody className="space-y-3">
                            <div className="flex items-center justify-between">
                                <span className="text-gray-500">Job Role</span>
                                <span className="font-medium">{interview?.job_role}</span>
                            </div>
                            <div className="flex items-center justify-between">
                                <span className="text-gray-500">Interview Type</span>
                                <span className="font-medium capitalize">{interview?.interview_type}</span>
                            </div>
                            <div className="flex items-center justify-between">
                                <span className="text-gray-500">Difficulty</span>
                                <span className="font-medium capitalize">{interview?.difficulty}</span>
                            </div>
                            {interview?.focus_areas && interview.focus_areas.length > 0 && (
                                <div className="pt-2">
                                    <span className="text-gray-500 text-sm">Focus Areas:</span>
                                    <div className="flex flex-wrap gap-1 mt-1">
                                        {interview.focus_areas.map((area, i) => (
                                            <span key={i} className="px-2 py-0.5 bg-blue-100 text-blue-700 text-xs rounded-full">
                                                {area}
                                            </span>
                                        ))}
                                    </div>
                                </div>
                            )}
                            <div className="border-t pt-3 mt-3">
                                <div className="flex items-center justify-between mb-2">
                                    <span className="text-gray-500">Duration</span>
                                    <span className="font-medium">{reportService.formatDuration(session?.duration_minutes)}</span>
                                </div>
                                <div className="flex items-center justify-between">
                                    <span className="text-gray-500">Questions</span>
                                    <span className="font-medium">{session?.answered_questions} / {session?.total_questions}</span>
                                </div>
                            </div>
                        </CardBody>
                    </Card>
                </div>

                {/* Middle & Right Column - Scores & Responses */}
                <div className="lg:col-span-2 space-y-6">
                    {/* Score Cards */}
                    <Card>
                        <CardHeader>
                            <h2 className="text-lg font-semibold flex items-center">
                                <Award className="h-5 w-5 mr-2 text-yellow-500" />
                                Performance Scores
                            </h2>
                        </CardHeader>
                        <CardBody>
                            <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
                                {/* Communication Score */}
                                <div className="text-center p-4 bg-blue-50 rounded-lg">
                                    <MessageSquare className="h-8 w-8 text-blue-500 mx-auto mb-2" />
                                    <p className="text-sm text-gray-500">Communication</p>
                                    <p className={`text-2xl font-bold ${reportService.getScoreColor(scores?.communication)}`}>
                                        {Math.round(scores?.communication || 0)}%
                                    </p>
                                </div>

                                {/* Technical Score */}
                                <div className="text-center p-4 bg-purple-50 rounded-lg">
                                    <Target className="h-8 w-8 text-purple-500 mx-auto mb-2" />
                                    <p className="text-sm text-gray-500">Technical</p>
                                    <p className={`text-2xl font-bold ${reportService.getScoreColor(scores?.technical)}`}>
                                        {Math.round(scores?.technical || 0)}%
                                    </p>
                                </div>

                                {/* Confidence Score */}
                                <div className="text-center p-4 bg-green-50 rounded-lg">
                                    <TrendingUp className="h-8 w-8 text-green-500 mx-auto mb-2" />
                                    <p className="text-sm text-gray-500">Confidence</p>
                                    <p className={`text-2xl font-bold ${reportService.getScoreColor(scores?.confidence)}`}>
                                        {Math.round(scores?.confidence || 0)}%
                                    </p>
                                </div>

                                {/* Completeness Score */}
                                <div className="text-center p-4 bg-orange-50 rounded-lg">
                                    <CheckCircle className="h-8 w-8 text-orange-500 mx-auto mb-2" />
                                    <p className="text-sm text-gray-500">Completeness</p>
                                    <p className={`text-2xl font-bold ${reportService.getScoreColor(scores?.completeness)}`}>
                                        {Math.round(scores?.completeness || 0)}%
                                    </p>
                                </div>
                            </div>

                            {/* Overall Score Bar */}
                            <div className="bg-gray-100 rounded-lg p-4">
                                <div className="flex items-center justify-between mb-2">
                                    <span className="font-semibold text-gray-700">Overall Score</span>
                                    <span className={`text-2xl font-bold ${reportService.getScoreColor(avgScore)}`}>
                                        {avgScore}%
                                    </span>
                                </div>
                                <div className="w-full bg-gray-200 rounded-full h-4">
                                    <div
                                        className={`h-4 rounded-full transition-all duration-500 ${avgScore >= 80 ? 'bg-green-500' :
                                            avgScore >= 60 ? 'bg-blue-500' :
                                                avgScore >= 40 ? 'bg-yellow-500' :
                                                    'bg-red-500'
                                            }`}
                                        style={{ width: `${avgScore}%` }}
                                    />
                                </div>
                            </div>
                        </CardBody>
                    </Card>

                    {/* Detailed Question Responses */}
                    <Card>
                        <CardHeader>
                            <h2 className="text-lg font-semibold flex items-center">
                                <FileText className="h-5 w-5 mr-2 text-indigo-500" />
                                Question & Answer Analysis
                            </h2>
                        </CardHeader>
                        <CardBody className="space-y-6">
                            {responses && responses.length > 0 ? (
                                responses.map((response, index) => (
                                    <div key={index} className="border rounded-lg overflow-hidden">
                                        {/* Question Header */}
                                        <div className="bg-gradient-to-r from-blue-50 to-indigo-50 p-4 border-b">
                                            <div className="flex items-start justify-between">
                                                <div className="flex items-start">
                                                    <span className="inline-flex items-center justify-center h-8 w-8 rounded-full bg-blue-600 text-white font-semibold text-sm mr-3 flex-shrink-0">
                                                        Q{response.question_number}
                                                    </span>
                                                    <div>
                                                        <p className="font-medium text-gray-900">{response.question_text || `Question ${response.question_number}`}</p>
                                                        {response.question_tags && response.question_tags.length > 0 && (
                                                            <div className="flex flex-wrap gap-1 mt-2">
                                                                {response.question_tags.map((tag, i) => (
                                                                    <span key={i} className="px-2 py-0.5 bg-blue-100 text-blue-700 text-xs rounded-full">
                                                                        {tag}
                                                                    </span>
                                                                ))}
                                                            </div>
                                                        )}
                                                    </div>
                                                </div>
                                                <span className={`px-3 py-1 rounded-full text-xs font-medium border ${getQualityBadge(response.answer_quality)}`}>
                                                    {response.answer_quality}
                                                </span>
                                            </div>
                                        </div>

                                        {/* Candidate Answer */}
                                        <div className="p-4">
                                            <h4 className="text-sm font-semibold text-gray-700 mb-2">Candidate's Answer:</h4>
                                            <div className="bg-gray-50 rounded-lg p-4 border-l-4 border-blue-400">
                                                <p className="text-gray-700 leading-relaxed italic">
                                                    "{response.candidate_answer || '[No response recorded]'}"
                                                </p>
                                            </div>

                                            {/* Key Points */}
                                            {response.key_points && response.key_points.length > 0 && (
                                                <div className="mt-4">
                                                    <h4 className="text-sm font-semibold text-green-700 mb-2 flex items-center">
                                                        <CheckCircle className="h-4 w-4 mr-1" />
                                                        Key Points Mentioned:
                                                    </h4>
                                                    <ul className="space-y-1">
                                                        {response.key_points.map((point, i) => (
                                                            <li key={i} className="text-sm text-gray-600 flex items-start">
                                                                <span className="inline-block w-1.5 h-1.5 bg-green-500 rounded-full mt-1.5 mr-2 flex-shrink-0"></span>
                                                                {point}
                                                            </li>
                                                        ))}
                                                    </ul>
                                                </div>
                                            )}

                                            {/* Improvement Areas */}
                                            {response.improvement_areas && response.improvement_areas.length > 0 && (
                                                <div className="mt-4 bg-yellow-50 rounded-lg p-3 border border-yellow-200">
                                                    <h4 className="text-sm font-semibold text-yellow-800 mb-2 flex items-center">
                                                        <Lightbulb className="h-4 w-4 mr-1" />
                                                        Suggestions for Improvement:
                                                    </h4>
                                                    <ul className="space-y-1">
                                                        {response.improvement_areas.map((area, i) => (
                                                            <li key={i} className="text-sm text-yellow-800 flex items-start">
                                                                <span className="inline-block w-1.5 h-1.5 bg-yellow-500 rounded-full mt-1.5 mr-2 flex-shrink-0"></span>
                                                                {area}
                                                            </li>
                                                        ))}
                                                    </ul>
                                                </div>
                                            )}
                                        </div>
                                    </div>
                                ))
                            ) : (
                                <div className="text-center py-8 text-gray-500">
                                    <MessageSquare className="h-12 w-12 mx-auto mb-4 text-gray-300" />
                                    <p>No responses recorded</p>
                                </div>
                            )}
                        </CardBody>
                    </Card>
                </div>
            </div>

            {/* Footer with timestamp */}
            <div className="text-center text-sm text-gray-400 pt-6 border-t">
                <p>Report generated on {formatDate(report.generated_at)}</p>
                <p className="mt-1">Session ID: {sessionId}</p>
            </div>
        </div>
    );
};

export default ReportDetail;
