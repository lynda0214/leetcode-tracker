import React, { useState, useEffect } from 'react';
import Leaderboard from './components/Leaderboard';

function App() {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetch('./stats.json')
      .then(res => {
        if (!res.ok) throw new Error("Failed to load stats");
        return res.json();
      })
      .then(data => {
        setData(data);
        setLoading(false);
      })
      .catch(err => {
        console.error(err);
        setError(err.message);
        setLoading(false);
      });
  }, []);

  return (
    <div className="min-h-screen bg-[#1a1a1a] flex flex-col items-center py-12">
      <header className="mb-12 text-center">
        <h1 className="text-4xl font-extrabold text-transparent bg-clip-text bg-gradient-to-r from-orange-400 to-yellow-600 mb-2">
          # 1337
        </h1>
        <p className="text-gray-400">You can do better than Ray.</p>
      </header>
      
      <main className="w-full">
        <Leaderboard data={data} loading={loading} error={error} />
      </main>
      
      <footer className="mt-auto py-8 text-center text-gray-600 text-sm">
        <p>Updates every 6 hours • Built with ❤️</p>
        {data && data.last_updated && (
          <p className="mt-2 text-xs text-gray-500">
            Last updated: {new Date(data.last_updated).toLocaleString()}
          </p>
        )}
      </footer>
    </div>
  );
}

export default App;
