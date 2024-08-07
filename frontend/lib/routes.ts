function path(root: string, sublink: string) {
  return `${root}${sublink}`;
}

const AUTHENTICATION_ROOT = "/auth";

export const AUTHENTICATION_APP = {
  SignIn: path(AUTHENTICATION_ROOT, "/signin"),
  SignUp: path(AUTHENTICATION_ROOT, "/signup"),
};

export const MAIN_APP = {
  HOME: "/",
  DASHBOARD: "/dashboard",
};
