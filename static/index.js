document.addEventListener('DOMContentLoaded', (event) => {
  let lastObjection = "";
  let lastProductIndex = 0;

  document.getElementById("chat-submit").addEventListener("click", async () => {
    const objectionInput = document.getElementById("objection-input");
    const objection = objectionInput.value;
    const productSelect = document.getElementById("product-select");
    const productIndex = productSelect.selectedIndex;

    if (objection && objection.trim() !== "") {
      lastObjection = objection; 
      lastProductIndex = productIndex;

      const chatOutput = document.getElementById("chat-output");
      const loadingBar = document.getElementById("loading-bar");

      chatOutput.innerHTML = "";
      loadingBar.classList.remove("d-none");

      const serverResponse = await sendChatMessage(objection);
      loadingBar.classList.add("d-none");

      const feedbackElement = document.createElement("p");
      feedbackElement.innerHTML = "<strong>Sales Sensei says:</strong> " + serverResponse;
      chatOutput.appendChild(feedbackElement);

      document.getElementById("follow-up-options").style.display = "block";
      document.getElementById("rate-response").style.display = "block";
    } else {
      alert("Please enter an objection before submitting");
    }
  });

document.getElementById("rate-submit").addEventListener("click", function () {
  const rating = document.getElementById("rating-input").value;
  if (rating && (rating >= 1 && rating <= 5)) {
    alert("Thank you for your rating!");
    document.getElementById("rate-response").style.display = "none";
    document.getElementById("rating-input").value = "";
  } else {
    alert("Please enter a rating between 1 and 5");
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

  document.getElementById("btn-another-objection").addEventListener("click", function () {
    document.getElementById("follow-up-options").style.display = "none";
    document.getElementById("chat-output").innerHTML = "";
    document.getElementById("objection-input").value = "";
    document.getElementById("product-select").selectedIndex = 0;
    lastObjection = "";
    lastProductIndex = 0;
  });

  let objections = document.querySelectorAll("#objectionExamplesModal ul li");
  objections.forEach((objection) => {
    objection.addEventListener("click", function () {
      objections.forEach((item) => {
        item.classList.remove('active-item');
      });

      populateObjection(this);
    });
  });

  function populateObjection(element) {
    const objection = element.textContent;
    const objectionInput = document.getElementById('objection-input');
    objectionInput.value = objection;
    $('#objectionExamplesModal').modal('hide');
  }

  $('#objectionExamplesModal').on('hidden.bs.modal', function () {
    objections.forEach((item) => {
      item.classList.remove('active-item');
    });
  });
});