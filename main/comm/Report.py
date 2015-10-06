

class Report(object):
    def __init__(self):
        self.start_time = datetime.now()

    def get_runtime():
        global startTime
        runtime = datetime.now() - startTime #by not including .time() we're creating a timedelta object
        return runtime

    def get_runtime_in_minutes():
        runtime = get_runtime()
        seconds = int(runtime.total_seconds()) #no millisecond nonsense please
        magentaprint("Seconds run: " + str(seconds))
        if seconds <= 1:
            seconds = 60
        minutes = (seconds / 60) #at least display 1 minute
        return minutes

    def calculate_vpm(value):
        minutes = get_runtime_in_minutes()
        vpm = int(value / minutes) #no decimals
        return vpm

