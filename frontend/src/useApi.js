import { useEffect, useState } from "react";
import { fetchApi } from "./api";

export function useApi(path, query = "") {
  const [state, setState] = useState({ data: null, error: null });
  useEffect(() => {
    const controller = new AbortController();
    fetchApi(path, new URLSearchParams(query), controller.signal)
      .then(data => {
        if (!controller.signal.aborted) setState({ data, error: null });
      })
      .catch(error => {
        if (!controller.signal.aborted) setState({ data: null, error: error.message });
      });
    return () => controller.abort();
  }, [path, query]);
  return state;
}
