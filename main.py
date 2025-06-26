import requests, datetime, time
from plyer import notification

class TrainReminder:
    def __init__(self, from_station, to_station, reminder_minutes=5,check_interval=60):
        """
        Initialize the TrainReminder class

        :param from_station: Thhe departure station (string)
        :param to_station: The destination station (string)
        :param reminder_minutes: How many minutes before departure will be notified
        :param check_interval: how often to check for departures
        """
        self.from_station = from_station
        self.to_station = to_station
        self.reminder_minutes = reminder_minutes
        self.check_interval = check_interval

    def get_departure(self):
        """
        Calls the VBB API (https://v5.vbb.transport.rest) to fetch the next departure time 
        from origin to destination.

        This API returns a list of 'journeys', each containing one or more 'legs'.
        Each leg includes a 'departure' timestamp in ISO 8601 format (with timezone).
        
        Important:
        - The 'from' and 'to' parameters MUST be valid IBNR stop IDs (e.g., '900000012102'),
        not plain station names. Using station names returns ambiguous location results
        or fails entirely (e.g., "from must be an IBNR").
        - A single journey may contain multiple legs; we take the departure time of the first leg.
        
        :return: A datetime object of the next departure, or None on failure.
        """
        url = "https://v5.vbb.transport.rest/journeys"
        try:
            response = requests.get(url, params={
                "from": self.from_station,  
                "to": self.to_station,      
                "results": 1,
                "language": "en"
            }, timeout=5)

            response.raise_for_status()
            data = response.json()

            journeys = data.get("journeys")
            if not journeys:
                print("No journeys found in API response.")
                return None

            # Access the departure time of the first leg of the first journey
            departure_str = journeys[0]["legs"][0].get("departure")
            if not departure_str:
                print("No departure timestamp found in journey leg.")
                return None

            return datetime.datetime.fromisoformat(departure_str)

        except (requests.RequestException, KeyError, IndexError, ValueError) as e:
            print(f"API error: {e}")
            return None

    def notify(self, departure_time):
        """
        Send a desktop notification to the user

        :param departure_time: datetieme of the upcoming train
        """
        notification.notify(
            title="Train Reminder",
            message=f"Train departs at {departure_time.strftime('%H:%M')}. Time to leave now."
        )

    def run(self):
        """
        Monitor departures and sends a notification when is time to leave.
        """
        print(f"Monitoring trains from '{self.from_station}' to '{self.to_station}'")

        while True:
            now = datetime.datetime.now(datetime.timezone.utc)
            departure_time = self.get_departure()

            # Default wait time before the next check
            sleep_duration = self.check_interval

            if departure_time:
                time_to_leave = departure_time - datetime.timedelta(minutes=self.reminder_minutes)

                if now >= time_to_leave:
                    self.notify(departure_time)
                    # Assume next train is in 1h so wait before checking again
                    sleep_duration = 60 * 60
                else:
                    notify_at = time_to_leave.strftime('%H:%M')
                    print(f"[{now.strftime('%H:%M:%S')}] Next train at {departure_time}, will notify at {notify_at}")

            time.sleep(sleep_duration)

if __name__ == "__main__":
    reminder = TrainReminder(
        from_station = "900000012102", # Assuming work location is Checkpoint Charlie
        to_station = "900000100025",  # Assuming home location in Unter den Linden
        reminder_minutes = 5,
        check_interval = 60
    )
    reminder.run()






