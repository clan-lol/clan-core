export default {
  async get(url: string, { signal = null }: { signal?: AbortSignal | null }) {
    const res = await fetch(url, { signal });
    return await res.json();
  },
  async post(
    url: string,
    { signal, body }: { body?: unknown; signal?: AbortSignal },
  ) {
    const res = await fetch(url, { signal, body: JSON.stringify(body) });
    return await res.json();
  },
};
