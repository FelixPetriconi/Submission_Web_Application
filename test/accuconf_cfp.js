const accuconf = require('../accuconf_cfp/static/js/accuconf.js');
//import * as accuconf from '../accuconf_cfp/static/js/accuconf.js';

const assert = require('assert');

describe('email validation works correctly', () => {
    it('valid email passes', () => {
        assert(accuconf.isValidEmail('russel@winder.org.uk'));
    });
    it('no @ symbol fails',  () => {
        assert(!accuconf.isValidEmail('russel.winder.org.uk'));
    });
});

describe('passphrases checking works as expected', () => {
    it('too short (less than 8 characters) fails', () => {
        assert(!accuconf.isValidPassphrase('xx'));
    });
    it('long enough (8 characters or more) works', () => {
        assert(accuconf.isValidPassphrase('xxxxxxxx'));
    });
    it('UTF-8 encoded Unicode codepoints are acceptable', () => {
        assert(accuconf.isValidPassphrase('a nice lengthy förmé'));
    });
});

describe('name validation works correctly', () => {
    it('long name passes', () => {
        assert(accuconf.isValidName('Russel Winder'));
    });
    it('name too short fails',  () => {
        assert(!accuconf.isValidName('r'));
    });
});

describe('phone number validation works correctly', () => {
    // Phone numbers should obey ITU rules.
    it('with country code and spaces passes', () => {
        assert(accuconf.isValidPhone('+44 20 7585 2200'));
    });
    it('with country code and no spaces passes', () => {
        assert(accuconf.isValidPhone('+442075852200'));
    });
    it('with no country code and spaces passes', () => {
        assert(accuconf.isValidPhone('020 7585 2200'));
    });
    it('with no country code and no spaces passes', () => {
        assert(accuconf.isValidPhone('02075852200'));
    });
    it('with country code and dashes fails', () => {
        assert(accuconf.isValidPhone('+44-20-7585-2200'));
    });
    it('with no country code and dashes fails', () => {
        assert(accuconf.isValidPhone('020-7585-2200'));
    });
    it('with letters correctly fails',  () => {
        assert(!accuconf.isValidPhone('xxxxxxxx'));
    });
});
