import React from 'react';
import { Users } from 'lucide-react';

const CandidateList = () => {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Candidates</h1>
        <p className="mt-1 text-sm text-gray-500">
          View and manage all candidate profiles
        </p>
      </div>

      <div className="card">
        <div className="text-center py-12">
          <Users className="mx-auto h-12 w-12 text-gray-400" />
          <h3 className="mt-2 text-sm font-medium text-gray-900">Candidate List</h3>
          <p className="mt-1 text-sm text-gray-500">
            This page will display all candidates with their profiles and interview history.
          </p>
          <div className="mt-6">
            <button className="btn-primary inline-flex items-center">
              <Users className="h-4 w-4 mr-2" />
              Coming Soon
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default CandidateList;


