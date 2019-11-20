function doloanreject(){
    alert("dooo")
    // data=$('#loanid').val()
    data=2
	urldata = 'textstr='+ data    
data=$('#loanapproval').serialize()
$.ajax({
    url:'/loan_reject',
    data:data,
    type:'GET',
    dataType: 'json',
    success:function(tt){
        console.log(tt)
        alert(tt)
        window.location.href="{{ url_for('pending') }}";
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