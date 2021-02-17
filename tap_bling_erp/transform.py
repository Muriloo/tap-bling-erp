from datetime import datetime


def extract_last_updated(record,API_RESP_DATETIME_FORMAT):
    """Extract last updated date from ocorrencias history."""
    
    ocurrences = record['ocorrencias']
    max_date = datetime.min
    for ocurrence in ocurrences:
        ocurr_date_str = ocurrence['ocorrencia']['data']
        ocurr_date = datetime.strptime(ocurr_date_str,API_RESP_DATETIME_FORMAT)

        if ocurr_date > max_date:
            max_date = ocurr_date

    max_date_str = datetime.strftime(max_date,API_RESP_DATETIME_FORMAT)

    record['dataAlteracao'] = max_date_str

    return record
