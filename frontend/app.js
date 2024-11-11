async function submitQuery() {
    const queryInput = document.getElementById("queryInput").value;
    const resultsDiv = document.getElementById("results");
    resultsDiv.innerHTML = "Loading...";

    try {
        const response = await fetch("http://127.0.0.1:5001/submit_query", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({ query: queryInput })
        });

        if (!response.ok) {
            throw new Error(`Server error: ${response.status}`);
        }

        const data = await response.json();
        // console.log("Response data:", data.response);  // Log entire response data for debugging

        if (data.response) {
            resultsDiv.innerHTML = `
                <p>${data.response}</p>
            `;
        } else {
            resultsDiv.innerHTML = "No relevant results found.";
        }
    } catch (error) {
        resultsDiv.innerHTML = "Error fetching results.";
        console.error("Error:", error);
    }
}
