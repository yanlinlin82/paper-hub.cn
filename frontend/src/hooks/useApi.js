import { useState, useEffect, useCallback } from 'react';

/**
 * Custom hook for making API calls with loading/error state management.
 */
export function useApi(apiFunc, immediate = false, ...params) {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const execute = useCallback(async (...args) => {
    setLoading(true);
    setError(null);
    try {
      const result = await apiFunc(...args);
      setData(result);
      return result;
    } catch (err) {
      setError(err.message || 'An error occurred');
      throw err;
    } finally {
      setLoading(false);
    }
  }, [apiFunc]);

  useEffect(() => {
    if (immediate) {
      execute(...params);
    }
  }, [immediate, execute, ...params]);

  return { data, loading, error, execute, setData };
}

export default useApi;
