const chatGptProcessingUrl = 'https://lambda-endpoint-url';

function getTime() {
  let today = new Date();
  hours = today.getHours();
  minutes = today.getMinutes();

  if (hours < 10) {
    hours = "0" + hours;
  }

  if (minutes < 10) {
    minutes = "0" + minutes;
  }

  let time = hours + ":" + minutes;
  return time;
}

// Gets the first message
function firstBotMessage() {
  let firstMessage = "Hi there! How can I help you today?"
  document.getElementById("botStarterMessage").innerHTML = '<p class="botText"><span>' + firstMessage + '</span></p>';

  let time = getTime();

  $("#chat-timestamp").append(time);
  document.getElementById("userInput").scrollIntoView(false);
}


// Retrieves the response
async function getChatbotResponse(userText) {
  let botHtmlLoading = '<p class="botText"><span id="messageLoader"><span /><span /><span /></span></p>';
  $("#chatbox").append(botHtmlLoading);

  let botResponse = await fetchChatbotResponseAPI(userText);

  $("#messageLoader").remove();

  console.log("Response : ", botResponse);
  let botAnswerText = botResponse?.answer;

  let botHtml = '<p class="botText"><span>' + botAnswerText + '</span></p>';
  $("#chatbox").append(botHtml);

  document.getElementById("chat-bar-bottom").scrollIntoView(true);
}

async function fetchChatbotResponseAPI(userText) {
  const data = {
    question: userText
  };

  const response = await fetch(chatGptProcessingUrl, {
    method: "POST",  
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(data), // body data type must match "Content-Type" header
  });

  return response.json()
}


//Gets the text text from the input box and processes it
function getResponse() {
  let userText = $("#textInput").val();

  let userHtml = '<p class="userText"><span>' + userText + '</span></p>';

  $("#textInput").val("");
  $("#chatbox").append(userHtml);
  document.getElementById("chat-bar-bottom").scrollIntoView(true);

  getChatbotResponse(userText);
  document.getElementById("chat-bar-bottom").scrollIntoView(true);
}

function sendButton() {
  getResponse();
}

// Press enter to send a message
$("#textInput").keypress(function (e) {
  if (e.which == 13) {
    getResponse();
  }
});


firstBotMessage();

// Collapsible
var coll = document.getElementsByClassName("collapsible");

for (let i = 0; i < coll.length; i++) {
  coll[i].addEventListener("click", function () {
    this.classList.toggle("active");

    var content = this.nextElementSibling;

    if (content.style.maxHeight) {
      content.style.maxHeight = null;
    } else {
      content.style.maxHeight = content.scrollHeight + "px";
    }

  });
}

