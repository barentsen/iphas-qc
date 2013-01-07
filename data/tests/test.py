"""
Implements a simply regression test to ensure that problems which have
previously been identified and fixed do no re-occur.
"""
import pyfits

qc = pyfits.getdata('../iphas-qc.fits', 1)

tests_failed = []
tests_passed = []

def test_passed(reason):
    tests_passed.append( reason )

def test_failed(reason):
    tests_failed.append( reason )

def test_report():
    n_failed = len(tests_failed)
    if n_failed == 0:
        print "All tests passed (%s)" % len(tests_passed)
    else:
        print "ERROR: %s TESTS FAILED!" % n_failed
        print "======================="
        for test in tests_failed:
            print test

def assert_qflag(fieldid, qflag, reason):
    """
    Asserts whether a field has a specific quality flag

    """
    c = qc.field('id') == fieldid
    if qc.field('qflag')[c] == qflag:
        test_passed( fieldid +': '+ reason )
    else:
        test_failed( fieldid +': '+ reason )

def assert_is_ok(fieldid, reason):
    """
    Asserts whether a field passed the quality tests

    """
    c = qc.field('id') == fieldid
    if qc.field('is_ok')[c]:
        test_passed( fieldid +': '+ reason )
    else:
        test_failed( fieldid +': '+ reason )


if __name__ == '__main__':

    # The depth of these fields only becomes dreadful after the calibration
    # is taking into account (cf. e-mail Janet 2013-01-05)
    ids = ['1066_oct2004', '1066o_oct2004', '2233_nov2005', '2233o_nov2005']
    for fieldid in ids:
        assert_qflag(fieldid, 'D', 'Sparse field with big calibration shift (likely cloud)')

    # Crowded fields are prone to fail the outlier test
    # cf e-mail Hywel 18 December 2012 15:07
    ids = ['4234_jun2004', '4234o_jun2004', '4275_jun2004', '4275o_jun2004',
            '4278_jun2004', '4278o_jun2004', '4282_jun2004', '4282o_jun2004',
            '4285_jun2004', '4285o_jun2004', '4289_jun2004', '4289o_jun2004',
            '4293_jun2004', '4293o_jun2004', '4313_jun2004', '4313o_jun2004',
            '4352_jun2004', '4352o_jun2004']
    for fieldid in ids:
        assert_is_ok(fieldid, 'Crowded field which should not fail outlier check')


    test_report()

