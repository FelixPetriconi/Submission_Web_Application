function isValidEmail(email) {
	return /^([a-zA-Z0-9_.+-])+\@(([a-zA-Z0-9-_])+\.)+([a-zA-Z0-9])+$/.test(email)
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

// There is no isValidCountry since a drop-down selection is used.

function getRandomInt(min, max) {
	return Math.floor(Math.random() * (max - min + 1)) + min
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
		$('#email_alert').text('Email should be of the format user@example.com')
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
	if (passphrase !== $('#cpassphrase').val()) {
		$('#cpassphrase_alert').text('Passphrase and confirmation passphrase not the same.')
		returnCode = false
	} else {
		$('#cpassphrase_alert').text('')
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
	$('#country_alert').text('')
	$('#puzzle_alert').text('')
	$('#alert').text('')
	return true
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
				'country': $('#country').val(),
			}),
			dataType: 'json',
			contentType: 'application/json',
			statusCode: {
				200: (data, text, jqXHR) => {
					window.location.replace("/" + data)
				},
				400: (jqXHR, textStatus, errorThrown) => {
					alert(jqXHR.responseText)
					$('#alert').text('')
				},
			}
		})
		$('#alert').text('Submitting form.')
	} else {
		$('#alert').text('Problem with form, not submitting.')
	}
	return false
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
		$('#passphrase_alert').text('Passphrase must be at least 8 characters long.')
		returnCode = false
	} else {
		$('#passphrase_alert').text('')
	}
	return returnCode
}

function clearLoginAlerts() {
	$('#login_alert').text('')
	$('#passphrase_alert').text('')
	$('#alert').text('')
	return true
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
					window.location.replace("/" + data)
				},
				400: (jqXHR, textStatus, errorThrown) => {
					alert(jqXHR.responseText)
					$('#alert').text('')
				},
			},
		})
		$('#alert').text('Submitting login details.')
	} else {
		$('#alert').text('Problem with login form, not submitting.')
	}
	return false
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

function isValidBio(bio) {
	return bio.length >= 50
}

function isValidPresenter(details, index) {
	let returnCode = true
	if (!isValidEmail(details['email'])) {
		$(`#email_${index}_alert`).text('Email not valid.')
		returnCode = false
	} else {
		$(`#email_${index}_alert`).text('')
	}
	if (!isValidName(details['name'])) {
		$(`#name_${index}_alert`).text('Name not valid.')
		returnCode = false
	} else {
		$(`#name_${index}_alert`).text('')
	}
	if (!isValidBio(details['bio'])) {
		$(`#bio_${index}_alert`).text('Bio not valid.')
		returnCode = false
	} else {
		$(`#bio_${index}_alert`).text('')
	}
	if (typeof details['is_lead'] !== 'boolean') {
		$(`#is_lead_${index}_alert`).text('Is_Lead is not valid.')
		returnCode = false
	} else {
		$(`#is_lead_${index}_alert`).text('')
	}
	return returnCode
}

function isValidTitle(title) {
	return title.length >= 8
}

function isValidSummary(summary) {
	return summary.length >= 50
}

function isValidSessionType(sessionType) {
	return ['quickie', 'session', 'workshop', 'longworkshop', 'fulldayworkshop'].indexOf(sessionType) > -1
}

function isValidAudience(audience) {
	return ['beginner', 'intermediate', 'expert', 'all'].indexOf(audience) > -1
}

function isValidKeywords(keywords) {
	return true
}

function isValidNotes(note) {
	return true
}

function isValidConstraints(constraint) {
	return true
}

function isValidSubmission(title, summary, sessionType, audience, keywords, no_video, notes, constraints, presenters) {
	let returnCode = true
	if (!isValidTitle(title)) {
		$('#title_alert').text('Title must be at least 8 characters long')
		returnCode = false
	} else {
		$('#title_alert').text('')
	}
	if (!isValidSummary(summary)) {
		$('#summary_alert').text('Summary must be at least 50 characters long')
		returnCode = false
	} else {
		$('#summary_alert').text('')
	}
	if (!isValidSessionType(sessionType)) {
		$('#session_type_alert').text('Session type not valid.')
		returnCode = false
	} else {
		$('#session_type_alert').text('')
	}
	if (!isValidAudience(audience)) {
		$('#audience_alert').text('Audience not valid.')
		returnCode = false
	} else {
		$('#audience_alert').text('')
	}
	if (!isValidKeywords(keywords)) {
		$('#keywords_alert').text('Keywords not valid.')
		returnCode = false
	} else {
		$('#keywords_alert').text('')
	}
	if (!isValidNotes(notes)) {
		$('#notes_alert').text('Notes not valid.')
		returnCode = false
	} else {
		$('#notes_alert').text('')
	}
	if (!isValidConstraints(constraints)) {
		$('#constraints_alert').text('Constraints not valid.')
		returnCode = false
	} else {
		$('#constraints_alert').text('')
	}
	for (const i in presenters) {
		if (!isValidPresenter(presenters[i], i)) {
			$('#presenter_alert').text('Presenter not valid.')
			returnCode = false
		} else {
			$('#presenter_alert').text('')
		}
	}
	const leads_list = presenters.filter((p) => {
		return p['is_lead']
	})
	if (leads_list.length !== 1) {
		returnCode = false
	}
	//  TODO Must check there is one and only one lead presenter.
	return returnCode
}

function clearSubmitAlerts() {
	$('#title_alert').text('')
	$('#summary_alert').text('')
	$('#keywords_alert').text('')
	$('#notes_alert').text('')
	$('#constraints_alert').text('')
	$('#alert').text('')
	return true
}

function submitProposal(proposalId) {
	const title = $('#title').val()
	const summary = $('#summary').val()
	const sessionType = $('#session_type').val()
	const audience = $('#audience').val()
	const keywords = $('#keywords').val()
	const no_video = document.getElementById('no_video').checked
	const notes = $('#notes').val()
	const constraints = $('#constraints').val()
	const presenters = []
	/*
	  For some reason the jQuery approach fails to do the right thing because
	  $(this) fails to be set. So do things with pure JavaScript (or is that ECMAScript)
	  pending finding the correct jQuery solution.
	*/
	const trNodes = document.getElementsByTagName('tr')
	for (let i = 0; i < trNodes.length; ++i) {
		const email = document.getElementById(`email_${i}_field`).value
		const name = document.getElementById(`name_${i}_field`).value
		const is_lead = document.getElementById(`is_lead_${i}_field`).checked
		const bio = document.getElementById(`bio_${i}_field`).value
		const countryNode = document.getElementById(`country_${i}_field`)
		const country = countryNode.options[countryNode.selectedIndex].value
		presenters.push({
			'email': email,
			'name': name,
			'is_lead': is_lead,
			'bio': bio,
			'country': country,
		})
	}
	if (isValidSubmission(title, summary, sessionType, audience, keywords, no_video, notes, constraints, presenters)) {
		$.ajax({
			method: 'POST',
			url: (proposalId ? `/proposal_update/${proposalId}` : '/submit'),
			data: JSON.stringify({
				'title': title,
				'session_type': sessionType,
				'summary': summary,
				'audience': audience,
				'keywords': keywords,
				'no_video': no_video,
				'notes': notes,
				'constraints': constraints,
				'presenters': presenters,
			}),
			dataType: 'json',
			contentType: 'application/json',
			statusCode: {
				200: (data, textStatus, jqXHR) => {
					window.location.replace('/' + data)
				},
				400: (jqXHR, textStatus, errorThrown) => {
					alert(jqXHR.responseText)
					$('#alert').text('')
				},
			},
		})
		$('#alert').text('Submitting proposal details.')
	} else {
		$('#alert').text('Problem with form, not submitting.')
	}
	return false
}

let current_presenter_number = 0

function addNewPresenter() {
	const email = $('#add-presenter-email').val()
	const name = $('#add-presenter-name').val()
	const bio = $('#add-presenter-bio').val()
	const country = $('#add-presenter-country option:selected').val()
	if (!isValidPresenter({
			'email': email,
			'name': name,
			'is_lead': false,
			'bio': bio,
			'country': country,
		})) {
		return false
	}
	current_presenter_number++
	$('#presenters tr:last').after(`
<tr><td>
	<div class="form-group">
		<label class="control-label col-sm-2">Email</label>
		<div class="col-sm-4">
		    <input class="email_field" id="email_${ current_presenter_number }_field" type="text" value="${ email }">
                    <span class="help-block" id="email_${ current_presenter_number}_alert"></span>
		</div>
    </div>
	<div class="form-group">
	    <label class="control-label col-sm-2">Name</label>
	    <div class="col-sm-4">
		    <input class="name_field" id="name_${ current_presenter_number }_field" type="text" value="${ name }">       
             <span class="help-block" id="name_${ current_presenter_number}_alert"></span>
		</div>
	</div>
	<div class="form-group">
            <label class="control-label col-sm-2">Is Lead?</label>
            <div class="col-sm-4">
                <input class="is_lead_field" id="is_lead_${ current_presenter_number }_field" type="checkbox">
            </div>
        </div>
	<div class="form-group">
		<label class="control-label col-sm-2">Bio</label>
		<div class="col-sm-4">
	    	<textarea class="bio_field" id="bio_${ current_presenter_number }_field" rows="24" cols="40">${bio}</textarea>
            <span class="help-block" id="bio_${ current_presenter_number}_alert"></span>
		</div>
	</div>
	<div class="form-group">
	    <label class="control-label col-sm-2">Country</label>
		<div class="col-sm-4">
             <select name="country_field" id="country_${ current_presenter_number }_field">
                  <option value="United Kingdom" selected > United Kingdom</option>
              </select>
	    </div>
	</div>
</td></tr>
`)
	$('.modal').on('hidden.bs.modal', () => {
		$("#add-presenter-modal").find('form')[0].reset()
	})
	$("#add-presenter-modal").modal('hide')
	return false
}


function submitScoreAndComment(id) {
	$('#alert').text('')
	$('#score_alert').text('')
	$('#comment_for_proposer_alert').text('')
	$('#comment_for_committee_alert').text('')
	const score = $('#score').val()
	const comment_for_proposer = $('#comment-for-proposer').val()
	const comment_for_committee = $('#comment-for-committee').val()
	if (score) {
		$('#alert').text('Submitting login details.')
		$.ajax({
			method: 'POST',
			url: `/review_proposal/${id}`,
			data: JSON.stringify({
				'score': score,
				'comment_for_proposer': comment_for_proposer,
				'comment_for_committee': comment_for_committee,
			}),
			dataType: 'json',
			contentType: 'application/json',
			statusCode: {
				200: (data, textStatus, jqXHR) => {
					$('#alert').text(data)
					$('#submit').text('Update')
				},
				400: (jqXHR, textStatus, errorThrown) => {
					alert(jqXHR.responseText)
					$('#alert').text('')
				},
			},
		})
	} else {
		$('#score_alert').text('Need to select a score to submit.')
	}
	return false
}

function navigatePrevious(id) {
	$.ajax({
		method: 'GET',
		url: `/previous_proposal/${id}/0`,
		statusCode: {
			200: (data, textStatus, jqXHR) => {
				window.location.replace(`/review_proposal/${data}`)
			},
			400: (jqXHR, textStatus, errorThrown) => {
				alert(jqXHR.responseText)
				$('#alert').text('')
			},
		},
	})
}

function navigatePreviousUnscored(id) {
	$.ajax({
		method: 'GET',
		url: `/previous_proposal/${id}/1`,
		statusCode: {
			200: (data, textStatus, jqXHR) => {
				window.location.replace(`/review_proposal/${data}`)
			},
			400: (jqXHR, textStatus, errorThrown) => {
				alert(jqXHR.responseText)
				$('#alert').text('')
			},
		},
	})
}

function navigateToList() {
	window.location.replace('/review_list')
}

function navigateNextUnscored(id) {
	$.ajax({
		method: 'GET',
		url: `/next_proposal/${id}/1`,
		statusCode: {
			200: (data, textStatus, jqXHR) => {
				window.location.replace(`/review_proposal/${data}`)
			},
			400: (jqXHR, textStatus, errorThrown) => {
				alert(jqXHR.responseText)
				$('#alert').text('')
			},
		},
	})
}

function navigateNext(id) {
	$.ajax({
		method: 'GET',
		url: `/next_proposal/${id}/0`,
		statusCode: {
			200: (data, textStatus, jqXHR) => {
				window.location.replace(`/review_proposal/${data}`)
			},
			400: (jqXHR, textStatus, errorThrown) => {
				alert(jqXHR.responseText)
				$('#alert').text('')
			},
		},
	})
}

// Apparently this is needed for Node execution and thus the tests.
if (typeof exports !== 'undefined') {
	exports.isValidEmail = isValidEmail
	exports.isValidPassphrase = isValidPassphrase
	exports.isValidName = isValidName
	exports.isValidPhone = isValidPhone
	exports.setPuzzle = setPuzzle
	exports.isPuzzleResultCorrect = isPuzzleResultCorrect
	exports.isValidBio = isValidBio
	exports.isValidSessionType = isValidSessionType
	exports.isValidSummary = isValidSummary
	exports.isValidAudience = isValidAudience
	exports.isValidNotes = isValidNotes
	exports.isValidConstraints = isValidConstraints
}
