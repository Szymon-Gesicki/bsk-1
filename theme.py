
class Theme:

    @staticmethod
    def colorize(text, color):
        return '<font color="' + color + '">' + text + '</font>'

    @staticmethod
    def new_line():
        return "<br/>"
