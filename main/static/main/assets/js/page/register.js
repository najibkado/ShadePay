document.addEventListener("DOMContentLoaded", () => {

    document.querySelector("#validator-message").style.display = "none"
    
    usernameInput = document.querySelector("#username")

    usernameInput.addEventListener("keyup", (e) => {
        user = e.target.value;

        fetch(`/input-validator`, {
            method: "POST",
            body: JSON.stringify({
                type: "username",
                username: user
            })
        })
        .then(response => response.json())
        .then(result => {
            message = document.querySelector("#validator-message")
            message.innerHTML = result.message
            message.style.display = "block"
            // setTimeout(() => {
            //     message.style.display = "none"
            // }, 2000);   
        })
    })




})