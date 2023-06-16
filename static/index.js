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
      } else {
        alert("Please enter an objection before submitting");
      }
  
      document.querySelector('.rate-response').style.display = 'block';
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
  
    window.addEventListener('pageshow', (event) => {
      if (event.persisted) {
        window.location.reload();
      }
    });
  
    document.getElementById("btn-yes").addEventListener("click", function () {
      document.getElementById("rating-thankyou").style.display = "none";
      document.getElementById("chat-output").innerHTML = "";
    });
  
    document.getElementById("btn-no").addEventListener("click", function () {
      document.getElementById("rating-thankyou").style.display = "none";
      document.getElementById("exit-options").style.display = "block";
    });
  
    document.getElementById("btn-exit").addEventListener("click", function () {
      location.reload();
    });
  });