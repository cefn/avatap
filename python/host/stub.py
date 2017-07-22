import sys

class StubHost:
    def displayGeneratedText(self, generator):
        for chunk in generator:
            sys.stdout.write(chunk)
