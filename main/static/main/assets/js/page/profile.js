document.addEventListener("DOMContentLoaded", ()=> {

    document.querySelector("#deactivate-account").addEventListener("keyup", (e) => {
        username = document.querySelector("#username").value
        username_confirm = e.target.value

        if (username == username_confirm){
            document.querySelector("#btn-deactivate").disabled = false
            document.querySelector("#username-message").style.color = "green"
            document.querySelector("#username-message").innerText = "Proceed"
        } else {
            document.querySelector("#btn-deactivate").disabled = true
            document.querySelector("#username-message").style.color = "red"
            document.querySelector("#username-message").innerText = "Incorrect Username"
        }

    })
})