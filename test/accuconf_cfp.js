const accuconf = require('../accuconf_cfp/static/js/accuconf.js')
//import * as accuconf from '../accuconf_cfp/static/js/accuconf.js'

const assert = require('assert')

describe('email validation works correctly', () => {
    it('valid email passes', () => {
        assert(accuconf.isValidEmail('russel@winder.org.uk'))
    })
    it('no @ symbol fails',  () => {
        assert(!accuconf.isValidEmail('russel.winder.org.uk'))
    })
})

describe('passphrases checking works as expected', () => {
    it('too short (less than 8 characters) fails', () => {
        assert(!accuconf.isValidPassphrase('xx'))
    })
    it('long enough (8 characters or more) works', () => {
        assert(accuconf.isValidPassphrase('xxxxxxxx'))
    })
    it('UTF-8 encoded Unicode codepoints are acceptable', () => {
        assert(accuconf.isValidPassphrase('a nice lengthy förmé'))
    })
})

describe('name validation works correctly', () => {
    it('long name passes', () => {
        assert(accuconf.isValidName('Russel Winder'))
    })
    it('name too short fails',  () => {
        assert(!accuconf.isValidName('r'))
    })
})

describe('phone number validation works correctly', () => {
    // Phone numbers should obey ITU rules.
    it('with country code and spaces passes', () => {
        assert(accuconf.isValidPhone('+44 20 7585 2200'))
    })
    it('with country code and no spaces passes', () => {
        assert(accuconf.isValidPhone('+442075852200'))
    })
    it('with no country code and spaces passes', () => {
        assert(accuconf.isValidPhone('020 7585 2200'))
    })
    it('with no country code and no spaces passes', () => {
        assert(accuconf.isValidPhone('02075852200'))
    })
    it('with country code and dashes fails', () => {
        assert(!accuconf.isValidPhone('+44-20-7585-2200'))
    })
    it('with no country code and dashes fails', () => {
        assert(!accuconf.isValidPhone('020-7585-2200'))
    })
    it('with letters correctly fails',  () => {
        assert(!accuconf.isValidPhone('xxxxxxxx'))
    })
})

describe('street address validation works correctly', () => {
    it('a known street address works', () => {
        assert(accuconf.isValidStreetAddress('41 Buckmaster Road'))
    })
})

describe('town city validation works correctly', () => {
    it('a known town city works', () => {
        assert(accuconf.isValidStreetAddress('London'))
    })
})

describe('state validation works correctly', () => {
    it('a known state works', () => {
        assert(accuconf.isValidState('Surrey'))
    })
})

describe('postal code validation works correctly', () => {
    it('a known UK postal code works', () => {
        assert(accuconf.isValidPostalCode('SW11 1EN'))
    })
    it('a known Indian pincode works', () => {
        assert(accuconf.isValidPostalCode('12345'))
    })
})

describe('puzzle setting and result consistency check.', () => {
    it('when it is correct it works', () => {
        const values = accuconf.setPuzzle()
        assert(accuconf.isPuzzleResultCorrect(values[0] + values[1]))
    })
    it('when it is incorrect it fails correctly', () => {
        const values = accuconf.setPuzzle()
        assert(!accuconf.isPuzzleResultCorrect(values[0] + values[1] + 1))
    })
})