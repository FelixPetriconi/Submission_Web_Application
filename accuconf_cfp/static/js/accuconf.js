function isValidEmail(email) {
  var regex = /^([a-zA-Z0-9_.+-])+\@(([a-zA-Z0-9-_])+\.)+([a-zA-Z0-9])+$/;
  return regex.test(email);
}

function isValidPassphrase(password) {
    if (password.length < 8) { return false; }
    return true;
}

function isValidName(name) {
    if (name.length < 1) { return false;}
    return true;
}

function isValidPhone(phone) {
    if (/[^0-9\-\+]+/.test(phone)) {return false;}
    return true;
}

function isValidState(state) {
    return true;
}

function isValidPostalCode(code) {
    if (/[^0-9a-zA-Z\s]/.test(code)) {return false;}
    return true;
}

function isValidStreetAddress(code) {
    if (/[^0-9a-zA-Z\s]/.test(code)) {return false;}
    return true;
}

function isValidCaptcha(captcha) {
    if (/\d+/.test(captcha)) {return true;}
    return false;
}

function validateRegistrationData() {
    var email = $('#email').val();
    var passphrase = $('#passphrase').val();
    var cpassphrase = $('#cpassphrase').val();
    var name = $('#name').val();
    var phone = $('#phone').val();
    var country = $('#country').val();
    var state = $('#state').val();
    var postalCode = $('#postal_code').val();
    var streetAddress =  $('#street_address').val();
    var question = $('#question').val();
    var captcha = $('#captcha').val();
    var submit = $('#submit');
    if (!isValidEmail(email)) {
        $('#emailalert').text("Email should be of the format user@example.com");
        return false;
    } else {
        $('#emailalert').text();
    }
    if (!isValidPassphrase(passphrase)) {
        return false;
    }
    if (!isValidName(name)) {
        return false;
    }
    if (!isValidPhone(phone)) {
        return false;
    }
    if (!isValidState(state)) {
        return false;
    }
    if (!isValidPostalCode(postalCode)) {
        return false;
    }
    if (!isValidCaptcha(captcha)) {
        return false;
    }
    submit.disabled = false;
    return true;
}

function registerUser() {
    if (validateRegistrationData()) {
        $.ajax({
            method: "POST",
            url: "/register",
            data: JSON.stringify({
                "email": $('#email').val(),
                "passphrase": $('#passphrase').val(),
                "name": $('#name').val(),
                "phone": $('#phone').val(),
                "country": $('#country').val(),
                "state": $('#state').val(),
                "postal_code": $('#postal_code').val(),
                "street_address": $('#street_address').val(),
            }),
            dataType: 'json',
            contentType: "application/json",
            success: function(data) {
                alert(data.valid);
            }
        });
        return true;
    } else {
        alert ("Invalid");
        return false;
    }
}

function checkDuplicate() {
    var email = $('#email').val();
    if (!isValidEmail(email)) {
        $('#emailalert').text("Please provide a valid email address");
        $('#submit').attr("disabled", true);
    } else {
        $('#emailalert').text();
        $('#submit').removeAttr("disabled");
    }
    var url = "/proposals/check/" + email;
    $.ajax({
        type: "GET",
        url: url,
        dataType: "json",
        success: function(data) {
            if (data.duplicate === true) {
                $('#emailalert').text("User id already exists!!!");
                $('#submit').attr("disabled", true);
            } else {
                $('#emailalert').text("");
                $('#submit').removeAttr("disabled");
            }
        }
    });

}

function notify(message) {
    $("#helpmessage").text(message);
    $("#helpmessage").fadeIn(100);
    //$("#helpmessage").fadeOut(3000);
}

function hidehelp() {
    $("#helpmessage").fadeOut(100);
}


function addPresenterOld() {
    var presenter = $('#presenter').val();
    if (!isValidEmail(presenter)) {
        return false;
    }
    var presenters_sel = $('#presenters');
    var allPresenters = [];
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

function addPresenter(tableId) {
    var presenter_tbl_loc = '#' + tableId;
    var presenter_loc = presenter_tbl_loc + '> tbody > tr';
    var count = $(presenter_loc).length;
    var onChangeString = "javascript:loadState('p_ctry_" + count + "', 'p_states_" + count + "', 'p_state_" + count + "', true);";

    var htmlString = "<tr> <td class=\"narrow\"> <input type=\"radio\" name=\"lead\" id=\"lead\" value=\"" + count +  "\"> </td> <td> <input type=\"text\" name=\"p_email_" + count + "\" id=\"p_email_" + count + "\" placeholder=\"Email Address\"> </td>  <td> <input type=\"text\" name=\"p_fname_" + count + "\" id=\"p_fname_" + count + "\" placeholder=\"First Name\"> </td> <td> <input type=\"text\" name=\"p_lname_" + count + "\" id=\"p_lname_" + count + "\" placeholder=\"Last Name\"> </td>  <td> <select class=\"widetable\" name=\"p_ctry_" + count + "\" id=\"p_ctry_" + count + "\" onchange=\"" + onChangeString + "\" onkeyup=\"this.onchange();\" onmouseup=\"this.onchange();\"> </td> <td> <input type=\"text\" name=\"p_state_" + count + "\" id=\"p_state_" + count + "\" placeholder=\"State\"> </td> <td style=\"display: none;\"> <select class=\"widetable\" name=\"p_states_" + count + "\" id=\"p_states_" + count + "\"> </td> <td> <button type=\"button\" class=\"adder\" onclick=\"javascript:addPresenter('presenterstable');\">+</button> </td> </tr>";

    $(presenter_tbl_loc).find('tbody')
        .append(htmlString);
    var options = $('#p_ctry_1 > option').clone();
    var new_loc = '#p_ctry_' + count;
    $(new_loc).append(options);
}

function uploadProposal() {
    var proposalTitle = $('#title').val();
    var proposal = $('#proposal').val();
    var proposalType = $('#proposaltype').val();
    var presenterRows = $("#presenters-body tr");
    var proposer = $("#def_email").text();
    var presenters = [];
    var leadId = $('input[name=lead]:checked', '#proposalform').val();
    if (leadId === undefined) {
        leadId = 1;
    }
    $("#presenters-body > tr").each(function(idx) {
        var cells = $(this).find('td');
        var presenter = {
            "lead": (leadId == (idx + 1)) ? 1 : 0,
            "email" : cells[2].innerText,
            "fname" : cells[3].innerText,
            "lname" : cells[4].innerText,
            "country" : cells[5].innerText,
            "state" : cells[6].innerText
        };
        presenters.push(presenter);
    });
    var proposalData = {
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

function validatePresenter(details) {
    return true;
}

function addNewPresenter() {
    var email = $("#add-presenter-email").val();
    var fname = $("#add-presenter-fname").val();
    var lname = $("#add-presenter-lname").val();
    var ctry = $("#add-presenter-country").val();
    var state_sel = $("#add-presenter-states").val();
    var state_txt = $("#add-presenter-state").val();
    var state;
    if (state_txt.length) {
        state = state_txt;
    } else {
        state = state_sel;
    }
    var presenters = $("#presenters-body");
    var trCnt = $("#presenters-body tr").length;
    var sno = trCnt + 1;
    var presenterRow = _.template($("#presenters-row-template").html());
    presenters.append(presenterRow({"sno": sno, "email": email, "fname": fname, "lname": lname, "ctry": ctry, "state": state}));
    resetModal();
    $("#add-presenter-modal").modal('hide');
    return true;
}

function resetModal() {
    $('.modal').on('hidden.bs.modal', function(){
        $("#add-presenter-modal").find('form')[0].reset();
    });
}

function deleteRow(rowIdx) {
    var presenters = $("#presenters-body");
    var msg = $("#presenters-body tr:eq(1)").text();
    alert(msg);
}

function showPointer(element) {
    element.css("cursor", "pointer");
}

function showDefaultPointer(element) {
    element.css("cursor", "default");
}


function uploadReview(button) {
    var button = button.value;
    var score = $("#score").val();
    var comment = $("#comment").val();
    var reviewData = {
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


// Apparently this is needed for Node execution.
if (typeof exports !== 'undefined') {
    exports.isValidEmail = isValidEmail;
    exports.isValidPassphrase = isValidPassphrase;
}