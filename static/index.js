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
    document.getElementById("objection-input").value = lastObjection;
    document.getElementById("product-select").selectedIndex = lastProductIndex;
  });

  document.getElementById("btn-another-objection").addEventListener("click", function () {
    document.getElementById("follow-up-options").style.display = "none";
    document.getElementById("chat-output").innerHTML = "";
    document.getElementById("objection-input").value = "";
    document.getElementById("product-select").selectedIndex = 0;
    lastObjection = "";
    lastProductIndex = 0;
  });

  document.getElementById("btn-save").addEventListener("click", function () {
    var doc = new jsPDF();
    var chatOutput = $('#chat-output').html();
    doc.text(chatOutput, 10, 10);
    doc.save('conversation.pdf');
    document.getElementById("objection-input").value = lastObjection;
    document.getElementById("product-select").selectedIndex = lastProductIndex; 
  });

  document.getElementById("btn-exit").addEventListener("click", function () {
    location.reload();
  });

  $('#btn-follow-up').click(function() {
    var objectionText = $('#objection-input').val();
    var chatOutput = $('#chat-output');
    chatOutput.append('<div class="user-text">User: ' + objectionText + '</div>');
    setTimeout(function() {
        var advice = "This is a follow up advice from the AI"; 
        chatOutput.append('<div class="ai-text">AI: ' + advice + '</div>');
    }, 2000);
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