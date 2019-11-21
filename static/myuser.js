function doloanreject(){
	//hide this value
	data=$('#loanid').val()
	urldata = 'textstr='+ data
	// alert(urldata)
$.ajax({
    url:'/loan_reject',
    data:urldata,
    type:'GET',
    dataType: 'json',
    success:function(tt){
        console.log(tt)
        alert("Loan Rejected Successfully")
		window.location.href="http://localhost:5000/admin.html";
		
        },
        error:function(anyv){
            console.log(anyv)
        }

    })

}

function findMe(){
	data=$('#CoopID').val()
	urldata = 'textstr='+ data
	// alert(data)
	$.ajax({
		url:'/SearchNames',
		data:urldata,
		type:'GET',
		dataType: 'json',
		success:function(tt){
			console.log(tt)
			if (tt=={}){
			document.getElementById('Name').value=''	
			}
			else{
			document.getElementById('Name').value=tt.fullname		
			}
		},
		error:function(anyv){
			console.log(anyv)
		}

	})
}

        function payWithPaystack(){
			var repayment = $('#amount').val();
			var balance = $('#loanbalance').val();
            var email = $('#email').val();
            alert(repayment)
            alert(balance)
            alert(email)
        if (repayment==' ' || repayment==0 || repayment<0){
            alert('Enter A valid Amount');
            $('#amount').focus();
			event.preventDefault(); 
			
		}
		else if(isNaN(repayment)==true){
            alert('Only Numbers are allowed ');
            $('#amount').focus();
			event.preventDefault();			
		}  		
		else if(repayment<balance){
            alert('Repayment Cannot be less than Loan Balance');
            $('#amount').focus();
			event.preventDefault();			
		}   
        else{
            var email=email
            var amt=$('#amount').val()*100
            var handler = PaystackPop.setup({
                    key: 'pk_test_e540194faba0a917009e15da930c0e2803408318',
                    email: email,
                    amount: amt,
                    currency: "NGN",
                ref: ''+Math.floor((Math.random() * 1000000000) + 1), // generates a pseudo-unique reference. Please replace with a reference you generated. Or remove the line entirely so our API will generate one for you
                
                metadata: {
                     custom_fields: [
                            {
                                    display_name: "Mobile Number",
                                    variable_name: "mobile_number",
                                    value: "+2348012345678"
                            }
                     ]
                },
                callback: function(){
                    // document.getElementById('paytackref').value=ref
                        doaajax()
                        alert('success. transaction ref is ' + response.reference);

                },
                onClose: function(){
                        alert('window closed');
                }
            });
            handler.openIframe();
        }

    }   

    


        function doaajax(){
    // data=$('#xyz').val()
    data=$('#repayment').serialize()
    // abc=confirm('Are You Sure You Want to Connect to secure banking')
    // if (abc==true){
    $.ajax({
        url:'/loanrepayment',
        data:data,
        type:'POST',
        dataType: 'json',
        success:function(tt){
            // console.log(tt)
            alert("Payment Successfully Made")
			window.location.href="http://localhost:5000/dashboard.html";
			// window.location.replace="{{ url_for('userdasboard') }}";
        },
        error:function(anyv){
            console.log(anyv)
        }

    })

}
