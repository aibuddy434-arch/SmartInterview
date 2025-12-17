import React from 'react';
import { Calendar } from 'lucide-react';

const InterviewList = () => {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Interviews</h1>
        <p className="mt-1 text-sm text-gray-500">
          Manage and monitor all interview sessions
        </p>
      </div>

      <div className="card">
        <div className="text-center py-12">
          <Calendar className="mx-auto h-12 w-12 text-gray-400" />
          <h3 className="mt-2 text-sm font-medium text-gray-900">Interview List</h3>
          <p className="mt-1 text-sm text-gray-500">
            This page will display all interviews with filtering and management options.
          </p>
          <div className="mt-6">
            <button className="btn-primary inline-flex items-center">
              <Calendar className="h-4 w-4 mr-2" />
              Coming Soon
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default InterviewList;


