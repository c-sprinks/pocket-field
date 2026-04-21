// Smoke tests for protocol.h constants.
// Phase 1 will add SerialCli parser tests here.

#include <unity.h>
#include <cstring>

#include "../../include/protocol.h"

void setUp(void) {}
void tearDown(void) {}

void test_protocol_version_is_one(void) {
    TEST_ASSERT_EQUAL_STRING("1", pocket_field::PROTOCOL_VERSION);
}

void test_serial_baud_is_115200(void) {
    TEST_ASSERT_EQUAL_UINT32(115200UL, pocket_field::SERIAL_BAUD);
}

void test_line_terminator_is_lf(void) {
    TEST_ASSERT_EQUAL(0x0A, pocket_field::LINE_TERMINATOR);
}

void test_error_codes_match_spec(void) {
    TEST_ASSERT_EQUAL(1, static_cast<int>(pocket_field::Error::UNKNOWN_COMMAND));
    TEST_ASSERT_EQUAL(10, static_cast<int>(pocket_field::Error::HARDWARE_MISSING));
    TEST_ASSERT_EQUAL(20, static_cast<int>(pocket_field::Error::TIMEOUT));
    TEST_ASSERT_EQUAL(42, static_cast<int>(pocket_field::Error::NFC_NO_TAG));
    TEST_ASSERT_EQUAL(255, static_cast<int>(pocket_field::Error::INTERNAL_ERROR));
}

void test_frame_prefixes_are_upper_case(void) {
    TEST_ASSERT_EQUAL_STRING("REQ", pocket_field::FRAME_REQ);
    TEST_ASSERT_EQUAL_STRING("OK", pocket_field::FRAME_OK);
    TEST_ASSERT_EQUAL_STRING("ERR", pocket_field::FRAME_ERR);
    TEST_ASSERT_EQUAL_STRING("STREAM", pocket_field::FRAME_STREAM);
    TEST_ASSERT_EQUAL_STRING("END", pocket_field::FRAME_END);
}

int main(int, char**) {
    UNITY_BEGIN();
    RUN_TEST(test_protocol_version_is_one);
    RUN_TEST(test_serial_baud_is_115200);
    RUN_TEST(test_line_terminator_is_lf);
    RUN_TEST(test_error_codes_match_spec);
    RUN_TEST(test_frame_prefixes_are_upper_case);
    return UNITY_END();
}
