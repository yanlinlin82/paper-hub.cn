import { useState, useEffect, useCallback, useRef } from "react";

/**
 * Custom hook for making API calls with loading/error state management.
 */
export function useApi<T>(
  apiFunc: (...args: unknown[]) => Promise<T>,
  immediate = false,
  ...params: unknown[]
) {
  const [data, setData] = useState<T | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const paramsRef = useRef(params);
  paramsRef.current = params;

  const execute = useCallback(
    async (...args: unknown[]): Promise<T> => {
      setLoading(true);
      setError(null);
      try {
        const result = await apiFunc(...args);
        setData(result);
        return result;
      } catch (err: unknown) {
        const message =
          err instanceof Error
            ? err.message || "An error occurred"
            : "An error occurred";
        setError(message);
        throw err;
      } finally {
        setLoading(false);
      }
    },
    [apiFunc],
  );

  useEffect(() => {
    if (immediate) {
      execute(...paramsRef.current);
    }
  }, [immediate, execute]);

  return { data, loading, error, execute, setData };
}

export default useApi;
