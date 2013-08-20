#!/usr/bin/env python
# encoding: utf-8
import xerox


class Actions(object):
    """
    Processes a data string with the form:
        command:arguments
    and if there is an action defined to it, the run it.
    """

    def __init__(self):
        """
        Constructor of the class.
        Initializes the existing actions to use.
        """
        self.ACTIONS = {
            'clipboard': self._clipboard,
            'browser': self._browser,
            'msg': self._msg
        }

    def run(self, data):
        """
        Run the specified command and argument specified in the 'data' argument
        if is implemented.

        :param data: the data that the client received containing command
                     and arguments.
        :type data: str
        """
        if ':' in data:
            action, args = data.split(':')
            function = self.ACTIONS.get(action, None)
            if function is not None:
                function(args)
                return True

    def _clipboard(self, data):
        """
        Copies the contents of the parameter data to the system clipboard.

        :param data: the data to save in the clipboard.
        :type data: str
        """
        xerox.copy(data)

    def _browser(self, data):
        """
        Opens the url in the parameter data in the browser.

        :param data: the url to open in the browser.
        :type data: str
        """
        pass

    def _msg(self, data):
        pass


if __name__ == '__main__':
    actions = Actions()
    actions.run('clipboard:demo string to clipboard!')
