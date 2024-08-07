import { getCurrentUser } from "@/lib/session";

export default async function Page() {
    const user = (await getCurrentUser());
    return (
        <>
            H1
            {user && JSON.stringify(user)}
        </>
    );
}
