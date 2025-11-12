import { Search, Loader, Clock } from 'lucide-react';

export default function SearchBar({ query, setQuery, onSubmit, loading, onHistoryClick, historyCount }) {
  return (
    <form onSubmit={onSubmit} className="relative">
      <div className="flex gap-2 items-stretch">
        <div className="relative flex-1 flex items-center">
          <div className="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none">
            <Search className="h-5 w-5 text-gray-400" />
          </div>
          <input
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Ask about lab procedures, safety protocols, or equipment usage..."
            className="w-full py-4 pl-12 pr-4 rounded-xl border border-gray-200 focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all duration-300 text-gray-900 placeholder-gray-400"
            disabled={loading}
          />
        </div>

        {historyCount > 0 && (
          <button
            type="button"
            onClick={onHistoryClick}
            disabled={loading}
            className="px-4 py-2 text-gray-600 hover:text-gray-900 border border-gray-200 rounded-xl transition-all duration-200 hover:bg-gray-50 disabled:opacity-50 flex items-center gap-2"
            title="Search history"
          >
            <Clock className="h-5 w-5" />
            <span className="text-sm hidden sm:inline">{historyCount}</span>
          </button>
        )}

        <button
          type="submit"
          disabled={loading || !query.trim()}
          className="px-6 py-2 bg-blue-600 hover:bg-blue-700 disabled:bg-blue-400 text-white font-medium rounded-xl transition-all duration-200 shadow-sm hover:shadow flex items-center gap-2 whitespace-nowrap"
        >
          {loading ? (
            <>
              <Loader className="h-5 w-5 animate-spin" />
              <span className="hidden sm:inline">Searching...</span>
            </>
          ) : (
            <>
              <span>Search</span>
              <Search className="h-4 w-4" />
            </>
          )}
        </button>
      </div>
    </form>
  );
}
