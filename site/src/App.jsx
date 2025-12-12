import React from 'react';
import Leaderboard from './components/Leaderboard';

function App() {
  return (
    <div className="min-h-screen bg-[#1a1a1a] flex flex-col items-center py-12">
      <header className="mb-12 text-center">
        <h1 className="text-4xl font-extrabold text-transparent bg-clip-text bg-gradient-to-r from-orange-400 to-yellow-600 mb-2">
          # 1337
        </h1>
        <p className="text-gray-400">You can do better than Ray.</p>
      </header>
      
      <main className="w-full">
        <Leaderboard />
      </main>
      
      <footer className="mt-auto py-8 text-center text-gray-600 text-sm">
        <p>Updates every 6 hours • Built with ❤️</p>
      </footer>
    </div>
  );
}

export default App;
