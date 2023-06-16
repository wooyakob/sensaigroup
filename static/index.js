document.addEventListener('DOMContentLoaded', (event) => {
  document.getElementById("chat-submit").addEventListener("click", async () => {
    const objectionInput = document.getElementById("objection-input");
    const objection = objectionInput.value;

    if (objection && objection.trim() !== "") {
      const chatOutput = document.getElementById("chat-output");
      const loadingBar = document.getElementById("loading-bar");

      chatOutput.innerHTML = "";
      loadingBar.classList.remove("d-none");

      const serverResponse = await sendChatMessage(objection);
      loadingBar.classList.add("d-none");

      const feedbackElement = document.createElement("p");
      feedbackElement.innerHTML = "<strong>Sales Sensei says:</strong> " + serverResponse;
      chatOutput.appendChild(feedbackElement);

      objectionInput.value = "";
      document.getElementById("product-select").selectedIndex = 0;
      
      document.getElementById("follow-up-options").style.display = "block";
    } else {
      alert("Please enter an objection before submitting");
    }
  });

  async function sendChatMessage(objection) {
    const serverResponse = await fetch('/chatbot', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ user_objection: objection })
    });

    const data = await serverResponse.json();
    return data.response_text;
  }

  document.getElementById("btn-follow-up").addEventListener("click", function () {
    document.getElementById("follow-up-options").style.display = "none";
    document.getElementById("chat-output").innerHTML = "";
  });

  document.getElementById("btn-another-objection").addEventListener("click", function () {
    document.getElementById("follow-up-options").style.display = "none";
    document.getElementById("chat-output").innerHTML = "";
  });

  document.getElementById("btn-save").addEventListener("click", function () {
    // add functionality to save the conversation to a PDF
  });

  document.getElementById("btn-exit").addEventListener("click", function () {
    location.reload();
  });
});