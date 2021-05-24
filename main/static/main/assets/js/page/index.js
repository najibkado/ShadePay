document.addEventListener("DOMContentLoaded", () => {
    
    document.querySelector("#quoteAmount").addEventListener("keyup", () => {
    quote_amount = document.querySelector("#quoteAmount").value

    if (quote_amount != ""){

        if (quote_amount >= 3000){
            val = (quote_amount / 100) * 1.25
            fee = val + 100
            receipent_amount = quote_amount - fee
            document.querySelector("#quoteAmountReceive").value = receipent_amount
            if (fee <= 3500){
                document.querySelector("#Quotefees").innerHTML = `Total fees - ${fee} NGN`
            }else{
                capped_amount = quote_amount - 3500
                document.querySelector("#quoteAmountReceive").value = capped_amount
                document.querySelector("#Quotefees").innerHTML = `Total fees - 3500 NGN`
            }
        }
        else if (quote_amount >= 100 && quote_amount < 3000){
            val = (quote_amount / 100) * 1.50
            fee = val
            receipent_amount = quote_amount - fee
            document.querySelector("#quoteAmountReceive").value = receipent_amount
            if (fee <= 3500){
                document.querySelector("#Quotefees").innerHTML = `Total fees - ${fee} NGN`
            }else{
                capped_amount = quote_amount - 3500
                document.querySelector("#quoteAmountReceive").value = capped_amount
                document.querySelector("#Quotefees").innerHTML = `Total fees - 3500 NGN`
            }
        }
        else{
            document.querySelector("#Quotefees").innerHTML = `Minimun amount is NGN 100`
        }  
    }
    else{
        document.querySelector("#Quotefees").innerHTML = `Total fees - 0 NGN`
        document.querySelector("#quoteAmountReceive").value = 0
    }

    })
})