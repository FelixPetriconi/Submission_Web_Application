function isValidEmail(email) {
  return  /^([a-zA-Z0-9_.+-])+\@(([a-zA-Z0-9-_])+\.)+([a-zA-Z0-9])+$/.test(email)
}

function isValidPassphrase(password) {
    return password.length >= 8
}

function isValidName(name) {
    return name.length > 1
}

function isValidPhone(phone) {
    return /^\+?[0-9 ]+$/.test(phone)
}

function isValidStreetAddress(street_address) {
    return true
}

function isValidTownCity(townCity) {
    return true
}

function isValidState(state) {
    return true
}

function isValidPostalCode(postal_code) {
    return /^[A-Z0-9 ]+$/.test(postal_code)
}

// There is no isValidCountry since a drop-down selection is used.

function getRandomInt(min, max) {
  return Math.floor(Math.random() * (max - min + 1)) + min;
}

let puzzleResult = 0

function setPuzzle() {
	const a = getRandomInt(0, 100)
	const b = getRandomInt(0, 100)
	puzzleResult = a + b
	return [a, b]
}

function setPuzzleLabel() {
	const values = setPuzzle()
	$('#puzzle_label').text(`${values[0]} + ${values[1]}`)
}

function isPuzzleResultCorrect(value) {
	return puzzleResult === Math.floor(value)
}

function isValidRegistrationData(passphraseRequired) {
	let returnCode = true
    if (!isValidEmail($('#email').val())) {
        $('#email_alert').text("Email should be of the format user@example.com")
        returnCode = false
    } else {
        $('#email_alert').text('')
    }
    const passphrase = $('#passphrase').val()
    if (passphraseRequired && !isValidPassphrase(passphrase)) {
    	$('#passphrase_alert').text('Passphrase is not valid.')
        returnCode = false
    } else {
    	$('#passphrase_alert').text('')
    }
    const cpassphrase = $('#cpassphrase').val()
    if (passphraseRequired && !isValidPassphrase(cpassphrase)) {
    	$('#cpassphrase_alert').text('Confirmation passphrase is not valid.')
        returnCode = false
    } else {
    	$('#cpassphrase_alert').text('')
    }
    if (passphrase !== cpassphrase) {
    	$('#passphrase_alert').text('Passphrase and confirmation passphrase not the same.')
        returnCode = false
    } else {
    	$('#passphrase_alert').text('')
    }
   if (!isValidName($('#name').val())) {
    	$('#name_alert').text('Invalid name.')
        returnCode = false
    } else {
    	$('#name_alert').text('')
    }
    if (!isValidPhone($('#phone').val())) {
    	$('#phone_alert').text('Invalid phone number.')
        returnCode = false
    } else {
    	$('#phone_alert').text('')
    }
    if (!isValidStreetAddress($('#street_address').val())) {
	    $('#street_address_alert').text('Invalid street address.')
        returnCode = false
    } else {
    	$('#street_address_alert').text()
    }
    if (!isValidTownCity($('#town_city').val())) {
	    $('#town_city_alert').text('Invalid town/city.')
        returnCode = false
    } else {
    	$('#town_city_alert').text('')
    }
    if (!isValidState($('#state').val())) {
    	$('#state_alert').text('Invalid state.')
        returnCode = false
    } else {
    	$('#state_alert').text('')
    }
    if (!isValidPostalCode($('#postal_code').val())) {
	    $('#postal_code_alert').text('Invalid postal code.')
        returnCode = false
    } else {
    	$('#postal_code_alert').text('')
    }
    // Country is select from a drop down and so must be valid.
	$('#country_alert').text('')
	if (passphraseRequired) {
		if (!isPuzzleResultCorrect($('#puzzle').val())) {
			$('#puzzle_alert').text('Incorrect value given.')
			returnCode = false
		} else {
			$('#puzzle_alert').text('')
		}
	}
	return returnCode
}

function clearRegisterAlerts() {
	$('#email_alert').text('')
	$('#passphrase_alert').text('')
	$('#cpassphrase_alert').text('')
	$('#name_alert').text('')
	$('#phone_alert').text('')
	$('#street_address_alert').text('')
	$('#town_city_alert').text('')
	$('#state_alert').text('')
	$('#postal_code_alert').text('')
	$('#country_alert').text('')
	$('#puzzle_alert').text('')
	$('#alert').text('')
	return true;
}

function registerUser(passphraseRequiredText) {
	const passphraseRequired = true === passphraseRequiredText
    if (isValidRegistrationData(passphraseRequired)) {
        $.ajax({
            method: 'POST',
            url: (passphraseRequired ? '/register' : '/registration_update'),
            data: JSON.stringify({
                'email': $('#email').val(),
                'passphrase': $('#passphrase').val(),
                'name': $('#name').val(),
                'phone': $('#phone').val(),
                'street_address': $('#street_address').val(),
                'town_city': $('#town_city').val(),
                'state': $('#state').val(),
                'postal_code': $('#postal_code').val(),
                'country': $('#country').val(),
            }),
            dataType: 'json',
            contentType: 'application/json',
	        statusCode: {
	        	200: (data, text, jqXHR) => {
			        window.location.replace("/" + data)
		        },
		        400: (jqXHR, textStatus, errorThrown) => {
			        alert(jqXHR.status + '\n' +  jqXHR.responseText)
		        },
	        }
        })
        $('#alert').text('Submitting form.')
        return true
    } else {
	    $('#alert').text('Problem with form, not submitting.')
        return true
    }
}

function isValidLoginData() {
	let returnCode = true
	if (!isValidEmail($('#email').val())) {
		$('#email_alert').text('Email not valid.')
		returnCode = false
	} else {
		$('#email_alert').text('')
	}
	if (!isValidPassphrase($('#passphrase').val())) {
		$('#passphrase_alert').text('Passphrase not valid.')
		returnCode = false
	} else {
		$('#passphrase_alert').text('')
	}
	return returnCode
}

function clearLoginAlerts() {
	$('#login_alert').text('')
	$('#passphrase_alert').text('')
	return true;
}

function loginUser() {
	if (isValidLoginData()) {
		$.ajax({
			method: 'POST',
			url: '/login',
			data: JSON.stringify({
				'email': $('#email').val(),
				'passphrase': $('#passphrase').val(),
			}),
			dataType: 'json',
			contentType: 'application/json',
			statusCode: {
				200: (data, textStatus, jqXHR) => {
					window.location.replace("/" + data);
				},
				400: (jqXHR, textStatus, errorThrown) => {
					alert(jqXHR.status + '\n' +  jqXHR.responseText)
				},
			},
		})
		$('#alert').text('Submitting login details.')
		return true
	} else {
	    $('#alert').text('Problem with login form, not submitting.')
		return true
	}
}

/*
function checkDuplicateEmail() {
    const email = $('#email').val();
    if (!isValidEmail(email)) {
        $('#email_alert').text("Please provide a valid email address.");
        $('#submit').attr("disabled", true);
    } else {
        $('#email_alert').text();
        $('#submit').removeAttr("disabled");
    }
    $.ajax({
        type: 'GET',
        url: '/checkDuplicateEmail/' + email,
        dataType: "json",
        success: (data) => {
            if (data.duplicate === true) {
                $('#email_alert').text("This email address is already in use.")
                $('#submit').attr("disabled", true)
            } else {
                $('#email_alert').text("")
                $('#submit').removeAttr("disabled")
            }
        }
    })
}
*/

/*
function validatePresenter(details) {
    return true;
}
*/

function clearSubmitAlerts() {
	$('#title_alert').text('')
	$('#abstract_alert').text('')
	$('#session_type_alert').text('')
	$('#presenters_alert').text('')
	return true
}

function submitProposal() {
    const title = $('#title').val()
    const sessionType = $('#session_type').val()
    const summary = $('#summary').val()
    const presenters = []
    $('#presenters  tr').each((index, element) => {
    	presenters.push('burble', index, element)
	    presenters.push('blob', this)
    	//presenters.push('burble', index, element, $( this ))
	    //presenters.push('blob', $(this))
    	//presenters.push('flob', $(this).find('.email_field').val())
    	//presenters.push('adob', $(this).find('.name_field').val())
    	/*
	    presenters.push({
		    'email': $(this).find('email_field').val(),
		    'name': $(this).find('name_field').val(),
		    'is_lead': $(this).find('is_lead_field').val(),
		    'bio': $(this).find('bio_field').val(),
		    'country': $(this).find('country_field').val(),
		    'state': $(this).find('state_field').val(),
	    })
	    */
    })
    $.ajax({
        method: 'POST',
        url: '/submit',
        data: JSON.stringify({
	        'title': title,
	        'session_type': sessionType,
	        'summary': summary,
	        'presenters': presenters,
        }),
        dataType: 'json',
        contentType: 'application/json',
	    statusCode: {
		    200: (data, textStatus, jqXHR) => {
			    window.location.replace('/' + data);
		    },
		    400: (jqXHR, textStatus, errorThrown) => {
			    alert(jqXHR.status + '\n' +  jqXHR.responseText);
		    },
	    },
    })
    return true
}

function addNewPresenter() {
    const email = $("#add-presenter-email").val();
    const name = $("#add-presenter-name").val();
    const bio = $("#add-presenter-bio").val();
    const country = $("#add-presenter-country").val();
    const state = $("#add-presenter-states").val();
	$('#presenters tr:last').after(`
<tr><td>
	<div class="form-group">
		<label class="control-label col-sm-2">Email</label>
		<div class="col-sm-4">
		    <input class="email_field" type="text" value="${ email }">
		</div>
    </div>
	<div class="form-group">
	    <label class="control-label col-sm-2">Name</label>
	    <div class="col-sm-4">
		    <input class="name_field" type="text" value="${ name }">
		</div>
	</div>
	<div class="form-group">
        <label class="control-label col-sm-2">Is Lead?</label>
        <div class="col-sm-4">
            <input class="is_lead_field" type="checkbox" value="Is Lead?">
        </div>
    </div>
	<div class="form-group">
		<label class="control-label col-sm-2">Bio</label>
		<div class="col-sm-4">
	    	<textarea class="bio_field" rows="24" cols="50" placeholder="${ bio }"></textarea>
		</div>
	</div>
	<div class="form-group">
	    <label class="control-label col-sm-2">Country</label>
		<div class="col-sm-4">
	    	<input class="country_field" type="text" value="${ country }">
	    </div>
	</div>
	<div class="form-group">
		<label class="control-label col-sm-2">State</label>
		<div class="col-sm-4">
		    <input class="state_field" type="text" value="${ state }">
		</div>
	</div>
</td></tr>
`)
	$('.modal').on('hidden.bs.modal', () => {
		$("#add-presenter-modal").find('form')[0].reset();
	});
    $("#add-presenter-modal").modal('hide');
    return true;
}

/*
function uploadReview(button) {
    const button = button.value;
    const score = $("#score").val();
    const comment = $("#comment").val();
    const reviewData = {
        "button" : button,
        "score" : score,
        "comment" : comment
    };
    $.ajax({
        method: "POST",
        url: "/proposals/upload_review",
        data: JSON.stringify(reviewData),
        contentType: "application/json",
        success: function(data) {
            console.log(data);
            if (data.success) {
                window.location = data.redirect;
            } else {
                $('#alert').text(data.message);
            }
        }
    });

    return true;
}
*/

// Apparently this is needed for Node execution and thus the tests.
if (typeof exports !== 'undefined') {
    exports.isValidEmail = isValidEmail
    exports.isValidPassphrase = isValidPassphrase
    exports.isValidName = isValidName
    exports.isValidPhone = isValidPhone
    exports.isValidStreetAddress = isValidStreetAddress
    exports.isValidTownCity = isValidTownCity
    exports.isValidState = isValidState
    exports.isValidPostalCode = isValidPostalCode
	exports.setPuzzle = setPuzzle
	exports.isPuzzleResultCorrect = isPuzzleResultCorrect
}