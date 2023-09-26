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
            const userObjectionElement = document.createElement("p");
            userObjectionElement.innerHTML = "<strong>Objection:</strong> " + objection;
            chatOutput.appendChild(userObjectionElement);
            loadingBar.classList.remove("d-none");
            rateResponse.style.display = "none";

            const serverResponse = await sendGenericObjection(objection);
            loadingBar.classList.add("d-none");

            const feedbackElement = document.createElement("p");
            feedbackElement.innerHTML = "<strong>SensAI:</strong> " + serverResponse;
            chatOutput.appendChild(feedbackElement);

            document.getElementById("follow-up-options").style.display = "block";
            rateResponse.style.display = "block"; 

            // Display the "below-chat-container" div
            document.getElementById("below-chat-container").style.display = "block";
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
          const productName = productSelect.options[productSelect.selectedIndex].text;
        
          if (productObjection && productObjection.trim() !== "" && productId) {
            lastProductObjection = productObjection; 
        
            const chatOutput = document.getElementById("chat-output");
            const loadingBar = document.getElementById("loading-bar");
            const rateResponse = document.getElementById("rate-response");
        
            chatOutput.innerHTML = "";
            const userObjectionElement = document.createElement("p");
            userObjectionElement.innerHTML = "<strong>Product Objection:</strong> " + productObjection + "<br><strong>Product:</strong> " + productName;
            chatOutput.appendChild(userObjectionElement);
            loadingBar.classList.remove("d-none");
            rateResponse.style.display = "none";
        
            const serverResponse = await sendProductObjection(productObjection, productId);
            loadingBar.classList.add("d-none");
        
            productObjectionInput.value = "";
            document.getElementById("product-objection-select").selectedIndex = 0;
        
            const feedbackElement = document.createElement("p");
            feedbackElement.innerHTML = "<strong>SensAI:</strong> " + serverResponse;
            chatOutput.appendChild(feedbackElement);
        
            document.getElementById("follow-up-options").style.display = "block";
            rateResponse.style.display = "block"; 
        
            document.getElementById("below-chat-container").style.display = "block";
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
          const productName = productSelect.options[productSelect.selectedIndex].text;
      
          if (productObjection && productObjection.trim() !== "" && productId) {
              lastProductObjection = productObjection; 
      
              const chatOutput = document.getElementById("chat-output");
              const loadingBar = document.getElementById("loading-bar");
              const rateResponse = document.getElementById("rate-response");
      
              chatOutput.innerHTML = "";
              const userObjectionElement = document.createElement("p");
              userObjectionElement.innerHTML = "<strong>Product Question:</strong> " + productObjection + "<br><strong>Product:</strong> " + productName;
              chatOutput.appendChild(userObjectionElement);
              loadingBar.classList.remove("d-none");
              rateResponse.style.display = "none";
      
              const serverResponse = await sendProductAdvice(productObjection, productId);
              loadingBar.classList.add("d-none");

              document.getElementById("product-advice-input").value = "";
              document.getElementById("product-question-select").selectedIndex = 0;
      
              const feedbackElement = document.createElement("p");
              feedbackElement.innerHTML = "<strong>SensAI:</strong> " + serverResponse;
              chatOutput.appendChild(feedbackElement);
      
              document.getElementById("follow-up-options").style.display = "block";
              rateResponse.style.display = "block";
      
              document.getElementById("below-chat-container").style.display = "block";
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
    const TIMEOUT = 120000;

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
      return 'An error occurred. Please add or select a product, hit refresh and enter another product objection'; 
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
      return 'An error occurred. Please add or select a product, hit refresh and enter another product question'; 
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
      var element = document.getElementById('prompt-container');
      element.scrollIntoView({ behavior: 'smooth' });
      window.scrollBy(0, -1500); 
      
      setTimeout(function() {
          document.getElementById('objection-input').focus();
      }, 500);

      setRating(0);
  });

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

    $('.option-btn').click(function() {
      $('#chat-container').css('display', 'block');
      $('#below-chat-container').css('display', 'block');
    });
    
// BUTTON CLICK EVENT
$('#objection-advice-btn, #product-objection-advice-btn, #product-advice-btn').click(function() {
  $('#below-chat-container').css('display', 'block');
});

  // CARD TOGGLE FUNCTIONALITY
  $('#sales-objections-option').click(function() {
    if($('#sales-objections-card').hasClass('hide-card')) {
      $('#sales-objections-card').removeClass('hide-card');
      $('#product-objections-card').addClass('hide-card');
      $('#product-question-card').addClass('hide-card');
    } else {
      $('#sales-objections-card').addClass('hide-card');
    }
  });

  $('#product-objections-option').click(function() {
    if($('#product-objections-card').hasClass('hide-card')) {
      $('#product-objections-card').removeClass('hide-card');
      $('#sales-objections-card').addClass('hide-card');
      $('#product-question-card').addClass('hide-card');
    } else {
      $('#product-objections-card').addClass('hide-card');
    }
  });

  $('#product-question-option').click(function() {
    if($('#product-question-card').hasClass('hide-card')) {
      $('#product-question-card').removeClass('hide-card');
      $('#sales-objections-card').addClass('hide-card');
      $('#product-objections-card').addClass('hide-card');
    } else {
      $('#product-question-card').addClass('hide-card');
    }
  });

  $(document).ready(function(){
    $('[data-toggle="tooltip"]').tooltip(); 
  });