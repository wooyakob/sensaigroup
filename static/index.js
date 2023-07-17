document.addEventListener('DOMContentLoaded', (event) => {
  let lastObjection = "";


    // EVENT LISTENER FOR GENERIC OBJECTION
    document.getElementById("objection-advice-btn").addEventListener("click", async () => {
      const objectionInput = document.getElementById("objection-input");
      const objection = objectionInput.value;

      if (objection && objection.trim() !== "") {
        lastObjection = objection; 
      
        const chatOutput = document.getElementById("chat-output");
        const loadingBar = document.getElementById("loading-bar");

        chatOutput.innerHTML = "";
        loadingBar.classList.remove("d-none");

        const serverResponse = await sendGenericObjection(objection);
        loadingBar.classList.add("d-none");

        const feedbackElement = document.createElement("p");
        feedbackElement.innerHTML = "<strong>SensAI:</strong> " + serverResponse;
        chatOutput.appendChild(feedbackElement);

        document.getElementById("follow-up-options").style.display = "block";
        document.getElementById("rate-response").style.display = "block";
      } else {
        alert("Please enter an objection before submitting");
      }
    });

      // EVENT LISTENER FOR PRODUCT OBJECTION
      document.getElementById("product-objection-advice-btn").addEventListener("click", async () => {
        const productObjectionInput = document.getElementById("product-objection-input");
        const productObjection = productObjectionInput.value;
        const productSelect = document.getElementById("product-select");
        const productId = productSelect.value;
    
        if (productObjection && productObjection.trim() !== "" && productId) {
            lastProductObjection = productObjection; 
    
            const chatOutput = document.getElementById("chat-output");
            const loadingBar = document.getElementById("loading-bar");
    
            chatOutput.innerHTML = "";
            loadingBar.classList.remove("d-none");
    
            const serverResponse = await sendProductObjection(productObjection, productId);
            loadingBar.classList.add("d-none");
    
            const feedbackElement = document.createElement("p");
            feedbackElement.innerHTML = "<strong>SensAI:</strong> " + serverResponse;
            chatOutput.appendChild(feedbackElement);
    
            document.getElementById("follow-up-options").style.display = "block";
            document.getElementById("rate-response").style.display = "block";
        } else {
            alert("Please enter a product objection and select a product before submitting");
        }
    });
    
        // EVENT LISTENER FOR PRODUCT ADVICE

        document.getElementById("product-advice-btn").addEventListener("click", async () => {
          const productObjectionInput = document.getElementById("product-advice-input");
          const productObjection = productObjectionInput.value;
          const productSelect = document.getElementById("product-select");
          const productId = productSelect.value;
      
          if (productObjection && productObjection.trim() !== "" && productId) {
              lastProductObjection = productObjection; 
      
              const chatOutput = document.getElementById("chat-output");
              const loadingBar = document.getElementById("loading-bar");
      
              chatOutput.innerHTML = "";
              loadingBar.classList.remove("d-none");
      
              const serverResponse = await sendProductAdvice(productObjection, productId);
              loadingBar.classList.add("d-none");
      
              const feedbackElement = document.createElement("p");
              feedbackElement.innerHTML = "<strong>SensAI:</strong> " + serverResponse;
              chatOutput.appendChild(feedbackElement);
      
              document.getElementById("follow-up-options").style.display = "block";
              document.getElementById("rate-response").style.display = "block";
          } else {
              alert("Please enter a product question and select a product before submitting");
          }
      });


    document.getElementById("rate-submit").addEventListener("click", async function () {
      const rating = document.getElementById("rating-input").value;
      if (rating && (rating >= 1 && rating <= 5)) {
        alert("Thank you for your rating!");
    
        try {
          const response = await fetch('/rate_interaction', {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json'
            },
            body: JSON.stringify({ rating: rating })
          });
    
          const data = await response.json();
          console.log(data.message);
        } catch (error) {
          console.error('Error:', error);
        }
    
        document.getElementById("rate-response").style.display = "none";
        document.getElementById("rating-input").value = "";
      } else {
        alert("Please enter a rating between 1 and 5");
      }
    });


  // GENERIC OBJECTION SEND TO ENDPOINT /CHATBOT
  async function sendGenericObjection(objection) {
    const TIMEOUT = 60000;

    const fetchPromise = fetch('/chatbot', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ user_objection: objection })
    });

    const timeoutPromise = new Promise((_, reject) => setTimeout(() => reject(new Error('Request timed out')), TIMEOUT));

    try {
      const response = await Promise.race([fetchPromise, timeoutPromise]);

      const data = await response.json();
      return data.response_text;
    } catch (error) {
      console.error(error); 
      return 'An error occurred. Please refresh and enter another objection'; 
    }
  }

  // PRODUCT OBJECTION SEND TO ENDPOINT /product_objection_advice
  async function sendProductObjection(message, productId) {
    const response = await fetch('/product_objection_advice', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ 'message': message, 'product_id': productId })
    });

    if (response.ok) {
        const data = await response.json();
        return data.response_text;
    } else {
        console.error('Error:', response.statusText);
    }
  }

  // PRODUCT ADVICE SEND TO ENDPOINT /product_advice
  async function sendProductAdvice(message, productId) {
    const response = await fetch('/product_advice', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ 'message': message, 'product_id': productId })
    });

    if (response.ok) {
        const data = await response.json();
        return data.response_text;
    } else {
        console.error('Error:', response.statusText);
    }
  }

    document.getElementById("btn-another-objection").addEventListener("click", function () {
      document.getElementById("follow-up-options").style.display = "none";
      document.getElementById("chat-output").innerHTML = "";
      document.getElementById("objection-input").value = "";
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