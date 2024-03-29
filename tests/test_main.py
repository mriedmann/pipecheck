import io
import unittest
import unittest.mock

from parameterized import parameterized

from pipecheck.__main__ import gen_call, get_commands_from_config, print_result, run
from pipecheck.api import Err, Ok, Warn
from pipecheck.checks.dns import DnsProbe
from pipecheck.checks.http import HttpProbe
from pipecheck.checks.icmp import PingProbe
from pipecheck.checks.tcp import TcpProbe

CRED = "\33[31m"
CGREEN = "\33[32m"
CYELLOW = "\33[33m"


class MainTests(unittest.TestCase):
    @parameterized.expand(
        [
            (Ok("Test Result"), CGREEN, ["OK", "Test Result"]),
            (Warn("Test Result"), CYELLOW, ["WARN", "Test Result"]),
            (Err("Test Result"), CRED, ["ERR", "Test Result"]),
        ]
    )
    @unittest.mock.patch("sys.stdout", new_callable=io.StringIO)
    def test_print_result(self, result, color, snippets, mock_stdout):
        print_result(result)
        print_text = mock_stdout.getvalue()
        self.assertIn(color, print_text)
        for text in snippets:
            self.assertIn(text, print_text)

    @parameterized.expand(
        [
            ({"type": "http", "url": "https://httpstat.us/200"}, {}, (HttpProbe, {"url": "https://httpstat.us/200"})),
            ({"host": "8.8.8.8", "port": 53, "type": "tcp"}, {}, (TcpProbe, {"host": "8.8.8.8", "port": 53})),
            (
                {"host": "1.1.1.1", "port": 53, "tcp_timeout": 0.1, "type": "tcp"},
                {},
                (TcpProbe, {"host": "1.1.1.1", "port": 53, "tcp_timeout": 0.1}),
            ),
            ({"type": "ping", "host": "8.8.8.8"}, {}, (PingProbe, {"host": "8.8.8.8"})),
            (
                {"ips": ["8.8.8.8", "8.8.4.4"], "name": "dns.google", "type": "dns"},
                {},
                (DnsProbe, {"ips": ["8.8.8.8", "8.8.4.4"], "name": "dns.google"}),
            ),
        ]
    )
    def test_gen_call(self, command, config, expected_call):
        call = gen_call(command, config)
        self.assertEqual(call[1], expected_call[0].get_type())
        self.assertDictEqual(call[0].__dict__, expected_call[1])

    def test_run_success(self):
        exit_code = run([(HttpProbe(url="https://httpbin.org/status/200"), "http")])
        self.assertEqual(exit_code, 0)

    def test_run_fail(self):
        exit_code = run([(HttpProbe(url="https://httpbin.org/status/500"), "http")])
        self.assertEqual(exit_code, 1)

    @parameterized.expand(
        [
            ({"type": "ping", "host": "8.8.8.8"}, [{"type": "ping", "host": "8.8.8.8"}]),
            (
                {"a": {"type": "ping", "host": "8.8.8.8"}, "b": {"type": "tcp", "host": "8.8.8.8", "port": 53}},
                [{"type": "ping", "host": "8.8.8.8"}, {"type": "tcp", "host": "8.8.8.8", "port": 53}],
            ),
            ({"a": {"b": {"c": {"type": "ping", "host": "8.8.8.8"}}}}, [{"type": "ping", "host": "8.8.8.8"}]),
            (
                {"a": {"type": "ping", "host": "8.8.8.8", "b": {"type": "tcp", "host": "8.8.8.8", "port": 53}}},
                [{"type": "ping", "host": "8.8.8.8"}],
            ),
        ]
    )
    def test_getcommands(self, config, expected_commands):
        commands = get_commands_from_config(config)
        for i in range(0, len(expected_commands)):
            self.assertEqual(commands[i], expected_commands[i])


if __name__ == "__main__":
    unittest.main()
