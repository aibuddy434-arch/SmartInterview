import React from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import {
  Calendar,
  Users,
  BarChart3,
  Plus,
  Clock,
  TrendingUp,
  UserCheck,
  FileText
} from 'lucide-react';

const Dashboard = () => {
  const { user } = useAuth();

  const stats = [
    {
      name: 'Total Interviews',
      value: '12',
      change: '+2.5%',
      changeType: 'positive',
      icon: Calendar,
    },
    {
      name: 'Active Candidates',
      value: '45',
      change: '+12.3%',
      changeType: 'positive',
      icon: Users,
    },
    {
      name: 'Completion Rate',
      value: '87%',
      change: '+5.2%',
      changeType: 'positive',
      icon: TrendingUp,
    },
    {
      name: 'Avg. Duration',
      value: '25m',
      change: '-2.1%',
      changeType: 'negative',
      icon: Clock,
    },
  ];

  const quickActions = [
    {
      name: 'Create Interview',
      description: 'Set up a new interview session',
      href: '/interviews/create',
      icon: Plus,
      color: 'bg-primary-500',
    },
    {
      name: 'View Candidates',
      description: 'Manage candidate profiles',
      href: '/candidates',
      icon: UserCheck,
      color: 'bg-green-500',
    },
    {
      name: 'Interview Reports',
      description: 'View detailed interview analysis',
      href: '/reports',
      icon: BarChart3,
      color: 'bg-purple-500',
    },
    {
      name: 'Session History',
      description: 'Review past interviews',
      href: '/interviews',
      icon: FileText,
      color: 'bg-orange-500',
    },
  ];

  const recentActivity = [
    {
      id: 1,
      type: 'interview_created',
      message: 'New interview "Frontend Developer" created',
      time: '2 hours ago',
      user: 'John Doe',
    },
    {
      id: 2,
      type: 'candidate_joined',
      message: 'Sarah Wilson joined "Backend Engineer" interview',
      time: '4 hours ago',
      user: 'Sarah Wilson',
    },
    {
      id: 3,
      type: 'interview_completed',
      message: 'Interview "Product Manager" completed by Mike Johnson',
      time: '1 day ago',
      user: 'Mike Johnson',
    },
  ];

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Dashboard</h1>
        <p className="mt-1 text-sm text-gray-500">
          Welcome back, {user?.full_name}. Here's what's happening with your interviews.
        </p>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 gap-5 sm:grid-cols-2 lg:grid-cols-4">
        {stats.map((item) => (
          <div key={item.name} className="card">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <item.icon className="h-8 w-8 text-gray-400" />
              </div>
              <div className="ml-5 w-0 flex-1">
                <dl>
                  <dt className="text-sm font-medium text-gray-500 truncate">
                    {item.name}
                  </dt>
                  <dd className="flex items-baseline">
                    <div className="text-2xl font-semibold text-gray-900">
                      {item.value}
                    </div>
                    <div className={`ml-2 flex items-baseline text-sm font-semibold ${item.changeType === 'positive' ? 'text-green-600' : 'text-red-600'
                      }`}>
                      {item.change}
                    </div>
                  </dd>
                </dl>
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Quick Actions */}
      <div>
        <h2 className="text-lg font-medium text-gray-900 mb-4">Quick Actions</h2>
        <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
          {quickActions.map((action) => (
            <Link
              key={action.name}
              to={action.href}
              className="card hover:shadow-md transition-shadow duration-200"
            >
              <div className="flex items-center">
                <div className={`flex-shrink-0 ${action.color} rounded-lg p-3`}>
                  <action.icon className="h-6 w-6 text-white" />
                </div>
                <div className="ml-4">
                  <h3 className="text-sm font-medium text-gray-900">
                    {action.name}
                  </h3>
                  <p className="text-sm text-gray-500">
                    {action.description}
                  </p>
                </div>
              </div>
            </Link>
          ))}
        </div>
      </div>

      {/* Recent Activity */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="card">
          <h2 className="text-lg font-medium text-gray-900 mb-4">Recent Activity</h2>
          <div className="space-y-4">
            {recentActivity.map((activity) => (
              <div key={activity.id} className="flex items-start space-x-3">
                <div className="flex-shrink-0">
                  <div className="h-8 w-8 rounded-full bg-gray-100 flex items-center justify-center">
                    <span className="text-sm font-medium text-gray-600">
                      {activity.user.charAt(0)}
                    </span>
                  </div>
                </div>
                <div className="flex-1 min-w-0">
                  <p className="text-sm text-gray-900">{activity.message}</p>
                  <p className="text-sm text-gray-500">
                    {activity.time} • {activity.user}
                  </p>
                </div>
              </div>
            ))}
          </div>
        </div>

        <div className="card">
          <h2 className="text-lg font-medium text-gray-900 mb-4">Upcoming Interviews</h2>
          <div className="space-y-4">
            <div className="text-center py-8">
              <Calendar className="mx-auto h-12 w-12 text-gray-400" />
              <h3 className="mt-2 text-sm font-medium text-gray-900">No upcoming interviews</h3>
              <p className="mt-1 text-sm text-gray-500">
                Get started by creating a new interview session.
              </p>
              <div className="mt-6">
                <Link
                  to="/interviews/create"
                  className="btn-primary inline-flex items-center"
                >
                  <Plus className="h-4 w-4 mr-2" />
                  Create Interview
                </Link>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;


