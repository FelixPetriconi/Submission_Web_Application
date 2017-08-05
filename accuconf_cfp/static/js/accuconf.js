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

function validateRegistrationData() {
    const email = $('#email').val()
    const passphrase = $('#passphrase').val()
    const cpassphrase = $('#cpassphrase').val()
    const name = $('#name').val()
    const phone = $('#phone').val()
    const streetAddress =  $('#street_address').val()
    const townCity =  $('#town_city').val()
    const state = $('#state').val()
    const postalCode = $('#postal_code').val()
	const country = $('#country').val()
	const puzzleValue = $('#puzzle').val()
	let returnCode = true
    if (!isValidEmail(email)) {
        $('#email_alert').text("Email should be of the format user@example.com")
        returnCode = false
    } else {
        $('#email_alert').text('')
    }
    if (!isValidPassphrase(passphrase)) {
    	$('#passphrase_alert').text('Passphrase is not valid.')
        returnCode = false
    } else {
    	$('#passphrase_alert').text('')
    }
    if (!isValidPassphrase(cpassphrase)) {
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
   if (!isValidName(name)) {
    	$('#name_alert').text('Invalid name.')
        returnCode = false
    } else {
    	$('#name_alert').text('')
    }
    if (!isValidPhone(phone)) {
    	$('#phone_alert').text('Invalid phone number.')
        returnCode = false
    } else {
    	$('#phone_alert').text('')
    }
    if (!isValidStreetAddress(streetAddress)) {
	    $('#street_address_alert').text('Invalid street address.')
        returnCode = false
    } else {
    	$('#street_address_alert').text()
    }
    if (!isValidTownCity(townCity)) {
	    $('#town_city_alert').text('Invalid town/city.')
        returnCode = false
    } else {
    	$('#town_city_alert').text('')
    }
    if (!isValidState(state)) {
    	$('#state_alert').text('Invalid state.')
        returnCode = false
    } else {
    	$('#state_alert').text('')
    }
    if (!isValidPostalCode(postalCode)) {
	    $('#postal_code_alert').text('Invalid postal code.')
        returnCode = false
    } else {
    	$('#postal_code_alert').text('')
    }
    // Country is select from a drop down and so must be valid.
	$('#country_alert').text('')
    if (!isPuzzleResultCorrect(puzzleValue)) {
     	$('#puzzle_alert').text('Incorrect value given.')
        returnCode = false
    } else {
    	$('#puzzle_alert').text('')
    }
	submit.disabled = ! returnCode
	return returnCode
}

function clearAlerts() {
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
	return true;
}

function registerUser() {
    if (validateRegistrationData()) {
        $.ajax({
            method: 'POST',
            url: '/register',
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
            success: (data) => {
                alert(data)
            },
            error: (data) => {
                alert(data)
            },
        })
        $('#alert').text('Submitting form.')
        return true
    } else {
	    $('#alert').text('Problem with form, not submitting.')
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
function notify(message) {
    $("#helpmessage").text(message);
    $("#helpmessage").fadeIn(100);
    //$("#helpmessage").fadeOut(3000);
}
*/
/*
function hidehelp() {
    $("#helpmessage").fadeOut(100);
}
*/
/*
function addPresenterOld() {
    const presenter = $('#presenter').val();
    if (!isValidEmail(presenter)) {
        return false;
    }
    const presenters_sel = $('#presenters');
    const allPresenters = [];
    $('#presenters option').each(function() {
        console.log($(this).val());
        allPresenters.push($(this).val());
    });
    if (!allPresenters.length) {
        $('#presenters').append('<option value="' + presenter + '">' + presenter + '</option>');
        allPresenters.push(presenter);
    }
    $.each(allPresenters, function(idx) {
        if (presenter === allPresenters[idx]) {
            console.log("Entry already present");
        } else {
            presenters_sel.append('<option value="' + presenter + '">' + presenter + '</option>');
        }
    });
}
*/
/*
function addPresenter(tableId) {
    const presenter_tbl_loc = '#' + tableId;
    const presenter_loc = presenter_tbl_loc + '> tbody > tr';
    const count = $(presenter_loc).length;
    const onChangeString = "javascript:loadState('p_ctry_" + count + "', 'p_states_" + count + "', 'p_state_" + count + "', true);";

    const htmlString = "<tr> <td class=\"narrow\"> <input type=\"radio\" name=\"lead\" id=\"lead\" value=\"" + count +  "\"> </td> <td> <input type=\"text\" name=\"p_email_" + count + "\" id=\"p_email_" + count + "\" placeholder=\"Email Address\"> </td>  <td> <input type=\"text\" name=\"p_fname_" + count + "\" id=\"p_fname_" + count + "\" placeholder=\"First Name\"> </td> <td> <input type=\"text\" name=\"p_lname_" + count + "\" id=\"p_lname_" + count + "\" placeholder=\"Last Name\"> </td>  <td> <select class=\"widetable\" name=\"p_ctry_" + count + "\" id=\"p_ctry_" + count + "\" onchange=\"" + onChangeString + "\" onkeyup=\"this.onchange();\" onmouseup=\"this.onchange();\"> </td> <td> <input type=\"text\" name=\"p_state_" + count + "\" id=\"p_state_" + count + "\" placeholder=\"State\"> </td> <td style=\"display: none;\"> <select class=\"widetable\" name=\"p_states_" + count + "\" id=\"p_states_" + count + "\"> </td> <td> <button type=\"button\" class=\"adder\" onclick=\"javascript:addPresenter('presenterstable');\">+</button> </td> </tr>";

    $(presenter_tbl_loc).find('tbody')
        .append(htmlString);
    const options = $('#p_ctry_1 > option').clone();
    const new_loc = '#p_ctry_' + count;
    $(new_loc).append(options);
}
*/
/*
function submitProposal() {
    const proposalTitle = $('#title').val();
    const proposal = $('#proposal').val();
    const proposalType = $('#proposaltype').val();
    const presenterRows = $("#presenters-body tr");
    const proposer = $("#def_email").text();
    const presenters = [];
    let leadId = $('input[name=lead]:checked', '#proposalform').val();
    if (leadId === undefined) {
        leadId = 1;
    }
    $("#presenters-body > tr").each(function(idx) {
        const cells = $(this).find('td');
        const presenter = {
            "lead": (leadId == (idx + 1)) ? 1 : 0,
            "email" : cells[2].innerText,
            "fname" : cells[3].innerText,
            "lname" : cells[4].innerText,
            "country" : cells[5].innerText,
            "state" : cells[6].innerText
        };
        presenters.push(presenter);
    });
    const proposalData = {
        "title": proposalTitle,
        "abstract": proposal,
        "proposer": proposer,
        "proposalType": proposalType,
        "presenters": presenters
    };
    $.ajax({
        url: "/proposals/upload_proposal",
        data: JSON.stringify(proposalData),
        type: "POST",
        method: "POST",
        dataType: "json",
        contentType: "application/json",
        success: function(data) {
            console.log(data);
            if (data.success) {
                alert(data.message);
                window.location = data.redirect;
            } else {
                $('#alert').text(data.message);
            }
        },
        error: function(data) {
            console.log("Error in proposal submission: " + data);
        }
    });
    return true;
}
*/
/*
function validatePresenter(details) {
    return true;
}
*/
/*
function addNewPresenter() {
    const email = $("#add-presenter-email").val();
    const fname = $("#add-presenter-fname").val();
    const lname = $("#add-presenter-lname").val();
    const ctry = $("#add-presenter-country").val();
    const state_sel = $("#add-presenter-states").val();
    const state_txt = $("#add-presenter-state").val();
    const presenters = $("#presenters-body");
    const trCnt = $("#presenters-body tr").length;
    const sno = trCnt + 1;
    const presenterRow = _.template($("#presenters-row-template").html());
    presenters.append(presenterRow({"sno": sno, "email": email, "fname": fname, "lname": lname, "ctry": ctry, "state": state}));
    resetModal();
    $("#add-presenter-modal").modal('hide');
    return true;
}
*/
/*
function resetModal() {
    $('.modal').on('hidden.bs.modal', function(){
        $("#add-presenter-modal").find('form')[0].reset();
    });
}
*/
/*
function deleteRow(rowIdx) {
    const presenters = $("#presenters-body");
    const msg = $("#presenters-body tr:eq(1)").text();
    alert(msg);
}
*/
/*
function showPointer(element) {
    element.css("cursor", "pointer");
}
*/
/*
function showDefaultPointer(element) {
    element.css("cursor", "default");
}
*/
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