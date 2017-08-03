# Apparently unused but has required side effects.
import configure

import accuconf_cfp.utils as utils


def test_reasonable_email():
    assert utils.is_valid_email('russel@winder.org.uk')


def test_string_with_no_at_is_not_email():
    assert not utils.is_valid_email('russel.winder.org.uk')


def test_passphrase_too_short_less_than_8_characters_fails():
    assert not utils.is_valid_passphrase('xx')


def test_passphrase_long_enough_8_or_more_characters_works():
    assert utils.is_valid_passphrase('xxxxxxxx')


def test_UTF8_encoded_Unicode_codepoints_are_acceptable_in_passphrases():
    assert utils.is_valid_passphrase('a nice lengthy förmé')


def test_long_name_passes():
    assert utils.is_valid_name('Russel Winder')


def test_name_too_short_fails():
    assert not utils.is_valid_name('r')


def test_phone_number_with_country_code_and_spaces_passes():
    assert utils.is_valid_phone('+44 20 7585 2200')


def test_phone_number_with_country_code_and_no_spaces_passes():
    assert utils.is_valid_phone('+442075852200')


def test_phone_number_with_no_country_code_and_spaces_passes():
    assert utils.is_valid_phone('020 7585 2200')


def test_phone_number_with_no_country_code_and_no_spaces_passes():
    assert utils.is_valid_phone('02075852200')


def test_phone_number_with_country_code_and_dashes_fails():
    assert utils.is_valid_phone('+44-20-7585-2200')


def test_phone_number_with_no_country_code_and_dashes_fails():
    assert utils.is_valid_phone('020-7585-2200')


def test_phone_number_with_letters_correctly_fails():
    assert not utils.is_valid_phone('xxxxxxxx')
