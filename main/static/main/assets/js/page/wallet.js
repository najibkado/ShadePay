document.addEventListener("DOMContentLoaded", () => {
    wallet_selector = document.querySelector("#wallet_selector")

    if (wallet_selector.value == 001) {
        wallet_note_title.innerText = "Individual Wallet"
        wallet_note.innerText = "An Individual wallet will let you have a wallet for individual usage."
    } else if (wallet_selector.value == 002) {
        wallet_note_title.innerText = "Saving Wallet"
        wallet_note.innerText = "A Saving wallet will let you have a wallet for saving purposes. It let's you set date for when you can be able to withdraw the fund you are saving."
    } else if (wallet_selector.value == 003) {
        wallet_note_title.innerText = "Business Wallet"
        wallet_note.innerText = "A Business wallet will let you have a wallet for business purposes. This will give you access to all developer tools in order to support your business."
    }

    wallet_selector.addEventListener("change", () => {
        wallet_note_title = document.querySelector("#wallet-note-title")
        wallet_note = document.querySelector("#wallet_note")
        

        if (wallet_selector.value == 001) {
            wallet_note_title.innerText = "Individual Wallet"
            wallet_note.innerText = "An Individual wallet will let you have a wallet for individual usage."
        } else if (wallet_selector.value == 002) {
            wallet_note_title.innerText = "Saving Wallet"
            wallet_note.innerText = "A Saving wallet will let you have a wallet for saving purposes. It let's you set date for when you can be able to withdraw the fund you are saving."
        } else if (wallet_selector.value == 003) {
            wallet_note_title.innerText = "Business Wallet"
            wallet_note.innerText = "A Business wallet will let you have a wallet for business purposes. This will give you access to all developer tools in order to support your business."
        }
    })
})