import React, { useState, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { Card, CardHeader, CardBody } from '../components/ui/Card';
import Button from '../components/ui/Button';
import { reportService } from '../services/reportService';
import { interviewService } from '../services/interviewService';
import toast from 'react-hot-toast';
import {
    FileText,
    User,
    Calendar,
    Clock,
    Award,
    Eye,
    ChevronRight,
    AlertCircle,
    TrendingUp,
    Briefcase
} from 'lucide-react';

const InterviewReports = () => {
    const navigate = useNavigate();
    const [sessions, setSessions] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    useEffect(() => {
        loadCompletedSessions();
    }, []);

    const loadCompletedSessions = async () => {
        try {
            setLoading(true);
            const data = await reportService.getCompletedSessions();
            setSessions(data.sessions || []);
        } catch (err) {
            console.error('Failed to load sessions:', err);
            setError('Failed to load interview reports');
            toast.error('Failed to load reports');
        } finally {
            setLoading(false);
        }
    };

    const formatDate = (dateString) => {
        if (!dateString) return 'N/A';
        // Backend returns UTC time, convert to local
        let date = new Date(dateString);
        // If the date string doesn't have timezone info, assume it's UTC
        if (!dateString.includes('Z') && !dateString.includes('+')) {
            date = new Date(dateString + 'Z');
        }
        return date.toLocaleString('en-US', {
            year: 'numeric',
            month: 'short',
            day: 'numeric',
            hour: '2-digit',
            minute: '2-digit',
            hour12: true
        });
    };

    const calculateDuration = (startTime, endTime) => {
        if (!startTime || !endTime) return 'N/A';
        const start = new Date(startTime);
        const end = new Date(endTime);
        const diffMinutes = Math.round((end - start) / 60000);
        return reportService.formatDuration(diffMinutes);
    };

    if (loading) {
        return (
            <div className="flex items-center justify-center min-h-64">
                <div className="animate-spin rounded-full h-16 w-16 border-b-2 border-blue-600"></div>
            </div>
        );
    }

    if (error) {
        return (
            <div className="flex flex-col items-center justify-center min-h-64">
                <AlertCircle className="h-16 w-16 text-red-500 mb-4" />
                <h2 className="text-xl font-semibold text-gray-900 mb-2">Error Loading Reports</h2>
                <p className="text-gray-600 mb-4">{error}</p>
                <Button onClick={loadCompletedSessions}>Try Again</Button>
            </div>
        );
    }

    return (
        <div className="space-y-6">
            {/* Header */}
            <div className="flex justify-between items-center">
                <div>
                    <h1 className="text-2xl font-bold text-gray-900">Interview Reports</h1>
                    <p className="mt-1 text-sm text-gray-500">
                        View detailed reports and analysis for completed interviews
                    </p>
                </div>
                <div className="flex items-center space-x-2 text-sm text-gray-500">
                    <FileText className="h-5 w-5" />
                    <span>{sessions.length} completed interviews</span>
                </div>
            </div>

            {/* Stats Overview */}
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                <Card>
                    <CardBody className="flex items-center space-x-4">
                        <div className="p-3 bg-blue-100 rounded-lg">
                            <FileText className="h-6 w-6 text-blue-600" />
                        </div>
                        <div>
                            <p className="text-sm text-gray-500">Total Reports</p>
                            <p className="text-2xl font-bold text-gray-900">{sessions.length}</p>
                        </div>
                    </CardBody>
                </Card>

                <Card>
                    <CardBody className="flex items-center space-x-4">
                        <div className="p-3 bg-green-100 rounded-lg">
                            <User className="h-6 w-6 text-green-600" />
                        </div>
                        <div>
                            <p className="text-sm text-gray-500">Candidates Interviewed</p>
                            <p className="text-2xl font-bold text-gray-900">
                                {new Set(sessions.map(s => s.candidate_email)).size}
                            </p>
                        </div>
                    </CardBody>
                </Card>

                <Card>
                    <CardBody className="flex items-center space-x-4">
                        <div className="p-3 bg-purple-100 rounded-lg">
                            <Briefcase className="h-6 w-6 text-purple-600" />
                        </div>
                        <div>
                            <p className="text-sm text-gray-500">Job Roles</p>
                            <p className="text-2xl font-bold text-gray-900">
                                {new Set(sessions.map(s => s.job_role)).size}
                            </p>
                        </div>
                    </CardBody>
                </Card>

                <Card>
                    <CardBody className="flex items-center space-x-4">
                        <div className="p-3 bg-orange-100 rounded-lg">
                            <TrendingUp className="h-6 w-6 text-orange-600" />
                        </div>
                        <div>
                            <p className="text-sm text-gray-500">Avg. Score</p>
                            <p className="text-2xl font-bold text-gray-900">
                                {sessions.length > 0 && sessions.some(s => s.score)
                                    ? `${Math.round(sessions.filter(s => s.score).reduce((acc, s) => acc + s.score, 0) / sessions.filter(s => s.score).length)}%`
                                    : 'N/A'
                                }
                            </p>
                        </div>
                    </CardBody>
                </Card>
            </div>

            {/* Reports List */}
            {sessions.length === 0 ? (
                <Card>
                    <CardBody className="text-center py-12">
                        <FileText className="h-16 w-16 text-gray-300 mx-auto mb-4" />
                        <h3 className="text-lg font-medium text-gray-900 mb-2">No Interview Reports Yet</h3>
                        <p className="text-gray-500 mb-6">
                            Completed interviews will appear here with detailed reports and analysis.
                        </p>
                        <Link to="/interviews/create">
                            <Button>Create New Interview</Button>
                        </Link>
                    </CardBody>
                </Card>
            ) : (
                <div className="space-y-4">
                    {sessions.map((session) => (
                        <Card key={session.session_id} className="hover:shadow-md transition-shadow">
                            <CardBody>
                                <div className="flex items-center justify-between">
                                    <div className="flex-1">
                                        <div className="flex items-center space-x-4">
                                            <div className="h-12 w-12 bg-gradient-to-br from-blue-500 to-purple-600 rounded-full flex items-center justify-center text-white font-bold text-lg">
                                                {session.candidate_name?.charAt(0)?.toUpperCase() || '?'}
                                            </div>
                                            <div>
                                                <h3 className="text-lg font-semibold text-gray-900">
                                                    {session.candidate_name}
                                                </h3>
                                                <p className="text-sm text-gray-500">{session.candidate_email}</p>
                                            </div>
                                        </div>

                                        <div className="mt-4 grid grid-cols-2 md:grid-cols-4 gap-4">
                                            <div className="flex items-center text-sm text-gray-600">
                                                <Briefcase className="h-4 w-4 mr-2 text-gray-400" />
                                                <span>{session.job_role}</span>
                                            </div>
                                            <div className="flex items-center text-sm text-gray-600">
                                                <Calendar className="h-4 w-4 mr-2 text-gray-400" />
                                                <span>{formatDate(session.end_time)}</span>
                                            </div>
                                            <div className="flex items-center text-sm text-gray-600">
                                                <Clock className="h-4 w-4 mr-2 text-gray-400" />
                                                <span>{calculateDuration(session.start_time, session.end_time)}</span>
                                            </div>
                                            <div className="flex items-center text-sm">
                                                <Award className="h-4 w-4 mr-2 text-gray-400" />
                                                <span className={`font-medium ${session.score ? reportService.getScoreColor(session.score) : 'text-gray-400'}`}>
                                                    {session.score ? `${Math.round(session.score)}%` : 'Pending'}
                                                </span>
                                            </div>
                                        </div>
                                    </div>

                                    <div className="ml-6">
                                        <Button
                                            onClick={() => navigate(`/reports/${session.session_id}`)}
                                            variant="outline"
                                            className="flex items-center"
                                        >
                                            <Eye className="h-4 w-4 mr-2" />
                                            View Report
                                            <ChevronRight className="h-4 w-4 ml-1" />
                                        </Button>
                                    </div>
                                </div>
                            </CardBody>
                        </Card>
                    ))}
                </div>
            )}
        </div>
    );
};

export default InterviewReports;
