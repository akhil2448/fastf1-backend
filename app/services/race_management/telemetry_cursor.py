class TelemetryCursor:

    def __init__(self, samples):

        self.samples = samples

        self.index = 0

    ##############################################################

    def nearest(
        self,
        session_time,
    ):

        ##########################################################
        # Walk forward only
        ##########################################################

        while (

            self.index < len(self.samples) - 1

            and

            self.samples[
                self.index + 1
            ].session_time <= session_time

        ):

            self.index += 1

        ##########################################################
        # Compare current vs next
        ##########################################################

        current = self.samples[self.index]

        if self.index == len(self.samples) - 1:

            return current

        nxt = self.samples[
            self.index + 1
        ]

        current_delta = abs(
            (
                current.session_time
                - session_time
            ).total_seconds()
        )

        next_delta = abs(
            (
                nxt.session_time
                - session_time
            ).total_seconds()
        )

        if next_delta < current_delta:

            return nxt

        return current