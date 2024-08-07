import ky from "ky";

const buildServerURL = (path: string): string => {
  return `http://127.0.0.1:8000/${path}`;
};

const serverAPI = ky.create({
  headers: {
    "Content-Type": "application/json",
  },
  hooks: {
    beforeRequest: [
      async (request) => {
        if (request.headers.get("Authorization")) {
          return;
        }

        console.log(`[Ky]: ${request.method} ${request.url}`);
      },
    ],
  },
});

const normalAPI = ky.create({});

const parserServerResponse = async <T>(
  response: Response
): Promise<APIResponse<T>> => {
  const data = await response.json();
  return data;
};

export type APIResponse<T> = {
  data?: T;
  context: {
    code: number;
    message: string;
    server_at: string;
  };
};

export { serverAPI, normalAPI, parserServerResponse, buildServerURL };
