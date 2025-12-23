import React, { useState } from 'react';

const Leaderboard = ({ data, loading, error }) => {

  if (loading) return <div className="p-10 text-center text-gray-400">Loading stats...</div>;
  if (error) return <div className="p-10 text-center text-red-500">Error: {error}</div>;

  if (!data || !data.users) return <div className="p-10 text-center">No data available</div>;

  // Convert users object to array and sort
  const usersList = Object.entries(data.users).map(([username, info]) => {
    const weeklySolved = info.total_solved - info.weekly_baseline;
    return {
      username,
      ...info,
      weeklySolved: Math.max(0, weeklySolved) // Ensure no negative
    };
  }).sort((a, b) => b.weeklySolved - a.weeklySolved || b.total_solved - a.total_solved);

  return (
    <div className="max-w-4xl mx-auto p-6">
      <div className="bg-leetcode-dark rounded-xl shadow-2xl overflow-hidden border border-leetcode-gray">
        <div className="p-6 border-b border-leetcode-gray flex justify-between items-center bg-[#2f2f2f]">
          <div>
            <h2 className="text-2xl font-bold text-white">Weekly Leaderboard</h2>
            <p className="text-gray-400 text-sm mt-1">
              Week of {new Date(data.week_start).toLocaleDateString()}
            </p>
          </div>
          <div className="text-leetcode-yellow text-sm font-semibold px-3 py-1 bg-yellow-900/30 rounded-full border border-yellow-700/50">
            Season 1
          </div>
        </div>

        <div className="divide-y divide-leetcode-gray">
          {usersList.map((user, index) => (
            <UserRow key={user.username} user={user} rank={index + 1} />
          ))}
        </div>
      </div>
    </div>
  );
};

const UserRow = ({ user, rank }) => {
  const [expanded, setExpanded] = useState(false);

  return (
    <div className="group transition-colors hover:bg-[#323232]">
      <div 
        className="p-4 flex items-center cursor-pointer"
        onClick={() => setExpanded(!expanded)}
      >
        <div className={`w-8 h-8 flex items-center justify-center rounded-lg font-bold mr-4 ${
          rank === 1 ? 'bg-yellow-500/20 text-yellow-500' :
          rank === 2 ? 'bg-gray-400/20 text-gray-400' :
          rank === 3 ? 'bg-orange-700/20 text-orange-600' :
          'text-gray-500'
        }`}>
          {rank}
        </div>

        <img 
          src={new URL(`../assets/${user.username}.png`, import.meta.url).href}
          alt={user.username}
          className="w-10 h-10 rounded-full mr-4 object-cover border-2 border-[#444]"
          onError={(e) => {
            e.target.onerror = null; 
            e.target.style.display = 'none'; // Fallback: hide if missing
          }}
        />
        
        <div className="flex-1">
          <h3 className="text-lg font-medium text-white flex items-center hover:text-blue-400 transition-colors">
            <a href={`https://leetcode.com/${user.username}`} target="_blank" rel="noreferrer" onClick={e => e.stopPropagation()}>
              {user.username}
            </a>
          </h3>
          <p className="text-xs text-gray-500">Total Solved: {user.total_solved}</p>
        </div>

        <div className="text-right">
          <div className="text-2xl font-bold text-green-400">
            +{user.weeklySolved}
          </div>
          <div className="text-xs text-gray-500 uppercase tracking-wider">
            Problems
          </div>
        </div>

        <div className={`ml-4 text-gray-400 transform transition-transform ${expanded ? 'rotate-180' : ''}`}>
          ▼
        </div>
      </div>

      {expanded && (
        <div className="bg-[#222] p-4 pl-16 border-t border-[#333]">
          <h4 className="text-xs text-gray-500 uppercase tracking-wider mb-3">Recently Solved</h4>
          {user.history && user.history.length > 0 ? (
            <ul className="space-y-2">
              {user.history.map(problem => (
                <li key={problem.id} className="flex items-center text-sm">
                  <span className="w-1.5 h-1.5 bg-green-500 rounded-full mr-2"></span>
                  <a 
                    href={`https://leetcode.com/problems/${problem.titleSlug}`}
                    target="_blank" 
                    rel="noreferrer"
                    className="text-gray-300 hover:text-green-400 transition-colors"
                  >
                    {problem.title}
                  </a>
                  <span className="text-gray-600 text-xs ml-auto">
                    {new Date(problem.timestamp * 1000).toLocaleDateString()}
                  </span>
                </li>
              ))}
            </ul>
          ) : (
             <p className="text-sm text-gray-600 italic">No detailed history available for this week yet.</p>
          )}
        </div>
      )}
    </div>
  );
};

export default Leaderboard;
