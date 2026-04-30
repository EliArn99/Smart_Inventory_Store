export async function postJson(url, payload, csrfToken) {
    const response = await fetch(url, {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            "X-CSRFToken": csrfToken || "",
        },
        credentials: "same-origin",
        body: JSON.stringify(payload),
    });

    let data = {};
    try {
        data = await response.json();
    } catch {
        data = {};
    }

    if (!response.ok) {
        throw new Error(data.error || data.message || "Възникна грешка при заявката.");
    }

    return data;
}
