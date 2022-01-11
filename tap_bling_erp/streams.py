from datetime import timedelta, datetime, timezone
from .transform import extract_last_updated
import pytz
import singer

LOGGER = singer.get_logger()
BOOKMARK_DATE_FORMAT = '%Y-%m-%dT%H:%M:%S.%fZ'
API_REQ_DATETIME_FORMAT = '%d/%m/%Y %H:%M:%S'
API_RESP_DATETIME_FORMAT = '%Y-%m-%d %H:%M:%S'

class Stream:
    def __init__(self, client):
        self.client = client

    def sao_paulo_tz_fixed(self,dt_param):
        """This method does a workaround for Sao Paulo lack of DST since may 2019. It's used Recife's, as it equivalent."""
        if not isinstance(dt_param,datetime):
            raise "Cannot parse an non datetime parameter"
        
        # Cutoff date when Brazil's president ended DST
        cutoff_date = datetime.strptime("2019-05-01","%Y-%m-%d")
        
        if dt_param.tzinfo is not None:
            cutoff_date = cutoff_date.replace(tzinfo=pytz.UTC) 

        if dt_param > cutoff_date:
            return 'America/Recife'
        else:
            return 'America/Sao_Paulo'


class Orders(Stream):
    tap_stream_id = 'bling_orders'
    key_properties = ['id']
    replication_method = 'INCREMENTAL'
    valid_replication_keys = ['dataAlteracao']
    replication_key = 'dataAlteracao'

    # Orders come from API as tz America/Sao_Paulo, but without the tz info in the payload. Therefore Singer will append UTC 0 by default, but the datetime value will still represent America/Sao_Paulo. This has to be converted in the DW later.
    def sync(self, state, stream_schema, stream_metadata, config, transformer):
        # Bookmark datetime is tz America/Sao_Paulo
        start_time_str = singer.get_bookmark(
            state,
            self.tap_stream_id,
            self.replication_key,
            config['start_date'])
        # add timezone UTC 0 without changing the datetime
        start_time = datetime.strptime(start_time_str,BOOKMARK_DATE_FORMAT).replace(tzinfo=pytz.UTC)
        max_record_value = start_time

        # singer.utils.now brings time in UTC converting correctly from the OS
        singer_now = singer.utils.now()
        # It's necessary to convert to the API tz
        extraction_time = singer_now.astimezone(pytz.timezone(self.sao_paulo_tz_fixed(singer_now)))
        api_start_time = datetime.strftime(start_time,API_REQ_DATETIME_FORMAT)

        # To ensure data quality truncate to use second 0 and use finish date as 2 minutes ago
        api_finish_time = extraction_time.replace(second=0,microsecond=0) - timedelta(minutes=2)
        api_finish_time = datetime.strftime(api_finish_time,API_REQ_DATETIME_FORMAT)
        
        # get orders from API and iterate over results
        for page, records in self.client.get_orders(api_start_time,api_finish_time):
            for record in records:
                record = extract_last_updated(record['pedido'],API_RESP_DATETIME_FORMAT)
                transformed_record = transformer.transform(record, stream_schema, stream_metadata)

                # as the transformed_record returns any datetime field as a str in the format of "%04Y-%m-%dT%H:%M:%S.%fZ", it's necessary to convert it to datetime for comparisons.
                # replace method is used because data was only faked as if it was UTC 0 timezone, but no changes in datetime were applied, so we don't need to change it again
                updated_at = datetime.strptime(
                    transformed_record[self.replication_key],
                    BOOKMARK_DATE_FORMAT)
                updated_at = updated_at.replace(tzinfo=pytz.timezone(self.sao_paulo_tz_fixed(updated_at)))

                singer.write_record(self.tap_stream_id,transformed_record,time_extracted=extraction_time)

                if updated_at > max_record_value:
                    max_record_value = updated_at

        # As the API will return data where updated_at < HH:MM, use the next minute as the bookmark
        # Altough updated_at is always truncated at the minute level, does this manual truncation just to be sure future updates in the API won't break the code
        max_record_value = max_record_value + timedelta(minutes=1)
        max_record_value = datetime.strftime(
            max_record_value.replace(second=0),BOOKMARK_DATE_FORMAT)
        state = singer.write_bookmark(state, self.tap_stream_id, self.replication_key, max_record_value)
        singer.write_state(state)
        
        return state

class Invoices(Stream):
    tap_stream_id = 'bling_invoices'
    key_properties = ['id'] # What's the role of this field?
    replication_method = 'INCREMENTAL'
    valid_replication_keys = ['dataEmissao']
    replication_key = 'dataEmissao'

    # Invoices come from API as tz America/Sao_Paulo, but without the tz info in the payload. Therefore Singer will append UTC 0 by default, but the datetime value will still represent America/Sao_Paulo. This has to be converted in the DW later.
    def sync(self, state, stream_schema, stream_metadata, config, transformer):
        # Bookmark datetime is tz America/Sao_Paulo
        start_time_str = singer.get_bookmark(
            state,
            self.tap_stream_id,
            self.replication_key,
            config['start_date'])
        # add timezone UTC 0 without changing the datetime
        start_time = datetime.strptime(start_time_str,BOOKMARK_DATE_FORMAT).replace(tzinfo=pytz.UTC)
        max_record_value = start_time

        # singer.utils.now brings time in UTC converting correctly from the OS
        singer_now = singer.utils.now()
        # It's necessary to convert to the API tz
        extraction_time = singer_now.astimezone(pytz.timezone(self.sao_paulo_tz_fixed(singer_now)))
        api_start_time = datetime.strftime(start_time,API_REQ_DATETIME_FORMAT)

        # To ensure data quality truncate to use second 0 and use finish date as 2 minutes ago
        api_finish_time = extraction_time.replace(second=0,microsecond=0) - timedelta(minutes=2)
        api_finish_time = datetime.strftime(api_finish_time,API_REQ_DATETIME_FORMAT)
        
        # get invoices from API and iterate over results
        for page, records in self.client.invoices(api_start_time,api_finish_time):
            for record in records:
                record = extract_last_updated(record['notafiscal'],API_RESP_DATETIME_FORMAT)
                transformed_record = transformer.transform(record, stream_schema, stream_metadata)

                # as the transformed_record returns any datetime field as a str in the format of "%04Y-%m-%dT%H:%M:%S.%fZ", it's necessary to convert it to datetime for comparisons.
                # replace method is used because data was only faked as if it was UTC 0 timezone, but no changes in datetime were applied, so we don't need to change it again
                updated_at = datetime.strptime(
                    transformed_record[self.replication_key],
                    BOOKMARK_DATE_FORMAT)
                updated_at = updated_at.replace(tzinfo=pytz.timezone(self.sao_paulo_tz_fixed(updated_at)))

                singer.write_record(self.tap_stream_id,transformed_record,time_extracted=extraction_time)

                if updated_at > max_record_value:
                    max_record_value = updated_at

        # As the API will return data where updated_at < HH:MM, use the next minute as the bookmark
        # Altough updated_at is always truncated at the minute level, does this manual truncation just to be sure future updates in the API won't break the code
        max_record_value = max_record_value + timedelta(minutes=1)
        max_record_value = datetime.strftime(
            max_record_value.replace(second=0),BOOKMARK_DATE_FORMAT)
        state = singer.write_bookmark(state, self.tap_stream_id, self.replication_key, max_record_value)
        singer.write_state(state)
        
        return state

STREAMS = {
    'bling_orders': Orders,
    'bling_invoices': Invoices
}