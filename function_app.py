import datetime
import logging
import azure.functions as func
from bi_sync import bi_directional_sync
from recom_engine import lasftm_similars


app = func.FunctionApp()

# run this every 5 minutes
@app.schedule(schedule="0 */5 * * * *", arg_name="myTimer", run_on_startup=True,
              use_monitor=True)
def SpotifyToLastfm(myTimer: func.TimerRequest) -> None:
    utc_timestamp = (
        datetime.datetime.now(datetime.timezone.utc)
        .replace(tzinfo=datetime.timezone.utc)
        .isoformat()
    )

    if datetime.datetime.now(datetime.timezone.utc).hour > 2:
        if token := bi_directional_sync(1):
            lasftm_similars(token) 

        if myTimer.past_due:
            logging.info('The timer is past due!')

        logging.info('Python timer trigger SpotifyToLastfm ran at %s', utc_timestamp)


# run this once per day at 0:30AM  
@app.schedule(schedule="0 30 0 * * *", arg_name="myTimer", run_on_startup=True,
              use_monitor=True)
def SpotifyToLastfm_nightly(myTimer: func.TimerRequest) -> None:
    utc_timestamp = (
        datetime.datetime.now(datetime.timezone.utc)
        .replace(tzinfo=datetime.timezone.utc)
        .isoformat()
    )

    _ = bi_directional_sync(limit=None)

    if myTimer.past_due:
        logging.info('The timer is past due!')

    logging.info('Python timer trigger SpotifyToLastfm_nightly ran at %s', utc_timestamp)    