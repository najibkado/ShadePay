//Sets Transaction Modal on the dashboard page
document.addEventListener("DOMContentLoaded", () => {
    
    document.querySelectorAll("#table-item").forEach(item => {
        item.onclick = () => {

            id = item.dataset.id
            user_id = item.dataset.userId

            fetch(`/transaction_details/${id}`, {
                method: "GET"
            })
            .then(res => res.json())
            .then(result => {

 

                if (user_id === result.transaction.sender_id) {
                    
                    document.querySelector("#trnsaction_reciever").innerHTML = result.transaction.reciever

                } else {

                    document.querySelector("#trnsaction_reciever").innerHTML = result.transaction.sender
                    
                }

                document.querySelector("#transaction-amount").innerHTML = result.transaction.amount

                document.querySelector("#transaction-date").innerHTML = result.transaction.date



                if (result.transaction.status_code == 1) {

                    document.querySelector("#transaction-status").innerHTML = "Completed"
                    
                } else if (result.transaction.status_code == 2) {

                    document.querySelector("#transaction-status").innerHTML = "Cancelled"
                    
                } else if (result.transaction.status_code == 3) {

                    document.querySelector("#transaction-status").innerHTML = "Completed"

                } else if (result.transaction.status_code == 4) {

                    document.querySelector("#transaction-status").innerHTML = "Hold"

                } else if (result.transaction.status_code == 5) {

                    document.querySelector("#transaction-status").innerHTML = "Review"

                } 

                

                document.querySelector("#tin").innerHTML = result.transaction.transaction_id

                document.querySelector("#from").innerHTML = result.transaction.sender

                document.querySelector("#to").innerHTML = result.transaction.reciever

                document.querySelector("#display-amount").innerHTML = result.transaction.amount

                document.querySelector("#description").innerHTML = result.transaction.desc

                document.querySelector("#ref").innerHTML = result.transaction.reference


            })
    
        }
    })

    //Send Functions

    function get_wallet_name(addr, wallet_type) {
        fetch(`/wallet/name/${wallet_type}?addr=${addr}`, {
            method: 'GET'
        })
        .then(response => response.json())
        .then(result => {
            document.querySelector("#recipient-confirmation").value = result.name
        })
    }

    document.querySelector("#recipient-wallet-address").addEventListener("keyup", (e) => {
        recipient_wallet_addr = e.target.value

        if (recipient_wallet_addr.endsWith(".siw")){
            get_wallet_name(recipient_wallet_addr, 1)
        } else if (recipient_wallet_addr.endsWith(".ssw")){
            get_wallet_name(recipient_wallet_addr, 2)
        } else if (recipient_wallet_addr.endsWith(".sbw")){
            get_wallet_name(recipient_wallet_addr, 3)
        }

    })

    document.querySelector("#send-wallet").addEventListener("change", (e) => {
        wallet_type = e.target.value

        if (wallet_type == 1){
            balance = document.querySelector("#individual-wallet-balance").value
            document.querySelector("#send-wallet-balance").value = balance

        }else if (wallet_type == 3) {
            balance = document.querySelector("#saving-wallet-balance").value
            document.querySelector("#send-wallet-balance").value = balance
            
        }else if (wallet_type == 2) {
            balance = document.querySelector("#business-wallet-balance").value
            document.querySelector("#send-wallet-balance").value = balance

        }

        if (balance < 100) {
            document.querySelector("#send-wallet-balance").value = "Insufficient Balance";
            document.querySelector("#send-button").disabled = true;
        } else {
            document.querySelector("#send-button").disabled = false;
        }

    })

    amount = document.querySelector("#send-amount")

    amount.addEventListener("keyup", () => {
        val = (amount.value / 100) * 1.25;
        fees = val += 20;

        if (fees <= 3500 ){
            document.querySelector("#send-transaction-fee").value = fees;
        } else {
            document.querySelector("#send-transaction-fee").value = 3500;
        }

        
        if (amount.value >= 100) {

            document.querySelector("#send-button").disabled = false;
    
        } else {
            document.querySelector("#send-transaction-fee").value = "Minimum is 100";
            document.querySelector("#send-button").disabled = true;
        }

    })


    //Request Functions

    function get_request_wallet_name(addr, wallet_type) {
        fetch(`/wallet/name/${wallet_type}?addr=${addr}`, {
            method: 'GET'
        })
        .then(response => response.json())
        .then(result => {
            document.querySelector("#request-recipient-confirmation").value = result.name
        })
    }


    document.querySelector("#request-recipient-wallet-address").addEventListener("keyup", (e) => {
        request_recipient_wallet_addr = e.target.value

        if (request_recipient_wallet_addr.endsWith(".siw")){
            get_request_wallet_name(request_recipient_wallet_addr, 1)
        } else if (request_recipient_wallet_addr.endsWith(".ssw")){
            get_request_wallet_name(request_recipient_wallet_addr, 2)
        } else if (request_recipient_wallet_addr.endsWith(".sbw")){
            get_request_wallet_name(request_recipient_wallet_addr, 3)
        }

    })

    document.querySelector("#request-amount").addEventListener("keyup", (e) => {
        amount = e.target.value

        if (amount >= 100){
            document.querySelector("#request-button").disabled = false
            document.querySelector("#request-error").innerHTML= ""
        } else {
            document.querySelector("#request-error").innerHTML= "Minimun Amount is 100"
            document.querySelector("#request-button").disabled = true
        }
    })
    
})