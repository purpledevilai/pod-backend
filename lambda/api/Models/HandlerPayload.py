class HandlerPayload:
    def __init__(self, lambda_event, logger):
        self.lambda_event = lambda_event
        self.logger = logger