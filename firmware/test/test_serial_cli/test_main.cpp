// Unit tests for the SerialCli parser + dispatcher.
// Runs on PlatformIO's `native` platform — no hardware required.

#include <unity.h>

#include <string>

#include "../../include/serial_cli.h"

using pocket_field::Error;
using pocket_field::Request;
using pocket_field::Response;
using pocket_field::SerialCli;

void setUp(void) {}
void tearDown(void) {}

// ---------------------------------------------------------------------------
// parse_request
// ---------------------------------------------------------------------------

void test_parse_request_basic(void) {
    Request r;
    TEST_ASSERT_TRUE(SerialCli::parse_request("REQ 42 system.version", r));
    TEST_ASSERT_EQUAL(42, r.id);
    TEST_ASSERT_EQUAL_STRING("system.version", r.command.c_str());
    TEST_ASSERT_EQUAL_STRING("", r.args.c_str());
}

void test_parse_request_with_args(void) {
    Request r;
    TEST_ASSERT_TRUE(SerialCli::parse_request("REQ 7 nfc.read timeout=5000", r));
    TEST_ASSERT_EQUAL(7, r.id);
    TEST_ASSERT_EQUAL_STRING("nfc.read", r.command.c_str());
    TEST_ASSERT_EQUAL_STRING("timeout=5000", r.args.c_str());
}

void test_parse_request_rejects_missing_prefix(void) {
    Request r;
    TEST_ASSERT_FALSE(SerialCli::parse_request("42 system.version", r));
}

void test_parse_request_rejects_wrong_prefix(void) {
    Request r;
    TEST_ASSERT_FALSE(SerialCli::parse_request("OK 42 system.version", r));
}

void test_parse_request_rejects_zero_id(void) {
    Request r;
    TEST_ASSERT_FALSE(SerialCli::parse_request("REQ 0 system.version", r));
}

void test_parse_request_rejects_missing_command(void) {
    Request r;
    TEST_ASSERT_FALSE(SerialCli::parse_request("REQ 42", r));
}

// ---------------------------------------------------------------------------
// format_ok / format_err
// ---------------------------------------------------------------------------

void test_format_ok(void) {
    std::string s = SerialCli::format_ok(42, "{\"x\":1}");
    TEST_ASSERT_EQUAL_STRING("OK 42 {\"x\":1}", s.c_str());
}

void test_format_err(void) {
    std::string s = SerialCli::format_err(7, Error::NFC_NO_TAG, "no tag detected");
    TEST_ASSERT_EQUAL_STRING("ERR 7 42 no tag detected", s.c_str());
}

// ---------------------------------------------------------------------------
// handle_line — dispatch + errors
// ---------------------------------------------------------------------------

void test_handle_line_unknown_command(void) {
    SerialCli cli;
    std::string out = cli.handle_line("REQ 99 does.not.exist");
    // Expect: ERR 99 1 ...
    TEST_ASSERT_TRUE(out.rfind("ERR 99 1 ", 0) == 0);
}

void test_handle_line_malformed(void) {
    SerialCli cli;
    std::string out = cli.handle_line("garbage line");
    // Expect: ERR 0 2 ... (BAD_ARGUMENTS)
    TEST_ASSERT_TRUE(out.rfind("ERR 0 2 ", 0) == 0);
}

void test_handle_line_dispatches_ok(void) {
    SerialCli cli;
    cli.register_command("ping", [](const Request&) {
        return Response{0, true, "{\"pong\":true}", Error::INTERNAL_ERROR};
    });
    std::string out = cli.handle_line("REQ 5 ping");
    TEST_ASSERT_EQUAL_STRING("OK 5 {\"pong\":true}", out.c_str());
}

void test_handle_line_dispatches_err(void) {
    SerialCli cli;
    cli.register_command("boom", [](const Request&) {
        return Response{0, false, "broke", Error::HARDWARE_FAILURE};
    });
    std::string out = cli.handle_line("REQ 5 boom");
    TEST_ASSERT_EQUAL_STRING("ERR 5 12 broke", out.c_str());
}

// ---------------------------------------------------------------------------

int main(int, char**) {
    UNITY_BEGIN();
    RUN_TEST(test_parse_request_basic);
    RUN_TEST(test_parse_request_with_args);
    RUN_TEST(test_parse_request_rejects_missing_prefix);
    RUN_TEST(test_parse_request_rejects_wrong_prefix);
    RUN_TEST(test_parse_request_rejects_zero_id);
    RUN_TEST(test_parse_request_rejects_missing_command);
    RUN_TEST(test_format_ok);
    RUN_TEST(test_format_err);
    RUN_TEST(test_handle_line_unknown_command);
    RUN_TEST(test_handle_line_malformed);
    RUN_TEST(test_handle_line_dispatches_ok);
    RUN_TEST(test_handle_line_dispatches_err);
    return UNITY_END();
}
