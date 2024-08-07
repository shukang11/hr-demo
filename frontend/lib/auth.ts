import { NextAuthOptions } from "next-auth";
import CredentialsProvider from "next-auth/providers/credentials";

export const authOptions: NextAuthOptions = {
  secret: process.env.SECRET || "secret",
  session: {
    strategy: "jwt",
  },
  providers: [
    CredentialsProvider({
      name: "credentials",
      credentials: {
        id: { label: "id", type: "text" },
        token: { label: "token", type: "text" },
        email: { label: "email", type: "text" },
        name: { label: "name", type: "text" },
      },
      async authorize(credentials, req) {
        console.log("Authorizing with credentials:", credentials);
        if (!credentials) {
          throw new Error("No credentials provided");
        }
        const { id, token, email, name } = credentials;
        // call login API
        // throw new Error("No credentials provided");
        const user = { id, email, name, token };
        console.log(`[lib/auth] [authorize]: ${JSON.stringify(user)}`);
        return user;
      },
    }),
  ],
  callbacks: {
    async jwt({ token, user, account, session }) {
      console.log(`[lib/auth/jwt] [jwt]: ${JSON.stringify(token)}`);
      console.log(`[lib/auth/jwt] [account]: ${JSON.stringify(account)}`);
      console.log(`[lib/auth/jwt] [session]: ${JSON.stringify(session)}`);
      console.log(`[lib/auth/jwt] [user]: ${JSON.stringify(user)}`);
      if (account?.type === "credentials") {
        // @ts-ignore
        token.accessTokenValue = user.token;
      }
      return token;
    },
    async session({ session, user, token }) {
      console.log(`[lib/auth] [session]: ${JSON.stringify(session)}`);
      console.log(`[lib/auth] [user]: ${JSON.stringify(user)}`);
      console.log(`[lib/auth] [token]: ${JSON.stringify(token)}`);
      if (token.accessTokenValue) {
        // @ts-ignore
        session.user.accessTokenValue = token.accessTokenValue;
      }
      return session;
    },
  },
};
