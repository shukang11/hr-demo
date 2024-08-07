import { buildServerURL, serverAPI } from "@/lib/api";
import { getCurrentUser } from "@/lib/session";

export default async function Page() {
    const user = (await getCurrentUser());
    const resp = await serverAPI.get(buildServerURL("api/health/check"));

    return (
        <>
            H1
            {user && JSON.stringify(user)}
            <br />
            {JSON.stringify(await resp.json())}
        </>
    );
}
