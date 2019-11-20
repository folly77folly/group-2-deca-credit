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
		window.location.href="{{ url_for('pending') }}"
		
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
