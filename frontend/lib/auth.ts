import { AccountInfo } from "@/types";
import { Account, NextAuthOptions, TokenSet } from "next-auth";
import { JWT } from "next-auth/jwt";
import EmailProvider from "next-auth/providers/email";
import CredentialsProvider from "next-auth/providers/credentials";

export const authOptions: NextAuthOptions = {
  session: {
    strategy: "database",
  },

  providers: [
    CredentialsProvider({
      name: "credentials",
      credentials: {
        email: { label: "email", type: "text" },
        password: { label: "Password", type: "password" },
      },
      async authorize(credentials, req) {
        console.log("Authorizing with credentials:", credentials);
        if (!credentials) {
          throw new Error("No credentials provided");
        }
        const { email, password } = credentials;
        // call login API

        return { id: "1", name: email, email: email };
      },
    }),
  ],
  callbacks: {
    async session({ session, user }) {
      console.log(`[lib/auth] [session]: ${session}`);
      console.log(`[lib/auth] [user]: ${user}`);
      return session;
    },
  },
};
