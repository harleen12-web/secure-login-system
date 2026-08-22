const client = new Appwrite.Client();

client
    .setEndpoint(process.env.APPWRITE_ENDPOINT)
    .setProject(process.env.APPWRITE_PROJECT_ID);

const account = new Appwrite.Account(client);
const storage = new Appwrite.Storage(client);

const BUCKET_ID = process.env.APPWRITE_BUCKET_ID;


// =========================
// APPWRITE FUNCTIONS
// =========================

async function appwriteRegister(email, password) {
    return await account.create(
        Appwrite.ID.unique(),
        email,
        password
    );
}


async function appwriteLogin(email, password) {
    return await account.createEmailPasswordSession(
        email,
        password
    );
}


async function appwriteLogout() {
    await account.deleteSession("current");
    return true;
}


async function appwriteGetMe() {
    return await account.get();
}


// =========================
// FILE FUNCTIONS
// =========================

async function appwriteGetFiles() {
    return await storage.listFiles(BUCKET_ID);
}


async function appwriteGetFile(fileId) {
    return await storage.getFile(
        BUCKET_ID,
        fileId
    );
}


async function appwriteDownloadFile(fileId) {
    return storage.getFileDownload(
        BUCKET_ID,
        fileId
    );
}


// =========================
// CONNECT PROVIDED GUI TO APPWRITE
// =========================

const originalFetch = window.fetch;

window.fetch = async function(url, options = {}) {

    if (
        typeof url === "string" &&
        url.startsWith("http://localhost:3000")
    ) {

        const path = url.replace(
            "http://localhost:3000",
            ""
        );

        try {

            // =========================
            // REGISTER
            // =========================

            if (path === "/register") {

                const data = JSON.parse(options.body);

                const user = await appwriteRegister(
                    data.email,
                    data.password
                );

                return new Response(
                    JSON.stringify(user),
                    {
                        status: 201,
                        headers: {
                            "Content-Type": "application/json"
                        }
                    }
                );
            }


            // =========================
            // LOGIN
            // =========================

            if (path === "/login") {

                const data = JSON.parse(options.body);

                const session = await appwriteLogin(
                    data.email,
                    data.password
                );

                return new Response(
                    JSON.stringify(session),
                    {
                        status: 200,
                        headers: {
                            "Content-Type": "application/json"
                        }
                    }
                );
            }


            // =========================
            // LOGOUT
            // =========================

            if (path === "/logout") {

                await appwriteLogout();

                return new Response(
                    JSON.stringify({
                        message: "Logged out successfully"
                    }),
                    {
                        status: 200,
                        headers: {
                            "Content-Type": "application/json"
                        }
                    }
                );
            }


            // =========================
            // GET CURRENT USER
            // =========================

            if (path === "/me") {

                const user = await appwriteGetMe();

                return new Response(
                    JSON.stringify(user),
                    {
                        status: 200,
                        headers: {
                            "Content-Type": "application/json"
                        }
                    }
                );
            }


            // =========================
            // GET ALL FILES
            // =========================

            if (path === "/files") {

                const files = await appwriteGetFiles();

                return new Response(
                    JSON.stringify(files),
                    {
                        status: 200,
                        headers: {
                            "Content-Type": "application/json"
                        }
                    }
                );
            }


            // =========================
            // GET SINGLE FILE
            // /files/:id
            // =========================

            const fileMatch = path.match(
                /^\/files\/([^/]+)$/
            );

            if (fileMatch) {

                const fileId = fileMatch[1];

                const file = await appwriteGetFile(
                    fileId
                );

                return new Response(
                    JSON.stringify(file),
                    {
                        status: 200,
                        headers: {
                            "Content-Type": "application/json"
                        }
                    }
                );
            }


            // =========================
            // DOWNLOAD FILE
            // /files/:id/download
            // =========================

            const downloadMatch = path.match(
                /^\/files\/([^/]+)\/download$/
            );

            if (downloadMatch) {

                const fileId = downloadMatch[1];

                // Check permission first
                await appwriteGetFile(fileId);

                const downloadUrl = appwriteDownloadFile(fileId);

                return new Response(
                    JSON.stringify({
                        downloadUrl: downloadUrl.toString()
                    }),
                    {
                        status: 200,
                        headers: {
                            "Content-Type": "application/json"
                        }
                    }
                );
            }

        } catch (error) {

            console.error(
                "Appwrite adapter error:",
                error
            );

            return new Response(
                JSON.stringify({
                    error: error.message
                }),
                {
                    status: 400,
                    headers: {
                        "Content-Type": "application/json"
                    }
                }
            );
        }
    }

    return originalFetch(url, options);
};