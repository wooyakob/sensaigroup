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

    // Additional code
    let interactionId; // define this variable if it's not defined elsewhere in your script

    document.getElementById("rate-submit").addEventListener("click", async () => {
        const ratingInput = document.getElementById("rating-input");
        const chatOutput = document.getElementById("chat-output");
        const rating = ratingInput.value;
    
        if (rating && rating >= 1 && rating <= 5) {
            const ratingResponse = await sendRating(rating);
    
            const ratingResponseElement = document.createElement("p");
            ratingResponseElement.textContent = "Thank you for your rating, we use this to improve your experience!";
            chatOutput.appendChild(ratingResponseElement);
    
            document.getElementById("objection-input").value = "";
            document.getElementById("response-input").value = "";
            ratingInput.value = "";
        } else {
            alert("How helpful was the advice you received (1 is unhelpful, 5 is very helpful)");
        }
    
        document.querySelector('.rate-response').style.display = 'none';
        while (chatOutput.firstChild) {
            chatOutput.removeChild(chatOutput.firstChild);
        }
    });

    async function sendRating(rating) {
        const ratingResponse = await fetch('/rate', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ rating: rating, interaction_id: interactionId })
        });
    
        return await ratingResponse.json();
    }
});