class WhisperTask:
    def __init__(self, command, transcript_file, start_timestamp):
        self.command = command
        self.transcript_file = transcript_file
        self.start_timestamp = start_timestamp