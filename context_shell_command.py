import os
import subprocess
import sys

import sublime
import sublime_plugin
from Default import exec

try:
    from dctxmenu import menu
except:
    sublime.error_message(
        f'The plugin `dctxmenu` is not installed, {__package__} stoped')
    raise


class Debug:
    __slots__ = []

    _debug = False

    @classmethod
    def print(cls, *args):
        if not cls._debug:
            return
        print(f'{__package__}:', *args)


class ExecuteShellCommandCommand(sublime_plugin.WindowCommand):
    def run(self, command, working_dir='', shell=False, **kwargs):
        variables = self.window.extract_variables()
        cmd = sublime.expand_variables(command, variables)
        working_dir = sublime.expand_variables(working_dir, variables)
        if shell:
            shell_cmd = ' '.join(cmd)
        else:
            shell_cmd = None

        Debug.print(f"""run
\tcmd: {cmd}
\tshell_cmd: '{shell_cmd}'
\tkwargs: {kwargs}""")

        try:
            exec.ExecCommand(self.window).run(
                cmd=cmd,
                shell_cmd=shell_cmd,
                working_dir=working_dir,
                **kwargs
            )
        except Exception as e:
            sublime.status_message(str(e))


class ContextShellCommandMenuCreater(menu.MenuCreater):
    def context_menu(self, event):
        Debug.print('context_menu')
        if not os.path.exists(self.view.file_name() or ''):
            return None

        items = []
        for i, cmd in enumerate(self.commands):
            items.append(
                self.item(
                    cmd.get('caption', ''),
                    'execute_shell_command',
                    {k: cmd[k] for k in cmd if k != 'caption'}
                )
            )
        if len(items) == 0:
            return None
        elif len(items) == 1:
            return items[0]

        item = self.folded_item(self.caption, items)
        Debug.print('item:', item)
        return item

    @classmethod
    def init(cls):
        platforms = ['', sublime.platform()]
        cls.caption = settings.get('caption', 'Run Shell Cmd')
        cls.commands = [
            command for command in settings.get('commands', [])
            if command.pop('platform', '').lower() in platforms
        ]


def reload_settings():
    global settings
    settings = sublime.load_settings('ContextShellCommand.sublime-settings')
    settings.add_on_change('caption', ContextShellCommandMenuCreater.init)
    ContextShellCommandMenuCreater.init()


def plugin_loaded():
    sublime.set_timeout_async(reload_settings)
    menu.register(__name__, ContextShellCommandMenuCreater)


def plugin_unloaded():
    settings.clear_on_change('caption')
    menu.remove(__name__)
