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

  $('#btn-save').click(function() {
    var doc = new jsPDF();
    var chatOutput = $('#chat-output').html();
    doc.text(chatOutput, 10, 10);
    doc.save('conversation.pdf');
});

$('#btn-follow-up').click(function() {
  // Append the follow up question to the existing conversation
  var objectionText = $('#objection-input').val();
  var chatOutput = $('#chat-output');
  chatOutput.append('<div class="user-text">User: ' + objectionText + '</div>');

  // Call your API to get the advice
  // For example purposes, a timeout function is used to simulate the API call
  setTimeout(function() {
      var advice = "This is a follow up advice from the AI"; // Replace this with the actual advice from your AI
      chatOutput.append('<div class="ai-text">AI: ' + advice + '</div>');
  }, 2000);
});

let objections = document.querySelectorAll("#objectionExamplesModal ul li");
objections.forEach((objection) => {
  objection.addEventListener("click", function () {
    // Remove the active class from all items
    objections.forEach((item) => {
      item.classList.remove('active-item');
    });

    populateObjection(this);
  });
});

function populateObjection(element) {
  const objection = element.textContent; // get the text of the clicked li
  const objectionInput = document.getElementById('objection-input'); // get the textarea
  objectionInput.value = objection; // set the value of the textarea
  $('#objectionExamplesModal').modal('hide'); // close the modal
}

$('#objectionExamplesModal').on('hidden.bs.modal', function () {
  // Remove the active class when the modal is closed
  objections.forEach((item) => {
    item.classList.remove('active-item');
  });
});

});