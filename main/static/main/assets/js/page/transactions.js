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

                console.log(result);

                if (user_id === result.transaction.sender_id) {
                    
                    document.querySelector("#trnsaction_reciever").innerHTML = result.transaction.reciever

                } else {

                    document.querySelector("#trnsaction_reciever").innerHTML = result.transaction.sender
                    
                }

                document.querySelector("#transaction-amount").innerHTML = result.transaction.amount

                document.querySelector("#transaction-date").innerHTML = formatDate(result.transaction.date)


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

                document.querySelector("#description").innerHTML = result.transaction.transaction_charges

                document.querySelector("#ref").innerHTML = result.transaction.reference

                document.querySelector("#frmw").innerHTML = result.transaction.sender_business_wallet

                document.querySelector("#tow").innerHTML = result.transaction.reciever_business_wallet

                document.querySelector("#ship-to").innerHTML = result.shipping.shipping

                document.querySelector("#state").innerHTML = result.shipping.state

                document.querySelector("#country").innerHTML = result.shipping.country

                document.querySelector("#display-amount-to-recieve").innerHTML = result.toRecieve


            })
    
        }
    })




})

function formatDate(date) {
    var x = new Date(date)
    var dd = x.getDate()
    var mm = x.getMonth()
    var yy = x.getFullYear()
    var hh = x.getUTCHours()
    var mi = x.getUTCMinutes()
    return dd + "-" +mm+"-"+yy+" "+ hh+":"+mi
}