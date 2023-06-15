document.addEventListener('DOMContentLoaded', (event) => {

    document.getElementById("rate-submit").addEventListener("click", async () => {
        const ratingInput = document.getElementById("rating-input");
        const chatOutput = document.getElementById("chat-output");
        const rating = ratingInput.value;
        const ratingThankyou = document.getElementById("rating-thankyou");

        if (rating && rating >= 1 && rating <= 5) {
            const ratingResponse = await sendRating(rating);

            const ratingResponseElement = document.createElement("p");
            ratingResponseElement.textContent = "Thank you for your rating, we use this to improve your experience!";
            chatOutput.appendChild(ratingResponseElement);

            document.getElementById("objection-input").value = "";
            document.getElementById("response-input").value = "";
            ratingInput.value = "";
            ratingThankyou.style.display = "block";
        } else {
            alert("How helpful was the advice (1: unhelpful, 5: very helpful)");
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

    const examplePrompts = [
        "Your competitor is cheaper",
        "This looks too complicated for my team to learn",
        "We’re using this budget elsewhere",
        "This is too expensive"
    ];

    function displayExamplePrompts() {
        const select = document.getElementById("objection-select");
        examplePrompts.forEach(prompt => {
            const option = document.createElement("option");
            option.textContent = prompt;
            select.appendChild(option);
        });
    }

    displayExamplePrompts();

    document.getElementById("chat-submit").addEventListener("click", async () => {
        const objectionInput = document.getElementById("objection-input");
        const objectionSelect = document.getElementById("objection-select");
        const responseInput = document.getElementById("response-input");

        if (objectionSelect.value !== 'Select a common objection' && objectionInput.value === '') {
        objectionInput.value = objectionSelect.value;
    }

        const objection = objectionInput.value;
        const response = responseInput.value;


        if (objection && (objection.length > 0 || response.length > 0)) {
            const chatOutput = document.getElementById("chat-output");

            const objectionElement = document.createElement("p");
            objectionElement.innerHTML = "<strong>Objection:</strong> " + objection;
            const responseElement = document.createElement("p");
            responseElement.innerHTML = "<strong>Your response:</strong> " + response;

            chatOutput.appendChild(objectionElement);
            chatOutput.appendChild(responseElement);

            const loadingBar = document.getElementById("loading-bar");
            loadingBar.classList.remove("d-none");

            const serverResponse = await sendChatMessage(objection, response);

            loadingBar.classList.add("d-none");

            let feedbackContent = "<strong>Sales Sensei says:</strong> ";
            let paragraphs = serverResponse.split('\n');
            for (let i = 0; i < paragraphs.length; i++) {
                let feedbackElement = document.createElement("p");
                feedbackElement.innerHTML = (i === 0 ? feedbackContent : "") + paragraphs[i];
                chatOutput.appendChild(feedbackElement);
            }

            objectionInput.value = "";
            responseInput.value = "";
            document.getElementById("product-select").selectedIndex = 0;
            document.getElementById("objection-select").selectedIndex = 0;
        } else if (response.length > 0) {
            alert('Please enter an objection before providing a response');
        }
        document.querySelector('.rate-response').style.display = 'block';
    });

    let interactionId = null;

    async function sendChatMessage(objection, response) {
        const serverResponse = await fetch('/chatbot', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ user_objection: objection, user_response: response })
        });

        const data = await serverResponse.json();
        interactionId = data.interaction_id;
        return data.response_text;
    }

    window.addEventListener('pageshow', function (event) {
        if (event.persisted) {
            window.location.reload();
        }
    });

    $(function () {
    $('i[data-toggle="tooltip"]').hover(
        function(){
            if ($(this).prev().text() === 'Enter Objection: ') {
                $(this).attr('title', 'Enter a common objection you encounter during sales discussions.');
            } else if ($(this).prev().text() === 'Enter Your Suggested Way of Dealing with It (Optional): ') {
                $(this).attr('title', 'You may optionally suggest a way to address the objection here.');
            }
            $(this).tooltip('show');
        },
        function() {
            $(this).tooltip('hide');
        }
    );

    $('[data-toggle="tooltip"]').tooltip();
    });

    document.getElementById("objection-select").addEventListener("change", function() {
        document.getElementById("objection-input").value = "";
    });


    document.getElementById("btn-yes").addEventListener("click", function() {
    document.getElementById("rating-thankyou").style.display = "none"; 
    document.getElementById("chat-output").innerHTML = ""; 
    });


    document.getElementById("btn-no").addEventListener("click", function() {
    document.getElementById("rating-thankyou").style.display = "none";
    document.getElementById("exit-options").style.display = "block"; 
    });

    document.getElementById("btn-exit").addEventListener("click", function() {
    location.reload();
    });

});