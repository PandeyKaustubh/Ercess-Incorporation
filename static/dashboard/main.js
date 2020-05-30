$(document).ready(function() {
	$('[data-toggle="tooltip"]').tooltip(); 
        $('#categ').change( function() {
  		var id= $(this).find('option:selected').attr('id');
		$.ajax({                       // initialize an AJAX request
		        url: '/live/dashboard/ajax/topics',                    
			dataType: 'json',		        
			data: {
		          'id': id
        		},
        		success: function (data) {   
                        		
			  $('#top').find('option').remove();
			  if(data == ''){ $('#top').append('<option value='+0+' selected readonly>' + "No Sub Category"+ '</option>')}
                          else {
				$.each(data, function(index, item) {

					$('#top').append('<option value='+item["pk"]+'>' +item['fields']['topic']+ '</option>')
				});}
        		}
      		});

	});

         $('.type1').click(function(){
		$('.type1').not(this).prop('checked', false);
       });
	$('.type2').click(function(){
		$('.type2').not(this).prop('checked', false);
       });

	$(".btn2").click(function(){
		form = $("#msform");
		form.validate({
			rules:{
				category_id:{
					required: true,
				}
			},
			highlight: function(element) {
                        // add a class "has_error" to the element
                          $(element).next('div').addClass('has_error');
                        },
                        unhighlight: function(element) {
                        // remove the class "has_error" from the element
                          $(element).next('div').removeClass('has_error');
                        },
			messages:{
				category_id:{
					required: "Please choose from dropdown."
				}
			},
			success: function (error, element) {
          error.remove();
          $(element).next('div').removeClass('has_error');
          $(element).next('div').hide();
      },
    errorPlacement: function(error, element) {

                          error.appendTo( element.next('div'));
                          element.next('div').show();


                        },
	        });
	});

	$(".btn5").click(function(){
        	 alert('clicked')
       		form = $("#msform");

              form.validate({
		
		rules: {
		  ticket_name: {
			required: true,
                        //minlength: 5,
		  },
  	       	  start_date: {
			required: true,
		  },
		  end_date: {
			required: true,
			enddate: true
		  },
		  start_time: {
			required: true,
		  },
		  end_time: {
			required: true,
                        endtime: true,
		  },
		  
		  				
		},
		highlight: function(element) {
        		// add a class "has_error" to the element 
        		$(element).next('div').addClass('has_error');
   	 	},
    	        unhighlight: function(element) {
        		// remove the class "has_error" from the element 
        		$(element).next('div').removeClass('has_error');
    		},
		messages: {
		  ticket_name: {
			required: "Please provide name of your event",
                        minlength: "Event Name should have atleast 5 characters."
		  },
		  start_date: {
			required: "Provide the Start Date of Event",
		  },
		  end_date: {
			required: "Provide the End Date of Event",
                        edate: "End Date cannot be less than Start Date."
		  },
		  start_time: {
			required: "Provide Start Time of the event",
		  },
		  end_time: {
			required: "Provide End Time of the event.",
                        endtime: "End Time can not be less than Start Time for same day event."
		  },
		  
				
		},
		success: function (error, element) {
          error.remove();
          $(element).next('div').removeClass('has_error');
          $(element).next('div').hide();
      },
    errorPlacement: function(error, element) {
    
			error.appendTo( element.next('div'));
			element.next('div').show();

			
    		},
	  });

      });

});
