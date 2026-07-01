from .models import (
    TrackProgressFrame,
    TrackProgressSample,
)


class TrackProgressService:

    """
    Converts FastF1 position data into our canonical format.

    This service deliberately does NOT calculate traffic or
    nearest cars.

    It simply normalizes position samples.
    """

    def build(
        self,
        session,
        driver_number: str,
    ) -> TrackProgressFrame:

        dataframe = session.pos_data[driver_number]

        frame = TrackProgressFrame(
            driver_number=driver_number,
        )

        for _, row in dataframe.iterrows():
            
            status = str(row["Status"])

            x = float(row["X"])
            y = float(row["Y"])

            if status != "OnTrack":
                continue

            if x == 0 and y == 0:
                continue

            frame.samples.append(

                TrackProgressSample(

                    session_time=row["SessionTime"],

                    x=x,

                    y=y,

                    status=status,
                )
            )

        return frame