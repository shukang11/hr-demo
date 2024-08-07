import ky from "ky";

const buildServerURL = (path: string): string => {
  return `/${path}`;
};

const serverAPI = ky.create({
  headers: {
    "Content-Type": "application/json",
  },
  hooks: {
    beforeRequest: [
      (request) => {
        if (request.headers.get("Authorization")) {
          return;
        }
        const token = localStorage.getItem("token");
        if (token) {
          request.headers.set("Authorization", `Bearer ${token}`);
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
