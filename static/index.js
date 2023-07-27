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
        const rateResponse = document.getElementById("rate-response"); 

        chatOutput.innerHTML = "";
        loadingBar.classList.remove("d-none");
        rateResponse.style.display = "none";

        const serverResponse = await sendGenericObjection(objection);
        loadingBar.classList.add("d-none");

        const feedbackElement = document.createElement("p");
        feedbackElement.innerHTML = "<strong>SensAI:</strong> " + serverResponse;
        chatOutput.appendChild(feedbackElement);

        document.getElementById("follow-up-options").style.display = "block";
        rateResponse.style.display = "block"; 
      } else {
        alert("Please enter an objection before submitting");
      }
    });

      // EVENT LISTENER FOR PRODUCT OBJECTION
      document.getElementById("product-objection-advice-btn").addEventListener("click", async () => {
        const productObjectionInput = document.getElementById("product-objection-input");
        const productObjection = productObjectionInput.value;
        const productSelect = document.getElementById("product-objection-select");
        const productId = productSelect.value;
    
        if (productObjection && productObjection.trim() !== "" && productId) {
            lastProductObjection = productObjection; 
    
            const chatOutput = document.getElementById("chat-output");
            const loadingBar = document.getElementById("loading-bar");
            const rateResponse = document.getElementById("rate-response");
    
            chatOutput.innerHTML = "";
            loadingBar.classList.remove("d-none");
            rateResponse.style.display = "none";
    
            const serverResponse = await sendProductObjection(productObjection, productId);
            loadingBar.classList.add("d-none");
    
            const feedbackElement = document.createElement("p");
            feedbackElement.innerHTML = "<strong>SensAI:</strong> " + serverResponse;
            chatOutput.appendChild(feedbackElement);
    
            document.getElementById("follow-up-options").style.display = "block";
            rateResponse.style.display = "block"; 
        } else {
            alert("Please enter a product objection and select a product before submitting");
        }
    });
    
        // EVENT LISTENER FOR PRODUCT ADVICE

        document.getElementById("product-advice-btn").addEventListener("click", async () => {
          const productObjectionInput = document.getElementById("product-advice-input");
          const productObjection = productObjectionInput.value;
          const productSelect = document.getElementById("product-question-select");
          const productId = productSelect.value;
      
          if (productObjection && productObjection.trim() !== "" && productId) {
              lastProductObjection = productObjection; 
      
              const chatOutput = document.getElementById("chat-output");
              const loadingBar = document.getElementById("loading-bar");
              const rateResponse = document.getElementById("rate-response");
      
              chatOutput.innerHTML = "";
              loadingBar.classList.remove("d-none");
              rateResponse.style.display = "none";
      
              const serverResponse = await sendProductAdvice(productObjection, productId);
              loadingBar.classList.add("d-none");
      
              const feedbackElement = document.createElement("p");
              feedbackElement.innerHTML = "<strong>SensAI:</strong> " + serverResponse;
              chatOutput.appendChild(feedbackElement);
      
              document.getElementById("follow-up-options").style.display = "block";
              rateResponse.style.display = "block";
          } else {
              alert("Please enter a product question and select a product before submitting");
          }
      });

      document.getElementById("rate-submit-btn").addEventListener("click", async function () {
        const rating = document.getElementById("rating-input").value;
        const outputContainer = document.getElementById("chat-output"); 
    
        if (rating && (rating >= 1 && rating <= 5)) {
            outputContainer.innerHTML += "<p>Thank you for your rating!</p>";
    
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
                outputContainer.innerHTML += `<p>You rated the advice <span style="font-weight: bold; color: #f09819;">${rating}</span> <br> <br> ${data.message}</p>`;
            } catch (error) {
                console.error('Error:', error);
                outputContainer.innerHTML += "<p>Error while submitting your rating. Please try again.</p>";
            }
    
            document.getElementById("rate-response").style.display = "none";
            document.getElementById("rating-input").value = "";
    
            currentRating = 0;
            setRating(0);
        } else {
            outputContainer.innerHTML += "<p>Please enter a rating between 1 and 5</p>";
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
    const TIMEOUT = 60000;

    const fetchPromise = fetch('/product_objection_advice', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ 'message': message, 'product_id': productId })
    });

    const timeoutPromise = new Promise((_, reject) => setTimeout(() => reject(new Error('Request timed out')), TIMEOUT));

    try {
      const response = await Promise.race([fetchPromise, timeoutPromise]);

      const data = await response.json();
      return data.response_text;
    } catch (error) {
      console.error(error); 
      return 'An error occurred. Please refresh and enter another product objection'; 
    }
  }

  // PRODUCT ADVICE SEND TO ENDPOINT /product_advice
  async function sendProductAdvice(message, productId) {
    const TIMEOUT = 60000;

    const fetchPromise = fetch('/product_advice', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ 'message': message, 'product_id': productId })
    });

    const timeoutPromise = new Promise((_, reject) => setTimeout(() => reject(new Error('Request timed out')), TIMEOUT));

    try {
      const response = await Promise.race([fetchPromise, timeoutPromise]);

      const data = await response.json();
      return data.response_text;
    } catch (error) {
      console.error(error); 
      return 'An error occurred. Please refresh and ask another product question'; 
    }
  }

    document.getElementById("enter-objection-btn").addEventListener("click", function () {
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

    let productObjections = document.querySelectorAll("#productObjectionsExamplesModal ul li");
  productObjections.forEach((objection) => {
    objection.addEventListener("click", function () {
      productObjections.forEach((item) => {
        item.classList.remove('active-item');
      });

      populateProductObjection(this);
    });
  });

  function populateProductObjection(element) {
    const productObjection = element.textContent;
    const productObjectionInput = document.getElementById('product-objection-input');
    productObjectionInput.value = productObjection;
    $('#productObjectionsExamplesModal').modal('hide');
  }

  $('#productObjectionsExamplesModal').on('hidden.bs.modal', function () {
    productObjections.forEach((item) => {
      item.classList.remove('active-item');
    });
  });


  let productAdviceItems = document.querySelectorAll("#productAdviceExamplesModal ul li");
  productAdviceItems.forEach((advice) => {
    advice.addEventListener("click", function () {
      productAdviceItems.forEach((item) => {
        item.classList.remove('active-item');
      });

      populateProductAdvice(this);
    });
  });

  function populateProductAdvice(element) {
    const productAdvice = element.textContent;
    const productAdviceInput = document.getElementById('product-advice-input');
    productAdviceInput.value = productAdvice;
    $('#productAdviceExamplesModal').modal('hide');
  }

  $('#productAdviceExamplesModal').on('hidden.bs.modal', function () {
    productAdviceItems.forEach((item) => {
      item.classList.remove('active-item');
    });
  });

// Hooking up the follow-up options to scroll to respective chat container

    document.querySelectorAll('.btn.btn-primary.active').forEach(function(sendButton) {
        sendButton.addEventListener('click', function() {
            document.getElementById('chat-output').scrollIntoView({ behavior: 'smooth' });
        });
    });

    document.getElementById('rate-submit-btn').addEventListener('click', function() {
        document.getElementById('follow-up-options').scrollIntoView({ behavior: 'smooth' });
    });

    document.getElementById('enter-objection-btn').addEventListener('click', function() {
        document.getElementById('prompt-container').scrollIntoView({ behavior: 'smooth' });
  });

    // document.getElementById('enter-product-objection-btn').addEventListener('click', function() {
     //   document.getElementById('product-objection-input').scrollIntoView({ behavior: 'smooth' });
    // });

    // document.getElementById('enter-product-question-btn').addEventListener('click', function() {
    //   document.getElementById('product-advice-input').scrollIntoView({ behavior: 'smooth' });
    // });

    let hideRatingElements = document.querySelectorAll('.hide-rating');

    hideRatingElements.forEach((element) => {
      element.addEventListener('click', function() {
        let rateResponse = document.getElementById('rate-response');
        let ratingInput = document.getElementById('rating-input');

        if (ratingInput.value.trim() === '') {
          rateResponse.style.display = 'none';
        }
      });
    });

    let currentRating = 0;

    function setRating(value) {
      const stars = document.getElementsByClassName("fa-star");
      currentRating = value;
      
      for (let i = 0; i < stars.length; i++) {
          if (i < value) {
              stars[i].classList.add("checked");
          } else {
              stars[i].classList.remove("checked");
          }
      }
      
      document.getElementById("rating-input").value = value;
    }
    
    function highlightStars(value) {
      const stars = document.getElementsByClassName("fa-star");
    
      for (let i = 0; i < stars.length; i++) {
          if (i < value) {
              stars[i].classList.add("highlight");
          } else {
              stars[i].classList.remove("highlight");
          }
      }
    }
    
    document.getElementById("stars-container").addEventListener("mouseout", function() {
        highlightStars(currentRating);
    });
    
  
  