const accuconf = require('../accuconf_cfp/static/js/accuconf.js');
//import * as accuconf from '../accuconf_cfp/static/js/accuconf.js';

const assert = require('assert');

describe('email validation works correctly', () => {
    it('valid email correctly passes', () => {
        assert(accuconf.isValidEmail('russel@winder.org.uk'));
    });
    it('invalid email correctly fails',  () => {
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
