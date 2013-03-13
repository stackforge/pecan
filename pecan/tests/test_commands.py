from pecan.tests import PecanTestCase


class TestCommandManager(PecanTestCase):

    def test_commands(self):
        from pecan.commands import ServeCommand, ShellCommand, CreateCommand
        from pecan.commands.base import CommandManager
        m = CommandManager()
        assert m.commands['serve'] == ServeCommand
        assert m.commands['shell'] == ShellCommand
        assert m.commands['create'] == CreateCommand


class TestCommandRunner(PecanTestCase):

    def test_commands(self):
        from pecan.commands import (
            ServeCommand, ShellCommand, CreateCommand, CommandRunner
        )
        runner = CommandRunner()
        assert runner.commands['serve'] == ServeCommand
        assert runner.commands['shell'] == ShellCommand
        assert runner.commands['create'] == CreateCommand

    def test_run(self):
        from pecan.commands import CommandRunner
        runner = CommandRunner()
        self.assertRaises(
            RuntimeError,
            runner.run,
            ['serve', 'missing_file.py']
        )


class TestCreateCommand(PecanTestCase):

    def test_run(self):
        from pecan.commands import CreateCommand

        class FakeArg(object):
            project_name = 'default'
            template_name = 'default'

        class FakeScaffold(object):
            def copy_to(self, project_name):
                assert project_name == 'default'

        class FakeManager(object):
            scaffolds = {
                'default': FakeScaffold
            }

        c = CreateCommand()
        c.manager = FakeManager()
        c.run(FakeArg())
