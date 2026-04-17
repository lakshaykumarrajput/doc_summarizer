async function uploadFile() {
    const file = document.getElementById("fileInput").files[0];
    const formData = new FormData();
    formData.append("file", file);

    document.getElementById("loader").classList.remove("hidden");

    const res = await fetch("/upload", {
        method: "POST",
        body: formData
    });

    const data = await res.json();

    document.getElementById("loader").classList.add("hidden");

    document.getElementById("summaryBox").innerText =
        "Summary:\n" + data.summary;
}

async function askQuestion() {
    const question = document.getElementById("question").value;

    const res = await fetch("/ask", {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({question})
    });

    const data = await res.json();

    const chat = document.getElementById("chat");

    chat.innerHTML += `
        <p><b>You:</b> ${question}</p>
        <p><b>AI:</b> ${data.answer}</p>
    `;
    
}